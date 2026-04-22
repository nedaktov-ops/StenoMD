#!/bin/bash
# Auto-sync StenoMD knowledge graph to Obsidian vault
# Run this script periodically or on file change

STENO_DIR="/home/adrian/Desktop/NEDAILAB/StenoMD"

echo "=== StenoMD Auto-Sync ==="
echo "Timestamp: $(date)"

cd "$STENO_DIR"

# Update knowledge graph first
echo "[1] Updating knowledge graph..."
python3 scripts/update_knowledge_graph.py

# Validate
echo "[2] Validating..."
python3 scripts/validate_knowledge_graph.py

# Sync to vault
echo "[3] Syncing to Obsidian vault..."
python3 scripts/sync_vault.py

echo "[4] Complete!"
echo "Refresh Obsidian with Ctrl+R to see updated notes."