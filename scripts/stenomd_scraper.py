#!/usr/bin/env python3
"""
StenoMD - Romanian Parliament Stenogram Scraper v2
Extracts real speeches and debates from cdep.ro
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import re
import json
import time
import random

DATA_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/data")
KG_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/knowledge_graph")
CDEP_BASE = "https://www.cdep.ro"

class StenogramScraper:
    """Extracts real Romanian Parliament stenograms."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        self.mps = set()
        self.laws = set()
        self.debates = []
    
    def log(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def get_session_ids(self, year, max_id=50):
        """Get all session IDs for a year."""
        self.log(f"Finding sessions for {year}...")
        
        session_ids = []
        
        for ids in range(1, max_id + 1):
            url = f"{CDEP_BASE}/pls/steno/steno{year}.stenograma_scris?idl=1&idm=1&ids={ids}&prn=1"
            try:
                r = self.session.get(url, timeout=10)
                if r.status_code == 200 and len(r.text) > 20000:
                    # Check if it has actual content
                    if 'domnul' in r.text.lower() or 'doamna' in r.text.lower():
                        session_ids.append(ids)
                        self.log(f"  Found session ID {ids} with content")
            except:
                pass
            
            if len(session_ids) >= 10:
                break
        
        self.log(f"Found {len(session_ids)} sessions with content")
        return session_ids
    
    def extract_stenogram(self, year, session_id):
        """Extract a full stenogram."""
        url = f"{CDEP_BASE}/pls/steno/steno{year}.stenograma_scris?idl=1&idm=1&ids={session_id}&prn=1"
        
        try:
            r = self.session.get(url, timeout=20)
            if r.status_code != 200:
                return None
        except:
            return None
        
        text = r.text
        
        # Check if has content
        if len(text) < 10000:
            return None
        
        soup = BeautifulSoup(text, 'html.parser')
        
        # Get title
        title = ""
        if soup.title:
            title = soup.title.string or ""
        
        # Extract MP names (Domnul/Doamna patterns)
        mps_found = set()
        names = re.findall(r'(?:Domnul|Doamna)\s+([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț\-]+)+)', text)
        for name in names:
            mps_found.add(name.strip())
        
        # Extract law numbers
        laws_found = set()
        laws = re.findall(r'(?:Legea|Proiectul de lege)\s+(?:nr\.?\s*)?(\d+/\d{4})', text, re.I)
        for law in laws:
            laws_found.add(law)
        
        # Extract actual debate content
        debates = []
        for p in soup.find_all('p'):
            t = p.get_text(strip=True)
            if t and len(t) > 50 and ('domnul' in t.lower() or 'doamna' in t.lower() or 'vot' in t.lower() or 'lege' in t.lower()):
                debates.append(t[:300])
        
        return {
            'year': year,
            'session_id': session_id,
            'title': title,
            'mps': list(mps_found),
            'laws': list(laws_found),
            'debates': debates[:30],
            'url': url,
            'date': datetime.now().strftime("%Y-%m-%d")
        }
    
    def save_to_file(self, data, filename):
        """Save stenogram to HTML file."""
        if not data:
            return False
        
        html = f"""<html>
<head>
<meta charset="UTF-8">
<title>{data['title']}</title>
</head>
<body>
<h1>{data['title']}</h1>
<h2>Deputaţi mentionaţi ({len(data['mps'])}):</h2>
<ul>
"""
        for mp in data['mps']:
            html += f"<li>{mp}</li>\n"
        
        html += f"""</ul>
<h2>Legi mentionate ({len(data['laws'])}):</h2>
<ul>
"""
        for law in data['laws']:
            html += f"<li>Legea {law}</li>\n"
        
        html += """</ul>
<h2>Fragmente din dezbateri:</h2>
<pre>
"""
        for debate in data['debates'][:50]:
            # Escape HTML
            debate_escaped = debate.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html += f"{debate_escaped}\n\n"
        
        html += f"""</pre>
<hr>
<p>Sursa: <a href="{data['url']}">{data['url']}</a></p>
</body>
</html>"""
        
        filepath = DATA_DIR / filename
        filepath.write_text(html, encoding='utf-8')
        
        self.mps.update(data['mps'])
        self.laws.update(data['laws'])
        
        return True
    
    def run(self, years=[2024, 2025, 2026]):
        """Main scraping function."""
        self.log("=== StenoMD Scraper Starting ===")
        
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        total_saved = 0
        
        for year in years:
            self.log(f"\\n=== Processing {year} ===")
            
            # Get session IDs
            session_ids = self.get_session_ids(year, max_id=60)
            
            for session_id in session_ids[:5]:  # Limit to 5 per year
                self.log(f"Extracting session {year}/{session_id}...")
                
                data = self.extract_stenogram(year, session_id)
                
                if data and data['debates']:
                    filename = f"stenogram_{year}_{session_id}.html"
                    if self.save_to_file(data, filename):
                        total_saved += 1
                        self.log(f"  Saved: {filename}")
                        self.log(f"  MPs: {len(data['mps'])}, Laws: {len(data['laws'])}, Debates: {len(data['debates'])}")
                
                time.sleep(random.uniform(1, 2))
            
            if total_saved >= 5:
                break
        
        self.log(f"\\n=== Complete ===")
        self.log(f"Saved: {total_saved} stenograms")
        self.log(f"MPs found: {len(self.mps)}")
        self.log(f"Laws found: {len(self.laws)}")
        
        return {
            'stenograms': total_saved,
            'mps': list(self.mps),
            'laws': list(self.laws)
        }

def main():
    scraper = StenogramScraper()
    stats = scraper.run()
    print("\n" + "="*50)
    print("RESULTS:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()