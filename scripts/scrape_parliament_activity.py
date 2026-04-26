#!/usr/bin/env python3
"""
Parliament Activity Scraper
=========================
Extracts voting/activity data from cdep.ro and senat.ro

Usage:
    python3 scripts/scrape_parliament_activity.py [--chamber] [--senate] [--limit N]
"""

import os
import re
import json
import time
import random
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from argparse import ArgumentParser

MIN_DELAY = 3
MAX_DELAY = 8
MAX_WORKERS = 3

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]

OUTPUT_FILE = "data/parliament_activity.json"
PROGRESS_FILE = "data/activity_progress.json"


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def random_delay():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


def get_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html",
    })
    return session


def parse_cdep_deputy(html, idm):
    """Parse Chamber of Deputies deputy page"""
    data = {"idm": idm, "chamber": "deputies"}
    
    # Activity counts from main profile page
    patterns = [
        ("proiecte", r'(\d+)\s*proiect[\w]*\s*de\s*lege'),
        ("interpelari", r'(\d+)\s*interpel[\w]*'),
        ("intrebari", r'(\d+)\s*întreb[\w]*'),
        ("motiuni", r'(\d+)\s*moțiun[\w]*'),
        ("declaratii", r'(\d+)\s*declara[\w]*'),
    ]
    
    for key, pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            data[key] = int(match.group(1))
    
    # Get voting records from electronic voting page
    try:
        # Get first page of voting records
        vot_url = f"https://www.cdep.ro/pls/steno/evot2015.mp?idm={idm}&cam=2&leg=2024&pag=1&idl=1"
        vot_response = requests.get(vot_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        
        if vot_response.status_code == 200:
            vot_html = vot_response.text
            
            # Count unique vote dates (each vote = one date in a table row)
            dates = re.findall(r'<tr[^>]*>.*?(\d+\.\d+\.\d{4}).*?</tr>', vot_html, re.DOTALL)
            unique_dates = set(dates)
            data["votes_cast"] = len(unique_dates)
            
            if dates:
                data["last_vote"] = sorted(dates)[-1]
            
            # Count record rows (more accurate)
            vote_rows = len(re.findall(r'<tr[^>]*>.*?<td[^>]*>.*?\d+\.\d+\.\d{4}.*?</td>', vot_html, re.DOTALL))
            if vote_rows:
                data["voting_records"] = vote_rows
    except Exception as e:
        pass
    
    return data


def parse_senator(html, pid):
    """Parse Senate senator page"""
    data = {"id": pid, "chamber": "senate"}
    
    # Activity counts
    patterns = [
        ("proiecte", r'(\d+)\s*proiect[\w]*\s*de\s*lege'),
        ("interpelari", r'(\d+)\s*interpel[\w]*'),
        ("intrebari", r'(\d+)\s*întreb[\w]*'),
    ]
    
    for key, pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            data[key] = int(match.group(1))
    
    # Sessions attended
    sedinte = re.findall(r'(\d+)\s*ședin', html, re.IGNORECASE)
    if sedinte:
        data["sedinte"] = int(sedinte[0])
    
    return data


def build_deputy_urls():
    """Build URLs for deputies"""
    urls = []
    for f in os.listdir('vault/politicians/deputies'):
        if not f.endswith('.md'):
            continue
        with open(f'vault/politicians/deputies/{f}', 'r') as fp:
            content = fp.read()
        
        idm_match = re.search(r'^idm:\s*(\d+)', content, re.MULTILINE)
        url_match = re.search(r'^url:\s*(.+)$', content, re.MULTILINE)
        
        if idm_match and url_match:
            urls.append({
                "idm": idm_match.group(1),
                "url": url_match.group(1),
                "name": f.replace('.md', '')
            })
    return urls


def build_senator_urls():
    """Build URLs for senators"""
    urls = []
    for f in os.listdir('vault/politicians/senators'):
        if not f.endswith('.md') or f == 'Index.md':
            continue
        with open(f'vault/politicians/senators/{f}', 'r') as fp:
            content = fp.read()
        
        # Extract senator ID from URL
        url_match = re.search(r'ParlamentarID=([a-f-]+)', content)
        url_full = re.search(r'^url:\s*(.+)$', content, re.MULTILINE)
        
        if url_match and url_full:
            urls.append({
                "url_id": url_match.group(1),
                "url": url_full.group(1),
                "name": f.replace('.md', '')
            })
    return urls


def scrape_deputy(session, url, idm):
    """Scrape single deputy"""
    try:
        r = session.get(url, timeout=20)
        if r.status_code == 200:
            return parse_cdep_deputy(r.text, idm)
    except Exception as e:
        log(f"Error {idm}: {e}")
    return None


def scrape_senator(session, url, url_id):
    """Scrape single senator"""
    try:
        r = session.get(url, timeout=20)
        if r.status_code == 200:
            return parse_senator(r.text, url_id)
    except Exception as e:
        log(f"Error {url_id}: {e}")
    return None


def main():
    parser = ArgumentParser()
    parser.add_argument("--chamber", action="store_true", help="Scrape Chamber of Deputies")
    parser.add_argument("--senate", action="store_true", help="Scrape Senate")
    parser.add_argument("--limit", type=int, default=0, help="Limit number to scrape")
    args = parser.parse_args()
    
    session = get_session()
    results = {"deputies": [], "senators": []}
    
    if args.chamber or (not args.chamber and not args.senate):
        log("Scraping Chamber of Deputies...")
        urls = build_deputy_urls()
        if args.limit:
            urls = urls[:args.limit]
        
        for i, u in enumerate(urls):
            result = scrape_deputy(session, u["url"], u["idm"])
            if result:
                results["deputies"].append(result)
            if (i + 1) % 10 == 0:
                log(f"  Processed {i+1}/{len(urls)}")
            random_delay()
    
    if args.senate:
        log("Scraping Senate...")
        urls = build_senator_urls()
        if args.limit:
            urls = urls[:args.limit]
        
        for i, u in enumerate(urls):
            result = scrape_senator(session, u["url"], u["url_id"])
            if result:
                results["senators"].append(result)
            if (i + 1) % 10 == 0:
                log(f"  Processed {i+1}/{len(urls)}")
            random_delay()
    
    # Save results
    with open(OUTPUT_FILE, 'w') as fp:
        json.dump(results, fp, indent=2)
    
    log(f"Complete: {len(results['deputies'])} deputies, {len(results['senators'])} senators")


if __name__ == "__main__":
    main()