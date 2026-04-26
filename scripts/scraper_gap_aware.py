#!/usr/bin/env python3
"""
Gap-Aware Scraper for StenoMD
Uses graph.json to identify and scrape only missing data.

Usage:
    python3 scraper_gap_aware.py --type party
    python3 scraper_gap_aware.py --type speeches
    python3 scraper_gap_aware.py --type committees
    python3 scraper_gap_aware.py --type all --limit 50
"""

import json
import sys
import time
import random
import requests
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
GRAPH_FILE = PROJECT_DIR / "Graphify" / "graphify-out" / "graph.json"
OUTPUT_DIR = PROJECT_DIR / "data" / "gap_aware"
VAULT_DIR = PROJECT_DIR / "vault"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_DELAY = 3
MAX_DELAY = 8
MAX_WORKERS = 2

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def random_delay():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

def load_graph():
    """Load existing graph."""
    if not GRAPH_FILE.exists():
        log("ERROR: No graph found. Run /graphify first!")
        sys.exit(1)
    
    with open(GRAPH_FILE) as f:
        return json.load(f)

def get_targets_by_type(graph, scrap_type):
    """Get entities needing specific data type."""
    targets = {
        "senators": [],
        "deputies": [],
        "laws": [],
        "sessions": []
    }
    
    for node in graph.get("nodes", []):
        source = node.get("source_file", "")
        label = node.get("label", "")
        
        if scrap_type in ["party", "speeches", "committees"]:
            # Politicians
            if "senators/" in source:
                if should_scrape(node, scrap_type):
                    targets["senators"].append(node)
            elif "deputies/" in source or "politicians/" in source:
                if should_scrape(node, scrap_type):
                    targets["deputies"].append(node)
        
        elif scrap_type == "law_sponsors" and "laws/" in source:
            if not node.get("sponsors") and not node.get("proposed_by"):
                targets["laws"].append(node)
        
        elif scrap_type == "session_activity" and "sessions/" in source:
            if not node.get("deputy_count") and not node.get("speech_count"):
                targets["sessions"].append(node)
    
    return targets

def should_scrape(node, scrap_type):
    """Check if node needs this data type."""
    if scrap_type == "party":
        return not node.get("party") and node.get("chamber")
    elif scrap_type == "speeches":
        return node.get("speeches_count", 0) == 0 or not node.get("speeches_count")
    elif scrap_type == "committees":
        return not node.get("committees") or node.get("committees") == []
    return False

def scrape_senator_data(targets, limit=20):
    """Scrape senator data from senat.ro."""
    scraped = []
    
    for target in targets[:limit]:
        name = target.get("label", "")
        url = target.get("url", "")
        
        if not url:
            continue
        
        try:
            random_delay()
            
            session = requests.Session()
            session.headers.update({
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html",
            })
            
            response = session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = parse_senator_page(response.text, target)
                scraped.append(data)
                log(f"Scraped: {name}")
            else:
                log(f"Failed: {name} ({response.status_code})")
        
        except Exception as e:
            log(f"Error scraping {name}: {e}")
    
    return scraped

def parse_senator_page(html, target):
    """Parse senator page for data."""
    import re
    from bs4 import BeautifulSoup
    
    data = {
        "id": target.get("id"),
        "name": target.get("label"),
        "source_url": target.get("url")
    }
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract party
    party_patterns = [
        r'Partidul\s+([A-Z\u0100-\u017F]+)',
        r' grupul[:\s]+([A-Z\u0100-\u017F]+)',
    ]
    for pattern in party_patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            data["party"] = match.group(1)
            break
    
    # Extract committees
    committee_links = soup.find_all("a", href=lambda x: x and "comisia" in x.lower() if x else False)
    if committee_links:
        data["committees"] = [link.get_text(strip=True) for link in committee_links[:5]]
    
    return data

def scrape_deputy_data(targets, limit=20):
    """Scrap deputy data from cdep.ro."""
    scraped = []
    
    for target in targets[:limit]:
        name = target.get("label", "")
        url = target.get("url", "")
        idm = target.get("idm", "")
        
        if not url and not idm:
            continue
        
        try:
            random_delay()
            
            # Try to construct URL
            if not url and idm:
                url = f"https://www.cdep.ro/pls/parlam/struct2015.mp?idm={idm}&cam=2&leg=2024"
            
            if not url:
                continue
            
            session = requests.Session()
            session.headers.update({
                "User-Agent": random.choice(USER_AGENTS),
            })
            
            response = session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = parse_deputy_page(response.text, target)
                scraped.append(data)
                log(f"Scraped: {name}")
        
        except Exception as e:
            log(f"Error: {e}")
    
    return scraped

def parse_deputy_page(html, target):
    """Parse deputy page."""
    import re
    from bs4 import BeautifulSoup
    
    data = {
        "id": target.get("id"),
        "name": target.get("label"),
    }
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Look for party info
    party_text = soup.find(text=re.compile(r'Partidul|Grupul', re.IGNORECASE))
    if party_text:
        data["party"] = party_text.parent.get_text(strip=True)[:50]
    
    return data

def save_scraped_data(data, scrap_type):
    """Save scraped data."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"{scrap_type}_{timestamp}.json"
    
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    log(f"Saved to: {output_file}")
    return output_file

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gap-aware scraper")
    parser.add_argument("--type", choices=["party", "speeches", "committees", "law_sponsors", "session_activity", "all"], required=True)
    parser.add_argument("--limit", type=int, default=20, help="Limit per category")
    args = parser.parse_args()
    
    log(f"=== Gap-Aware Scraper: {args.type} ===")
    
    graph = load_graph()
    log(f"Loaded graph: {len(graph.get('nodes', []))} nodes")
    
    targets = get_targets_by_type(graph, args.type)
    
    # Report targets
    log(f"\n=== Targets Found ===")
    for category, items in targets.items():
        log(f"{category}: {len(items)} need {args.type}")
    
    if args.type == "party":
        scraped = scrape_senator_data(targets["senators"], args.limit)
        scraped += scrape_deputy_data(targets["deputies"], args.limit)
    elif args.type == "speeches":
        log("Speeches scraping - use dedicated speech scraper")
    elif args.type == "committees":
        scraped = scrape_senator_data(targets["senators"], args.limit)
    else:
        log(f"Type {args.type} not yet implemented")
        return
    
    if scraped:
        save_scraped_data(scraped, args.type)
        log(f"\nScraped {len(scraped)} records")
    else:
        log("\nNo data scraped (or type not implemented)")

if __name__ == "__main__":
    main()