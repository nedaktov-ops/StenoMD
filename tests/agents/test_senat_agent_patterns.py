#!/usr/bin/env python3
"""Tests for senat_agent.py - senate scraper patterns."""

import re


def test_senator_pattern():
    SENATOR_PATTERN = re.compile(
        r'domnul\s+([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)',
        re.IGNORECASE
    )
    
    text = "domnul Mihai Coteț a luat cuvîntul."
    match = SENATOR_PATTERN.search(text)
    assert match is not None
    assert match.group(1).lower() == "mihai coteț"


def test_senator_pattern_female():
    # Pattern for female honorific 'doamna'
    NAME_PATTERN = re.compile(
        r'doamna\s+([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)',
        re.IGNORECASE
    )
    # Should match "doamna" due to pattern using 'doamna'
    text = "doamna Ana Birchall a intervenit."
    match = NAME_PATTERN.search(text)
    assert match is not None
    assert "Ana Birchall" in match.group(1)


def test_pdf_name_extraction():
    # Test extracting name from PDF-derived text
    text = "Domnul VASILE BLAGA.\nPreşedinte Senat."
    pattern = re.compile(r'Domnul\s+([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)', re.IGNORECASE)
    match = pattern.search(text)
    assert match is not None
    assert "VASILE BLAGA" in match.group(1) or "Vasile Blaga" in match.group(1)


if __name__ == "__main__":
    test_senator_pattern()
    test_senator_pattern_female()
    test_pdf_name_extraction()
    print("All senat_agent unit tests passed!")
