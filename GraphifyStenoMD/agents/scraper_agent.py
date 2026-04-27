#!/usr/bin/env python3
"""
GraphifyStenoMD Scraper Agent
Analyzes graph for data gaps and prioritizes scraping.

Usage:
    python3 agents/scraper_agent.py --analyze
    python3 agents/scraper_agent.py --chamber cdep --years 2025
"""

import json
import sys
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Add project scripts to path centralized config
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
OUTPUT_DIR = PROJECT_DIR / "GraphifyStenoMD" "output"

class GapAwareScraper:
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
    
    def analyze_gaps(self):
        """Analyze graph for missing data."""
        if not self.graph_data:
            return {}
        
        gaps = {
            "politicians_no_party": [],
            "politicians_no_speeches": [],
            "politicians_no_committees": [],
            "laws_no_sponsors": [],
            "sessions_no_deputies": [],
        }
        
        # Analyze nodes for gaps
        for node in self.graph_data.get("nodes", []):
            source = node.get("source_file", "")
            
            # Politician gaps
            if "politicians/" in source:
                if not node.get("party"):
                    gaps["politicians_no_party"].append(node.get("label"))
                if not node.get("speeches_count") or node.get("speeches_count", 0) == 0:
                    gaps["politicians_no_speeches"].append(node.get("label"))
                if not node.get("committees"):
                    gaps["politicians_no_committees"].append(node.get("label"))
            
            # Law gaps
            if "laws/" in source and not node.get("sponsors"):
                gaps["laws_no_sponsors"].append(node.get("label"))
            
            # Session gaps
            if "sessions/" in source and not node.get("deputy_count"):
                gaps["sessions_no_deputies"].append(node.get("label"))
        
        return gaps
    
    def prioritize_scraping(self, gaps):
        """Determine scraping priorities."""
        priorities = []
        
        # Calculate gap counts
        gap_counts = {
            "party": len(gaps["politicians_no_party"]),
            "speeches": len(gaps["politicians_no_speeches"]),
            "committees": len(gaps["politicians_no_committees"]),
            "sponsors": len(gaps["laws_no_sponsors"]),
            "deputies": len(gaps["sessions_no_deputies"]),
        }
        
        # Priority by impact
        if gap_counts["party"] > 0:
            priorities.append({
                "rank": 1,
                "type": "party",
                "count": gap_counts["party"],
                "action": "enrich profiles with party data",
                "script": "scripts/enrich_profiles.py"
            })
        
        if gap_counts["speeches"] > 0:
            priorities.append({
                "rank": 2,
                "type": "speeches", 
                "count": gap_counts["speeches"],
                "action": "enrich profiles with speeches",
                "script": "scripts/add_speeches_to_profiles.py"
            })
        
        if gap_counts["committees"] > 0:
            priorities.append({
                "rank": 3,
                "type": "committees",
                "count": gap_counts["committees"],
                "action": "add committee data",
                "script": "scripts/add_committees.py"
            })
        
        if gap_counts["sponsors"] > 0:
            priorities.append({
                "rank": 4,
                "type": "sponsors",
                "count": gap_counts["sponsors"],
                "action": "add law sponsors",
                "script": "scripts/enrich_laws.py"
            })
        
        return priorities
    
    def run(self, chamber=None, years=None):
        """Run gap analysis and show priorities."""
        print("\n=== Gap Analysis ===")
        gaps = self.analyze_gaps()
        
        print(f"Politicians missing party: {len(gaps['politicians_no_party'])}")
        print(f"Politicians missing speeches: {len(gaps['politicians_no_speeches'])}")
        print(f"Politicians missing committees: {len(gaps['politicians_no_committees'])}")
        print(f"Laws missing sponsors: {len(gaps['laws_no_sponsors'])}")
        print(f"Sessions missing deputy data: {len(gaps['sessions_no_deputies'])}")
        
        print("\n=== Priority Queue ===")
        priorities = self.prioritize_scraping(gaps)
        
        for p in priorities:
            print(f"{p['rank']}. {p['type']}: {p['count']} items")
            print(f"   Action: {p['action']}")
            print(f"   Script: {p['script']}")
        
        return gaps, priorities
    
    def suggest_scripts(self, priorities):
        """Generate script suggestions."""
        suggestions = []
        
        for p in priorities:
            if p["type"] == "party":
                suggestions.append(f"# Enrich party data\npython3 {SCRIPTS_DIR}/enrich_profiles.py --type party")
            elif p["type"] == "speeches":
                suggestions.append(f"# Add speeches\npython3 {SCRIPTS_DIR}/add_speeches_to_profiles.py")
            elif p["type"] == "committees":
                suggestions.append(f"# Add committees\npython3 {SCRIPTS_DIR}/add_committees.py")
            elif p["type"] == "sponsors":
                suggestions.append(f"# Enrich law sponsors\npython3 {SCRIPTS_DIR}/enrich_laws.py")
        
        return suggestions


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gap-aware scraper agent")
    parser.add_argument("--analyze", action="store_true", help="Analyze gaps")
    parser.add_argument("--chamber", choices=["cdep", "senat"], help="Chamber to scrape")
    parser.add_argument("--years", help="Years to scrape (comma-separated)")
    
    args = parser.parse_args()
    
    agent = GapAwareScraper()
    
    if args.analyze:
        gaps, priorities = agent.run()
        print("\n=== Suggested Actions ===")
        suggestions = agent.suggest_scripts(priorities)
        for s in suggestions:
            print(s)
    else:
        print("Use --analyze to see gap analysis")
        print("Usage: python3 agents/scraper_agent.py --analyze")


if __name__ == "__main__":
    main()