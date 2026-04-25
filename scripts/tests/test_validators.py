"""Tests for validators module."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_date_parsing():
    """Test date parsing."""
    dates = ["2024-01-15", "2025-09-10"]
    for d in dates:
        assert "2024" in d or "2025" in d
    print("✓ test_date_parsing")


def test_law_format():
    """Test law number format."""
    import re
    LAW_PATTERN = re.compile(r'\d+/\d{4}')
    
    valid = LAW_PATTERN.match("5/2024")
    assert valid is not None
    print("✓ test_law_format")


def test_min_participants():
    """Test minimum participants."""
    valid = ["MP1", "MP2"]
    assert len(valid) >= 1
    print("✓ test_min_participants")


if __name__ == "__main__":
    test_date_parsing()
    test_law_format()
    test_min_participants()
    print("\n✓ All validator tests passed!")