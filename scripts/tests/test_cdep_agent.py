"""Tests for cdep_agent URL patterns and regex."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.cdep_agent import EnhancedCDEPAgent
import re


def test_mp_name_pattern_html():
    """Test HTML MP name pattern."""
    MP_NAME_PATTERN_HTML = re.compile(
        r'<font\s+color="#0000FF">(Domnul|Doamna)\s+([A-ZĂÂÎȘȚ][a-zăâîșț\-]+(?:\s+[A-ZĂÂÎȘȚ]\.?)?(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)[:\s]*</font>',
        re.IGNORECASE
    )
    
    html1 = '<font color="#0000FF">Domnul Ion Diaconescu: </font>'
    match1 = MP_NAME_PATTERN_HTML.search(html1)
    assert match1 is not None
    assert match1.group(2) == 'Ion Diaconescu'
    print("✓ test_mp_name_pattern_html")


def test_mp_name_pattern_simple():
    """Test simple MP name pattern."""
    MP_NAME_PATTERN = re.compile(
        r'(?:Domnul|Doamna)\s+([A-ZĂÂÎȘȚ][a-zăâîșț\-]+(?:\s+[A-ZĂÂÎȘȚ]\.?)?(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)[:\s]*',
        re.IGNORECASE
    )
    
    text = "Domnul Ion Diaconescu a declarat"
    match = MP_NAME_PATTERN.search(text)
    assert match is not None
    print("✓ test_mp_name_pattern_simple")


def test_law_pattern():
    """Test law number pattern."""
    LAW_PATTERN = re.compile(
        r'(?:Legea|Proiectul de Lege)\s+(?:nr\.)?\s*(\d+/\d{4})',
        re.IGNORECASE
    )
    
    text = "Legea 5/2024"
    match = LAW_PATTERN.search(text)
    assert match is not None
    assert match.group(1) == '5/2024'
    print("✓ test_law_pattern")


def test_url_patterns():
    """Test URL pattern generation."""
    BASE_URL = 'https://www.cdep.ro'
    year = 2024
    
    patterns = [
        f"{BASE_URL}/pls/steno/steno{year}.stenograma_scris?idl=1&idm=1&ids={{}}",
        f"{BASE_URL}/pls/steno/steno{year}.stenograma?idl=1&idm=1&ids={{}}",
    ]
    
    urls = [p.format(10) for p in patterns]
    assert all('ids=10' in u for u in urls)
    print("✓ test_url_patterns")


def test_session_object():
    """Test Session object."""
    from agents.cdep_agent import Session
    
    session = Session(
        id="test_001",
        date="2024-01-01",
        chamber="deputies",
        title="Test",
        url="http://test.com",
        participants=["MP1"],
        laws_discussed=["1/2024"],
        summary="Test"
    )
    
    assert session.id == "test_001"
    assert session.chamber == "deputies"
    print("✓ test_session_object")


if __name__ == "__main__":
    test_mp_name_pattern_html()
    test_mp_name_pattern_simple()
    test_law_pattern()
    test_url_patterns()
    test_session_object()
    print("\n✓ All cdep_agent tests passed!")