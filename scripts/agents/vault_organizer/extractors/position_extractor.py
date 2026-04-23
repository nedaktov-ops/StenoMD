#!/usr/bin/env python3
"""
StenoMD Position Extractor
Extracts voting positions and stances from stenograms
"""

import re
from typing import List, Optional, Dict


class PositionExtractor:
    """Extract voting positions from transcript."""
    
    POSITION_PATTERNS = {
        'sustinere': [
            r'vot\s+(?:pentru|în\s+favoarea)',
            r'în\s+favoarea\s+(?:amendamentului|proiectului|legii)',
            r'susține\s+(?:amendamentul|proiectul|legea)',
            r'aprobare',
            r'adoptare',
            r'votat\s+cu\s+',
            r'pentru\s+acest\s+proiect',
        ],
        'impotriva': [
            r'vot\s+(?:împotriv[ăa]|împotriv[ăa])',
            r'împotriv[ăa]\s+(?:amendamentului|proiectului|legii)',
            r'împotriv[ăa]',
            r'respingere',
            r'împotriv[ăa]\s+vot',
        ],
        'abtinere': [
            r'abținere',
            r'abținut',
            r'vot\s+abțineri?',
        ],
        'redirectionat': [
            r'retrimis\s+(?:la|in)\s+(?:Comisie|Comisia)',
            r'la\s+comisie',
            r'dezbatere\s+ulterioar[ăa]',
            r'pentru\s+aviz',
        ],
    }
    
    def __init__(self):
        self.compiled_patterns = {}
        for position, patterns in self.POSITION_PATTERNS.items():
            self.compiled_patterns[position] = [
                re.compile(p, re.I) for p in patterns
            ]
    
    def extract_positions(self, transcript: str, person_name: Optional[str] = None) -> List[Dict]:
        """
        Extract voting positions from transcript.
        
        If person_name is provided, only extract their positions.
        Otherwise, extract all positions from the transcript.
        """
        if not transcript:
            return []
        
        positions = []
        
        for position_type, patterns in self.POSITION_PATTERNS.items():
            for pattern in patterns:
                regex = re.compile(pattern, re.I | re.DOTALL)
                
                if person_name:
                    # Look for person's position
                    person_pos = self._find_person_position(
                        transcript, person_name, position_type, regex
                    )
                    if person_pos:
                        positions.append(person_pos)
                else:
                    # Extract all positions of this type
                    for match in regex.finditer(transcript):
                        context = self._get_context(transcript, match.start(), 150)
                        positions.append({
                            'position': position_type,
                            'context': context,
                            'reference': match.group(0),
                        })
        
        return positions
    
    def _find_person_position(
        self, transcript: str, person_name: str, position_type: str, pattern: re.Pattern
    ) -> Optional[Dict]:
        """Find a specific person's position on a topic."""
        # Look for person name near position pattern
        search_start = 0
        person_lower = person_name.lower()
        transcript_lower = transcript.lower()
        
        while True:
            idx = transcript_lower.find(person_lower, search_start)
            if idx == -1:
                break
            
            # Check if position pattern is within 500 chars after person name
            search_region = transcript[idx:min(idx + 500, len(transcript))]
            match = pattern.search(search_region)
            
            if match:
                return {
                    'position': position_type,
                    'person': person_name,
                    'context': self._get_context(transcript, idx, 200),
                }
            
            search_start = idx + 1
        
        return None
    
    def _get_context(self, text: str, position: int, radius: int = 100) -> str:
        """Get context around position mention."""
        start = max(0, position - radius)
        end = min(len(text), position + radius)
        return text[start:end].strip()
    
    def extract_topic_position(
        self, transcript: str, topic: str
    ) -> Dict:
        """Extract aggregated position on a specific topic."""
        if not transcript:
            return {}
        
        positions = {
            'sustinere': 0,
            'impotriva': 0,
            'abtinere': 0,
            'redirectionat': 0,
        }
        
        transcript_lower = transcript.lower()
        topic_lower = topic.lower()
        
        # Find topic mentions
        topic_matches = list(re.finditer(topic_lower, transcript_lower))
        
        for pos_type, patterns in self.POSITION_PATTERNS.items():
            for pattern in patterns:
                regex = re.compile(pattern, re.I)
                for match in regex.finditer(transcript_lower):
                    # Check if near a topic mention
                    for tm in topic_matches:
                        if abs(match.start() - tm.start()) < 300:
                            positions[pos_type] += 1
                            break
        
        return positions
    
    def classify_position_stance(
        self, position: str
    ) -> str:
        """Classify position as positive, negative, or neutral."""
        positive = ['sustinere', 'aprobare', 'adoptare']
        negative = ['impotriva', 'respingere']
        neutral = ['abtinere', 'redirectionat']
        
        if position in positive:
            return 'positive'
        elif position in negative:
            return 'negative'
        elif position in neutral:
            return 'neutral'
        
        return 'unknown'


def extract_positions(transcript: str, person: Optional[str] = None) -> List[Dict]:
    """Standalone position extraction."""
    extractor = PositionExtractor()
    return extractor.extract_positions(transcript, person)


if __name__ == '__main__':
    extractor = PositionExtractor()
    
    test_transcripts = [
        """(L14/2026) (Retrimitere la Comisia pentru buget, finanţe, activitate bancară şi piaţă de capital.)
        5 Dezbaterea și respingerea Propunerii legislative pentru reducerea gradului de recidivă în cadrul reformei legii penale și a condițiilor din penitenciare. (L95/2026) 
        6 Vot pentru acest proiect.""",
        """1 Aprobarea ordinii de zi și a programului de lucru.""",
        """Senatorul a votat impotriva amendamentului.""",
    ]
    
    print("=== Position Extractor Tests ===")
    for i, transcript in enumerate(test_transcripts):
        print(f"\n--- Transcript {i+1} ---")
        positions = extractor.extract_positions(transcript)
        for pos in positions:
            print(f"  {pos['position']}: {pos.get('context', pos.get('reference', ''))[:50]}...")