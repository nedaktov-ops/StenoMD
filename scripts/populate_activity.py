#!/usr/bin/env python3
"""Populate speeches_count and laws_proposed from activity data."""

import json
import re
from pathlib import Path

VAULT_DIR = Path("vault/politicians/deputies")
DATA_DIR = Path("data")

def load_activity_data():
    """Load activity stats by idm."""
    with open(DATA_DIR / "deputy_activity_stats.json") as f:
        data = json.load(f)
    mapping = {}
    for entry in data:
        idm = str(entry.get('idm', ''))
        if idm:
            mapping[idm] = {
                'speeches': entry.get('speeches', 0),
                'proposals': entry.get('proposals', 0),
                'motions': entry.get('motions', 0)
            }
    print(f"Loaded activity data for {len(mapping)} idm values")
    return mapping

def main():
    activity = load_activity_data()
    
    files = list(VAULT_DIR.glob("*.md"))
    updated = 0
    
    for f in files:
        content = f.read_text(encoding='utf-8')
        
        # Get idm from file
        idm_match = re.search(r'^idm:\s*(\d+)', content, re.MULTILINE)
        if not idm_match:
            continue
        idm = idm_match.group(1)
        
        act = activity.get(idm)
        if not act:
            continue
        
        # Replace placeholder speeches_count
        if '(See speeches)' in content or re.search(r'^speeches_count:\s*$', content, re.MULTILINE):
            # Replace in frontmatter
            new_content = re.sub(
                r'^speeches_count:.*$',
                f'speeches_count: {act["speeches"]}',
                content,
                flags=re.MULTILINE
            )
            if new_content != content:
                content = new_content
                updated += 1
        
        # Replace placeholder laws_proposed
        if '(See sponsored laws)' in content or re.search(r'^laws_proposed:\s*$', content, re.MULTILINE):
            new_content = re.sub(
                r'^laws_proposed:.*$',
                f'laws_proposed: {act["proposals"]}',
                content,
                flags=re.MULTILINE
            )
            if new_content != content:
                content = new_content
                updated += 1
        
        if content != f.read_text(encoding='utf-8'):
            f.write_text(content, encoding='utf-8')
    
    print(f"Updated {updated} placeholder fields with real data")

if __name__ == "__main__":
    main()