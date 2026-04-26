#!/usr/bin/env python3
"""
Scrape voting records from cdep.ro.

Usage: python3 scripts/scrape_votes.py --apply
"""
import re
import json
from pathlib import Path
from urllib.request import urlopen
from html import unescape

BASE_URL = "https://www.cdep.ro/pls/steno"

def get_recent_votes():
    """Get recent voting session IDs."""
    votes = []
    
    url = f"{BASE_URL}/evot2015.data"
    try:
        html = urlopen(url, timeout=15).read().decode('utf-8', errors='ignore')
        vote_ids = re.findall(r'idv=(\d+)', html)
        
        for vid in set(vote_ids):
            votes.append({
                'vote_id': vid,
                'url': f"{BASE_URL}/evot2015.nominal?idv={vid}&idl=2"
            })
    except Exception as e:
        print(f"Error: {e}")
    
    return votes[:50]

def parse_vote_page(vote_info):
    """Parse individual vote page."""
    try:
        html = urlopen(vote_info['url'], timeout=15).read().decode('utf-8', errors='ignore')
    except:
        return []
    
    votes = []
    
    # Find rows with MP data
    # Pattern: name in <b>...</b>, idm=XXX somewhere in row
    rows = re.findall(r'<tr[^>]*>(.+?)</tr>', html, re.DOTALL)
    
    for row in rows:
        # Skip header rows
        if '<th' in row or 'Vot final' in row or 'Total' in row:
            continue
        
        # Find MP ID
        mp_match = re.search(r'idm=(\d+)', row)
        if not mp_match:
            continue
        
        mp_id = mp_match.group(1)
        
        # Find name
        name_match = re.search(r'<b>([^<]+)</b>', row)
        name = unescape(name_match.group(1).strip()) if name_match else ""
        
        if not name or len(name) < 3:
            continue
        
        # Determine vote - find position in table cell
        vote = "abstain"
        row_lower = row.lower()
        
        # Check which column (position in row determines vote)
        # Usually: for | against | abstain
        if '<td' in row:
            cells = re.findall(r'<td[^>]*>([^<]+)</td>', row)
            if cells:
                cell_text = ' '.join(cells).lower()
                if 'pentru' in cell_text or 'vot pentru' in cell_text:
                    vote = "for"
                elif 'impotriva' in cell_text or 'împotriva' in cell_text:
                    vote = "against"
        
        votes.append({
            'mp_id': mp_id,
            'name': name,
            'vote': vote
        })
    
    return votes

def main():
    print("=== Voting Record Scraper ===")
    
    print("Getting vote IDs...")
    votes_info = get_recent_votes()
    print(f"Found {len(votes_info)} votes")
    
    all_votes = []
    
    # Parse a few votes
    for vi in votes_info[:5]:
        print(f"Parsing vote {vi['vote_id']}...")
        parsed = parse_vote_page(vi)
        
        if parsed:
            all_votes.append({
                'vote_id': vi['vote_id'],
                'votes': parsed
            })
            # Count votes
            counts = {'for': 0, 'against': 0, 'abstain': 0}
            for p in parsed:
                counts[p['vote']] = counts.get(p['vote'], 0) + 1
            print(f"  For: {counts['for']}, Against: {counts['against']}, Abstain: {counts['abstain']}")
    
    # Save
    output = Path("data/voting_records.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output, "w") as f:
        json.dump(all_votes, f, ensure_ascii=False, indent=2)
    
    total = sum(len(v['votes']) for v in all_votes)
    print(f"\nTotal individual votes: {total}")
    print(f"Saved: {output}")

if __name__ == "__main__":
    main()