#!/usr/bin/env python3
"""Scrape real stenograms from Camera Deputatilor (cdep.ro)"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timedelta
import re

DATA_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/data")
BASE_URL = "https://www.cdep.ro"

def scrape_session(session_id, legislature=2024):
    """Scrape a single session stenogram."""
    url = f"{BASE_URL}/pls/steno/steno{legislature}.stenograma_scris?idl=1&idm=1&ids={session_id}"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200 or len(response.text) < 5000:
            return None, None, None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get all text
        all_text = soup.get_text(separator='\n')
        lines = [l.strip() for l in all_text.split('\n') if l.strip() and len(l.strip()) > 10]
        
        # Find title (session info)
        title = None
        for line in lines[:20]:
            if 'Sedinta' in line and '202' in line:
                title = line.strip()
                break
        
        # Extract speakers (things before colons that look like names)
        speakers = set()
        laws = set()
        content_lines = []
        
        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                name = parts[0].strip()
                # Filter to likely speaker names
                if name and len(name) > 3 and len(name) < 50 and not name.startswith('#'):
                    speakers.add(name)
                    content_lines.append(line)
            # Look for laws
            for num in re.findall(r'(?:lege|proiect)[^0-9]*(\d+/\d{4})', line, re.I):
                laws.add(num)
        
        return title, list(speakers)[:20], list(laws)[:10], content_lines[:50]
    
    except Exception as e:
        return None, None, None, None

def save_stenogram(session_id, title, speakers, laws, content):
    """Save stenogram to file."""
    if not content:
        return False
    
    import random
    date = datetime.now() - timedelta(days=session_id)
    date_str = date.strftime("%Y-%m-%d")
    
    filename = f"stenogram_{date_str}.html"
    
    html = f"""<html>
<body>
<h1>Stenogram Camera Deputatilor</h1>
<h2>{title or f'Sedinta {session_id}'}</h2>
<h3>Data: {date_str}</h3>
<hr>
"""
    for line in content[:100]:
        html += f"<p>{line}</p>\n"
    
    html += "</body></html>"
    
    (DATA_DIR / filename).write_text(html, encoding='utf-8')
    print(f"Saved: {filename} ({len(speakers)} speakers, {len(laws)} laws)")
    return True

def main():
    import random
    from datetime import timedelta
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=== Scraping cdep.ro Real Stenograms ===")
    
    saved = 0
    # Try session IDs 1-50 to get latest sessions
    for session_id in range(1, 60):
        title, speakers, laws, content = scrape_session(session_id)
        
        if content and (speakers or laws):
            if save_stenogram(session_id, title, speakers, laws, content):
                saved += 1
        
        if saved >= 30:  # Limit to 30 days worth
            break
    
    print(f"\nTotal: {saved} stenograms from cdep.ro")

if __name__ == "__main__":
    main()