#!/usr/bin/env python3
"""
StenoMD - Automated Romanian Parliament Knowledge Brain
Run this script daily to keep the vault updated with real stenogram data from cdep.ro
"""

import sys
from pathlib import Path

# Add project paths
SCRIPT_DIR = Path(__file__).parent.parent
PROJECT_DIR = SCRIPT_DIR

def run_daily_update():
    """Run the full daily update pipeline."""
    print("="*60)
    print("STENOMD - Daily Update Pipeline")
    print("="*60)
    
    # Step 1: Scrape new stenograms
    print("\n[1] Scraping new stenograms from cdep.ro...")
    import subprocess
    result = subprocess.run(
        [sys.executable, str(PROJECT_DIR / "scripts/stenomd_scraper.py")],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  Scraping complete")
    else:
        print(f"  Scraping had issues: {result.stderr[:200]}")
    
    # Step 2: Update knowledge graph
    print("\n[2] Updating knowledge graph...")
    result = subprocess.run(
        [sys.executable, str(PROJECT_DIR / "scripts/update_knowledge_graph.py")],
        capture_output=True, text=True
    )
    print(result.stdout)
    
    # Step 3: Sync to vault
    print("\n[3] Syncing to Obsidian vault...")
    result = subprocess.run(
        [sys.executable, str(PROJECT_DIR / "scripts/sync_vault.py")],
        capture_output=True, text=True
    )
    print(result.stdout)
    
    # Step 4: Validate
    print("\n[4] Validating...")
    result = subprocess.run(
        [sys.executable, str(PROJECT_DIR / "scripts/validate_knowledge_graph.py")],
        capture_output=True, text=True
    )
    print(result.stdout)
    
    print("\n" + "="*60)
    print("Daily update complete!")
    print("Refresh Obsidian with Ctrl+R to see updated vault.")
    print("="*60)

if __name__ == "__main__":
    run_daily_update()