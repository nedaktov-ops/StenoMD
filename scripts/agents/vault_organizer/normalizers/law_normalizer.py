#!/usr/bin/env python3
"""
StenoMD Law Normalizer
Standardizes law numbers to canonical format
"""

import re
from typing import Optional, List


class LawNormalizer:
    """Normalize law references."""
    
    # Patterns that indicate a law reference
    LAW_PATTERNS = [
        r'(L|Legea|Proiectul de lege|Proiectul|Lege|PL)\s*(?:nr\.?\s*)?(\d+/\d{4})',
        r'\((\d+/\d{4})\)',
        r'Legislația\s+(?:nr\.?\s*)?(\d+/\d{4})',
    ]
    
    def __init__(self):
        self.known_laws = {}
    
    def normalize(self, law_ref: str) -> Optional[str]:
        """Normalize law reference to canonical format L{num}-{year}."""
        if not law_ref:
            return None
        
        law_ref = law_ref.strip()
        
        # Already normalized
        if re.match(r'^L?\d+-\d{4}$', law_ref):
            if not law_ref.startswith('L'):
                return f"L{law_ref}"
            return law_ref
        
        # Extract number/year
        match = re.search(r'(\d+)/(\d{4})', law_ref)
        if match:
            num, year = match.groups()
            return f"L{num}-{year}"
        
        return None
    
    def extract_from_text(self, text: str) -> List[str]:
        """Extract all law references from text."""
        if not text:
            return []
        
        laws = set()
        
        for pattern in self.LAW_PATTERNS:
            for match in re.finditer(pattern, text, re.I):
                groups = match.groups()
                for g in groups:
                    if g and '/' in g:
                        law_id = self.normalize(g)
                        if law_id:
                            laws.add(law_id)
        
        return sorted(list(laws))
    
    def to_display(self, law_id: str) -> str:
        """Convert canonical ID to display format."""
        if not law_id:
            return ''
        
        match = re.match(r'^L?(\d+)-(\d{4})$', law_id)
        if match:
            num, year = match.groups()
            return f"L{num}/{year}"
        
        return law_id
    
    def get_number(self, law_id: str) -> Optional[str]:
        """Extract just the number (without L prefix and year)."""
        if not law_id:
            return None
        
        match = re.match(r'^L?(\d+)-(\d{4})$', law_id)
        if match:
            return match.group(1)
        
        return None
    
    def get_year(self, law_id: str) -> Optional[int]:
        """Extract the year from law ID."""
        if not law_id:
            return None
        
        match = re.match(r'^L?(\d+)-(\d{4})$', law_id)
        if match:
            return int(match.group(2))
        
        return None
    
    def register(self, law_id: str, metadata: dict):
        """Register law metadata."""
        self.known_laws[law_id] = metadata
    
    def get(self, law_id: str) -> Optional[dict]:
        """Get law metadata."""
        return self.known_laws.get(law_id)


def normalize_law(law_ref: str) -> Optional[str]:
    """Standalone law normalization."""
    normalizer = LawNormalizer()
    return normalizer.normalize(law_ref)


def extract_laws(text: str) -> List[str]:
    """Standalone law extraction."""
    normalizer = LawNormalizer()
    return normalizer.extract_from_text(text)


if __name__ == '__main__':
    normalizer = LawNormalizer()
    
    test_refs = [
        'L14/2026',
        '14/2026',
        '(L95/2026)',
        'Proiectul de lege nr. 30/2026',
        'Legislația nr.123/2026',
        'L499-2025',
    ]
    
    test_text = """
    (L14/2026) (Retrimitere la Comisie pentru buget, finanţe) 
    2 Aprobarea ordinii de zi și a programului de lucru. 
    5 Dezbaterea și respingerea Propunerii legislative pentru reducerea gradului de recidivă în cadrul reformei legii penale și a condițiilor din penitenciare. (L95/2026) 
    6 Dezbaterea și respingerea Propunerii legislative pentru completarea Legii nr.286/2009 privind Codul penal. (L96/2026)
    """
    
    print("=== Law Normalizer Tests ===")
    for ref in test_refs:
        normalized = normalizer.normalize(ref)
        display = normalizer.to_display(normalized) if normalized else 'INVALID'
        print(f"{ref:20} -> {normalized or 'FAILED':12} -> {display}")
    
    print("\n=== Law Extraction from Text ===")
    laws = normalizer.extract_from_text(test_text)
    for law in laws:
        print(f"  {law} -> {normalizer.to_display(law)}")