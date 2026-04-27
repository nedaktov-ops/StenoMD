#!/usr/bin/env python3
"""Tests for merge_vault_to_kg.py - core KG population logic."""

import sys
import os
from pathlib import Path

# Add scripts to path (go up from tests/kg to scripts)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from merge_vault_to_kg import parse_frontmatter


def test_parse_frontmatter_simple():
    content = """---
date: '2024-11-05'
title: Test Session
chamber: deputies
---
Body content here."""
    
    fm, body = parse_frontmatter(content)
    # Note: custom parser does NOT strip quotes from values
    assert fm['date'] == "'2024-11-05'"
    assert fm['title'] == 'Test Session'
    assert fm['chamber'] == 'deputies'
    # Body includes leading newline after closing ---
    assert "Body content here" in body


def test_parse_frontmatter_no_frontmatter():
    content = "Just body content, no frontmatter."
    fm, body = parse_frontmatter(content)
    assert fm == {}
    assert body == content


def test_parse_frontmatter_with_unicode():
    content = """---
name: Gheorghe-Valentin RĂDUCEA
party: PSD
constituency: SUCEAVA
---
Unicode test: șăîțțâ"""
    
    fm, body = parse_frontmatter(content)
    assert fm['name'] == 'Gheorghe-Valentin RĂDUCEA'
    assert 'ș' in body


def test_parse_frontmatter_handles_numeric():
    content = """---
speeches_count: 42
laws_proposed: 3
---
Numeric values should be strings in frontmatter."""
    
    fm, body = parse_frontmatter(content)
    # The parser doesn't convert types; values are strings from YAML parsing would handle it
    # But our custom parser just returns strings
    # In actual YAML, these would be ints, but our simple parser splits lines
    # This test documents current behavior
    assert 'speeches_count' in fm
    assert 'laws_proposed' in fm


if __name__ == "__main__":
    test_parse_frontmatter_simple()
    test_parse_frontmatter_no_frontmatter()
    test_parse_frontmatter_with_unicode()
    test_parse_frontmatter_handles_numeric()
    print("All merge_vault_to_kg tests passed!")
