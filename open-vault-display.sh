#!/bin/bash
# Open StenoMD Vault in Obsidian with auto-refresh

cd /home/adrian/Desktop/NEDAILAB/StenoMD

# Sync first
python3 scripts/sync_vault.py

# Open Obsidian with vault
/opt/Obsidian/obsidian /home/adrian/Desktop/NEDAILAB/StenoMD/vault &

echo "Obsidian is opening..."
echo ""
echo "In Obsidian:"
echo "1. Look at the LEFT sidebar - click 'politicians' folder"
echo "2. Click on any .md file to view"
echo "3. Press Ctrl+P for Quick Switcher"
echo "4. Press Ctrl+R to refresh vault"
echo ""
echo "Files in vault:"
find vault/politicians -name "*.md" | head -10