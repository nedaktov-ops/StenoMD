#!/usr/bin/env python3
"""Update search_aliases for all deputy files with proper name variations."""

import json
import re
from pathlib import Path

VAULT_DIR = Path("vault/politicians/deputies")

def build_name_aliases(name: str) -> list:
    """Generate search aliases from a name"""
    # Clean name: Title Case, handle hyphens
    clean = name.replace('-', ' ').strip()
    parts = clean.split()
    
    aliases = set()
    
    # Full name variations
    aliases.add(name)
    aliases.add(name.upper())
    aliases.add(name.lower())
    aliases.add(name.title())
    
    # First Last
    if len(parts) >= 2:
        first = parts[0]
        last = parts[-1]
        aliases.add(f"{first} {last}")
        aliases.add(f"{first.upper()} {last.upper()}")
        aliases.add(f"{first.lower()} {last.lower()}")
        # Comma format: Last, First
        aliases.add(f"{last}, {first}")
        aliases.add(f"{last.upper()}, {first.upper()}")
    
    # Only last name
    if len(parts) >= 1:
        aliases.add(parts[-1])
        aliases.add(parts[-1].upper())
        aliases.add(parts[-1].lower())
    
    # Remove any empty or single-char aliases
    aliases = {a for a in aliases if a and len(a) > 1}
    
    return sorted(list(aliases))

def main():
    print("Updating search_aliases for all deputy files...")
    
    files = list(VAULT_DIR.glob("*.md"))
    updated = 0
    
    for f in files:
        content = f.read_text(encoding='utf-8')
        
        # Extract name
        name_match = re.search(r'^name:\s*(.+?)(?:\n|$)', content, re.MULTILINE)
        if not name_match:
            continue
            
        name = name_match.group(1).strip()
        
        # Generate proper aliases
        proper_aliases = build_name_aliases(name)
        aliases_str = json.dumps(proper_aliases, ensure_ascii=False)
        
        # Replace existing search_aliases
        new_content = re.sub(
            r'^search_aliases:.*$',
            f'search_aliases: {aliases_str}',
            content,
            flags=re.MULTILINE
        )
        
        # If no search_aliases existed, add after ai_friendly_name
        if new_content == content:
            # Insert after ai_friendly_name or name
            lines = content.split('\n')
            new_lines = []
            inserted = False
            for i, line in enumerate(lines):
                new_lines.append(line)
                if line.strip().startswith('ai_friendly_name:') and not inserted:
                    new_lines.append(f'search_aliases: {aliases_str}')
                    inserted = True
            if inserted:
                new_content = '\n'.join(new_lines)
            else:
                # Fallback: add after name in frontmatter
                new_lines = []
                in_fm = False
                for line in lines:
                    new_lines.append(line)
                    if line.strip().startswith('name:') and not inserted:
                        new_lines.append(f'search_aliases: {aliases_str}')
                        inserted = True
                new_content = '\n'.join(new_lines)
        
        if new_content != content:
            f.write_text(new_content, encoding='utf-8')
            updated += 1
    
    print(f"Updated search_aliases for {updated} files")

if __name__ == "__main__":
    main()