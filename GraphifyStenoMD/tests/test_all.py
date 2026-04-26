#!/usr/bin/env python3
"""
GraphifyStenoMD Test Suite
Tests for GraphifyStenoMD components.

Usage:
    python3 tests/test_all.py           # Run all tests
    python3 tests/test_agents.py        # Test agents
    python3 tests/test_workflows.py   # Test workflows
"""

import sys
import json
from pathlib import Path

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
GRAPH_FILE = PROJECT_DIR / "Graphify" / "graphify-out" / "graph.json"

def test_graph_exists():
    """Test that graph exists."""
    if GRAPH_FILE.exists():
        print("✓ Graph exists")
        return True
    else:
        print("✗ Graph not found")
        return False

def test_graph_loads():
    """Test that graph loads."""
    if not GRAPH_FILE.exists():
        print("✗ Cannot test - graph not found")
        return False
    
    try:
        with open(GRAPH_FILE) as f:
            graph = json.load(f)
        print("✓ Graph loads correctly")
        return True
    except Exception as e:
        print(f"✗ Graph load failed: {e}")
        return False

def test_graph_structure():
    """Test graph has required structure."""
    if not GRAPH_FILE.exists():
        return False
    
    with open(GRAPH_FILE) as f:
        graph = json.load(f)
    
    required = ["nodes", "links"]
    for field in required:
        if field not in graph:
            print(f"✗ Missing field: {field}")
            return False
    
    print(f"✓ Graph structure valid")
    print(f"  Nodes: {len(graph.get('nodes', []))}")
    print(f"  Links: {len(graph.get('links', []))}")
    return True

def test_nodes():
    """Test node structure."""
    if not GRAPH_FILE.exists():
        return False
    
    with open(GRAPH_FILE) as f:
        graph = json.load(f)
    
    valid = 0
    invalid = 0
    
    for node in graph.get("nodes", [])[:10]:
        if "id" in node and "label" in node:
            valid += 1
        else:
            invalid += 1
    
    if invalid == 0:
        print(f"✓ Node structure valid")
    else:
        print(f"✗ {invalid} invalid nodes")
    
    return invalid == 0

def test_edges():
    """Test edge structure."""
    if not GRAPH_FILE.exists():
        return False
    
    with open(GRAPH_FILE) as f:
        graph = json.load(f)
    
    valid = 0
    invalid = 0
    
    for edge in graph.get("links", [])[:10]:
        if "source" in edge and "target" in edge:
            valid += 1
        else:
            invalid += 1
    
    if invalid == 0:
        print(f"✓ Edge structure valid")
    else:
        print(f"✗ {invalid} invalid edges")
    
    return invalid == 0

def test_all():
    """Run all tests."""
    print("=" * 50)
    print("GraphifyStenoMD Test Suite")
    print("=" * 50)
    print("")
    
    results = []
    
    print("1. Graph Exists")
    results.append(test_graph_exists())
    
    print("\n2. Graph Loads")
    results.append(test_graph_loads())
    
    print("\n3. Graph Structure")
    results.append(test_graph_structure())
    
    print("\n4. Node Structure")
    results.append(test_nodes())
    
    print("\n5. Edge Structure")
    results.append(test_edges())
    
    print("")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 50)
    
    return passed == total

def test_agents():
    """Test agents can load."""
    print("Testing agents...")
    
    # Test scraper agent
    agent_file = PROJECT_DIR / "GraphifyStenoMD" / "agents" / "scraper_agent.py"
    if agent_file.exists():
        print(f"✓ scraper_agent.py exists")
    else:
        print(f"✗ scraper_agent.py not found")
    
    # Test enrichment agent
    agent_file = PROJECT_DIR / "GraphifyStenoMD" / "agents" / "enrichment_agent.py"
    if agent_file.exists():
        print(f"✓ enrichment_agent.py exists")
    else:
        print(f"✗ enrichment_agent.py not found")
    
    # Test validator agent
    agent_file = PROJECT_DIR / "GraphifyStenoMD" / "agents" / "validator_agent.py"
    if agent_file.exists():
        print(f"✓ validator_agent.py exists")
    else:
        print(f"✗ validator_agent.py not found")

def test_workflows():
    """Test workflows exist."""
    print("Testing workflows...")
    
    workflows = [
        "daily_scrape.py",
        "missing_data.py",
        "health_check.py",
        "orchestrator.py",
    ]
    
    for wf in workflows:
        wf_file = PROJECT_DIR / "GraphifyStenoMD" / "workflows" / wf
        if wf_file.exists():
            print(f"✓ {wf} exists")
        else:
            print(f"✗ {wf} not found")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("tests", nargs="?", default="all", help="Test to run")
    args = parser.parse_args()
    
    if args.tests == "agents":
        test_agents()
    elif args.tests == "workflows":
        test_workflows()
    else:
        test_all()

if __name__ == "__main__":
    main()