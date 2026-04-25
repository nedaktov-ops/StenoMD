#!/usr/bin/env python3
"""
Enrich law profiles from session data.
Creates law profiles with metadata from sessions.
"""

import re
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
VAULT_LAWS_DIR = PROJECT_DIR / "vault/laws"
SESSIONS_DIR = PROJECT_DIR / "vault/sessions"


def collect_law_numbers() -> Dict[str, Dict]:
    """Collect all law numbers from sessions"""
    laws = {}
    
    # Scan both chambers
    for chamber_dir in [SESSIONS_DIR / "deputies", SESSIONS_DIR / "senate"]:
        if not chamber_dir.exists():
            continue
        
        for session_file in chamber_dir.glob("*.md"):
            if session_file.name == "Index.md":
                continue
            
            try:
                content = session_file.read_text(encoding='utf-8')
                
                # Find laws_discussed in frontmatter
                match = re.search(r'laws_discussed:\s*\[?([^\]\n]+)', content)
                if match:
                    law_str = match.group(1)
                    # Parse law numbers (format: "59/2026, 607/2025, ...")
                    law_nums = re.findall(r'(\d+/\d{4})', law_str)
                    
                    for law_num in law_nums:
                        if law_num not in laws:
                            laws[law_num] = {
                                'law_number': law_num,
                                'sessions': []
                            }
                        laws[law_num]['sessions'].append(session_file.stem)
                
            except Exception:
                continue
    
    return laws


def create_law_profile(law_data: Dict) -> str:
    """Create law markdown profile"""
    law_num = law_data.get('law_number', 'Unknown')
    year = law_num.split('/')[-1] if '/' in law_num else ''
    num = law_num.split('/')[0] if '/' in law_num else law_num
    sessions = law_data.get('sessions', [])
    
    content = f"""---
tags:
- law
law_number: "{law_num}"
title: "Law {law_num}"
title_short: "Law {num}"
chamber: senate
status: discussed
year: {year}
date_proposed: ""
date_adopted: ""
sessions_count: {len(sessions)}
---

# {law_num}: Law {law_num}

## Details

- **Number**: {law_num}
- **Year**: {year}
- **Status**: Discussed in parliament
- **Sessions**: {len(sessions)}

## Tags

#law #{year}
"""
    
    return content


def main():
    """Main entry point"""
    print("=" * 60)
    print("Law Profile Enrichment")
    print("=" * 60)
    
    # Collect law numbers from sessions
    laws = collect_law_numbers()
    print(f"Found {len(laws)} unique law numbers in sessions")
    
    if not laws:
        print("No laws found - nothing to update")
        return 0
    
    # Show sample
    for ln in list(laws.keys())[:10]:
        print(f"  {ln}")
    
    # Create/update law profiles
    VAULT_LAWS_DIR.mkdir(parents=True, exist_ok=True)
    
    updated = 0
    for law_num, law_data in laws.items():
        # Clean filename
        filename = law_num.replace('/', '-')
        
        # Skip if filename has invalid chars
        if not re.match(r'^\d+-\d+$', filename):
            continue
        
        filepath = VAULT_LAWS_DIR / f"{filename}.md"
        
        # Check if needs update
        needs_update = False
        
        if filepath.exists():
            # Check if minimal content
            content = filepath.read_text(encoding='utf-8')
            if 'Source: N/A' in content or len(content) < 150:
                needs_update = True
        else:
            needs_update = True
        
        if needs_update:
            content = create_law_profile(law_data)
            filepath.write_text(content, encoding='utf-8')
            updated += 1
    
    print(f"\nUpdated: {updated} law profiles")
    
    print("\n" + "=" * 60)
    print("Complete")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())