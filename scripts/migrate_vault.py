#!/usr/bin/env python3
"""
StenoMD Vault Migration Script
Consolidates vault structure by migrating root-level files to proper chambers.

Migration:
- vault/sessions/*.md → vault/sessions/deputies/ or vault/sessions/senate/
- vault/politicians/*.md → vault/politicians/deputies/ or vault/politicians/senators/

Detection:
- If contains "senat" or "Senat" or senate-related → senate/
- If contains "cdep" or "Camera" or deputies-related → deputies/
- Default: Use date parsing to determine chamber
"""

import re
import shutil
from pathlib import Path
from datetime import datetime

VAULT = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/vault")

SOURCES = {
    "sessions_root": VAULT / "sessions",
    "politicians_root": VAULT / "politicians",
}

TARGETS = {
    "deputies_sessions": VAULT / "sessions" / "deputies",
    "senate_sessions": VAULT / "sessions" / "senate",
    "deputies_politicians": VAULT / "politicians" / "deputies",
    "senators_politicians": VAULT / "politicians" / "senators",
}

SENATE_KEYWORDS = ["senat", "senatului", "senator", "camera superioara", "plen"]
DEPUTIES_KEYWORDS = ["camera deputatilor", "deputat", "deputati", "deputies", "camera inferioara"]

def detect_chamber(content: str, filename: str) -> str:
    """Detect chamber from content or filename."""
    text = (content + " " + filename).lower()
    
    for kw in SENATE_KEYWORDS:
        if kw in text:
            return "senate"
    for kw in DEPUTIES_KEYWORDS:
        if kw in text:
            return "deputies"
    
    return None

def parse_date_from_filename(filename: str) -> str | None:
    """Extract date from filename to help determine session."""
    patterns = [
        r"(\d{4})-(\d{2})-(\d{2})",
        r"(\d{8})",
        r"(\d{1,2})-(\w+)-(\d{4})",
    ]
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            return match.group()
    return None

def migrate():
    """Main migration function."""
    migrated = []
    skipped = []
    errors = []
    
    for target_key, target_dir in TARGETS.items():
        target_dir.mkdir(parents=True, exist_ok=True)
    
    if SOURCES["sessions_root"].exists():
        for f in SOURCES["sessions_root"].glob("*.md"):
            if f.name.lower() == "index.md":
                skipped.append((f.name, "Index file"))
                continue
            
            try:
                content = f.read_text(encoding="utf-8")
                chamber = detect_chamber(content, f.name)
                
                if chamber == "senate":
                    target = TARGETS["senate_sessions"]
                elif chamber == "deputies":
                    target = TARGETS["deputies_sessions"]
                elif f.name.startswith("202"):
                    target = TARGETS["senate_sessions"]
                else:
                    target = TARGETS["deputies_sessions"]
                
                target_file = target / f.name
                if not target_file.exists():
                    shutil.move(str(f), str(target_file))
                    migrated.append((f.name, str(target_file.name)))
                else:
                    skipped.append((f.name, f"Target exists: {target_file.name}"))
                    
            except Exception as e:
                errors.append((f.name, str(e)))
    
    if SOURCES["politicians_root"].exists():
        for f in SOURCES["politicians_root"].glob("*.md"):
            if f.name.lower() == "index.md":
                skipped.append((f.name, "Index file"))
                continue
            
            try:
                content = f.read_text(encoding="utf-8")
                chamber = detect_chamber(content, f.name)
                
                if chamber == "senate":
                    target = TARGETS["senators_politicians"]
                elif chamber == "deputies":
                    target = TARGETS["deputies_politicians"]
                elif "senator" in f.name.lower():
                    target = TARGETS["senators_politicians"]
                else:
                    target = TARGETS["deputies_politicians"]
                
                target_file = target / f.name
                if not target_file.exists():
                    shutil.move(str(f), str(target_file))
                    migrated.append((f.name, str(target_file.name)))
                else:
                    skipped.append((f.name, f"Target exists: {target_file.name}"))
                    
            except Exception as e:
                errors.append((f.name, str(e)))
    
    return migrated, skipped, errors

if __name__ == "__main__":
    print(f"Starting vault migration: {datetime.now()}")
    print(f"Vault: {VAULT}")
    print("-" * 50)
    
    migrated, skipped, errors = migrate()
    
    print("-" * 50)
    print(f"Migrated: {len(migrated)} files")
    print(f"Skipped: {len(skipped)} files")
    print(f"Errors: {len(errors)} files")
    
    if errors:
        print("\nErrors:")
        for name, err in errors:
            print(f"  {name}: {err}")