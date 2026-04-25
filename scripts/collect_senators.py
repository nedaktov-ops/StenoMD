#!/usr/bin/env python3
"""
StenoMD Senator Collection Pipeline
Finds senators in Senate sessions not yet in vault and adds them.

Usage:
    python3 scripts/collect_senators.py
    python3 scripts/collect_senators.py --years 2024,2025,2026
    python3 scripts/collect_senators.py --years 2024,2025,2026 --max 50
"""

import sys
import re
import subprocess
import argparse
from pathlib import Path
from typing import Set, List

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
VAULT_DIR = PROJECT_DIR / "vault"


def get_senate_participants() -> Set[str]:
    """Get all participant names from Senate sessions."""
    participants = set()
    senate_dir = VAULT_DIR / "sessions" / "senate"
    
    if not senate_dir.exists():
        return participants
    
    for session_file in senate_dir.glob("*.md"):
        if session_file.name == "Index.md":
            continue
        try:
            content = session_file.read_text(encoding='utf-8')
            names = re.findall(r'participants:\s*-\s*(.+?)(?:\n|$)', content)
            for name in names:
                participants.add(name.strip())
        except Exception:
            pass
    
    return participants


def get_current_senators() -> Set[str]:
    """Get senators currently in vault."""
    senators = set()
    senator_dir = VAULT_DIR / "politicians" / "senators"
    
    if not senator_dir.exists():
        return senators
    
    for mp_file in senator_dir.glob("*.md"):
        if mp_file.name == "Index.md":
            continue
        senators.add(mp_file.stem.replace("-", " "))
    
    return senators


def find_missing_senators() -> List[str]:
    """Find senators in sessions but not in vault."""
    session_participants = get_senate_participants()
    current_senators = get_current_senators()
    
    missing = session_participants - current_senators
    return sorted(missing)


def run_senate_scraper(years: List[int], max_sessions: int = 50):
    """Run Senate agent for specified years."""
    for year in years:
        print(f"\n[RUN] senat_agent.py --year {year} --max {max_sessions} --sync-vault")
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_DIR / "scripts/agents/senat_agent.py"),
                "--year", str(year),
                "--max", str(max_sessions),
                "--sync-vault"
            ],
            capture_output=True,
            text=True
        )
        status = "OK" if result.returncode == 0 else "FAILED"
        print(f"  {year}: {status}")


def main():
    parser = argparse.ArgumentParser(description="Collect missing senators")
    parser.add_argument(
        "--years",
        default="2024,2025,2026",
        help="Years to scrape (comma-separated)"
    )
    parser.add_argument(
        "--max",
        type=int,
        default=50,
        help="Max sessions per year"
    )
    args = parser.parse_args()
    
    years = [int(y) for y in args.years.split(',')]
    
    print("=" * 60)
    print("StenoMD - Senator Collection Pipeline")
    print("=" * 60)
    
    # Step 1: Show current state
    current = get_current_senators()
    print(f"\n[STATUS] Senators in vault: {len(current)}")
    for s in sorted(current):
        print(f"  - {s}")
    
    # Step 2: Run additional scraping
    print(f"\n[SCRAPE] Running Senate agent for {years}...")
    run_senate_scraper(years, args.max)
    
    # Step 3: Find missing
    print("\n[CHECK] Finding missing senators...")
    missing = find_missing_senators()
    print(f"  Found {len(missing)} potential new senators")
    
    for name in missing[:15]:
        print(f"  + {name}")
    
    if len(missing) > 15:
        print(f"  ... and {len(missing) - 15} more")
    
    print("\n" + "=" * 60)
    print("Collection complete!")


if __name__ == "__main__":
    main()