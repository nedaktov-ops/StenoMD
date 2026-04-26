#!/usr/bin/env python3
"""
GraphifyStenoMD Daily Scrape Workflow
Shows daily scraping recommendations based on graph gaps.

Usage:
    python3 workflows/daily_scrape.py           # Show recommendations
    python3 workflows/daily_scrape.py --run   # Actually run (requires confirmation)
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
GRAPH_FILE = PROJECT_DIR / "Graphify" / "graphify-out" / "graph.json"

def analyze_graph():
    """Analyze current graph state."""
    if not GRAPH_FILE.exists():
        print("No graph found. Run /graphify first.")
        return None
    
    with open(GRAPH_FILE) as f:
        graph = json.load(f)
    
    stats = {
        "total_nodes": len(graph.get("nodes", [])),
        "total_edges": len(graph.get("links", [])),
        "politicians": 0,
        "sessions": 0,
        "laws": 0,
    }
    
    for node in graph.get("nodes", []):
        source = node.get("source_file", "")
        if "politicians/" in source:
            stats["politicians"] += 1
        elif "sessions/" in source:
            stats["sessions"] += 1
        elif "laws/" in source:
            stats["laws"] += 1
    
    return stats

def get_gap_recommendations(stats):
    """Generate gap-based recommendations."""
    recommendations = []
    
    # Based on stats, recommend actions
    if stats["politicians"] < 100:
        recommendations.append({
            "action": "Scrape more politicians",
            "priority": "HIGH",
            "reason": f"Only {stats['politicians']} in graph"
        })
    
    if stats["sessions"] < 100:
        recommendations.append({
            "action": "Scrape more sessions", 
            "priority": "HIGH",
            "reason": f"Only {stats['sessions']} in graph"
        })
    
    if stats["laws"] < 100:
        recommendations.append({
            "action": "Enrich law data",
            "priority": "MEDIUM",
            "reason": f"Only {stats['laws']} laws tracked"
        })
    
    # Default recommendations
    recommendations.extend([
        {
            "action": "Run enrichment pipeline",
            "priority": "MEDIUM",
            "reason": "Fill missing data fields"
        },
        {
            "action": "Validate vault links",
            "priority": "LOW",
            "reason": "Ensure data consistency"
        }
    ])
    
    return recommendations

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Daily scrape workflow")
    parser.add_argument("--run", action="store_true", help="Actually run (not implemented)")
    
    args = parser.parse_args()
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Daily Scrape Analysis")
    print("=" * 50)
    
    stats = analyze_graph()
    
    if stats:
        print(f"\nGraph State:")
        print(f"  Total nodes: {stats['total_nodes']}")
        print(f"  Total edges: {stats['total_edges']}")
        print(f"  Politicians: {stats['politicians']}")
        print(f"  Sessions: {stats['sessions']}")
        print(f"  Laws: {stats['laws']}")
        
        print(f"\nRecommendations:")
        recs = get_gap_recommendations(stats)
        for i, rec in enumerate(recs, 1):
            print(f"  {i}. [{rec['priority']}] {rec['action']}")
            print(f"     Reason: {rec['reason']}")
        
        print(f"\n(Note: --run not implemented yet)")
    
    return stats

if __name__ == "__main__":
    main()