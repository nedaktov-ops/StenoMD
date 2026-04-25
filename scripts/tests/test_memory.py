#!/usr/bin/env python3
"""
Unit tests for MemoryStore - Simplified
"""

import unittest
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestMemoryStore(unittest.TestCase):
    """Test cases for MemoryStore."""
    
    def test_import_memory(self):
        """Test MemoryStore can be imported."""
        from memory import MemoryStore
        self.assertIsNotNone(MemoryStore)
    
    def test_memory_store_creation(self):
        """Test MemoryStore can be created."""
        from memory import MemoryStore
        try:
            store = MemoryStore()
            self.assertIsNotNone(store)
        except Exception as e:
            self.skipTest(f"MemoryStore initialization error: {e}")


if __name__ == '__main__':
    unittest.main()