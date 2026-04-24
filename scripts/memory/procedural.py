"""
Procedural Memory Module

Stores and manages learned patterns.
Learns from single occurrences (aggressive learning as per user preference).
"""

import json
import uuid
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

from .schema import DatabaseSchema


class ProceduralMemory:
    """
    Procedural memory for learned patterns.
    
    Learns patterns from action-outcome pairs:
    - Issue patterns: what problems occur
    - Fix patterns: what solutions work
    - Success rates: how often fixes succeed
    - Dependencies: what fixes often follow others
    
    Learning: Aggressive (1+ occurrences as per user preference)
    Retention: All forever (as per user preference)
    """
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON backup for readability
        self.json_path = memory_dir / 'patterns.json'
        
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
            'patterns': [],
            'metadata': {
                'total_patterns': 0,
                'avg_success_rate': 0.0,
                'learning_enabled': True
            }
        }
        self._write_json(initial)
    
    def _read_json(self) -> dict:
        """Read JSON backup."""
        if self.json_path.exists():
            return json.loads(self.json_path.read_text())
        return {'patterns': [], 'metadata': {}}
    
    def _write_json(self, data: dict):
        """Write JSON backup."""
        data['last_updated'] = datetime.now().isoformat()
        self.json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    def learn_fix(self, action: dict, outcome: dict):
        """
        Learn from a successful fix.
        
        Args:
            action: Action details
            outcome: Outcome details (success=True)
        """
        issue_desc = action.get('issue', {}).get('description', '')
        issue_type = action.get('type', '')
        severity = action.get('severity', '')
        command = action.get('command', '')
        
        if not issue_desc and not command:
            return
        
        # Normalize for matching
        normalized_issue = self._normalize(issue_desc)
        normalized_fix = self._normalize(command)
        
        # Check if pattern already exists
        existing = self._find_pattern(normalized_issue, normalized_fix)
        
        if existing:
            # Update existing pattern
            self._update_pattern(existing['id'], success=True, duration_ms=outcome.get('duration_ms', 0))
        else:
            # Create new pattern
            self._create_pattern(
                issue_pattern=issue_desc,
                fix_pattern=command,
                issue_type=issue_type,
                severity=severity,
                success=True,
                duration_ms=outcome.get('duration_ms', 0)
            )
    
    def learn_failure(self, action: dict, outcome: dict):
        """
        Learn from a failed attempt.
        
        Args:
            action: Action details
            outcome: Outcome details (success=False)
        """
        issue_desc = action.get('issue', {}).get('description', '')
        command = action.get('command', '')
        
        if not issue_desc and not command:
            return
        
        normalized_issue = self._normalize(issue_desc)
        normalized_fix = self._normalize(command)
        
        existing = self._find_pattern(normalized_issue, normalized_fix)
        
        if existing:
            self._update_pattern(existing['id'], success=False, duration_ms=outcome.get('duration_ms', 0))
        else:
            # Still record the failure pattern
            self._create_pattern(
                issue_pattern=issue_desc,
                fix_pattern=command,
                success=False,
                duration_ms=outcome.get('duration_ms', 0)
            )
    
    def _normalize(self, text: str) -> str:
        """Normalize text for pattern matching."""
        if not text:
            return ''
        # Lowercase, remove special chars, collapse whitespace
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _find_pattern(self, issue: str, fix: str) -> Optional[dict]:
        """Find existing pattern by issue and fix."""
        conn = self.schema._conn()
        
        # Search by normalized patterns
        pattern = f'%{issue}%'
        
        rows = conn.execute(
            """
            SELECT * FROM patterns
            WHERE issue_pattern LIKE ? OR fix_pattern LIKE ?
            LIMIT 10
            """,
            (pattern, pattern)
        ).fetchall()
        
        for row in rows:
            row_dict = dict(row)
            if self._normalize(row_dict.get('issue_pattern', '')) == issue:
                return row_dict
        
        return None
    
    def _create_pattern(self, issue_pattern: str, fix_pattern: str, 
                        issue_type: str = '', severity: str = '',
                        success: bool = True, duration_ms: int = 0):
        """Create a new pattern."""
        pattern_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        conn = self.schema._conn()
        conn.execute(
            """
            INSERT INTO patterns (
                id, issue_pattern, fix_pattern, success_count, failure_count,
                total_uses, avg_duration_ms, first_seen, last_seen, confidence,
                metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pattern_id,
                issue_pattern,
                fix_pattern,
                1 if success else 0,
                0 if success else 1,
                1,
                duration_ms if duration_ms > 0 else None,
                timestamp,
                timestamp,
                0.9 if success else 0.1,  # Initial confidence from single example
                json.dumps({'issue_type': issue_type, 'severity': severity})
            )
        )
        self.schema.commit()
        
        # Update JSON
        self._update_json_backup()
    
    def _update_pattern(self, pattern_id: str, success: bool, duration_ms: int = 0):
        """Update existing pattern with new data."""
        conn = self.schema._conn()
        
        # Get current values
        row = conn.execute(
            "SELECT * FROM patterns WHERE id = ?",
            (pattern_id,)
        ).fetchone()
        
        if not row:
            return
        
        success_count = row['success_count'] + (1 if success else 0)
        failure_count = row['failure_count'] + (0 if success else 1)
        total_uses = row['total_uses'] + 1
        
        # Calculate new average duration
        old_avg = row['avg_duration_ms'] or 0
        old_count = row['total_uses']
        if duration_ms > 0:
            new_avg = ((old_avg * old_count) + duration_ms) / total_uses
        else:
            new_avg = old_avg
        
        # Calculate confidence
        confidence = success_count / total_uses if total_uses > 0 else 0.5
        
        conn.execute(
            """
            UPDATE patterns SET
                success_count = ?,
                failure_count = ?,
                total_uses = ?,
                avg_duration_ms = ?,
                last_seen = ?,
                confidence = ?
            WHERE id = ?
            """,
            (
                success_count,
                failure_count,
                total_uses,
                int(new_avg),
                datetime.now().isoformat(),
                confidence,
                pattern_id
            )
        )
        self.schema.commit()
        
        self._update_json_backup()
    
    def _update_json_backup(self):
        """Update JSON backup from database."""
        conn = self.schema._conn()
        rows = conn.execute("SELECT * FROM patterns ORDER BY last_seen DESC").fetchall()
        
        patterns = [dict(row) for row in rows]
        
        total = len(patterns)
        avg_success = sum(p.get('confidence', 0) for p in patterns) / total if total > 0 else 0
        
        self._write_json({
            'version': '2.0',
            'last_updated': datetime.now().isoformat(),
            'patterns': patterns,
            'metadata': {
                'total_patterns': total,
                'avg_success_rate': avg_success,
                'learning_enabled': True
            }
        })
    
    def find_patterns(self, issue_desc: str = '', issue_type: str = '', 
                      severity: str = '') -> List[dict]:
        """
        Find patterns matching issue.
        
        Args:
            issue_desc: Issue description
            issue_type: Issue type
            severity: Issue severity
            
        Returns:
            List of matching patterns sorted by confidence
        """
        conn = self.schema._conn()
        
        # Build query
        conditions = []
        params = []
        
        if issue_desc:
            conditions.append("issue_pattern LIKE ?")
            params.append(f'%{issue_desc}%')
        
        if issue_type:
            conditions.append("metadata LIKE ?")
            params.append(f'%"{issue_type}"%')
        
        if severity:
            conditions.append("metadata LIKE ?")
            params.append(f'%"{severity}"%')
        
        query = "SELECT * FROM patterns"
        if conditions:
            query += " WHERE " + " OR ".join(conditions)
        query += " ORDER BY confidence DESC, total_uses DESC LIMIT 20"
        
        rows = conn.execute(query, params).fetchall() if params else \
               conn.execute("SELECT * FROM patterns ORDER BY confidence DESC LIMIT 20").fetchall()
        
        results = []
        for row in rows:
            r = dict(row)
            # Calculate success rate
            total = r.get('total_uses', 1)
            successes = r.get('success_count', 0)
            r['success_rate'] = successes / total if total > 0 else 0
            r['times_used'] = total
            results.append(r)
        
        return results
    
    def search(self, query: str, limit: int = 10) -> List[dict]:
        """Search patterns by query."""
        conn = self.schema._conn()
        pattern = f'%{query}%'
        
        rows = conn.execute(
            """
            SELECT * FROM patterns
            WHERE issue_pattern LIKE ? OR fix_pattern LIKE ?
            ORDER BY confidence DESC
            LIMIT ?
            """,
            (pattern, pattern, limit)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_most_effective(self, limit: int = 5, min_uses: int = 2) -> List[dict]:
        """Get most effective patterns (high success rate, used multiple times)."""
        conn = self.schema._conn()
        
        rows = conn.execute(
            """
            SELECT * FROM patterns
            WHERE total_uses >= ?
            ORDER BY (success_count * 1.0 / total_uses) DESC, total_uses DESC
            LIMIT ?
            """,
            (min_uses, limit)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_least_effective(self, limit: int = 5) -> List[dict]:
        """Get least effective patterns (high failure rate)."""
        conn = self.schema._conn()
        
        rows = conn.execute(
            """
            SELECT * FROM patterns
            WHERE total_uses >= 2
            ORDER BY (success_count * 1.0 / total_uses) ASC, total_uses DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_effectiveness(self) -> dict:
        """Get comprehensive effectiveness analysis."""
        conn = self.schema._conn()
        
        total_patterns = self.count()
        
        if total_patterns == 0:
            return {
                'total_patterns': 0,
                'avg_success_rate': 0,
                'avg_uses': 0,
                'top_fix': None,
                'worst_fix': None
            }
        
        # Overall stats
        row = conn.execute(
            """
            SELECT 
                AVG(confidence) as avg_conf,
                AVG(total_uses) as avg_uses
            FROM patterns
            """
        ).fetchone()
        
        # Best performing
        top = self.get_most_effective(limit=1, min_uses=1)
        worst = self.get_least_effective(limit=1)
        
        return {
            'total_patterns': total_patterns,
            'avg_success_rate': row['avg_conf'] if row else 0,
            'avg_uses': row['avg_uses'] if row else 0,
            'top_fix': top[0] if top else None,
            'worst_fix': worst[0] if worst else None
        }
    
    def count(self) -> int:
        """Get total pattern count."""
        conn = self.schema._conn()
        row = conn.execute("SELECT COUNT(*) as count FROM patterns").fetchone()
        return row['count'] if row else 0
    
    def get_statistics(self) -> dict:
        """Get pattern statistics."""
        conn = self.schema._conn()
        
        total = self.count()
        
        if total == 0:
            return {
                'total': 0,
                'avg_confidence': 0,
                'avg_uses': 0,
                'perfect_success': 0,
                'mixed_results': 0
            }
        
        row = conn.execute(
            """
            SELECT 
                AVG(confidence) as avg_conf,
                AVG(total_uses) as avg_uses,
                SUM(CASE WHEN success_count = total_uses THEN 1 ELSE 0 END) as perfect,
                SUM(CASE WHEN success_count > 0 AND failure_count > 0 THEN 1 ELSE 0 END) as mixed
            FROM patterns
            """
        ).fetchone()
        
        return {
            'total': total,
            'avg_confidence': row['avg_conf'] if row else 0,
            'avg_uses': row['avg_uses'] if row else 0,
            'perfect_success': row['perfect'] if row else 0,
            'mixed_results': row['mixed'] if row else 0
        }