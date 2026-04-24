"""
Database schema and migrations for Memory System.

Provides SQLite schema definitions and migration utilities.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


class DatabaseSchema:
    """Manages database schema and migrations."""
    
    SCHEMA_VERSION = 2
    
    CREATE_TABLES_SQL = """
        -- Actions table: stores all agent actions
        CREATE TABLE IF NOT EXISTS actions (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT,
            severity TEXT,
            description TEXT,
            location TEXT,
            command TEXT,
            files_affected TEXT,
            parameters TEXT,
            success INTEGER,
            duration_ms INTEGER,
            result TEXT,
            side_effects TEXT,
            mode TEXT,
            project_hash TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Patterns table: learned fix patterns
        CREATE TABLE IF NOT EXISTS patterns (
            id TEXT PRIMARY KEY,
            issue_pattern TEXT NOT NULL,
            fix_pattern TEXT NOT NULL,
            success_count INTEGER DEFAULT 0,
            failure_count INTEGER DEFAULT 0,
            total_uses INTEGER DEFAULT 0,
            avg_duration_ms INTEGER,
            first_seen TEXT,
            last_seen TEXT,
            confidence REAL DEFAULT 0.5,
            metadata TEXT
        );
        
        -- Knowledge table: semantic knowledge graph
        CREATE TABLE IF NOT EXISTS knowledge (
            id TEXT PRIMARY KEY,
            entity_type TEXT,
            entity_name TEXT,
            predicate TEXT,
            value TEXT,
            confidence REAL DEFAULT 1.0,
            source_action TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            valid_from TEXT,
            valid_to TEXT
        );
        
        -- Insights table: generated insights
        CREATE TABLE IF NOT EXISTS insights (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            insight_type TEXT,
            content TEXT,
            supporting_data TEXT,
            confidence REAL
        );
        
        -- Metadata table: schema versioning
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    """
    
    CREATE_INDEXES_SQL = """
        CREATE INDEX IF NOT EXISTS idx_actions_timestamp ON actions(timestamp);
        CREATE INDEX IF NOT EXISTS idx_actions_type ON actions(type);
        CREATE INDEX IF NOT EXISTS idx_actions_success ON actions(success);
        CREATE INDEX IF NOT EXISTS idx_actions_description ON actions(description);
        
        CREATE INDEX IF NOT EXISTS idx_patterns_issue ON patterns(issue_pattern);
        CREATE INDEX IF NOT EXISTS idx_patterns_fix ON patterns(fix_pattern);
        CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON patterns(confidence);
        
        CREATE INDEX IF NOT EXISTS idx_knowledge_entity ON knowledge(entity_name);
        CREATE INDEX IF NOT EXISTS idx_knowledge_predicate ON knowledge(predicate);
        
        CREATE INDEX IF NOT EXISTS idx_insights_timestamp ON insights(timestamp);
        CREATE INDEX IF NOT EXISTS idx_insights_type ON insights(insight_type);
    """
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.db_path = memory_dir / 'memory.db'
        self._connection: Optional[sqlite3.Connection] = None
        
        # Initialize database
        self._init_db()
        
    def _init_db(self):
        """Initialize database and run migrations."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = self._conn()
        
        # Create tables
        conn.executescript(self.CREATE_TABLES_SQL)
        conn.executescript(self.CREATE_INDEXES_SQL)
        
        # Set schema version
        self._set_metadata('schema_version', str(self.SCHEMA_VERSION))
        self._set_metadata('created_at', datetime.now().isoformat())
        
        conn.commit()
        
    def _conn(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.db_path),
                timeout=10,
                check_same_thread=False
            )
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA foreign_keys=ON")
        return self._connection
    
    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def _set_metadata(self, key: str, value: str):
        """Set metadata value."""
        conn = self._conn()
        conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            (key, value)
        )
    
    def get_metadata(self, key: str) -> Optional[str]:
        """Get metadata value."""
        conn = self._conn()
        row = conn.execute(
            "SELECT value FROM metadata WHERE key = ?",
            (key,)
        ).fetchone()
        return row['value'] if row else None
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute SQL statement."""
        conn = self._conn()
        return conn.execute(sql, params)
    
    def executescript(self, sql: str):
        """Execute multiple SQL statements."""
        conn = self._conn()
        conn.executescript(sql)
    
    def commit(self):
        """Commit transaction."""
        if self._connection:
            self._connection.commit()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        self.close()
        return False