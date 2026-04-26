#!/usr/bin/env python3
"""
Respectful senat.ro Scraper
========================
A VERY respectful web scraper that avoids getting banned.
Uses multiple strategies:
1. Long delays between requests (5-15 seconds)
2. Random delays to appear human
3. Rotating User-Agent headers
4. Only processes a few senators at a time
5. Saves progress frequently
6. Can resume from中断

CAUTION: Use responsibly. This scraper respects the website's resources.
"""

import os
import re
import json
import time
import random
import requests
from datetime import datetime
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
OUTPUT_FILE = "data/senate/scraped_senators.json"
PROGRESS_FILE = "data/senate/scraping_progress.json"

# RESPECTFUL SETTINGS
MIN_DELAY = 8  # Minimum seconds between requests
MAX_DELAY = 20  # Maximum seconds between requests
MAX_RETRIES = 2   # Maximum retry attempts per page
BATCH_SIZE = 5    # Process only 5 senators before taking a longer break

# Rotating User Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")

def random_delay():
    """Generate random delay to appear more human"""
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    log(f"Waiting {delay:.1f} seconds before next request...")
    time.sleep(delay)

def get_session():
    """Create a respectful session with retry logic"""
    session = requests.Session()
    
    # Add retry logic for network issues
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    return session

def get_headers():
    """Generate respectful headers"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

def load_existing_progress():
    """Load progress if exists"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"processed": [], "failed": [], "last_senator": None}

def save_progress(progress):
    """Save progress frequently"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def scrape_senator_page(session, senator_url):
    """Scrape individual senator page"""
    try:
        response = session.get(
            senator_url, 
            timeout=30,
            headers=get_headers()
        )
        
        if response.status_code == 200:
            return response.text
        elif response.status_code == 404:
            log(f"Page not found: {senator_url}", "WARNING")
            return None
        else:
            log(f"HTTP {response.status_code}: {senator_url}", "WARNING")
            return None
            
    except requests.exceptions.Timeout:
        log(f"Timeout: {senator_url}", "ERROR")
        return None
    except requests.exceptions.RequestException as e:
        log(f"Request error: {e}", "ERROR")
        return None

def parse_senator_page(html, senator_name):
    """Parse senator page for data"""
    data = {
        "name": senator_name,
        "speeches_count": 0,
        "laws_proposed": 0,
        "committees": [],
        "sessions_attended": 0,
    }
    
    if not html:
        return data
    
    # Parse speeches count (this is a guess - actual parsing depends on page structure)
    # Looking for patterns like "XX de luări de cuvânt" in Romanian
    speeches_match = re.search(r'(\d+)\s+de\s+luări\s+de\s+cuvânt', html, re.IGNORECASE)
    if speeches_match:
        data["speeches_count"] = int(speeches_match.group(1))
    
    # Laws proposed - looking for "proiecte de lege"  
    laws_match = re.search(r'(\d+)\s+proiecte\s+de\s+lege', html, re.IGNORECASE)
    if laws_match:
        data["laws_proposed"] = int(laws_match.group(1))
    
    # Sessions - looking for "sedinte"
    sessions_match = re.search(r'(\d+)\s+ședin', html, re.IGNORECASE)
    if sessions_match:
        data["sessions_attended"] = int(sessions_match.group(1))
    
    # Parse committees - looking for "Comisia" sections
    committees = re.findall(r'Comisia.*?<\/a>', html)
    data["committees"] = [c.replace('</a>', '').strip() for c in committees[:10]]
    
    return data

def build_senator_urls():
    """Build URLs for all senators from existing data"""
    urls = []
    
    # Check if we have senator data with URLs
    if os.path.exists("data/senators_2024_full.json"):
        try:
            with open("data/senators_2024_full.json", 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'senators' in data:
                    for senator in data['senators']:
                        url = senator.get('url', '')
                        if url and 'senat.ro' in url:
                            urls.append({
                                'name': senator.get('name', ''),
                                'url': url
                            })
                elif isinstance(data, list):
                    for senator in data:
                        url = senator.get('url', '')
                        if url:
                            urls.append({
                                'name': senator.get('name', ''),
                                'url': url
                            })
        except Exception as e:
            log(f"Error loading senator data: {e}")
    
    # Fallback: Generate URLs from known pattern
    if not urls:
        log("Generating senator URLs from known pattern...")
        for senator_file in os.listdir('vault/politicians/senators'):
            if senator_file.endswith('.md') and senator_file != 'Index.md':
                filepath = f'vault/politicians/senators/{senator_file}'
                with open(filepath, 'r') as f:
                    content = f.read()
                
                url_match = re.search(r'^url:\s*(.+)$', content, re.MULTILINE)
                name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                
                if url_match:
                    urls.append({
                        'name': name_match.group(1).strip() if name_match else senator_file,
                        'url': url_match.group(1).strip()
                    })
    
    return urls

def main():
    log("=" * 60)
    log("RESPECTFUL SENAT.RO SCRAPER - STARTING")
    log("=" * 60)
    log(f"Settings: {MIN_DELAY}-{MAX_DELAY}s delay between requests")
    
    # Load progress
    progress = load_existing_progress()
    processed = progress.get("processed", [])
    failed = progress.get("failed", [])
    
    log(f"Already processed: {len(processed)} senators")
    log(f"Previously failed: {len(failed)}")
    
    # Get session
    session = get_session()
    
    # Get senator URLs
    senator_urls = build_senator_urls()
    log(f"Found {len(senator_urls)} senator URLs")
    
    # Create output
    os.makedirs("data/senate", exist_ok=True)
    
    scraped_data = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                scraped_data = json.load(f)
        except:
            pass
    
    # Count already processed
    already_done = sum(1 for s in scraped_data if s.get('name') in processed)
    log(f"Already scraped: {already_done}")
    
    # Process senators
    batch_count = 0
    new_scraped = 0
    
    for idx, senator_info in enumerate(senator_urls):
        senator_name = senator_info.get('name', '')
        senator_url = senator_info.get('url', '')
        
        # Skip if already processed
        if senator_name in processed:
            continue
        
        # Skip if already scraped
        if any(s.get('name') == senator_name for s in scraped_data):
            continue
        
        # Skip invalid URLs
        if not senator_url or 'senat.ro' not in senator_url:
            continue
        
        log(f"[{idx+1}/{len(senator_urls)}] Processing: {senator_name}")
        
        # Scrape page
        html = scrape_senator_page(session, senator_url)
        
        # Parse data
        data = parse_senator_page(html, senator_name)
        data['source_url'] = senator_url
        
        # Save result
        scraped_data.append(data)
        processed.append(senator_name)
        new_scraped += 1
        
        # Save frequently
        if new_scraped % 3 == 0:
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(scraped_data, f, indent=2)
            progress["processed"] = processed
            progress["failed"] = failed
            save_progress(progress)
            log(f"Progress saved: {new_scraped} new scrapes")
        
        # Take a break every BATCH_SIZE senators
        batch_count += 1
        if batch_count >= BATCH_SIZE:
            log("Taking a 60 second break...", "INFO")
            time.sleep(60)  # Longer break
            batch_count = 0
        else:
            # Random delay
            random_delay()
        
        # Safety limit
        if new_scraped >= 50:
            log("Reached safety limit (50). Saving progress...", "WARNING")
            break
    
    # Final save
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(scraped_data, f, indent=2)
    
    progress["processed"] = processed
    save_progress(progress)
    
    log("=" * 60)
    log(f"COMPLETE: Scraped {new_scraped} new senators")
    log(f"Total processed: {len(processed)}")
    log(f"Data saved to: {OUTPUT_FILE}")
    log("=" * 60)
    
    return scraped_data

if __name__ == "__main__":
    main()