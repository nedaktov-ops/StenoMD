#!/usr/bin/env python3
"""
query-brain.py - Query the StenoMD knowledge graph
Usage: python query-brain.py <politician|session|law> <query>
"""

import sys
import json
import os
from pathlib import Path

VAULT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/vault")
KG_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/knowledge_graph")

def load_entities():
    """Load entities from knowledge graph."""
    entities_file = KG_DIR / "entities.json"
    if entities_file.exists():
        with open(entities_file) as f:
            data = json.load(f)
            return {
                "persons": data.get("persons") or data.get("people", []),
                "sessions": data.get("sessions", []),
                "laws": data.get("laws", [])
            }
    return {"persons": [], "sessions": [], "laws": []}

def search_politician(name):
    """Search for politician by name."""
    entities = load_entities()
    results = []
    for e in entities.get("persons", []):
        if name.lower() in e.get("name", "").lower():
            results.append(e)
    return results

def search_session(date):
    """Search for session by date."""
    entities = load_entities()
    results = []
    for e in entities.get("sessions", []):
        if date in e.get("date", ""):
            results.append(e)
    return results

def search_law(law_num):
    """Search for law by number."""
    entities = load_entities()
    results = []
    for e in entities.get("laws", []):
        if law_num in str(e.get("law_number", "")):
            results.append(e)
    return results

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    query_type = sys.argv[1]
    query = sys.argv[2]
    
    if query_type == "politician":
        results = search_politician(query)
    elif query_type == "session":
        results = search_session(query)
    elif query_type == "law":
        results = search_law(query)
    else:
        print(f"Unknown query type: {query_type}")
        sys.exit(1)
    
    if results:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(f"No results found for {query_type}: {query}")

if __name__ == "__main__":
    main()