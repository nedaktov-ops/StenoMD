#!/bin/bash
# Open StenoMD Vault in Obsidian

OBSIDIAN_PATH="/opt/Obsidian/obsidian"
VAULT_PATH="/home/adrian/Desktop/NEDAILAB/StenoMD/vault"

if [ -x "$OBSIDIAN_PATH" ]; then
    "$OBSIDIAN_PATH" "$VAULT_PATH"
    echo "Opened Obsidian with StenoMD vault"
else
    echo "Obsidian not found at $OBSIDIAN_PATH"
    echo "Trying alternative locations..."
    for path in /usr/bin/obsidian /snap/obsidian/current/bin/obsidian ~/obsidian/obsidian; do
        if [ -x "$path" ]; then
            "$path" "$VAULT_PATH"
            echo "Opened with: $path"
            exit 0
        fi
    done
    echo "Please open Obsidian manually, then select: $VAULT_PATH"
fi