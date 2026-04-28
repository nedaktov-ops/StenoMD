#!/usr/bin/env python3
"""
StenoMD Brain Builder - Vault Enhancement & Scraper Orchestrator
==================================================================
Builds the "Brain" vault by:
1. Running gap-aware scrapers
2. Processing existing data
3. Updating vault with links and connections

Usage:
    python3 brain_builder.py --scrape senators --limit 20
    python3 brain_builder.py --process existing --limit 50
    python3 brain_builder.py --full
"""

import os
import re
import json
import time
import random
import requests
from pathlib import Path
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# Use centralized configuration
try:
    from config import get_config
    config = get_config()
    PROJECT_DIR = config.PROJECT_ROOT
    GRAPH_FILE = PROJECT_DIR / "Graphify" / "graphify-out" / "graph.json"
    DATA_DIR = PROJECT_DIR / "data"
    VAULT_DIR = config.VAULT_DIR
except ImportError:
    PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
    GRAPH_FILE = PROJECT_DIR / "Graphify" / "graphify-out" / "graph.json"
    DATA_DIR = PROJECT_DIR / "data"
    VAULT_DIR = PROJECT_DIR / "vault"

# Respectful scraping settings
MIN_DELAY = 3
MAX_DELAY = 8
MAX_WORKERS = 2

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def random_delay():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

def load_graph():
    """Load existing graph."""
    if GRAPH_FILE.exists():
        with open(GRAPH_FILE) as f:
            return json.load(f)
    return {"nodes": [], "links": []}

def get_targets():
    """Get entities needing data from graph."""
    graph = load_graph()
    
    targets = {
        "senators": [],
        "deputies": [],
        "laws": [],
        "sessions": []
    }
    
    for node in graph.get("nodes", []):
        source = node.get("source_file", "")
        
        if "senators/" in source:
            if not node.get("party") or not node.get("speeches_count"):
                targets["senators"].append(node)
        elif "deputies/" in source:
            if not node.get("party") or not node.get("speeches_count"):
                targets["deputies"].append(node)
        elif "laws/" in source:
            if not node.get("sponsors"):
                targets["laws"].append(node)
        elif "sessions/" in source:
            if not node.get("speech_count"):
                targets["sessions"].append(node)
    
    return targets

def create_vault_profile(data, chamber_type):
    """Create/enhance a vault profile with enrichment data."""
    name = data.get("name", "")
    if not name:
        return None
    
    # Create filename safe name
    filename = name.lower()
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'\s+', '-', filename)
    
    # Determine path
    if chamber_type == "senator":
        file_path = VAULT_DIR / "politicians" / "senators" / f"{filename}.md"
    else:
        file_path = VAULT_DIR / "politicians" / "deputies" / f"{filename}.md"
    
    # If doesn't exist, create basic
    if not file_path.exists():
        # Create directory if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate frontmatter
        frontmatter = f"""---
stable_id: {data.get('stable_id', '')}
original_elected_party: {data.get('party', 'Unknown')}
type: {chamber_type}
chamber: {'senate' if chamber_type == 'senator' else 'chamber'}
party: {data.get('party', 'Unknown')}
party_full: {data.get('party_full', '')}
constituency: {data.get('constituency', '')}
legislature: 2024-2028
status: active
url: {data.get('url', '')}
ai_friendly_name: {name.upper()}
search_aliases: ['{name.upper()}', '{name.lower()}']
activity_score: 0
idm: {data.get('idm', '')}
speeches_count: 0
laws_proposed: 0
committees: []
---

# {name}

## Related Sections
- [[politicians/deputies|Deputies]]
- [[politicians/senators|Senators]]
- [[laws|Laws]]
- [[committees|Committees]]
- [[sessions|Sessions]]

## Activity
- **(Source URL):** {data.get('url', '')}
- **(Last Synced):** {datetime.now().strftime('%Y-%m-%d')}

## Memory
### Speeches
- (None recorded yet)

### Voting Record
- (Not available)

## Intelligence Notes
- Created by Brain Builder
"""
        
        file_path.write_text(frontmatter)
        log(f"Created: {file_path.name}")
    else:
        # Update existing - add missing fields
        content = file_path.read_text()
        
        # Only update if doesn't have party
        if 'party: Unknown' in content or 'party:\n' in content:
            # Update party if we have it
            if data.get('party'):
                # Simple update - just log for now
                log(f"Needs update: {file_path.name}")
    
    return str(file_path)

def process_stenogram_data():
    """Process existing stenogram data to extract activity."""
    log("=== Processing Existing Stenogram Data ===")
    
    processed = 0
    
    # Process stenogram HTML files
    for html_file in DATA_DIR.glob("stenogram*.html"):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract speakers
            speakers = set()
            for text in soup.find_all(string=re.compile(r'domnul|doamna', re.IGNORECASE)):
                # Extract name
                match = re.search(r'(domnul|doamna)\s+([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)', text, re.IGNORECASE)
                if match:
                    speakers.add(match.group(2))
            
            if speakers:
                log(f"  {html_file.name}: {len(speakers)} speakers")
                processed += 1
        
        except Exception as e:
            log(f"Error processing {html_file.name}: {e}")
    
    return processed

def scrape_senator_session_urls():
    """Get senator speech URLs from senat.ro."""
    log("=== Fetching Senator Session URLs ===")
    
    urls = []
    base_url = "https://www.senat.ro"
    
    try:
        # Get 2024-2025 senators list page
        session = requests.Session()
        session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
        })
        
        # Senators list
        list_url = f"{base_url}/ListaSenatori.aspx?legislatura=2024"
        
        random_delay()
        response = session.get(list_url, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find senator links
            for link in soup.find_all('a', href=re.compile(r'FisaSenator\.aspx\?ParlamentarID=')):
                href = link.get('href', '')
                if href:
                    full_url = f"{base_url}/{href}" if not href.startswith('http') else href
                    name = link.get_text(strip=True)
                    if name and len(name) > 3:
                        urls.append({"name": name, "url": full_url})
            
            log(f"Found {len(urls)} senator profile URLs")
    
    except Exception as e:
        log(f"Error fetching senator URLs: {e}")
    
    return urls

def update_vault_from_scraped():
    """Update vault files with newly scraped data."""
    log("=== Updating Vault from Scraped Data ===")
    
    updated = 0
    
    # Check existing data files - format is {"legislature": "", "senators": [...]}
    if (DATA_DIR / "senators_2024_full.json").exists():
        with open(DATA_DIR / "senators_2024_full.json") as f:
            data = json.load(f)
            
            senators_list = data.get("senators", [])
            log(f"Found {len(senators_list)} senators in data")
            
            for item in senators_list:
                # Create or update profile - format is {"name": "...", "party": "...", ...}
                name = item.get("name", "")
                if name:
                    profile_data = {
                        "name": name,
                        "party": item.get("party", "Unknown"),
                        "party_full": item.get("party_full", ""),
                        "constituency": item.get("constituency", ""),
                        "stable_id": f"sen_{name.replace(' ', '_').lower()}"
                    }
                    
                    result = create_vault_profile(profile_data, "senator")
                    if result:
                        updated += 1
    
    log(f"Updated {updated} vault profiles")
    return updated

def build_brain():
    """Main brain building orchestration."""
    log("=" * 60)
    log("STENOMD BRAIN BUILDER")
    log("=" * 60)
    log(f"Project: {PROJECT_DIR.name}")
    log(f"Graph: {len(load_graph().get('nodes', []))} nodes")
    
    targets = get_targets()
    log(f"\n=== Gap Targets ===")
    log(f"Senators needing data: {len(targets['senators'])}")
    log(f"Deputies needing data: {len(targets['deputies'])}")
    log(f"Laws needing data: {len(targets['laws'])}")
    log(f"Sessions needing data: {len(targets['sessions'])}")
    
    # Process existing data
    log(f"\n=== Step 1: Process Existing Data ===")
    processed = process_stenogram_data()
    log(f"Processed {processed} stenogram files")
    
    # Update vault
    log(f"\n=== Step 2: Update Vault ===")
    updated = update_vault_from_scraped()
    log(f"Updated {updated} vault profiles")
    
    # Get URLs for scraping
    log(f"\n=== Step 3: Get Senator URLs ===")
    urls = scrape_senator_session_urls()
    log(f"Found {len(urls)} senator URLs ready for scraping")
    
    return {
        "targets": targets,
        "processed": processed,
        "updated": updated,
        "senator_urls": urls
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="StenoMD Brain Builder")
    parser.add_argument("--scrape", help="Scrape type: senators, deputies")
    parser.add_argument("--limit", type=int, default=10, help="Limit scrapes")
    parser.add_argument("--process", help="Process existing: all, stenograms")
    parser.add_argument("--full", action="store_true", help="Full brain build")
    args = parser.parse_args()
    
    if args.full:
        result = build_brain()
        log(f"\n=== SUMMARY ===")
        log(f"Targets: {result['targets']}")
        log(f"Processed: {result['processed']}")
        log(f"Updated: {result['updated']}")
        log(f"Senator URLs: {result['senator_urls']}")
    elif args.process:
        if args.process == "existing" or args.process == "stenograms":
            processed = process_stenogram_data()
            log(f"Processed {processed} files")
    elif args.scrape:
        log(f"Would scrape {args.scrape} with limit {args.limit}")
        log("(Note: Scraping requires manual confirmation for rate limiting)")
    else:
        # Show status
        targets = get_targets()
        log(f"=== Current Gap Status ===")
        log(f"Senators: {len(targets['senators'])} need data")
        log(f"Deputies: {len(targets['deputies'])} need data")
        log(f"Use --full to process and build")

if __name__ == "__main__":
    main()