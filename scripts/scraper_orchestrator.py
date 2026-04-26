#!/usr/bin/env python3
"""
Scraper Orchestrator with Graph Gap Awareness
Automatically selects best scraper based on graph gaps.

Usage:
    python3 scripts/scraper_orchestrator.py --auto
    python3 scripts/scraper_orchestrator.py --priority party
    python3 scripts/scraper_orchestrator.py --status
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
GRAPH_FILE = PROJECT_DIR / "Graphify" / "graphify-out" / "graph.json"
SCRAPERS_DIR = PROJECT_DIR / "scripts"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

class ScraperOrchestrator:
    def __init__(self):
        self.graph_data = None
        self.load_graph()
    
    def load_graph(self):
        """Load graph for gap analysis."""
        if GRAPH_FILE.exists():
            with open(GRAPH_FILE) as f:
                self.graph_data = json.load(f)
            log(f"Loaded graph: {len(self.graph_data.get('nodes', []))} nodes")
        else:
            log("No graph found - run /graphify first")
            sys.exit(1)
    
    def analyze_gaps(self):
        """Analyze gaps in graph."""
        gaps = {
            "senators_need_party": 0,
            "deputies_need_party": 0,
            "need_speeches": 0,
            "need_committees": 0,
            "laws_need_sponsors": 0,
            "sessions_need_activity": 0,
        }
        
        for node in self.graph_data.get("nodes", []):
            source = node.get("source_file", "")
            
            # Senator gaps
            if "senators/" in source:
                if not node.get("party"):
                    gaps["senators_need_party"] += 1
                if not node.get("speeches_count"):
                    gaps["need_speeches"] += 1
                if not node.get("committees"):
                    gaps["need_committees"] += 1
            
            # Deputy gaps
            if "deputies/" in source or ("politicians/" in source and "senators" not in source):
                if not node.get("party"):
                    gaps["deputies_need_party"] += 1
            
            # Law gaps
            if "laws/" in source:
                if not node.get("sponsors") and not node.get("proposed_by"):
                    gaps["laws_need_sponsors"] += 1
            
            # Session gaps
            if "sessions/" in source:
                if not node.get("deputy_count"):
                    gaps["sessions_need_activity"] += 1
        
        return gaps
    
    def prioritize_scraping(self):
        """Determine scraper priorities based on gaps."""
        gaps = self.analyze_gaps()
        
        priorities = []
        
        # Calculate priority scores
        if gaps["senators_need_party"] > 0:
            priorities.append({
                "rank": 1,
                "scraper": "senat_agent.py",
                "target": "party",
                "count": gaps["senators_need_party"],
                "impact": "HIGH"
            })
        
        if gaps["deputies_need_party"] > 0:
            priorities.append({
                "rank": 2,
                "scraper": "cdep_agent.py",
                "target": "party",
                "count": gaps["deputies_need_party"],
                "impact": "HIGH"
            })
        
        if gaps["need_speeches"] > 0:
            priorities.append({
                "rank": 3,
                "scraper": "speech_extractor.py",
                "target": "speeches", 
                "count": gaps["need_speeches"],
                "impact": "MEDIUM"
            })
        
        if gaps["need_committees"] > 0:
            priorities.append({
                "rank": 4,
                "scraper": "scrape_committees.py",
                "target": "committees",
                "count": gaps["need_committees"],
                "impact": "MEDIUM"
            })
        
        if gaps["laws_need_sponsors"] > 0:
            priorities.append({
                "rank": 5,
                "scraper": "enrich_laws.py",
                "target": "sponsors",
                "count": gaps["laws_need_sponsors"],
                "impact": "LOW"
            })
        
        return sorted(priorities, key=lambda x: x["rank"])
    
    def run_auto(self):
        """Run automatic scraping based on priorities."""
        log("=== Auto Scraper Mode ===")
        
        gaps = self.analyze_gaps()
        
        log("\n=== Gap Analysis ===")
        for gap, count in gaps.items():
            log(f"{gap}: {count}")
        
        priorities = self.prioritize_scraping()
        
        log("\n=== Priority Queue ===")
        for p in priorities:
            log(f"{p['rank']}. {p['scraper']} for {p['target']}: {p['count']} targets")
        
        log("\n=== Recommended Actions ===")
        for p in priorities[:3]:
            log(f"- Run: {p['scraper']} to fill {p['count']} {p['target']} gaps")
            log(f"  Command: python3 scripts/{p['scraper']}")
    
    def run_priority(self, priority_target):
        """Run specific priority."""
        priorities = self.prioritize_scraping()
        
        for p in priorities:
            if p["target"] == priority_target:
                log(f"Running {p['scraper']} for {p['target']}...")
                # Note: Would actually run scraper here
                log(f"Would execute: python3 scripts/{p['scraper']}")
                return
        
        log(f"No scraper found for target: {priority_target}")
    
    def show_status(self):
        """Show scraper status."""
        log("=== Scraper Status ===")
        
        gaps = self.analyze_gaps()
        priorities = self.prioritize_scraping()
        
        log(f"\nGraph nodes: {len(self.graph_data.get('nodes', []))}")
        log(f"Graph edges: {len(self.graph_data.get('links', []))}")
        
        log("\n=== Gap Summary ===")
        total_gaps = sum(gaps.values())
        log(f"Total missing data points: {total_gaps}")
        
        log("\n=== Priorities ===")
        for p in priorities:
            print(f"  {p['rank']}. [{p['impact']}] {p['scraper']}: {p['count']} {p['target']}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scraper orchestrator")
    parser.add_argument("--auto", action="store_true", help="Auto-select scraper")
    parser.add_argument("--priority", help="Run specific priority (party, speeches, committees)")
    parser.add_argument("--status", action="store_true", help="Show status")
    args = parser.parse_args()
    
    orch = ScraperOrchestrator()
    
    if args.status:
        orch.show_status()
    elif args.priority:
        orch.run_priority(args.priority)
    else:
        orch.run_auto()

if __name__ == "__main__":
    main()