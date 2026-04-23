#!/usr/bin/env python3
"""
StenoMD Person Processor
Processes person data from both CDEP and Senate into unified format
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from normalizers import (
    DateNormalizer, NameNormalizer, LawNormalizer, 
    TopicNormalizer, IDNormalizer
)
from extractors import StatementExtractor, PositionExtractor


class PersonProcessor:
    """Process person data into unified format."""
    
    CHAMBER_DISPLAY = {
        'senate': 'Senat',
        'deputies': 'Camera Deputatilor',
    }
    
    ROLE_DISPLAY = {
        'senator': 'Senator',
        'deputat': 'Deputat',
    }
    
    def __init__(self):
        self.name_norm = NameNormalizer()
        self.id_norm = IDNormalizer()
        self.date_norm = DateNormalizer()
        self.topic_norm = TopicNormalizer()
        self.statement_extractor = StatementExtractor()
        self.position_extractor = PositionExtractor()
    
    def process(
        self,
        name: str,
        chamber: str,
        role: str = None,
        party: str = None,
        legislature: str = '2024-2028',
        sessions: List[Dict] = None,
    ) -> Dict:
        """
        Process person data into unified format.
        
        Sessions is a list of dicts with keys:
        - session_id
        - date
        - role
        - statement_count
        - topics
        """
        # Normalize name
        normalized_name = self.name_norm.normalize(name)
        slug = self.name_norm.to_slug(name)
        first, last = self.name_norm.split_name(name)
        person_id = self.id_norm.person_id(slug)
        
        # Process sessions
        sessions = sessions or []
        processed_sessions = []
        for sess in sessions:
            date_iso = self.date_norm.parse(sess.get('date', ''))
            processed_sessions.append({
                'id': sess.get('session_id', ''),
                'date': date_iso,
                'date_display': self.date_norm.to_display(date_iso, chamber) if date_iso else '',
                'chamber': chamber,
                'chamber_folder': 'senate' if chamber == 'senate' else 'deputies',
                'role': sess.get('role', 'speaker'),
                'statement_count': sess.get('statement_count', 0),
                'topics': sess.get('topics', []),
            })
        
        # Calculate totals
        statements_total = sum(s.get('statement_count', 0) for s in processed_sessions)
        
        return {
            'id': person_id,
            'name': normalized_name,
            'name_first': first,
            'name_last': last,
            'slug': slug,
            'chamber': chamber,
            'chamber_display': self.CHAMBER_DISPLAY.get(chamber, chamber),
            'role': role or (self.ROLE_DISPLAY.get(chamber, chamber)),
            'party': party,
            'party_display': self._get_party_display(party),
            'legislature': legislature,
            'sessions': processed_sessions,
            'sessions_count': len(processed_sessions),
            'statements_total': statements_total,
            'positions': [],
            'positions_count': 0,
            'committees': [],
            'is_complete': len(sessions) > 0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
    
    def process_from_transcript(
        self,
        name: str,
        chamber: str,
        transcript: str,
        session_id: str,
        session_date: str,
    ) -> Dict:
        """Process person data extracted from transcript."""
        # Get basic info
        person = self.process(name, chamber)
        
        # Extract statements from this session
        stmt = self.statement_extractor.get_first_statement(transcript, name)
        if stmt:
            person['first_statement'] = stmt.excerpt
        
        # Extract positions from this session
        positions = self.position_extractor.extract_positions(transcript, name)
        person['positions'] = [{
            'position': pos['position'],
            'topic': 'general',
            'session': session_id,
            'date': session_date,
            'context': pos.get('context', '')[:100],
        } for pos in positions[:3]]
        person['positions_count'] = len(person['positions'])
        
        return person
    
    def update_from_session(
        self,
        person_data: Dict,
        session_id: str,
        session_date: str,
        role: str = None,
        statement_count: int = 0,
        topics: List[str] = None,
    ) -> Dict:
        """Update person data with new session participation."""
        date_iso = self.date_norm.parse(session_date)
        
        # Check if session already exists
        exists = any(s['id'] == session_id for s in person_data.get('sessions', []))
        
        if not exists:
            new_session = {
                'id': session_id,
                'date': date_iso,
                'date_display': self.date_norm.to_display(date_iso, person_data['chamber']) if date_iso else '',
                'chamber': person_data['chamber'],
                'chamber_folder': 'senate' if person_data['chamber'] == 'senate' else 'deputies',
                'role': role or 'speaker',
                'statement_count': statement_count,
                'topics': topics or [],
            }
            person_data['sessions'].append(new_session)
            person_data['sessions_count'] = len(person_data['sessions'])
            person_data['statements_total'] += statement_count
        
        person_data['updated_at'] = datetime.now().isoformat()
        
        return person_data
    
    def _get_party_display(self, party: str) -> str:
        """Get full party name."""
        parties = {
            'PSD': 'Partidul Social Democrat',
            'PNL': 'Partidul Național Liberal',
            'USR': 'Uniunea Salvați România',
            'AUR': 'Alternativa pentru Demnitate și Ortografie Națională',
            'UDMR': 'Uniunea Democrată Maghiară din România',
            'SOS': 'SOS România',
            'POT': 'Partidul Oamenilor Tineri',
            'REPER': 'Partidul REPER',
        }
        return parties.get(party, party or 'independent')


def process_person(
    name: str,
    chamber: str,
    role: str = None,
    party: str = None,
) -> Dict:
    """Standalone person processing."""
    processor = PersonProcessor()
    return processor.process(name, chamber, role, party)


if __name__ == '__main__':
    processor = PersonProcessor()
    
    print("=== Person Processor Test ===")
    
    # Test basic processing
    person = processor.process(
        'Mihai Coteț',
        'senate',
        party='PNL',
        legislature='2024-2028',
    )
    
    print(f"ID: {person['id']}")
    print(f"Name: {person['name']}")
    print(f"Slug: {person['slug']}")
    print(f"Chamber: {person['chamber_display']}")
    print(f"Party: {person['party']} ({person['party_display']})")
    
    # Test with sessions
    person2 = processor.process(
        'Vasile Blaga',
        'senate',
        party='PNL',
        sessions=[
            {
                'session_id': 'session_senate_2026-04-01',
                'date': '1 aprilie 2026',
                'role': 'secretar',
                'statement_count': 5,
                'topics': ['buget'],
            }
        ]
    )
    
    print(f"\n{person2['name']}:")
    print(f"  Sessions: {person2['sessions_count']}")
    print(f"  Statements: {person2['statements_total']}")
    for sess in person2['sessions']:
        print(f"    - {sess['date']} ({sess['role']})")