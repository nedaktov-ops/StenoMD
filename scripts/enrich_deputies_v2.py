#!/usr/bin/env python3
"""
Enrich deputy profiles from local open-parliament-ro data.
Matches by name to update vault profiles with complete data.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import yaml

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
OPEN_PARLIAMENT_DIR = PROJECT_DIR / "data/parlamint/open-parliament-ro/data/2024/full-deputies"
VAULT_DEPUTIES_DIR = PROJECT_DIR / "vault/politicians/deputies"


def normalize_for_matching(text: str) -> str:
    """Normalize text for matching - remove diacritics, lowercase, sort"""
    text = text.lower()
    # Remove diacritics
    replacements = {
        'ă': 'a', 'â': 'a', 'ț': 't', 'ș': 's',
        'Ă': 'a', 'Â': 'a', 'Ț': 't', 'Ș': 'S',
        'é': 'e', 'è': 'e', 'ë': 'e',
        'ö': 'o', 'ü': 'u', 'ß': 'ss'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Remove punctuation, extra spaces
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = ' '.join(text.split())
    return text


def load_open_parliament_deputies() -> Dict[str, Dict]:
    """Load all deputies from open-parliament-ro"""
    deputies = {}
    
    if not OPEN_PARLIAMENT_DIR.exists():
        print(f"ERROR: {OPEN_PARLIAMENT_DIR} not found")
        return deputies
    
    for filepath in OPEN_PARLIAMENT_DIR.glob("*.json"):
        try:
            with open(filepath) as f:
                data = json.load(f)
            
            deputy_data = data.get('data', {})
            name = deputy_data.get('name', '')
            if not name:
                continue
            
            # Extract key fields
            idm = deputy_data.get('idm', filepath.stem)
            party = deputy_data.get('party', {})
            district = deputy_data.get('district', {})
            activity = deputy_data.get('activity', {})
            
            # Normalize name for matching
            name_key = normalize_for_matching(name)
            
            deputies[name_key] = {
                'idm': idm,
                'name': name,
                'party_abbrev': party.get('abbrev', ''),
                'party_full': party.get('name', ''),
                'constituency': district.get('name', ''),
                'photo_url': deputy_data.get('photoUrl', ''),
                'url': deputy_data.get('url', ''),
                'activity': activity
            }
        except Exception as e:
            print(f"Error loading {filepath.name}: {e}")
    
    return deputies


def match_vault_to_op(vault_name: str, op_deputies: Dict) -> Tuple[Dict, float]:
    """Match vault name against open parliament deputies"""
    vault_key = normalize_for_matching(vault_name)
    
    # Try different matching strategies
    match_scores = []
    
    for op_key, op_data in op_deputies.items():
        # Calculate similarity score
        vault_words = set(vault_key.split())
        op_words = set(op_key.split())
        
        # Word overlap
        common = vault_words & op_words
        if len(common) >= 2:
            score = len(common) / max(len(vault_words), len(op_words))
            match_scores.append((op_data, score))
    
    # Return best match if score > 0.3
    match_scores.sort(key=lambda x: x[1], reverse=True)
    if match_scores and match_scores[0][1] > 0.3:
        return match_scores[0]
    
    return None, 0.0


def enrich_vault_deputy(filepath: Path, op_data: Dict) -> bool:
    """Enrich a single deputy profile"""
    try:
        content = filepath.read_text(encoding='utf-8')
        
        # Parse frontmatter
        if '---' not in content:
            return False
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False
        
        fm_text = parts[1]
        body = parts[2]
        
        try:
            fm = yaml.safe_load(fm_text) or {}
        except:
            fm = {}
        
        # Only update if data is missing or placeholder
        needs_update = False
        
        # Add party data if missing
        if op_data.get('party_abbrev') and not fm.get('party'):
            fm['party'] = op_data['party_abbrev']
            needs_update = True
        
        if op_data.get('party_full') and not fm.get('party_full'):
            fm['party_full'] = op_data['party_full']
            needs_update = True
        
        if op_data.get('constituency') and not fm.get('constituency'):
            fm['constituency'] = op_data['constituency']
            needs_update = True
        
        if op_data.get('photo_url') and not fm.get('photo_url'):
            fm['photo_url'] = op_data['photo_url']
            needs_update = True
        
        if op_data.get('url') and not fm.get('url'):
            fm['url'] = op_data['url']
            needs_update = True
        
        # Add chamber if missing
        if 'chamber' not in fm:
            fm['chamber'] = 'deputies'
            needs_update = True
        
        if 'legislature' not in fm:
            fm['legislature'] = '2024-2028'
            needs_update = True
        
        if 'type' not in fm:
            fm['type'] = 'deputy'
            needs_update = True
        
        if needs_update:
            new_fm = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
            new_content = f"---\n{new_fm}---\n{body}"
            filepath.write_text(new_content, encoding='utf-8')
            return True
        
        return False
        
    except Exception as e:
        print(f"Error enriching {filepath.name}: {e}")
        return False


def main():
    print("=" * 60)
    print("Phase 2: Enrich Deputy Profiles from Local Data")
    print("=" * 60)
    
    # Load open parliament data
    print("\nLoading Open Parliament data...")
    op_deputies = load_open_parliament_deputies()
    print(f"Loaded {len(op_deputies)} deputy profiles from open-parliament-ro")
    
    if not op_deputies:
        print("ERROR: No open parliament data found")
        return 1
    
    # Process vault deputies
    if not VAULT_DEPUTIES_DIR.exists():
        print(f"ERROR: {VAULT_DEPUTIES_DIR} not found")
        return 1
    
    enriched_count = 0
    matched_count = 0
    
    for filepath in sorted(VAULT_DEPUTIES_DIR.glob("*.md")):
        if filepath.name == "Index.md":
            continue
        
        vault_name = filepath.stem.replace('-', ' ')
        
        # Match against open parliament
        op_data, score = match_vault_to_op(vault_name, op_deputies)
        
        if op_data:
            matched_count += 1
            if enrich_vault_deputy(filepath, op_data):
                enriched_count += 1
                if enriched_count <= 5:
                    print(f"  Enriched: {filepath.name} <- {op_data['name']}")
    
    print(f"\nResults:")
    print(f"  Matched: {matched_count} vault files to open-parliament data")
    print(f"  Enriched: {enriched_count} files")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())