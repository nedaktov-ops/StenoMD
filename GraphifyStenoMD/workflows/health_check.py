#!/usr/bin/env python3
"""
GraphifyStenoMD Health Check Workflow
Validates data consistency across the project.

Usage:
    python3 workflows/health_check.py           # Full check
    python3 workflows/health_check.py --type links    # Check links only
    python3 workflows/health_check.py --type yaml     # Check YAML only
    python3 workflows/health_check.py --type graph     # Check graph only
    python3 workflows/health_check.py --fix            # Show fixes
"""

import json
import re
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
GRAPH_FILE = PROJECT_DIR / "Graphify" / "graphify-out" / "graph.json"
VAULT_DIR = PROJECT_DIR / "vault"

def check_links():
    """Validate wikilinks in vault."""
    issues = {"broken": [], "warnings": []}
    
    for md_file in VAULT_DIR.rglob("*.md"):
        content = md_file.read_text()
        links = re.findall(r'\[\[([^\]|]+)\]\]', content)
        for link in links:
            target = link.split("|")[0].strip()
            # Simple resolution check
            if not (VAULT_DIR / target).exists() and not (VAULT_DIR / f"{target}.md").exists():
                issues["broken"].append({
                    "file": str(md_file.relative_to(VAULT_DIR)),
                    "link": target
                })
    
    return issues

def check_yaml():
    """Validate YAML frontmatter."""
    issues = {"missing": [], "invalid": [], "incomplete": []}
    
    required = {
        "politicians": ["stable_id", "type", "party"],
        "sessions": ["date", "chamber"],
        "laws": ["law_number", "title"]
    }
    
    for category, fields in required.items():
        cat_dir = VAULT_DIR / category
        if not cat_dir.exists():
            continue
        
        for md_file in cat_dir.rglob("*.md"):
            content = md_file.read_text()
            if not content.startswith("---"):
                issues["missing"].append(str(md_file.relative_to(VAULT_DIR)))
            else:
                # Check for required fields
                for field in fields:
                    if field not in content:
                        issues["incomplete"].append({
                            "file": str(md_file.relative_to(VAULT_DIR)),
                            "field": field
                        })
    
    return issues

def check_graph():
    """Validate graph structure."""
    issues = {"orphaned": [], "self_loops": [], "missing_refs": []}
    
    if not GRAPH_FILE.exists():
        issues["missing_refs"].append("graph.json not found")
        return issues
    
    with open(GRAPH_FILE) as f:
        graph = json.load(f)
    
    node_ids = {n["id"] for n in graph.get("nodes", [])}
    
    for edge in graph.get("links", []):
        if edge.get("source") == edge.get("target"):
            issues["self_loops"].append(edge.get("source"))
        if edge.get("source") not in node_ids:
            issues["missing_refs"].append(f"Source: {edge.get('source')}")
        if edge.get("target") not in node_ids:
            issues["missing_refs"].append(f"Target: {edge.get('target')}")
    
    # Find orphaned nodes
    degrees = {}
    for edge in graph.get("links", []):
        for node_id in [edge.get("source"), edge.get("target")]:
            degrees[node_id] = degrees.get(node_id, 0) + 1
    
    for node in graph.get("nodes", []):
        if degrees.get(node["id"], 0) == 0:
            issues["orphaned"].append(node.get("label"))
    
    return issues

def run_check(check_type="all"):
    """Run health check."""
    print(f"\n{'=' * 50}")
    print("HEALTH CHECK")
    print(f"{'=' * 50}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    results = {}
    
    if check_type in ["all", "links"]:
        print("--- Checking Links ---")
        results["links"] = check_links()
        print(f"Broken links: {len(results['links']['broken'])}")
        print(f"Warnings: {len(results['links']['warnings'])}")
    
    if check_type in ["all", "yaml"]:
        print("\n--- Checking YAML ---")
        results["yaml"] = check_yaml()
        print(f"Missing frontmatter: {len(results['yaml']['missing'])}")
        print(f"Incomplete: {len(results['yaml']['incomplete'])}")
    
    if check_type in ["all", "graph"]:
        print("\n--- Checking Graph ---")
        results["graph"] = check_graph()
        print(f"Self-loops: {len(results['graph']['self_loops'])}")
        print(f"Orphaned nodes: {len(results['graph']['orphaned'])}")
        print(f"Missing refs: {len(results['graph']['missing_refs'])}")
    
    # Summary
    total = sum(len(v) for r in results.values() for v in r.values() if isinstance(v, list))
    print(f"\n{'=' * 50}")
    print(f"TOTAL ISSUES: {total}")
    print("=" * 50)
    
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["all", "links", "yaml", "graph"], default="all", help="Check type")
    parser.add_argument("--fix", action="store_true", help="Show fixes")
    args = parser.parse_args()
    
    run_check(args.type)

if __name__ == "__main__":
    main()