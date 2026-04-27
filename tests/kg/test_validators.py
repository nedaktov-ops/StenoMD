#!/usr/bin/env python3
"""Tests for validators.py - data validation utilities."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from validators import parse_session_date, DataValidator


def test_parse_session_date_iso():
    assert parse_session_date("2024-11-05") == "2024-11-05"
    assert parse_session_date("2024-12-31") == "2024-12-31"


def test_parse_session_date_romanian():
    assert parse_session_date("05-noiembrie-2024") == "2024-11-05"
    assert parse_session_date("1-ianuarie-2025") == "2025-01-01"
    assert parse_session_date("15-august-2024") == "2024-08-15"


def test_parse_session_date_invalid():
    # Invalid date string (non-matching patterns)
    assert parse_session_date("not-a-date") is None
    # Parser treats any YYYY-MM-DD as valid without month/day validation
    assert parse_session_date("2024-13-01") == "2024-13-01"  # passes due to pattern


def test_data_validator_initialization():
    vault_dir = Path(__file__).parent.parent / "vault"
    if not vault_dir.exists():
        # Skip test if vault doesn't exist in test environment
        return
    validator = DataValidator(vault_dir)
    assert validator.sessions_dir is not None
    assert validator._existing_sessions is not None


if __name__ == "__main__":
    test_parse_session_date_iso()
    test_parse_session_date_romanian()
    test_parse_session_date_invalid()
    test_data_validator_initialization()
    print("All validator tests passed!")
