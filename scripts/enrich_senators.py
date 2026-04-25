#!/usr/bin/env python3
"""
Enrich senator profiles with party and constituency data.
Uses detailed senator profile pages from senat.ro.
"""

import re
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, List
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
VAULT_SENATORS_DIR = PROJECT_DIR / "vault/politicians/senators"
BASE_URL = "https://senat.ro"


def get_existing_senators() -> List[Dict]:
    """Get existing senator profiles from vault"""
    senators = []
    
    for filepath in VAULT_SENATORS_DIR.glob("*.md"):
        if filepath.name == "Index.md":
            continue
        
        name = filepath.stem.replace('-', ' ').title()
        senators.append({
            'name': name,
            'filepath': filepath
        })
    
    return senators


def try_senat_detail_pages(existing: List[Dict]) -> Dict[str, Dict]:
    """Try to scrape detailed senator pages"""
    enriched = {}
    
    if not HAS_DEPS:
        return enriched
    
    # Common patterns for senator detail pages
    senator_urls = [
        f"{BASE_URL}/Senatori.aspx",
        f"{BASE_URL}/Senatori.aspx?leg=2024",
    ]
    
    print("Enriching senator profiles with party/constituency data...")
    
    # Try the main page again with more thorough parsing
    for url in senator_urls:
        try:
            print(f"  Fetching {url}...")
            resp = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Look for tables with senator data
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        # Try to extract: Name, Party, Constituency
                        name_cell = cells[0]
                        link = name_cell.find('a')
                        if link:
                            name = link.get_text(strip=True)
                            
                            # Get subsequent cells for party/constituency
                            party = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                            const = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                            
                            if name and len(name) > 3:
                                normalized = name.lower().strip()
                                enriched[normalized] = {
                                    'party': party,
                                    'constituency': const
                                }
            
            print(f"  Found data for {len(enriched)} senators")
            
            if enriched:
                break
                
        except Exception as e:
            print(f"  Error: {e}")
    
    # Fallback: Use known party data from Wikipedia/public sources
    if not enriched:
        print("  Using fallback party data...")
        
        # Known senators with their parties (from Wikipedia 2024-2028 list)
        known_parties = {
            'mircea abrudean': {'party': 'PNL', 'constituency': 'Cluj'},
            'mihai coteț': {'party': 'PNL', 'constituency': 'Galați'},
            'vasile blaga': {'party': 'PNL', 'constituency': 'Hunedoara'},
            'niculina stelea': {'party': 'PSD', 'constituency': 'Teleorman'},
            'doina elena federovici': {'party': 'PSD', 'constituency': 'Botoșani'},
            'valentina mariana aldea': {'party': 'POT', 'constituency': 'București'},
            'cristian ghinea': {'party': 'USR', 'constituency': 'Iași'},
            'ninel peia': {'party': 'AUR', 'constituency': 'Mureș'},
        }
        
        enriched.update(known_parties)
        print(f"  Added fallback data for {len(enriched)} known senators")
    
    return enriched


def merge_party_data(enriched: Dict[str, Dict]) -> int:
    """Merge party/constituency into existing profiles"""
    updated = 0
    
    party_map = {
        'Partidul Social Democrat': 'PSD',
        'Alianța pentru Unirea Românilor': 'AUR', 
        'Partidul Național Liberal': 'PNL',
        'Uniunea Salvați România': 'USR',
        'S.O.S. România': 'SOS',
        'Uniunea Democrată Maghiară': 'UDMR',
        'Partidul Oamenilor Tineri': 'POT'
    }
    
    for filepath in VAULT_SENATORS_DIR.glob("*.md"):
        if filepath.name == "Index.md":
            continue
        
        # Find matching enriched data
        name_normalized = filepath.stem.lower().replace('-', ' ')
        
        data = None
        for key, enriched_data in enriched.items():
            if key in name_normalized or name_normalized in key:
                data = enriched_data
                break
        
        if not data:
            continue
        
        # Read existing profile
        content = filepath.read_text(encoding='utf-8')
        
        # Parse frontmatter
        if '---' not in content:
            continue
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            continue
        
        fm_text = parts[1]
        body = parts[2]
        
        # Simple YAML-like update
        party_abbrev = data.get('party', '')
        party_full = data.get('party_full', '')
        constituency = data.get('constituency', '')
        
        # Map party name to abbreviation if needed
        if party_abbrev not in ['PSD', 'AUR', 'PNL', 'USR', 'SOS', 'UDMR', 'POT']:
            for full, abbr in party_map.items():
                if full.lower() in party_abbrev.lower():
                    party_abbrev = abbr
                    party_full = full
                    break
        
        # Update frontmatter
        if 'party: UNKN' in fm_text and party_abbrev:
            fm_text = fm_text.replace('party: UNKN', f'party: {party_abbrev}')
        if 'party_full: Unknown' in fm_text and party_full:
            fm_text = fm_text.replace('party_full: Unknown', f'party_full: {party_full}')
        if 'constituency: ' in fm_text and constituency:
            fm_text = fm_text.replace('constituency: \n', f'constituency: {constituency}\n')
        
        # Write back
        new_content = f"---\n{fm_text}---\n{body}"
        filepath.write_text(new_content, encoding='utf-8')
        updated += 1
    
    return updated


def main():
    """Main entry point"""
    print("=" * 60)
    print("Enriching Senator Profiles")
    print("=" * 60)
    
    if not HAS_DEPS:
        print("ERROR: Install dependencies first:")
        print("  pip install requests beautifulsoup4")
        return 1
    
    # Get existing
    existing = get_existing_senators()
    print(f"Existing senators: {len(existing)}")
    
    # Try to enrich
    enriched = try_senat_detail_pages(existing)
    
    # Merge
    updated = merge_party_data(enriched)
    print(f"\nUpdated: {updated} profiles")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())