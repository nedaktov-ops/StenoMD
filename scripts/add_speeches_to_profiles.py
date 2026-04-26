#!/usr/bin/env python3
"""
Add Open Parliament data to MP profiles.

Usage: python3 scripts/add_speeches_to_profiles.py --apply
"""
import json
import re
from pathlib import Path

SPEECHES_DIR = Path("data/parlamint/open-parliament-ro/data/2024/speeches/deputies")
DEPUTIES_DIR = Path("vault/politicians/deputies")

def build_id_map():
    id_to_stable = {}
    for f in DEPUTIES_DIR.glob("*.md"):
        if f.name == "Index.md":
            continue
        content = f.read_text(encoding="utf-8")
        idm_match = re.search(r"idm=(\d+)", content)
        stable_match = re.search(r"^stable_id:\s*(\S+)", content, re.MULTILINE)
        if idm_match and stable_match:
            id_to_stable[idm_match.group(1)] = stable_match.group(1)
    return id_to_stable

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    
    print("=== Adding Open Parliament Data to MP Profiles ===")
    
    id_to_stable = build_id_map()
    print(f"MP ID mappings: {len(id_to_stable)}")
    
    # Aggregate data by MP
    mp_data = {}
    
    for f in SPEECHES_DIR.glob("*.json"):
        with open(f) as fp:
            data = json.load(fp)
            for entry in data.get("data", []):
                mp_id = entry.get("idm")
                if not mp_id or mp_id not in id_to_stable:
                    continue
                
                stable_id = id_to_stable[mp_id]
                
                if stable_id not in mp_data:
                    mp_data[stable_id] = {
                        "speech_count": 0,
                        "topics": [],
                        "sessions": []
                    }
                
                mp_data[stable_id]["speech_count"] += 1
                
                date = entry.get("date", "")[:10]
                session_title = entry.get("title", "")[:80]
                mp_data[stable_id]["sessions"].append(f"{date}: {session_title}")
                
                for t in entry.get("transcripts", []):
                    desc = t.get("description", "")
                    if desc:
                        mp_data[stable_id]["topics"].append(desc[:150])
    
    print(f"MPs with data: {len(mp_data)}")
    
    # Update profiles
    updated = 0
    for stable_id, data in mp_data.items():
        # Find profile
        profile = None
        for f in DEPUTIES_DIR.glob("*.md"):
            if f.name == "Index.md":
                continue
            content = f.read_text(encoding="utf-8")
            if stable_id in content:
                profile = f
                break
        
        if not profile:
            continue
        
        content = profile.read_text(encoding="utf-8")
        
        # Skip if already has speeches data
        if "speeches_count:" in content:
            continue
        
        # Build new fields
        speech_count = data["speech_count"]
        
        # Add speeches field after laws_proposed
        lines = content.split("\n")
        new_lines = []
        inserted = False
        
        for line in lines:
            new_lines.append(line)
            if line.startswith("laws_proposed:") and not inserted:
                new_lines.append(f"speeches_count: {speech_count}")
                inserted = True
        
        if inserted and args.apply:
            profile.write_text("\n".join(new_lines), encoding="utf-8")
            updated += 1
            print(f"  Updated {stable_id}: {speech_count} speeches")
    
    print(f"\nUpdated: {updated}/{len(mp_data)}")

if __name__ == "__main__":
    main()