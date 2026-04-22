#!/usr/bin/env python3
"""Update knowledge graph from real stenogram HTML files"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

DATA_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/data")
KG_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/knowledge_graph")
ENTITIES_FILE = KG_DIR / "entities.json"

def load_existing():
    if ENTITIES_FILE.exists():
        with open(ENTITIES_FILE) as f:
            data = json.load(f)
            return {
                "persons": data.get("persons") or data.get("people", []),
                "sessions": data.get("sessions", []),
                "laws": data.get("laws", [])
            }
    return {"persons": [], "sessions": [], "laws": []}

def save(data):
    with open(ENTITIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def extract_from_stenogram(filepath):
    """Extract MPs, laws, and session info from HTML stenogram."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ')
    
    # Extract MPs (Domnul/Doamna patterns)
    mps = re.findall(r'(?:Domnul|Doamna)\s+([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț\-]+)+)', text)
    
    # Extract laws
    laws = re.findall(r'(?:legea|Legea|Proiectul de Lege)\s+(?:nr\.?\s*)?(\d+/\d{4})', text, re.I)
    
    # Extract session date/title from title tag
    try:
        title = soup.title.string if soup.title else filepath.stem
    except AttributeError:
        title = filepath.stem
    
    return mps, laws, title

def main():
    print("=== Updating Knowledge Graph ===")
    
    entities = load_existing()
    existing_mps = {p['name'] for p in entities['persons']}
    existing_laws = {l['law_number'] for l in entities['laws']}
    
    new_mps = []
    new_laws = []
    sessions = []
    
    for filepath in DATA_DIR.glob("stenogram_*.html"):
        print(f"Processing: {filepath.name}")
        mps, laws, title = extract_from_stenogram(filepath)
        
        # Add session
        sessions.append({
            "title": title,
            "source": filepath.name,
            "url": f"https://www.cdep.ro/pls/steno/{filepath.name.replace('.html', '')}"
        })
        
        # Add new MPs
        for mp in mps:
            if mp not in existing_mps:
                new_mps.append({
                    "name": mp.strip(),
                    "type": "politician",
                    "source": filepath.name
                })
                existing_mps.add(mp)
        
        # Add new laws
        for law in laws:
            if law not in existing_laws:
                new_laws.append({
                    "law_number": law,
                    "type": "law",
                    "source": filepath.name
                })
                existing_laws.add(law)
    
    entities['persons'].extend(new_mps)
    entities['laws'].extend(new_laws)
    entities['sessions'] = sessions
    
    save(entities)
    
    print(f"\\n=== Results ===")
    print(f"New MPs: {len(new_mps)}")
    print(f"New Laws: {len(new_laws)}")
    print(f"Total MPs: {len(entities['persons'])}")
    print(f"Total Laws: {len(entities['laws'])}")
    print(f"Total Sessions: {len(entities['sessions'])}")

if __name__ == "__main__":
    main()