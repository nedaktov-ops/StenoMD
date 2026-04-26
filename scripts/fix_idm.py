#!/usr/bin/env python3
"""
Fix incorrect idm values by extracting from URL field.
"""

import re
from pathlib import Path

VAULT_DIR = Path("vault")

def extract_idm_from_url(content: str) -> str:
    """Extract idm from URL in content."""
    match = re.search(r'idm=(\d+)', content)
    return match.group(1) if match else ''

def main():
    print("=== Fixing incorrect idm values ===\n")
    
    deputy_files = list(VAULT_DIR.glob("politicians/deputies/*.md"))
    fixed = 0
    
    for f in deputy_files:
        content = f.read_text(encoding='utf-8')
        
        # Get current idm from frontmatter
        match = re.search(r'^idm:\s*(\d+)', content, re.MULTILINE)
        current_idm = match.group(1) if match else ''
        
        # Get idm from URL
        url_idm = extract_idm_from_url(content)
        
        # If they don't match, fix it
        if current_idm and url_idm and current_idm != url_idm:
            print(f"Fixing {f.stem}: idm {current_idm} -> {url_idm}")
            new_content = re.sub(
                r'^(idm:\s*)\d+',
                rf'\1{url_idm}',
                content,
                flags=re.MULTILINE
            )
            f.write_text(new_content, encoding='utf-8')
            fixed += 1
    
    print(f"\nFixed: {fixed} files")

if __name__ == "__main__":
    main()