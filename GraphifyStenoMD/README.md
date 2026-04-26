# GraphifyStenoMD Integration

**Version:** 1.0  
**Created:** 2026-04-26  
**Project:** StenoMD - Romanian Parliament Knowledge Brain

---

## Overview

GraphifyStenoMD extends your StenoMD project with knowledge graph capabilities. It creates intelligent workflows, queries, and automation while keeping systems separate (OptionB: read-only integration).

## Project Structure

```
GraphifyStenoMD/
├── README.md                 # This file
├── config.yaml              # Configuration
├── skills/                # OpenCode skills
├── agents/                # Specialized agents
├── queries/               # Query templates
├── workflows/              # Workflow scripts
├── reports/              # Report templates
├── docs/                 # Documentation
├── templates/             # File templates
├── tests/                 # Test suites
├── output/               # Generated outputs
└── cache/                # Cached data
```

## Quick Start

### Build Knowledge Graph
```
/graphify /home/adrian/Desktop/NEDAILAB/StenoMD/vault --output /home/adrian/Desktop/NEDAILAB/StenoMD/Graphify/graphify-out
```

### Query Politician
```
/stenomd query "Vasile Citea"
```

### Analyze Activity
```
/stenomd analyze politician "TANASESCU ALINA"
```

## Skills Available

| Skill | Trigger | Purpose |
|-------|---------|---------|
| Scrape | `/stenomd scrape` | Run scraping with gap awareness |
| Enrich | `/stenomd enrich` | Run enrichment pipelines |
| Query | `/stenomd query` | Query the knowledge graph |
| Sync | `/stenomd sync` | Sync vault and graph |
| Analyze | `/stenomd analyze` | Analytics and reporting |
| Task | `/stenomd task` | Task management |

## Agents Included

| Agent | Function |
|-------|----------|
| `scraper_agent.py` | Gap-aware scraping |
| `enrichment_agent.py` | Data gap enrichment |
| `validator_agent.py` | Data consistency validation |

## Query Templates

| Query | Use Case |
|-------|----------|
| `politician_activity.md` | Sessions a politician spoke in |
| `law_co_sponsors.md` | Law co-sponsorship network |
| `party_members.md` | Party membership |
| `gap_analysis.md` | Missing data fields |

## Workflows

| Workflow | Purpose |
|----------|---------|
| `daily_scrape.py` | Daily data update |
| `weekly_report.py` | Weekly analytics |
| `health_check.py` | Data validation |

## Integration Points

| System | Integration |
|--------|------------|
| `vault/` | Graph-aware sync (on demand) |
| `knowledge_graph/entities.json` | Read-only |
| `scripts/agents/` | Gap-aware scraping |

## Why OptionB (Standalone)

- No automatic modifications
- Manual trigger only
- Read-only graph access
- Safe, controlled integration

## Next Steps

1. Review `config.yaml` settings
2. Explore skills in `/skills`
3. Try a query: `/stenomd query "Index"`
4. Run `/stenomd analyze coverage`

---

**Linked to:** Main project graph at `Graphify/graphify-out/graph.json`