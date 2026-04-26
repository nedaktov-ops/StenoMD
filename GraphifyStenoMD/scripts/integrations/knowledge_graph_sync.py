#!/usr/bin/env python3
"""
GraphifyStenoMD Integration: Knowledge Graph Sync
Bridges Graphify output with existing knowledge_graph/.

Usage:
    python3 scripts/integrations/knowledge_graph_sync.py --direction vault_to_kg
    python3 scripts/integrations/knowledge_graph_sync.py --direction kg_to_vault
    python3 scripts/integrations/knowledge_graph_sync.py --compare
"""

import json
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
GRAPHIFY_FILE = PROJECT_DIR / "Graphify" / "graphify-out" / "graph.json"
KG_FILE = PROJECT_DIR / "knowledge_graph" / "entities.json"

class KnowledgeGraphSync:
    def __init__(self):
        self.graphify_data = None
        self.kg_data = None
        self.load_data()
    
    def load_data(self):
        """Load both data sources."""
        if GRAPHIFY_FILE.exists():
            with open(GRAPHIFY_FILE) as f:
                self.graphify_data = json.load(f)
            print(f"Loaded Graphify: {len(self.graphify_data.get('nodes', []))} nodes")
        
        if KG_FILE.exists():
            with open(KG_FILE) as f:
                self.kg_data = json.load(f)
            print(f"Loaded knowledge_graph: {len(self.kg_data.get('persons', []))} persons")
        else:
            print("knowledge_graph/entities.json not found")
            self.kg_data = {"persons": [], "sessions": [], "laws": []}
    
    def get_graphify_entities(self):
        """Extract entities from Graphify."""
        entities = {"persons": [], "sessions": [], "laws": []}
        
        for node in self.graphify_data.get("nodes", []):
            source = node.get("source_file", "")
            
            if "politicians/" in source or "deputies/" in source or "senators/" in source:
                entities["persons"].append({
                    "name": node.get("label"),
                    "type": node.get("type"),
                    "party": node.get("party"),
                })
            elif "sessions/" in source:
                entities["sessions"].append({
                    "label": node.get("label"),
                    "date": node.get("date"),
                })
            elif "laws/" in source:
                entities["laws"].append({
                    "number": node.get("law_number"),
                    "title": node.get("title"),
                })
        
        return entities
    
    def compare(self):
        """Compare both sources."""
        print(f"\n{'=' * 50}")
        print("COMPARE KNOWLEDGE GRAPH vs GRAPHIFY")
        print(f"{'=' * 50}")
        
        graphify = self.get_graphify_entities()
        kg = self.kg_data
        
        print(f"\nGraphify:")
        print(f"  Persons: {len(graphify['persons'])}")
        print(f"  Sessions: {len(graphify['sessions'])}")
        print(f"  Laws: {len(graphify['laws'])}")
        
        print(f"\nknowledge_graph:")
        print(f"  Persons: {len(kg.get('persons', []))}")
        print(f"  Sessions: {len(kg.get('sessions', []))}")
        print(f"  Laws: {len(kg.get('laws', []))}")
        
        print(f"\nDifferences:")
        print(f"  Persons: {len(graphify['persons']) - len(kg.get('persons', []))}")
    
    def sync_vault_to_kg(self):
        """Sync from Graphify to knowledge_graph."""
        print("NOTE: This is a read-only comparison.")
        print("To sync, use separate scripts in scripts/ directory.")
        
        self.compare()
    
    def sync_kg_to_vault(self):
        """Sync from knowledge_graph to vault."""
        print("NOTE: Not implemented in OptionB mode.")
        
        self.compare()

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--direction", choices=["vault_to_kg", "kg_to_vault", "compare"], default="compare")
    args = parser.parse_args()
    
    sync = KnowledgeGraphSync()
    
    if args.direction == "compare":
        sync.compare()
    elif args.direction == "vault_to_kg":
        sync.sync_vault_to_kg()
    elif args.direction == "kg_to_vault":
        sync.sync_kg_to_vault()

if __name__ == "__main__":
    main()