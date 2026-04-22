#!/usr/bin/env python3
"""Update knowledge graph from real stenogram HTML files"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.parent
DATA_DIR = SCRIPT_DIR / "data"
KG_DIR = SCRIPT_DIR / "knowledge_graph"
ENTITIES_FILE = KG_DIR / "entities.json"

# Romanian month mapping
MONTHS_RO = {
    'ianuarie': 1, 'februarie': 2, 'martie': 3, 'aprilie': 4, 'mai': 5, 'iunie': 6,
    'iulie': 7, 'august': 8, 'septembrie': 9, 'octombrie': 10, 'noiembrie': 11, 'decembrie': 12
}

def extract_date_from_title(title):
    """Extract date from session title like 'Sedinta Camerei Deputatilor din 5 noiembrie 2024'."""
    try:
        # Match pattern: "din DD month YYYY"
        match = re.search(r'din\s+(\d+)\s+(\w+)\s+(\d{4})', title, re.I)
        if match:
            day = int(match.group(1))
            month_str = match.group(2).lower()
            year = int(match.group(3))
            
            if month_str in MONTHS_RO:
                month = MONTHS_RO[month_str]
                return f"{year:04d}-{month:02d}-{day:02d}"
    except:
        pass
    return None

def load_existing():
    if ENTITIES_FILE.exists():
        with open(ENTITIES_FILE) as f:
            data = json.load(f)
            sessions = data.get("sessions", [])
            laws = data.get("laws", [])
            
            # Normalize law records: rename "number" to "law_number"
            for law in laws:
                if "number" in law and "law_number" not in law:
                    law["law_number"] = law.pop("number")
            
            return {
                "persons": data.get("persons") or data.get("people", []),
                "sessions": sessions,
                "laws": laws
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
        
        # Extract date from title
        session_date = extract_date_from_title(title)
        if not session_date:
            session_date = datetime.now().strftime("%Y-%m-%d")
        
        # Add session
        sessions.append({
            "title": title,
            "date": session_date,
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
    
    print(f"\n=== Results ===")
    print(f"New MPs: {len(new_mps)}")
    print(f"New Laws: {len(new_laws)}")
    print(f"Total MPs: {len(entities['persons'])}")
    print(f"Total Laws: {len(entities['laws'])}")
    print(f"Total Sessions: {len(entities['sessions'])}")

if __name__ == "__main__":
    main()