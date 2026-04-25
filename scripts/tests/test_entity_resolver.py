"""Tests for entity_resolver module."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_resolver_creation():
    """Test resolver creation."""
    from resolve.entity_resolver import EntityResolver
    
    resolver = EntityResolver()
    assert resolver is not None
    print("✓ test_resolver_creation")


def test_canonical_mps_loaded():
    """Test canonical MPs loaded."""
    from resolve.entity_resolver import EntityResolver
    
    resolver = EntityResolver()
    assert len(resolver.canonical_mps) >= 100
    print(f"✓ test_canonical_mps_loaded ({len(resolver.canonical_mps)} MPs)")


def test_exact_match():
    """Test exact match."""
    from resolve.entity_resolver import EntityResolver
    
    resolver = EntityResolver()
    result = resolver.resolve('Kelemen Hunor', 'deputies')
    
    assert result is not None
    print("✓ test_exact_match")


def test_match_result():
    """Test MatchResult."""
    from resolve.entity_resolver import MatchResult
    
    result = MatchResult("test-001", "Test Name", 0.95, "exact")
    assert result.canonical_id == "test-001"
    assert result.confidence == 0.95
    print("✓ test_match_result")


def test_db_count():
    """Test database count."""
    import sqlite3
    
    conn = sqlite3.connect('resolve/canonical.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM canonical_mps')
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count >= 100
    print(f"✓ test_db_count ({count} MPs)")


if __name__ == "__main__":
    test_resolver_creation()
    test_canonical_mps_loaded()
    test_exact_match()
    test_match_result()
    test_db_count()
    print("\n✓ All entity_resolver tests passed!")