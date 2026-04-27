#!/usr/bin/env python3
"""
Fix deputy data from Open Parliament RO source.
Uses idm field in vault files to match and overwrite incorrect/placeholder data.

Fixes:
- party (currently set to constituency)
- party_full
- constituency (currently set to candidate name)
- speeches_count (currently placeholder)
- laws_proposed
- photo_url, url
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
OP_DIR = PROJECT_DIR / "data/parlamint/open-parliament-ro/data/2024/full-deputies"
VAULT_DIR = PROJECT_DIR / "vault/politicians/deputies"

def load_op_data() -> Dict[str, Dict]:
    """Load all Open Parliament deputies indexed by idm."""
    op_by_idm = {}
    for fp in OP_DIR.glob("*.json"):
        try:
            data = json.loads(fp.read_text())
            d = data.get('data', {})
            idm = d.get('idm')
            if idm:
                # Extract activity counts
                activity = d.get('activity', {})
                speeches = activity.get('Luări de cuvânt', {}).get('count', 0)
                laws = activity.get('Propuneri legislative iniţiate', {}).get('count', 0)
                party_info = d.get('party', {})
                district_info = d.get('district', {})
                op_by_idm[str(idm)] = {
                    'name': d.get('name', '').strip(),
                    'party_abbrev': party_info.get('abbrev', ''),
                    'party_full': party_info.get('name', ''),
                    'constituency': district_info.get('name', ''),
                    'photo_url': d.get('photoUrl', ''),
                    'url': d.get('url', ''),
                    'speeches_count': speeches,
                    'laws_proposed': laws,
                }
        except Exception as e:
            print(f"Error loading {fp.name}: {e}")
    return op_by_idm

def parse_frontmatter(content: str) -> Tuple[Dict, str]:
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

def dump_frontmatter(fm: Dict, body: str) -> str:
    new_fm = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return f"---\n{new_fm}---\n{body}"

def main():
    print("=== Fix Deputy Data from Open Parliament ===\n")
    op_data = load_op_data()
    print(f"Loaded {len(op_data)} OP deputies")
    
    fixed = 0
    errors = 0
    for fp in sorted(VAULT_DIR.glob("*.md")):
        if fp.name == "Index.md":
            continue
        try:
            content = fp.read_text()
            fm, body = parse_frontmatter(content)
            idm = fm.get('idm')
            if not idm:
                continue
            op = op_data.get(str(idm))
            if not op:
                continue
            
            changes = []
            # Force update these fields
            if op['party_abbrev'] and (not fm.get('party') or fm.get('party') in ['Dâmbovița', 'București', 'Sibiu', 'Cluj'] or True):
                fm['party'] = op['party_abbrev']
                changes.append(f"party -> {op['party_abbrev']}")
            if op['party_full']:
                fm['party_full'] = op['party_full']
                changes.append(f"party_full -> {op['party_full']}")
            if op['constituency']:
                fm['constituency'] = op['constituency']
                changes.append(f"constituency -> {op['constituency']}")
            # Always set numeric counts: if missing or string, or explicitly want to ensure numeric
            if 'speeches_count' in op:
                # Overwrite if not an integer (string placeholder) or if missing
                if not isinstance(fm.get('speeches_count'), int):
                    fm['speeches_count'] = int(op['speeches_count'])
                    changes.append(f"speeches_count -> {op['speeches_count']}")
            if 'laws_proposed' in op:
                if not isinstance(fm.get('laws_proposed'), int):
                    fm['laws_proposed'] = int(op['laws_proposed'])
                    changes.append(f"laws_proposed -> {op['laws_proposed']}")
            if op['photo_url'] and not fm.get('photo_url'):
                fm['photo_url'] = op['photo_url']
                changes.append("photo_url added")
            if op['url'] and not fm.get('url'):
                fm['url'] = op['url']
                changes.append("url added")
            
            if changes:
                new_content = dump_frontmatter(fm, body)
                fp.write_text(new_content)
                fixed += 1
                print(f"{fp.name}: {'; '.join(changes)}")
        except Exception as e:
            errors += 1
            print(f"Error {fp.name}: {e}")
    
    print(f"\nFixed: {fixed} files, errors: {errors}")

if __name__ == "__main__":
    main()
