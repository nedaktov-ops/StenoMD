#!/bin/bash
# StenoMD Dashboard Launcher

cd /home/adrian/Desktop/NEDAILAB/StenoMD

# Kill existing instance
pkill -f "dashboard.py" 2>/dev/null || true

# Start in background
nohup python3 -c "
import uvicorn
import sys
sys.path.insert(0, 'scripts')
from dashboard import app
uvicorn.run(app, host='0.0.0.0', port=8080)
" > dashboard.log 2>&1 &

echo "Dashboard starting on http://localhost:8080"
sleep 2
echo "Log: $(tail -5 dashboard.log)"