#!/usr/bin/env python3
"""Merge vault data into knowledge graph - Populate entities.json from existing vault files"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

# Use centralized configuration
try:
    from config import get_config
    config = get_config()
    PROJECT_DIR = config.PROJECT_ROOT
    KG_FILE = config.ENTITIES_FILE
    VAULT_DIR = config.VAULT_DIR
except ImportError:
    PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
    KG_FILE = PROJECT_DIR / "knowledge_graph" / "entities.json"
    VAULT_DIR = PROJECT_DIR / "vault"


def parse_frontmatter(content: str) -> tuple:
    """Parse simple frontmatter from markdown content."""
    metadata = {}
    body_start = 0
    
    if content.startswith('---'):
        end = content.find('---', 3)
        if end > 0:
            fm_text = content[3:end]
            body_start = end + 3
            
            for line in fm_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
    
    return metadata, content[body_start:]


def extract_participants_from_session(filepath: Path) -> List[str]:
    """Extract participant names from session markdown."""
    participants = []
    try:
        content = filepath.read_text(encoding='utf-8')
        metadata, body = parse_frontmatter(content)
        
        # Look for participant list
        in_participants = False
        for line in body.split('\n'):
            if line.strip().startswith('participants:'):
                in_participants = True
                continue
            if in_participants:
                if line.strip().startswith('#') or (line.strip() and not line.startswith(' ') and not line.startswith('-')):
                    break
                if line.strip().startswith('-'):
                    name = line.strip().lstrip('- ').strip()
                    if name and len(name) > 3:
                        participants.append(name)
    except:
        pass
    return participants


def merge_vault_to_kg():
    """Read all vault sessions and populate entities.json."""
    print("=== Merging Vault to Knowledge Graph ===")
    
    # Load existing KG data
    kg_data = {
        'metadata': {
            'version': '2.0',
            'last_updated': datetime.now().isoformat(),
            'sources': ['cdep.ro', 'senat.ro', 'vault'],
            'legislatures': ['2024-2028']
        },
        'persons': [],
        'sessions': [],
        'laws': []
    }
    
    existing_entities = {"persons": {}, "sessions": {}, "laws": {}}
    
    if KG_FILE.exists():
        try:
            existing = json.loads(KG_FILE.read_text())
            # Load existing entities
            for p in existing.get('persons', []):
                if p.get('name'):
                    existing_entities['persons'][p['name']] = p
            for s in existing.get('sessions', []):
                if s.get('id'):
                    existing_entities['sessions'][s['id']] = s
            for l in existing.get('laws', []):
                if l.get('number'):
                    existing_entities['laws'][l['number']] = l
            print(f"Loaded existing KG: {len(existing_entities['persons'])} persons, {len(existing_entities['sessions'])} sessions")
        except:
            print("Could not load existing KG, starting fresh")
    
    # Process deputy sessions
    deputies_dir = VAULT_DIR / "sessions" / "deputies"
    if deputies_dir.exists():
        session_count = 0
        mp_set = set()
        law_set = set()
        
        for session_file in deputies_dir.glob("*.md"):
            if session_file.name == "Index.md":
                continue
            
            try:
                content = session_file.read_text(encoding='utf-8')
                metadata, body = parse_frontmatter(content)
                
                date = metadata.get('date', '') or session_file.stem[:10]
                title = metadata.get('title', session_file.stem)
                url = metadata.get('url', '')
                chamber = metadata.get('chamber', 'deputies')
                laws_str = metadata.get('laws_discussed', '')
                laws = [l.strip() for l in laws_str.split(',') if l.strip() and l.strip() != 'None']
                
                # Extract participants
                participants = extract_participants_from_session(session_file)
                mp_set.update(participants)
                
                # Extract laws
                for law in laws:
                    if law and law not in ['None', '']:
                        law_set.add(law)
                
                # Create session
                session_id = date or session_file.stem
                if session_id not in existing_entities['sessions']:
                    kg_data['sessions'].append({
                        'id': session_id,
                        'date': date,
                        'chamber': chamber,
                        'title': title,
                        'url': url,
                        'participants': participants,
                        'source': 'vault'
                    })
                
                session_count += 1
            except Exception as e:
                print(f"  Error processing {session_file.name}: {e}")
        
        print(f"Processed {session_count} deputy sessions")
        print(f"  Found {len(mp_set)} unique MPs")
        print(f"  Found {len(law_set)} unique laws")
    
    # Process senate sessions
    senate_dir = VAULT_DIR / "sessions" / "senate"
    if senate_dir.exists():
        session_count = 0
        
        for session_file in senate_dir.glob("*.md"):
            if session_file.name == "Index.md":
                continue
            
            try:
                content = session_file.read_text(encoding='utf-8')
                metadata, body = parse_frontmatter(content)
                
                date = metadata.get('date', '') or session_file.stem[:10]
                title = metadata.get('title', session_file.stem)
                url = metadata.get('url', '')
                chamber = metadata.get('chamber', 'senate')
                
                # Extract participants
                participants = extract_participants_from_session(session_file)
                
                # Create session
                session_id = date or session_file.stem
                if session_id not in existing_entities['sessions']:
                    kg_data['sessions'].append({
                        'id': session_id,
                        'date': date,
                        'chamber': chamber,
                        'title': title,
                        'url': url,
                        'participants': participants,
                        'source': 'vault'
                    })
                
                session_count += 1
            except Exception as e:
                print(f"  Error processing senate {session_file.name}: {e}")
        
        print(f"Processed {session_count} senate sessions")
    
    # Add MPs from deputy sessions
    deputy_mp_dir = VAULT_DIR / "politicians" / "deputies"
    if deputy_mp_dir.exists():
        for mp_file in deputy_mp_dir.glob("*.md"):
            if mp_file.name == "Index.md":
                continue
            try:
                name = mp_file.stem.replace("-", " ")
                if name not in existing_entities['persons']:
                    kg_data['persons'].append({
                        'id': f"mp_{len(kg_data['persons']) + 1}",
                        'name': name,
                        'chamber': 'deputies',
                        'appearances': [],
                        'source': 'vault'
                    })
            except:
                pass
    
    # Add senators
    senator_mp_dir = VAULT_DIR / "politicians" / "senators"
    if senator_mp_dir.exists():
        for mp_file in senator_mp_dir.glob("*.md"):
            if mp_file.name == "Index.md":
                continue
            try:
                name = mp_file.stem.replace("-", " ")
                if name not in existing_entities['persons']:
                    kg_data['persons'].append({
                        'id': f"sen_{len(kg_data['persons']) + 1}",
                        'name': name,
                        'chamber': 'senate',
                        'appearances': [],
                        'source': 'vault'
                    })
            except:
                pass
    
    # Save updated KG
    with open(KG_FILE, 'w', encoding='utf-8') as f:
        json.dump(kg_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== Knowledge Graph Updated ===")
    print(f"Persons: {len(kg_data['persons'])}")
    print(f"Sessions: {len(kg_data['sessions'])}")
    print(f"Laws: {len(kg_data['laws'])}")
    print(f"File: {KG_FILE}")
    
    return kg_data


if __name__ == "__main__":
    merge_vault_to_kg()