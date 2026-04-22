# StenoMD Brain Architecture

## Overview

The StenoMD Brain uses a dual-layer architecture:
1. **Knowledge Graph Layer** - mempalace for extracting entities from stenograms
2. **Application Layer** - Skills/apps for consuming the knowledge graph

## System Components

```
┌─────────────────────────────────────────────────┐
│              Obsidian Vault (This)               │
│  - Browse and search knowledge                 │
│  - Notes, templates, documentation            │
│  - Manual research and exploration            │
└─────────────────────────────────────────────────┘
                       │
                       ▼ (via scripts)
┌─────────────────────────────────────────────────┐
│              Skills/Apps (skills/)              │
│  - Web search interface                        │
│  - Mobile API                                 │
│  - MCP server for AI                         │
│  - Analytics                                 │
└─────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│           Knowledge Graph (knowledge_graph/) │
│  - mempalace engine                           │
│  - Entity extraction                        │
│  - Relationship mapping                    │
└─────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              Raw Data (data/)                  │
│  - Stenogram PDFs/HTML                        │
│  - Monitorul Oficial sources                 │
└─────────────────────────────────────────────────┘
```

## Query Flow

1. **Manual**: Open vault → Search notes → Reference knowledge
2. **Scripted**: Run `_scripts/query-brain.py` → Query knowledge graph
3. **Skill-based**: Use skills/skills/* to expose via API
4. **AI-assisted**: Use MCP skill for LLM context

## Daily Workflow

1. GitHub Actions fetches new stenograms → `data/`
2. mempalace processes → updates `knowledge_graph/entities.json`
3. Vault scripts can query/display → notes auto-update
4. Skills serve via APIs → web/mobile/AI consume

## Maintenance

- Run: `python vault/_scripts/query-brain.py` for CLI queries
- Run: `bash vault/_scripts/sync-vault.sh` to sync notes with KG
- Check logs in `knowledge_graph/logs/`

## Tagging Convention

- `#politician` - MP profiles
- `#session` - Stenogram sessions  
- `#law` - Legislation
- `#committee` - Committee info
- `#romania` - Romanian context