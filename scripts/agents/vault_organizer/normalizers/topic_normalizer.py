#!/usr/bin/env python3
"""
StenoMD Topic Normalizer
Hybrid topic classification (predefined + dynamic)
"""

import re
from typing import List, Optional, Dict


class TopicNormalizer:
    """Normalize and classify topics."""
    
    # Primary category taxonomy
    CATEGORIES = {
        'economie': {
            'display': 'Economie',
            'topics': ['buget', 'finante', 'impozite', 'taxe', 'PIB', 'investitii'],
            'keywords': ['buget', 'finanțe', 'economic', 'impozit', 'taxe', 'PIB'],
        },
        'justitie': {
            'display': 'Justiție',
            'topics': ['codul-penal', ' instante', 'judicial', 'penal'],
            'keywords': ['penal', 'instanț', 'judecat', 'justiție'],
        },
        'sanatate': {
            'display': 'Sănătate',
            'topics': ['medical', 'spital', 'medicamente'],
            'keywords': ['sănătate', 'medical', 'spital', 'doctor'],
        },
        'aparare': {
            'display': 'Apărare',
            'topics': ['NATO', 'securitate', 'armata'],
            'keywords': ['apărare', 'armată', 'militar', 'NATO'],
        },
        'mediu': {
            'display': 'Mediu',
            'topics': ['clima', 'energie', 'ecologie'],
            'keywords': ['mediu', 'ecologie', 'climă', 'energie'],
        },
        'social': {
            'display': 'Social',
            'topics': ['pensii', 'alocatii', 'asistenta-sociala'],
            'keywords': ['pensii', 'alocații', 'beneficii', 'asistență'],
        },
        'european': {
            'display': 'European',
            'topics': ['UE', 'regulament', 'COM'],
            'keywords': ['european', 'UE', 'Bruxelles', 'comisar'],
        },
    }
    
    # Topic aliases (dynamic to canonical)
    ALIASES = {
        'codul fiscal': 'buget',
        'codul-fiscal': 'buget',
        'cod-fiscal': 'buget',
        'pensii': 'social',
        'alocatii': 'social',
        'cod penal': 'justitie',
    }
    
    def __init__(self):
        self.dynamic_topics: Dict[str, dict] = {}
    
    def normalize(self, topic: str) -> str:
        """Normalize topic to canonical slug."""
        if not topic:
            return ''
        
        topic = topic.lower().strip()
        
        # Check aliases
        if topic in self.ALIASES:
            return self.ALIASES[topic]
        
        # Make URL-safe
        topic = re.sub(r'[^\w-]', '-', topic)
        topic = re.sub(r'-+', '-', topic)
        
        return topic
    
    def classify(self, text: str, threshold: int = 2) -> List[str]:
        """Classify text to topics based on keyword density."""
        if not text:
            return []
        
        text_lower = text.lower()
        topics = set()
        
        for category, config in self.CATEGORIES.items():
            count = 0
            for keyword in config['keywords']:
                count += text_lower.count(keyword.lower())
            
            if count >= threshold:
                topics.add(config['topics'][0])
        
        return sorted(list(topics))
    
    def get_category(self, topic: str) -> Optional[str]:
        """Get parent category for a topic."""
        topic = self.normalize(topic)
        
        for category, config in self.CATEGORIES.items():
            if topic in config['topics']:
                return category
        
        return None
    
    def get_display(self, topic: str) -> str:
        """Get display name for topic."""
        topic = self.normalize(topic)
        
        for category, config in self.CATEGORIES.items():
            if topic in config['topics']:
                idx = config['topics'].index(topic)
                return topic.replace('-', ' ').title()
        
        return topic.replace('-', ' ').title()
    
    def get_category_display(self, topic: str) -> str:
        """Get category display name."""
        category = self.get_category(topic)
        if category and category in self.CATEGORIES:
            return self.CATEGORIES[category]['display']
        return ''
    
    def register_dynamic(self, topic: str, metadata: dict):
        """Register dynamically discovered topic."""
        slug = self.normalize(topic)
        self.dynamic_topics[slug] = metadata
    
    def get_all_canonical(self) -> List[str]:
        """Get all canonical topics."""
        topics = set()
        for config in self.CATEGORIES.values():
            topics.update(config['topics'])
        topics.update(self.dynamic_topics.keys())
        return sorted(list(topics))


def normalize_topic(topic: str) -> str:
    """Standalone topic normalization."""
    normalizer = TopicNormalizer()
    return normalizer.normalize(topic)


def classify_topics(text: str) -> List[str]:
    """Standalone topic classification."""
    normalizer = TopicNormalizer()
    return normalizer.classify(text)


if __name__ == '__main__':
    normalizer = TopicNormalizer()
    
    test_topics = [
        'buget',
        'codul-fiscal',
        'CODUL FISCAL',
        'justitie',
        'sanatate',
    ]
    
    test_text = """
    Propunerea legislativă pentru completarea Legii nr.227/2015 privind Codul fiscal. 
    
    Dezbaterea și adoptarea Proiectului de hotărâre privind eliberarea din funcție a unui secretar general adjunct al Senatului. 
    
    Dezbaterea și respingerea Propunerii legislative pentru reducerea gradului de recidivă în cadrul reformei legii penale și a condițiilor din penitenciare. 
    
    Aprobarea ordinii de zi și a programului de lucru. 
    """
    
    print("=== Topic Normalizer Tests ===")
    for topic in test_topics:
        normalized = normalizer.normalize(topic)
        category = normalizer.get_category(normalized)
        display = normalizer.get_display(normalized)
        print(f"{topic:20} -> {normalized:15} | {category:10} | {display}")
    
    print("\n=== Topic Classification from Text ===")
    topics = normalizer.classify(test_text)
    for topic in topics:
        display = normalizer.get_display(topic)
        print(f"  {topic:15} -> {display}")
    
    print("\n=== All Canonical Topics ===")
    for topic in normalizer.get_all_canonical():
        print(f"  {topic}")