#!/usr/bin/env python3
"""
StenoMD Vault Analyzer & Cleaner
Analyzes the vault for issues and provides cleanup utilities.
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict

VAULT_DIR = Path("vault")
DATA_DIR = Path("data")

class VaultAnalyzer:
    def __init__(self):
        self.issues = defaultdict(list)
        self.stats = {}
        
    def analyze(self):
        print("=== StenoMD Vault Analysis ===\n")
        
        # 1. Count profiles
        deputies = list(VAULT_DIR.glob("politicians/deputies/*.md"))
        senators = list(VAULT_DIR.glob("politicians/senators/*.md"))
        
        print(f"Deputy profiles: {len(deputies)}")
        print(f"Senator profiles: {len(senators)}")
        print(f"Expected: 332 deputies, 136 senators (2024 legislature)")
        print(f"ISSUE: {len(deputies) - 332} extra deputy profiles\n")
        
        # 2. Check missing fields
        missing_idm = 0
        missing_party = 0
        missing_constituency = 0
        missing_speeches = 0
        missing_laws = 0
        missing_committees = 0
        
        for f in deputies:
            content = f.read_text(encoding='utf-8')
            if not self._has_field(content, 'idm'): missing_idm += 1
            if not self._has_field(content, 'party'): missing_party += 1
            if not self._has_field(content, 'constituency'): missing_constituency += 1
            if not self._has_field(content, 'speeches_count'): missing_speeches += 1
            if not self._has_field(content, 'laws_proposed'): missing_laws += 1
            if not self._has_field(content, 'committees'): missing_committees += 1
        
        print("=== Deputy Profile Completeness ===")
        print(f"Missing idm: {missing_idm}")
        print(f"Missing party: {missing_party}")
        print(f"Missing constituency: {missing_constituency}")
        print(f"Missing speeches_count: {missing_speeches}")
        print(f"Missing laws_proposed: {missing_laws}")
        print(f"Missing committees: {missing_committees}")
        print()
        
        # 3. Check senators
        missing_senator_party = 0
        for f in senators:
            content = f.read_text(encoding='utf-8')
            if not self._has_field(content, 'party'): missing_senator_party += 1
            
        print(f"=== Senator Profile Completeness ===")
        print(f"Missing party: {missing_senator_party}")
        print()
        
        # 4. Find duplicates
        print("=== Checking for duplicates ===")
        names = defaultdict(list)
        for f in deputies + senators:
            name = f.stem.lower()
            names[name].append(f)
        
        duplicates = {k: v for k, v in names.items() if len(v) > 1}
        if duplicates:
            print(f"Found {len(duplicates)} duplicate names:")
            for name, files in list(duplicates.items())[:5]:
                print(f"  {name}: {len(files)} files")
        else:
            print("No exact duplicate names found")
        print()
        
        # 5. Check data files
        print("=== Data Files ===")
        for f in DATA_DIR.glob("*.json"):
            size = f.stat().st_size
            print(f"  {f.name}: {size} bytes")
        print()
        
        # 6. Agent/script status
        print("=== Scripts & Agents ===")
        agents = list(Path("scripts").glob("**/agent*.py"))
        print(f"Found {len(agents)} agent files")
        for a in agents[:5]:
            print(f"  {a.relative_to('scripts')}")
        print()
        
        # 7. Dataview queries
        queries = list(VAULT_DIR.glob("_scripts/dataview/*.md"))
        print(f"=== Dataview Queries: {len(queries)} ===")
        for q in queries:
            print(f"  {q.name}")
        
    def _has_field(self, content: str, field: str) -> bool:
        lines = content.split('\n')
        for line in lines[:20]:  # Check frontmatter
            if line.strip().startswith(f"{field}:"):
                return True
        return False
    
    def fix_missing_fields(self):
        """Fill missing fields from data sources."""
        print("\n=== Fixing Missing Fields ===\n")
        
        # Load activity stats
        activity_file = DATA_DIR / "deputy_activity_stats.json"
        if activity_file.exists():
            data = json.loads(activity_file.read_text())
            stats_map = {str(d['idm']): d for d in data}
            print(f"Loaded activity stats for {len(stats_map)} deputies")
        
        # Load senators data
        senators_file = DATA_DIR / "senators_2024_full.json"
        if senators_file.exists():
            data = json.loads(senators_file.read_text())
            senators = {s['name'].lower(): s for s in data['senators']}
            print(f"Loaded {len(senators)} senators data")
        
    def find_orphans(self):
        """Find orphaned files."""
        print("\n=== Finding Orphaned Files ===\n")
        # All files that are not linked
        all_files = set()
        linked_files = set()
        
        for f in VAULT_DIR.glob("**/*.md"):
            if f.name.startswith('.'): continue
            all_files.add(f.name)
            
        # Simple check: files with no links
        orphans = []
        for f in VAULT_DIR.glob("politicians/**/*.md"):
            content = f.read_text()
            links = content.count('[[') + content.count('](http')
            if links == 0:
                orphans.append(f)
        
        print(f"Orphaned files (no links): {len(orphans)}")
        for f in orphans[:10]:
            print(f"  {f.relative_to(VAULT_DIR)}")

def main():
    analyzer = VaultAnalyzer()
    analyzer.analyze()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        analyzer.fix_missing_fields()
    elif len(sys.argv) > 1 and sys.argv[1] == '--orphans':
        analyzer.find_orphans()

if __name__ == "__main__":
    main()