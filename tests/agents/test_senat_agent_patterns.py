#!/usr/bin/env python3
"""Tests for senat_agent.py - senate scraper patterns."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

# Import actual patterns from senat_agent to ensure module load coverage
from agents.senat_agent import SENATOR_PATTERN, NAME_PATTERN


def test_senator_pattern():
    text = "domnul Mihai Coteț a luat cuvîntul."
    match = SENATOR_PATTERN.search(text)
    assert match is not None
    assert match.group(1).lower() == "mihai coteț"


def test_senator_pattern_female():
    # Should match "doamna" because NAME_PATTERN uses 'doamna'
    text = "doamna Ana Birchall a intervenit."
    match = NAME_PATTERN.search(text)
    assert match is not None
    assert "Ana Birchall" in match.group(1)


def test_pdf_name_extraction():
    # Test extracting name from PDF-derived text using SENATOR_PATTERN (Domnul)
    text = "Domnul VASILE BLAGA.\nPreşedinte Senat."
    match = SENATOR_PATTERN.search(text)
    assert match is not None
    # The match may preserve case; ensure it contains VASILE BLAGA (case-insensitive)
    matched = match.group(1).upper()
    assert "VASILE" in matched and "BLAGA" in matched


if __name__ == "__main__":
    test_senator_pattern()
    test_senator_pattern_female()
    test_pdf_name_extraction()
    print("All senat_agent unit tests passed!")
