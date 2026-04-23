#!/usr/bin/env python3
"""
StenoMD Normalizers Package
Unified normalization for all entity types
"""

from .date_normalizer import DateNormalizer, normalize_date, normalize_date_display
from .name_normalizer import NameNormalizer, normalize_name, name_to_slug, name_to_person_id
from .law_normalizer import LawNormalizer, normalize_law, extract_laws
from .topic_normalizer import TopicNormalizer, normalize_topic, classify_topics
from .id_normalizer import IDNormalizer, session_id, person_id, law_id

__all__ = [
    'DateNormalizer',
    'NameNormalizer', 
    'LawNormalizer',
    'TopicNormalizer',
    'IDNormalizer',
    'normalize_date',
    'normalize_date_display',
    'normalize_name',
    'name_to_slug',
    'name_to_person_id',
    'normalize_law',
    'extract_laws',
    'normalize_topic',
    'classify_topics',
    'session_id',
    'person_id',
    'law_id',
]


class Normalizers:
    """Combined normalizer for convenience."""
    
    def __init__(self):
        self.date = DateNormalizer()
        self.name = NameNormalizer()
        self.law = LawNormalizer()
        self.topic = TopicNormalizer()
        self.id = IDNormalizer()
    
    def session(self, chamber: str, date_str: str) -> dict:
        """Normalize session data."""
        iso_date = self.date.parse(date_str)
        if not iso_date:
            return {}
        
        return {
            'id': self.id.session_id(chamber, iso_date),
            'date': iso_date,
            'date_display': self.date.to_display(iso_date, chamber),
            'chamber': chamber,
        }
    
    def person(self, name: str, chamber: str) -> dict:
        """Normalize person data."""
        normalized_name = self.name.normalize(name)
        slug = self.name.to_slug(name)
        
        return {
            'id': self.id.person_id(slug),
            'name': normalized_name,
            'slug': slug,
            'chamber': chamber,
        }
    
    def law(self, law_ref: str) -> dict:
        """Normalize law data."""
        law_id = self.law.normalize(law_ref)
        if not law_id:
            return {}
        
        return {
            'id': law_id,
            'number': self.law.get_number(law_id),
            'year': self.law.get_year(law_id),
            'number_display': self.law.to_display(law_id),
        }