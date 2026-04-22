#!/usr/bin/env python3
"""StenoMD Analytics - Generate reports and analysis"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

KG_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/knowledge_graph")
ENTITIES_FILE = KG_DIR / "entities.json"

def load_entities():
    if ENTITIES_FILE.exists():
        with open(ENTITIES_FILE) as f:
            return json.load(f)
    return {"persons": [], "sessions": [], "laws": []}

def top_politicians(entities, limit=10):
    """Get most active politicians."""
    counter = Counter()
    for p in entities.get("persons", []):
        counter[p.get("name", "")] += 1
    
    return counter.most_common(limit)

def top_laws(entities, limit=10):
    """Get most referenced laws."""
    counter = Counter()
    for l in entities.get("laws", []):
        counter[l.get("law_number", "")] += 1
    
    return counter.most_common(limit)

def sessions_by_month(entities):
    """Group sessions by month."""
    by_month = Counter()
    for s in entities.get("sessions", []):
        date = s.get("date", "")
        if date:
            month = date[:7]
            by_month[month] += 1
    
    return sorted(by_month.items(), reverse=True)

def generate_report():
    """Generate analytics report."""
    entities = load_entities()
    
    print("="* 50)
    print("StenoMD Analytics Report")
    print(f"Generated: {datetime.now().isoformat()}")
    print("="* 50)
    
    print(f"\nTotal Politicians: {len(entities.get('persons', []))}")
    print(f"Total Sessions: {len(entities.get('sessions', []))}")
    print(f"Total Laws: {len(entities.get('laws', []))}")
    
    print("\n--- Top 10 Politicians ---")
    for name, count in top_politicians(entities, 10):
        print(f"  {name}: {count}")
    
    print("\n--- Top 10 Laws ---")
    for law, count in top_laws(entities, 10):
        print(f"  {law}: {count}")
    
    print("\n--- Sessions by Month ---")
    for month, count in sessions_by_month(entities)[:12]:
        print(f"  {month}: {count}")

def export_csv():
    """Export entities to CSV."""
    entities = load_entities()
    
    print("\n--- Politicians CSV ---")
    print("name,type,source")
    for p in entities.get("persons", []):
        print(f'"{p.get("name", "")}","{p.get("type", "")}","{p.get("source", "")}"')
    
    print("\n--- Laws CSV ---")
    print("law_number,type,source")
    for l in entities.get("laws", []):
        print(f'"{l.get("law_number", "")}","{l.get("type", "")}","{l.get("source", "")}"')

def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--csv":
        export_csv()
    else:
        generate_report()

if __name__ == "__main__":
    main()