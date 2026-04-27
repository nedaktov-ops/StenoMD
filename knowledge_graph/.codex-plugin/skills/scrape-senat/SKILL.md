---
name: scrape-senat
description: Scrape Romanian Senate (senat.ro) for senate sessions, senator profiles, and legislation. Use when user says "scrape senate", "senat.ro", "senate sessions".
allowed-tools: Bash, Read, Write, Task
---

# Scrape senat.ro

Scrape the Romanian Senate website.

## Prerequisites
Same as scrape-cdep.

## Workflow

### Step 1: Create Session
```bash
curl -s http://127.0.0.1:8000/sessions \
  -X POST -H 'content-type: application/json' \
  -d '{"name":"senat-scrape","start_url":"https://www.senat.ro/"}'
```

### Step 2: Navigate to Stenograms
```bash
curl -s "http://127.0.0.1:8000/sessions/$SESSION_ID/navigate?url=https://www.senat.ro/"
```

### Step 3: Process via Existing Pipeline
```bash
python3 scripts/agents/senat_agent.py --year 2024 --sync-vault
```

## Output
- Raw HTML: `data/senate/`
- Processed: `vault/politicians/senators/`
- Knowledge Graph: entities.json updated

## Notes
- senat.ro only shows current legislature (2024-2028)
- 136 senators in current legislature
- 15 committees