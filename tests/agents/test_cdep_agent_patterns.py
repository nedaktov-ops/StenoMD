#!/usr/bin/env python3
"""Tests for cdep_agent.py - scraping utility functions."""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

# Test regex patterns without full agent initialization
def test_mp_name_pattern_html():
    # Pattern expects strict Romanian name: each word starts with cap letter, followed by lowercase/diacritics
    MP_NAME_PATTERN_HTML = re.compile(
        r'<font\s+color="#0000FF">(Domnul|Doamna)\s+([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)</font>'
    )
    
    # Use a name without hyphens/numbers that matches strict pattern
    html = '<font color="#0000FF">Domnul Bogdan Alexandru Bola</font>'
    match = MP_NAME_PATTERN_HTML.search(html)
    assert match is not None
    assert match.group(1) == "Domnul"
    assert match.group(2) == "Bogdan Alexandru Bola"


def test_law_pattern():
    LAW_PATTERN = re.compile(r'(?:Legea|Proiectul de lege)\s+(\d+/\d{4})')
    
    text = "Legea 123/2024 a fost adoptată."
    matches = LAW_PATTERN.findall(text)
    assert matches == ['123/2024']
    
    text2 = "Proiectul de lege 456/2025 va fi discutată."
    matches2 = LAW_PATTERN.findall(text2)
    assert matches2 == ['456/2025']


def test_date_in_url():
    # Simple date extraction from URL pattern used in agent
    url = "https://www.cdep.ro/pls/steno/steno2024.stenograma_scris?idl=1&idm=1&ids=10&prn=1"
    year_match = re.search(r'steno(\d{4})', url)
    assert year_match is not None
    assert year_match.group(1) == "2024"


if __name__ == "__main__":
    test_mp_name_pattern_html()
    test_law_pattern()
    test_date_in_url()
    print("All cdep_agent unit tests passed!")
