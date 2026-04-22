#!/bin/bash
# query-brain.sh - Query the StenoMD knowledge graph from Obsidian vault
# Usage: ./query-brain.sh <query_type> [args]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/query-brain.py"

case "$1" in
    politician)
        NAME="$2"
        python3 "$PYTHON_SCRIPT" politician "$NAME"
        ;;
    session)
        DATE="$2"
        python3 "$PYTHON_SCRIPT" session "$DATE"
        ;;
    law)
        LAW="$2"
        python3 "$PYTHON_SCRIPT" law "$LAW"
        ;;
    recent)
        python3 "$PYTHON_SCRIPT" session ""
        ;;
    *)
        echo "Usage: $0 {politician|session|law} [query]"
        exit 1
        ;;
esac