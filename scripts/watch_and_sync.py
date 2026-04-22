#!/usr/bin/env python3
"""Watch data directory for changes and auto-sync to vault"""

import time
import os
import sys
import json
from pathlib import Path

DATA_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/data")
STATE_FILE = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/scripts/.watcher_state.json")

def log(msg):
    print(msg)
    sys.stdout.flush()

def load_state():
    """Load previous file state."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def save_state(state):
    """Save current file state."""
    STATE_FILE.write_text(json.dumps(state))

def get_modified():
    """Get dict of files and their modification times."""
    modified = {}
    for f in DATA_DIR.glob("stenogram_*.html"):
        modified[f.name] = f.stat().st_mtime
    return modified

def sync():
    """Run sync process."""
    log(f"[Sync] {time.strftime('%Y-%m-%d %H:%M:%S')}")
    os.system("cd /home/adrian/Desktop/NEDAILAB/StenoMD && python3 scripts/update_knowledge_graph.py")
    os.system("cd /home/adrian/Desktop/NEDAILAB/StenoMD && python3 scripts/sync_vault.py")
    log("[Sync] Complete - refresh Obsidian with Ctrl+R")

def main():
    log("=== StenoMD File Watcher ===")
    log(f"Watching: {DATA_DIR}")
    log("Press Ctrl+C to stop")
    log("")
    
    LAST_MOD = load_state()
    current = get_modified()
    
    if not LAST_MOD:
        log(f"First run - tracking {len(current)} current files")
        save_state(current)
    else:
        for name, mtime in current.items():
            if name not in LAST_MOD or mtime != LAST_MOD[name]:
                log(f"[Change detected] {name}")
                sync()
                save_state(current)
                break
        else:
            log(f"No new changes - {len(current)} files tracked")
    
    # Save state for next run
    save_state(get_modified())
    log("Watcher ready - file changes will trigger sync")

if __name__ == "__main__":
    main()