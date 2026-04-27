#!/usr/bin/env python3
"""
Final reconciliation: Use numeric filename as idm, add committees.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Optional

VAULT_DIR = Path("vault/politicians/deputies")
DATA_DIR = Path("data")

def extract_name_from_frontmatter(content: str) -> Optional[str]:
    match = re.search(r'^name:\s*(.+?)(?:\n|$)', content, re.MULTILINE)
    return match.group(1).strip() if match else None

def has_field(content: str, field: str) -> bool:
    return bool(re.search(rf'^{field}:\s', content, re.MULTILINE))

def main():
    print("="*60)
    print("FINAL RECONCILIATION: IDM = filename, Committees")
    print("="*60)
    
    # Load committees: idm -> list of committees
    committees_data = json.load(open(DATA_DIR / "committees_members.json"))
    idm_to_committees = defaultdict(list)
    for c in committees_data:
        mp_id = str(c.get('mp_id', ''))
        if mp_id:
            idm_to_committees[mp_id].append({
                'name': c.get('committee_name', ''),
                'role': c.get('position', 'member')
            })
    
    print(f"Found committees for {len(idm_to_committees)} idm values\n")
    
    stats = {
        'processed': 0,
        'idm_added': 0,
        'committees_added': 0,
        'skipped': 0,
        'errors': 0
    }
    
    files = list(VAULT_DIR.glob("*.md"))
    print(f"Processing {len(files)} files...\n")
    
    for f in files:
        stats['processed'] += 1
        try:
            content = f.read_text(encoding='utf-8')
            original_content = content
            
            # Strategy 1: Numeric filename -> use as idm
            if f.stem.isdigit():
                idm = f.stem
                # Add idm if missing
                if not has_field(content, 'idm'):
                    lines = content.split('\n')
                    new_lines = []
                    name_added = False
                    for line in lines:
                        new_lines.append(line)
                        if line.strip().startswith('name:') and not name_added:
                            new_lines.append(f"idm: {idm}")
                            name_added = True
                    content = '\n'.join(new_lines)
                    stats['idm_added'] += 1
            else:
                # Non-numeric filename: skip for now (already have idm)
                continue
            
    # Add committees if available and missing OR empty
            needs_committees = False
            if idm in idm_to_committees:
                # Check if committees field is empty or missing
                has_any_committee = bool(re.search(r'committees:\s*\n(\s+- name:)', content))
                if not has_any_committee:
                    needs_committees = True
            
            if needs_committees:
                comms = idm_to_committees[idm]
                if comms:
                    lines = content.split('\n')
                    new_lines = []
                    in_fm = False
                    fm_end_idx = -1
                    
                    for i, line in enumerate(lines):
                        if line.strip() == '---':
                            if not in_fm:
                                in_fm = True
                            else:
                                fm_end_idx = i
                                new_lines.append(line)
                                break
                        new_lines.append(line)
                    
                    if fm_end_idx != -1:
                        new_lines.append("committees:")
                        for c in comms[:3]:
                            name_clean = c['name'].replace('"', '\\"')
                            role = c['role'].lower()
                            if 'presedinte' in role or 'chair' in role.lower():
                                role = 'presedinte'
                            elif 'vice' in role.lower():
                                role = 'vice_presedinte'
                            else:
                                role = 'member'
                            new_lines.append(f'  - name: "{name_clean}"')
                            new_lines.append(f'    role: "{role}"')
                        new_lines.extend(lines[i+1:])
                        content = '\n'.join(new_lines)
                        stats['committees_added'] += 1
            
            if content != original_content:
                f.write_text(content, encoding='utf-8')
                
        except Exception as e:
            print(f"ERROR: {f.name}: {e}")
            stats['errors'] += 1
    
    print("\n" + "="*60)
    print("RECONCILIATION COMPLETE")
    print("="*60)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Show affected files
    print("Numeric files updated (sample):")
    numeric_files = list(VAULT_DIR.glob("[0-9]*.md"))
    for f in numeric_files[:10]:
        print(f"  {f.name}")
    print("="*60)

if __name__ == "__main__":
    main()