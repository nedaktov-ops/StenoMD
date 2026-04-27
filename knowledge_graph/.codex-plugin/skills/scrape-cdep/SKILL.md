---
name: scrape-cdep
description: Scrape Romanian Chamber of Deputies (cdep.ro) for parliamentary transcripts, MP profiles, and session data. Use when user says "scrape cdep", "chamber deputies", "parliamentary sessions", "update parliament data".
allowed-tools: Bash, Read, Write, Task
---

# Scrape cdep.ro

Scrape the Chamber of Deputies website for parliamentary data.

## Prerequisites

### Option A: Auto-Browser (Docker - Primary)
```bash
cd auto-browser && docker compose up -d
# Wait for services to start
```

### Option B: Native Playwright (Fallback)
```bash
pip install playwright && playwright install chromium
```

## Workflow

### Step 1: Create Session (Auto-Browser)
```bash
curl -s http://127.0.0.1:8000/sessions \
  -X POST -H 'content-type: application/json' \
  -d '{"name":"cdep-scrape","start_url":"https://www.cdep.ro/pls/stenogr/"}'
```

### Step 2: Navigate to Stenograms
```bash
curl -s "http://127.0.0.1:8000/sessions/$SESSION_ID/navigate?url=https://www.cdep.ro/pls/stenogr/"
```

### Step 3: Get Content
```bash
curl -s "http://127.0.0.1:8000/sessions/$SESSION_ID/snapshot"
curl -s "http://127.0.0.1:8000/sessions/$SESSION_ID/get_text"
```

### Step 4: Save Raw Data
Save to: `data/cdep/scrape-$(date +%Y%m%d)/`

### Step 5: Process via Existing Pipeline
```bash
python3 scripts/agents/cdep_agent.py --years 2024,2025 --sync-vault
```

## Output
- Raw HTML: `data/cdep/stenogram_*.html`
- Processed: Updated vault files
- Knowledge Graph: entities.json updated

## Integration Points
- Uses existing `scripts/agents/cdep_agent.py`
- Updates vault via sync_vault.py
- Triggers MemPalace via bridge

## Notes
- cdep.ro blocks historical data 1996-2014 (returns 404)
- Current legislature: 2024-2028
- Session IDs available from calendar page