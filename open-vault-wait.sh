#!/bin/bash
# Wrapper that waits for Obsidian to fully initialize

/usr/bin/obsidian "/home/adrian/Desktop/NEDAILAB/StenoMD/vault" --disable-gpu --disable-dev-shm-usage --no-sandbox --disable-gpu-sandbox &

# Wait for window to appear
for i in {1..30}; do
    if xdotool search --name "Obsidian" 2>/dev/null | head -1 | grep -q .; then
        echo "Obsidian window detected"
        exit 0
    fi
    sleep 0.5
done

echo "Obsidian may have started"
