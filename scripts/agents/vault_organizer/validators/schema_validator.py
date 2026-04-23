#!/usr/bin/env python3
"""
StenoMD Schema Validator
Validates entities against canonical schemas
"""

import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any


class SchemaValidator:
    """Validate entities against YAML schemas."""
    
    def __init__(self):
        self.schemas = self._load_schemas()
    
    def _load_schemas(self) -> Dict:
        """Load all schemas from YAML files."""
        schemas_dir = Path(__file__).parent.parent / 'schemas'
        schemas = {}
        
        for schema_file in schemas_dir.glob('*_schema.yaml'):
            schema_name = schema_file.stem.replace('_schema', '')
            with open(schema_file, 'r', encoding='utf-8') as f:
                schemas[schema_name] = yaml.safe_load(f)
        
        return schemas
    
    def validate_session(self, data: Dict) -> tuple:
        """Validate session data."""
        errors = []
        
        # Required fields
        required = ['id', 'date', 'chamber', 'title', 'source']
        for field in required:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Date format
        if data.get('date'):
            import re
            if not re.match(r'\d{4}-\d{2}-\d{2}', data['date']):
                errors.append(f"Invalid date format: {data['date']}")
        
        # Chamber enum
        if data.get('chamber'):
            if data['chamber'] not in ['senate', 'deputies']:
                errors.append(f"Invalid chamber: {data['chamber']}")
        
        # Word count minimum
        if data.get('word_count', 0) < 100:
            errors.append(f"Word count too low: {data['word_count']}")
        
        # Speakers validation
        if 'speakers' in data and isinstance(data['speakers'], list):
            if len(data['speakers']) == 0:
                errors.append("No speakers in session")
        
        return (len(errors) == 0, errors)
    
    def validate_person(self, data: Dict) -> tuple:
        """Validate person data."""
        errors = []
        
        required = ['id', 'name', 'chamber', 'legislature']
        for field in required:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Name validation
        if data.get('name'):
            parts = data['name'].split()
            if len(parts) < 2:
                errors.append(f"Name too short: {data['name']}")
        
        # Chamber enum
        if data.get('chamber'):
            if data['chamber'] not in ['senate', 'deputies', 'both']:
                errors.append(f"Invalid chamber: {data['chamber']}")
        
        return (len(errors) == 0, errors)
    
    def validate_law(self, data: Dict) -> tuple:
        """Validate law data."""
        errors = []
        
        required = ['id', 'number', 'legislature']
        for field in required:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Law ID format
        if data.get('id'):
            import re
            if not re.match(r'^L?\d+-\d{4}$', data['id']):
                errors.append(f"Invalid law ID format: {data['id']}")
        
        return (len(errors) == 0, errors)
    
    def validate(self, entity_type: str, data: Dict) -> tuple:
        """Validate any entity type."""
        validators = {
            'session': self.validate_session,
            'person': self.validate_person,
            'law': self.validate_law,
        }
        
        validator = validators.get(entity_type)
        if validator:
            return validator(data)
        
        return (False, [f"Unknown entity type: {entity_type}"])


def validate(entity_type: str, data: Dict) -> tuple:
    """Standalone validation."""
    validator = SchemaValidator()
    return validator.validate(entity_type, data)


if __name__ == '__main__':
    validator = SchemaValidator()
    
    print("=== Schema Validator ===")
    print(f"Loaded schemas: {list(validator.schemas.keys())}")
    
    # Test session validation
    test_session = {
        'id': 'session_senate_2026-04-01',
        'date': '2026-04-01',
        'chamber': 'senate',
        'title': 'Test Session',
        'source': 'senat.ro',
        'word_count': 500,
        'speakers': [{'name': 'Mihai Coteț'}],
    }
    
    valid, errors = validator.validate_session(test_session)
    print(f"\nSession validation: {'PASS' if valid else 'FAIL'}")
    if errors:
        for error in errors:
            print(f"  Error: {error}")