#!/usr/bin/env python3
"""
StenoMD Data Validator - Prevents duplicate extraction
Checks vault for existing sessions and validates data integrity
"""

import re
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def atomic_write(filepath: Path, data: str):
    """Write data atomically using temp file + rename."""
    temp = filepath.with_suffix('.tmp')
    temp.write_text(data, encoding='utf-8')
    temp.replace(filepath)


def atomic_json_write(filepath: Path, data: dict):
    """Write JSON atomically."""
    atomic_write(filepath, json.dumps(data, indent=2, ensure_ascii=False))


MONTHS = {
    "ianuarie": "01", "februarie": "02", "martie": "03", "aprilie": "04",
    "mai": "05", "iunie": "06", "iulie": "07", "august": "08",
    "septembrie": "09", "octombrie": "10", "noiembrie": "11", "decembrie": "12"
}


def parse_session_date(filename: str) -> Optional[str]:
    """Extract YYYY-MM-DD from various date formats in filename."""
    iso_match = re.match(r"(\d{4})-(\d{2})-(\d{2})", filename)
    if iso_match:
        return iso_match.group()
    
    romanian_match = re.match(r"(\d{1,2})-([a-zăâîșț]+)-(\d{4})", filename, re.IGNORECASE)
    if romanian_match:
        day, month_ro, year = romanian_match.groups()
        month = MONTHS.get(month_ro.lower())
        if month:
            return f"{year}-{month}-{int(day):02d}"
    
    return None


class DataValidator:
    """Validates scraped data and checks for duplicates."""
    
    MIN_WORD_COUNT = 100
    MIN_PARTICIPANTS = 1
    VALID_PARTIES = {'PSD', 'PNL', 'USR', 'AUR', 'UDMR', 'SOS', 'POT', 'REPER', 'PER'}
    
    def __init__(self, vault_dir: Path):
        self.vault_dir = vault_dir
        self.sessions_dir = vault_dir / "sessions"
        self._existing_sessions: Dict[str, Dict] = {}
        self._load_existing_sessions()
    
    def refresh_sessions(self):
        """Refresh in-memory cache from disk."""
        self._existing_sessions = {}
        self._load_existing_sessions()
    
    def _load_existing_sessions(self):
        """Load existing session metadata from vault."""
        for chamber in ["senate", "deputies"]:
            chamber_dir = self.sessions_dir / chamber
            if not chamber_dir.exists():
                continue
            
            for md_file in chamber_dir.glob("*.md"):
                if md_file.name == "Index.md":
                    continue
                
                session_id = md_file.stem
                try:
                    content = md_file.read_text(encoding='utf-8')
                    meta = self._parse_session_metadata(content, session_id, chamber)
                    if meta:
                        self._existing_sessions[session_id] = meta
                except Exception:
                    continue
    
    def _parse_session_metadata(self, content: str, session_id: str, chamber: str) -> Optional[Dict]:
        """Parse frontmatter and extract session metadata."""
        meta = {
            'id': session_id,
            'chamber': chamber,
            'date': None,
            'word_count': 0,
            'participants': [],
            'laws_discussed': [],
            'is_complete': False,
            'last_updated': None
        }
        
        if '---' in content:
            parts = content.split('---', 2)
            if len(parts) >= 3:
                fm = parts[1]
                
                date_match = re.search(r'date:\s*(.+)', fm)
                if date_match:
                    meta['date'] = date_match.group(1).strip()
                
                wc_match = re.search(r'word_count:\s*(\d+)', fm)
                if wc_match:
                    meta['word_count'] = int(wc_match.group(1))
                
                laws_match = re.search(r'laws_discussed:\s*(.+)', fm)
                if laws_match:
                    laws_str = laws_match.group(1).strip()
                    if laws_str and laws_str.lower() != 'none':
                        meta['laws_discussed'] = [l.strip() for l in laws_str.split(',') if l.strip()]
                
                part_match = re.search(r'participants:([\s\S]+?)$', fm)
                if part_match:
                    participants_str = part_match.group(1).strip()
                    if participants_str and participants_str.lower() != 'none':
                        lines = [l.strip().lstrip('- ') for l in participants_str.split('\n') if l.strip()]
                        meta['participants'] = [p for p in lines if p and p != 'None']
                
                updated_match = re.search(r'updated:\s*(\d{4}-\d{2}-\d{2})', fm)
                if updated_match:
                    meta['last_updated'] = updated_match.group(1)
        
        is_complete = (
            meta['word_count'] >= self.MIN_WORD_COUNT and
            len(meta['participants']) >= self.MIN_PARTICIPANTS
        )
        meta['is_complete'] = is_complete
        
        return meta
    
    def session_exists(self, date: str, chamber: str) -> bool:
        """Check if session already exists in vault."""
        date_clean = date.replace('.', '-').replace(' ', '-')
        
        date_iso = parse_session_date(date_clean) if date_clean else None
        
        for sid, meta in self._existing_sessions.items():
            if meta['chamber'] != chamber:
                continue
            
            sid_iso = parse_session_date(sid)
            
            if sid_iso and date_iso and sid_iso == date_iso:
                return True
            if meta['date'] and date_clean in meta['date']:
                return True
            if sid == date_clean:
                return True
        
        return False
    
    def get_existing_session(self, date: str, chamber: str) -> Optional[Dict]:
        """Get existing session metadata if it exists."""
        date_clean = date.replace('.', '-').replace(' ', '-')
        
        date_iso = parse_session_date(date_clean) if date_clean else None
        
        for sid, meta in self._existing_sessions.items():
            if meta['chamber'] != chamber:
                continue
            
            sid_iso = parse_session_date(sid)
            
            if sid_iso and date_iso and sid_iso == date_iso:
                return meta
            if meta['date'] and date_clean in meta['date']:
                return meta
            if sid == date_clean:
                return meta
        
        return None
    
    def validate_session(self, data: Dict) -> Tuple[bool, str]:
        """
        Validate session data for integrity, correctness, completeness.
        Returns (is_valid, error_message)
        """
        if not data.get('stenogram_content') and not data.get('summary'):
            return False, "No content to validate"
        
        word_count = data.get('word_count', 0)
        if word_count < self.MIN_WORD_COUNT:
            return False, f"Word count too low: {word_count}"
        
        participants = data.get('participants', [])
        if len(participants) < self.MIN_PARTICIPANTS:
            return False, f"No participants found"
        
        laws = data.get('laws_discussed', [])
        if laws:
            for law in laws:
                if not re.match(r'\d+/\d{4}', law):
                    return False, f"Invalid law format: {law}"
        
        return True, "OK"
    
    def check_duplicate(self, data: Dict, chamber: str) -> bool:
        """Check if this exact session already exists."""
        date = data.get('date', '')
        if not date:
            return False
        
        existing = self.get_existing_session(date, chamber)
        if existing and existing['is_complete']:
            if existing['word_count'] >= data.get('word_count', 0):
                return True
        
        return False
    
    def find_latest_session_date(self, chamber: str) -> Optional[str]:
        """Find the most recent session date in vault for a chamber."""
        chamber_dir = self.sessions_dir / chamber
        if not chamber_dir.exists():
            return None
        
        session_files = [
            f for f in chamber_dir.glob("*.md") 
            if f.name != "Index.md"
        ]
        
        if not session_files:
            return None
        
        latest = max(session_files, key=lambda f: f.stat().st_mtime)
        
        content = latest.read_text(encoding='utf-8')
        date_match = re.search(r'date:\s*(.+)', content)
        if date_match:
            return date_match.group(1).strip()
        
        return latest.stem
    
    def get_session_dates(self, chamber: str) -> List[str]:
        """Get all session dates already extracted for a chamber."""
        dates = []
        chamber_dir = self.sessions_dir / chamber
        
        if not chamber_dir.exists():
            return dates
        
        for f in chamber_dir.glob("*.md"):
            if f.name == "Index.md":
                continue
            
            content = f.read_text(encoding='utf-8')
            date_match = re.search(r'date:\s*(.+)', content)
            if date_match:
                dates.append(date_match.group(1).strip())
        
        return sorted(dates)


def get_validator(vault_dir: Path = None) -> DataValidator:
    """Get validator instance with configured vault path."""
    if vault_dir is None:
        # Use config if available, otherwise fallback
        try:
            from config import get_config
            vault_dir = get_config().VAULT_DIR
        except ImportError:
            vault_dir = Path(__file__).parent.parent.parent / "vault"
    return DataValidator(vault_dir)


if __name__ == "__main__":
    validator = get_validator()
    
    print("=== StenoMD Data Validator ===")
    print(f"Existing Senate sessions: {len([s for s in validator._existing_sessions.values() if s['chamber'] == 'senate'])}")
    print(f"Existing Deputies sessions: {len([s for s in validator._existing_sessions.values() if s['chamber'] == 'deputies'])}")
    
    latest_senate = validator.find_latest_session_date("senate")
    latest_deputy = validator.find_latest_session_date("deputies")
    
    print(f"\nLatest Senate session: {latest_senate or 'None'}")
    print(f"Latest Deputies session: {latest_deputy or 'None'}")