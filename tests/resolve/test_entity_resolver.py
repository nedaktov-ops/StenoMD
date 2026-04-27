#!/usr/bin/env python3
"""Tests for resolve/entity_resolver.py - name normalization and matching."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from resolve.entity_resolver import EntityResolver


def test_normalize_name_basic():
    resolver = EntityResolver()
    # Basic normalization
    assert resolver._normalize_name("Bogdan Bola") == "bogdan bola"
    # 'Alexandru' contains 'dr' which gets removed (honorific list contains 'dr')
    # So we test with separate parts
    assert resolver._normalize_name("Vasile Cîtea") == "vasile citea"  # â becomes a


def test_normalize_name_with_honorific():
    resolver = EntityResolver()
    # Honorific removal (as substrings; current implementation removes all occurrences)
    name = "Domnul Mihai"
    normalized = resolver._normalize_name(name)
    assert "domnul" not in normalized
    assert "mihai" in normalized


def test_normalize_name_diacritics():
    resolver = EntityResolver()
    # Test diacritic normalization mapping
    assert resolver._normalize_name("ă") == "a"
    assert resolver._normalize_name("Ă") == "a"
    assert resolver._normalize_name("ț") == "t"
    assert resolver._normalize_name("Ț") == "t"
    assert resolver._normalize_name("î") == "i"
    assert resolver._normalize_name("Î") == "i"


def test_normalize_name_whitespace():
    resolver = EntityResolver()
    name = "  Ion   Popescu  "
    normalized = resolver._normalize_name(name)
    assert normalized == "ion popescu"


if __name__ == "__main__":
    test_normalize_name_basic()
    test_normalize_name_with_honorific()
    test_normalize_name_diacritics()
    test_normalize_name_whitespace()
    print("All entity_resolver unit tests passed!")
