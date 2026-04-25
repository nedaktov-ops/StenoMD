#!/usr/bin/env python3
"""
Unit tests for EntityResolver - Simplified
"""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestEntityResolver(unittest.TestCase):
    """Test cases for EntityResolver."""
    
    def test_import_entity_resolver(self):
        """Test EntityResolver can be imported."""
        from resolve.entity_resolver import EntityResolver
        self.assertIsNotNone(EntityResolver)
    
    def test_name_normalizations(self):
        """Test name normalizations exist."""
        from resolve.entity_resolver import EntityResolver
        resolver = EntityResolver()
        
        self.assertIn('ă', resolver.NAME_NORMALIZATIONS)
        self.assertIn('ş', resolver.NAME_NORMALIZATIONS)
        self.assertIn('ț', resolver.NAME_NORMALIZATIONS)
    
    def test_honorifics(self):
        """Test honorifics are defined."""
        from resolve.entity_resolver import EntityResolver
        resolver = EntityResolver()
        
        self.assertIn('domnul', resolver.HONORIFICS)
        self.assertIn('doamna', resolver.HONORIFICS)


if __name__ == '__main__':
    unittest.main()