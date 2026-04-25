#!/usr/bin/env python3
"""
Enrich senator profiles with party and constituency data from Wikipedia.

Usage: python3 scripts/enrich_senators.py
"""
import os
import json
import re
import yaml
from difflib import SequenceMatcher
from pathlib import Path

VAULT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/vault/politicians/senators")
DATA_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/data")

PARTY_MAP = {
    "PSD": "Partidul Social Democrat",
    "PNL": "Partidul Național Liberal",
    "AUR": "Alianța pentru Unirea Românilor",
    "USR": "Uniunea Salvați România",
    "UDMR": "Uniunea Democrată Maghiară din România",
    "SOS": "S.O.S. România",
    "POT": "Partidul Oamenilor Tineri",
}

def normalize_name(name):
    name = re.sub(r'[-\s]+', ' ', name.strip().lower())
    return name

def flip_name(name):
    parts = name.split()
    if len(parts) == 2:
        return f"{parts[1]} {parts[0]}"
    return name

def similarity(a, b):
    a_norm = normalize_name(a)
    b_norm = normalize_name(b)
    a_flip = flip_name(a_norm)
    b_flip = flip_name(b_norm)
    
    score1 = SequenceMatcher(None, a_norm, b_norm).ratio()
    score2 = SequenceMatcher(None, a_flip, b_norm).ratio()
    score3 = SequenceMatcher(None, a_norm, b_flip).ratio()
    score4 = SequenceMatcher(None, a_flip, b_flip).ratio()
    
    return max(score1, score2, score3, score4)

def load_source_data():
    source_file = DATA_DIR / "senators_2024_full.json"
    if not source_file.exists():
        print(f"Source file not found: {source_file}")
        return {}
    
    with open(source_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    senators = {}
    for s in data.get("senators", []):
        name = s["name"]
        senators[name] = s
    
    print(f"Loaded {len(senators)} senators from source")
    return senators

def find_best_match(name, candidates, threshold=0.5):
    name_lower = normalize_name(name)
    best_match = None
    best_score = 0
    
    for candidate in candidates:
        score = similarity(name, candidate)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = candidate
    
    return best_match, best_score

def update_senator_file(filepath, senator_data):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.split("\n")
    new_lines = []
    updated = False
    
    party = senator_data["party"]
    party_full = PARTY_MAP.get(party, senator_data.get("party_full", party))
    constituency = senator_data["constituency"]
    
    for line in lines:
        if line.startswith("party:"):
            new_lines.append(f"party: {party}")
            updated = True
        elif line.startswith("party_full:"):
            new_lines.append(f"party_full: {party_full}")
        elif line.startswith("constituency:"):
            new_lines.append(f"constituency: {constituency}")
        else:
            new_lines.append(line)
    
    if not updated:
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("type:"):
                insert_idx = i + 1
                break
        
        new_lines = lines[:insert_idx] + [
            f"party: {party}",
            f"party_full: {party_full}",
            f"constituency: {constituency}",
            "",
        ] + lines[insert_idx:]
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

def main():
    print("=== Senator Party Enrichment ===")
    
    source_data = load_source_data()
    if not source_data:
        return
    
    senator_files = list(VAULT_DIR.glob("*.md"))
    senator_files = [f for f in senator_files if f.name != "Index.md"]
    
    print(f"Found {len(senator_files)} senator files")
    
    matched = 0
    unmatched = []
    
    candidates = list(source_data.keys())
    extra_mappings = {
        "antal istv n lor nt": "István-Loránt Antal",
        "fej r l szl d n": "László-Ödön Fejér",
    }
    
    for filepath in sorted(senator_files):
        name = filepath.stem.replace("-", " ")
        
        if name in extra_mappings:
            match_name = extra_mappings[name]
            update_senator_file(filepath, source_data[match_name])
            matched += 1
            print(f"  ✓ {name} -> {source_data[match_name]['party']} (manual)")
            continue
        
        match_name, score = find_best_match(name, candidates)
        
        if match_name:
            update_senator_file(filepath, source_data[match_name])
            matched += 1
            print(f"  ✓ {name} -> {source_data[match_name]['party']} ({score:.2f})")
        else:
            unmatched.append(name)
            print(f"  ✗ {name} (no match)")
    
    print(f"\nResults: {matched}/{len(senator_files)} matched")
    if unmatched:
        print(f"Unmatched ({len(unmatched)}):")
        for name in unmatched[:10]:
            print(f"  - {name}")
        if len(unmatched) > 10:
            print(f"  ... and {len(unmatched) - 10} more")

if __name__ == "__main__":
    main()