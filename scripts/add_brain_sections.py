#!/usr/bin/env python3
"""
Add Brain Sections to Politician Profiles

Adds 4 brain-analogous sections to all deputy and senator profiles:
- Sensory Input (source tracking)
- Processing (activity scores)
- Memory (linked items)
- Action/Output (query-ready fields)

Idempotent: Checks for existing sections before adding.
"""

import json
import re
from pathlib import Path
from datetime import datetime

VAULT_DIR = Path("vault/politicians")
DATA_DIR = Path("data")

def load_activity_stats():
    """Load deputy activity statistics."""
    try:
        stats = json.load(open(DATA_DIR / "deputy_activity_stats.json"))
        return {s['idm']: s for s in stats}
    except:
        return {}

def load_committees():
    """Load committee memberships."""
    try:
        committees = json.load(open(DATA_DIR / "committees_members.json"))
        idm_to_committees = {}
        for c in committees:
            if c.get('chamber') == 'deputy':
                mp_id = c.get('mp_id')
                if mp_id:
                    if mp_id not in idm_to_committees:
                        idm_to_committees[mp_id] = []
                    idm_to_committees[mp_id].append({
                        'name': c['committee_name'],
                        'role': c.get('position', 'member')
                    })
        return idm_to_committees
    except:
        return {}

def extract_field(content, field_name):
    """Extract field from frontmatter."""
    pattern = rf'^{field_name}:\s*(.+)$'
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else None

def has_section(content, section_name):
    """Check if section already exists."""
    return f"## {section_name}" in content

def add_brain_sections_to_file(filepath, activity_data, committees_data):
    """Add brain sections to a single politician file."""
    content = filepath.read_text(encoding='utf-8')
    
    # Skip empty files
    if len(content.strip()) == 0:
        return False
    
    # Get idm for data lookup
    idm = extract_field(content, 'idm')
    if not idm:
        return False
    
    # Check if brain sections already exist (idempotent)
    if has_section(content, 'Sensory Input'):
        return False
    
    # Build new sections
    new_sections = []
    
    # Sensory Input
    source_url = extract_field(content, 'url') or ''
    new_sections.append("## Sensory Input")
    new_sections.append("")
    new_sections.append(f"- **Source URL:** {source_url}")
    new_sections.append(f"- **Last Synced:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    new_sections.append("- **Data Sources:** parlamint, cdep.ro")
    new_sections.append("")
    
    # Processing
    activity = activity_data.get(idm, {})
    activity_score = activity.get('proposals', 0) + activity.get('motions', 0) + activity.get('speeches', 0)
    new_sections.append("## Processing")
    new_sections.append("")
    new_sections.append(f"- **Activity Score:** {activity_score}")
    
    # Get collaboration network (same party)
    party = extract_field(content, 'party') or extract_field(content, 'original_elected_party') or ''
    if party:
        new_sections.append(f"- **Party Alignment:** {party}")
    new_sections.append("")
    
    # Memory section
    new_sections.append("## Memory")
    new_sections.append("")
    new_sections.append("### Proposals Sponsored")
    new_sections.append("")
    
    # Add existing proposals if any
    if '## Proposals' in content:
        # Extract existing proposals
        prop_section = content.split('## Proposals')[1].split('##')[0] if '## Proposals' in content else ''
        new_sections.append(prop_section.strip())
    
    new_sections.append("")
    new_sections.append("### Co-Sponsors")
    new_sections.append("- (Track from proposals)")
    new_sections.append("")
    new_sections.append("### Speeches")
    new_sections.append(f"- Total: {activity.get('speeches', 0)}")
    new_sections.append("")
    new_sections.append("### Voting Record")
    new_sections.append("- (Link to voting data)")
    new_sections.append("")
    
    # Action/Output section
    new_sections.append("## Action/Output")
    new_sections.append("")
    new_sections.append("### Query Ready")
    new_sections.append("```dataview")
    new_sections.append('FROM "politicians"')
    new_sections.append(f'WHERE idm = "{idm}"')
    new_sections.append("```")
    new_sections.append("")
    new_sections.append("### Alerts")
    
    # Check for alerts
    alerts = []
    if activity_score == 0:
        alerts.append("- No legislative activity recorded")
    if activity.get('speeches', 0) == 0:
        alerts.append("- No speeches recorded")
    
    if alerts:
        new_sections.extend(alerts)
    else:
        new_sections.append("- No alerts")
    
    new_sections.append("")
    
    # Append new sections to content
    content += "\n\n" + "\n".join(new_sections)
    
    # Write back
    filepath.write_text(content, encoding='utf-8')
    return True

def main():
    """Main function to process all politician files."""
    print("=" * 60)
    print("ADD BRAIN SECTIONS TO POLITICIANS")
    print("=" * 60)
    
    # Load data
    activity_data = load_activity_stats()
    committees_data = load_committees()
    
    print(f"Loaded {len(activity_data)} activity records")
    print(f"Loaded {len(committees_data)} committee records")
    
    # Process deputies
    deputies_dir = VAULT_DIR / "deputies"
    if deputies_dir.exists():
        deputy_files = list(deputies_dir.glob("*.md"))
        print(f"\nProcessing {len(deputy_files)} deputy files...")
        
        updated = 0
        skipped = 0
        errors = 0
        
        for f in deputy_files:
            try:
                if add_brain_sections_to_file(f, activity_data, committees_data):
                    updated += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"Error processing {f.name}: {e}")
                errors += 1
        
        print(f"  Updated: {updated}")
        print(f"  Skipped (already has sections): {skipped}")
        print(f"  Errors: {errors}")
    
    # Process senators
    senators_dir = VAULT_DIR / "senators"
    if senators_dir.exists():
        senator_files = list(senators_dir.glob("*.md"))
        print(f"\nProcessing {len(senator_files)} senator files...")
        
        updated = 0
        skipped = 0
        errors = 0
        
        for f in senator_files:
            try:
                if add_brain_sections_to_file(f, {}, {}):
                    updated += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"Error processing {f.name}: {e}")
                errors += 1
        
        print(f"  Updated: {updated}")
        print(f"  Skipped (already has sections): {skipped}")
        print(f"  Errors: {errors}")
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()