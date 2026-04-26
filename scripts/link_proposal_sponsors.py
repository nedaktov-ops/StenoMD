#!/usr/bin/env python3
"""
Link proposals to MP sponsors using Open Parliament data.

Usage: python3 scripts/link_proposal_sponsors.py --apply
"""
import re
import json
from pathlib import Path

PROPOSALS_DIR = Path("data/parlamint/open-parliament-ro/data/2024/proposals")
DEPUTIES_DIR = Path("vault/politicians/deputies")
LAWS_DIR = Path("vault/laws")

def build_id_map():
    """Build numeric ID -> stable_id and name mapping from profiles."""
    id_to_stable = {}
    id_to_name = {}
    
    for f in DEPUTIES_DIR.glob("*.md"):
        if f.name == "Index.md":
            continue
        content = f.read_text(encoding="utf-8")
        
        stable_match = re.search(r"^stable_id:\s*(\S+)", content, re.MULTILINE)
        if not stable_match:
            continue
        stable_id = stable_match.group(1)
        
        idm_match = re.search(r"idm=(\d+)", content)
        if idm_match:
            mp_id = idm_match.group(1)
            id_to_stable[mp_id] = stable_id
            
            name_match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
            if name_match:
                id_to_name[mp_id] = name_match.group(1).strip()
    
    return id_to_stable, id_to_name

def load_proposals():
    proposals = []
    for f in PROPOSALS_DIR.glob("*.json"):
        with open(f) as fp:
            data = json.load(fp)
            proposals.append(data.get("data", {}))
    return proposals

def get_status_stage(status_short):
    if not status_short:
        return "unknown"
    
    status = status_short.lower()
    
    if "promulgat" in status:
        return "promulgated"
    elif "adoptat" in status:
        return "adopted"
    elif "respins" in status:
        return "rejected"
    elif "comis" in status or "raport" in status:
        return "in_committee"
    elif "senat" in status or "camer" in status:
        return "in_chamber"
    else:
        return "proposed"

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    
    print("=== Linking Proposals to Sponsors ===")
    
    id_to_stable, id_to_name = build_id_map()
    print(f"MP ID mappings: {len(id_to_stable)}")
    
    proposals = load_proposals()
    print(f"Total proposals: {len(proposals)}")
    
    # Build lookup
    law_lookup = {}
    for prop in proposals:
        reg = prop.get("registrationNumber", {})
        reg_num = reg.get("senateChamber") or reg.get("deputyChamber")
        
        if not reg_num:
            continue
        
        m = re.search(r"L(\d+)/(\d{4})", reg_num)
        if m:
            law_id = f"{m.group(1)}/{m.group(2)}"
            law_lookup[law_id] = prop
    
    print(f"Law lookups: {len(law_lookup)}")
    
    # Get law files that need updating
    laws_to_update = []
    for f in LAWS_DIR.glob("*.md"):
        if f.name == "Index.md":
            continue
        
        content = f.read_text(encoding="utf-8")
        
        # Skip if already has sponsors or status
        if "sponsors:" in content or "process_stage:" in content:
            continue
        
        m = re.match(r"(\d+)-(\d{4})", f.stem)
        if not m:
            continue
        
        law_id = f"{m.group(1)}/{m.group(2)}"
        prop = law_lookup.get(law_id)
        
        if prop:
            laws_to_update.append((f, law_id, prop))
    
    print(f"Laws with matching proposals: {len(laws_to_update)}")
    
    # Update files
    updated = 0
    linked = 0
    
    for f, law_id, prop in laws_to_update:
        initiators = prop.get("initiators", [])
        sponsors = []
        
        for init_id in initiators:
            if init_id == "GOVERNMENT":
                sponsors.append({"name": "Guvern", "type": "government"})
            elif init_id in id_to_stable:
                sponsors.append({
                    "id": init_id,
                    "stable_id": id_to_stable[init_id],
                    "name": id_to_name.get(init_id, "Unknown"),
                    "type": "sponsor"
                })
                linked += 1
        
        if not sponsors:
            continue
        
        # Build YAML
        sponsor_lines = []
        for s in sponsors:
            if s.get("stable_id"):
                sponsor_lines.append(f"  - stable_id: {s['stable_id']}")
                sponsor_lines.append(f"    name: {s.get('name', 'Unknown')}")
                sponsor_lines.append(f"    type: {s.get('type', 'sponsor')}")
            elif s.get("type") == "government":
                sponsor_lines.append(f"  - name: \"{s['name']}\"")
                sponsor_lines.append(f"    type: government")
        
        stage = get_status_stage(prop.get("status", {}).get("short", ""))
        
        content = f.read_text(encoding="utf-8")
        lines = content.split("\n")
        new_lines = []
        inserted = False
        
        for line in lines:
            new_lines.append(line)
            if line.startswith("law_number:") and not inserted:
                new_lines.append("sponsors:")
                new_lines.extend(sponsor_lines)
                new_lines.append(f"process_stage: {stage}")
                inserted = True
        
        if inserted and args.apply:
            f.write_text("\n".join(new_lines), encoding="utf-8")
            updated += 1
            print(f"  Updated: {law_id}")
    
    print(f"\nUpdated: {updated}/{len(laws_to_update)}")
    print(f"Linked sponsors: {linked}")

if __name__ == "__main__":
    main()