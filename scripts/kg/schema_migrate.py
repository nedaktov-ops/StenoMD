#!/usr/bin/env python3
"""
Knowledge Graph Schema Migration
Migrates entities.json to SQLite with triples support

Usage:
    python3 schema_migrate.py --migrate
    python3 schema_migrate.py --stats
    python3 schema_migrate.py --add-triple subject predicate object
"""

import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
KG_DIR = PROJECT_DIR / "knowledge_graph"
KG_DB = KG_DIR / "knowledge_graph.db"


@dataclass
class Entity:
    """Knowledge graph entity."""
    id: str
    name: str
    entity_type: str  # 'person', 'session', 'law'
    properties: Dict
    created_at: str = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class Triple:
    """Knowledge graph triple (subject-predicate-object)."""
    subject: str
    predicate: str
    object: str
    confidence: float = 1.0
    source: str = None
    created_at: str = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class KnowledgeGraph:
    """Knowledge graph with SQLite backend."""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or KG_DB
        self._init_schema()
    
    def _init_schema(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                entity_type TEXT,
                properties TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Triples table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS triples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                object TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                source TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(subject, predicate, object)
            )
        """)
        
        # Sessions table (denormalized for fast queries)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                date TEXT,
                chamber TEXT,
                title TEXT,
                url TEXT,
                participants TEXT,
                laws_discussed TEXT,
                summary TEXT,
                word_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_triples_subject ON triples(subject)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_triples_predicate ON triples(predicate)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_chamber ON sessions(chamber)")
        
        conn.commit()
        conn.close()
    
    def add_entity(self, entity: Entity):
        """Add entity to graph."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO entities (id, name, entity_type, properties, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (entity.id, entity.name, entity.entity_type, 
              json.dumps(entity.properties), entity.created_at))
        
        conn.commit()
        conn.close()
    
    def add_triple(self, triple: Triple):
        """Add triple to graph."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO triples (subject, predicate, object, confidence, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (triple.subject, triple.predicate, triple.object,
                  triple.confidence, triple.source, triple.created_at))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Triple already exists
        
        conn.close()
    
    def add_session(self, session_data: Dict):
        """Add session to graph."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO sessions 
            (id, date, chamber, title, url, participants, laws_discussed, summary, word_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_data.get('id'),
            session_data.get('date'),
            session_data.get('chamber'),
            session_data.get('title'),
            session_data.get('url'),
            json.dumps(session_data.get('participants', [])),
            json.dumps(session_data.get('laws_discussed', [])),
            session_data.get('summary'),
            session_data.get('word_count', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def migrate_from_json(self, json_path: Path):
        """Migrate from entities.json to SQLite."""
        print(f"Migrating from {json_path}...")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Migrate persons
        persons_count = 0
        for person in data.get('persons', []):
            entity = Entity(
                id=person.get('id', f"person_{persons_count}"),
                name=person.get('name', ''),
                entity_type='person',
                properties=person
            )
            self.add_entity(entity)
            persons_count += 1
            
            # Add triples for relationships
            if person.get('party'):
                self.add_triple(Triple(
                    subject=entity.id,
                    predicate='member_of',
                    object=person['party'],
                    source='cdep_agent'
                ))
            
            for appearance in person.get('appearances', [])[:5]:
                self.add_triple(Triple(
                    subject=entity.id,
                    predicate='spoke_in',
                    object=appearance,
                    source='cdep_agent'
                ))
        
        # Migrate sessions
        sessions_count = 0
        for session in data.get('sessions', []):
            self.add_session(session)
            sessions_count += 1
            
            # Add triples
            for participant in session.get('participants', [])[:10]:
                self.add_triple(Triple(
                    subject=participant,
                    predicate='spoke_in',
                    object=session.get('id', ''),
                    source='cdep_agent'
                ))
            
            for law in session.get('laws_discussed', [])[:5]:
                self.add_triple(Triple(
                    subject=session.get('id', ''),
                    predicate='discussed',
                    object=law,
                    source='cdep_agent'
                ))
        
        # Migrate laws
        laws_count = 0
        for law in data.get('laws', []):
            entity = Entity(
                id=law.get('id', f"law_{laws_count}"),
                name=law.get('number', ''),
                entity_type='law',
                properties=law
            )
            self.add_entity(entity)
            laws_count += 1
            
            for discussion in law.get('discussions', [])[:5]:
                self.add_triple(Triple(
                    subject=entity.id,
                    predicate='discussed_in',
                    object=discussion,
                    source='cdep_agent'
                ))
        
        print(f"Migration complete: {persons_count} persons, {sessions_count} sessions, {laws_count} laws")
    
    def query(self, subject: str = None, predicate: str = None, 
              obj: str = None, limit: int = 100) -> List[Dict]:
        """Query triples."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM triples WHERE 1=1"
        params = []
        
        if subject:
            query += " AND subject LIKE ?"
            params.append(f"%{subject}%")
        if predicate:
            query += " AND predicate = ?"
            params.append(predicate)
        if obj:
            query += " AND object LIKE ?"
            params.append(f"%{obj}%")
        
        query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_stats(self) -> Dict:
        """Get graph statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM entities")
        stats['entities'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT entity_type, COUNT(*) FROM entities GROUP BY entity_type")
        stats['entities_by_type'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT COUNT(*) FROM triples")
        stats['triples'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT predicate, COUNT(*) FROM triples GROUP BY predicate")
        stats['triples_by_predicate'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT COUNT(*) FROM sessions")
        stats['sessions'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT chamber, COUNT(*) FROM sessions GROUP BY chamber")
        stats['sessions_by_chamber'] = dict(cursor.fetchall())
        
        conn.close()
        return stats


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Knowledge Graph Schema Migration')
    parser.add_argument('--migrate', action='store_true', help='Migrate from entities.json')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--query', nargs=3, metavar=('SUBJECT', 'PREDICATE', 'OBJECT'),
                       help='Query triples')
    parser.add_argument('--add-triple', nargs=3, metavar=('SUBJECT', 'PREDICATE', 'OBJECT'),
                       help='Add a triple')
    
    args = parser.parse_args()
    
    kg = KnowledgeGraph()
    
    if args.migrate:
        json_path = KG_DIR / "entities.json"
        if json_path.exists():
            kg.migrate_from_json(json_path)
        else:
            print(f"entities.json not found at {json_path}")
    
    elif args.query:
        subject, predicate, obj = args.query
        results = kg.query(subject if subject != '*' else None,
                          predicate if predicate != '*' else None,
                          obj if obj != '*' else None)
        print(f"Found {len(results)} triples:")
        for r in results[:10]:
            print(f"  {r['subject']} --{r['predicate']}--> {r['object']} ({r['confidence']:.2f})")
    
    elif args.add_triple:
        subject, predicate, obj = args.add_triple
        kg.add_triple(Triple(subject, predicate, obj, source='manual'))
        print("Triple added")
    
    else:
        stats = kg.get_stats()
        print("=== Knowledge Graph Statistics ===")
        print(f"Entities: {stats['entities']}")
        print(f"  By type: {stats.get('entities_by_type', {})}")
        print(f"Triples: {stats['triples']}")
        print(f"  By predicate: {stats.get('triples_by_predicate', {})}")
        print(f"Sessions: {stats['sessions']}")
        print(f"  By chamber: {stats.get('sessions_by_chamber', {})}")


if __name__ == '__main__':
    main()