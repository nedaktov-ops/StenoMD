#!/usr/bin/env python3
"""
Generate stable IDs for politicians across multiple legislatures.

Stable ID format: hash(name + constituency + first_elected)
This ID stays consistent across legislatures for the same person.

Usage: python3 scripts/generate_stable_ids.py [--dry-run]
"""
import os
import re
import hashlib
import json
from pathlib import Path
from datetime import datetime

VAULT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/vault/politicians")

PARTY_MAP = {
    "PSD": "Partidul Social Democrat",
    "PNL": "Partidul Național Liberal",
    "AUR": "Alianța pentru Unirea Românilor",
    "USR": "Uniunea Salvați România",
    "UDMR": "Uniunea Democrată Maghiară din România",
    "SOS": "S.O.S. România",
    "POT": "Partidul Oamenilor Tineri",
}

def normalize_name(name):
    name = re.sub(r'[^\w\s]', '', name.strip())
    return ' '.join(name.split()).lower()

def generate_stable_id(name, constituency, first_elected=None):
    """Generate a stable hash-based ID."""
    normalized = normalize_name(name)
    constit = constituency.upper().strip() if constituency else "UNK"
    
    if first_elected:
        seed = f"{normalized}|{constit}|{first_elected}"
    else:
        seed = f"{normalized}|{constit}|2024"
    
    hash_obj = hashlib.sha256(seed.encode('utf-8'))
    return f"pol_{hash_obj.hexdigest()[:12]}"

def extract_legislature(content):
    """Extract legislature year from content."""
    match = re.search(r'legislature:\s*(\d{4})', content)
    if match:
        return match.group(1)
    return "2024"

def extract_birth_year(content):
    """Try to extract birth year from content."""
    match = re.search(r'born[:\s]+(\d{4})', content, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def extract_constituency(content):
    """Extract constituency from content."""
    match = re.search(r'constituency:\s*(\w+)', content)
    if match:
        return match.group(1)
    return "UNK"

def update_frontmatter(filepath, stable_id):
    """Add stable_id to frontmatter."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")
    
    new_lines = []
    id_added = False
    
    for line in lines:
        if line.startswith("---") and not id_added:
            new_lines.append(line)
        elif line.startswith("type:") and not id_added:
            new_lines.append(f"stable_id: {stable_id}")
            new_lines.append(line)
        else:
            new_lines.append(line)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

def process_chamber(chamber_dir, dry_run=True):
    """Process all politicians in a chamber directory."""
    if not chamber_dir.exists():
        print(f"  Directory not found: {chamber_dir}")
        return {}
    
    files = list(chamber_dir.glob("*.md"))
    files = [f for f in files if f.name != "Index.md"]
    
    print(f"  Found {len(files)} files in {chamber_dir.name}")
    
    stable_ids = {}
    collisions = 0
    
    for filepath in sorted(files):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        name = filepath.stem.replace("-", " ")
        
        constituency = extract_constituency(content)
        legislature = extract_legislature(content)
        
        stable_id = generate_stable_id(name, constituency, legislature)
        
        if stable_id in stable_ids:
            collisions += 1
            print(f"  Collision: {name}")
        
        stable_ids[stable_id] = name
        
        if not dry_run:
            update_frontmatter(filepath, stable_id)
    
    print(f"  Generated {len(stable_ids)} stable IDs ({collisions} collisions)")
    return stable_ids

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate stable IDs")
    parser.add_argument("--dry-run", action="store_true", default=True,
                     help="Show what would happen without making changes")
    parser.add_argument("--apply", action="store_true",
                     help="Apply changes (disable dry-run)")
    args = parser.parse_args()
    
    dry_run = not args.apply
    
    if dry_run:
        print("=== DRY RUN MODE ===")
    else:
        print("=== APPLYING CHANGES ===")
    
    print("\n=== Generating Stable IDs ===")
    
    deps_dir = VAULT_DIR / "deputies"
    sens_dir = VAULT_DIR / "senators"
    
    deps_ids = process_chamber(deps_dir, dry_run)
    sens_ids = process_chamber(sens_dir, dry_run)
    
    all_ids = {**deps_ids, **sens_ids}
    print(f"\nTotal: {len(all_ids)} unique stable IDs")
    
    if not dry_run:
        print("\nStable IDs have been added to frontmatter.")
        print("Use generate_stable_ids.py --apply to enable.")
    
    print(f"\nSample IDs:")
    for i, (sid, name) in enumerate(list(all_ids.items())[:5]):
        print(f"  {sid}: {name}")

if __name__ == "__main__":
    main()