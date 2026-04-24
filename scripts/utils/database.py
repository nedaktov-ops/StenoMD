"""
Database Connection Pool

Provides thread-safe database connections for memory system.
"""

import sqlite3
import threading
from pathlib import Path
from typing import Optional


class DatabasePool:
    """
    Simple database connection pool.
    
    Note: Python's sqlite3 doesn't support true pooling,
    but this provides thread-safe connection management.
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(Path(__file__).parent.parent / 'memory' / 'memory.db')
        self._local = threading.local()
        self._lock = threading.Lock()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'connection'):
            self._local.connection = self._create_connection()
        return self._local.connection
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create new database connection."""
        conn = sqlite3.connect(
            self.db_path,
            timeout=10,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn
    
    def execute(self, sql: str, params: tuple = ()):
        """Execute SQL statement."""
        conn = self.get_connection()
        return conn.execute(sql, params)
    
    def executemany(self, sql: str, params_list: list):
        """Execute SQL statement with multiple parameter sets."""
        conn = self.get_connection()
        return conn.executemany(sql, params_list)
    
    def executescript(self, sql: str):
        """Execute multiple SQL statements."""
        conn = self.get_connection()
        conn.executescript(sql)
    
    def commit(self):
        """Commit transaction."""
        conn = self.get_connection()
        conn.commit()
    
    def close(self):
        """Close thread-local connection."""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            delattr(self._local, 'connection')
    
    def close_all(self):
        """Close all connections (use on shutdown)."""
        self.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        return False


class Transaction:
    """Context manager for database transactions."""
    
    def __init__(self, pool: DatabasePool):
        self.pool = pool
        self.committed = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and not self.committed:
            self.pool.commit()
        return False
    
    def commit(self):
        """Explicitly commit transaction."""
        self.pool.commit()
        self.committed = True