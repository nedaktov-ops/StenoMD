#!/usr/bin/env python3
"""
StenoMD Link Processor
Generates wikilinks and manages backlink relationships
"""

import sys
from pathlib import Path
from typing import Dict, List, Set


class LinkProcessor:
    """Generate and manage wikilinks."""
    
    def __init__(self, vault_dir: Path):
        self.vault_dir = vault_dir
    
    def generate_session_links(self, session_data: Dict) -> Dict:
        """Generate all links for a session file."""
        links = {
            'politicians': [],
            'laws': [],
            'topics': [],
            'wikilinks': [],
        }
        
        # Speaker links
        for speaker in session_data.get('speakers', []):
            slug = speaker.get('slug', '')
            if slug:
                links['politicians'].append(slug)
                chamber = session_data['chamber']
                folder = 'senate' if chamber == 'senate' else 'deputies'
                links['wikilinks'].append(f"[[politicians/{folder}/{slug}]]")
        
        # Law links
        for law in session_data.get('laws', []):
            law_id = law.get('id', '')
            if law_id:
                links['laws'].append(law_id)
                links['wikilinks'].append(f"[[laws/{law_id}]]")
        
        # Topic links
        for topic in session_data.get('topics', []):
            if topic:
                links['topics'].append(topic)
                links['wikilinks'].append(f"[[topics/{topic}]]")
        
        return links
    
    def generate_person_links(self, person_data: Dict) -> Dict:
        """Generate all links for a person file."""
        links = {
            'sessions': [],
            'parties': [],
            'topics': [],
            'wikilinks': [],
        }
        
        # Session links
        for session in person_data.get('sessions', []):
            sess_id = session.get('id', '')
            sess_date = session.get('date', '')
            chamber = session.get('chamber', person_data.get('chamber', 'senate'))
            folder = 'senate' if chamber == 'senate' else 'deputies'
            
            if sess_id:
                links['sessions'].append(sess_id)
                links['wikilinks'].append(f"[[sessions/{folder}/{sess_date}]]")
        
        # Party link
        party = person_data.get('party')
        if party:
            links['parties'].append(party)
            links['wikilinks'].append(f"[[parties/{party}]]")
        
        # Topic links from positions
        for pos in person_data.get('positions', []):
            topic = pos.get('topic')
            if topic:
                links['topics'].append(topic)
                links['wikilinks'].append(f"[[topics/{topic}]]")
        
        return links
    
    def generate_law_links(self, law_data: Dict) -> Dict:
        """Generate all links for a law file."""
        links = {
            'sessions': [],
            'topics': [],
            'politicians': [],
            'wikilinks': [],
        }
        
        # Session links
        for session in law_data.get('sessions', []):
            sess_id = session.get('id', '')
            sess_date = session.get('date', '')
            chamber = session.get('chamber', 'senate')
            folder = 'senate' if chamber == 'senate' else 'deputies'
            
            if sess_id:
                links['sessions'].append(sess_id)
                links['wikilinks'].append(f"[[sessions/{folder}/{sess_date}]]")
        
        # Topic link
        topic = law_data.get('topic')
        if topic:
            links['topics'].append(topic)
            links['wikilinks'].append(f"[[topics/{topic}]]")
        
        return links
    
    def build_backlinks(self, entity_type: str, entity_id: str) -> List[Dict]:
        """
        Find all files that link to this entity.
        
        Returns list of files with their link context.
        """
        backlinks = []
        
        # Search through vault files
        search_in = f"{entity_type}s"
        if entity_type == 'person':
            search_in = 'politicians'
        
        search_dir = self.vault_dir / search_in
        if not search_dir.exists():
            search_dir = self.vault_dir
        
        for md_file in search_dir.rglob('*.md'):
            if '.obsidian' in md_file.parts:
                continue
            
            try:
                content = md_file.read_text(encoding='utf-8')
                
                # Check if file links to entity
                patterns = [
                    f"[[{entity_id}]]",
                    f"[[{entity_type}/{entity_id}]]",
                    f"[[{entity_type}s/{entity_id}]]",
                ]
                
                for pattern in patterns:
                    if pattern in content:
                        index = content.index(pattern)
                        context_start = max(0, index - 100)
                        context_end = min(len(content), index + 100)
                        context = content[context_start:context_end]
                        
                        backlinks.append({
                            'file': str(md_file.relative_to(self.vault_dir)),
                            'context': context,
                        })
                        break
            except Exception:
                continue
        
        return backlinks
    
    def verify_links(self, content: str) -> Dict:
        """Verify all links in content exist."""
        import re
        
        wikilink_pattern = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]]')
        
        existing_files = self._get_existing_files()
        broken = []
        valid = []
        
        for match in wikilink_pattern.finditer(content):
            link = match.group(1)
            
            if self._link_exists(link, existing_files):
                valid.append(link)
            else:
                broken.append(link)
        
        return {
            'valid': valid,
            'broken': broken,
            'valid_count': len(valid),
            'broken_count': len(broken),
        }
    
    def _get_existing_files(self) -> Set[str]:
        """Get all existing files relative paths."""
        files = set()
        for md_file in self.vault_dir.rglob('*.md'):
            if '.obsidian' in md_file.parts:
                continue
            
            rel = md_file.relative_to(self.vault_dir)
            files.add(str(rel))
            files.add(rel.stem)
        
        return files
    
    def _link_exists(self, link: str, existing_files: Set[str]) -> bool:
        """Check if link target exists."""
        for ext in ['', '.md']:
            if Path(link + ext) in existing_files:
                return True
        
        for f in existing_files:
            if f.endswith(link) or f.endswith(link + '.md'):
                return True
        
        return False


def generate_links(entity_type: str, entity_data: Dict, vault_dir: Path) -> Dict:
    """Standalone link generation."""
    processor = LinkProcessor(vault_dir)
    
    if entity_type == 'session':
        return processor.generate_session_links(entity_data)
    elif entity_type == 'person':
        return processor.generate_person_links(entity_data)
    elif entity_type == 'law':
        return processor.generate_law_links(entity_data)
    
    return {}


if __name__ == '__main__':
    from pathlib import Path
    
    vault_dir = Path('/home/adrian/Desktop/NEDAILAB/StenoMD/vault')
    processor = LinkProcessor(vault_dir)
    
    print("=== Link Processor Test ===")
    
    test_session = {
        'chamber': 'senate',
        'speakers': [
            {'slug': 'mihai-cotet', 'role': 'presedinte'},
            {'slug': 'vasile-blaga', 'role': 'secretar'},
        ],
        'laws': [
            {'id': 'L14-2026'},
            {'id': 'L95-2026'},
        ],
        'topics': ['buget', 'justitie'],
    }
    
    links = processor.generate_session_links(test_session)
    print(f"Session links: {len(links['wikilinks'])}")
    for link in links['wikilinks']:
        print(f"  {link}")