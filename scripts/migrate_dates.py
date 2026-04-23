#!/usr/bin/env python3
"""
Migrate Senate session filenames from Romanian format to ISO format.

Converts: 16-martie-2026.md -> 2026-03-16.md
"""
import re
from pathlib import Path

VAULT_SENATE = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/vault/sessions/senate")

MONTHS = {
    "ianuarie": "01", "februarie": "02", "martie": "03", "aprilie": "04",
    "mai": "05", "iunie": "06", "iulie": "07", "august": "08",
    "septembrie": "09", "octombrie": "10", "noiembrie": "11", "decembrie": "12"
}

def romanian_to_iso(filename: str) -> str | None:
    """Convert '16-martie-2026.md' to '2026-03-16.md'."""
    pattern = r"(\d{1,2})-([a-zăâîșț]+)-(\d{4})\.md$"
    match = re.match(pattern, filename, re.IGNORECASE)
    if not match:
        return None
    day, month_ro, year = match.groups()
    month = MONTHS.get(month_ro.lower())
    if not month:
        return None
    return f"{year}-{month}-{int(day):02d}.md"

def migrate():
    """Rename all Romanian date files to ISO format."""
    renamed = []
    skipped = []
    
    for f in VAULT_SENATE.glob("*.md"):
        if f.name.lower() == "index.md":
            skipped.append((f.name, "Index file - skipped"))
            continue
        
        new_name = romanian_to_iso(f.name)
        if new_name and new_name != f.name:
            new_path = f.parent / new_name
            if not new_path.exists():
                f.rename(new_path)
                renamed.append((f.name, new_name))
                print(f"Renamed: {f.name} -> {new_name}")
            else:
                skipped.append((f.name, f"Target exists: {new_name}"))
        else:
            skipped.append((f.name, "Already ISO or no match"))
    
    return renamed, skipped

if __name__ == "__main__":
    print(f"Migrating Senate session dates in: {VAULT_SENATE}")
    print("-" * 50)
    renamed, skipped = migrate()
    print("-" * 50)
    print(f"Renamed: {len(renamed)} files")
    print(f"Skipped: {len(skipped)} files")
    if skipped:
        print("\nSkipped files:")
        for name, reason in skipped[:10]:
            print(f"  {name}: {reason}")