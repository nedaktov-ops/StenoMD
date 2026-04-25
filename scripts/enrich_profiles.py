#!/usr/bin/env python3
"""
Data enrichment script - enrich deputy profiles with Open Parliament RO data.
Uses data/parlamint/open-parliament-ro/data/2024/full-deputies/ to enrich vault profiles.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import yaml

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
OPEN_PARLIAMENT_DIR = PROJECT_DIR / "data/parlamint/open-parliament-ro/data/2024/full-deputies"
VAULT_DEPUTIES_DIR = PROJECT_DIR / "vault/politicians/deputies"


def normalize_name(name: str) -> str:
    """Normalize name: 'Mirela Elena ADOMNICĂI' -> 'Mirela Elena Adomnicăi'."""
    if not name:
        return ""
    name = name.strip()
    parts = name.split()
    normalized = []
    for part in parts:
        if part.isupper() and len(part) > 1:
            part = part.title()
        normalized.append(part)
    return " ".join(normalized)


def slug_from_name(name: str) -> str:
    """Create filename-safe slug from name."""
    name = normalize_name(name)
    slug = re.sub(r'[^a-zA-Z\-]', '-', name)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-').lower()


def load_open_parliament_deputies() -> Dict[str, Dict]:
    """Load all Open Parliament deputy data."""
    deputies = {}
    
    if not OPEN_PARLIAMENT_DIR.exists():
        print(f"Warning: Open Parliament directory not found: {OPEN_PARLIAMENT_DIR}")
        return deputies
    
    for filepath in OPEN_PARLIAMENT_DIR.glob("*.json"):
        try:
            with open(filepath) as f:
                data = json.load(f)
            
            deputy_data = data.get('data', {})
            idm = deputy_data.get('idm', filepath.stem)
            
            name = normalize_name(deputy_data.get('name', ''))
            party = deputy_data.get('party', {}).get('abbrev', '')
            party_full = deputy_data.get('party', {}).get('name', '')
            constituency = deputy_data.get('district', {}).get('name', '')
            photo_url = deputy_data.get('photoUrl', '')
            url = deputy_data.get('url', '')
            
            activity = deputy_data.get('activity', {})
            speeches_count = activity.get('Luări de cuvânt', {}).get('count', 0)
            laws_proposed = activity.get('Propuneri legislative iniţiate', {}).get('count', 0)
            
            deputies[idm] = {
                'name': name,
                'slug': slug_from_name(name),
                'party': party,
                'party_full': party_full,
                'constituency': constituency,
                'photo_url': photo_url,
                'url': url,
                'speeches_count': speeches_count,
                'laws_proposed': laws_proposed,
                'activity': activity
            }
        except Exception as e:
            print(f"Error loading {filepath.name}: {e}")
    
    return deputies


def find_matching_op_deputy(name_slug: str, op_deputies: Dict) -> Optional[Dict]:
    """Find matching Open Parliament deputy by name slug."""
    name_slug_clean = name_slug.replace('-', '').lower()
    
    for idm, op_data in op_deputies.items():
        op_slug_clean = op_data['slug'].replace('-', '').lower()
        
        if name_slug_clean == op_slug_clean:
            return op_data
        
        if name_slug_clean in op_slug_clean or op_slug_clean in name_slug_clean:
            return op_data
    
    for idm, op_data in op_deputies.items():
        op_first = op_data['name'].split()[0].lower()
        if op_first in name_slug.lower() or name_slug.lower().split()[0] in op_first:
            return op_data
    
    return None


def enrich_deputy_profile(filepath: Path, op_data: Dict) -> Tuple[bool, List[str]]:
    """Enrich a single deputy profile with Open Parliament data."""
    changes = []
    
    content = filepath.read_text()
    fm, body = parse_frontmatter(content)
    
    if not fm:
        fm = {}
    
    old_fm = dict(fm)
    
    if op_data.get('party') and not fm.get('party'):
        fm['party'] = op_data['party']
        changes.append(f"party: None -> {op_data['party']}")
    
    if op_data.get('party_full') and not fm.get('party_full'):
        fm['party_full'] = op_data['party_full']
        changes.append(f"party_full: added")
    
    if op_data.get('constituency') and not fm.get('constituency'):
        fm['constituency'] = op_data['constituency']
        changes.append(f"constituency: added")
    
    if op_data.get('photo_url') and not fm.get('photo_url'):
        fm['photo_url'] = op_data['photo_url']
        changes.append(f"photo_url: added")
    
    if op_data.get('url') and not fm.get('url'):
        fm['url'] = op_data['url']
        changes.append(f"url: added")
    
    if op_data.get('speeches_count') and not fm.get('speeches_count'):
        fm['speeches_count'] = op_data['speeches_count']
        changes.append(f"speeches_count: {op_data['speeches_count']}")
    
    if op_data.get('laws_proposed') and not fm.get('laws_proposed'):
        fm['laws_proposed'] = op_data['laws_proposed']
        changes.append(f"laws_proposed: {op_data['laws_proposed']}")
    
    if 'type' not in fm:
        fm['type'] = 'deputy'
    
    if 'chamber' not in fm:
        fm['chamber'] = 'deputies'
    
    if 'legislature' not in fm:
        fm['legislature'] = '2024-2028'
    
    if not changes:
        return False, []
    
    new_fm = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    new_content = f"---\n{new_fm}---\n{body}"
    filepath.write_text(new_content)
    
    return True, changes


def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """Parse YAML frontmatter from content."""
    if '---' not in content:
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    fm_text = parts[1]
    body = parts[2]
    
    try:
        fm = yaml.safe_load(fm_text) or {}
    except:
        fm = {}
    
    return fm, body


def main():
    """Main entry point."""
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    
    print("=" * 60)
    print("Phase 2: Data Enrichment")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print()
    
    print("Loading Open Parliament data...")
    op_deputies = load_open_parliament_deputies()
    print(f"Loaded {len(op_deputies)} Open Parliament deputies")
    print()
    
    if not VAULT_DEPUTIES_DIR.exists():
        print(f"Error: Vault deputies directory not found: {VAULT_DEPUTIES_DIR}")
        return 1
    
    enriched_count = 0
    unchanged_count = 0
    
    for filepath in sorted(VAULT_DEPUTIES_DIR.glob("*.md")):
        if filepath.name == "Index.md":
            continue
        
        name_slug = filepath.stem
        op_data = find_matching_op_deputy(name_slug, op_deputies)
        
        if op_data:
            if dry_run:
                print(f"  {filepath.name}: would enrich with {op_data['name']}")
            else:
                changed, changes = enrich_deputy_profile(filepath, op_data)
                if changed:
                    enriched_count += 1
                    print(f"  {filepath.name}: {changes}")
                else:
                    unchanged_count += 1
        else:
            unchanged_count += 1
    
    print()
    print(f"Results: {enriched_count} enriched, {unchanged_count} unchanged")
    
    if dry_run:
        print("\nRun without --dry-run to apply changes.")
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())