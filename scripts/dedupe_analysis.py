#!/usr/bin/env python3
"""
Deduplication analysis for deputy profiles.
Identifies potential duplicates and suggests removals.
"""

import json
from pathlib import Path
from collections import defaultdict
import re

VAULT_DIR = Path("vault")

def normalize_name(name: str) -> str:
    """Normalize name for matching."""
    return name.upper().replace('-', ' ').replace('_', ' ').replace('  ', ' ')

def get_idm(content: str) -> str:
    """Extract idm from content."""
    match = re.search(r'^idm:\s*(\d+)', content, re.MULTILINE)
    return match.group(1) if match else ''

def get_stable_id(content: str) -> str:
    """Extract stable_id."""
    match = re.search(r'^stable_id:\s*(\S+)', content, re.MULTILINE)
    return match.group(1) if match else ''

def main():
    print("=== Deputy Deduplication Analysis ===\n")
    
    deputy_files = list(VAULT_DIR.glob("politicians/deputies/*.md"))
    
    # Group by idm (duplicate idm = duplicate!)
    by_idm = defaultdict(list)
    by_name = defaultdict(list)
    
    for f in deputy_files:
        content = f.read_text(encoding='utf-8')
        name = f.stem.replace('-', ' ')
        
        # Get idm
        idm = get_idm(content)
        if idm:
            by_idm[idm].append(f)
        
        # Also group by normalized name
        by_name[normalize_name(name)].append(f)
    
    # Find duplicates by idm
    dup_by_idm = {k: v for k, v in by_idm.items() if len(v) > 1}
    print(f"Duplicates by ID: {len(dup_by_idm)}")
    
    for idm, files in list(dup_by_idm.items())[:5]:
        print(f"\n  ID {idm}:")
        for f in files:
            print(f"    {f.stem}")
    
    # Find name duplicates (potential duplicates - different IDs)
    dup_by_name = {k: v for k, v in by_name.items() if len(v) > 1}
    print(f"\nDuplicates by name: {len(dup_by_name)}")
    
    # Extra deputies - likely old legislature
    # 332 expected + 115 extra = 447 total
    # Those without idm are likely duplicates/old
    
    print("\n=== Files without idm (likely obsolete) ===")
    no_idm = [f for f in deputy_files if not get_idm(f.read_text())]
    print(f"Count: {len(no_idm)}")
    
    # List them for review
    for f in sorted(no_idm)[:20]:
        print(f"  {f.stem}")
    
    print(f"\n... and {max(0, len(no_idm) - 20)} more")
    
    # Also find exact name duplicates
    print("\n=== Exact Duplicate Names ===")
    for name, files in dup_by_name.items():
        if len(files) > 1 and all(get_idm(f.read_text()) for f in files):
            print(f"\n  {name}:")
            for f in files:
                idm = get_idm(f.read_text())
                print(f"    {f.stem} (idm: {idm})")

if __name__ == "__main__":
    main()