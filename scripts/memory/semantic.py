"""
Semantic Memory Module

Integrates with knowledge graph for semantic knowledge storage.
Provides entity-relationship based memory.
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

from .schema import DatabaseSchema


class SemanticMemory:
    """
    Semantic memory using knowledge graph principles.
    
    Stores knowledge as entities and relationships:
    - Entity: person, file, concept, tool, etc.
    - Relationship: works_on, depends_on, uses, affects
    
    Provides reasoning capabilities through graph traversal.
    """
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON backup
        self.json_path = memory_dir / 'knowledge.json'
        
        # SQLite for graph queries
        self.schema = DatabaseSchema(memory_dir)
        
        if not self.json_path.exists():
            self._init_json()
    
    def _init_json(self):
        """Initialize JSON backup."""
        initial = {
            'version': '2.0',
            'last_updated': datetime.now().isoformat(),
            'entities': [],
            'relationships': [],
            'metadata': {
                'total_entities': 0,
                'total_relationships': 0
            }
        }
        self._write_json(initial)
    
    def _read_json(self) -> dict:
        """Read JSON backup."""
        if self.json_path.exists():
            return json.loads(self.json_path.read_text())
        return {'entities': [], 'relationships': [], 'metadata': {}}
    
    def _write_json(self, data: dict):
        """Write JSON backup."""
        data['last_updated'] = datetime.now().isoformat()
        self.json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    def add_entity(self, name: str, entity_type: str, properties: dict = None):
        """
        Add an entity to semantic memory.
        
        Args:
            name: Entity name
            entity_type: Type (person, file, concept, tool, etc.)
            properties: Additional properties
        """
        entity_id = str(uuid.uuid4())
        
        conn = self.schema._conn()
        conn.execute(
            """
            INSERT OR REPLACE INTO knowledge (id, entity_type, entity_name, value, confidence)
            VALUES (?, ?, ?, ?, ?)
            """,
            (entity_id, entity_type, name, json.dumps(properties or {}), 1.0)
        )
        self.schema.commit()
        
        # Update JSON
        self._update_json_backup()
        
        return entity_id
    
    def add_knowledge(self, action: dict, outcome: dict):
        """
        Extract and store knowledge from action-outcome.
        
        Args:
            action: Action details
            outcome: Outcome details
        """
        # Extract entities from action
        files = action.get('files_affected', [])
        command = action.get('command', '')
        issue_desc = action.get('issue', {}).get('description', '')
        
        # Add file entities
        for file_path in files:
            if isinstance(file_path, str):
                # Extract filename
                filename = file_path.split('/')[-1].replace('.md', '').replace('.py', '')
                if filename:
                    self.add_entity(filename, 'file', {'path': file_path})
        
        # Add command as tool entity
        if command:
            cmd_parts = command.split()
            if cmd_parts:
                tool_name = cmd_parts[0].replace('python3', '').replace('scripts/', '')
                if tool_name:
                    self.add_entity(tool_name, 'tool', {'command': command})
        
        # Add relationship: file affected by tool
        if command and files:
            tool_name = command.split()[0] if command.split() else 'unknown'
            for file_path in files:
                self.add_relationship(
                    subject=tool_name,
                    predicate='affects',
                    obj=file_path,
                    confidence=1.0 if outcome.get('success') else 0.5
                )
        
        # Add relationship: issue resolved by tool
        if issue_desc and command and outcome.get('success'):
            self.add_relationship(
                subject=issue_desc[:100],  # Truncate for storage
                predicate='resolved_by',
                obj=command,
                confidence=0.9
            )
    
    def add_relationship(self, subject: str, predicate: str, obj: str, 
                         confidence: float = 1.0, source_action: str = None):
        """
        Add a relationship between entities.
        
        Args:
            subject: Subject entity
            predicate: Relationship type (affects, uses, depends_on, etc.)
            obj: Object entity
            confidence: Relationship confidence (0-1)
            source_action: Source action ID for traceability
        """
        # Check if relationship exists
        conn = self.schema._conn()
        existing = conn.execute(
            """
            SELECT * FROM knowledge
            WHERE entity_name = ? AND predicate = ? AND value = ?
            """,
            (subject, predicate, obj)
        ).fetchone()
        
        if existing:
            # Update confidence if better
            if confidence > (existing['confidence'] or 0):
                conn.execute(
                    "UPDATE knowledge SET confidence = ? WHERE id = ?",
                    (confidence, existing['id'])
                )
        else:
            # Create new relationship
            rel_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO knowledge (id, entity_type, entity_name, predicate, value, confidence, source_action)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (rel_id, 'relationship', subject, predicate, obj, confidence, source_action)
            )
        
        self.schema.commit()
        self._update_json_backup()
    
    def search(self, query: str, limit: int = 10) -> List[dict]:
        """
        Search semantic memory.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching knowledge entries
        """
        conn = self.schema._conn()
        pattern = f'%{query}%'
        
        rows = conn.execute(
            """
            SELECT * FROM knowledge
            WHERE entity_name LIKE ? OR value LIKE ? OR predicate LIKE ?
            ORDER BY confidence DESC, created_at DESC
            LIMIT ?
            """,
            (pattern, pattern, pattern, limit)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_entity(self, name: str) -> List[dict]:
        """Get all knowledge about an entity."""
        conn = self.schema._conn()
        
        rows = conn.execute(
            """
            SELECT * FROM knowledge
            WHERE entity_name = ? OR value LIKE ?
            ORDER BY created_at DESC
            """,
            (name, f'%{name}%')
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_related(self, entity: str, depth: int = 1) -> Dict[str, List]:
        """
        Get related entities up to given depth.
        
        Args:
            entity: Starting entity
            depth: Traversal depth
            
        Returns:
            Dictionary of related entities by relationship type
        """
        conn = self.schema._conn()
        results = {}
        
        # Get direct relationships
        rows = conn.execute(
            """
            SELECT * FROM knowledge
            WHERE entity_name = ? OR value = ?
            """,
            (entity, entity)
        ).fetchall()
        
        for row in rows:
            rel_type = row['predicate']
            related = row['value'] if row['entity_name'] == entity else row['entity_name']
            
            if rel_type not in results:
                results[rel_type] = []
            
            results[rel_type].append({
                'entity': related,
                'confidence': row['confidence'],
                'depth': 1
            })
        
        # Recursive traversal for deeper relationships
        if depth > 1:
            for rel_type, entities in list(results.items()):
                for ent in entities:
                    deeper = self.get_related(ent['entity'], depth - 1)
                    for dt, items in deeper.items():
                        full_type = f"{rel_type}->{dt}"
                        if full_type not in results:
                            results[full_type] = []
                        for item in items:
                            item['depth'] = item.get('depth', 1) + 1
                            results[full_type].append(item)
        
        return results
    
    def count(self) -> int:
        """Get total knowledge entries."""
        conn = self.schema._conn()
        row = conn.execute("SELECT COUNT(*) as count FROM knowledge WHERE entity_type = 'relationship'").fetchone()
        return row['count'] if row else 0
    
    def _update_json_backup(self):
        """Update JSON backup from database."""
        conn = self.schema._conn()
        
        # Get entities
        entity_rows = conn.execute(
            """
            SELECT * FROM knowledge
            WHERE entity_type != 'relationship'
            GROUP BY entity_name
            ORDER BY entity_type, entity_name
            """
        ).fetchall()
        
        # Get relationships
        rel_rows = conn.execute(
            """
            SELECT * FROM knowledge
            WHERE entity_type = 'relationship'
            ORDER BY entity_name, predicate
            """
        ).fetchall()
        
        self._write_json({
            'version': '2.0',
            'last_updated': datetime.now().isoformat(),
            'entities': [dict(r) for r in entity_rows],
            'relationships': [dict(r) for r in rel_rows],
            'metadata': {
                'total_entities': len(entity_rows),
                'total_relationships': len(rel_rows)
            }
        })
    
    def get_statistics(self) -> dict:
        """Get semantic memory statistics."""
        conn = self.schema._conn()
        
        total = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
        
        entity_counts = conn.execute(
            """
            SELECT entity_type, COUNT(*) as count
            FROM knowledge
            WHERE entity_type != 'relationship'
            GROUP BY entity_type
            """
        ).fetchall()
        
        predicate_counts = conn.execute(
            """
            SELECT predicate, COUNT(*) as count
            FROM knowledge
            WHERE entity_type = 'relationship'
            GROUP BY predicate
            ORDER BY count DESC
            """
        ).fetchall()
        
        return {
            'total_entries': total,
            'by_entity_type': {row[0]: row[1] for row in entity_counts},
            'by_predicate': {row[0]: row[1] for row in predicate_counts}
        }