#!/usr/bin/env python3
"""
Final reconciliation: Add idm and committees to ALL deputy files using
committees_members.json as the authoritative idm source.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Optional

VAULT_DIR = Path("vault/politicians/deputies")
DATA_DIR = Path("data")

def normalize_name(name: str) -> str:
    """Normalize name for matching: lowercase, reorder Romanian names.
    Committee data uses 'Lastname Firstname Middlename' format.
    Vault uses 'Firstname Middlename Lastname' format.
    """
    name = name.lower().strip()
    parts = name.split()
    if len(parts) >= 2:
        # Move first part (lastname) to the end
        lastname = parts[0]
        given_names = parts[1:]
        return ' '.join(given_names + [lastname])
    return name

def build_name_to_idm_from_committees():
    """Build name -> idm mapping from committees_members.json"""
    committees = json.load(open(DATA_DIR / "committees_members.json"))
    name_to_idm = {}
    
    for c in committees:
        mp_id = str(c.get('mp_id', ''))
        if not mp_id:
            continue
        raw_name = c.get('name', '').strip()
        norm_name = normalize_name(raw_name)
        name_to_idm[norm_name] = mp_id
    
    print(f"Built mapping with {len(name_to_idm)} entries from committees")
    return name_to_idm

def extract_name_from_frontmatter(content: str) -> Optional[str]:
    """Extract the 'name:' field from frontmatter"""
    match = re.search(r'^name:\s*(.+?)(?:\n|$)', content, re.MULTILINE)
    return match.group(1).strip() if match else None

def has_field(content: str, field: str) -> bool:
    """Check if frontmatter contains field"""
    return bool(re.search(rf'^{field}:\s', content, re.MULTILINE))

def add_idm_and_committees():
    """Main function"""
    print("="*60)
    print("FINAL RECONCILIATION: Add IDM + Committees")
    print("="*60)
    
    name_to_idm = build_name_to_idm_from_committees()
    
    # Build committees lookup: idm -> list of committees
    committees_data = json.load(open(DATA_DIR / "committees_members.json"))
    idm_to_committees = defaultdict(list)
    for c in committees_data:
        mp_id = str(c.get('mp_id', ''))
        if mp_id:
            idm_to_committees[mp_id].append({
                'name': c.get('committee_name', ''),
                'role': c.get('position', 'member')
            })
    
    print(f"Found committees for {len(idm_to_committees)} unique idm values")
    
    stats = {
        'processed': 0,
        'idm_added': 0,
        'committees_added': 0,
        'skipped': 0,
        'errors': 0,
        'debug_matches': 0,
        'debug_not_found': 0
    }
    
    files = list(VAULT_DIR.glob("*.md"))
    print(f"\nProcessing {len(files)} deputy files...\n")
    
    for f in files:
        stats['processed'] += 1
        try:
            content = f.read_text(encoding='utf-8')
            original_content = content
            
            # Extract name
            name = extract_name_from_frontmatter(content)
            if not name:
                stats['skipped'] += 1
                continue
            
            # Normalize name for lookup
            norm_name = normalize_name(name)
            
            # Debug: show some names
            if f.stem.isdigit() and 115 <= int(f.stem) <= 150:
                print(f"{f.stem}: {name} -> {norm_name} -> idm? {norm_name in name_to_idm}")
            
            # Find idm
            idm = None
            if has_field(content, 'idm'):
                idm_match = re.search(r'^idm:\s*(\d+)', content, re.MULTILINE)
                if idm_match:
                    idm = idm_match.group(1)
            else:
                # Try to find from committees mapping
                if norm_name in name_to_idm:
                    idm = name_to_idm[norm_name]
                else:
                    # Try alternative matching
                    for mapping_name, mapping_idm in name_to_idm.items():
                        if name.lower() in mapping_name or mapping_name in name.lower():
                            idm = mapping_idm
                            break
            
            if idm:
                # Add idm if missing
                if not has_field(content, 'idm'):
                    # Insert after name field
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
            
            # Add committees if idm found and committees field missing
            if idm and idm in idm_to_committees and not has_field(content, 'committees'):
                comms = idm_to_committees[idm]
                if comms:
                    # Insert before closing ---
                    lines = content.split('\n')
                    new_lines = []
                    fm_end = -1
                    in_fm = False
                    for i, line in enumerate(lines):
                        if line.strip() == '---':
                            if not in_fm:
                                in_fm = True
                            else:
                                fm_end = i
                                new_lines.append(line)
                                break
                        new_lines.append(line)
                    
                    if fm_end != -1:
                        # Add committees
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
                        # Add rest of lines
                        new_lines.extend(lines[i+1:])
                        content = '\n'.join(new_lines)
                        stats['committees_added'] += 1
            
            if content != original_content:
                f.write_text(content, encoding='utf-8')
                
        except Exception as e:
            print(f"ERROR processing {f.name}: {e}")
            stats['errors'] += 1
    
    print("\n" + "="*60)
    print("FINAL RECONCILIATION COMPLETE")
    print("="*60)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("="*60)

if __name__ == "__main__":
    add_idm_and_committees()