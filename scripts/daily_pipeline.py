#!/usr/bin/env python3
"""
Daily enrichment pipeline - orchestrates all enrichment steps.
Runs automatically via cron/systemd timer.
"""

import json
import subprocess
import sys
from datetime import datetime
import argparse
from pathlib import Path

BASE = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
VAULT = BASE / "vault"
LOG_DIR = BASE / "vault" / "ai-memory"

def log(message: str, level="INFO"):
    """Log to MemPalace-compatible daily log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    log_file = LOG_DIR / "pipeline_log.md"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"- [{timestamp}] [{level}] {message}\n")
    print(f"[{level}] {message}")

def run_script(script_name: str, desc: str) -> bool:
    """Run a Python script and capture result"""
    log(f"Starting: {desc}")
    result = subprocess.run(
        [sys.executable, f"scripts/{script_name}"],
        cwd=BASE,
        capture_output=True,
        text=True,
        timeout=300
    )
    if result.returncode != 0:
        log(f"FAILED: {desc}\nSTDERR: {result.stderr[:500]}", "ERROR")
        return False
    log(f"Completed: {desc}")
    return True

def quick_fix_enrichment():
    """Quick fix: reconcile numeric files, add committees, update aliases"""
    steps = [
        ("final_reconciliation_v2.py", "Add idm and committees to numeric files"),
        ("update_search_aliases.py", "Update search aliases for all files"),
        ("populate_activity.py", "Populate speeches_count and laws_proposed"),
    ]
    return all(run_script(script, desc) for script, desc in steps)

def merge_to_kg():
    """Merge enriched vault to knowledge graph"""
    return run_script("merge_vault_to_kg.py", "Merge vault to knowledge graph")

def autobrowser_scrape():
    """Scrape new sessions using Playwright (light version)"""
    # Try to import playwright; if not available, skip
    try:
        import playwright
        result = subprocess.run(
            [sys.executable, "scripts/scrape_parliament_playwright.py", "--max-cdep", "20", "--max-senat", "10"],
            cwd=BASE,
            capture_output=True,
            text=True,
            timeout=600
        )
        if result.returncode == 0:
            log("Auto-Browser scraping completed")
            return True
        else:
            log(f"Auto-Browser error: {result.stderr[:200]}", "WARNING")
            return False  # Non-critical
    except ImportError:
        log("Playwright not installed - skipping Auto-Browser", "WARNING")
        return True  # Non-critical

def validate_vault():
    """Check for placeholder values"""
    result = subprocess.run(
        ["bash", "-c", "grep -r 'speeches_count: (See' vault/politicians/deputies/*.md 2>/dev/null | wc -l"],
        cwd=BASE,
        capture_output=True,
        text=True
    )
    count = int(result.stdout.strip() or 0)
    if count > 0:
        log(f"Warning: {count} deputies still have placeholder speeches_count", "WARNING")
    return True

def main():
    parser = argparse.ArgumentParser(description="Daily enrichment pipeline")
    parser.add_argument("--skip-scrape", action="store_true", help="Skip Auto-Browser scraping")
    parser.add_argument("--skip-quickfix", action="store_true", help="Skip quick fix (metadata reconciliation)")
    args = parser.parse_args()

    log("=== DAILY ENRICHMENT PIPELINE STARTED ===")
    
    success = True
    
    # Step 1: Quick fix (metadata reconciliation)
    if not args.skip_quickfix:
        success &= quick_fix_enrichment()
    
    # Step 2: Auto-Browser scraping
    if not args.skip_scrape:
        success &= autobrowser_scrape()
    
    # Step 3: Merge to knowledge graph
    success &= merge_to_kg()
    
    # Step 4: Validation
    validate_vault()
    
    # Final status
    if success:
        log("Pipeline completed successfully", "INFO")
        # Touch a success file for monitoring
        (BASE / "data" / "last_successful_run.txt").write_text(datetime.now().isoformat())
    else:
        log("Pipeline completed with errors", "ERROR")
    
    log("=== DAILY ENRICHMENT PIPELINE FINISHED ===")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())