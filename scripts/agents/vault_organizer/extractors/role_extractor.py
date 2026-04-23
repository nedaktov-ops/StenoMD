#!/usr/bin/env python3
"""
StenoMD Role Extractor
Extracts session roles (presedinte, secretar) from stenograms
"""

import re
from typing import List, Optional, Dict, Tuple


class RoleExtractor:
    """Extract session leadership roles from transcript."""
    
    ROLE_PATTERNS = {
        'presedinte': [
            r'(?:vice)?președinte\s+(?:al\s+)?Senatului',
            r'președinte\s+de\s+ședință',
            r'președintele\s+(?:ședinței\s+)?(?:a\s+fost)?',
            r'conduse\s+de\s+domnul',
            r'conduse\s+de\s+(?:domnul|doamna)\s+([A-ZĂÂÎȘȚ][a-zăâîșț]+\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)',
        ],
        'secretar': [
            r'secretar(?:i)?\s+(?:ai\s+)?Senatului',
            r'asistat\s+de\s+domnii',
            r'secretari\s+ai\s+Senatului',
        ],
    }
    
    ROLE_KEYWORDS = {
        'presedinte': ['președinte', 'vicepreședinte', 'condus', 'conduce'],
        'secretar': ['secretar', 'secretari'],
    }
    
    def __init__(self):
        self.compiled_patterns = {}
        for role, patterns in self.ROLE_PATTERNS.items():
            self.compiled_patterns[role] = [
                re.compile(p, re.I | re.DOTALL) for p in patterns
            ]
    
    def extract_roles(self, transcript: str) -> List[Dict]:
        """Extract all session roles from transcript."""
        if not transcript:
            return []
        
        roles = []
        seen = set()
        
        # Find presedinte
        presedinte = self._extract_presedinte(transcript)
        if presedinte:
            roles.append(presedinte)
            seen.add(presedinte['name'])
        
        # Find secretari
        secretari = self._extract_secretari(transcript)
        for sec in secretari:
            if sec['name'] not in seen:
                roles.append(sec)
                seen.add(sec['name'])
        
        return roles
    
    def _extract_presedinte(self, transcript: str) -> Optional[Dict]:
        """Extract session president."""
        # Pattern: "Lucrările ședinței au fost conduse de domnul Mihai Coteț"
        pattern = re.compile(
            r'(?:conduse?\s+de\s+(?:domnul|doamna)\s+|președinte\s+al\s+Senatului\s+(?:a\s+fost\s+)?)([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)',
            re.I
        )
        
        match = pattern.search(transcript)
        if match:
            name = match.group(1).strip()
            return {
                'name': name,
                'role': 'presedinte',
                'context': self._get_context(transcript, name, 100),
            }
        
        return None
    
    def _extract_secretari(self, transcript: str) -> List[Dict]:
        """Extract session secretaries."""
        secretaries = []
        
        # Pattern: "asistat de domnii Vasile Blaga și Cristian Ghinea, secretari"
        pattern = re.compile(
            r'asistat\s+de\s+domnii?\s+([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+(?:\s+și\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)*)',
            re.I
        )
        
        match = pattern.search(transcript)
        if match:
            names_text = match.group(1)
            names = re.split(r'\s+și\s+', names_text)
            for name in names:
                name = name.strip()
                if name:
                    secretaries.append({
                        'name': name,
                        'role': 'secretar',
                        'context': self._get_context(transcript, name, 50),
                    })
        
        return secretaries
    
    def _get_context(self, text: str, name: str, radius: int = 100) -> str:
        """Get context around name mention."""
        idx = text.find(name)
        if idx == -1:
            return ''
        
        start = max(0, idx - radius)
        end = min(len(text), idx + len(name) + radius)
        
        return text[start:end].strip()
    
    def extract_role_for_person(self, transcript: str, person_name: str) -> Optional[str]:
        """Check if a specific person has a role in the session."""
        if not transcript or not person_name:
            return None
        
        # Quick keyword check
        person_lower = person_name.lower()
        transcript_lower = transcript.lower()
        
        if f'conduse de {person_lower}' in transcript_lower:
            return 'presedinte'
        
        if f'asistat de {person_lower}' in transcript_lower:
            return 'secretar'
        
        # Check position mentions
        if f'președinte al senatului {person_lower}' in transcript_lower:
            return 'presedinte'
        
        return None


def extract_roles(transcript: str) -> List[Dict]:
    """Standalone role extraction."""
    extractor = RoleExtractor()
    return extractor.extract_roles(transcript)


if __name__ == '__main__':
    extractor = RoleExtractor()
    
    test_transcripts = [
        """Lucrările ședinței au fost conduse de domnul Mihai Coteț, vicepreședinte al Senatului, asistat de domnii Vasile Blaga și Cristian Ghinea, secretari ai Senatului. SUMAR 1 Propunerea legislativă pentru completarea Legii nr.227/2015 privind Codul fiscal.""",
        """Ședința a început la ora 10.07. Președinte al Senatului a fost domnul Vasile Blaga.""",
        """Sedinta a fost condusa de presedintele de sedinta.""",
    ]
    
    print("=== Role Extractor Tests ===")
    for i, transcript in enumerate(test_transcripts):
        print(f"\n--- Transcript {i+1} ---")
        roles = extractor.extract_roles(transcript)
        for role in roles:
            print(f"  {role['name']}: {role['role']}")