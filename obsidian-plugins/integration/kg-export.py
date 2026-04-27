#!/usr/bin/env python3
"""
KG Export - Export knowledge graph for AI consumption
"""

import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
KG_FILE = PROJECT_ROOT / "knowledge_graph" / "entities.json"
OUTPUT_FILE = PROJECT_ROOT / "vault" / "ai-memory" / "kg-export.json"


def export_simplified():
    """Export simplified KG for AI queries."""
    print("Exporting knowledge graph...")
    
    if not KG_FILE.exists():
        print("No KG found")
        return False
    
    with open(KG_FILE) as f:
        kg = json.load(f)
    
    simplified = {
        "last_updated": datetime.now().isoformat(),
        "persons": [],
        "sessions": [],
        "laws": []
    }
    
    # Simplify persons
    for p in kg.get("persons", [])[:100]:
        simplified["persons"].append({
            "name": p.get("name"),
            "chamber": p.get("chamber"),
            "party": p.get("party"),
            "source": p.get("source")
        })
    
    # Simplify sessions  
    for s in kg.get("sessions", [])[:100]:
        simplified["sessions"].append({
            "id": s.get("id"),
            "date": s.get("date"),
            "chamber": s.get("chamber"),
            "participants_count": len(s.get("participants", []))
        })
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(simplified, f, indent=2)
    
    print(f"Exported: {len(simplified['persons'])} persons, {len(simplified['sessions'])} sessions")
    return True


if __name__ == "__main__":
    export_simplified()