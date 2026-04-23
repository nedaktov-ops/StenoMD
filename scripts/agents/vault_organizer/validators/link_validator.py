#!/usr/bin/env python3
"""
StenoMD Link Validator
Validates wikilinks and detects broken links
"""

import re
from pathlib import Path
from typing import List, Dict, Set


class LinkValidator:
    """Validate wikilinks in Obsidian vault."""
    
    WIKILINK_PATTERN = re.compile(r'\[\[([^\]]+)\]\]')
    
    def __init__(self, vault_dir: Path):
        self.vault_dir = vault_dir
        self.files = self._index_files()
        self.links: Dict[str, Set[str]] = {}
        self.broken_links: List[Dict] = []
    
    def _index_files(self) -> Set[str]:
        """Index all files in vault."""
        files = set()
        
        for md_file in self.vault_dir.rglob('*.md'):
            if '.obsidian' in md_file.parts:
                continue
            
            # Get relative path from vault
            rel_path = md_file.relative_to(self.vault_dir)
            files.add(str(rel_path))
            
            # Also add without extension for wikilinks
            files.add(rel_path.stem)
        
        return files
    
    def validate_file(self, file_path: Path) -> List[Dict]:
        """Validate all links in a file."""
        if not file_path.exists():
            return [{'file': str(file_path), 'error': 'File not found'}]
        
        content = file_path.read_text(encoding='utf-8')
        errors = []
        
        for match in self.WIKILINK_PATTERN.finditer(content):
            link = match.group(1)
            
            # Parse link (might have alias)
            if '|' in link:
                link_target = link.split('|')[0]
            else:
                link_target = link
            
            # Check if link target exists
            if not self._link_exists(link_target):
                errors.append({
                    'file': str(file_path),
                    'link': link_target,
                    'line': content[:match.start()].count('\n') + 1,
                })
        
        return errors
    
    def _link_exists(self, link_target: str) -> bool:
        """Check if link target exists."""
        # Direct file match
        for ext in ['', '.md']:
            if Path(link_target + ext) in self.files:
                return True
            
            # Check in subdirectories
            for file in self.files:
                if file.endswith(link_target + ext):
                    return True
                if file.endswith(link_target):
                    return True
        
        return False
    
    def validate_all(self) -> List[Dict]:
        """Validate all files in vault."""
        all_errors = []
        
        for md_file in self.vault_dir.rglob('*.md'):
            if '.obsidian' in md_file.parts:
                continue
            
            errors = self.validate_file(md_file)
            all_errors.extend(errors)
        
        self.broken_links = all_errors
        return all_errors
    
    def get_broken_links_report(self) -> str:
        """Generate report of broken links."""
        if not self.broken_links:
            return "No broken links found!"
        
        lines = ["Broken Links Report", "=" * 50, ""]
        
        by_file: Dict[str, List] = {}
        for error in self.broken_links:
            file = error['file']
            if file not in by_file:
                by_file[file] = []
            by_file[file].append(error)
        
        for file, errors in sorted(by_file.items()):
            lines.append(f"File: {file}")
            for error in errors:
                lines.append(f"  - Missing link: {error['link']}")
            lines.append("")
        
        lines.append(f"Total broken links: {len(self.broken_links)}")
        
        return '\n'.join(lines)


def validate_links(vault_dir: Path) -> List[Dict]:
    """Standalone link validation."""
    validator = LinkValidator(vault_dir)
    return validator.validate_all()


if __name__ == '__main__':
    from pathlib import Path
    
    vault_dir = Path('/home/adrian/Desktop/NEDAILAB/StenoMD/vault')
    validator = LinkValidator(vault_dir)
    
    print("=== Link Validator ===")
    print(f"Indexed files: {len(validator.files)}")
    
    errors = validator.validate_all()
    print(f"Broken links: {len(errors)}")
    
    if errors:
        print("\nFirst 10 errors:")
        for error in errors[:10]:
            print(f"  {error['file']}: {error['link']}")