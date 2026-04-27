#!/usr/bin/env python3
"""
GraphifyStenoMD Enrichment Agent
Identifies data gaps and runs enrichment pipelines.

Usage:
    python3 agents/enrichment_agent.py --analyze
    python3 agents/enrichment_agent.py --type party
    python3 agents/enrichment_agent.py --politician "NAME"
"""

import json
import sys
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
    SCRIPTS_DIR = config.PROJECT_ROOT / "scripts"
except ImportError:
    PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
    VAULT_DIR = PROJECT_DIR / "vault"
    KG_DIR = PROJECT_DIR / "knowledge_graph"
    ENTITIES_FILE = KG_DIR / "entities.json"
    SCRIPTS_DIR = PROJECT_DIR / "scripts"

GRAPH_FILE = PROJECT_DIR / "Graphify" / "graphify-out" / "graph.json"

class EnrichmentAgent:
    def __init__(self):
        self.graph_data = None
        self.load_graph()
    
    def load_graph(self):
        """Load existing graph."""
        if GRAPH_FILE.exists():
            with open(GRAPH_FILE) as f:
                self.graph_data = json.load(f)
            print(f"Loaded graph: {len(self.graph_data.get('nodes', []))} nodes")
        else:
            print("No graph found. Run /graphify first.")
            self.graph_data = {"nodes": [], "links": []}
    
    def analyze_enrichment_targets(self):
        """Find entities needing enrichment."""
        targets = {
            "party": [],
            "speeches": [],
            "committees": [],
            "sponsors": [],
            "stable_id": [],
        }
        
        for node in self.graph_data.get("nodes", []):
            source = node.get("source_file", "")
            
            if "politicians/" in source:
                # Check missing fields
                if not node.get("party"):
                    targets["party"].append(node.get("label"))
                if not node.get("speeches_count"):
                    targets["speeches"].append(node.get("label"))
                if not node.get("committees"):
                    targets["committees"].append(node.get("label"))
                if not node.get("stable_id"):
                    targets["stable_id"].append(node.get("label"))
            
            if "laws/" in source and not node.get("sponsors"):
                targets["sponsors"].append(node.get("label"))
        
        return targets
    
    def get_enrichment_scripts(self, enrich_type):
        """Get scripts for enrichment type."""
        scripts = {
            "party": [
                "scripts/enrich_profiles.py --type party",
                "scripts/generate_stable_ids.py"
            ],
            "speeches": [
                "scripts/add_speeches_to_profiles.py"
            ],
            "committees": [
                "scripts/add_committees.py"
            ],
            "sponsors": [
                "scripts/enrich_laws.py",
                "scripts/link_proposal_sponsors.py"
            ],
            "stable_id": [
                "scripts/generate_stable_ids.py"
            ]
        }
        return scripts.get(enrich_type, [])
    
    def run(self, enrich_type=None, politician=None):
        """Run enrichment analysis."""
        if enrich_type and enrich_type != "all":
            print(f"\n=== Enrichment: {enrich_type} ===")
            scripts = self.get_enrichment_scripts(enrich_type)
            print(f"Scripts to run:")
            for s in scripts:
                print(f"  python3 {PROJECT_DIR}/{s}")
            return
        
        print("\n=== Enrichment Targets ===")
        targets = self.analyze_enrichment_targets()
        
        print(f"Missing party: {len(targets['party'])}")
        print(f"Missing speeches: {len(targets['speeches'])}")
        print(f"Missing committees: {len(targets['committees'])}")
        print(f"Missing law sponsors: {len(targets['sponsors'])}")
        print(f"Missing stable_id: {len(targets['stable_id'])}")
        
        print("\n=== By Type ===")
        for etype, items in targets.items():
            if items:
                print(f"\n{etype.upper()} ({len(items)}):")
                for item in items[:5]:
                    print(f"  - {item}")
                if len(items) > 5:
                    print(f"  ... and {len(items) - 5} more")
        
        return targets


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Enrichment agent")
    parser.add_argument("--analyze", action="store_true", help="Analyze enrichment targets")
    parser.add_argument("--type", choices=["party", "speeches", "committees", "sponsors", "all"], help="Enrichment type")
    parser.add_argument("--politician", help="Specific politician to check")
    
    args = parser.parse_args()
    
    agent = EnrichmentAgent()
    
    if args.analyze:
        agent.run(args.type)
    else:
        print("Use --analyze to see enrichment targets")
        print("Usage: python3 agents/enrichment_agent.py --analyze --type party")


if __name__ == "__main__":
    main()