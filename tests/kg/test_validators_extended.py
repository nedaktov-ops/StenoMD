#!/usr/bin/env python3
"""Extended tests for validators.DataValidator class."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from validators import DataValidator


def test_parse_session_metadata_full():
    # Note: participants should be last in frontmatter to avoid being merged with other fields
    content = """---
date: '2024-11-05'
title: Test Session
word_count: 7500
participants:
  - Ion Popescu
  - Ana Ionescu
---
Body text."""
    validator = DataValidator(Path("/tmp/unused"))
    meta = validator._parse_session_metadata(content, "2024-11-05", "deputies")
    # Quoted values include quotes
    assert meta['date'] == "'2024-11-05'"
    assert meta['word_count'] == 7500
    assert meta['participants'] == ['Ion Popescu', 'Ana Ionescu']
    assert meta['laws_discussed'] == []  # no laws_discussed field
    assert meta['is_complete'] is True
    assert meta['chamber'] == 'deputies'
    assert meta['id'] == '2024-11-05'


def test_parse_session_metadata_minimal():
    content = "---\ndate: '2024-11-05'\n---\nMinimal body."
    validator = DataValidator(Path("/tmp/unused"))
    meta = validator._parse_session_metadata(content, "2024-11-05", "deputies")
    assert meta['date'] == "'2024-11-05'"
    assert meta['word_count'] == 0
    assert meta['participants'] == []
    assert meta['laws_discussed'] == []
    assert meta['is_complete'] is False


def test_parse_session_metadata_with_missing_date():
    content = "---\ntitle: No Date\n---\nBody."
    validator = DataValidator(Path("/tmp/unused"))
    meta = validator._parse_session_metadata(content, "fallback-id", "deputies")
    assert meta['id'] == 'fallback-id'
    assert meta['date'] is None
    assert meta['word_count'] == 0


def test_data_validator_refresh_sessions_loads_files(tmp_path):
    vault = tmp_path / "vault"
    sess_dir = vault / "sessions" / "deputies"
    sess_dir.mkdir(parents=True)
    (sess_dir / "2024-01-01.md").write_text("""---
date: '2024-01-01'
word_count: 500
participants:
  - Test User
---
Content.""")
    (sess_dir / "2024-01-02.md").write_text("""---
date: '2024-01-02'
word_count: 50
participants:
  - X
---
Short.""")
    validator = DataValidator(vault)
    validator.refresh_sessions()
    assert len(validator._existing_sessions) == 2
    assert "2024-01-01" in validator._existing_sessions
    assert validator._existing_sessions["2024-01-01"]['is_complete'] is True
    assert validator._existing_sessions["2024-01-02"]['is_complete'] is False


def test_data_validator_session_exists_match_iso(tmp_path):
    vault = tmp_path / "vault"
    sess_dir = vault / "sessions" / "deputies"
    sess_dir.mkdir(parents=True)
    (sess_dir / "2024-11-05.md").write_text("""---
date: '2024-11-05'
word_count: 100
participants: []
---
""")
    validator = DataValidator(vault)
    validator.refresh_sessions()
    assert validator.session_exists("2024-11-05", "deputies") is True
    assert validator.session_exists("2024-11-06", "deputies") is False


def test_data_validator_session_exists_romanian_date(tmp_path):
    vault = tmp_path / "vault"
    sess_dir = vault / "sessions" / "deputies"
    sess_dir.mkdir(parents=True)
    # Use Romanian month name in filename
    (sess_dir / "05-noiembrie-2024.md").write_text("""---
date: '5 noiembrie 2024'
word_count: 100
participants: []
---
""")
    validator = DataValidator(vault)
    validator.refresh_sessions()
    # Both ISO and Romanian formats should match
    assert validator.session_exists("05-noiembrie-2024", "deputies") is True
    assert validator.session_exists("2024-11-05", "deputies") is True


def test_data_validator_initialization_with_missing_vault():
    # Should not raise even if vault dir doesn't exist
    vault = Path("/tmp/does_not_exist_12345")
    validator = DataValidator(vault)
    assert validator.sessions_dir == vault / "sessions"
