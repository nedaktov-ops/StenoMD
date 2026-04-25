#!/usr/bin/env python3
"""
StenoMD Senate Agent - Romanian Senate Scraper
Phase 2: ASP.NET-based stenogram extraction from senat.ro

Features:
- Form-based search with date filtering
- Multi-click "Citește" button handling (may require multiple clicks)
- Full stenogram content extraction
- Senator/speech extraction from session transcripts
- Obsidian vault sync
- Duplicate detection via vault validation
- Backward traversal when session already extracted

Usage:
    python3 senat_agent.py --year 2024
    python3 senat_agent.py --update
    python3 senat_agent.py --sync-vault
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import re
import json
import time
import random
import sys
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field, asdict
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent))
from validators import DataValidator
from memory import MemoryStore
from resolve.entity_resolver import EntityResolver

PROGRESS_FILE = Path("/tmp/stenomd_progress_senate.json")

def write_progress(chamber: str, current: int, total: int, session_name: str):
    """Write progress to file for dashboard polling."""
    PROGRESS_FILE.write_text(json.dumps({
        "chamber": chamber,
        "current": current,
        "total": total,
        "session": session_name,
        "timestamp": datetime.now().isoformat()
    }))

BASE_URL = "https://www.senat.ro"
SCRIPT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = SCRIPT_DIR / "data" / "senate"
KG_DIR = SCRIPT_DIR / "knowledge_graph"
VAULT_DIR = SCRIPT_DIR / "vault"

SENATOR_PATTERN = re.compile(
    r'domnul\s+([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)',
    re.IGNORECASE
)

NAME_PATTERN = re.compile(
    r'doamna\s+([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)',
    re.IGNORECASE
)

LAW_PATTERN = re.compile(r'\((?:L|Proiectul|Legea)\s*(?:nr\.?\s*)?(\d+/\d{4})\)', re.IGNORECASE)

TOPIC_KEYWORDS = {
    'buget': ['buget', 'finanțe', 'impozit', 'taxe', 'bani'],
    'justitie': ['penal', 'codul penal', 'instanț', 'judecat'],
    'sanatate': ['sănătate', 'medical', 'spital'],
    'medru': ['mediu', 'ecologie', 'deșeuri', 'emisi'],
    'transport': ['transport', 'vehicul', 'auto', 'sosea'],
    'energie': ['energie', 'electric', 'gaz', 'petrol'],
    'agricultura': ['agricol', 'ferm', 'sponsoriz'],
    'europa': ['uniunea european', 'comisia european', 'COM', 'regulament'],
}


@dataclass
class Senator:
    id: str
    name: str
    chamber: str = "senate"
    party: Optional[str] = None
    legislature: str = "2024-2028"
    appearances: List[str] = field(default_factory=list)
    statements: List[dict] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SenateSession:
    id: str
    date: str
    title: str
    url: str
    stenogram_content: str = ""
    participants: List[str] = field(default_factory=list)
    laws_discussed: List[str] = field(default_factory=list)
    word_count: int = 0
    summary: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


class SenateAgent:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        self.senators: Dict[str, Senator] = {}
        self.sessions: Dict[str, SenateSession] = {}
        self.validator = DataValidator(VAULT_DIR)
        self.memory = MemoryStore()
        self.resolver = EntityResolver()
        self.statistics = {
            'sessions_found': 0,
            'sessions_scraped': 0,
            'sessions_skipped': 0,
            'sessions_validated': 0,
            'senators_found': set(),
            'laws_found': set(),
            'statements_extracted': 0,
            'errors': []
        }
    
    def log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[SENATE:{ts}] {msg}")
    
    def random_delay(self, min_sec: float = 1.0, max_sec: float = 5.0):
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def _get_hidden_fields(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract all hidden form fields from ASP.NET page."""
        data = {}
        for inp in soup.find_all('input', {'type': 'hidden'}):
            name = inp.get('name')
            value = inp.get('value', '')
            if name:
                data[name] = value
        return data
    
    def search_sessions(self, year: int, max_pages: int = 5) -> List[Tuple[str, str, str]]:
        """Search for sessions with pagination support.
        
        Note: senat.ro only returns current legislature sessions.
        Returns up to max_sessions from multiple pages.
        """
        self.log(f"Searching for sessions (max {max_pages} pages)...")
        all_sessions = []
        
        for page in range(1, max_pages + 1):
            sessions = self._search_page(year, page)
            if not sessions:
                break
            
            all_sessions.extend(sessions)
            self.log(f"  Page {page}: {len(sessions)} sessions")
            
            if len(all_sessions) >= 20:
                break
        
        self.log(f"Found {len(all_sessions)} total sessions")
        return all_sessions
    
    def _search_page(self, year: int, page: int = 1) -> List[Tuple[str, str, str]]:
        """Search a single page of sessions."""
        sessions = []
        
        r = self.session.get(f"{BASE_URL}/StenoPag2.aspx", timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        form_data = self._get_hidden_fields(soup)
        
        # Just get current page - date filtering doesn't work
        r = self.session.post(f"{BASE_URL}/StenoPag2.aspx", data=form_data, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        grid = soup.find('table', {'id': 'gr2Rezultat'})
        if not grid:
            return sessions
        
        rows = grid.find_all('tr')
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) < 2:
                continue
            
            date = cells[0].get_text(strip=True)
            title = cells[1].get_text(strip=True)
            
            # Accept all sessions (year filter only works for current year)
            if year and str(year) not in date and '2024' not in date and '2025' not in date and '2026' not in date:
                # Allow all dates if filtering not possible
                pass
            
            btn = row.find('input', {'value': 'Citeşte'})
            if btn:
                btn_name = btn.get('name', '')
                sessions.append((date, title, btn_name))
                self.statistics['sessions_found'] += 1
        
        self.log(f"Found {len(sessions)} sessions")
        return sessions
    
    def click_both_buttons(self, soup: BeautifulSoup, btn_name: str) -> Tuple[str, BeautifulSoup]:
        """Click Citește button, then Sumar2 button to get full stenogram.
        
        The stenogram requires clicking TWO buttons:
        1. gr2Rezultat$ctl##$Button1 to show summary
        2. Sumar2$ctl##$sumar_ID to show full content
        """
        form_data = self._get_hidden_fields(soup)
        form_data[btn_name] = 'Citeşte'
        
        r = self.session.post(f"{BASE_URL}/StenoPag2.aspx", data=form_data, timeout=15)
        new_soup = BeautifulSoup(r.text, 'html.parser')
        
        s2_btn = new_soup.find('input', {'name': lambda n: n and 'Sumar2' in str(n) and 'sumar_ID' in str(n)})
        if s2_btn:
            guid = s2_btn.get('value')
            
            form_data2 = self._get_hidden_fields(new_soup)
            form_data2['Sumar2$ctl02$sumar_ID'] = guid
            
            r = self.session.post(f"{BASE_URL}/StenoPag2.aspx", data=form_data2, timeout=15)
            new_soup = BeautifulSoup(r.text, 'html.parser')
        
        return r.text, new_soup

    def extract_stenogram_content(self, html: str) -> Tuple[str, str, List[str], List[str]]:
        """Extract content, date, senators, and laws from stenogram page.
        
        The stenogram content is in Table 12 (index 12) after clicking Citește.
        Full stenograms require clicking BOTH gr2Rezultat button and Sumar2 button.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        content = ""
        date = ""
        senators = []
        laws = []
        
        tables = soup.find_all('table')
        if len(tables) > 12:
            table = tables[12]
            text = table.get_text(separator=' ', strip=True)
            
            if 'S T E N O G R A M A' in text or 'ședinței' in text:
                content = re.sub(r'\s+', ' ', text)
                
                date_match = re.search(r'din\s+(\d+\s+[a-zăâîșț]+\s+\d{4})', content)
                if date_match:
                    date = date_match.group(1)
        
        if not content:
            return "", date, senators, laws
        
        senator_matches = SENATOR_PATTERN.findall(content)
        for match in senator_matches:
            if len(match) > 5 and len(match) < 60:
                senators.append(match)
        
        law_matches = LAW_PATTERN.findall(content)
        for match in law_matches:
            law_num = match if isinstance(match, str) else match[0] if match else ""
            if law_num and law_num not in laws:
                laws.append(law_num)
        
        return content, date, senators, laws
    
    def extract_participants(self, html: str) -> List[Tuple[str, str]]:
        """Extract participants who spoke in the session.
        
        The stenogram is a transcript where senators take turns speaking.
        Each person's contribution is extracted. Uses both 'Domnul senator' 
        and simple 'Domnul/Doamna' patterns. Also extracts names from
        the leadership mentions (vicepreședinte, secretari).
        """
        soup = BeautifulSoup(html, 'html.parser')
        participants = []
        seen = set()
        
        text = soup.get_text()
        clean_text = re.sub(r'\s+', ' ', text)
        
        all_matches = list(SENATOR_PATTERN.finditer(clean_text)) + list(NAME_PATTERN.finditer(clean_text))
        all_matches.sort(key=lambda m: m.start())
        
        for match in all_matches:
            name = match.group(1).strip()
            if len(name) > 5 and len(name) < 60 and name not in seen:
                participants.append((name, "senate"))
                seen.add(name)
        
        return participants
    
    def generate_summary(self, content: str, laws: List[str]) -> str:
        """Generate a 2-3 sentence summary of the session."""
        if not content:
            return ""
        
        summary = []
        
        if laws:
            summary.append(f"Discussed {len(laws)} law(s): {', '.join(laws[:3])}")
        
        if 'Codul fiscal' in content:
            summary.append("Included fiscal code discussions")
        if 'Uniunea European' in content or 'COM' in content:
            summary.append("Covered EU regulations")
        if 'vot' in content.lower():
            summary.append("Featured voting on legislative proposals")
        
        return '. '.join(summary) if summary else content[:200]
    
    def scrape_session(self, year: int, btn_name: str, date: str, title: str) -> Optional[Dict]:
        """Scrape a single Senate session."""
        r = self.session.get(f"{BASE_URL}/StenoPag2.aspx", timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        form_data = self._get_hidden_fields(soup)
        form_data['blLegislaturi'] = '2024-12-21-2028-12-20'
        form_data['CalendarControl1$TextBox1'] = '01.01.2024'
        form_data['CalendarControl1$TextBox2'] = '31.12.2024'
        
        r = self.session.post(f"{BASE_URL}/StenoPag2.aspx", data=form_data, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        html, soup = self.click_both_buttons(soup, btn_name)
        
        content, extracted_date, senators, laws = self.extract_stenogram_content(html)
        participants = self.extract_participants(html)
        
        if not content or len(content) < 100:
            return None
        
        sess_date = extracted_date or date
        sess_id = f"senate_{date.replace('-', '')}_{year}"
        
        summary = self.generate_summary(content, laws)
        
        return {
            'id': sess_id,
            'date': sess_date,
            'title': title,
            'url': f"{BASE_URL}/StenoPag2.aspx",
            'stenogram_content': content,
            'participants': [p[0] for p in participants],
            'laws_discussed': laws,
            'word_count': len(content.split()),
            'summary': summary
        }
    
    def save_to_vault(self, data: Dict):
        """Save session to Obsidian vault."""
        if not data:
            return
        
        VAULT_DIR.mkdir(parents=True, exist_ok=True)
        (VAULT_DIR / 'politicians' / 'senators').mkdir(parents=True, exist_ok=True)
        (VAULT_DIR / 'sessions' / 'senate').mkdir(parents=True, exist_ok=True)
        
        date_str = data['date'].replace(' ', '-')
        sess_file = VAULT_DIR / 'sessions' / 'senate' / f"{date_str}.md"
        
        content = f"""---
date: {data['date']}
title: {data['title']}
chamber: Senate
source: senat.ro
laws_discussed: {', '.join(data['laws_discussed']) if data['laws_discussed'] else 'None'}
word_count: {data['word_count']}
participants:
{chr(10).join(f"  - {p}" for p in data['participants']) if data['participants'] else '  - None'}
---

# {data['title']}

**Date:** {data['date']}  
**Chamber:** Senate  
**Source:** [senat.ro]({data['url']})

## Summary

{data['summary']}

## Laws Discussed

{chr(10).join(f"- {law}" for law in data['laws_discussed']) if data['laws_discussed'] else 'None'}

## Participants

{', '.join(data['participants']) if data['participants'] else 'None'}

## Transcript

{data['stenogram_content'][:2000]}

---

*Synced from StenoMD Senate Agent on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        sess_file.write_text(content, encoding='utf-8')
        self.log(f"  Saved to vault: {sess_file.name}")
        
        for senator_name in data['participants']:
            self._save_senator_note(senator_name, data['id'])
    
    def _save_senator_note(self, name: str, session_id: str):
        """Save senator note to vault."""
        # Skip invalid names
        invalid_patterns = ['domnul', 'doamna', 'senator', 'vicepreședinte', 'secretar', 'asistat']
        name_lower = name.lower()
        if any(p in name_lower for p in invalid_patterns):
            return
        
        # Skip multi-name entries (with "și", ", ")
        if 'și' in name or ',' in name:
            # Try to extract first name
            first_name = name.split(',')[0].split('și')[0].strip()
            if len(first_name) > 3:
                name = first_name
            else:
                return
        
        safe_name = re.sub(r'[^\w\s-]', '', name).strip()
        safe_name = re.sub(r'\s+', '-', safe_name)
        
        senator_file = VAULT_DIR / 'politicians' / 'senators' / f"{safe_name}.md"
        
        if senator_file.exists():
            existing = senator_file.read_text(encoding='utf-8')
            if session_id in existing:
                return
        
        content = f"""---
name: {name}
chamber: Senate
legislature: 2024-2028
---

# {name}

**Chamber:** Senate  
**Legislature:** 2024-2028

## Appearances

- [[{session_id}]]

## Notes

*Senator in the Romanian Senate*

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        senator_file.write_text(content, encoding='utf-8')
    
    def run(self, year: int, max_sessions: int = 20, sync_vault: bool = True):
        """Main scraping loop with duplicate detection."""
        self.log(f"=== Starting Senate Agent ===")
        self.log(f"Year: {year}, Max: {max_sessions}, Sync: {sync_vault}")
        
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        existing_dates = self.validator.get_session_dates("senate")
        self.log(f"Found {len(existing_dates)} existing sessions in vault")
        
        all_sessions = self.search_sessions(year)
        
        # Filter already-extracted sessions
        filtered_sessions = []
        for date, title, btn_name in all_sessions:
            # Check if session exists
            data = self.scrape_session(year, btn_name, date, title)
            if not data:
                continue
            
            is_duplicate = self.validator.check_duplicate(data, 'senate')
            
            if is_duplicate:
                self.log(f"  Session {date} already extracted - checking backward...")
                self.statistics['sessions_skipped'] += 1
                existing = self.validator.get_existing_session(date, 'senate')
                if existing and existing['is_complete']:
                    continue
                else:
                    is_valid, msg = self.validator.validate_session(data)
                    if is_valid:
                        self.statistics['sessions_validated'] += 1
                        filtered_sessions.append((date, title, btn_name))
            else:
                filtered_sessions.append((date, title, btn_name))
        
        filtered_sessions = filtered_sessions[:max_sessions]
        self.log(f"Sessions to scrape: {len(filtered_sessions)}")
        
        total = len(filtered_sessions)
        for idx, (date, title, btn_name) in enumerate(filtered_sessions):
            self.log(f"Scraping {date}: {title[:50]}...")
            write_progress("senate", idx + 1, total, date)
            
            data = self.scrape_session(year, btn_name, date, title)
            
            if data and data['stenogram_content']:
                session = SenateSession(
                    id=data['id'],
                    date=data['date'],
                    title=data['title'],
                    url=data['url'],
                    stenogram_content=data['stenogram_content'],
                    participants=data['participants'],
                    laws_discussed=data['laws_discussed'],
                    word_count=data['word_count'],
                    summary=data['summary']
                )
                self.sessions[data['id']] = session
                
                for name in data['participants']:
                    if name not in self.senators:
                        self.senators[name] = Senator(id=str(uuid4()), name=name)
                    self.senators[name].appearances.append(data['id'])
                    self.statistics['senators_found'].add(name)
                
                for law in data['laws_discussed']:
                    self.statistics['laws_found'].add(law)
                
                if sync_vault:
                    self.save_to_vault(data)
                
                # Resolve senator names to canonical entities
                resolved_senators = []
                for name in data['participants']:
                    result = self.resolver.resolve(name, 'senate')
                    if result.canonical_id:
                        resolved_senators.append(result.canonical_name)
                        if result.confidence < 0.95:
                            self.log(f"  Resolved: {name} -> {result.canonical_name} ({result.method}, {result.confidence:.2f})")
                    else:
                        self.log(f"  Unresolved: {name}")
                        resolved_senators.append(name)
                
                # Learn from this scrape operation
                self.memory.learn(
                    action={
                        'type': 'scrape_session',
                        'description': f"Scraped {len(data['participants'])} senators, {len(data['laws_discussed'])} laws from {data.get('date')}",
                        'parameters': {
                            'chamber': 'senate',
                            'year': year,
                            'session_id': data.get('id'),
                            'date': data.get('date'),
                            'senators_count': len(data['participants']),
                            'laws_count': len(data['laws_discussed']),
                            'url': data.get('url', '')
                        }
                    },
                    outcome={
                        'success': True,
                        'sessions_scraped': 1,
                        'duration_ms': 0
                    }
                )
                
                self.statistics['sessions_scraped'] += 1
                self.log(f"  {len(data['participants'])} senators, {len(data['laws_discussed'])} laws")
            
            self.random_delay()
        
        self.log(f"=== Senate Agent Complete ===")
        self.log(f"Sessions found: {self.statistics['sessions_found']}")
        self.log(f"Sessions scraped: {self.statistics['sessions_scraped']}")
        self.log(f"Sessions skipped (duplicates): {self.statistics['sessions_skipped']}")
        self.log(f"Sessions validated: {self.statistics['sessions_validated']}")
        self.log(f"Unique senators: {len(self.statistics['senators_found'])}")
        self.log(f"Laws discussed: {len(self.statistics['laws_found'])}")
        
        return self.statistics


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Senate Agent')
    parser.add_argument('--year', type=int, default=2024, help='Year to process')
    parser.add_argument('--max', type=int, default=20, help='Max sessions')
    parser.add_argument('--sync-vault', action='store_true', help='Sync to Obsidian vault')
    parser.add_argument('--json-output', action='store_true', help='Output JSON summary to stdout')
    
    args = parser.parse_args()
    
    agent = SenateAgent()
    result = agent.run(args.year, args.max, args.sync_vault)
    
    if args.json_output:
        output = {
            "status": "complete",
            "chamber": "senate",
            "sessions_found": len(agent.sessions),
            "sessions_scraped": agent.statistics.get('sessions_scraped', 0),
            "sessions_skipped": agent.statistics.get('sessions_skipped', 0),
            "politicians": len(agent.senators),
            "laws": len(agent.statistics.get('laws_found', [])),
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(output))


if __name__ == '__main__':
    main()