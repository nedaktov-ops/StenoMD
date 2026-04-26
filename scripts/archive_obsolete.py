#!/usr/bin/env python3
"""
Archive deputy profiles without idm (likely obsolete from old legislatures).
"""

import re
from pathlib import Path
import shutil

VAULT_DIR = Path("vault")
ARCHIVE_DIR = Path("archive/deputies_old")

def has_idm(content: str) -> bool:
    """Check if file has idm field."""
    return bool(re.search(r'^idm:\s*\d+', content, re.MULTILINE))

def main():
    print("=== Archiving obsolete deputy profiles ===\n")
    
    deputy_files = list(VAULT_DIR.glob("politicians/deputies/*.md"))
    to_archive = []
    
    for f in deputy_files:
        content = f.read_text(encoding='utf-8')
        if not has_idm(content):
            to_archive.append(f)
    
    print(f"Found {len(to_archive)} files without idm")
    print("Archiving to: archive/deputies_old/")
    
    for f in to_archive:
        dest = ARCHIVE_DIR / f.name
        if not dest.exists():
            shutil.move(str(f), str(dest))
        else:
            # Already exists, check if different
            existing = dest.read_text()
            if len(content) > len(existing):
                shutil.move(str(f), str(dest))
    
    print(f"\nArchived: {len(to_archive)} files")
    
    # Count remaining
    remaining = len(list(VAULT_DIR.glob("politicians/deputies/*.md")))
    print(f"Remaining deputies: {remaining}")

if __name__ == "__main__":
    main()