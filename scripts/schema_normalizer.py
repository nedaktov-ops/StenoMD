#!/usr/bin/env python3
"""
Schema validator and migrator for StenoMD vault.
Fixes schema inconsistencies and normalizes to unified schema v2.0.
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import yaml

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
VAULT_DIR = PROJECT_DIR / "vault"

ROMANIAN_MONTHS = {
    'ianuarie': '01', 'februarie': '02', 'martie': '03',
    'aprilie': '04', 'mai': '05', 'iunie': '06',
    'iulie': '07', 'august': '08', 'septembrie': '09',
    'octombrie': '10', 'noiembrie': '11', 'decembrie': '12'
}

DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
ROMANIAN_DATE_PATTERN = re.compile(r'(\d{1,2})\s+(\w+)\s+(\d{4})')


def normalize_date(date_val: Any) -> str:
    """Convert any date format to YYYY-MM-DD string."""
    if isinstance(date_val, datetime):
        return date_val.strftime("%Y-%m-%d")
    elif hasattr(date_val, 'strftime'):
        return date_val.strftime("%Y-%m-%d")
    
    date_str = str(date_val).strip()
    
    if DATE_PATTERN.match(date_str):
        return date_str
    
    match = ROMANIAN_DATE_PATTERN.match(date_str.lower())
    if match:
        day, month_ro, year = match.groups()
        month = ROMANIAN_MONTHS.get(month_ro, '01')
        return f"{year}-{month}-{day.zfill(2)}"
    
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        return dt.strftime("%Y-%m-%d")
    except:
        pass
    
    raise ValueError(f"Unknown date format: {date_val}")


def normalize_chamber(chamber: str) -> str:
    """Normalize chamber value to lowercase."""
    chamber = str(chamber).lower().strip()
    if chamber in ['deputies', 'deputy', 'camera', 'cdep', 'camera deputatilor']:
        return 'deputies'
    elif chamber in ['senate', 'senat', 'senator', 'senatul']:
        return 'senate'
    elif chamber in ['joint', 'comuna', 'joint_session']:
        return 'joint'
    return chamber


def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """Parse YAML frontmatter from content."""
    if '---' not in content:
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    fm_text = parts[1]
    body = parts[2]
    
    try:
        fm = yaml.safe_load(fm_text) or {}
    except:
        fm = {}
    
    return fm, body


def fix_session_schema(content: str, filepath: Path) -> Tuple[str, List[str]]:
    """Fix session schema and return (fixed_content, list of changes)."""
    changes = []
    fm, body = parse_frontmatter(content)
    
    if not fm:
        return content, ["No frontmatter found"]
    
    if 'date' in fm:
        try:
            old_date = fm['date']
            new_date = normalize_date(old_date)
            if old_date != new_date:
                fm['date'] = new_date
                changes.append(f"date: {old_date} -> {new_date}")
        except ValueError as e:
            changes.append(f"date error: {e}")
    
    if 'chamber' in fm:
        old_chamber = fm['chamber']
        new_chamber = normalize_chamber(old_chamber)
        if old_chamber != new_chamber:
            fm['chamber'] = new_chamber
            changes.append(f"chamber: {old_chamber} -> {new_chamber}")
    
    if 'laws_discussed' in fm and fm['laws_discussed'] is None:
        fm['laws_discussed'] = []
        changes.append("laws_discussed: None -> []")
    
    if changes:
        new_fm = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
        content = f"---\n{new_fm}---\n{body}"
    
    return content, changes


def fix_session_file(filepath: Path, dry_run: bool = True) -> List[str]:
    """Fix a single session file."""
    content = filepath.read_text()
    new_content, changes = fix_session_schema(content, filepath)
    
    if changes and not dry_run:
        filepath.write_text(new_content)
        print(f"Fixed: {filepath.name}: {changes}")
    
    return changes


def fix_all_sessions(dry_run: bool = True) -> Dict[str, int]:
    """Fix all session files."""
    stats = {'fixed': 0, 'unchanged': 0, 'errors': 0}
    
    sessions_dirs = [
        VAULT_DIR / "sessions" / "deputies",
        VAULT_DIR / "sessions" / "senate"
    ]
    
    for sessions_dir in sessions_dirs:
        if not sessions_dir.exists():
            continue
            
        for filepath in sessions_dir.glob("*.md"):
            if filepath.name == "Index.md":
                continue
            
            try:
                changes = fix_session_file(filepath, dry_run)
                if changes:
                    stats['fixed'] += 1
                    print(f"  {filepath.relative_to(VAULT_DIR)}: {changes}")
                else:
                    stats['unchanged'] += 1
            except Exception as e:
                stats['errors'] += 1
                print(f"  ERROR {filepath.name}: {e}")
    
    return stats


def main():
    """Main entry point."""
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    
    print("=" * 60)
    print("Schema Unification Phase 1: Fixing session schemas")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print()
    
    stats = fix_all_sessions(dry_run)
    
    print()
    print(f"Results: {stats['fixed']} fixed, {stats['unchanged']} unchanged, {stats['errors']} errors")
    
    if dry_run:
        print("\nRun without --dry-run to apply changes.")
    
    return 0 if stats['errors'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())