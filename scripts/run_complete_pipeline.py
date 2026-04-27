#!/usr/bin/env python3
"""
Complete Parliament Data Pipeline

Phases:
1. Scrape cdep.ro
2. Scrape senat.ro  
3. Process and sync vault
4. Update knowledge graph

Usage:
    python3 scripts/run_complete_pipeline.py --full       # All phases
    python3 scripts/run_complete_pipeline.py --scrape   # Only scraping
    python3 scripts/run_complete_pipeline.py --sync    # Only sync
"""

import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")


def phase1_scrape_cdep():
    """Phase 1: Scrape cdep.ro."""
    print("=== Phase 1: Scraping cdep.ro ===")
    
    result = subprocess.run([
        sys.executable,
        str(PROJECT_ROOT / "scripts/agents/cdep_agent.py"),
        "--years", "2024,2025",
        "--max-id", "50",
        "--sync-vault"
    ], cwd=PROJECT_ROOT, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("  ✅ cdep.ro scraping complete")
        return True
    else:
        print(f"  ⚠️ cdep.ro: {result.stderr[:200] if result.stderr else 'No output'}")
        return False


def phase2_scrape_senat():
    """Phase 2: Scrape senat.ro."""
    print("=== Phase 2: Scraping senat.ro ===")
    
    result = subprocess.run([
        sys.executable,
        str(PROJECT_ROOT / "scripts/agents/senat_agent.py"),
        "--year", "2024",
        "--max", "30",
        "--sync-vault"
    ], cwd=PROJECT_ROOT, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("  ✅ senat.ro scraping complete")
        return True
    else:
        print(f"  ⚠️ senat.ro: {result.stderr[:200] if result.stderr else 'No output'}")
        return False


def phase3_sync_vault():
    """Phase 3: Sync vault to knowledge graph."""
    print("=== Phase 3: Syncing vault ===")
    
    result = subprocess.run([
        sys.executable,
        str(PROJECT_ROOT / "scripts/merge_vault_to_kg.py")
    ], cwd=PROJECT_ROOT, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("  ✅ Vault sync complete")
        return True
    else:
        print(f"  ⚠️ Sync: {result.stderr[:200] if result.stderr else 'No output'}")
        return False


def phase4_update_ai_bridge():
    """Phase 4: Update AI bridge."""
    print("=== Phase 4: Updating AI bridge ===")
    
    result = subprocess.run([
        sys.executable,
        str(PROJECT_ROOT / "obsidian-plugins/integration/copilot-bridge.py"),
        "--full-sync"
    ], cwd=PROJECT_ROOT, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("  ✅ AI bridge update complete")
        return True
    else:
        print(f"  ⚠️ Bridge: {result.stderr[:200] if result.stderr else 'No output'}")
        return False


def run_full_pipeline():
    """Run complete pipeline."""
    print(f"Starting pipeline: {datetime.now().isoformat()}")
    print("=" * 50)
    
    phases = [
        ("Scrape cdep.ro", phase1_scrape_cdep),
        ("Scrape senat.ro", phase2_scrape_senat),
        ("Sync vault", phase3_sync_vault),
        ("Update AI bridge", phase4_update_ai_bridge)
    ]
    
    results = []
    for name, func in phases:
        try:
            success = func()
            results.append((name, success))
        except Exception as e:
            print(f"  ❌ Error in {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("Pipeline Results:")
    print("=" * 50)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    success_count = sum(1 for _, s in results if s)
    print(f"\nResult: {success_count}/{len(results)} phases successful")
    
    return all(r for _, r in results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Complete Parliament Pipeline")
    parser.add_argument("--full", action="store_true", help="Run all phases")
    parser.add_argument("--scrape", action="store_true", help="Only scraping")
    parser.add_argument("--sync", action="store_true", help="Only sync")
    
    args = parser.parse_args()
    
    if args.full:
        run_full_pipeline()
    elif args.scrape:
        phase1_scrape_cdep()
        phase2_scrape_senat()
    elif args.sync:
        phase3_sync_vault()
        phase4_update_ai_bridge()
    else:
        print("Usage:")
        print("  python3 scripts/run_complete_pipeline.py --full    # All phases")
        print("  python3 scripts/run_complete_pipeline.py --scrape  # Only scraping")
        print("  python3 scripts/run_complete_pipeline.py --sync    # Only sync")