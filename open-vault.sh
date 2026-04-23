#!/bin/bash
# Open StenoMD Vault in Obsidian

OBSIDIAN_PATH="/usr/bin/obsidian"
VAULT_PATH="/home/adrian/Desktop/NEDAILAB/StenoMD/vault"

$OBSIDIAN_PATH "$VAULT_PATH" --disable-gpu --disable-dev-shm-usage --no-sandbox --disable-gpu-sandbox &