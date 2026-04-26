#!/usr/bin/env python3
"""
Remove all placeholder text from vault files
Phase 4: Remove Placeholders

Replaces: "(Track from proposals)", "(To be filled)", empty data
"""

import os
import re
from datetime import datetime

TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    print(f"[{TIMESTAMP}] {msg}")

def remove_placeholders():
    """Remove all placeholder text"""
    log("Starting Phase 4: Remove Placeholders")
    
    replacements = [
        ("- (Track from proposals)", "- (No co-sponsors data available)"),
        ("- (Track from voting data)", "- (No voting records available)"),
        ("- (Link to voting data)", "- (No voting records available)"),
        ("- (To be filled)", "- (Data not available)"),
    ]
    
    total_files = 0
    total_replacements = 0
    
    # Walk entire vault
    for root, dirs, files in os.walk("vault"):
        for filename in files:
            if not filename.endswith('.md'):
                continue
            
            filepath = os.path.join(root, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            
            for old, new in replacements:
                if old in content:
                    content = content.replace(old, new)
                    total_replacements += 1
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                total_files += 1
    
    log(f"Phase 4 complete: Updated {total_files} files with {total_replacements} replacements")
    
    # Verify
    verify_count = 0
    for root, dirs, files in os.walk("vault"):
        for filename in files:
            if not filename.endswith('.md'):
                continue
            filepath = os.path.join(root, filename)
            with open(filepath, 'r') as f:
                if "(Track from proposals)" in f.read():
                    verify_count += 1
    
    log(f"Verification: {verify_count} files still with placeholders")
    
    return total_files, total_replacements

if __name__ == "__main__":
    remove_placeholders()