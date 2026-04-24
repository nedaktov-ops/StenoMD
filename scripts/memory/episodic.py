"""
Episodic Memory Module

Stores and retrieves action history with full context.
Provides fast search and recall capabilities.
"""

import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import Counter

from .schema import DatabaseSchema


class EpisodicMemory:
    """
    Episodic memory for action history.
    
    Stores every action the agent takes with:
    - Full context (issue, action, outcome)
    - Timestamps and duration
    - Success/failure tracking
    - File impacts
    
    Retention: All forever (as per user preference)
    """
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON backup for readability
        self.json_path = memory_dir / 'actions.json'
        
        # SQLite for fast queries
        self.schema = DatabaseSchema(memory_dir)
        
        # Initialize JSON if needed
        if not self.json_path.exists():
            self._init_json()
    
    def _init_json(self):
        """Initialize JSON backup file."""
        initial = {
            'version': '2.0',
            'last_updated': datetime.now().isoformat(),
            'actions': [],
            'metadata': {
                'total_actions': 0,
                'success_rate': 0.0,
                'avg_duration_ms': 0
            }
        }
        self._write_json(initial)
    
    def _read_json(self) -> dict:
        """Read JSON backup."""
        if self.json_path.exists():
            return json.loads(self.json_path.read_text())
        return self._init_json() or {'actions': [], 'metadata': {}}
    
    def _write_json(self, data: dict):
        """Write JSON backup."""
        data['last_updated'] = datetime.now().isoformat()
        self.json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    def store(self, action: dict, outcome: dict) -> str:
        """
        Store an action and its outcome.
        
        Args:
            action: Action details (type, command, params, issue, etc.)
            outcome: Outcome details (success, duration, result, etc.)
            
        Returns:
            Unique action ID
        """
        action_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Build full record
        record = {
            'id': action_id,
            'timestamp': timestamp,
            'type': action.get('type', 'unknown'),
            'category': action.get('category'),
            'severity': action.get('severity'),
            'description': action.get('issue', {}).get('description', ''),
            'location': action.get('issue', {}).get('location'),
            'command': action.get('command'),
            'files_affected': action.get('files_affected', []),
            'parameters': action.get('parameters', {}),
            'success': outcome.get('success', False),
            'duration_ms': outcome.get('duration_ms', 0),
            'result': outcome.get('result', ''),
            'side_effects': outcome.get('side_effects', []),
            'mode': action.get('mode', 'unknown'),
            'project_hash': outcome.get('project_hash', '')
        }
        
        # Store in SQLite
        self.schema.execute(
            """
            INSERT INTO actions (
                id, timestamp, type, category, severity, description,
                location, command, files_affected, parameters,
                success, duration_ms, result, side_effects, mode, project_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record['id'],
                record['timestamp'],
                record['type'],
                record['category'],
                record['severity'],
                record['description'],
                record['location'],
                record['command'],
                json.dumps(record['files_affected']),
                json.dumps(record['parameters']),
                1 if record['success'] else 0,
                record['duration_ms'],
                record['result'],
                json.dumps(record['side_effects']),
                record['mode'],
                record['project_hash']
            )
        )
        self.schema.commit()
        
        # Update JSON backup (append)
        json_data = self._read_json()
        json_data['actions'].insert(0, record)  # Most recent first
        
        # Update metadata
        total = len(json_data['actions'])
        successes = sum(1 for a in json_data['actions'] if a.get('success'))
        durations = [a.get('duration_ms', 0) for a in json_data['actions']]
        
        json_data['metadata']['total_actions'] = total
        json_data['metadata']['success_rate'] = successes / total if total > 0 else 0
        json_data['metadata']['avg_duration_ms'] = sum(durations) / total if total > 0 else 0
        
        self._write_json(json_data)
        
        return action_id
    
    def search(self, query: str, limit: int = 10) -> List[dict]:
        """
        Search actions by query string.
        
        Args:
            query: Search query (matches description, command, result)
            limit: Maximum results to return
            
        Returns:
            List of matching action records
        """
        conn = self.schema._conn()
        pattern = f'%{query}%'
        
        rows = conn.execute(
            """
            SELECT * FROM actions
            WHERE description LIKE ?
               OR command LIKE ?
               OR result LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (pattern, pattern, pattern, limit)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_recent(self, limit: int = 10) -> List[dict]:
        """Get most recent actions."""
        conn = self.schema._conn()
        rows = conn.execute(
            "SELECT * FROM actions ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
    
    def get_by_id(self, action_id: str) -> Optional[dict]:
        """Get action by ID."""
        conn = self.schema._conn()
        row = conn.execute(
            "SELECT * FROM actions WHERE id = ?",
            (action_id,)
        ).fetchone()
        return dict(row) if row else None
    
    def get_similar(self, description: str, limit: int = 5) -> List[dict]:
        """Find similar actions based on description."""
        words = description.lower().split()
        if not words:
            return []
        
        # Build OR query for each word
        conditions = ' OR '.join(['description LIKE ?' for _ in words])
        params = [f'%{w}%' for w in words] + [limit]
        
        conn = self.schema._conn()
        rows = conn.execute(
            f"""
            SELECT * FROM actions
            WHERE {conditions}
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            params
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_by_outcome(self, success: bool, limit: int = 50) -> List[dict]:
        """Get actions by outcome (success/failure)."""
        conn = self.schema._conn()
        rows = conn.execute(
            """
            SELECT * FROM actions
            WHERE success = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (1 if success else 0, limit)
        ).fetchall()
        return [dict(row) for row in rows]
    
    def count(self) -> int:
        """Get total action count."""
        conn = self.schema._conn()
        row = conn.execute("SELECT COUNT(*) as count FROM actions").fetchone()
        return row['count'] if row else 0
    
    def get_common_issues(self, limit: int = 5) -> List[tuple]:
        """Get most frequently occurring issues."""
        conn = self.schema._conn()
        rows = conn.execute(
            """
            SELECT description, COUNT(*) as count
            FROM actions
            WHERE description IS NOT NULL AND description != ''
            GROUP BY description
            ORDER BY count DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()
        return [(row['description'], row['count']) for row in rows]
    
    def get_statistics(self) -> dict:
        """Get comprehensive statistics."""
        conn = self.schema._conn()
        
        total = self.count()
        successes = conn.execute(
            "SELECT COUNT(*) FROM actions WHERE success = 1"
        ).fetchone()[0]
        
        avg_duration = conn.execute(
            "SELECT AVG(duration_ms) FROM actions WHERE duration_ms > 0"
        ).fetchone()[0] or 0
        
        type_counts = conn.execute(
            "SELECT type, COUNT(*) FROM actions GROUP BY type"
        ).fetchall()
        
        category_counts = conn.execute(
            "SELECT category, COUNT(*) FROM actions WHERE category IS NOT NULL GROUP BY category"
        ).fetchall()
        
        return {
            'total_actions': total,
            'success_count': successes,
            'failure_count': total - successes,
            'success_rate': successes / total if total > 0 else 0,
            'avg_duration_ms': avg_duration,
            'by_type': {row[0]: row[1] for row in type_counts},
            'by_category': {row[0]: row[1] for row in category_counts}
        }
    
    def get_trends(self, days: int = 7) -> dict:
        """Analyze trends over time."""
        conn = self.schema._conn()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Actions per day
        daily = conn.execute(
            """
            SELECT DATE(timestamp) as date, COUNT(*) as count,
                   SUM(success) as successes
            FROM actions
            WHERE timestamp > ?
            GROUP BY DATE(timestamp)
            ORDER BY date
            """,
            (cutoff,)
        ).fetchall()
        
        # Success rate trend
        recent_success_rate = conn.execute(
            """
            SELECT SUM(success) * 1.0 / COUNT(*) as rate
            FROM actions
            WHERE timestamp > ?
            """,
            (cutoff,)
        ).fetchone()[0] or 0
        
        return {
            'days_analyzed': days,
            'daily_breakdown': [{'date': row[0], 'count': row[1], 'successes': row[2]} for row in daily],
            'recent_success_rate': recent_success_rate
        }