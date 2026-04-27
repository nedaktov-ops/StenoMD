#!/usr/bin/env python3
"""Tests for config.py - centralized configuration."""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from config import get_config


def test_config_loads():
    cfg = get_config()
    assert cfg.PROJECT_ROOT is not None
    assert cfg.VAULT_DIR is not None
    assert cfg.ENTITIES_FILE is not None  # knowledge graph entities file


def test_config_paths_exist():
    cfg = get_config()
    # These paths should exist on the system
    assert cfg.PROJECT_ROOT.exists()
    assert cfg.VAULT_DIR.exists()
    # ENTITIES_FILE might not exist yet, but parent dir should
    assert cfg.ENTITIES_FILE.parent.exists()


def test_config_directories():
    cfg = get_config()
    assert cfg.DATA_DIR is not None
    assert cfg.KG_DIR is not None
    # These should be directories
    assert cfg.DATA_DIR.is_dir()
    assert cfg.KG_DIR.is_dir()


if __name__ == "__main__":
    test_config_loads()
    test_config_paths_exist()
    test_config_directories()
    print("All config tests passed!")
