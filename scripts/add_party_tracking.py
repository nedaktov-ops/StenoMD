#!/usr/bin/env python3
"""
Add party change tracking (traseism) fields to politician profiles.

Usage: python3 scripts/add_party_tracking.py [--apply]
"""
import os
import re
import json
from pathlib import Path
from datetime import datetime

DEPUTIES_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/vault/politicians/deputies")
SENATORS_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/vault/politicians/senators")

def get_current_party(content):
    """Extract current party from content."""
    match = re.search(r'^party:\s*(\w+)', content, re.MULTILINE)
    return match.group(1) if match else None

def add_party_tracking_fields(filepath, dry_run=True):
    """Add party change tracking fields."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "party_affiliations:" in content:
        return None
    
    current_party = get_current_party(content)
    if not current_party:
        return None
    
    now = datetime.now().strftime("%Y-%m")
    
    party_affiliation = f"""- party: {current_party}
  start_date: "2024-12"
  is_original: true"""
    
    lines = content.split("\n")
    new_lines = []
    inserted = False
    
    for line in lines:
        if line.startswith("stable_id:") and not inserted:
            new_lines.append(line)
            new_lines.append(f"original_elected_party: {current_party}")
            new_lines.append("party_affiliations:")
            new_lines.append(party_affiliation)
            inserted = True
        else:
            new_lines.append(line)
    
    if inserted and not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
        return current_party
    
    return current_party

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    
    dry_run = not args.apply
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY'}")
    
    print("\n=== Adding Party Tracking Fields ===")
    
    all_dirs = [DEPUTIES_DIR, SENATORS_DIR]
    
    total_added = 0
    for chamber_dir in all_dirs:
        files = list(chamber_dir.glob("*.md"))
        files = [f for f in files if f.name != "Index.md"]
        
        print(f"\n{chamber_dir.name}: {len(files)} files")
        
        added = 0
        for filepath in files:
            result = add_party_tracking_fields(filepath, dry_run)
            if result:
                added += 1
                print(f"  + {filepath.name}: {result}")
        
        print(f"  Updated: {added}/{len(files)}")
        total_added += added
    
    print(f"\nTotal: {total_added} profiles updated")

if __name__ == "__main__":
    main()