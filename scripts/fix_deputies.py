#!/usr/bin/env python3
"""
Fix missing deputy fields using data sources.
"""

import json
import os
from pathlib import Path
from difflib import SequenceMatcher

VAULT_DIR = Path("vault")
DATA_DIR = Path("data")
OPEN_PARL = DATA_DIR / "parlamint/open-parliament-ro/data/2024"

def get_name_key(name: str) -> str:
    """Normalize name for matching."""
    return name.upper().replace('-', ' ').replace('_', ' ').strip()

def find_best_match(name: str, candidates: dict, threshold: float = 0.7) -> str | None:
    """Find best matching name from candidates."""
    key = get_name_key(name)
    for cand_key, cand_data in candidates.items():
        ratio = SequenceMatcher(None, key, cand_key.upper()).ratio()
        if ratio >= threshold:
            return cand_data
    return None

def main():
    print("=== Fixing Missing Deputy Fields ===\n")
    
    # Load Open Parliament deputies
    deputies_json = OPEN_PARL / "deputies.json"
    if deputies_json.exists():
        dep_data = json.loads(deputies_json.read_text())
        open_deps = {d['name'].lower(): d for d in dep_data['data']}
        print(f"Loaded {len(open_deps)} Open Parliament deputies")
    
    # Load committees data
    committees_file = DATA_DIR / "committees_members.json"
    if committees_file.exists():
        comm_data = json.loads(committees_file.read_text())
        print(f"Loaded {len(comm_data)} committee assignments")
    
    # Load activity stats
    activity_file = DATA_DIR / "deputy_activity_stats.json"
    if activity_file.exists():
        activity = json.loads(activity_file.read_text())
        activity_map = {str(a['idm']): a for a in activity}
        print(f"Loaded {len(activity_map)} activity records")
    
    # Process deputies
    deputy_files = list(VAULT_DIR.glob("politicians/deputies/*.md"))
    updated = 0
    skipped = 0
    
    for f in deputy_files:
        content = f.read_text(encoding='utf-8')
        lines = content.split('\n')
        frontmatter = []
        body = []
        in_frontmatter = False
        found_end = False
        
        for line in lines:
            if line.strip() == '---' and not found_end:
                if in_frontmatter:
                    found_end = True
                    in_frontmatter = False
                else:
                    in_frontmatter = True
                frontmatter.append(line)
            elif in_frontmatter:
                frontmatter.append(line)
            else:
                body.append(line)
        
        # Parse current fields
        fields = {}
        for line in frontmatter[1:]:
            if ':' in line:
                key, val = line.split(':', 1)
                fields[key.strip()] = val.strip()
        
        original_fields = fields.copy()
        
        # Get name for matching
        name = fields.get('name', f.stem.replace('-', ' '))
        
        # Find matching Open Parliament record
        if not fields.get('idm'):
            match = find_best_match(name, open_deps)
            if match:
                fields['idm'] = match.get('idm', '')
                if match.get('group', {}).get('name'):
                    fields['party'] = match['group']['name'].split()[0]  # PSD, PNL, etc
                if match.get('district', {}).get('name'):
                    fields['constituency'] = match['district']['name']
        
        # Add activity from stats
        if fields.get('idm') and fields['idm'] in activity_map:
            act = activity_map[fields['idm']]
            if act.get('proposals'):
                fields['laws_proposed'] = act['proposals']
            if act.get('motions'):
                fields['motions'] = act['motions']
        
        # Write back if changed
        if fields != original_fields:
            new_content = '---\n'
            for k, v in fields.items():
                new_content += f"{k}: {v}\n"
            new_content += '---\n\n' + '\n'.join(body)
            f.write_text(new_content, encoding='utf-8')
            updated += 1
        else:
            skipped += 1
    
    print(f"\nUpdated: {updated} files")
    print(f"Skipped: {skipped} files (no changes needed)")

if __name__ == "__main__":
    main()