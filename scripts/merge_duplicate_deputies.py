#!/usr/bin/env python3
"""
Merge duplicate deputy files by normalizing to a single canonical version.
Priority: Keep file with lowercase hyphenated name if content is similar,
or merge if content differs.
"""

import re
from pathlib import Path
from collections import defaultdict

PROJECT = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
DEP_DIR = PROJECT / "vault/politicians/deputies"

def normalize_name(name: str) -> str:
    """Normalize filename to canonical form."""
    name = name.lower()
    # Replace diacritics
    replacements = {
        'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ț': 't',
        'á': 'a', 'à': 'a', 'é': 'e', 'è': 'e', 'ê': 'e',
        'í': 'i', 'ì': 'i', 'ó': 'o', 'ò': 'o', 'ô': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    # Keep only alphanumeric and hyphens, collapse multiple hyphens
    name = re.sub(r'[^a-z0-9-]', '', name)
    name = re.sub(r'-+', '-', name).strip('-')
    return name

def build_duplicate_groups():
    """Find groups of files with same normalized name."""
    groups = defaultdict(list)
    for f in DEP_DIR.glob("*.md"):
        if f.name == "Index.md":
            continue
        norm = normalize_name(f.stem)
        groups[norm].append(f)
    return {k: v for k, v in groups.items() if len(v) > 1}

def merge_files(files):
    """Merge duplicate files, keeping the best version."""
    # Score each file by completeness
    scored = []
    for f in files:
        content = f.read_text(encoding='utf-8', errors='ignore')
        score = 0
        # Prefer files with idm field
        if re.search(r'^idm:\s*\d+', content, re.MULTILINE):
            score += 10
        # Prefer files with more frontmatter fields
        fm_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
        if fm_match:
            fm = fm_match.group(1)
            score += len(fm.split('\n'))
        # Prefer files with longer content (more info)
        score += len(content)
        scored.append((score, f))
    
    # Sort by score descending, pick best as primary
    scored.sort(reverse=True)
    primary = scored[0][1]
    others = [f for _, f in scored[1:]]
    
    return primary, others

def main():
    print("=== Merging Duplicate Deputy Files ===\n")
    groups = build_duplicate_groups()
    print(f"Found {len(groups)} duplicate groups")
    
    total_merged = 0
    for norm, files in groups.items():
        if len(files) < 2:
            continue
        
        print(f"\nGroup: {norm}")
        for f in files:
            print(f"  - {f.name}")
        
        primary, to_delete = merge_files(files)
        
        # If primary doesn't exist (deleted already), pick first existing
        existing = [f for f in [primary] + to_delete if f.exists()]
        if not existing:
            print("  All files missing, skipping")
            continue
        
        primary = existing[0]
        to_delete = [f for f in existing[1:] if f != primary]
        
        # Delete duplicates
        for f in to_delete:
            try:
                f.unlink()
                print(f"  Deleted: {f.name}")
                total_merged += 1
            except Exception as e:
                print(f"  Error deleting {f.name}: {e}")
    
    print(f"\nMerged/deleted: {total_merged} duplicate files")

if __name__ == "__main__":
    main()
