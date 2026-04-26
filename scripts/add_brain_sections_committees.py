#!/usr/bin/env python3
"""
Add Brain Sections to Committee Files

Adds 4 brain-analogous sections to all committee files:
- Sensory Input (source tracking)
- Processing (activity scores)
- Memory (members, meetings, reports)
- Action/Output (query-ready fields)

Idempotent: Checks for existing sections before adding.
"""

import re
import json
from pathlib import Path
from datetime import datetime

COMMITTEE_DIRS = [
    Path("vault/committees"),
    Path("vault/_parliament/committees"),
]

def extract_field(content, field_name):
    """Extract field from frontmatter."""
    pattern = rf'^{field_name}:\s*(.+)$'
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else None

def has_section(content, section_name):
    """Check if section already exists."""
    return f"## {section_name}" in content

def load_committee_members():
    """Load committee member data."""
    try:
        data = json.load(open("data/committees_members.json"))
        committee_data = {}
        for c in data:
            name = c.get('committee_name')
            if name:
                if name not in committee_data:
                    committee_data[name] = []
                committee_data[name].append(c)
        return committee_data
    except:
        return {}

def add_brain_sections_to_committee(filepath, committee_members_data):
    """Add brain sections to a single committee file."""
    content = filepath.read_text(encoding='utf-8')
    
    # Skip empty files
    if len(content.strip()) == 0:
        return False
    
    # Get committee name
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    committee_name = title_match.group(1).strip() if title_match else filepath.stem
    
    # Check if brain sections already exist (idempotent)
    if has_section(content, 'Sensory Input'):
        return False
    
    # Get member count
    members = committee_members_data.get(committee_name, [])
    member_count = len(members)
    
    # Build new sections
    new_sections = []
    
    # Sensory Input
    new_sections.append("## Sensory Input")
    new_sections.append("")
    new_sections.append("- **Source URL:** cdep.ro/senat.ro (committees)")
    new_sections.append(f"- **Last Synced:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    new_sections.append(f"- **Meeting Schedule:** (from parliament calendar)")
    new_sections.append("")
    
    # Processing
    new_sections.append("## Processing")
    new_sections.append("")
    new_sections.append(f"- **Activity Score:** {member_count}")
    new_sections.append("- **Meeting Frequency:** monthly")
    new_sections.append(f"- **Bills Reviewed:** (track from session data)")
    new_sections.append("")
    
    # Memory
    new_sections.append("## Memory")
    new_sections.append("")
    new_sections.append("### Members")
    for m in members[:10]:
        new_sections.append(f"- {m.get('name', 'Unknown')}")
    if len(members) > 10:
        new_sections.append(f"- ... and {len(members) - 10} more")
    new_sections.append("")
    new_sections.append("### Meetings")
    new_sections.append("- (Track meeting dates)")
    new_sections.append("")
    new_sections.append("### Reports")
    new_sections.append("- (Link published reports)")
    new_sections.append("")
    new_sections.append("### Legislation Reviewed")
    new_sections.append("- (Link laws)")
    new_sections.append("")
    
    # Action/Output
    new_sections.append("## Action/Output")
    new_sections.append("")
    new_sections.append("### Query Ready")
    new_sections.append("```dataview")
    new_sections.append('FROM "committees"')
    new_sections.append(f'WHERE contains(name, "{committee_name}")')
    new_sections.append("```")
    new_sections.append("")
    new_sections.append("### Member Attendance")
    new_sections.append("- (Track from meetings)")
    new_sections.append("")
    new_sections.append("### Bills Passed Through")
    new_sections.append("- (Track laws)")
    new_sections.append("")
    new_sections.append("### Activity Report")
    new_sections.append("- Auto-generate")
    new_sections.append("")
    
    # Append new sections to content
    content += "\n\n" + "\n".join(new_sections)
    
    # Write back
    filepath.write_text(content, encoding='utf-8')
    return True

def main():
    """Main function to process all committee files."""
    print("=" * 60)
    print("ADD BRAIN SECTIONS TO COMMITTEES")
    print("=" * 60)
    
    # Load committee member data
    committee_data = load_committee_members()
    print(f"\nLoaded {len(committee_data)} committees with member data")
    
    total_updated = 0
    total_skipped = 0
    total_errors = 0
    
    for committee_dir in COMMITTEE_DIRS:
        if not committee_dir.exists():
            continue
        
        # Get all MD files in this directory
        if committee_dir.is_file():
            files = [committee_dir]
        else:
            files = list(committee_dir.glob("*.md"))
        
        print(f"\nProcessing {len(files)} files in {committee_dir.name}...")
        
        updated = 0
        skipped = 0
        errors = 0
        
        for f in files:
            try:
                if add_brain_sections_to_committee(f, committee_data):
                    updated += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"Error processing {f.name}: {e}")
                errors += 1
        
        print(f"  Updated: {updated}")
        print(f"  Skipped (already has sections): {skipped}")
        print(f"  Errors: {errors}")
        
        total_updated += updated
        total_skipped += skipped
        total_errors += errors
    
    print("\n" + "=" * 60)
    print(f"TOTALS: Updated {total_updated}, Skipped {total_skipped}, Errors {total_errors}")
    print("COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()