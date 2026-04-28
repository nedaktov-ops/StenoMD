#!/usr/bin/env python3
"""
Senator profile creation with enriched data.
Uses multiple sources to create comprehensive senator profiles.
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml

# Use centralized configuration
try:
    from config import get_config
    config = get_config()
    PROJECT_DIR = config.PROJECT_ROOT
    VAULT_SENATORS_DIR = config.VAULT_DIR / "politicians" / "senators"
    DATA_DIR = config.PROJECT_ROOT / "data"
except ImportError:
    PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
    VAULT_SENATORS_DIR = PROJECT_DIR / "vault/politicians/senators"
    DATA_DIR = PROJECT_DIR / "data"


def get_current_senators() -> List[str]:
    """Get currently stored senators."""
    senators = []
    if not VAULT_SENATORS_DIR.exists():
        return senators
    
    for mp_file in VAULT_SENATORS_DIR.glob("*.md"):
        if mp_file.name == "Index.md":
            continue
        senators.append(mp_file.stem.replace("-", " "))
    
    return sorted(senators)


def scrape_senat_ro() -> Dict[str, Dict]:
    """Scrape senator list from senat.ro."""
    senators = {}
    
    print("Attempting to scrape senat.ro...")
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        resp = requests.get(
            "https://www.senat.ro/Senatori.aspx",
            timeout=30,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; StenoMD/1.0)'}
        )
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        links = soup.select('a[href*="Senatori"]')
        
        for link in links:
            name = link.get_text(strip=True)
            if name and len(name) > 3:
                href = link.get('href', '')
                if href:
                    senators[name] = {
                        'name': name,
                        'url': f"https://www.senat.ro{href}",
                        'source': 'senat.ro'
                    }
        
        print(f"  Found {len(senators)} senators from senat.ro")
    except ImportError:
        print("  requests/bs4 not available")
    except Exception as e:
        print(f"  Error: {e}")
    
    return senators


def load_wikipedia_senators() -> Dict[str, Dict]:
    """Try loading senator data from Wikipedia or other sources."""
    senators = {}
    
    sources = [
        DATA_DIR / "senators_wikipedia.json",
        DATA_DIR / "senators.json",
        DATA_DIR / "senat_ro_senators.json"
    ]
    
    for source in sources:
        if not source.exists():
            continue
        
        try:
            data = json.loads(source.read_text())
            for item in data:
                name = item.get('name', item.get('nume', ''))
                if name:
                    senators[name] = item
            print(f"  Loaded {len(senators)} from {source.name}")
            break
        except Exception as e:
            print(f"  Error loading {source.name}: {e}")
    
    return senators


def create_senator_profile(name: str, metadata: Dict = None) -> str:
    """Create a senator profile markdown file."""
    if metadata is None:
        metadata = {}
    
    name_parts = name.split()
    slug = "-".join(name_parts).lower()
    
    party = metadata.get('party', 'Unknown')
    party_full = metadata.get('party_full', '')
    constituency = metadata.get('constituency', '')
    
    content = f"""---
tags:
- politician
type: deputy
chamber: senate
party: {party}
party_full: {party_full}
constituency: {constituency}
legislature: 2024-2028
status: active
---

# {name}

## Activity

- Source: {metadata.get('source', 'senat.ro')}
- URL: {metadata.get('url', '')}

## Tags

#politician
"""
    
    return content


def main():
    """Main entry point."""
    print("=" * 60)
    print("Phase 3: Senator Profile Creation")
    print("=" * 60)
    print()
    
    current = get_current_senators()
    print(f"Current senators in vault: {len(current)}")
    
    for s in current:
        print(f"  - {s}")
    
    print()
    
    for name in current:
        filepath = VAULT_SENATORS_DIR / f"{name.replace(' ', '-')}.md"
        if filepath.exists():
            content = filepath.read_text()
            if '---' in content:
                fm, body = content.split('---', 2)
                try:
                    data = yaml.safe_load(fm)
                    if not data.get('party') or not data.get('constituency'):
                        print(f"  {name}: needs enrichment")
                except:
                    pass
    
    print("\nNote: Run senat_agent.py with more sessions to discover new senators.")
    print("  python3 scripts/agents/senat_agent.py --year 2026 --max 100 --sync-vault")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())