#!/usr/bin/env python3
"""
Enrich law files with proposal data from Open Parliament RO.

Usage: python3 scripts/enrich_laws.py [--dry-run]
"""
import os
import json
import re
from pathlib import Path
from datetime import datetime

VAULT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/vault/laws")
PROPOSALS_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/data/parlamint/open-parliament-ro/data/2024/proposals")

def extract_year(number):
    """Extract year from law number like 127/2026."""
    match = re.search(r'/(\d{4})', number)
    if match:
        return match.group(1)
    return None

def normalize_number(number):
    """Normalize law number to find matching proposal."""
    number = number.strip()
    match = re.search(r'(\d+)', number)
    if match:
        return match.group(1)
    return None

def load_proposals():
    """Load all proposals from Open Parliament RO data."""
    proposals = {}
    
    if not PROPOSALS_DIR.exists():
        print(f"Proposals directory not found: {PROPOSALS_DIR}")
        return proposals
    
    files = list(PROPOSALS_DIR.glob("*.json"))
    print(f"Loading {len(files)} proposal files...")
    
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            
            prop = data.get("data", {})
            if not prop:
                continue
            
            idp = prop.get("idp", "")
            title = prop.get("title", "")
            status = prop.get("status", {})
            status_short = status.get("short", "") if status else ""
            prop_type = prop.get("type", "")
            initiators = prop.get("initiators", [])
            reg_numbers = prop.get("registrationNumber", {})
            
            proposals[idp] = {
                "title": title,
                "type": prop_type,
                "status": status_short,
                "initiators": initiators,
                "senateChamber": reg_numbers.get("senateChamber", ""),
            }
        except Exception as e:
            pass
    
    print(f"Loaded {len(proposals)} proposals")
    return proposals

def enrich_law_file(filepath, proposals, dry_run=True):
    """Enrich a law file with proposal data."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    number_match = re.search(r'law_number:\s*["\']?(\d+/\d{4})', content)
    if not number_match:
        return None
    
    law_number = number_match.group(1)
    year = extract_year(law_number)
    
    if year != "2024" and year != "2025" and year != "2026":
        return None
    
    num = normalize_number(law_number)
    
    best_match = None
    best_prop = None
    
    for idp, prop in proposals.items():
        reg_num = prop.get("senateChamber", "")
        if num and num in reg_num:
            best_match = idp
            best_prop = prop
            break
    
    if not best_match:
        for idp, prop in proposals.items():
            title = prop.get("title", "")
            if num and num in title[:50]:
                best_match = idp
                best_prop = prop
                break
    
    if best_match and best_prop:
        if not dry_run:
            new_title = best_prop.get("title", "")[:200]
            new_status = best_prop.get("status", "")[:100]
            
            lines = content.split("\n")
            new_lines = []
            for line in lines:
                if line.startswith("title:"):
                    new_lines.append(f'title: "{new_title}"')
                elif line.startswith("status:"):
                    new_lines.append(f"status: {new_status}")
                else:
                    new_lines.append(line)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines))
        
        return best_match
    
    return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Enrich law files")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    
    dry_run = not args.apply
    
    print("=== Enriching Law Files ===")
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY'}")
    
    proposals = load_proposals()
    
    law_files = list(VAULT_DIR.glob("*.md"))
    law_files = [f for f in law_files if f.name not in ["Index.md", "Unknown.md"]]
    print(f"\nFound {len(law_files)} law files")
    
    matched = 0
    for filepath in sorted(law_files):
        result = enrich_law_file(filepath, proposals, dry_run)
        if result:
            matched += 1
            print(f"  Matched: {filepath.name} -> proposal {result}")
    
    print(f"\nMatched: {matched}/{len(law_files)} law files")

if __name__ == "__main__":
    main()