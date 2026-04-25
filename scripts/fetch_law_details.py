#!/usr/bin/env python3
"""
Fetch law details from cdep.ro/pls/parlam/
Creates law profiles with title, sponsors, status, etc.
"""

import re
import sys
import json
import time
import random
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
VAULT_LAWS_DIR = PROJECT_DIR / "vault/laws"
CDEP_LEGISLATION_URL = "https://www.cdep.ro/pls/proy/upload/"
BASE_URL = "https://www.cdep.ro"


def scrape_legislative_proposals(page: int = 1, max_results: int = 100) -> List[Dict]:
    """Scrape legislative proposals from cdep.ro"""
    laws = []
    
    if not HAS_DEPS:
        return laws
    
    # Try different endpoints
    urls_to_try = [
        f"{CDEP_LEGISLATION_URL}?pag={page}&leg=2024",
        f"https://www.cdep.ro/pls/proy/lista?leg=2024&pag={page}",
    ]
    
    for url in urls_to_try:
        try:
            print(f"Fetching {url}...")
            resp = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if resp.status_code != 200:
                continue
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Look for law entries
            # Try table rows first
            rows = soup.select('table tr, .proiect, .law-item')
            
            for row in rows[:max_results]:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    # Try to extract law number, title
                    text = row.get_text()
                    
                    # Look for law number pattern like "76/2024" or "PL-x 2024"
                    law_match = re.search(r'(\d+)/(\d{4})|PL-x\s*(\d+)', text)
                    if law_match:
                        law_num = law_match.group(1) or law_match.group(3)
                        year = law_match.group(2) if law_match.group(2) else "2024"
                        
                        # Get title from nearby element
                        title = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                        
                        if title and len(title) > 5:
                            laws.append({
                                'law_number': f"{law_num}/{year}",
                                'title': title,
                                'year': year
                            })
            
            if laws:
                print(f"Found {len(laws)} laws")
                break
                
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue
    
    return laws


def parse_law_from_session_content(content: str) -> List[Dict]:
    """Extract laws mentioned in session transcripts"""
    laws = []
    
    # Law number patterns
    patterns = [
        r'Legea\s+(nr\.)?\s*(\d+)/(\d{4})',
        r'PL-x\s*#?\s*(\d+)',
        r'Proiect(ul)?\s+de\s+legege\s+(nr\.)?\s*(\d+)/(\d{4})',
        r'Hotărâre\s+(nr\.)?\s*(\d+)/(\d{4})',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            num = match.group(1) or match.group(3)
            year = match.group(2) or match.group(4) if match.lastindex >= 2 else ""
            
            law_num = f"{num}/{year}" if year else num
            
            laws.append({
                'law_number': law_num,
                'context': content[max(0, match.start()-50):match.end()+50]
            })
    
    return laws


def get_existing_laws() -> Dict[str, Path]:
    """Get existing law files from vault"""
    existing = {}
    
    for filepath in VAULT_LAWS_DIR.glob("*.md"):
        if filepath.name == "Index.md":
            continue
        
        # Extract law number from filename
        law_num = filepath.stem
        existing[law_num] = filepath
    
    return existing


def create_law_profile(law: Dict) -> str:
    """Create law markdown profile"""
    law_num = law.get('law_number', 'Unknown')
    title = law.get('title', 'Unknown Law')
    year = law.get('year', '')
    status = law.get('status', 'pending')
    sponsors = law.get('sponsors', [])
    category = law.get('category', '')
    
    content = f"""---
tags:
- law
law_number: "{law_num}"
title: "{title}"
title_short: "{title[:50]}..."
chamber: deputies
status: {status}
date_proposed: ""
date_adopted: ""
year: {year}
sponsors:
{sponsors}
category: {category}
---

# {law_num}: {title}

## Details

- **Number**: {law_num}
- **Title**: {title}
- **Year**: {year}
- **Status**: {status}
- **Chamber**: deputies

## Legislative History

- Proposed: 
- Adopted: 

## Tags

#law #{year}
"""
    
    return content


def enrich_law_file(filepath: Path, law_data: Dict) -> bool:
    """Enrich an existing law file with data"""
    try:
        content = filepath.read_text(encoding='utf-8')
        
        if '---' not in content:
            return False
        
        # Simple check - if content is minimal, skip
        if len(content) < 100:
            # Rewrite with enriched content
            new_content = create_law_profile(law_data)
            filepath.write_text(new_content, encoding='utf-8')
            return True
        
        return False
        
    except Exception as e:
        print(f"Error enriching {filepath.name}: {e}")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Fetch law details from cdep.ro")
    parser.add_argument('--dry-run', '-n', action='store_true', help='Show what would be created')
    parser.add_argument('--max', type=int, default=100, help='Max laws to process')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Phase 3: Law Details Scraper")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()
    
    if not HAS_DEPS:
        print("ERROR: Install dependencies:")
        print("  pip install requests beautifulsoup4")
        return 1
    
    # Get existing laws
    existing = get_existing_laws()
    print(f"Existing law files: {len(existing)}")
    
    # Try to scrape legislation
    print("\n[1] Scraping cdep.ro for legislation...")
    laws = scrape_legislative_proposals(max_results=args.max)
    
    if not laws:
        print("No laws scraped from cdep.ro - trying session-based extraction...")
        # Fallback: Scan existing sessions for law references
        from pathlib import Path
        sessions_dir = PROJECT_DIR / "vault/sessions/deputies"
        
        laws_found = {}
        
        for session_file in list(sessions_dir.glob("*.md"))[:50]:
            try:
                content = session_file.read_text(encoding='utf-8')
                session_laws = parse_law_from_session_content(content)
                
                for law in session_laws:
                    law_num = law.get('law_number', '')
                    if law_num and law_num not in laws_found:
                        laws_found[law_num] = law
                        
            except:
                continue
        
        laws = list(laws_found.values())
        print(f"Found {len(laws)} laws from session transcripts")
    
    print(f"\n[2] Processing {len(laws)} laws...")
    
    # Save laws
    for law in laws[:args.max]:
        law_num = law.get('law_number', '')
        if not law_num:
            continue
        
        # Clean law number
        law_num = re.sub(r'[^0-9/]', '', law_num)
        
        if args.dry_run:
            print(f"  Would create/update: {law_num}")
            continue
        
        # Check existing
        filepath = VAULT_LAWS_DIR / f"{law_num}.md"
        
        if filepath.exists():
            # Try to enrich
            if enrich_law_file(filepath, law):
                print(f"  Enriched: {law_num}")
        else:
            # Create new
            content = create_law_profile(law)
            filepath.write_text(content, encoding='utf-8')
            print(f"  Created: {law_num}")
    
    print(f"\nResults: Law profiles updated")
    print("\n" + "=" * 60)
    print("Phase 3: Law Scraper Complete")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())