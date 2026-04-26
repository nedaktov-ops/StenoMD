#!/usr/bin/env python3
"""
GraphifyStenoMD Integration Test
Tests integration with existing StenoMD systems.

Usage:
    python3 tests/test_integration.py
"""

import sys
import json
from pathlib import Path

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")

def test_vault_exists():
    """Test vault directory exists."""
    vault = PROJECT_DIR / "vault"
    if vault.exists():
        print("✓ Vault exists")
        return True
    else:
        print("✗ Vault not found")
        return False

def test_scripts_exist():
    """Test scripts directory exists."""
    scripts = PROJECT_DIR / "scripts"
    if scripts.exists():
        print("✓ Scripts directory exists")
        return True
    else:
        print("✗ Scripts not found")
        return False

def test_graphify_out_exists():
    """Test Graphify output exists."""
    out = PROJECT_DIR / "Graphify" / "graphify-out"
    if out.exists():
        print("✓ Graphify output exists")
        return True
    else:
        print("✗ Graphify output not found")
        return False

def test_graph_statemd_exists():
    """Test GraphifyStenoMD directory exists."""
    gsmd = PROJECT_DIR / "GraphifyStenoMD"
    if gsmd.exists():
        print("✓ GraphifyStenoMD exists")
        return True
    else:
        print("✗ GraphifyStenoMD not found")
        return False

def test_knowledge_graph_exists():
    """Test knowledge_graph directory exists."""
    kg = PROJECT_DIR / "knowledge_graph"
    if kg.exists():
        print("✓ knowledge_graph exists")
        return True
    else:
        print("✗ knowledge_graph not found")
        return False

def main():
    print("=" * 50)
    print("Integration Test Suite")
    print("=" * 50)
    print("")
    
    results = []
    
    print("1. Vault Directory")
    results.append(test_vault_exists())
    
    print("\n2. Scripts Directory")
    results.append(test_scripts_exist())
    
    print("\n3. Graphify Output")  
    results.append(test_graphify_out_exists())
    
    print("\n4. GraphifyStenoMD")
    results.append(test_graph_statemd_exists())
    
    print("\n5. knowledge_graph")
    results.append(test_knowledge_graph_exists())
    
    print("")
    print("=" * 50)
    print(f"RESULTS: {sum(results)}/{len(results)} passed")
    print("=" * 50)

if __name__ == "__main__":
    main()