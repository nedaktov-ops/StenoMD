# StenoMD Obsidian Setup Guide

## How to Open the StenoMD Vault in Obsidian

### Option 1: Command Line (Recommended)

```bash
/opt/Obsidian/obsidian /home/adrian/Desktop/NEDAILAB/StenoMD/vault
```

### Option 2: Open Obsidian First

1. Open Obsidian from your applications
2. Click "Open another vault"
3. Navigate to: `/home/adrian/Desktop/NEDAILAB/StenoMD/vault`
4. Select "Open"

---

## Navigation Guide

### Main Entry Points

| File | Purpose |
|------|---------|
| `Welcome.md` | Welcome screen with quick links |
| `00-Camera.md` | Daily feed and entry point |
| `politicians/Index.md` | Browse all MPs |
| `sessions/Index.md` | Browse sessions |
| `laws/Index.md` | Browse legislation |
| `committees/Index.md` | Browse committees |

### Using the Vault

1. **Search**: Press `Ctrl+P` to search any note
2. **Graph view**: Press `Ctrl+G` for graph visualization
3. **Backlinks**: Press `Ctrl+Shift+B` to see backlinks panel

---

## Daily Workflow in Obsidian

1. Open Obsidian → Vault opens to `Welcome.md`
2. Check `00-Camera.md` for daily updates
3. Browse `politicians/Index.md` to search MPs
4. Use `Ctrl+O` to jump to specific politician

---

## Notes are Auto-Synced

Run this to sync new data to vault:
```bash
cd /home/adrian/Desktop/NEDAILAB/StenoMD
python3 scripts/sync_vault.py
```

Then refresh Obsidian (`Ctrl+R`) to see new notes.