#!/usr/bin/env python3
"""
Add committees from committees_members.json to deputy profiles.
Uses idm from mp_id field.
"""

import json
from pathlib import Path
from collections import defaultdict

VAULT_DIR = Path("vault")
DATA_DIR = Path("data")

def main():
    print("=== Adding Committees to Deputies ===\n")
    
    # Load committees data
    committees_file = DATA_DIR / "committees_members.json"
    comm_data = json.loads(committees_file.read_text())
    
    # Group by deputy mp_id (which is idm)
    by_mpid = defaultdict(list)
    for c in comm_data:
        mp_id = str(c.get('mp_id', ''))
        if mp_id:
            by_mpid[mp_id].append({
                'name': c.get('committee_name', ''),
                'role': c.get('role', 'member')
            })
    
    print(f"Loaded committees for {len(by_mpid)} deputies")
    print(f"Sample first entry: {by_mpid[list(by_mpid.keys())[0]]}")
    
    # Process deputy files
    deputy_files = list(VAULT_DIR.glob("politicians/deputies/*.md"))
    updated = 0
    
    for f in deputy_files:
        content = f.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Extract idm - check various field names
        idm = None
        for line in lines[:30]:
            for prefix in ['idm:', 'stable_id:']:
                if line.startswith(prefix):
                    val = line.split(':', 1)[1].strip()
                    # stable_id starts with pol_, idm is numeric
                    if val.isdigit():
                        idm = val
                        break
        
        if not idm or idm not in by_mpid:
            continue
        
        comms = by_mpid[idm]
        if not comms:
            continue
        
        # Add committees to frontmatter
        new_lines = []
        in_frontmatter = False
        added = False
        
        for i, line in enumerate(lines):
            if line.strip() == '---' and not in_frontmatter:
                in_frontmatter = True
                new_lines.append(line)
            elif in_frontmatter and line.strip() == '---':
                if not added:
                    new_lines.append("committees:")
                    for c in comms[:3]:  # Max 3 committees
                        name = c['name'].replace('"', '\\"')
                        role = c['role'].lower()
                        if 'presedinte' in role or 'chair' in role.lower():
                            role = 'presedinte'
                        elif 'vice' in role.lower():
                            role = 'vice_presedinte'
                        else:
                            role = 'member'
                        new_lines.append(f"  - name: \"{name}\"")
                        new_lines.append(f"    role: \"{role}\"")
                    added = True
                new_lines.append(line)
                in_frontmatter = False
            elif in_frontmatter and line.startswith('committees'):
                added = True
                new_lines.append(line)
            else:
                new_lines.append(line)
        
        if added:
            f.write_text('\n'.join(new_lines), encoding='utf-8')
            updated += 1
    
    print(f"Updated: {updated} deputies with committees")

if __name__ == "__main__":
    main()