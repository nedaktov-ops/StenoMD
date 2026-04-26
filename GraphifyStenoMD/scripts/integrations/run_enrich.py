#!/usr/bin/env python3
"""
StenoMD Scripts Integration
Runs existing StenoMD scripts with Graphify gap awareness.

Usage:
    python3 scripts/integrations/run_enrich.py --type party
    python3 scripts/integrations/run_enrich.py --check
"""

import sys
import subprocess
from pathlib import Path

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
SCRIPTS_DIR = PROJECT_DIR / "scripts"

# Mapping of gap types to scripts
ENRICH_SCRIPTS = {
    "party": SCRIPTS_DIR / "enrich_profiles.py",
    "speeches": SCRIPTS_DIR / "add_speeches_to_profiles.py",
    "committees": SCRIPTS_DIR / "add_committees.py",
    "sponsors": SCRIPTS_DIR / "enrich_laws.py",
    "stable_id": SCRIPTS_DIR / "generate_stable_ids.py",
}

SCRAPE_SCRIPTS = {
    "cdep": SCRIPTS_DIR / "agents" / "cdep_agent.py",
    "senate": SCRIPTS_DIR / "agents" / "senat_agent.py",
    "master": SCRIPTS_DIR / "stenomd_master.py",
}

def list_available_scripts():
    """List available scripts."""
    print("\n=== Available Enrichment Scripts ===")
    for name, path in ENRICH_SCRIPTS.items():
        if path.exists():
            print(f"  [{name}]: {path}")
        else:
            print(f"  [{name}]: NOT FOUND")
    
    print("\n=== Available Scraping Scripts ===")
    for name, path in SCRAPE_SCRIPTS.items():
        if path.exists():
            print(f"  [{name}]: {path}")
        else:
            print(f"  [{name}]: NOT FOUND")

def run_enrich(enrich_type, dry_run=True):
    """Run enrichment script."""
    script = ENRICH_SCRIPTS.get(enrich_type)
    
    if not script:
        print(f"Unknown enrichment type: {enrich_type}")
        return False
    
    if not script.exists():
        print(f"Script not found: {script}")
        return False
    
    print(f"\n=== Would Run: {script.name} ===")
    
    if dry_run:
        print(f"(DRY RUN - no actual execution)")
        print(f"Command: python3 {script}")
        return True
    
    # Actually run
    print(f"Running: python3 {script}")
    result = subprocess.run(["python3", str(script)], cwd=PROJECT_DIR)
    return result.returncode == 0

def run_scrape(scrape_type, dry_run=True):
    """Run scraping script."""
    script = SCRAPE_SCRIPTS.get(scrape_type)
    
    if not script:
        print(f"Unknown scrape type: {scrape_type}")
        return False
    
    if not script.exists():
        print(f"Script not found: {script}")
        return False
    
    print(f"\n=== Would Run: {script.name} ===")
    
    if dry_run:
        print(f"(DRY RUN - no actual execution)")
        print(f"Command: python3 {script} --help")
        return True
    
    print(f"Running: python3 {script}")
    result = subprocess.run(["python3", str(script)], cwd=PROJECT_DIR)
    return result.returncode == 0

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", help="Enrichment or scrape type")
    parser.add_argument("--scrape", help="Scrape type (cdep, senate, master)")
    parser.add_argument("--list", action="store_true", help="List available scripts")
    parser.add_argument("--run", action="store_true", help="Actually run (not dry run)")
    args = parser.parse_args()
    
    if args.list:
        list_available_scripts()
        return
    
    if args.type:
        run_enrich(args.type, dry_run=not args.run)
    elif args.scrape:
        run_scrape(args.scrape, dry_run=not args.run)
    else:
        print("Usage:")
        print("  python3 scripts/integrations/run_enrich.py --list")
        print("  python3 scripts/integrations/run_enrich.py --type party --run")
        print("  python3 scripts/integrations/run_enrich.py --scrape cdep")

if __name__ == "__main__":
    main()