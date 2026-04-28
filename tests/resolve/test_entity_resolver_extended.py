#!/usr/bin/env python3
"""Extended tests for resolve/entity_resolver.py - match logic."""

import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from resolve.entity_resolver import EntityResolver, MatchResult, CanonicalMP


def test_resolve_exact_match():
    resolver = EntityResolver()
    if not resolver.canonical_mps:
        pytest.skip("No canonical MPs loaded")
    resolver.ollama_model = None
    sample_mp = next(iter(resolver.canonical_mps.values()))
    result = resolver.resolve(sample_mp.name)
    assert result.canonical_id == sample_mp.id
    assert result.method == 'exact'
    assert result.confidence == 1.0
    assert result.canonical_name == sample_mp.name


def test_resolve_normalized_match():
    resolver = EntityResolver()
    if not resolver.canonical_mps:
        pytest.skip("No canonical MPs loaded")
    resolver.ollama_model = None
    # Find an MP with diacritic difference
    for mp in resolver.canonical_mps.values():
        norm = mp.normalized_name
        name_lower = mp.name.lower()
        if norm != name_lower and len(mp.name) > 5:
            result = resolver.resolve(norm)
            # Could be normalized or fuzzy (if substring)
            assert result.canonical_id == mp.id
            assert result.method in ('normalized', 'fuzzy', 'exact')
            break
    else:
        pytest.skip("No MP with diacritic difference found")


def test_resolve_fuzzy_match_substring():
    resolver = EntityResolver()
    if not resolver.canonical_mps:
        pytest.skip("No canonical MPs loaded")
    resolver.ollama_model = None
    # Pick an MP with normalized name longer than 10 chars
    for mp in resolver.canonical_mps.values():
        norm = mp.normalized_name
        if len(norm) > 10:
            # Create a substring variant (remove last two chars)
            variant = norm[:-2]
            if len(variant) >= 5 and variant != norm:
                result = resolver.resolve(variant)
                # Fuzzy condition: normalized in or vice versa
                assert result.method == 'fuzzy', f"Expected fuzzy, got {result.method}"
                assert result.canonical_id == mp.id
                break
    else:
        pytest.skip("No suitable MP for fuzzy test")


def test_resolve_chamber_filter():
    resolver = EntityResolver()
    resolver.ollama_model = None
    # Create a fake MP with diacritic to ensure exact match fails
    fake_mp = CanonicalMP(
        id='sen_123',
        name='Test Senatôr',
        normalized_name='test senator',
        chamber='senate'
    )
    resolver.canonical_mps = {'sen_123': fake_mp}
    # Normalized input that matches normalized_name but not exact name
    result = resolver.resolve('test senator', chamber='deputies')
    # Normalized match should happen but be filtered due to chamber mismatch
    assert result.method == 'none'
    assert result.canonical_id is None
    # Without chamber, should get normalized match
    result2 = resolver.resolve('test senator')
    assert result2.method == 'normalized'
    assert result2.canonical_id == 'sen_123'


def test_match_result_creation():
    result = MatchResult("mp_1", "Test MP", 0.95, "exact")
    assert result.canonical_id == "mp_1"
    assert result.canonical_name == "Test MP"
    assert result.confidence == 0.95
    assert result.method == "exact"
