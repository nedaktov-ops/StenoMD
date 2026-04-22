#!/usr/bin/env python3
"""
StenoMD Master Controller
Coordinates CDEP and Senate agents for unified scraping.

Usage:
    python3 stenomd_master.py --all --year 2024 --max 10
    python3 stenomd_master.py --cdep --year 2024
    python3 stenomd_master.py --senate --year 2024
    python3 stenomd_master.py --sync-vault
    python3 stenomd_master.py --status
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import json

SCRIPT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from agents.cdep_agent import EnhancedCDEPAgent
from agents.senat_agent import SenateAgent


PROJECT_DIR = SCRIPT_DIR.parent
KG_DIR = PROJECT_DIR / "knowledge_graph"
VAULT_DIR = PROJECT_DIR / "vault"


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[MASTER:{ts}] {msg}")


def save_checkpoint(cdep_stats: dict, senat_stats: dict):
    """Save checkpoint for resume capability."""
    checkpoint = {
        "last_updated": datetime.now().isoformat(),
        "cdep": {
            "sessions_found": cdep_stats.get("sessions_found", 0),
            "sessions_scraped": cdep_stats.get("sessions_scraped", 0),
            "statements_extracted": cdep_stats.get("statements_extracted", 0),
        },
        "senate": {
            "sessions_found": senat_stats.get("sessions_found", 0),
            "sessions_scraped": senat_stats.get("sessions_scraped", 0),
            "senators_found": len(senat_stats.get("senators_found", set())),
        }
    }
    
    KG_DIR.mkdir(parents=True, exist_ok=True)
    with open(KG_DIR / "checkpointer.json", "w") as f:
        json.dump(checkpoint, f, indent=2)
    
    log(f"Checkpoint saved to {KG_DIR}/checkpointer.json")


def load_checkpoint() -> dict:
    """Load checkpoint for resume."""
    checkpoint_file = KG_DIR / "checkpointer.json"
    if checkpoint_file.exists():
        with open(checkpoint_file) as f:
            return json.load(f)
    return {}


def run_cdep(year: int, max_sessions: int, sync_vault: bool):
    """Run CDEP agent."""
    log(f"=== Starting CDEP Agent ===")
    agent = EnhancedCDEPAgent()
    result = agent.run(years=[year], max_id=max_sessions)
    log(f"=== CDEP Complete: {result['sessions_scraped']} sessions ===")
    return result


def run_senate(year: int, max_sessions: int, sync_vault: bool):
    """Run Senate agent."""
    log(f"=== Starting Senate Agent ===")
    agent = SenateAgent()
    result = agent.run(year, max_sessions, sync_vault)
    log(f"=== Senate Complete: {result['sessions_scraped']} sessions ===")
    return result


def merge_knowledge_graph():
    """Merge entities from both agents into unified KG."""
    log("Merging knowledge graph entities...")
    
    kg_file = KG_DIR / "entities.json"
    if not kg_file.exists():
        kg_file = KG_DIR / "entities.json"
    
    entities = {
        "last_updated": datetime.now().isoformat(),
        "persons": [],
        "sessions": [],
        "laws": [],
        "chambers": {
            "senate": {"count": 0},
            "deputies": {"count": 0}
        }
    }
    
    # Count senators
    senators_dir = VAULT_DIR / "politicians" / "senators"
    if senators_dir.exists():
        entities["chambers"]["senate"]["count"] = len(list(senators_dir.glob("*.md")))
    
    # Count deputies
    deputies_dir = VAULT_DIR / "politicians" / "deputies"
    if deputies_dir.exists():
        entities["chambers"]["deputies"]["count"] = len(list(deputies_dir.glob("*.md")))
    
    # Count sessions
    senate_sessions = VAULT_DIR / "sessions" / "senate"
    if senate_sessions.exists():
        entities["chambers"]["senate"]["sessions"] = len(list(senate_sessions.glob("*.md")))
    
    with open(kg_file, "w") as f:
        json.dump(entities, f, indent=2)
    
    log(f"Unified KG: {entities['chambers']['senate']['count']} senators, "
        f"{entities['chambers']['deputies']['count']} deputies")


def show_status():
    """Show current status."""
    checkpoint = load_checkpoint()
    
    print("\n=== StenoMD Status ===")
    print(f"Last updated: {checkpoint.get('last_updated', 'Never')}")
    print()
    
    print("CDEP Agent:")
    cdep = checkpoint.get("cdep", {})
    print(f"  Sessions found: {cdep.get('sessions_found', 0)}")
    print(f"  Sessions scraped: {cdep.get('sessions_scraped', 0)}")
    print(f"  Statements: {cdep.get('statements_extracted', 0)}")
    print()
    
    print("Senate Agent:")
    senat = checkpoint.get("senate", {})
    print(f"  Sessions found: {senat.get('sessions_found', 0)}")
    print(f"  Sessions scraped: {senat.get('sessions_scraped', 0)}")
    print(f"  Senators: {senat.get('senators_found', 0)}")
    print()
    
    print("Vault:")
    print(f"  Senators: {len(list((VAULT_DIR / 'politicians' / 'senators').glob('*.md')))}")
    print(f"  Deputies: {len(list((VAULT_DIR / 'politicians' / 'deputies').glob('*.md')))}")
    print(f"  Senate sessions: {len(list((VAULT_DIR / 'sessions' / 'senate').glob('*.md')))}")


def main():
    parser = argparse.ArgumentParser(description="StenoMD Master Controller")
    parser.add_argument("--all", action="store_true", help="Run both agents")
    parser.add_argument("--cdep", action="store_true", help="Run CDEP agent only")
    parser.add_argument("--senate", action="store_true", help="Run Senate agent only")
    parser.add_argument("--year", type=int, default=2024, help="Year to process")
    parser.add_argument("--max", type=int, default=10, help="Max sessions per agent")
    parser.add_argument("--sync-vault", action="store_true", help="Sync to vault")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--merge", action="store_true", help="Merge knowledge graph")
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
        return
    
    if args.merge:
        merge_knowledge_graph()
        return
    
    cdep_result = {}
    senat_result = {}
    
    if args.all or args.cdep:
        cdep_result = run_cdep(args.year, args.max, args.sync_vault)
    
    if args.all or args.senate:
        senat_result = run_senate(args.year, args.max, args.sync_vault)
    
    if cdep_result or senat_result:
        save_checkpoint(cdep_result, senat_result)
        merge_knowledge_graph()
    
    if not (args.all or args.cdep or args.senate or args.merge):
        parser.print_help()


if __name__ == "__main__":
    main()