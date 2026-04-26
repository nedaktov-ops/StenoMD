#!/usr/bin/env python3
"""Normalize session file names to ISO format (YYYY-MM-DD.md)."""

import re
from pathlib import Path

PROJECT = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
VAULT = PROJECT / "vault"

# Romanian month names to numbers
MONTHS = {
    'ianuarie': '01', 'februarie': '02', 'martie': '03', 'martie': '03',
    'aprilie': '04', 'mai': '05', 'iunie': '06', 'iulie': '07',
    'august': '08', 'septembrie': '09', 'octombrie': '10',
    'noiembrie': '11', 'decembrie': '12'
}

def normalize_romanain_date(filename: str) -> str:
    """Convert filename like 30-martie-2026.md to 2026-03-30.md"""
    stem = Path(filename).stem
    m = re.match(r'(\d{1,2})-([a-zăâîșț]+)-(\d{4})', stem, re.IGNORECASE)
    if m:
        day, month_ro, year = m.groups()
        month_ro = month_ro.lower()
        if month_ro in MONTHS:
            month = MONTHS[month_ro]
            return f"{year}-{month}-{int(day):02d}.md"
    return None

def normalize_yyyymmdd(filename: str) -> str:
    """Convert filename like 20241220.md to 2024-12-20.md"""
    stem = Path(filename).stem
    m = re.match(r'(\d{4})(\d{2})(\d{2})', stem)
    if m:
        year, month, day = m.groups()
        return f"{year}-{month}-{day}.md"
    return None

def main():
    renamed = 0
    errors = 0
    
    # Process sessions/deputies
    dep_dir = VAULT / "sessions" / "deputies"
    sen_dir = VAULT / "sessions" / "senate"
    
    for session_dir in [dep_dir, sen_dir]:
        if not session_dir.exists():
            print(f"Directory not found: {session_dir}")
            continue
        
        for f in list(session_dir.glob("*.md")):
            if f.name == "Index.md":
                continue
            
            new_name = None
            
            # Check Romanian format
            if re.match(r'^\d+-[a-zăâîșț]+-\d{4}\.md$', f.name, re.IGNORECASE):
                new_name = normalize_romanain_date(f.name)
            # Check YYYYMMDD format
            elif re.match(r'^\d{8}\.md$', f.name):
                new_name = normalize_yyyymmdd(f.name)
            
            if new_name:
                new_path = f.parent / new_name
                if not new_path.exists():
                    try:
                        f.rename(new_path)
                        print(f"Renamed: {session_dir.name}/{f.name} -> {new_name}")
                        renamed += 1
                    except Exception as e:
                        print(f"Error renaming {f.name}: {e}")
                        errors += 1
                else:
                    # Target exists, delete duplicate
                    try:
                        f.unlink()
                        print(f"Deleted duplicate: {session_dir.name}/{f.name} (target exists)")
                        renamed += 1
                    except Exception as e:
                        print(f"Error deleting {f.name}: {e}")
                        errors += 1
    
    print(f"\nRenamed/deleted: {renamed}, errors: {errors}")

if __name__ == "__main__":
    main()
