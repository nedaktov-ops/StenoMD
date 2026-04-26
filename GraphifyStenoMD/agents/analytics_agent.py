#!/usr/bin/env python3
"""
GraphifyStenoMD Analytics Agent
Generates analytics and reports from graph data.

Usage:
    python3 agents/analytics_agent.py --type coverage
    python3 agents/analytics_agent.py --type activity
    python3 agents/analytics_agent.py --report weekly
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
GRAPH_FILE = PROJECT_DIR / "Graphify" / "graphify-out" / "graph.json"
OUTPUT_DIR = PROJECT_DIR / "GraphifyStenoMD" / "reports"

class AnalyticsAgent:
    def __init__(self):
        self.graph_data = None
        self.load_graph()
    
    def load_graph(self):
        if GRAPH_FILE.exists():
            with open(GRAPH_FILE) as f:
                self.graph_data = json.load(f)
            print(f"Loaded graph: {len(self.graph_data.get('nodes', []))} nodes")
        else:
            print("No graph found")
            self.graph_data = {"nodes": [], "links": []}
    
    def coverage_report(self):
        """Generate coverage report."""
        report = []
        report.append("# Coverage Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Count by type
        types = Counter()
        completions = {"full": 0, "partial": 0, "missing": 0}
        
        for node in self.graph_data.get("nodes", []):
            source = node.get("source_file", "")
            if "politicians/" in source or "senators/" in source or "deputies/" in source:
                types["politicians"] += 1
            elif "sessions/" in source:
                types["sessions"] += 1
            elif "laws/" in source:
                types["laws"] += 1
            
            # Check completeness
            fields = [node.get("party"), node.get("speeches_count"), node.get("committees")]
            if all(fields):
                completions["full"] += 1
            elif any(fields):
                completions["partial"] += 1
            else:
                completions["missing"] += 1
        
        report.append("## Summary")
        report.append("")
        report.append(f"- Total nodes: {len(self.graph_data.get('nodes', []))}")
        report.append(f"- Politicians: {types.get('politicians', 0)}")
        report.append(f"- Sessions: {types.get('sessions', 0)}")
        report.append(f"- Laws: {types.get('laws', 0)}")
        report.append("")
        
        report.append("## Completeness")
        report.append(f"- Complete: {completions['full']}")
        report.append(f"- Partial: {completions['partial']}")
        report.append(f"- Missing: {completions['missing']}")
        
        return "\n".join(report)
    
    def activity_report(self):
        """Generate activity leaderboard."""
        report = []
        report.append("# Activity Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Calculate activity scores
        activity = []
        
        for node in self.graph_data.get("nodes", []):
            source = node.get("source_file", "")
            if "politicians/" in source or "senators/" in source or "deputies/" in source:
                label = node.get("label", "")
                speeches = node.get("speeches_count", 0) or 0
                if speeches > 0:
                    activity.append((label, speeches))
        
        # Sort by activity
        activity.sort(key=lambda x: -x[1])
        
        report.append("## Top 20 Most Active Politicians")
        report.append("")
        report.append("| Rank | Name | Speeches |")
        report.append("|------|------|---------|")
        
        for i, (name, count) in enumerate(activity[:20], 1):
            report.append(f"| {i} | {name} | {count} |")
        
        return "\n".join(report)
    
    def trends_report(self):
        """Generate trends analysis."""
        report = []
        report.append("# Trends Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Group sessions by year
        years = Counter()
        
        for node in self.graph_data.get("nodes", []):
            source = node.get("source_file", "")
            if "sessions/" in source:
                label = node.get("label", "")
                # Extract year from label like "session-20241221"
                if "session-" in label:
                    year = label.split("-")[-1][:4]
                    if year.isdigit():
                        years[year] += 1
        
        report.append("## Sessions by Year")
        report.append("")
        
        for year in sorted(years.keys(), reverse=True):
            report.append(f"- {year}: {years[year]} sessions")
        
        return "\n".join(report)
    
    def run(self, report_type="coverage"):
        """Run report generation."""
        if report_type == "coverage":
            return self.coverage_report()
        elif report_type == "activity":
            return self.activity_report()
        elif report_type == "trends":
            return self.trends_report()
        else:
            return f"Unknown report type: {report_type}"
    
    def save_report(self, report_type="coverage"):
        """Save report to file."""
        content = self.run(report_type)
        
        OUTPUT_DIR.mkdir(exist_ok=True)
        
        filename = f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = OUTPUT_DIR / filename
        
        filepath.write_text(content)
        print(f"Saved: {filepath}")
        
        return str(filepath)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Analytics agent")
    parser.add_argument("--type", choices=["coverage", "activity", "trends"], default="coverage", help="Report type")
    parser.add_argument("--save", action="store_true", help="Save to file")
    
    args = parser.parse_args()
    
    agent = AnalyticsAgent()
    
    if args.save:
        agent.save_report(args.type)
    else:
        print(agent.run(args.type))


if __name__ == "__main__":
    main()