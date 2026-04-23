#!/usr/bin/env python3
"""
StenoMD Name Normalizer
Standardizes names to canonical format with slug generation
"""

import re
from typing import Dict, List, Optional, Tuple


class NameNormalizer:
    """Normalize person names and generate slugs."""
    
    # Romanian diacritics mapping
    DIACRITICS_MAP = {
        'ă': 'a', 'Ă': 'A',
        'â': 'a', 'Â': 'A',
        'î': 'i', 'Î': 'I',
        'ș': 's', 'Ș': 'S',
        'ț': 't', 'Ț': 'T',
    }
    
    # Invalid name patterns to skip
    INVALID_PATTERNS = [
        'domnul', 'doamna', 'senator', 'deputat',
        'vicepresedinte', 'secretar', 'presedinte',
        'asistat', 'si', 'șii', 'domnii',
    ]
    
    def __init__(self):
        self.known_names: Dict[str, str] = {}
    
    def normalize(self, name: str) -> str:
        """Normalize name to canonical format."""
        if not name:
            return ''
        
        name = name.strip()
        name = re.sub(r'\s+', ' ', name)
        
        for diacritic, plain in self.DIACRITICS_MAP.items():
            name = name.replace(diacritic, plain)
        
        return name
    
    def to_slug(self, name: str) -> str:
        """Convert name to URL-safe slug."""
        if not name:
            return ''
        
        # Normalize first
        name = self.normalize(name)
        
        # Split into parts
        parts = name.split()
        
        # Take first and last
        if len(parts) >= 2:
            slug = f"{parts[0].lower()}-{parts[-1].lower()}"
        else:
            slug = parts[0].lower()
        
        # Handle compound names
        return slug
    
    def to_person_id(self, name: str) -> str:
        """Generate person ID from name."""
        slug = self.to_slug(name)
        return f"person_{slug}"
    
    def is_valid_name(self, name: str) -> bool:
        """Check if name is valid (not a role/title)."""
        if not name:
            return False
        
        name_lower = name.lower()
        
        for pattern in self.INVALID_PATTERNS:
            if pattern in name_lower:
                return False
        
        # Must have at least 2 parts (first + last name)
        parts = name.split()
        if len(parts) < 2:
            return False
        
        # Each part should start with uppercase
        for part in parts:
            if not part[0].isupper():
                return False
            if len(part) < 2:
                return False
        
        return True
    
    def split_name(self, name: str) -> Tuple[str, str]:
        """Split name into first and last name."""
        parts = name.split()
        
        if len(parts) >= 2:
            first = parts[0]
            last = parts[-1]
        else:
            first = parts[0] if parts else ''
            last = ''
        
        return first, last
    
    def clean_multi_name(self, text: str) -> List[str]:
        """Handle multi-name entries like 'Ion și Maria' or 'Ion, Maria'."""
        if not text:
            return []
        
        # Split on various separators
        parts = re.split(r',\s*|\s+și\s+|\s+si\s+', text)
        
        names = []
        for part in parts:
            part = part.strip()
            if self.is_valid_name(part):
                names.append(part)
        
        return names
    
    def register_alias(self, name: str, canonical_name: str):
        """Register name alias."""
        slug = self.to_slug(name)
        self.known_names[slug] = canonical_name
    
    def get_canonical(self, name: str) -> str:
        """Get canonical name (handling aliases)."""
        slug = self.to_slug(name)
        return self.known_names.get(slug, name)


def normalize_name(name: str) -> str:
    """Standalone name normalization."""
    normalizer = NameNormalizer()
    return normalizer.normalize(name)


def name_to_slug(name: str) -> str:
    """Standalone slug generation."""
    normalizer = NameNormalizer()
    return normalizer.to_slug(name)


def name_to_person_id(name: str) -> str:
    """Standalone person ID generation."""
    normalizer = NameNormalizer()
    return normalizer.to_person_id(name)


if __name__ == '__main__':
    normalizer = NameNormalizer()
    
    test_names = [
        'Mihai Coteț',
        'Vasile Blaga',
        'Niculina Stelea',
        'domnul Mihai Coteț',
        'Vasile',
        'Ion și Maria Popescu',
        'NICOLAE GIUGEA',
    ]
    
    print("=== Name Normalizer Tests ===")
    for name in test_names:
        normalized = normalizer.normalize(name)
        slug = normalizer.to_slug(name)
        valid = normalizer.is_valid_name(name)
        first, last = normalizer.split_name(name)
        print(f"{name:25} -> {normalized:20} | {slug:20} | {'✓' if valid else '✗'} | {first} + {last}")