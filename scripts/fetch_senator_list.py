#!/usr/bin/env python3
"""
Fetch senator list from senat.ro/FisaSenatori.aspx
Creates 134+ senator profiles with party and constituency data.
"""

import re
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
SENATOR_LIST_URL = "https://senat.ro/FisaSenatori.aspx"
VAULT_SENATORS_DIR = PROJECT_DIR / "vault/politicians/senators"


def scrape_senat_ro() -> List[Dict]:
    """Scrape senator list from senat.ro/FisaSenatori.aspx"""
    senators = []
    
    if not HAS_DEPS:
        print("ERROR: requests and BeautifulSoup required")
        print("  pip install requests beautifulsoup4")
        return senators
    
    print(f"Fetching {SENATOR_LIST_URL}...")
    
    try:
        resp = requests.get(
            SENATOR_LIST_URL,
            timeout=30,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find senator links - they typically link to individual senator pages
        senator_links = soup.select('a[href*="senator"], a[href*="Senator"]')
        
        seen = set()
        for link in senator_links:
            name = link.get_text(strip=True)
            if not name or len(name) < 5:
                continue
            
            # Skip navigation links
            if any(skip in name.lower() for skip in ['camera', 'senat', 'acasa', 'home', 'legi', 'info']):
                continue
            
            # Clean name
            name = re.sub(r'\s+', ' ', name).strip()
            name_key = name.lower()
            
            if name_key in seen:
                continue
            seen.add(name_key)
            
            href = link.get('href', '')
            profile_url = urljoin("https://senat.ro", href) if href else ""
            
            senators.append({
                'name': name,
                'profile_url': profile_url
            })
        
        print(f"  Found {len(senators)} potential senators from primary list")
        
    except Exception as e:
        print(f"  Error fetching primary: {e}")
    
    # Try alternative: Find in table format
    if not senators:
        print("  Trying table format...")
        try:
            resp = requests.get(SENATOR_LIST_URL, timeout=30)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Try table rows
            for row in soup.select('table tr, .senator-row, .list-item'):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    name_cell = cells[0]
                    name_link = name_cell.find('a') or name_cell
                    name = name_link.get_text(strip=True)
                    if name and len(name) > 3:
                        senators.append({
                            'name': name,
                            'profile_url': ""
                        })
            
            print(f"  Found {len(senators)} from table format")
        except Exception as e:
            print(f"  Table format error: {e}")
    
    return senators


def scrape_wikipedia() -> List[Dict]:
    """Scrape senator list from Romanian Wikipedia"""
    senators = []
    
    wiki_url = "https://ro.wikipedia.org/wiki/Legislatura_2024-2028_(Senat)"
    
    if not HAS_DEPS:
        return senators
    
    print(f"Fetching {wiki_url}...")
    
    try:
        resp = requests.get(wiki_url, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find table with senators
        tables = soup.select('table.wikitable, table.sortable')
        
        for table in tables:
            rows = table.select('tr')
            for row in rows[1:]:  # Skip header
                cells = row.select('td')
                if len(cells) >= 3:
                    # Format: Name | Party | Constituency
                    name_cell = cells[0]
                    party_cell = cells[1]
                    const_cell = cells[2]
                    
                    name = name_cell.get_text(strip=True)
                    party = party_cell.get_text(strip=True)
                    constituency = const_cell.get_text(strip=True)
                    
                    if name and party:
                        senators.append({
                            'name': name,
                            'party': party,
                            'constituency': constituency
                        })
        
        print(f"  Found {len(senators)} senators from Wikipedia")
        
    except Exception as e:
        print(f"  Wikipedia error: {e}")
    
    return senators


def parse_ipu_csv() -> List[Dict]:
    """Try to load IPU Parline data"""
    senators = []
    
    # Try local cache first
    ipu_cache = PROJECT_DIR / "data" / "ipu_senators_ro.csv"
    
    if ipu_cache.exists():
        print(f"Loading from {ipu_cache}...")
        try:
            content = ipu_cache.read_text()
            for line in content.split('\n')[1:]:  # Skip header
                if not line.strip():
                    continue
                parts = line.split(',')
                if len(parts) >= 4:
                    senators.append({
                        'name': parts[1].strip().strip('"'),
                        'constituency': parts[2].strip().strip('"'),
                        'party': parts[3].strip().strip('"')
                    })
            print(f"  Loaded {len(senators)} from IPU cache")
            return senators
        except Exception as e:
            print(f"  IPU cache error: {e}")
    
    print("  No IPU CSV cache - will use scraped data only")
    return senators


def merge_senator_data(primary: List[Dict], wiki: List[Dict]) -> List[Dict]:
    """Merge data from multiple sources"""
    merged = {}
    
    # Index by name (normalized)
    for s in primary:
        name_norm = s['name'].lower().strip()
        merged[name_norm] = s.copy()
    
    # Add wiki data
    for s in wiki:
        name_norm = s['name'].lower().strip()
        if name_norm in merged:
            merged[name_norm].update({
                'party': s.get('party', ''),
                'constituency': s.get('constituency', '')
            })
        else:
            merged[name_norm] = s.copy()
    
    return list(merged.values())


def create_senator_profile(senator: Dict) -> str:
    """Create senator markdown profile"""
    name = senator.get('name', 'Unknown')
    party = senator.get('party', 'Unknown')
    constituency = senator.get('constituency', '')
    profile_url = senator.get('profile_url', '')
    
    # Parse party abbreviation if full name provided
    party_abbrev = ''
    party_map = {
        'Partidul Social Democrat': 'PSD',
        'Alianța pentru Unirea Românilor': 'AUR',
        'Partidul Național Liberal': 'PNL',
        'Uniunea Salvați România': 'USR',
        'S.O.S. România': 'SOS',
        'Uniunea Democrată Maghiară din România': 'UDMR',
        'Partidul Oamenilor Tineri': 'POT'
    }
    for full, abbr in party_map.items():
        if full.lower() in party.lower():
            party_abbrev = abbr
            break
    
    if not party_abbrev and party:
        party_abbrev = party[:4].upper()
    
    content = f"""---
tags:
- politician
type: senator
chamber: senate
party: {party_abbrev}
party_full: {party}
constituency: {constituency}
legislature: 2024-2028
status: active
url: {profile_url}
---

# {name}

## Details

- **Party**: {party} ({party_abbrev})
- **Constituency**: {constituency}
- **Legislature**: 2024-2028
- **Source**: senat.ro

## Activity

- Source: {profile_url}

## Tags

#politician #senator
"""
    
    return content


def save_senator_profiles(senators: List[Dict], dry_run: bool = True) -> int:
    """Save senator profiles to vault"""
    saved = 0
    
    VAULT_SENATORS_DIR.mkdir(parents=True, exist_ok=True)
    
    for senator in senators:
        name = senator.get('name', '')
        if not name:
            continue
        
        # Create filename-safe slug (preserving Romanian characters)
        name_for_slug = name.replace('ă', 'a').replace('â', 'a').replace('ț', 't')
        name_for_slug = name_for_slug.replace('ș', 's').replace('Ș', 'S')
        name_for_slug = name_for_slug.replace('Ă', 'A').replace('Ț', 'T')
        name_for_slug = name_for_slug.replace('Î', 'I').replace('ș', 's')
        
        # Simple ASCII-only slug
        name_for_slug = re.sub(r'[^a-zA-Z\s]', ' ', name_for_slug)
        name_for_slug = re.sub(r'\s+', ' ', name_for_slug).strip()
        
        slug_parts = name_for_slug.lower().split()
        slug = '-'.join(slug_parts)
        
        filepath = VAULT_SENATORS_DIR / f"{slug}.md"
        
        if dry_run:
            print(f"  Would create: {filepath.name}")
        else:
            content = create_senator_profile(senator)
            filepath.write_text(content, encoding='utf-8')
            print(f"  Created: {filepath.name}")
        
        saved += 1
    
    return saved


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Fetch senator list from senat.ro")
    parser.add_argument('--dry-run', '-n', action='store_true', help='Show what would be created')
    parser.add_argument('--force', '-f', action='store_true', help='Overwrite existing')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Phase 1: Senator List Scraping")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()
    
    if not HAS_DEPS:
        print("ERROR: Install dependencies first:")
        print("  pip install requests beautifulsoup4")
        return 1
    
    # Step 1: Scrape senat.ro
    print("[1] Scraping senat.ro...")
    primary_senators = scrape_senat_ro()
    print()
    
    # Step 2: Try Wikipedia
    print("[2] Scraping Wikipedia...")
    wiki_senators = scrape_wikipedia()
    print()
    
    # Step 3: Merge data
    print("[3] Merging data sources...")
    all_senators = merge_senator_data(primary_senators, wiki_senators)
    print(f"  Total unique senators: {len(all_senators)}")
    print()
    
    # Step 4: Save profiles
    print(f"[4] Saving to {VAULT_SENATORS_DIR}...")
    saved = save_senator_profiles(all_senators, dry_run=args.dry_run)
    print()
    
    print(f"Results: {saved} senator profiles")
    
    if args.dry_run:
        print("\nRun without --dry-run to apply changes.")
        return 0
    
    print("\n" + "=" * 60)
    print("Phase 1: Senator List Complete")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())