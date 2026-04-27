#!/usr/bin/env python3
"""
Comprehensive enrichment of deputy vault files.
- Add idm to numeric files using name mapping
- Link committees from committees_members.json
- Add ai_fields (search_aliases)
- Add activity scores from scraped data
- Ensure consistency across all files
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Optional, Dict, List

BASE_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
VAULT_DIR = BASE_DIR / "vault" / "politicians" / "deputies"
DATA_DIR = BASE_DIR / "data"

class VaultEnricher:
    def __init__(self):
        self.deputies_2024 = {d['name'].lower(): d for d in json.load(open(DATA_DIR / "deputies_2024.json"))['deputies']}
        self.committees = json.load(open(DATA_DIR / "committees_members.json"))
        self.idm_to_name = {}  # Will be built from vault files
        self.name_to_idm = {}  # Reverse mapping
        self.stats = defaultdict(int)
        
    def build_idm_mapping(self):
        """Extract idm -> name from existing vault files"""
        print("Building idm mapping from vault files...")
        for f in VAULT_DIR.glob("*.md"):
            content = f.read_text(encoding='utf-8')
            
            # Extract name and idm
            name_match = re.search(r'name:\s*(.+?)(?:\n|$)', content)
            idm_match = re.search(r'idm:\s*(\d+)', content)
            
            if name_match and idm_match:
                name = name_match.group(1).strip().lower()
                idm = idm_match.group(1)
                self.idm_to_name[idm] = name
                self.name_to_idm[name] = idm
                
        print(f"  Found {len(self.idm_to_name)} idm mappings")
        
    def get_deputy_data(self, name: str) -> Optional[Dict]:
        """Get deputy data from deputies_2024.json"""
        return self.deputies_2024.get(name.lower())
    
    def add_idm_to_numeric_files(self):
        """Add idm to files with numeric names"""
        print("\nAdding idm to numeric files...")
        
        for f in VAULT_DIR.glob("[0-9]*.md"):
            self.stats['processed_numeric'] += 1
            content = f.read_text(encoding='utf-8')
            
            # Already has idm?
            if re.search(r'idm:\s*\d+', content):
                self.stats['numeric_had_idm'] += 1
                continue
            
            # Extract name from frontmatter
            name_match = re.search(r'name:\s*(.+?)(?:\n|$)', content)
            if not name_match:
                self.stats['numeric_no_name'] += 1
                continue
                
            name = name_match.group(1).strip()
            deputy_data = self.get_deputy_data(name)
            
            if not deputy_data:
                self.stats['numeric_not_found'] += 1
                continue
            
            # Find idm from any existing file with this name (lookup by name)
            idm = self.name_to_idm.get(name.lower())
            if not idm:
                # Try to find from other enriched files
                for other_f in VAULT_DIR.glob("*.md"):
                    if other_f == f:
                        continue
                    other_content = other_f.read_text(encoding='utf-8')
                    other_name_match = re.search(r'name:\s*(.+?)(?:\n|$)', other_content)
                    other_idm_match = re.search(r'idm:\s*(\d+)', other_content)
                    if other_name_match and other_idm_match:
                        if other_name_match.group(1).strip().lower() == name.lower():
                            idm = other_idm_match.group(1)
                            break
            
            if not idm:
                self.stats['numeric_no_idm_found'] += 1
                continue
            
            # Add idm to frontmatter (after name field)
            lines = content.split('\n')
            new_lines = []
            added = False
            for line in lines:
                new_lines.append(line)
                if line.strip().startswith('name:') and not added:
                    new_lines.append(f"idm: {idm}")
                    added = True
            
            if added:
                f.write_text('\n'.join(new_lines), encoding='utf-8')
                self.stats['numeric_idm_added'] += 1
        
        print(f"  Numeric files with idm already: {self.stats['numeric_had_idm']}")
        print(f"  Added idm: {self.stats['numeric_idm_added']}")
        print(f"  Skipped (no name): {self.stats['numeric_no_name']}")
        print(f"  Skipped (name not in deputies_2024): {self.stats['numeric_not_found']}")
    
    def add_committees_to_all(self):
        """Add committees using idm mapping"""
        print("\nLinking committees...")
        
        # Build idm -> committees mapping
        idm_to_committees = defaultdict(list)
        for c in self.committees:
            mp_id = str(c.get('mp_id', ''))
            if mp_id:
                idm_to_committees[mp_id].append({
                    'name': c.get('committee_name', ''),
                    'role': c.get('role', 'member')
                })
        
        print(f"  Found committees for {len(idm_to_committees)} idm values")
        
        updated = 0
        for f in VAULT_DIR.glob("*.md"):
            content = f.read_text(encoding='utf-8')
            
            # Get idm
            idm_match = re.search(r'idm:\s*(\d+)', content)
            if not idm_match:
                continue
                
            idm = idm_match.group(1)
            comms = idm_to_committees.get(idm, [])
            
            if not comms:
                continue
            
            # Check if already has committees
            if re.search(r'committees:', content):
                self.stats['had_committees'] += 1
                continue
            
            # Add committees before closing ---
            lines = content.split('\n')
            new_lines = []
            in_frontmatter = False
            frontmatter_end = -1
            
            for i, line in enumerate(lines):
                if line.strip() == '---':
                    if not in_frontmatter:
                        in_frontmatter = True
                    else:
                        frontmatter_end = i
                        break
                new_lines.append(line)
            
            if frontmatter_end == -1:
                continue
                
            # Add committees section
            new_lines.append("committees:")
            for c in comms[:3]:  # Max 3
                name = c['name'].replace('"', '\\"')
                role = c['role'].lower()
                if 'presedinte' in role or 'chair' in role.lower():
                    role = 'presedinte'
                elif 'vice' in role.lower():
                    role = 'vice_presedinte'
                else:
                    role = 'member'
                new_lines.append(f'  - name: "{name}"')
                new_lines.append(f'    role: "{role}"')
            
            # Add rest of file
            new_lines.extend(lines[frontmatter_end:])
            
            f.write_text('\n'.join(new_lines), encoding='utf-8')
            updated += 1
        
        print(f"  Updated {updated} files with committees")
        self.stats['committees_added'] = updated
    
    def add_ai_fields(self):
        """Add ai_friendly_name and search_aliases if missing"""
        print("\nAdding AI fields...")
        
        updated = 0
        for f in VAULT_DIR.glob("*.md"):
            content = f.read_text(encoding='utf-8')
            
            # Skip if already has ai_friendly_name
            if 'ai_friendly_name:' in content:
                self.stats['had_ai_fields'] += 1
                continue
            
            # Extract name
            name_match = re.search(r'name:\s*(.+?)(?:\n|$)', content)
            if not name_match:
                continue
                
            name = name_match.group(1).strip()
            
            # Generate ai fields
            ai_name = name.replace('-', ' ').title()
            aliases = [name.upper(), name.lower(), name.title()]
            
            # Add before closing ---
            lines = content.split('\n')
            new_lines = []
            in_frontmatter = False
            frontmatter_end = -1
            
            for i, line in enumerate(lines):
                if line.strip() == '---':
                    if not in_frontmatter:
                        in_frontmatter = True
                    else:
                        frontmatter_end = i
                        break
                new_lines.append(line)
            
            if frontmatter_end == -1:
                continue
            
            # Add AI fields
            new_lines.append(f'ai_friendly_name: {ai_name}')
            new_lines.append(f'search_aliases: {json.dumps(aliases, ensure_ascii=False)}')
            
            # Add rest of file
            new_lines.extend(lines[frontmatter_end:])
            
            f.write_text('\n'.join(new_lines), encoding='utf-8')
            updated += 1
        
        print(f"  Updated {updated} files with AI fields")
        self.stats['ai_fields_added'] = updated
    
    def add_activity_scores(self):
        """Add activity scores from deputy_activity_stats.json if available"""
        print("\nAdding activity scores...")
        
        activity_file = DATA_DIR / "deputy_activity_stats.json"
        if not activity_file.exists():
            print("  No activity stats file found, skipping")
            return
        
        activity = json.load(open(activity_file))
        idm_to_score = {str(d['idm']): d.get('activity_score', 0) for d in activity}
        
        updated = 0
        for f in VAULT_DIR.glob("*.md"):
            content = f.read_text(encoding='utf-8')
            
            # Already has activity_score?
            if re.search(r'activity_score:\s*\d+', content):
                continue
            
            idm_match = re.search(r'idm:\s*(\d+)', content)
            if not idm_match:
                continue
                
            idm = idm_match.group(1)
            score = idm_to_score.get(idm, 0)
            
            if score == 0:
                continue
            
            # Add activity_score before closing ---
            lines = content.split('\n')
            new_lines = []
            in_frontmatter = False
            frontmatter_end = -1
            
            for i, line in enumerate(lines):
                if line.strip() == '---':
                    if not in_frontmatter:
                        in_frontmatter = True
                    else:
                        frontmatter_end = i
                        break
                new_lines.append(line)
            
            if frontmatter_end == -1:
                continue
            
            # Add score
            new_lines.append(f'activity_score: {score}')
            
            # Add rest of file
            new_lines.extend(lines[frontmatter_end:])
            
            f.write_text('\n'.join(new_lines), encoding='utf-8')
            updated += 1
        
        print(f"  Updated {updated} files with activity scores")
        self.stats['activity_added'] = updated
    
    def run(self):
        """Run all enrichment steps"""
        print("="*60)
        print("VAULT ENRICHMENT PIPELINE")
        print("="*60)
        
        self.build_idm_mapping()
        self.add_idm_to_numeric_files()
        self.add_committees_to_all()
        self.add_ai_fields()
        self.add_activity_scores()
        
        print("\n" + "="*60)
        print("ENRICHMENT COMPLETE")
        print("="*60)
        for key, value in self.stats.items():
            print(f"  {key}: {value}")
        print("="*60)

def main():
    enricher = VaultEnricher()
    enricher.run()

if __name__ == "__main__":
    main()