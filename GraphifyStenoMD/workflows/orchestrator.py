#!/usr/bin/env python3
"""
GraphifyStenoMD Workflow Orchestrator
Coordinates all workflows with a unified interface.

Usage:
    python3 workflows/orchestrator.py daily         # Daily workflow
    python3 workflows/orchestrator.py weekly        # Weekly workflow
    python3 workflows/orchestrator.py analytics   # Run analytics
"""

import sys
import json
from datetime import datetime
from collections import defaultdict
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

class WorkflowOrchestrator:
    def __init__(self):
        self.project_dir = PROJECT_DIR
        self.graph_file = GRAPH_FILE
        self.load_graph()
    
    def load_graph(self):
        """Load graph data."""
        if self.graph_file.exists():
            with open(self.graph_file) as f:
                self.graph = json.load(f)
        else:
            self.graph = {"nodes": [], "links": []}
    
    def stats(self):
        """Get graph statistics."""
        counts = defaultdict(int)
        
        for node in self.graph.get("nodes", []):
            source = node.get("source_file", "")
            if "politicians/" in source or "senators/" in source or "deputies/" in source:
                counts["politicians"] += 1
            elif "sessions/" in source:
                counts["sessions"] += 1
            elif "laws/" in source:
                counts["laws"] += 1
        
        return dict(counts)
    
    def daily_workflow(self):
        """Run daily workflow."""
        print(f"\n{'#' * 60}")
        print(f"# DAILY WORKFLOW - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#' * 60}")
        
        stats = self.stats()
        
        print("\n=== GRAPH STATE ===")
        print(f"Nodes: {len(self.graph.get('nodes', []))}")
        print(f"Edges: {len(self.graph.get('links', []))}")
        print(f"Politicians: {stats.get('politicians', 0)}")
        print(f"Sessions: {stats.get('sessions', 0)}")
        print(f"Laws: {stats.get('laws', 0)}")
        
        print("\n=== RECOMMENDED ACTIONS ===")
        
        # Gap analysis
        gaps = self.analyze_gaps()
        
        print("\n1. MISSING DATA GAPS")
        for gap_type, count in gaps.items():
            if count > 0:
                print(f"   - {gap_type}: {count}")
        
        print("\n2. PRIORITY ACTIONS")
        if gaps.get("missing_party", 0) > 0:
            print("   [HIGH] Enrich party data: stenom enrich --type party")
        if gaps.get("missing_speeches", 0) > 50:
            print("   [MEDIUM] Add speeches: stenom enrich --type speeches")
        if gaps.get("missing_committees", 0) > 50:
            print("   [MEDIUM] Add committees: stenom enrich --type committees")
        
        print("\n3. NEXT SCRAPING")
        print("   Run: python3 GraphifyStenoMD/workflows/daily_scrape.py")
        
        return gaps
    
    def analyze_gaps(self):
        """Analyze data gaps."""
        gaps = {
            "missing_party": 0,
            "missing_speeches": 0,
            "missing_committees": 0,
            "missing_sponsors": 0,
        }
        
        for node in self.graph.get("nodes", []):
            source = node.get("source_file", "")
            
            if "politicians/" in source or "senators/" in source:
                if not node.get("party"):
                    gaps["missing_party"] += 1
                if not node.get("speeches_count") or node.get("speeches_count", 0) == 0:
                    gaps["missing_speeches"] += 1
                if not node.get("committees"):
                    gaps["missing_committees"] += 1
            
            if "laws/" in source and not node.get("sponsors"):
                gaps["missing_sponsors"] += 1
        
        return gaps
    
    def weekly_workflow(self):
        """Run weekly workflow."""
        print(f"\n{'#' * 60}")
        print(f"# WEEKLY WORKFLOW - {datetime.now().strftime('%Y-%m-%d')}")
        print(f"{'#' * 60}")
        
        stats = self.stats()
        
        print("\n=== WEEKLY SUMMARY ===")
        print(f"Graph nodes: {len(self.graph.get('nodes', []))}")
        print(f"Graph edges: {len(self.graph.get('links', []))}")
        
        print("\n=== ENTITY COUNTS ===")
        print(f"Politicians: {stats.get('politicians', 0)}")
        print(f"Sessions: {stats.get('sessions', 0)}")
        print(f"Laws: {stats.get('laws', 0)}")
        
        print("\n=== GENERATE REPORTS ===")
        print("1. python3 GraphifyStenoMD/agents/analytics_agent.py --type coverage --save")
        print("2. python3 GraphifyStenoMD/agents/analytics_agent.py --type activity --save")
        print("3. python3 GraphifyStenoMD/agents/analytics_agent.py --type trends --save")
        
        print("\n=== VALIDATION ===")
        print("Run: python3 GraphifyStenoMD/workflows/health_check.py")
    
    def analytics_workflow(self):
        """Run analytics workflow."""
        print(f"\n{'#' * 60}")
        print(f"# ANALYTICS WORKFLOW")
        print(f"{'#' * 60}")
        
        print("\n=== RUNNING ANALYTICS ===")
        
        print("\n1. COVERAGE")
        # Already showed in daily
        
        print("\n2. ACTIVITY")
        activity = []
        for node in self.graph.get("nodes", []):
            source = node.get("source_file", "")
            if "politicians/" in source or "deputies/" in source or "senators/" in source:
                speeches = node.get("speeches_count", 0) or 0
                if speeches > 0:
                    activity.append((node.get("label"), speeches))
        
        activity.sort(key=lambda x: -x[1])
        
        print("Top 10 most active politicians:")
        for i, (name, count) in enumerate(activity[:10], 1):
            print(f"   {i}. {name}: {count} speeches")
        
        print("\n3. TRENDS")
        years = defaultdict(int)
        for node in self.graph.get("nodes", []):
            source = node.get("source_file", "")
            if "sessions/" in source:
                label = node.get("label", "")
                if "session-" in label:
                    year = label.split("-")[-1][:4]
                    if year.isdigit():
                        years[year] += 1
        
        print("Sessions by year:")
        for year in sorted(years.keys(), reverse=True)[:10]:
            print(f"   {year}: {years[year]} sessions")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Workflow orchestrator")
    parser.add_argument("workflow", choices=["daily", "weekly", "analytics"], help="Workflow to run")
    args = parser.parse_args()
    
    orchestrator = WorkflowOrchestrator()
    
    if args.workflow == "daily":
        orchestrator.daily_workflow()
    elif args.workflow == "weekly":
        orchestrator.weekly_workflow()
    elif args.workflow == "analytics":
        orchestrator.analytics_workflow()

if __name__ == "__main__":
    main()