#!/usr/bin/env python3
"""
StenoMD Enhanced CDEP Agent - Camera Deputatilor Scraper
Phase 1: Full implementation with enhanced entity extraction

Features:
- Full MP name extraction with Romanian diacritics
- Party affiliation detection
- Statement extraction per MP per session
- Session summary generation
- Improved session title parsing
- Enhanced law number detection
- Duplicate detection via vault validation
- Backward traversal when session already extracted

Usage:
    python3 cdep_agent.py --update --years 2024,2025,2026
    python3 cdep_agent.py --backfill --year 2020
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
from uuid import uuid4
import argparse

PROGRESS_FILE = Path("/tmp/stenomd_progress.json")

def write_progress(chamber: str, current: int, total: int, session_name: str):
    """Write progress to file for dashboard polling."""
    PROGRESS_FILE.write_text(json.dumps({
        "chamber": chamber,
        "current": current,
        "total": total,
        "session": session_name,
        "timestamp": datetime.now().isoformat()
    }))
from dataclasses import dataclass, field, asdict
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent))
from validators import DataValidator

# Configuration
BASE_URL = "https://www.cdep.ro"
SCRIPT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = SCRIPT_DIR / "data" / "cdep"
KG_DIR = SCRIPT_DIR / "knowledge_graph"
VAULT_DIR = SCRIPT_DIR / "vault"

# Enhanced regex patterns for Romanian diacritics
# Pattern for extracting names from HTML with font tags (the actual format in cdep.ro)
MP_NAME_PATTERN_HTML = re.compile(
    r'<font\s+color="#0000FF">(Domnul|Doamna)\s+([A-ZĂÂÎȘȚ][a-zăâîșț\-]+(?:\s+[A-ZĂÂÎȘȚ]\.?)?(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)</font>',
    re.IGNORECASE
)

# Simple pattern for standalone text
MP_NAME_PATTERN = re.compile(
    r'(?:Domnul|Doamna)\s+([A-ZĂÂÎȘȚ][a-zăâîșț\-]+(?:\s+[A-ZĂÂÎȘȚ]\.?)?(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)',
    re.IGNORECASE
)

# Party affiliation patterns
PARTY_PATTERNS = {
    'PSD': ['PSD', 'Partidul Social Democrat', 'social-democrat'],
    'PNL': ['PNL', 'Partidul Național Liberal', 'național liberal'],
    'USR': ['USR', 'Uniunea Salvați România', 'salvați românia'],
    'AUR': ['AUR', 'Alternativa pentru Demnitate', 'alternativa pentru'],
    'UDMR': ['UDMR', 'Uniunea Democrată Maghiară', 'democrată maghiară'],
    'SOS': ['SOS', 'SOS România', 'SOS Romania'],
    'POT': ['POT', 'Partidul Oamenilor Tineri', 'oamenilor tineri'],
}

# Law number patterns
LAW_PATTERNS = [
    r'(?:Legea|Proiectul de lege|Lege|PL)\s*(?:nr\.?\s*)?(\d+/\d{4})',
    r'Legislația\s+(?:nr\.?\s*)?(\d+/\d{4})',
    r'Dispozițiilor\s+(?:nr\.?\s*)?(\d+/\d{4})',
]

# Session title patterns
SESSION_TITLE_PATTERNS = [
    r'Sedint[ăa]\s+(?:Camerei\s+Deputaților\s+din\s+)?(.+?)(?:\s+dintea|\s+din\s+|\s+la|\s+\d{4})',
    r'Sedint[ăa]\s+Comun[ăa]\s+(?:a\s+)?(.+?)(?:\s+și\s+|\s+din\s+|\s+\d{4})',
    r'Sedint[ăa]\s+dinspre\s+(.+?)(?:\s+din\s+|\s+\d{4})',
]

# Topic keywords for debate classification
TOPIC_KEYWORDS = {
    'economie': ['economie', 'economic', 'buget', 'finanțe', 'bani', 'investiții', 'PIB'],
    'sanatate': ['sănătate', 'medical', 'spital', 'doctor', 'pacienți', 'vaccin'],
    'educatie': ['educație', 'școală', 'universitate', 'invățământ', 'studenți'],
    'justitie': ['justiție', 'judicial', 'instanță', 'judecătorie', 'penal'],
    'aparare': ['apărare', 'armată', 'militar', 'NATO', 'securitate'],
    'mediu': ['mediu', 'climă', 'poluare', 'verde', 'ecologie'],
    'social': ['social', 'pensii', 'alocații', 'beneficii', 'asistență'],
    'europa': ['european', 'UE', 'Bruxelles', 'euro', 'comisar'],
}


@dataclass
class Statement:
    """A single statement/speech by an MP during a session."""
    speaker: str
    session_id: str
    date: str
    text_excerpt: str
    word_count: int
    topics: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Person:
    """A parliament member (MP or Senator)."""
    id: str
    name: str
    chamber: str  # 'deputies' or 'senate' or 'both'
    party: Optional[str] = None
    legislature: str = "2024-2028"
    constituency: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    committees: List[str] = field(default_factory=list)
    appearances: List[str] = field(default_factory=list)
    statements: List[Statement] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['statements'] = [s.to_dict() if hasattr(s, 'to_dict') else s for s in data['statements']]
        return data


@dataclass
class Session:
    """A parliamentary session."""
    id: str
    date: str
    chamber: str
    title: str
    url: str
    participants: List[str] = field(default_factory=list)
    laws_discussed: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    word_count: int = 0
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Law:
    """A law or bill discussed in parliament."""
    id: str
    number: str
    title: Optional[str] = None
    status: str = "discussed"
    sponsors: List[str] = field(default_factory=list)
    discussions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)


class EnhancedCDEPAgent:
    """Enhanced AI Agent for scraping Camera Deputatilor stenograms."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        self.persons: Dict[str, Person] = {}
        self.sessions: Dict[str, Session] = {}
        self.laws: Dict[str, Law] = {}
        self.validator = DataValidator(VAULT_DIR)
        self.statistics = {
            'sessions_found': 0,
            'sessions_scraped': 0,
            'sessions_skipped': 0,
            'sessions_validated': 0,
            'mps_found': set(),
            'laws_found': set(),
            'statements_extracted': 0,
            'errors': []
        }
    
    def log(self, msg: str):
        """Log message with timestamp."""
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[CDEP:{ts}] {msg}")
    
    def random_delay(self, min_sec: float = 1.0, max_sec: float = 5.0):
        """Random delay to avoid rate limiting."""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def get_session_ids(self, year: int, max_id: int = 200) -> List[int]:
        """Discover all session IDs for a given year."""
        self.log(f"Discovering sessions for {year}...")
        session_ids = []
        
        for ids in range(1, max_id + 1):
            url = f"{BASE_URL}/pls/steno/steno{year}.stenograma_scris?idl=1&idm=1&ids={ids}&prn=1"
            
            try:
                r = self.session.get(url, timeout=15)
                if r.status_code == 200 and len(r.text) > 20000:
                    # Check if it has actual debate content
                    if 'domnul' in r.text.lower() or 'doamna' in r.text.lower():
                        session_ids.append(ids)
                        self.statistics['sessions_found'] += 1
                        self.log(f"  Found session ID {ids} with content")
            except Exception as e:
                self.statistics['errors'].append(f"ID {ids}: {str(e)}")
            
            # Random delay
            if ids % 10 == 0:
                self.random_delay()
            
            # Stop early if we have enough
            if len(session_ids) >= 20 and ids > 50:
                break
        
        self.log(f"Discovered {len(session_ids)} sessions for {year}")
        return session_ids
    
    def extract_title(self, html: str) -> str:
        """Extract session title from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        if soup.title:
            title = soup.title.string or ""
            # Clean up title
            title = re.sub(r'\s+', ' ', title).strip()
            return title
        
        return f"Session {datetime.now().strftime('%Y-%m-%d')}"
    
    def extract_date_from_title(self, title: str) -> Optional[str]:
        """Extract date from session title."""
        months_ro = {
            'ianuarie': '01', 'februarie': '02', 'martie': '03', 'aprilie': '04',
            'mai': '05', 'iunie': '06', 'iulie': '07', 'august': '08',
            'septembrie': '09', 'octombrie': '10', 'noiembrie': '11', 'decembrie': '12'
        }
        
        # Try YYYY-MM-DD format first
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', title)
        if match and len(match.groups()) == 3:
            return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        
        # Try Romanian format: "5 noiembrie 2024" or "din 5 noiembrie 2024"
        match = re.search(r'(?:din\s+)?(\d{1,2})\s+(noiembrie|decembrie|ianuarie|februarie|martie|aprilie|mai|iunie|iulie|august|septembrie|octombrie)\s+(\d{4})?', title, re.I)
        if match:
            day = match.group(1)
            month_name = match.group(2).lower()
            year = match.group(3) if match.group(3) else "2024"
            if month_name in months_ro:
                return f"{year}-{months_ro[month_name]}-{day.zfill(2)}"
        
        return None
    
    def extract_persons(self, html: str, session_id: str) -> List[Tuple[str, str]]:
        """Extract all MPs from stenogram with party affiliation."""
        persons = []
        
        # Find all MP names from HTML structure
        for match in MP_NAME_PATTERN_HTML.finditer(html):
            title = match.group(1)  # Domnul or Doamna
            full_name = match.group(2).strip()
            if len(full_name) > 5 and len(full_name) < 60:
                persons.append((full_name, session_id))
                self.statistics['mps_found'].add(full_name)
        
        return persons
    
    def detect_party(self, text: str, speaker: str) -> Optional[str]:
        """Detect party affiliation from context around speaker name."""
        # Find speaker in text
        idx = text.find(speaker)
        if idx == -1:
            return None
        
        # Get context around speaker (500 chars before and after)
        start = max(0, idx - 500)
        end = min(len(text), idx + 500)
        context = text[start:end]
        
        # Look for party mentions
        for party, keywords in PARTY_PATTERNS.items():
            for keyword in keywords:
                if keyword.lower() in context.lower():
                    return party
        
        return None
    
    def extract_statements(self, html: str, session_id: str, date: str) -> List[Statement]:
        """Extract individual statements/speeches from session."""
        statements = []
        
        # Parse HTML structure - each speech is in a table row
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all rows with speeches (they have valign="top" and the speaker link)
        for row in soup.find_all('tr', valign='top'):
            # Find the speaker name
            name_match = MP_NAME_PATTERN_HTML.search(str(row))
            if not name_match:
                continue
                
            speaker = name_match.group(2).strip()
            
            # Get the speech content - it's in the middle cell (2nd td)
            cells = row.find_all('td')
            if len(cells) < 2:
                continue
            
            speech_cell = cells[1]
            
            # Remove the B tag and speaker link, keep the speech paragraphs
            speech_html = str(speech_cell)
            
            # Remove speaker tag and everything up to and including </B>
            speech_html = re.sub(r'<B>.*?</B>\s*:?\s*', '', speech_html, flags=re.DOTALL)
            
            # Convert HTML to text
            speech_soup = BeautifulSoup(speech_html, 'html.parser')
            speech_text = speech_soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            speech_text = re.sub(r'\s+', ' ', speech_text).strip()
            
            if len(speech_text) < 20:
                continue
            
            # Detect topics
            topics = []
            for topic, keywords in TOPIC_KEYWORDS.items():
                if any(kw.lower() in speech_text.lower() for kw in keywords):
                    topics.append(topic)
            
            # Get excerpt (first 500 chars, removing speaker name)
            excerpt = speech_text[:500]
            if len(speech_text) > 500:
                excerpt = excerpt.rsplit(' ', 1)[0] + '...'
            
            # Remove speaker name prefix if still present
            if excerpt.startswith(speaker):
                excerpt = excerpt[len(speaker):].strip()
                if excerpt.startswith(':'):
                    excerpt = excerpt[1:].strip()
            
            statement = Statement(
                speaker=speaker,
                session_id=session_id,
                date=date,
                text_excerpt=excerpt,
                word_count=len(speech_text.split()),
                topics=topics
            )
            statements.append(statement)
            self.statistics['statements_extracted'] += 1
        
        return statements
    
    def extract_laws(self, html: str) -> List[str]:
        """Extract all law numbers from stenogram."""
        laws = []
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        for pattern in LAW_PATTERNS:
            for match in re.finditer(pattern, text, re.I):
                law_num = match.group(1)
                if law_num not in laws:
                    laws.append(law_num)
                    self.statistics['laws_found'].add(law_num)
        
        return laws
    
    def generate_summary(self, html: str, session_id: str, date: str) -> str:
        """Generate a 2-3 sentence summary of the session."""
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        # Get first few statements
        statements = self.extract_statements(html, session_id, date)
        
        if not statements:
            return f"Session {session_id} from {date}"
        
        # Generate summary from first 3 statements
        summary_parts = []
        for stmt in statements[:3]:
            # First 100 chars of each statement
            excerpt = stmt.text_excerpt[:100].strip()
            if excerpt:
                summary_parts.append(f"{stmt.speaker}: {excerpt}...")
        
        if summary_parts:
            return ' '.join(summary_parts[:2])
        
        return f"Session {session_id} from {date}"
    
    def scrape_session(self, year: int, session_id: int) -> Optional[Dict]:
        """Scrape a single session."""
        url = f"{BASE_URL}/pls/steno/steno{year}.stenograma_scris?idl=1&idm=1&ids={session_id}&prn=1"
        
        try:
            r = self.session.get(url, timeout=20)
            if r.status_code != 200:
                return None
            
            html = r.text
            if len(html) < 20000:
                return None
            
            # Extract data
            title = self.extract_title(html)
            date = self.extract_date_from_title(title) or datetime.now().strftime("%Y-%m-%d")
            
            # Generate session ID
            sess_id = f"session_{year}_{session_id}"
            
            # Extract persons
            persons = self.extract_persons(html, sess_id)
            
            # Extract statements
            statements = self.extract_statements(html, sess_id, date)
            
            # Extract laws
            laws = self.extract_laws(html)
            
            # Generate summary
            summary = self.generate_summary(html, sess_id, date)
            
            return {
                'id': sess_id,
                'year': year,
                'session_id': session_id,
                'title': title,
                'date': date,
                'url': url,
                'persons': persons,
                'statements': statements,
                'laws': laws,
                'summary': summary,
                'html': html
            }
            
        except Exception as e:
            self.statistics['errors'].append(f"Session {session_id}: {str(e)}")
            return None
    
    def save_stenogram(self, data: Dict):
        """Save stenogram HTML to file."""
        if not data:
            return
        
        filename = f"stenogram_{data['year']}_{data['session_id']}.html"
        filepath = DATA_DIR / filename
        
        # Only save if not exists
        if not filepath.exists():
            filepath.write_text(data['html'], encoding='utf-8')
    
    def _save_session_to_vault(self, data: Dict):
        """Save session to Obsidian vault."""
        if not data:
            return
        
        VAULT_DIR.mkdir(parents=True, exist_ok=True)
        (VAULT_DIR / 'sessions' / 'deputies').mkdir(parents=True, exist_ok=True)
        
        # Calculate word count from HTML
        word_count = 0
        if data.get('html'):
            soup = BeautifulSoup(data['html'], 'html.parser')
            word_count = len(soup.get_text().split())
        
        # Generate filename from date - use extracted date, not current date
        date_str = data['date']
        sess_file = VAULT_DIR / 'sessions' / 'deputies' / f"{date_str}.md"
        
        # Build markdown content
        participants_list = '\n'.join(f"  - {p[0]}" for p in data['persons'])
        laws_list = '\n'.join(f"- {law}" for law in data['laws']) if data['laws'] else 'None'
        
        content = f"""---
date: {data['date']}
title: {data['title']}
chamber: deputies
source: cdep.ro
url: {data['url']}
word_count: {word_count}
laws_discussed: {', '.join(data['laws']) if data['laws'] else 'None'}
participants:
{participants_list}
---

# {data['title']}

**Date:** {data['date']}  
**Chamber:** Chamber of Deputies  
**Source:** [cdep.ro]({data['url']})

## Summary

{data['summary']}

## Laws Discussed

{laws_list}

## Participants

{', '.join([p[0] for p in data['persons']])}

---

*Synced from StenoMD CDEP Agent on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        sess_file.write_text(content, encoding='utf-8')
        self.log(f"  Saved to vault: {sess_file.name}")
        
        # Also save MP notes
        for name, sess_id in data['persons']:
            self._save_mp_note(name, sess_id, data['date'])
    
    def _save_mp_note(self, name: str, session_id: str, date: str):
        """Save MP profile note to vault."""
        DEPUTIES_DIR = VAULT_DIR / 'politicians' / 'deputies'
        DEPUTIES_DIR.mkdir(parents=True, exist_ok=True)
        
        safe_name = re.sub(r'[^\w\s-]', '', name).strip()
        safe_name = re.sub(r'\s+', '-', safe_name)
        mp_file = DEPUTIES_DIR / f"{safe_name}.md"
        
        if mp_file.exists():
            existing = mp_file.read_text(encoding='utf-8')
            if f"[[{session_id}]]" in existing or session_id in existing:
                return
        
        # Create or update MP note
        existing_content = ""
        if mp_file.exists():
            existing_content = mp_file.read_text(encoding='utf-8')
        
        new_entry = f"- [[{session_id}]] ({date})"
        
        if new_entry not in existing_content:
            if "## Appearances" in existing_content:
                existing_content = existing_content.replace(
                    "## Appearances",
                    f"## Appearances\n\n{new_entry}"
                )
            else:
                existing_content += f"\n\n## Appearances\n\n{new_entry}\n"
            mp_file.write_text(existing_content, encoding='utf-8')
    
    def update_knowledge_graph(self):
        """Save updated knowledge graph."""
        kg_data = {
            'metadata': {
                'version': '2.0',
                'last_updated': datetime.now().isoformat(),
                'sources': ['cdep.ro'],
                'legislatures': ['2024-2028']
            },
            'persons': [],
            'sessions': [],
            'laws': []
        }
        
        # Convert persons to dict
        for person in self.persons.values():
            kg_data['persons'].append(person.to_dict())
        
        # Convert sessions to dict
        for session in self.sessions.values():
            kg_data['sessions'].append(session.to_dict())
        
        # Convert laws to dict
        for law in self.laws.values():
            kg_data['laws'].append(law.to_dict())
        
        # Save
        kg_file = KG_DIR / 'entities.json'
        with open(kg_file, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, indent=2, ensure_ascii=False)
        
        self.log(f"Knowledge graph saved: {len(self.persons)} MPs, {len(self.sessions)} sessions, {len(self.laws)} laws")
    
    def run(self, years: List[int], max_id: int = 200):
        """Main scraping loop with duplicate detection."""
        self.log(f"=== Starting Enhanced CDEP Agent ===")
        self.log(f"Years: {years}, Max ID: {max_id}")
        
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        existing_dates = self.validator.get_session_dates("deputies")
        self.log(f"Found {len(existing_dates)} existing sessions in vault")
        
        all_session_ids = []
        
        # Discover all sessions across years
        for year in years:
            session_ids = self.get_session_ids(year, max_id)
            
            # Filter out already-extracted sessions
            filtered = []
            for sid in session_ids:
                data = self.scrape_session(year, sid)
                if not data:
                    continue
                    
                date = data.get('date', '')
                is_duplicate = self.validator.check_duplicate(data, 'deputies')
                
                if is_duplicate:
                    self.log(f"  Session {sid} ({date}) already extracted - checking backward...")
                    self.statistics['sessions_skipped'] += 1
                    # Continue to check if this data is better than existing
                    existing = self.validator.get_existing_session(date, 'deputies')
                    if existing and existing['is_complete']:
                        # Already have complete data, skip this session
                        continue
                    else:
                        # Existing data incomplete, validate this one
                        is_valid, msg = self.validator.validate_session(data)
                        if is_valid:
                            self.statistics['sessions_validated'] += 1
                            filtered.append(sid)
                else:
                    filtered.append(sid)
            
            all_session_ids.extend([(year, sid) for sid in filtered])
        
        self.log(f"Total new sessions to scrape: {len(all_session_ids)}")
        
        # Scrape each session
        total_sessions = len(all_session_ids)
        for idx, (year, session_id) in enumerate(all_session_ids):
            self.log(f"Scraping {year}/{session_id}...")
            write_progress("cdep", idx + 1, total_sessions, f"{year}/{session_id}")
            
            data = self.scrape_session(year, session_id)
            
            if data and data['persons']:
                # Save HTML
                self.save_stenogram(data)
                
                # Create session
                session = Session(
                    id=data['id'],
                    date=data['date'],
                    chamber='deputies',
                    title=data['title'],
                    url=data['url'],
                    participants=[p[0] for p in data['persons']],
                    laws_discussed=data['laws'],
                    summary=data['summary']
                )
                self.sessions[data['id']] = session
                
                # Create/update persons
                for name, sess_id in data['persons']:
                    if name not in self.persons:
                        self.persons[name] = Person(
                            id=str(uuid4()),
                            name=name,
                            chamber='deputies'
                        )
                    self.persons[name].appearances.append(sess_id)
                
                # Create/update laws
                for law_num in data['laws']:
                    if law_num not in self.laws:
                        self.laws[law_num] = Law(
                            id=f"law_{law_num.replace('/', '_')}",
                            number=law_num
                        )
                    self.laws[law_num].discussions.append(data['id'])
                
                # Save session to vault
                self._save_session_to_vault(data)
                
                self.statistics['sessions_scraped'] += 1
                
                self.log(f"  {data['title'][:50]}...")
                self.log(f"  MPs: {len(data['persons'])}, Laws: {len(data['laws'])}")
            
            # Random delay between requests
            self.random_delay()
            
            # Progress report every 10 sessions
            if self.statistics['sessions_scraped'] % 10 == 0:
                self.log(f"Progress: {self.statistics['sessions_scraped']} sessions scraped")
        
        # Save knowledge graph
        self.update_knowledge_graph()
        
        # Final statistics
        self.log(f"=== Scraping Complete ===")
        self.log(f"Statistics:")
        self.log(f"  Sessions found: {self.statistics['sessions_found']}")
        self.log(f"  Sessions scraped: {self.statistics['sessions_scraped']}")
        self.log(f"  Unique MPs: {len(self.statistics['mps_found'])}")
        self.log(f"  Unique laws: {len(self.statistics['laws_found'])}")
        self.log(f"  Statements: {self.statistics['statements_extracted']}")
        
        if self.statistics['errors']:
            self.log(f"  Errors: {len(self.statistics['errors'])}")
        
        return self.statistics


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced CDEP Agent')
    parser.add_argument('--update', action='store_true', help='Update recent data')
    parser.add_argument('--backfill', action='store_true', help='Backfill historical data')
    parser.add_argument('--years', default='2024,2025,2026', help='Years to process (comma-separated)')
    parser.add_argument('--year', type=int, help='Single year for backfill')
    parser.add_argument('--max-id', type=int, default=200, help='Max session ID to try')
    
    args = parser.parse_args()
    
    agent = EnhancedCDEPAgent()
    
    if args.update or not args.backfill:
        years = [int(y) for y in args.years.split(',')]
        agent.run(years, args.max_id)
    elif args.backfill and args.year:
        agent.run([args.year], args.max_id)


if __name__ == '__main__':
    main()