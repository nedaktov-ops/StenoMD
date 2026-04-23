#!/usr/bin/env python3
"""
StenoMD ID Normalizer
Unified ID generation across all entity types
"""

import re
from datetime import datetime
from typing import Optional


class IDNormalizer:
    """Generate unified IDs for all entity types."""
    
    CHAMBERS = ['senate', 'deputies']
    
    def __init__(self):
        pass
    
    def session_id(self, chamber: str, date_iso: str) -> str:
        """
        Generate session ID.
        
        Pattern: session_{chamber}_{date}
        Example: session_senate_2026-04-01
        """
        chamber = self._validate_chamber(chamber)
        if not chamber:
            return ''
        
        return f"session_{chamber}_{date_iso}"
    
    def person_id(self, name_slug: str) -> str:
        """
        Generate person ID.
        
        Pattern: person_{slug}
        Example: person_mihai-cotet
        """
        slug = self._slugify(name_slug)
        return f"person_{slug}"
    
    def law_id(self, law_number: str) -> str:
        """
        Generate law ID.
        
        Pattern: L{num}-{year}
        Example: L14-2026
        """
        # Extract number and year
        match = re.match(r'^L?(\d+)-(\d{4})$', law_number)
        if not match:
            # Try other formats
            match = re.search(r'L?(\d+)/(\d{4})', law_number)
        
        if match:
            num, year = match.groups()
            return f"L{num}-{year}"
        
        return ''
    
    def topic_id(self, topic_slug: str) -> str:
        """
        Generate topic ID.
        
        Pattern: topic_{slug}
        Example: topic_buget
        """
        slug = self._slugify(topic_slug)
        return f"topic_{slug}"
    
    def party_id(self, party_name: str) -> str:
        """
        Generate party ID.
        
        Pattern: party_{name}
        Example: party_PNL
        """
        slug = self._slugify(party_name)
        return f"party_{slug}"
    
    def session_file_path(self, chamber: str, date_iso: str) -> str:
        """Generate session file path."""
        chamber_folder = 'senate' if chamber == 'senate' else 'deputies'
        return f"sessions/{chamber_folder}/{date_iso}.md"
    
    def person_file_path(self, name_slug: str, chamber: str) -> str:
        """Generate person file path."""
        chamber_folder = 'senate' if chamber == 'senate' else 'deputies'
        return f"politicians/{chamber_folder}/{name_slug}.md"
    
    def law_file_path(self, law_id: str) -> str:
        """Generate law file path."""
        return f"laws/{law_id}.md"
    
    def topic_file_path(self, topic_id: str) -> str:
        """Generate topic file path."""
        return f"topics/{topic_id}.md"
    
    def _validate_chamber(self, chamber: str) -> Optional[str]:
        """Validate chamber value."""
        chamber_lower = chamber.lower()
        if chamber_lower in self.CHAMBERS:
            return chamber_lower
        return None
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug."""
        if not text:
            return ''
        
        text = text.lower()
        text = re.sub(r'[^\w-]', '-', text)
        text = re.sub(r'-+', '-', text)
        text = text.strip('-')
        
        return text
    
    def parse_session_id(self, session_id: str) -> Optional[dict]:
        """Parse session ID components."""
        match = re.match(r'^session_(.+?)_(.+)$', session_id)
        if match:
            return {
                'chamber': match.group(1),
                'date': match.group(2),
            }
        return None
    
    def parse_person_id(self, person_id: str) -> Optional[str]:
        """Parse person ID to get slug."""
        match = re.match(r'^person_(.+)$', person_id)
        if match:
            return match.group(1)
        return None
    
    def parse_law_id(self, law_id: str) -> Optional[dict]:
        """Parse law ID components."""
        match = re.match(r'^L(\d+)-(\d{4})$', law_id)
        if match:
            return {
                'number': match.group(1),
                'year': match.group(2),
            }
        return None


def session_id(chamber: str, date: str) -> str:
    """Standalone session ID generation."""
    normalizer = IDNormalizer()
    return normalizer.session_id(chamber, date)


def person_id(name_slug: str) -> str:
    """Standalone person ID generation."""
    normalizer = IDNormalizer()
    return normalizer.person_id(name_slug)


def law_id(number: str) -> str:
    """Standalone law ID generation."""
    normalizer = IDNormalizer()
    return normalizer.law_id(number)


if __name__ == '__main__':
    normalizer = IDNormalizer()
    
    print("=== ID Normalizer Tests ===")
    
    # Session IDs
    print("\n--- Session IDs ---")
    test_sessions = [
        ('senate', '2026-04-01'),
        ('deputies', '2024-11-05'),
        ('SENATE', '2026-03-30'),
    ]
    for chamber, date in test_sessions:
        sid = normalizer.session_id(chamber, date)
        path = normalizer.session_file_path(chamber, date)
        print(f"{chamber}/{date} -> {sid}")
        print(f"  -> file: {path}")
    
    # Person IDs
    print("\n--- Person IDs ---")
    test_names = ['mihai-cotet', 'Vasile Blaga', 'Niculina Stelea']
    for name in test_names:
        pid = normalizer.person_id(name)
        print(f"{name} -> {pid}")
    
    # Law IDs
    print("\n--- Law IDs ---")
    test_laws = ['L14-2026', '14/2026', '95/2026', 'L499-2025']
    for law in test_laws:
        lid = normalizer.law_id(law)
        print(f"{law} -> {lid}")
    
    # Topic IDs
    print("\n--- Topic IDs ---")
    test_topics = ['buget', 'codul-fiscal', 'justitie']
    for topic in test_topics:
        tid = normalizer.topic_id(topic)
        print(f"{topic} -> {tid}")