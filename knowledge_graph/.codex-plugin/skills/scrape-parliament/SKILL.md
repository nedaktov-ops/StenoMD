---
name: scrape-parliament
description: Complete parliamentary data scrape - scrapes both cdep.ro and senat.ro, processes data, updates knowledge graph. Use when user says "scrape parliament", "update parliament data", "refresh parliamentary knowledge", "full scrape".
allowed-tools: bash, Task
---

# Scrape Complete Parliament Data

Run full pipeline to scrape and update all parliamentary data.

## Prerequisites

### Auto-Browser (Docker)
```bash
cd auto-browser && docker compose up -d
```

## Run Full Pipeline

### Option 1: Use existing pipeline script
```bash
python3 scripts/run_complete_pipeline.py --full
```

### Option 2: Manual steps

1. Scrape cdep.ro:
```bash
python3 scripts/agents/cdep_agent.py --years 2024,2025 --max-id 50 --sync-vault
```

2. Scrape senat.ro:
```bash
python3 scripts/agents/senat_agent.py --year 2024 --max 30 --sync-vault
```

3. Sync vault:
```bash
python3 scripts/merge_vault_to_kg.py
```

4. Update MemPalace:
```bash
cd knowledge_graph && mempalace mine ../vault
```

## Output
- Updated vault with new MPs, sessions, laws
- Knowledge graph enriched
- MemPalace indexed
- Ready for queries

## Status Checks

### View current status
```bash
python3 scripts/stenomd_master.py --status
```

### Check vault contents
```bash
ls -la vault/politicians/deputies/ | wc -l
ls -la vault/sessions/deputies/ | wc -l
```

### Check knowledge graph
```bash
python3 -c "import json; print(json.load(open('knowledge_graph/entities.json'))['metadata'])"