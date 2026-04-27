#!/usr/bin/env python3
"""
Enhanced parliament scraper with better HTML parsing.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent / '.venv' / 'lib' / 'python3.12' / 'site-packages'))

from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup

BASE_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
VAULT_DIR = BASE_DIR / "vault"
DATA_DIR = BASE_DIR / "data"

class EnhancedParliamentScraper:
    def __init__(self):
        self.page: Optional[Page] = None
        self.deputies_2024 = self.load_deputies()
        
    def load_deputies(self) -> List[Dict]:
        with open(DATA_DIR / "deputies_2024.json") as f:
            data = json.load(f)
            return data.get("deputies", [])
    
    async def start(self):
        p = await async_playwright().start()
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = await context.new_page()
        await self.page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7',
        })
        
    async def stop(self):
        if self.page:
            await self.page.close()
            await self.page.context.browser.close()
    
    async def scrape_cdep_sessions_enhanced(self, max_pages: int = 10) -> List[Dict]:
        """Enhanced scraping using BeautifulSoup parsing"""
        sessions = []
        
        try:
            print("Navigating to cdep.ro stenogram page...")
            await self.page.goto("https://www.cdep.ro/pls/steno/steno.stenograma", timeout=60000)
            await self.page.wait_for_load_state('networkidle')
            
            for page_num in range(1, max_pages + 1):
                print(f"Processing page {page_num}...")
                html = await self.page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find all links containing stenograma?id=
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if 'steno.stenograma?id=' in href:
                        # Extract ID from URL
                        id_match = re.search(r'id=(\d+)', href)
                        if id_match:
                            session_id = id_match.group(1)
                            title = link.get_text(strip=True)
                            
                            if session_id not in [s['id'] for s in sessions]:
                                sessions.append({
                                    'id': session_id,
                                    'title': title[:200],
                                    'source': 'cdep',
                                    'url': f"https://www.cdep.ro{href}" if href.startswith('/') else href,
                                    'page': page_num
                                })
                
                print(f"  Found {len(sessions)} sessions so far")
                
                # Try to go to next page
                if page_num < max_pages:
                    next_link = await self.page.query_selector('a[title="Următoarea"], a[aria-label="Next"]')
                    if next_link:
                        await next_link.click()
                        await self.page.wait_for_timeout(3000)
                    else:
                        # Look for page number links
                        page_links = await self.page.query_selector_all('a.page-link')
                        found_next = False
                        for link in page_links:
                            text = await link.text_content()
                            if text and str(page_num + 1) in text:
                                await link.click()
                                await self.page.wait_for_timeout(3000)
                                found_next = True
                                break
                        if not found_next:
                            print("No more pages found")
                            break
                        
        except Exception as e:
            print(f"Error scraping cdep: {e}")
            
        return sessions
    
    async def scrape_senat_sessions_enhanced(self, max_pages: int = 5) -> List[Dict]:
        """Scrape senate sessions"""
        sessions = []
        
        try:
            print("Navigating to senat.ro stenograme...")
            await self.page.goto("https://www.senat.ro/stenograme.aspx", timeout=60000)
            await self.page.wait_for_load_state('networkidle')
            
            for page_num in range(1, max_pages + 1):
                print(f"Processing senat page {page_num}...")
                html = await self.page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find stenogram links
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if 'stenograme' in href.lower() or 'steno' in href.lower():
                        title = link.get_text(strip=True)
                        if title and len(title) > 5:  # Filter out navigation
                            sessions.append({
                                'id': f"senat_{len(sessions)+1}",
                                'title': title[:200],
                                'source': 'senat',
                                'url': href if href.startswith('http') else f"https://www.senat.ro{href}",
                                'page': page_num
                            })
                
                print(f"  Found {len(sessions)} senate sessions")
                
                # Next page
                if page_num < max_pages:
                    next_btn = await self.page.query_selector('a:has-text("Următoarea"), input[value=">"]')
                    if next_btn:
                        await next_btn.click()
                        await self.page.wait_for_timeout(3000)
                    else:
                        break
                        
        except Exception as e:
            print(f"Error scraping senat: {e}")
            
        return sessions
    
    async def search_deputy_on_cdep(self, deputy_name: str) -> Dict:
        """Search for a deputy's speeches"""
        try:
            encoded_name = deputy_name.replace(' ', '+')
            search_url = f"https://www.cdep.ro/pls/steno/steno.stenograme?cam=1&datei=&numel={encoded_name}"
            await self.page.goto(search_url, timeout=60000)
            await self.page.wait_for_load_state('networkidle')
            
            html = await self.page.content()
            
            # Count results
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for result count
            result_text = soup.get_text()
            speech_count = result_text.lower().count(deputy_name.lower())
            
            # Check for table rows
            rows = soup.find_all('tr')
            speech_rows = [r for r in rows if deputy_name.lower() in r.get_text().lower()]
            
            return {
                'name': deputy_name,
                'speeches_found': len(speech_rows),
                'search_url': search_url,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'name': deputy_name,
                'error': str(e),
                'speeches_found': 0
            }
    
    async def run_comprehensive_scrape(self):
        """Run full scraping workflow"""
        print("="*50)
        print("COMPREHENSIVE PARLIAMENT SCRAPE")
        print("="*50)
        
        results = {
            'scraped_at': datetime.now().isoformat(),
            'cdep_sessions': [],
            'senat_sessions': [],
            'deputy_activity': []
        }
        
        # Scrape cdep sessions
        print("\n1. SCRAPING CDEP SESSIONS")
        cdep_sessions = await self.scrape_cdep_sessions_enhanced(max_pages=10)
        results['cdep_sessions'] = cdep_sessions
        print(f"   Total cdep sessions: {len(cdep_sessions)}")
        
        # Save intermediate
        with open(DATA_DIR / "cdep_sessions_raw.json", 'w') as f:
            json.dump(cdep_sessions, f, indent=2, ensure_ascii=False)
        
        # Scrape senate sessions
        print("\n2. SCRAPING SENATE SESSIONS")
        senat_sessions = await self.scrape_senat_sessions_enhanced(max_pages=5)
        results['senat_sessions'] = senat_sessions
        print(f"   Total senate sessions: {len(senat_sessions)}")
        
        # Scrape deputy activity (sample)
        print("\n3. SCRAPING DEPUTY ACTIVITY")
        activity = []
        sample_deputies = self.deputies_2024[:30]  # First 30
        
        for i, deputy in enumerate(sample_deputies, 1):
            print(f"   Searching {i}/{len(sample_deputies)}: {deputy['name']}")
            act = await self.search_deputy_on_cdep(deputy['name'])
            activity.append(act)
            
            # Delay to avoid rate limiting
            await self.page.wait_for_timeout(1000)
        
        results['deputy_activity'] = activity
        
        # Save results
        output_file = DATA_DIR / "comprehensive_scrape.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*50)
        print("SCRAPE COMPLETE")
        print(f"Sessions saved to: {output_file}")
        print(f"  - CDEP sessions: {len(cdep_sessions)}")
        print(f"  - Senate sessions: {len(senat_sessions)}")
        print(f"  - Deputy activity records: {len(activity)}")
        print("="*50)
        
        return results


async def main():
    scraper = EnhancedParliamentScraper()
    await scraper.start()
    try:
        await scraper.run_comprehensive_scrape()
    finally:
        await scraper.stop()


if __name__ == "__main__":
    import re
    asyncio.run(main())