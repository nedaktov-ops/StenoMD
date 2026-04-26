#!/usr/bin/env python3
"""Add committees to MP profiles using MP ID matching."""
import json
import re
from pathlib import Path

DATA_FILE = Path("data/committees_members.json")
PROFILES_DIR = Path("vault/politicians/deputies")

def main():
    print("=== Adding Committees via MP ID ===")
    
    with open(DATA_FILE) as f:
        committees = json.load(f)
    
    # Build MP ID -> profile lookup
    mp_id_to_profile = {}
    for f in PROFILES_DIR.glob("*.md"):
        if f.name == "Index.md":
            continue
        content = f.read_text(encoding='utf-8')
        
        # Extract MP ID from cdep URL
        # URL pattern: ...idm=327&cam=2
        m = re.search(r'idm=(\d+)', content)
        if m:
            mp_id = m.group(1)
            mp_id_to_profile[mp_id] = f
    
    print(f"Profiles with MP ID: {len(mp_id_to_profile)}")
    
    # Group committees by MP ID
    from collections import defaultdict
    by_mp_id = defaultdict(list)
    for c in committees:
        by_mp_id[c['mp_id']].append(c)
    
    print(f"Committee MPs: {len(by_mp_id)}")
    
    # Match and update
    updated = 0
    for mp_id, comms in by_mp_id.items():
        profile = mp_id_to_profile.get(mp_id)
        if not profile:
            continue
        
        content = profile.read_text(encoding='utf-8')
        if "committees:" in content:
            continue
        
        lines = []
        for c in comms[:3]:
            lines.append(f"  - name: {c['committee_name']}")
            lines.append(f"    position: {c['position']}")
            lines.append(f"    chamber: deputy")
        
        content2 = content.split("\n")
        new_lines = []
        inserted = False
        
        for line in content2:
            new_lines.append(line)
            if line.startswith("stable_id:") and not inserted:
                new_lines.append("committees:")
                new_lines.extend(lines)
                inserted = True
        
        if inserted:
            profile.write_text("\n".join(new_lines), encoding='utf-8')
            updated += 1
    
    print(f"Updated: {updated}/{len(by_mp_id)}")

if __name__ == "__main__":
    main()