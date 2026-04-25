#!/usr/bin/env python3
"""
StenoMD - Automated Romanian Parliament Knowledge Brain
Daily update pipeline using modern cdep_agent.py and senat_agent.py

Usage:
    python3 scripts/run_daily.py
    python3 scripts/run_daily.py --dry-run
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.parent
PROJECT_DIR = SCRIPT_DIR


def run_daily_update(dry_run=False):
    """Run the full daily update pipeline."""
    print("=" * 60)
    print("STENOMD - Daily Update Pipeline")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    
    if dry_run:
        print("\n[DRY RUN] Would execute:")
        print("  [1] cdep_agent.py --years 2024,2025,2026 --max-id 50 --sync-vault")
        print("  [2] senat_agent.py --year 2026 --max 30 --sync-vault")
        print("  [3] merge_vault_to_kg.py")
        print("  [4] validate_knowledge_graph.py")
        print("  [5] stenomd_master.py --status")
        return
    
    # Step 1: Scrape Chamber (Deputies)
    print("\n[1] Scraping Chamber from cdep.ro...")
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_DIR / "scripts/agents/cdep_agent.py"),
            "--years", "2024,2025,2026",
            "--max-id", "50",
            "--sync-vault"
        ],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("  Chamber scraping complete")
    else:
        print(f"  Chamber issues: {result.stderr[:200] if result.stderr else 'N/A'}")
    
    # Step 2: Scrape Senate
    print("\n[2] Scraping Senate from senat.ro...")
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_DIR / "scripts/agents/senat_agent.py"),
            "--year", "2026",
            "--max", "30",
            "--sync-vault"
        ],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("  Senate scraping complete")
    else:
        print(f"  Senate issues: {result.stderr[:200] if result.stderr else 'N/A'}")
    
    # Step 3: Merge vault to knowledge graph
    print("\n[3] Populating knowledge graph...")
    result = subprocess.run(
        [sys.executable, str(PROJECT_DIR / "scripts/merge_vault_to_kg.py")],
        capture_output=True,
        text=True
    )
    print(result.stdout[:500] if result.stdout else "Complete")
    
    # Step 4: Validate data
    print("\n[4] Validating data...")
    result = subprocess.run(
        [sys.executable, str(PROJECT_DIR / "scripts/validate_knowledge_graph.py")],
        capture_output=True,
        text=True
    )
    print(result.stdout[:300] if result.stdout else "Complete")
    
    # Step 5: Show status
    print("\n[5] Getting statistics...")
    result = subprocess.run(
        [sys.executable, str(PROJECT_DIR / "scripts/stenomd_master.py"), "--status"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    
    print("\n" + "=" * 60)
    print("Daily update complete!")
    print(f"Completed: {datetime.now().isoformat()}")
    print("Refresh Obsidian with Ctrl+R to see updated vault.")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StenoMD Daily Update")
    parser.add_argument("--dry-run", action="store_true", help="Show what would run")
    args = parser.parse_args()
    
    run_daily_update(dry_run=args.dry_run)