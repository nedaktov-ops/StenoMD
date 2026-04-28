#!/usr/bin/env python3
"""
StenoMD Configuration - Centralized Configuration with Environment Variable Support

SECURITY: Add this file to .gitignore to protect sensitive configuration
Import this module in all scripts instead of hardcoding paths

Usage:
    from scripts.config import PROJECT_ROOT, VAULT_DIR, KG_DIR
    
Environment Variables:
    STENOMD_DIR          - Override project root path
    STENOMD_ALLOWED_ORIGIN - CORS allowed origin (default: localhost)
    STENOMD_MAX_ID       - Max session ID for scraping (default: 200)
    STENOMD_CACHE_TTL    - Cache TTL in seconds (default: 3600)
    STENOMD_LOG_LEVEL    - Logging level (default: INFO)
    STENOMD_DEBUG        - Enable debug mode (default: false)
    STENOMD_OLLAMA_MODEL - Ollama model (default: qwen2.5-coder:1.5b)

Example:
    export STENOMD_DIR=/path/to/project
    export STENOMD_ALLOWED_ORIGIN=localhost
    export STENOMD_DEBUG=true
"""

import os
import logging
from pathlib import Path
from typing import Optional


def get_project_root() -> Path:
    """Get project root directory.
    
    Priority:
    1. STENOMD_DIR environment variable
    2. Default: parent of scripts directory
    """
    env_path = os.environ.get('STENOMD_DIR')
    if env_path:
        return Path(env_path)
    
    current_file = Path(__file__).resolve()
    return current_file.parent.parent


class StenoMDConfig:
    """StenoMD Configuration with environment variable support."""
    
    _instance: Optional['StenoMDConfig'] = None
    
    def __new__(cls) -> 'StenoMDConfig':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._project_root = get_project_root()
        
        self.PROJECT_ROOT = self._project_root
        self.BASE_DIR = self._project_root
        self.VAULT_DIR = self._project_root / "vault"
        self.DATA_DIR = self._project_root / "data"
        self.KG_DIR = self._project_root / "knowledge_graph"
        self.KG_DB = self.KG_DIR / "knowledge_graph.db"
        self.ENTITIES_FILE = self.KG_DIR / "entities.json"
        
        self.MEMORY_DIR = self._project_root / "scripts" / "memory"
        
        self.ALLOWED_ORIGIN = os.environ.get('STENOMD_ALLOWED_ORIGIN', 'localhost')
        self.API_RATE_LIMIT = int(os.environ.get('STENOMD_API_RATE_LIMIT', '100'))
        
        self.MAX_ID = int(os.environ.get('STENOMD_MAX_ID', '200'))
        self.CACHE_TTL = int(os.environ.get('STENOMD_CACHE_TTL', '3600'))
        
        self.LOG_LEVEL = os.environ.get('STENOMD_LOG_LEVEL', 'INFO')
        self.DEBUG = os.environ.get('STENOMD_DEBUG', '').lower() == 'true'
        
        self.OLLAMA_MODEL = os.environ.get('STENOMD_OLLAMA_MODEL', 'qwen2.5-coder:1.5b')
        
        self.RAM_LIMIT_GB = float(os.environ.get('STENOMD_RAM_LIMIT_GB', '4'))
        self.BATCH_SIZE = int(os.environ.get('STENOMD_BATCH_SIZE', self._get_default_batch_size()))
        self.USE_LIGHTWEIGHT_MODEL = self.RAM_LIMIT_GB < 12
        
        self.PROGRESS_FILE = Path('/tmp/stenomd_progress.json')
        self.KG_DB_ALT = self._project_root / '.mempalace' / 'knowledge_graph.sqlite3'
        
        self._setup_logging()
    
    def _get_default_batch_size(self) -> int:
        """Get default batch size based on RAM limit."""
        ram = self.RAM_LIMIT_GB
        if ram >= 16:
            return 50
        elif ram >= 12:
            return 30
        elif ram >= 8:
            return 15
        else:
            return 5
    
    def _setup_logging(self) -> None:
        """Configure logging based on settings."""
        logging.basicConfig(
            level=getattr(logging, self.LOG_LEVEL),
            format='[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def __repr__(self) -> str:
        return f"StenoMDConfig(root={self._project_root})"
    
    def validate(self) -> bool:
        """Validate configuration directories exist."""
        required = [self.VAULT_DIR, self.DATA_DIR, self.KG_DIR]
        for directory in required:
            if not directory.exists():
                logging.warning(f"Directory not found: {directory}")
        return True


def get_config() -> StenoMDConfig:
    """Get configuration singleton (lazy-loaded)."""
    return StenoMDConfig()


_config = get_config()
PROJECT_ROOT = _config.PROJECT_ROOT
VAULT_DIR = _config.VAULT_DIR
DATA_DIR = _config.DATA_DIR
KG_DIR = _config.KG_DIR
KG_DB = _config.KG_DB
ENTITIES_FILE = _config.ENTITIES_FILE
ALLOWED_ORIGIN = _config.ALLOWED_ORIGIN
MAX_ID = _config.MAX_ID
CACHE_TTL = _config.CACHE_TTL
DEBUG = _config.DEBUG
LOG_LEVEL = _config.LOG_LEVEL
OLLAMA_MODEL = _config.OLLAMA_MODEL
RAM_LIMIT_GB = _config.RAM_LIMIT_GB
BATCH_SIZE = _config.BATCH_SIZE
USE_LIGHTWEIGHT_MODEL = _config.USE_LIGHTWEIGHT_MODEL


if __name__ == "__main__":  # pragma: no cover
    config = get_config()
    print(f"Project Root: {config.PROJECT_ROOT}")
    print(f"Vault Dir: {config.VAULT_DIR}")
    print(f" KG Dir: {config.KG_DIR}")
    print(f" KG DB: {config.KG_DB}")
    print(f"Allowed Origin: {config.ALLOWED_ORIGIN}")
    print(f"Max ID: {config.MAX_ID}")
    print(f"Cache TTL: {config.CACHE_TTL}")
    print(f"Debug: {config.DEBUG}")
    print(f"Ollama Model: {config.OLLAMA_MODEL}")
    print(f"\nValidation: {config.validate()}")