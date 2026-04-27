#!/usr/bin/env python3
"""
GraphifyStenoMD Missing Data Workflow
Identifies and reports on missing data in the project.

Usage:
    python3 workflows/missing_data.py           # Show gaps
    python3 workflows/missing_data.py --enrich   # Show enrichment options
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add project scripts to path for centralized config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

try:
    from config import get_config
    config = get_config()
    PROJECT_DIR = config.PROJECT_ROOT
    VAULT_DIR = config.VAULT_DIR
    KG_DIR = config.KG_DIR
    ENTITIES_FILE = config.ENTITIES_FILE
except ImportError:
    PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
    VAULT_DIR = PROJECT_DIR / "vault"
    KG_DIR = PROJECT_DIR / "knowledge_graph"
    ENTITIES_FILE = KG_DIR / "entities.json"

GRAPH_FILE = PROJECT_DIR / "Graphify" / "graphify-out" / "graph.json"

def load_graph():
    if GRAPH_FILE.exists():
        with open(GRAPH_FILE) as f:
            return json.load(f)
    return {"nodes": [], "links": []}

def analyze_gaps(graph):
    """Analyze missing data fields."""
    gaps = {
        "politicians_no_party": [],
        "politicians_no_speeches": [],
        "politicians_no_committees": [],
        "laws_no_sponsors": [],
        "sessions_no_deputies": [],
    }
    
    for node in graph.get("nodes", []):
        source = node.get("source_file", "")
        
        if "politicians/" in source or "senators/" in source or "deputies/" in source:
            if not node.get("party"):
                gaps["politicians_no_party"].append(node.get("label"))
            if not node.get("speeches_count") or node.get("speeches_count", 0) == 0:
                gaps["politicians_no_speeches"].append(node.get("label"))
            if not node.get("committees"):
                gaps["politicians_no_committees"].append(node.get("label"))
        
        if "laws/" in source and not node.get("sponsors"):
            gaps["laws_no_sponsors"].append(node.get("label"))
        
        if "sessions/" in source and not node.get("deputy_count"):
            gaps["sessions_no_deputies"].append(node.get("label"))
    
    return gaps

def print_gaps(gaps):
    """Print gap analysis."""
    print("=" * 50)
    print("MISSING DATA ANALYSIS")
    print("=" * 50)
    print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    print("### Politicians ###")
    print(f"Missing party: {len(gaps['politicians_no_party'])}")
    print(f"Missing speeches: {len(gaps['politicians_no_speeches'])}")
    print(f"Missing committees: {len(gaps['politicians_no_committees'])}")
    
    print("\n### Laws ###")
    print(f"Missing sponsors: {len(gaps['laws_no_sponsors'])}")
    
    print("\n### Sessions ###")
    print(f"Missing deputy data: {len(gaps['sessions_no_deputies'])}")
    
    total = sum(len(v) for v in gaps.values())
    print(f"\n### TOTAL ###")
    print(f"Missing data points: {total}")
    
    return gaps

def get_resolution_paths(gaps):
    """Get resolution recommendations."""
    paths = []
    
    if gaps["politicians_no_party"]:
        paths.append({
            "gap": "Missing party data",
            "resolution": "python3 scripts/enrich_profiles.py --type party",
            "priority": "HIGH"
        })
    
    if gaps["politicians_no_speeches"]:
        paths.append({
            "gap": "Missing speeches count", 
            "resolution": "python3 scripts/add_speeches_to_profiles.py",
            "priority": "MEDIUM"
        })
    
    if gaps["politicians_no_committees"]:
        paths.append({
            "gap": "Missing committees",
            "resolution": "python3 scripts/add_committees.py",
            "priority": "MEDIUM"
        })
    
    if gaps["laws_no_sponsors"]:
        paths.append({
            "gap": "Missing law sponsors",
            "resolution": "python3 scripts/enrich_laws.py",
            "priority": "LOW"
        })
    
    return paths

def print_resolution(paths):
    """Print resolution paths."""
    print("\n### RESOLUTION PATHS ###")
    for p in paths:
        print(f"\n[{p['priority']}] {p['gap']}")
        print(f"  {p['resolution']}")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--enrich", action="store_true", help="Show enrichment options")
    args = parser.parse_args()
    
    graph = load_graph()
    gaps = analyze_gaps(graph)
    print_gaps(gaps)
    
    if args.enrich:
        paths = get_resolution_paths(gaps)
        print_resolution(paths)

if __name__ == "__main__":
    main()