#!/usr/bin/env python3
"""Import speeches from Open Parliament RO data to StenoMD vault."""
import json
import re
import requests
from pathlib import Path
from datetime import datetime


MP_PATTERN = re.compile(
    r'(?:Domnul|Doamna)\s+([A-ZĂÂÎȘȚ][a-zăâîșț\-]+(?:\s+[A-ZĂÂÎȘȚ]\.?)?(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)',
    re.IGNORECASE
)

LAW_PATTERN = re.compile(
    r'(?:Legea|Proiectul de Lege)\s+(?:nr\.)?\s*(\d+/\d{4})',
    re.IGNORECASE
)


def main():
    # Paths
    base = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/data/parlamint/open-parliament-ro/data/2024")
    speeches_dir = base / "speeches/deputies"
    vault_base = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/vault/sessions/deputies")
    
    # Load deputy names
    deputies = {}
    with open(base / "deputies.json") as f:
        data = json.load(f)
        for dep in data.get('data', []):
            idm = str(dep.get('idm', ''))
            name = dep.get('name', '')
            if idm and name:
                deputies[idm] = name
    
    print(f"Loaded {len(deputies)} deputies")
    
    # Load speeches
    all_speeches = []
    for file in speeches_dir.glob("*.json"):
        mp_id = file.stem
        with open(file) as f:
            data = json.load(f)
            for speech in data.get("data", []):
                for transcript in speech.get("transcripts", []):
                    all_speeches.append({
                        'mp_id': mp_id,
                        'date': speech.get("date", "")[:10],
                        'title': speech.get("title", ""),
                        'ids': speech.get("ids", ""),
                        'url': transcript.get("fullTextUrl", "")
                    })
    
    print(f"Loaded {len(all_speeches)} speeches")
    
    # Process limited speeches
    saved = 0
    for i, speech in enumerate(all_speeches[:20]):  # Limit for testing
        mp_name = deputies.get(speech['mp_id'], f"MP-{speech['mp_id']}")
        print(f"Processing {i+1}/20: {speech['date']} - {mp_name}")
        
        # Fetch content
        try:
            r = requests.get(speech['url'], timeout=30, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                html = r.text
                
                # Extract MPs
                mps = set()
                for match in MP_PATTERN.finditer(html):
                    name = match.group(1).strip()
                    if len(name) > 5 and len(name) < 50:
                        mps.add(name)
                
                # Extract laws
                laws = set()
                for match in LAW_PATTERN.finditer(html):
                    laws.add(match.group(1))
                
                # Save to vault
                date_formatted = speech['date'].replace("-", "")
                vault_file = vault_base / f"{date_formatted}.md"
                
                content = f"""---
date: {speech['date']}
title: {speech['title']}
chamber: deputies
ids: {speech['ids']}
participants: {list(mps)}
laws_discussed: {list(laws)}
---

# {speech['title']}

**Date**: {speech['date']}  
**IDs**: {speech['ids']}  
**Source**: [cdep.ro]({speech['url']})

## Participants

"""
                for mp in sorted(mps):
                    content += f"- [[{mp}]]\n"
                
                content += "\n## Laws Discussed\n\n"
                for law in sorted(laws):
                    content += f"- [[{law}]]\n"
                
                content += f"\n## Transcript\n\n[Source]({speech['url']})\n"
                
                vault_base.mkdir(parents=True, exist_ok=True)
                with open(vault_file, "w", encoding="utf-8") as f:
                    f.write(content)
                
                saved += 1
                print(f"  Saved: {vault_file.name}")
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"\nSaved {saved} sessions to vault")


if __name__ == "__main__":
    main()