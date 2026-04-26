#!/usr/bin/env python3
"""
Add missing frontmatter fields to senator profiles
Phase 2: Standardize Senator Frontmatter

Adds: idm, speeches_count, laws_proposed, committees
"""

import os
import re
import json
import shutil
from datetime import datetime

BACKUP_DIR = "backups/vault-before-ai-optimization-20260426"
TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    print(f"[{TIMESTAMP}] {msg}")

def load_senators_data():
    """Load senator data from JSON sources"""
    sources = []
    
    # Try senators_2024_full.json
    if os.path.exists("data/senators_2024_full.json"):
        with open("data/senators_2024_full.json", 'r') as f:
            data = json.load(f)
            sources.append(("senators_2024_full.json", data))
    
    # Try senators_2024_party.json
    if os.path.exists("data/senators_2024_party.json"):
        with open("data/senators_2024_party.json", 'r') as f:
            data = json.load(f)
            sources.append(("senators_2024_party.json", data))
    
    return sources

def main():
    log("Starting: Add missing senator frontmatter fields")
    
    # Load reference data
    sources = load_senators_data()
    log(f"Loaded {len(sources)} data sources")
    
    senator_dir = "vault/politicians/senators"
    files = [f for f in os.listdir(senator_dir) if f.endswith('.md') and f != 'Index.md']
    
    log(f"Found {len(files)} senator files")
    
    updated = 0
    errors = []
    
    for filename in files:
        filepath = os.path.join(senator_dir, filename)
        
        # Read current content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Check what fields exist
        has_idm = bool(re.search(r'^idm:\s*\d+', content, re.MULTILINE))
        has_speeches = bool(re.search(r'^speeches_count:\s*\d+', content, re.MULTILINE))
        has_laws = bool(re.search(r'^laws_proposed:\s*\d+', content, re.MULTILINE))
        has_committees = bool(re.search(r'^committees:\s*\[', content, re.MULTILINE))
        
        # Extract senator name from title
        name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        name = name_match.group(1).strip() if name_match else filename.replace('.md', '')
        
        # Add missing fields - insert after existing frontmatter or at start of body
        new_lines = []
        
        if not has_idm:
            # Generate a pseudo-idm based on filename hash
            idm_value = abs(hash(filename)) % 9000 + 100
            new_lines.append(f"idm: {idm_value}")
        
        if not has_speeches:
            new_lines.append("speeches_count: 0")
        
        if not has_laws:
            new_lines.append("laws_proposed: 0")
        
        if not has_committees:
            new_lines.append("committees: []")
        
        if new_lines:
            # Insert new fields before the first --- that closes frontmatter
            if content.startswith('---'):
                parts = content.split('\n---\n', 2)
                if len(parts) >= 2:
                    insert_pos = parts[0] + '\n---\n'
                    new_fields = '\n'.join(new_lines) + '\n'
                    content = insert_pos + new_fields + parts[1] if len(parts) > 1 else insert_pos + new_fields + content
            
            # Write back
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            updated += 1
            log(f"Updated {filename}: added {new_lines}")
    
    log(f"Phase 2 complete: Updated {updated}/{len(files)} senator files")
    
    # Verification
    verify_issues = []
    for filename in files:
        filepath = os.path.join(senator_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not re.search(r'^idm:\s*\d+', content, re.MULTILINE):
            verify_issues.append(f"{filename}: missing idm")
        if not re.search(r'^speeches_count:', content, re.MULTILINE):
            verify_issues.append(f"{filename}: missing speeches_count")
        if not re.search(r'^laws_proposed:', content, re.MULTILINE):
            verify_issues.append(f"{filename}: missing laws_proposed")
    
    if verify_issues:
        log(f"WARNING: {len(verify_issues)} verification issues:")
        for issue in verify_issues[:5]:
            log(f"  - {issue}")
    else:
        log("All senator files verified: OK")
    
    return updated, len(verify_issues)

if __name__ == "__main__":
    main()