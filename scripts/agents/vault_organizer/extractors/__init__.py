#!/usr/bin/env python3
"""
StenoMD Extractors Package
Extractors for roles, positions, topics, and statements
"""

from .role_extractor import RoleExtractor, extract_roles
from .position_extractor import PositionExtractor, extract_positions
from .statement_extractor import StatementExtractor, Statement, extract_statements

__all__ = [
    'RoleExtractor',
    'PositionExtractor',
    'StatementExtractor',
    'Statement',
    'extract_roles',
    'extract_positions',
    'extract_statements',
]


class Extractors:
    """Combined extractors for convenience."""
    
    def __init__(self):
        self.role = RoleExtractor()
        self.position = PositionExtractor()
        self.statement = StatementExtractor()
    
    def extract_all(self, transcript: str, person_name: Optional[str] = None) -> dict:
        """Extract all metadata from transcript."""
        from typing import Optional
        
        return {
            'roles': self.role.extract_roles(transcript),
            'positions': self.position.extract_positions(transcript, person_name),
            'statements': self.statement.extract(transcript, person_name),
            'speaker_count': self.statement.get_speaker_count(transcript),
        }
    
    def get_person_metadata(
        self, transcript: str, person_name: str
    ) -> dict:
        """Get all metadata for a specific person."""
        return {
            'role': self.role.extract_role_for_person(transcript, person_name),
            'statements': self.statement.extract(transcript, person_name),
            'statement_count': self.statement.get_statement_count(transcript, person_name),
            'positions': self.position.extract_positions(transcript, person_name),
        }