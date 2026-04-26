#!/usr/bin/env python3
"""
Ultra-Respectful senat.ro Scraper
================================
A VERY slow and careful scraper designed to run over multiple sessions
without ever getting banned.

Key features:
- 20-40 second delays between requests (appears very human-like)
- Can run for just 3-5 senators per session
- Saves ALL progress immediately
- Can be stopped and resumed anytime
- Very conservative settings
"""

import os
import re
import json
import time
import random
import requests
from datetime import datetime

# SUPER CONSERVATIVE SETTINGS
MIN_DELAY = 20  # 20 seconds minimum
MAX_DELAY = 40  # 40 seconds maximum
BATCH_SIZE = 3   # Only 3 per session before taking a break
BREAK_TIME = 180  # 3 minutes break between batches

OUTPUT_FILE = "data/senate/scraped_senators.json"
PROGRESS_FILE = "data/senate/scraping_progress.json"

def log(msg, level="INFO"):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {msg}")

def random_delay():
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    log(f"Waiting {delay:.1f}s (being very respectful)...")
    time.sleep(delay)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"processed": [], "failed": [], "total_scraped": 0}

def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def load_scraped():
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return []

def get_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        ]),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ro;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
    })
    return session

def main():
    log("=" * 60)
    log("ULTRA-RESPECTFUL SENAT.RO SCRAPER")
    log("=" * 60)
    log(f"Settings: {MIN_DELAY}-{MAX_DELAY}s delay, max {BATCH_SIZE}/batch")
    
    # Load progress
    progress = load_progress()
    processed = progress.get("processed", [])
    total_scraped = progress.get("total_scraped", 0)
    log(f"Resume from: {total_scraped} already scraped")
    
    # Load existing scraped data
    scraped = load_scraped()
    
    # Build senator list from vault
    senators = []
    for f in os.listdir('vault/politicians/senators'):
        if f.endswith('.md') and f != 'Index.md':
            with open(f'vault/politicians/senators/{f}', 'r') as fp:
                content = fp.read()
            
            url_match = re.search(r'url:\s*(.+)$', content, re.MULTILINE)
            name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            
            if url_match and name_match:
                name = name_match.group(1).strip()
                if name not in processed:
                    senators.append({
                        "name": name,
                        "url": url_match.group(1).strip()
                    })
    
    log(f"Found {len(senators)} senators to process")
    
    session = get_session()
    session_count = 0
    new_count = 0
    
    for senator in senators[:BATCH_SIZE]:  # Only process BATCH_SIZE
        name = senator["name"]
        url = senator["url"]
        
        log(f"Scraping: {name}")
        
        try:
            response = session.get(url, timeout=30)
            
            if response.status_code == 200:
                html = response.text
                
                # Parse data from HTML
                data = {
                    "name": name,
                    "url": url,
                    "speeches_count": 0,
                    "laws_proposed": 0  # Try different patterns
                }
                
                # Look for activity patterns in the HTML
                # Note: These regex patterns are guesses - actual parsing depends on page structure
                
                # Pattern 1: Look for "luari de cuvant" (speeches)
                speeches = re.findall(r'(\d+)\s*lu?s?r?\s+de\s+cuv', html, re.IGNORECASE)
                if speeches:
                    data["speeches_count"] = int(speeches[0])
                
                # Pattern 2: Look for proiecte de lege (laws)
                laws = re.findall(r'(\d+)\s*proiecte\s+de\s+lege', html, re.IGNORECASE)
                if laws:
                    data["laws_proposed"] = int(laws[0])
                
                scraped.append(data)
                processed.append(name)
                total_scraped += 1
                new_count += 1
                
                log(f"  ✓ Got speeches: {data['speeches_count']}, laws: {data['laws_proposed']}")
                
            else:
                log(f"  ✗ HTTP {response.status_code}")
                
        except Exception as e:
            log(f"  ✗ Error: {str(e)[:50]}")
        
        # Save progress after each
        progress["processed"] = processed
        progress["total_scraped"] = total_scraped
        save_progress(progress)
        
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(scraped, f, indent=2)
        
        # Random delay
        random_delay()
        session_count += 1
    
    log("=" * 60)
    log(f"SESSION COMPLETE: {new_count} senators scraped this session")
    log(f"Total scraped: {total_scraped}")
    log(f"Progress saved. Run again to continue.")
    log("=" * 60)

if __name__ == "__main__":
    main()