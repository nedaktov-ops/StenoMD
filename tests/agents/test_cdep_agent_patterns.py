#!/usr/bin/env python3
"""Tests for cdep_agent.py - scraping utility functions."""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

# Import actual patterns from cdep_agent to ensure module load coverage
from agents.cdep_agent import MP_NAME_PATTERN_HTML, LAW_PATTERNS


def test_mp_name_pattern_html():
    html = '<font color="#0000FF">Domnul Bogdan Alexandru Bola</font>'
    match = MP_NAME_PATTERN_HTML.search(html)
    assert match is not None
    assert match.group(1) == "Domnul"
    assert match.group(2) == "Bogdan Alexandru Bola"


def test_law_pattern():
    text = "Legea 123/2024 a fost adoptată."
    # Use each pattern in LAW_PATTERNS to find matches
    matches = []
    for pattern in LAW_PATTERNS:
        matches.extend(re.findall(pattern, text, re.IGNORECASE))
    assert '123/2024' in matches

    text2 = "Proiectul de lege 456/2025 va fi discutată."
    matches2 = []
    for pattern in LAW_PATTERNS:
        matches2.extend(re.findall(pattern, text2, re.IGNORECASE))
    assert '456/2025' in matches2


def test_date_in_url():
    url = "https://www.cdep.ro/pls/steno/steno2024.stenograma_scris?idl=1&idm=1&ids=10&prn=1"
    year_match = re.search(r'steno(\d{4})', url)
    assert year_match is not None
    assert year_match.group(1) == "2024"


if __name__ == "__main__":
    test_mp_name_pattern_html()
    test_law_pattern()
    test_date_in_url()
    print("All cdep_agent unit tests passed!")
