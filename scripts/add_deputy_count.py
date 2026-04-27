#!/usr/bin/env python3
"""
Add deputy_count to session files by counting participants.
"""

import yaml
from pathlib import Path

VAULT = Path("vault/sessions")

def add_deputy_count():
    updated = 0
    for session_file in VAULT.rglob("*.md"):
        if session_file.name == "Index.md":
            continue
        try:
            content = session_file.read_text(encoding='utf-8')
            if not content.startswith('---'):
                continue
            parts = content.split('---', 2)
            if len(parts) < 3:
                continue
            fm_text = parts[1]
            body = parts[2]
            try:
                fm = yaml.safe_load(fm_text) or {}
            except:
                continue
            # Skip if already has deputy_count
            if 'deputy_count' in fm:
                continue
            # Count participants from frontmatter list
            participants = fm.get('participants', [])
            if isinstance(participants, list):
                count = len(participants)
            else:
                count = 0
            if count > 0:
                fm['deputy_count'] = count
                # Write back
                new_fm = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
                new_content = f"---\n{new_fm}---\n{body}"
                session_file.write_text(new_content, encoding='utf-8')
                updated += 1
                print(f"{session_file.relative_to(VAULT.parent)} -> deputy_count: {count}")
        except Exception as e:
            print(f"Error {session_file}: {e}")
    print(f"\nUpdated {updated} session files with deputy_count")

if __name__ == "__main__":
    add_deputy_count()
