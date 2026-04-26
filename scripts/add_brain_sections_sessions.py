#!/usr/bin/env python3
"""
Add Brain Sections to Session Files

Adds 4 brain-analogous sections to all session files:
- Sensory Input (source tracking)
- Processing (topics, sentiment, speakers)
- Memory (participants, agenda, votes)
- Action/Output (query-ready fields, summaries)

Idempotent: Checks for existing sections before adding.
"""

import re
from pathlib import Path
from datetime import datetime

SESSIONS_DIRS = [
    Path("vault/sessions"),
    Path("vault/sessions/deputies"),
    Path("vault/sessions/senate"),
]

def extract_field(content, field_name):
    """Extract field from frontmatter."""
    pattern = rf'^{field_name}:\s*(.+)$'
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else None

def has_section(content, section_name):
    """Check if section already exists."""
    return f"## {section_name}" in content

def extract_participants(content):
    """Extract participant list from content."""
    # Try frontmatter first
    participants = []
    for i in range(1, 100):
        p = extract_field(content, f'participants.{i}')
        if p:
            participants.append(p)
        else:
            break
    
    if not participants:
        # Try finding in content
        part_match = re.search(r'## Participants\s*\n\s*(.+?)\n', content, re.DOTALL)
        if part_match:
            participants = [p.strip() for p in part_match.group(1).split(',')]
    
    return participants

def add_brain_sections_to_session(filepath):
    """Add brain sections to a single session file."""
    content = filepath.read_text(encoding='utf-8')
    
    # Skip empty files
    if len(content.strip()) == 0:
        return False
    
    # Get date for reference
    date = extract_field(content, 'date') or filepath.stem
    chamber = extract_field(content, 'chamber') or 'Unknown'
    word_count = extract_field(content, 'word_count') or '0'
    laws = extract_field(content, 'laws_discussed') or ''
    
    # Check if brain sections already exist (idempotent)
    if has_section(content, 'Sensory Input'):
        return False
    
    # Extract participants
    participants = extract_participants(content)
    attendance = len(participants)
    
    # Build new sections
    new_sections = []
    
    # Sensory Input
    source_url = extract_field(content, 'url') or ''
    
    new_sections.append("## Sensory Input")
    new_sections.append("")
    new_sections.append(f"- **Source URL:** {source_url}")
    new_sections.append(f"- **Last Synced:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Estimate duration from word count
    duration = int(word_count) // 150 if word_count.isdigit() else 0
    new_sections.append(f"- **Duration (Minutes):** ~{duration}")
    new_sections.append(f"- **Attendance:** {attendance}")
    new_sections.append("")
    
    # Processing
    new_sections.append("## Processing")
    new_sections.append("")
    
    # Extract topics (from laws discussed)
    if laws:
        topics = [laws]
    else:
        topics = []
    
    new_sections.append(f"- **Topics Discussed:** {', '.join(topics) if topics else '(extract from transcript)'}")
    new_sections.append("- **Sentiment:** neutral")
    new_sections.append(f"- **Speakers Identified:** {len([p for p in participants if p])}")
    new_sections.append("")
    
    # Memory
    new_sections.append("## Memory")
    new_sections.append("")
    new_sections.append("### Participants")
    for p in participants[:20]:
        new_sections.append(f"- {p}")
    if len(participants) > 20:
        new_sections.append(f"- ... and {len(participants) - 20} more")
    new_sections.append("")
    new_sections.append("### Agenda")
    new_sections.append("- (Extract from stenogram)")
    new_sections.append("")
    new_sections.append("### Laws Discussed")
    if laws:
        new_sections.append(f"- [[laws/{laws}|{laws}]]")
    else:
        new_sections.append("- (Track laws)")
    new_sections.append("")
    new_sections.append("### Key Votes")
    new_sections.append("- (Track votes)")
    new_sections.append("")
    new_sections.append("### Statements")
    new_sections.append("- (Extract statements)")
    new_sections.append("")
    
    # Action/Output
    new_sections.append("## Action/Output")
    new_sections.append("")
    new_sections.append("### Query Ready")
    new_sections.append("```dataview")
    new_sections.append('FROM "sessions"')
    new_sections.append(f'WHERE date = "{date}"')
    new_sections.append("```")
    new_sections.append("")
    new_sections.append("### Daily Summary")
    new_sections.append("- Auto-generate summary")
    new_sections.append("")
    new_sections.append("### Searchable Transcript")
    new_sections.append("- Full text available")
    new_sections.append("")
    
    # Append new sections to content
    content += "\n\n" + "\n".join(new_sections)
    
    # Write back
    filepath.write_text(content, encoding='utf-8')
    return True

def main():
    """Main function to process all session files."""
    print("=" * 60)
    print("ADD BRAIN SECTIONS TO SESSIONS")
    print("=" * 60)
    
    total_updated = 0
    total_skipped = 0
    total_errors = 0
    
    for sessions_dir in SESSIONS_DIRS:
        if not sessions_dir.exists():
            continue
        
        session_files = list(sessions_dir.glob("*.md"))
        print(f"\nProcessing {len(session_files)} session files in {sessions_dir.name}...")
        
        updated = 0
        skipped = 0
        errors = 0
        
        for f in session_files:
            try:
                if add_brain_sections_to_session(f):
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