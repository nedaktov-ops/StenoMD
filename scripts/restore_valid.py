#!/usr/bin/env python3
"""
Restore archived deputies if they exist in current Open Parliament data.
"""

import json
from pathlib import Path
import shutil

ARCHIVE_DIR = Path("archive/deputies_old")
VAULT_DIR = Path("vault")
OPEN_PARL = Path("data/parlamint/open-parliament-ro/data/2024")

def main():
    print("=== Checking archived vs current deputies ===\n")
    
    # Load current Open Parliament deputies
    deps_file = OPEN_PARL / "deputies.json"
    if deps_file.exists():
        data = json.loads(deps_file.read_text())
        current_names = {d['name'].lower() for d in data['data']}
        print(f"Current Open Parliament: {len(current_names)}")
    
    # Check archived files
    archived = list(ARCHIVE_DIR.glob("*.md"))
    print(f"Archived files: {len(archived)}")
    
    # Check which are valid
    to_restore = []
    for f in archived:
        content = f.read_text(encoding='utf-8')
        # Extract name from content
        name_match = content.split('\n')[1] if '\n' in content else ''
        if name_match.startswith('name:'):
            name = name_match.split(':', 1)[1].strip().lower()
            if name in current_names:
                to_restore.append((f, name))
    
    print(f"\nCan restore (in current data): {len(to_restore)}")
    for f, name in to_restore[:10]:
        print(f"  {f.name}: {name}")
    
    if to_restore:
        # Restore them
        for f, name in to_restore:
            dest = VAULT_DIR / "politicians/deputies" / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"Restored: {f.name}")
        print(f"\nRestored: {len(to_restore)} files")
    
    # Remaining count
    remaining = len(list(VAULT_DIR.glob("politicians/deputies/*.md")))
    print(f"\nCurrent deputies: {remaining}")

if __name__ == "__main__":
    main()