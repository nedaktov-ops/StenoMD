#!/usr/bin/env python3
"""
StenoMD Session Processor
Processes session data from both CDEP and Senate into unified format
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
from extractors import (
    RoleExtractor, PositionExtractor, StatementExtractor
)


class SessionProcessor:
    """Process session data into unified format."""
    
    CHAMBER_DISPLAY = {
        'senate': 'Senat',
        'deputies': 'Camera Deputatilor',
    }
    
    def __init__(self):
        self.date_norm = DateNormalizer()
        self.name_norm = NameNormalizer()
        self.law_norm = LawNormalizer()
        self.topic_norm = TopicNormalizer()
        self.id_norm = IDNormalizer()
        self.role_extractor = RoleExtractor()
        self.position_extractor = PositionExtractor()
        self.statement_extractor = StatementExtractor()
    
    def process(
        self, 
        raw_data: Dict,
        source: str  # 'senat.ro' or 'cdep.ro'
    ) -> Dict:
        """
        Process raw session data into unified format.
        
        Expected raw_data keys:
        - date: Session date
        - title: Session title
        - transcript: Full transcript text
        - participants: List of participant names
        - laws: List of law references
        - source_url: Source URL
        - source_id: Original ID from website
        """
        chamber = 'senate' if 'senat' in source else 'deputies'
        
        # Normalize date
        date_iso = self.date_norm.parse(raw_data.get('date', ''))
        date_display = self.date_norm.to_display(date_iso, chamber) if date_iso else ''
        
        # Generate IDs
        session_id = self.id_norm.session_id(chamber, date_iso) if date_iso else ''
        
        # Extract roles
        transcript = raw_data.get('transcript', '')
        roles = self.role_extractor.extract_roles(transcript)
        
        # Process speakers
        speakers = self._process_speakers(
            raw_data.get('participants', []),
            roles,
            transcript
        )
        
        # Process laws
        laws = self._process_laws(raw_data.get('laws', []))
        
        # Classify topics
        topics = self.topic_norm.classify(transcript)
        
        # Extract summary
        summary = self._generate_summary(raw_data)
        
        return {
            'id': session_id,
            'date': date_iso,
            'date_display': date_display,
            'chamber': chamber,
            'chamber_display': self.CHAMBER_DISPLAY.get(chamber, chamber),
            'title': raw_data.get('title', ''),
            'source': source,
            'source_url': raw_data.get('source_url', ''),
            'source_id': raw_data.get('source_id', ''),
            'transcript': transcript[:5000] if transcript else '',
            'word_count': len(transcript.split()) if transcript else 0,
            'speakers': speakers,
            'speakers_count': len(speakers),
            'laws': laws,
            'laws_count': len(laws),
            'topics': topics,
            'summary': summary,
            'is_complete': len(speakers) > 0 and len(transcript) > 100,
            'extracted_at': datetime.now().isoformat(),
        }
    
    def _process_speakers(
        self, 
        participants: List[str],
        roles: List[Dict],
        transcript: str
    ) -> List[Dict]:
        """Process speakers with roles and statements."""
        speakers = []
        seen = set()
        
        # Add roles first
        for role in roles:
            name = role['name']
            slug = self.name_norm.to_slug(name)
            person_id = self.id_norm.person_id(slug)
            
            if person_id in seen:
                continue
            
            speakers.append({
                'id': person_id,
                'name': self.name_norm.normalize(name),
                'slug': slug,
                'role': role['role'],
                'party': None,
                'statement_count': self.statement_extractor.get_statement_count(transcript, name),
                'excerpt': self._get_first_statement(transcript, name),
            })
            seen.add(person_id)
        
        # Add other participants
        for name in participants:
            slug = self.name_norm.to_slug(name)
            person_id = self.id_norm.person_id(slug)
            
            if person_id in seen:
                continue
            
            if not self.name_norm.is_valid_name(name):
                continue
            
            speakers.append({
                'id': person_id,
                'name': self.name_norm.normalize(name),
                'slug': slug,
                'role': 'speaker',
                'party': None,
                'statement_count': self.statement_extractor.get_statement_count(transcript, name),
                'excerpt': self._get_first_statement(transcript, name),
            })
            seen.add(person_id)
        
        return speakers
    
    def _get_first_statement(self, transcript: str, speaker_name: str) -> str:
        """Get first statement from speaker."""
        stmt = self.statement_extractor.get_first_statement(transcript, speaker_name)
        return stmt.excerpt if stmt else ''
    
    def _process_laws(self, law_refs: List[str]) -> List[Dict]:
        """Process law references."""
        laws = []
        
        for ref in law_refs:
            law_id = self.law_norm.normalize(ref)
            if not law_id:
                continue
            
            laws.append({
                'id': law_id,
                'number': self.law_norm.to_display(law_id),
                'status': 'dezbatere',
            })
        
        return laws
    
    def _generate_summary(self, raw_data: Dict) -> str:
        """Generate session summary."""
        transcript = raw_data.get('transcript', '')[:1000]
        
        if not transcript:
            return ''
        
        parts = []
        
        laws = self._process_laws(raw_data.get('laws', []))
        if laws:
            parts.append(f"Discutate {len(laws)} legi")
        
        topics = self.topic_norm.classify(transcript)
        if topics:
            topic_names = [self.topic_norm.get_display(t) for t in topics[:3]]
            parts.append(f"Subiecte: {', '.join(topic_names)}")
        
        speakers = raw_data.get('participants', [])
        if speakers:
            parts.append(f"{len(speakers)} participanti")
        
        return '. '.join(parts) if parts else transcript[:200]


def process_session(raw_data: Dict, source: str) -> Dict:
    """Standalone session processing."""
    processor = SessionProcessor()
    return processor.process(raw_data, source)


if __name__ == '__main__':
    processor = SessionProcessor()
    
    test_data = {
        'date': '1 aprilie 2026',
        'title': 'Stenograma Sedintei Senatului din 1 aprilie 2026',
        'transcript': """Lucrarile sedintei au fost conduse de domnul Mihai Coteț, presedinte al Senatului, asistat de domnii Vasile Blaga si Cristian Ghinea, secretari. SUMAR 1 Propunerea legislativă pentru completarea Legii nr.227/2015 privind Codul fiscal. (L14/2026) 2 Aprobarea ordinii de zi. Domnul Vasile Blaga: Sunt de acord cu acest proiect. Doamna Niculina Stelea: Am amendamente la aceasta lege.""",
        'participants': ['Mihai Coteț', 'Vasile Blaga', 'Niculina Stelea'],
        'laws': ['L14/2026', 'L95/2026'],
        'source_url': 'https://senat.ro/StenoPag2.aspx',
    }
    
    print("=== Session Processor Test ===")
    result = processor.process(test_data, 'senat.ro')
    
    print(f"ID: {result['id']}")
    print(f"Date: {result['date']}")
    print(f"Chamber: {result['chamber']}")
    print(f"Speakers: {result['speakers_count']}")
    for speaker in result['speakers']:
        print(f"  - {speaker['name']} ({speaker['role']})")
    print(f"Laws: {result['laws_count']}")
    print(f"Topics: {result['topics']}")
    print(f"Word count: {result['word_count']}")