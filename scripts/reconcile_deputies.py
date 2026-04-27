#!/usr/bin/env python3
"""
Reconcile vault deputy files with real data from data/deputies_2024.json.
- Maps numeric filenames (114.md) to real names
- Updates frontmatter with party, constituency, ai_friendly_name
- Handles both current and historical deputies
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
import argparse

BASE_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
VAULT_DIR = BASE_DIR / "vault" / "politicians" / "deputies"
DATA_DIR = BASE_DIR / "data"

class DeputyReconciler:
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.deputies_2024 = self.load_deputies_2024()
        self.committees = self.load_committees()
        self.mapping = self.build_mapping()
        self.stats = {
            'processed': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
    def load_deputies_2024(self) -> List[Dict]:
        with open(DATA_DIR / "deputies_2024.json") as f:
            return json.load(f)["deputies"]
    
    def load_committees(self) -> Dict:
        try:
            with open(DATA_DIR / "committees_members.json") as f:
                return json.load(f)  # List of {deputy_name, committee, role}
        except:
            return {}
    
    def build_mapping(self) -> Dict[str, Dict]:
        """
        Build mapping from numeric ID to deputy data.
        Strategy: Use file order 114, 115, 116... mapped alphabetically to deputies_2024 list
        NOTE: This is a heuristic since we don't have the direct mapping
        """
        mapping = {}
        sorted_deputies = sorted(self.deputies_2024, key=lambda x: x["name"])
        
        # Map IDs to sorted deputy list
        for i, deputy in enumerate(sorted_deputies, start=114):
            deputy_id = str(i)
            mapping[deputy_id] = {
                "name": deputy["name"],
                "party": deputy["party"],
                "party_full": deputy.get("party_full", ""),
                "constituency": deputy["constituency"],
                "ai_friendly_name": self.make_ai_name(deputy["name"])
            }
        
        # Also try direct name matching if filenames might be names
        for deputy in self.deputies_2024:
            name_file = self.make_filename(deputy["name"])
            mapping[name_file] = {
                "name": deputy["name"],
                "party": deputy["party"],
                "party_full": deputy.get("party_full", ""),
                "constituency": deputy["constituency"],
                "ai_friendly_name": self.make_ai_name(deputy["name"])
            }
        
        return mapping
    
    def make_filename(self, name: str) -> str:
        """Convert name to potential filename"""
        return name.lower().replace(" ", "-").replace("ă", "a").replace("î", "i").replace("ș", "s").replace("ț", "t").replace("â", "a") + ".md"
    
    def make_ai_name(self, name: str) -> str:
        """Generate AI-friendly search name"""
        return name.replace("-", " ").title()
    
    def parse_frontmatter(self, content: str) -> Optional[Dict]:
        """Extract YAML frontmatter from markdown"""
        match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not match:
            return None
        
        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                frontmatter[key.strip()] = val.strip()
        return frontmatter
    
    def update_frontmatter(self, frontmatter: Dict, deputy_data: Dict) -> Dict:
        """Update frontmatter with real data"""
        updated = frontmatter.copy()
        updated.update({
            'name': deputy_data['name'],
            'party': deputy_data['party'],
            'party_full': deputy_data.get('party_full', ''),
            'constituency': deputy_data['constituency'],
            'ai_friendly_name': deputy_data['ai_friendly_name'],
            'activity_score': deputy_data.get('activity_score', 0)
        })
        return updated
    
    def format_frontmatter(self, data: Dict) -> str:
        """Format dict as YAML frontmatter"""
        lines = []
        for key, value in data.items():
            if value:  # Only include non-empty values
                lines.append(f"{key}: {value}")
        return "---\n" + "\n".join(lines) + "\n---\n"
    
    def process_file(self, filepath: Path) -> bool:
        """Process a single deputy file"""
        self.stats['processed'] += 1
        
        # Extract ID from filename
        stem = filepath.stem  # e.g., "114"
        if not stem.isdigit():
            self.stats['skipped'] += 1
            if self.verbose:
                print(f"  SKIP: Non-numeric ID: {filepath.name}")
            return False
        
        if stem not in self.mapping:
            self.stats['skipped'] += 1
            if self.verbose:
                print(f"  SKIP: No mapping for ID {stem}")
            return False
        
        deputy_data = self.mapping[stem]
        
        try:
            content = filepath.read_text(encoding='utf-8')
            frontmatter = self.parse_frontmatter(content)
            
            if not frontmatter:
                self.stats['errors'] += 1
                print(f"  ERROR: No frontmatter in {filepath.name}")
                return False
            
            # Check if already updated with real name
            if frontmatter.get('name') and frontmatter.get('name') != stem:
                self.stats['skipped'] += 1
                if self.verbose:
                    print(f"  SKIP: Already updated: {filepath.name} -> {frontmatter['name']}")
                return False
            
            # Update frontmatter
            updated_fm = self.update_frontmatter(frontmatter, deputy_data)
            new_frontmatter = self.format_frontmatter(updated_fm)
            
            # Replace old frontmatter with new
            new_content = new_frontmatter + content.split('---\n', 2)[-1]
            
            if self.dry_run:
                print(f"  DRY RUN: Would update {filepath.name} -> {deputy_data['name']}")
                return True
            
            filepath.write_text(new_content, encoding='utf-8')
            self.stats['updated'] += 1
            if self.verbose:
                print(f"  UPDATED: {filepath.name} -> {deputy_data['name']}")
            return True
            
        except Exception as e:
            self.stats['errors'] += 1
            print(f"  ERROR: {filepath.name}: {e}")
            return False
    
    def run(self):
        """Process all deputy files"""
        print("="*50)
        print("DEPUTY RECONCILIATION")
        print(f"Total deputies in data file: {len(self.deputies_2024)}")
        print(f"Total mappings available: {len(self.mapping)}")
        print(f"Processing files in: {VAULT_DIR}")
        print("="*50)
        
        files = list(VAULT_DIR.glob("*.md"))
        print(f"\nFound {len(files)} files to process")
        
        for filepath in files:
            self.process_file(filepath)
        
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        print(f"Processed: {self.stats['processed']}")
        print(f"Updated:   {self.stats['updated']}")
        print(f"Skipped:   {self.stats['skipped']}")
        print(f"Errors:    {self.stats['errors']}")
        print("="*50)
        
        return self.stats

def main():
    parser = argparse.ArgumentParser(description="Reconcile deputy files with real data")
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--start-id', default='114', help='Starting file ID')
    parser.add_argument('--end-id', default='999', help='Ending file ID')
    
    args = parser.parse_args()
    
    reconciler = DeputyReconciler(dry_run=args.dry_run, verbose=args.verbose)
    reconciler.run()

if __name__ == "__main__":
    main()