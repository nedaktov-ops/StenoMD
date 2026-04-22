#!/usr/bin/env python3
"""Validate knowledge graph consistency"""

import json
import sys
from pathlib import Path

KG_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/knowledge_graph")
ENTITIES_FILE = KG_DIR / "entities.json"

def load_entities():
    """Load entities from knowledge graph."""
    if ENTITIES_FILE.exists():
        with open(ENTITIES_FILE) as f:
            return json.load(f)
    return {"persons": [], "sessions": [], "laws": []}

def validate_persons(persons):
    """Validate person entities."""
    errors = []
    seen_names = set()
    
    for i, p in enumerate(persons):
        name = p.get("name", "")
        if not name:
            errors.append(f"Person {i}: missing name")
        elif name in seen_names:
            errors.append(f"Person {i}: duplicate name '{name}'")
        else:
            seen_names.add(name)
    
    return errors

def validate_sessions(sessions):
    """Validate session entities."""
    errors = []
    seen_dates = set()
    
    for i, s in enumerate(sessions):
        date = s.get("date", "")
        if not date:
            errors.append(f"Session {i}: missing date")
        elif date in seen_dates:
            errors.append(f"Session {i}: duplicate date '{date}'")
        else:
            seen_dates.add(date)
    
    return errors

def validate_laws(laws):
    """Validate law entities."""
    errors = []
    seen = set()
    
    for i, l in enumerate(laws):
        num = l.get("law_number", "")
        if not num:
            errors.append(f"Law {i}: missing law_number")
        elif num in seen:
            errors.append(f"Law {i}: duplicate law_number '{num}'")
        else:
            seen.add(num)
    
    return errors

def main():
    entities = load_entities()
    
    all_errors = []
    
    person_errors = validate_persons(entities.get("persons", []))
    all_errors.extend(person_errors)
    
    session_errors = validate_sessions(entities.get("sessions", []))
    all_errors.extend(session_errors)
    
    law_errors = validate_laws(entities.get("laws", []))
    all_errors.extend(law_errors)
    
    if all_errors:
        print("Validation FAILED:")
        for e in all_errors[:20]:
            print(f"  - {e}")
        sys.exit(1)
    
    print("Validation PASSED:")
    print(f"  - Persons: {len(entities.get('persons', []))}")
    print(f"  - Sessions: {len(entities.get('sessions', []))}")
    print(f"  - Laws: {len(entities.get('laws', []))}")
    sys.exit(0)

if __name__ == "__main__":
    main()