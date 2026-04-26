#!/usr/bin/env python3
"""
Add Brain Sections to Law Files

Adds 4 brain-analogous sections to all law files:
- Sensory Input (source tracking)
- Processing (status tracking, bottlenecks)
- Memory (sponsors, timeline, debates)
- Action/Output (query-ready fields, alerts)

Idempotent: Checks for existing sections before adding.
"""

import re
from pathlib import Path
from datetime import datetime

LAWS_DIR = Path("vault/laws")

def extract_field(content, field_name):
    """Extract field from frontmatter."""
    pattern = rf'^{field_name}:\s*(.+)$'
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else None

def has_section(content, section_name):
    """Check if section already exists."""
    return f"## {section_name}" in content

def add_brain_sections_to_law(filepath):
    """Add brain sections to a single law file."""
    content = filepath.read_text(encoding='utf-8')
    
    # Skip empty files
    if len(content.strip()) == 0:
        return False
    
    # Get law number for reference
    law_number = extract_field(content, 'law_number') or filepath.stem
    
    # Check if brain sections already exist (idempotent)
    if has_section(content, 'Sensory Input'):
        return False
    
    # Build new sections
    new_sections = []
    
    # Sensory Input
    status = extract_field(content, 'status') or 'Unknown'
    year = extract_field(content, 'year') or ''
    
    new_sections.append("## Sensory Input")
    new_sections.append("")
    new_sections.append(f"- **Source URL:** cdep.ro/pls/parlam/{law_number}")
    new_sections.append(f"- **Last Synced:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    new_sections.append(f"- **Submitted Date:** {extract_field(content, 'date_proposed') or 'N/A'}")
    new_sections.append("")
    
    # Processing
    new_sections.append("## Processing")
    new_sections.append("")
    new_sections.append("- **Processing Time (Days):** (calculate from dates)")
    
    # Determine bottleneck stage
    if 'comisi' in status.lower():
        bottleneck = "Committee Review"
    elif 'senat' in status.lower():
        bottleneck = "Senate"
    elif 'deputat' in status.lower():
        bottleneck = "Chamber of Deputies"
    else:
        bottleneck = "Unknown"
    
    new_sections.append(f"- **Bottleneck Stage:** {bottleneck}")
    new_sections.append(f"- **Current Stage:** {status}")
    new_sections.append("")
    
    # Memory
    sessions = extract_field(content, 'sessions_count') or '0'
    new_sections.append("## Memory")
    new_sections.append("")
    new_sections.append("### Status History")
    new_sections.append(f"- Proposed: {extract_field(content, 'date_proposed') or 'N/A'}")
    new_sections.append(f"- Adopted: {extract_field(content, 'date_adopted') or 'N/A'}")
    new_sections.append("")
    new_sections.append("### Sponsors")
    new_sections.append("- (Extract from source)")
    new_sections.append("")
    new_sections.append("### Co-Sponsors")
    new_sections.append("- (Extract from source)")
    new_sections.append("")
    new_sections.append("### Amendments")
    new_sections.append("- (Track amendments)")
    new_sections.append("")
    new_sections.append("### Debates")
    new_sections.append(f"- Discussed in {sessions} sessions")
    new_sections.append("")
    
    # Action/Output
    new_sections.append("## Action/Output")
    new_sections.append("")
    new_sections.append("### Query Ready")
    new_sections.append("```dataview")
    new_sections.append('FROM "laws"')
    new_sections.append(f'WHERE law_number = "{law_number}"')
    new_sections.append("```")
    new_sections.append("")
    new_sections.append("### Alerts")
    
    # Check for alerts
    alerts = []
    if not extract_field(content, 'date_adopted'):
        alerts.append("- Law not yet adopted")
    if int(sessions or 0) == 0:
        alerts.append("- No discussion in sessions")
    
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
    """Main function to process all law files."""
    print("=" * 60)
    print("ADD BRAIN SECTIONS TO LAWS")
    print("=" * 60)
    
    if not LAWS_DIR.exists():
        print("ERROR: Laws directory not found")
        return
    
    law_files = list(LAWS_DIR.glob("*.md"))
    print(f"\nProcessing {len(law_files)} law files...")
    
    updated = 0
    skipped = 0
    errors = 0
    
    for f in law_files:
        try:
            if add_brain_sections_to_law(f):
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