#!/usr/bin/env python3
"""
Add AI-optimized fields to politician profiles
Phase 5: Add AI-Optimized Fields

Adds: ai_friendly_name, search_aliases, activity_score calculation
"""

import os
import re
from datetime import datetime

TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    print(f"[{TIMESTAMP}] {msg}")

def add_ai_fields():
    log("Starting Phase 5: Add AI-Optimized Fields")
    
    updated = 0
    
    # Process deputies
    deputy_dir = "vault/politicians/deputies"
    for filename in os.listdir(deputy_dir):
        if not filename.endswith('.md'):
            continue
        
        filepath = os.path.join(deputy_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already has AI fields
        if 'ai_friendly_name:' in content:
            continue
        
        # Extract name for AI-friendly version
        name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        if not name_match:
            continue
        
        name = name_match.group(1).strip()
        
        # Calculate activity score
        laws_match = re.search(r'^laws_proposed:\s*(\d+)', content, re.MULTILINE)
        speeches_match = re.search(r'^speeches_count:\s*(\d+)', content, re.MULTILINE)
        
        laws = int(laws_match.group(1)) if laws_match else 0
        speeches = int(speeches_match.group(1)) if speeches_match else 0
        activity_score = laws + speeches
        
        # Create search aliases (simple version)
        aliases = [name.upper(), name.lower()]
        
        # Add AI fields at end of frontmatter
        # Find the closing --- of frontmatter
        parts = content.split('\n---\n', 1)
        if len(parts) < 2:
            continue
        
        frontmatter = parts[0]
        body = parts[1]
        
        # Add new fields
        new_fields = f"ai_friendly_name: {name}\nsearch_aliases: {aliases}\nactivity_score: {activity_score}\n"
        
        content = frontmatter + '\n---\n' + new_fields + body
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        updated += 1
    
    log(f"Updated {updated} deputy profiles with AI fields")
    
    # Process senators  
    senator_dir = "vault/politicians/senators"
    for filename in os.listdir(senator_dir):
        if not filename.endswith('.md') or filename == 'Index.md':
            continue
        
        filepath = os.path.join(senator_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'ai_friendly_name:' in content:
            continue
        
        # Extract name
        name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if not name_match:
            continue
        
        name = name_match.group(1).strip()
        
        # Calculate activity score
        laws_match = re.search(r'^laws_proposed:\s*(\d+)', content, re.MULTILINE)
        speeches_match = re.search(r'^speeches_count:\s*(\d+)', content, re.MULTILINE)
        
        laws = int(laws_match.group(1)) if laws_match else 0
        speeches = int(speeches_match.group(1)) if speeches_match else 0
        activity_score = laws + speeches
        
        aliases = [name.upper(), name.lower()]
        
        # Find closing ---
        parts = content.split('\n---\n', 1)
        if len(parts) < 2:
            continue
        
        frontmatter = parts[0]
        body = parts[1]
        
        new_fields = f"ai_friendly_name: {name}\nsearch_aliases: {aliases}\nactivity_score: {activity_score}\n"
        
        content = frontmatter + '\n---\n' + new_fields + body
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        updated += 1
    
    log(f"Phase 5 complete: Updated {updated} total profiles")
    log("All profiles now have AI-optimized fields")
    
    return updated

if __name__ == "__main__":
    add_ai_fields()