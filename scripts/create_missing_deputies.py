#!/usr/bin/env python3
"""
Create missing deputy profiles from Open Parliament RO data.

Usage: python3 scripts/create_missing_deputies.py [--dry-run]
"""
import os
import json
import re
import hashlib
import shutil
from pathlib import Path
from datetime import datetime

VAULT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/vault/politicians/deputies")
DATA_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/data/parlamint/open-parliament-ro/data/2024/full-deputies")

PARTY_MAP = {
    "PSD": "Partidul Social Democrat",
    "PNL": "Partidul Național Liberal",
    "AUR": "Alianța pentru Unirea Românilor",
    "USR": "Uniunea Salvați România",
    "UDMR": "Uniunea Democrată Maghiară din România",
    "SOS": "S.O.S. România",
    "POT": "Partidul Oamenilor Tineri",
    "PMP": "Partidul Mișcarea Populară",
    "PRM": "Partidul România Mare",
    "ALDE": "Alianța Liberal Democrat",
    "PC": "Partidul Conservator",
    "PER": "Partidul Extraordinar",
}

def normalize_name(name):
    return re.sub(r'[^\w\s]', '', name.strip())

def make_filename(name):
    normalized = normalize_name(name).upper()
    return re.sub(r'\s+', '-', normalized) + ".md"

def generate_stable_id(name, constituency, legislature="2024"):
    name_norm = ' '.join(name.strip().split()).lower()
    seed = f"{name_norm}|{constituency.upper()}|{legislature}"
    hash_obj = hashlib.sha256(seed.encode('utf-8'))
    return f"pol_{hash_obj.hexdigest()[:12]}"

def existing_deputy_names():
    """Get list of names already in vault."""
    names = set()
    for f in VAULT_DIR.glob("*.md"):
        if f.name == "Index.md":
            continue
        name = f.stem.replace("-", " ")
        names.add(name.lower())
    return names

def load_full_deputies():
    """Load all deputies from full-deputies data."""
    deputies = []
    
    if not DATA_DIR.exists():
        print(f"Data directory not found: {DATA_DIR}")
        return deputies
    
    files = sorted(DATA_DIR.glob("*.json"))
    print(f"Loading {len(files)} deputy files...")
    
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            
            dep = data.get("data", {})
            if not dep:
                continue
            
            name = dep.get("name", "").strip()
            if not name:
                continue
            
            party = dep.get("party", {})
            party_abbrev = party.get("abbrev", "")
            party_name = party.get("name", "")
            
            district = dep.get("district", {})
            constit = district.get("name", "")
            
            url = dep.get("url", "")
            photo_url = dep.get("photoUrl", "")
            
            activity = dep.get("activity", {})
            speeches = activity.get("Luări de cuvânt", {}).get("count", 0)
            laws = activity.get("Propuneri legislative iniţiate", {}).get("count", 0)
            
            idm = dep.get("idm", "")
            
            deputies.append({
                "name": name,
                "party": party_abbrev,
                "party_full": party_name or PARTY_MAP.get(party_abbrev, "Unknown"),
                "constituency": constit,
                "url": url,
                "photo_url": photo_url,
                "speeches_count": speeches,
                "laws_proposed": laws,
                "idm": idm,
            })
        except Exception as e:
            print(f"Error loading {f}: {e}")
    
    print(f"Loaded {len(deputies)} deputies from data")
    return deputies

def create_deputy_profile(data):
    """Create a deputy profile markdown file."""
    name = data["name"]
    party = data.get("party", "UNKN")
    party_full = data.get("party_full", PARTY_MAP.get(party, "Unknown"))
    constit = data.get("constituency", "")
    url = data.get("url", "")
    photo_url = data.get("photo_url", "")
    speeches = data.get("speeches_count", 0)
    laws = data.get("laws_proposed", 0)
    idm = data.get("idm", "")
    
    stable_id = generate_stable_id(name, constit)
    
    filename = make_filename(name)
    filepath = VAULT_DIR / filename
    
    content = f"""---
name: {name}
chamber: Chamber of Deputies
legislature: 2024-2028
source: cdep.ro
party: {party}
party_full: {party_full}
constituency: {constit}
photo_url: {photo_url}
url: {url}
idm: {idm}
speeches_count: {speeches}
laws_proposed: {laws}
stable_id: {stable_id}
type: deputy
---

# {name}

**Chamber:** Chamber of Deputies  
**Legislature:** 2024-2028  
**Source:** [cdep.ro]({url})

## Profile

**Party:** {party_full}  
**Constituency:** {constit}  
**Speeches:** {speeches}  
**Laws Proposed:** {laws}

## Notes

*Deputy in the Romanian Parliament*

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return content, filepath

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Create missing deputy profiles")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    
    dry_run = not args.apply
    
    print("=== Creating Missing Deputy Profiles ===")
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY'}")
    
    existing = existing_deputy_names()
    print(f"Existing deputies in vault: {len(existing)}")
    
    all_deputies = load_full_deputies()
    
    missing = []
    for dep in all_deputies:
        name_lower = dep["name"].lower()
        if name_lower not in existing:
            missing.append(dep)
    
    print(f"\nMissing deputies: {len(missing)}")
    
    if dry_run:
        for dep in missing[:20]:
            filename = make_filename(dep["name"])
            print(f"  Would create: {filename}")
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")
        return
    
    created = 0
    for dep in missing:
        content, filepath = create_deputy_profile(dep)
        
        if filepath.exists():
            continue
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        created += 1
        print(f"  Created: {filepath.name}")
    
    print(f"\nCreated {created} new deputy profiles")
    
    existing_after = len(list(VAULT_DIR.glob("*.md"))) - 1
    print(f"Total deputies now: {existing_after}")

if __name__ == "__main__":
    main()