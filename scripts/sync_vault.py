#!/usr/bin/env python3
"""Sync knowledge graph to Obsidian vault"""

import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import get_config
    config = get_config()
    KG_DIR = config.KG_DIR
    VAULT_DIR = config.VAULT_DIR
    ENTITIES_FILE = config.ENTITIES_FILE
except ImportError:
    KG_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/knowledge_graph")
    VAULT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/vault")
    ENTITIES_FILE = KG_DIR / "entities.json"

def load_entities():
    if ENTITIES_FILE.exists():
        with open(ENTITIES_FILE) as f:
            data = json.load(f)
            return {
                "persons": data.get("persons") or data.get("people", []),
                "sessions": data.get("sessions", []),
                "laws": data.get("laws", [])
            }
    return {"persons": [], "sessions": [], "laws": []}

def sync_politicians(entities):
    """Sync politicians to vault."""
    politicians_dir = VAULT_DIR / "politicians"
    politicians_dir.mkdir(parents=True, exist_ok=True)
    
    current_legislature = str(datetime.now().year + 1)[:4] + "-" + str(datetime.now().year + 5)[:4]
    
    index_content = "# Politicians Index\n\n> Romanian Parliament Members\n\n## By Legislature\n\n"
    
    for p in entities.get("persons", [])[:100]:
        name = p.get("name", "Unknown")
        safe_name = name.replace(" ", "-").replace(",", "")
        
        note_path = politicians_dir / f"{safe_name}.md"
        
        if not note_path.exists():
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(f"""---
tags: [politician]
type: person
---

# {name}

## Activity

- Source: {p.get('source', 'N/A')}

## Tags

#politician
""")
    
    index_content += f"- [[Current]] - {current_legislature}\n"
    
    with open(politicians_dir / "Index.md", 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"Synced {len(entities.get('persons', []))} politicians")

def sync_sessions(entities):
    """Sync sessions to vault."""
    sessions_dir = VAULT_DIR / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    
    index_content = "# Sessions Index\n\n> Stenogram Sessions\n\n## Recent\n\n"
    
    for s in sorted(entities.get("sessions", []), key=lambda x: x.get("date", ""), reverse=True)[:20]:
        date = s.get("date", "Unknown")
        safe_date = date.replace("-", "")
        
        note_path = sessions_dir / f"{safe_date}.md"
        
        if not note_path.exists():
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(f"""---
tags: [session]
date: {date}
---

# Session {date}

## Details

- Source: {s.get('source', 'N/A')}

## Tags

#session
""")
        
        index_content += f"- [[{date}]] - {date}\n"
    
    with open(sessions_dir / "Index.md", 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"Synced {len(entities.get('sessions', []))} sessions")

def sync_laws(entities):
    """Sync laws to vault."""
    laws_dir = VAULT_DIR / "laws"
    laws_dir.mkdir(parents=True, exist_ok=True)
    
    index_content = "# Laws Index\n\n> Legislation\n\n"
    
    for l in entities.get("laws", [])[:100]:
        law_num = l.get("law_number", "Unknown")
        safe_num = law_num.replace("/", "-")
        
        note_path = laws_dir / f"{safe_num}.md"
        
        if not note_path.exists():
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(f"""---
tags: [law]
law_number: {law_num}
---

# Law {law_num}

## Details

- Source: {l.get('source', 'N/A')}

## Tags

#law
""")
        
        index_content += f"- [[{law_num}]] - Law {law_num}\n"
    
    with open(laws_dir / "Index.md", 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"Synced {len(entities.get('laws', []))} laws")

def main():
    entities = load_entities()
    
    print("Syncing knowledge graph to vault...")
    
    sync_politicians(entities)
    sync_sessions(entities)
    sync_laws(entities)
    
    print("Sync complete.")

if __name__ == "__main__":
    main()