#!/usr/bin/env python3
"""
Copilot Bridge - Sync vault with Copilot memory and MemPalace

Usage:
    python3 obsidian-plugins/integration/copilot-bridge.py --sync-vault
    python3 obsidian-plugins/integration/copilot-bridge.py --export-kg
    python3 obsidian-plugins/integration/copilot-bridge.py --full-sync
"""

import json
import shutil
import sys
from pathlib import Path
from datetime import datetime


def main():
    PROJECT_ROOT = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
    VAULT_DIR = PROJECT_ROOT / "vault"
    AI_MEMORY = VAULT_DIR / "ai-memory"
    KG_FILE = PROJECT_ROOT / "knowledge_graph" / "entities.json"
    
    args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
    
    if "--sync-vault" in args or "--full-sync" in args:
        print("Syncing vault to ai-memory...")
        
        AI_MEMORY.mkdir(parents=True, exist_ok=True)
        
        dirs_to_sync = [
            ("politicians", "politicians"),
            ("sessions", "sessions"),
            ("laws", "laws"),
            ("committees", "committees"),
        ]
        
        synced = []
        for src_name, dst_name in dirs_to_sync:
            src = VAULT_DIR / src_name
            dst = AI_MEMORY / dst_name
            
            if src.exists():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                synced.append(src_name)
                print(f"  ✅ Synced {src_name}/")
        
        # Create index
        index = {
            "last_sync": datetime.now().isoformat(),
            "synced_directories": synced,
            "source": "vault/",
            "destination": "vault/ai-memory/"
        }
        
        with open(AI_MEMORY / "sync-index.json", "w") as f:
            json.dump(index, f, indent=2)
        
        print(f"\n✓ Synced {len(synced)} directories to ai-memory/")
    
    if "--export-kg" in args or "--full-sync" in args:
        print("\nExporting knowledge graph...")
        
        if not KG_FILE.exists():
            print("  ⚠️ No KG found - skipping")
        else:
            with open(KG_FILE) as f:
                kg = json.load(f)
            
            export = {
                "last_updated": datetime.now().isoformat(),
                "metadata": kg.get("metadata", {}),
                "persons": {
                    "total": len(kg.get("persons", [])),
                    "deputies": len([p for p in kg.get("persons", []) if p.get("chamber") == "deputies"]),
                    "senators": len([p for p in kg.get("persons", []) if p.get("chamber") == "senate"])
                },
                "sessions": {
                    "total": len(kg.get("sessions", [])),
                    "deputies": len([s for s in kg.get("sessions", []) if s.get("chamber") == "deputies"]),
                    "senate": len([s for s in kg.get("sessions", []) if s.get("chamber") == "senate"])
                },
                "laws": {
                    "total": len(kg.get("laws", []))
                }
            }
            
            export_file = AI_MEMORY / "knowledge_summary.json"
            with open(export_file, "w") as f:
                json.dump(export, f, indent=2)
            
            print(f"  ✅ Exported: {export['persons']['total']} persons, {export['sessions']['total']} sessions")
    
    if "--full-sync" in args:
        print("\n✓ Full sync complete")
    elif "--help" in args:
        print("Usage:")
        print("  --sync-vault  Sync vault to ai-memory")
        print("  --export-kg   Export knowledge graph")
        print("  --full-sync  Complete sync")


if __name__ == "__main__":
    main()