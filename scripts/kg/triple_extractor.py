#!/usr/bin/env python3
"""
Triple Extractor for StenoMD
Extracts relationships from session data

Predicates:
- spoke_in: MP spoke in a session
- discussed: Session discussed a law
- member_of: MP is member of a party

Usage:
    python3 triple_extractor.py --extract
    python3 triple_extractor.py --from-vault
"""

import json
import re
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from collections import defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
VAULT_DIR = PROJECT_DIR / "vault"
KG_DIR = PROJECT_DIR / "knowledge_graph"
KG_DB = KG_DIR / "knowledge_graph.db"


class TripleExtractor:
    """Extracts triples from parliamentary sessions."""
    
    def __init__(self):
        self.kg_path = KG_DB
        self._init_connection()
    
    def _init_connection(self):
        """Initialize database connection."""
        self.conn = sqlite3.connect(self.kg_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close database connection."""
        self.conn.close()
    
    def _add_triple(self, subject: str, predicate: str, obj: str, 
                   confidence: float = 1.0, source: str = 'extractor'):
        """Add triple to database."""
        try:
            self.cursor.execute("""
                INSERT INTO triples (subject, predicate, object, confidence, source)
                VALUES (?, ?, ?, ?, ?)
            """, (subject, predicate, obj, confidence, source))
        except sqlite3.IntegrityError:
            pass  # Already exists
    
    def extract_from_vault(self, chamber: str = 'deputies'):
        """Extract triples from vault session files."""
        chamber_dir = VAULT_DIR / "sessions" / chamber
        
        if not chamber_dir.exists():
            print(f"No vault directory for {chamber}")
            return 0
        
        sessions_dir = list(chamber_dir.glob("*.md"))
        triples_extracted = 0
        
        for session_file in sessions_dir:
            content = session_file.read_text(encoding='utf-8')
            
            # Extract date
            date_match = re.search(r'^date:\s*(.+)$', content, re.MULTILINE)
            date = date_match.group(1) if date_match else session_file.stem
            
            # Extract participants
            participants = self._extract_participants(content)
            for participant in participants:
                self._add_triple(participant, 'spoke_in', date, source='vault')
                triples_extracted += 1
            
            # Extract laws discussed
            laws = self._extract_laws(content)
            for law in laws:
                self._add_triple(date, 'discussed', law, source='vault')
                triples_extracted += 1
        
        self.conn.commit()
        print(f"Extracted {triples_extracted} triples from {chamber}")
        return triples_extracted
    
    def _extract_participants(self, content: str) -> List[str]:
        """Extract participant names from session content."""
        participants = []
        
        # Match wikilinks [[session_xxx]] or dates
        for match in re.finditer(r'\[\[([^\]]+)\]\]', content):
            name = match.group(1)
            # Filter out session references
            if not name.startswith('session_') and not name.startswith('20'):
                participants.append(name)
        
        # Also check participants section
        section_match = re.search(r'## Participants\s*\n(.*?)(?:\n##|\Z)', content, re.DOTALL)
        if section_match:
            participant_text = section_match.group(1)
            # Extract names (simple: look for capitalized words)
            for match in re.finditer(r'([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)', 
                                    participant_text):
                name = match.group(1)
                if len(name) > 5:
                    participants.append(name)
        
        return list(set(participants))
    
    def _extract_laws(self, content: str) -> List[str]:
        """Extract law numbers from session content."""
        laws = []
        
        # Match patterns like "Legea 123/2024" or just numbers
        for match in re.finditer(r'(\d+/\d{4})', content):
            laws.append(match.group(1))
        
        return list(set(laws))
    
    def extract_from_memory(self):
        """Extract triples from memory database (action records)."""
        memory_db = SCRIPT_DIR / "memory" / "memory.db"
        
        if not memory_db.exists():
            print("memory.db not found")
            return 0
        
        conn = sqlite3.connect(memory_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        triples_extracted = 0
        
        # Get scrape actions with parameters
        cursor.execute("""
            SELECT id, parameters, outcome 
            FROM actions 
            WHERE type = 'scrape_session'
        """)
        
        for row in cursor.fetchall():
            try:
                params = json.loads(row['parameters']) if row['parameters'] else {}
                chamber = params.get('chamber', '')
                date = params.get('date', '')
                
                if chamber and date:
                    # Add scrape action triple
                    self._add_triple(
                        f"scrape_{row['id'][:8]}",
                        'scraped_session',
                        f"{chamber}:{date}",
                        source='memory'
                    )
                    triples_extracted += 1
                    
                    # Add MP involvement if known
                    mps_count = params.get('mps_count') or params.get('senators_count', 0)
                    if mps_count:
                        self._add_triple(
                            f"{chamber}_session",
                            'had_participants',
                            str(mps_count),
                            confidence=0.8,
                            source='memory'
                        )
                        triples_extracted += 1
            except (json.JSONDecodeError, TypeError):
                continue
        
        conn.close()
        self.conn.commit()
        print(f"Extracted {triples_extracted} triples from memory")
        return triples_extracted
    
    def build_entity_relationships(self):
        """Build entity relationships from extracted triples."""
        # Get all "spoke_in" triples
        self.cursor.execute("""
            SELECT subject, object FROM triples 
            WHERE predicate = 'spoke_in'
        """)
        
        # Group by speaker
        speaker_sessions = defaultdict(list)
        for row in self.cursor.fetchall():
            speaker_sessions[row['subject']].append(row['object'])
        
        # Add session count relationship
        for speaker, sessions in speaker_sessions.items():
            if len(sessions) > 1:
                self._add_triple(
                    speaker,
                    'participated_in_sessions',
                    str(len(sessions)),
                    confidence=0.9,
                    source='inferred'
                )
        
        # Get all "discussed" triples
        self.cursor.execute("""
            SELECT subject, object FROM triples 
            WHERE predicate = 'discussed'
        """)
        
        # Group by session
        session_laws = defaultdict(list)
        for row in self.cursor.fetchall():
            session_laws[row['subject']].append(row['object'])
        
        # Add law count relationship
        for session, laws in session_laws.items():
            if len(laws) > 1:
                self._add_triple(
                    session,
                    'discussed_laws',
                    str(len(laws)),
                    confidence=0.9,
                    source='inferred'
                )
        
        self.conn.commit()
        print("Built entity relationships")
    
    def get_extraction_stats(self) -> Dict:
        """Get extraction statistics."""
        stats = {}
        
        self.cursor.execute("SELECT COUNT(*) FROM triples")
        stats['total_triples'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT predicate, COUNT(*) FROM triples GROUP BY predicate")
        stats['by_predicate'] = dict(self.cursor.fetchall())
        
        self.cursor.execute("SELECT source, COUNT(*) FROM triples GROUP BY source")
        stats['by_source'] = dict(self.cursor.fetchall())
        
        return stats


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Triple Extractor')
    parser.add_argument('--extract', action='store_true', help='Extract all triples')
    parser.add_argument('--from-vault', action='store_true', help='Extract from vault')
    parser.add_argument('--from-memory', action='store_true', help='Extract from memory')
    parser.add_argument('--build-relations', action='store_true', help='Build entity relationships')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--chamber', default='deputies', help='Chamber to process')
    
    args = parser.parse_args()
    
    extractor = TripleExtractor()
    
    if args.extract or args.from_vault:
        extractor.extract_from_vault(args.chamber)
        extractor.extract_from_vault('senators')
    
    if args.extract or args.from_memory:
        extractor.extract_from_memory()
    
    if args.build_relations:
        extractor.build_entity_relationships()
    
    if args.stats:
        stats = extractor.get_extraction_stats()
        print("=== Triple Extraction Stats ===")
        print(f"Total triples: {stats['total_triples']}")
        print(f"By predicate: {stats['by_predicate']}")
        print(f"By source: {stats['by_source']}")
    
    extractor.close()


if __name__ == '__main__':
    main()