#!/usr/bin/env python3
"""
Scrape committee assignments from Chamber of Deputies (cdep.ro).

Usage: python3 scripts/scrape_committees.py --apply
"""
import re
import json
from pathlib import Path
from urllib.request import urlopen
from html import unescape

BASE_URL = "https://www.cdep.ro/pls/parlam/structura.co"

CHAMBER_COMMITTEES = [
    (1, "Economic Policies"),
    (2, "Budget, Finance"),
    (3, "Industries and Services"),
    (4, "Agriculture"),
    (5, "Human Rights"),
    (6, "Public Administration"),
    (7, "Labour"),
    (8, "Health"),
    (9, "Education"),
    (10, "Culture"),
    (11, "Legal"),
    (12, "Defense"),
    (13, "Foreign Policy"),
    (14, "Abuse, Corruption"),
    (15, "Standing Orders"),
    (16, "IT"),
    (17, "Equal Opportunities"),
]

PID_MAP = {"1": "PSD", "3": "PNL", "2": "AUR", "4": "USR",
           "7": "UDMR", "5": "SOS", "6": "POT", "8": "MIN"}

def parse_committee(html, comm_id, comm_name, chamber):
    members = []
    
    rows = re.findall(r'<tr[^>]*class="row\d*"[^>]*>(.*?)</tr>', html, re.DOTALL)
    
    for row in rows:
        cols = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(cols) < 3:
            continue
        
        raw_pos = cols[1].strip()
        raw_pos = re.sub(r'<[^>]+>', '', raw_pos).strip()
        
        if re.match(r'^\d+\.?$', raw_pos):
            position = "Member"
        else:
            position = raw_pos if raw_pos else "Member"
        
        mp_match = re.search(r'idm=(\d+)[^>]*><b>([^<]+)</b></a>', cols[2])
        if not mp_match:
            continue
        mp_id = mp_match.group(1)
        name = unescape(mp_match.group(2)).strip()
        
        if not name or len(name) < 3:
            continue
        
        party_match = re.search(r'idg=(\d+)', cols[3])
        party = PID_MAP.get(party_match.group(1), "Unknown") if party_match else "Unknown"
        
        members.append({
            "name": name, "position": position, "party": party,
            "committee_id": comm_id, "committee_name": comm_name,
            "chamber": chamber, "mp_id": mp_id
        })
    
    return members

def main():
    print("=== Committee Scraper (Chamber of Deputies) ===")
    all_members = []
    
    for comm_id, name in CHAMBER_COMMITTEES:
        try:
            url = f"{BASE_URL}?idc={comm_id}&idl=2"
            html = urlopen(url, timeout=15).read().decode('utf-8', errors='ignore')
            members = parse_committee(html, comm_id, name, "deputy")
            all_members.extend(members)
            print(f"  {name}: {len(members)} members")
        except Exception as e:
            print(f"  {name}: ERROR")
    
    print(f"\nTotal: {len(all_members)} assignments")
    
    output = Path("data/committees_members.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(all_members, f, ensure_ascii=False, indent=2)
    print(f"Saved: {output}")
    
    from collections import Counter
    parties = Counter(m['party'] for m in all_members)
    print(f"\nParty breakdown:")
    for party, count in parties.most_common():
        print(f"  {party}: {count}")

if __name__ == "__main__":
    main()