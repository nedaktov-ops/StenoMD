# GraphifyStenoMD Documentation

## Overview

GraphifyStenoMD provides knowledge graph capabilities for your StenoMD project with standalone, manual-trigger workflows.

## Quick Start

### 1. Build Knowledge Graph
```bash
cd /home/adrian/Desktop/NEDAILAB/StenoMD
/graphify vault --output /home/adrian/Desktop/NEDAILAB/StenoMD/Graphify/graphify-out
```

### 2. Run Daily Workflow
```bash
python3 GraphifyStenoMD/workflows/daily_scrape.py
```

### 3. Query the Graph
```bash
/graphify query "TANASESCU" --graph Graphify/graphify-out/graph.json
```

### 4. Generate Reports
```bash
python3 GraphifyStenoMD/agents/analytics_agent.py --type coverage
python3 GraphifyStenoMD/agents/analytics_agent.py --type activity
python3 GraphifyStenoMD/agents/analytics_agent.py --type trends
```

---

## Workflows

### Daily Workflow
Shows graph state and gap analysis:
```bash
python3 GraphifyStenoMD/workflows/daily_scrape.py
```
Output:
- Current graph statistics
- Data gaps identified
- Recommended actions

### Weekly Workflow
Generates weekly summary:
```bash
python3 GraphifyStenoMD/workflows/weekly_report.py --save
```
Output:
- Markdown report saved to reports/

### Missing Data Analysis
Shows all data gaps:
```bash
python3 GraphifyStenoMD/workflows/missing_data.py --enrich
```
Output:
- Missing party data
- Missing speeches
- Missing committees
- Resolution scripts

### Health Check
Validates data consistency:
```bash
python3 GraphifyStenoMD/workflows/health_check.py
python3 GraphifyStenoMD/workflows/health_check.py --type links
python3 GraphifyStenoMD/workflows/health_check.py --type yaml
python3 GraphifyStenoMD/workflows/health_check.py --type graph
```

### Orchestrator
Unified workflow interface:
```bash
python3 GraphifyStenoMD/workflows/orchestrator.py daily
python3 GraphifyStenoMD/workflows/orchestrator.py weekly
python3 GraphifyStenoMD/workflows/orchestrator.py analytics
```

---

## Agents

### Scraper Agent
Analyzes graph for data gaps:
```bash
python3 GraphifyStenoMD/agents/scraper_agent.py --analyze
```

### Enrichment Agent
Shows enrichment targets:
```bash
python3 GraphifyStenoMD/agents/enrichment_agent.py --analyze
```

### Validator Agent
Validates data consistency:
```bash
python3 GraphifyStenoMD/agents/validator_agent.py --check all
python3 GraphifyStenoMD/agents/validator_agent.py --check links
python3 GraphifyStenoMD/agents/validator_agent.py --check yaml
python3 GraphifyStenoMD/agents/validator_agent.py --check duplicates
```

### Analytics Agent
Generates reports:
```bash
python3 GraphifyStenoMD/agents/analytics_agent.py --type coverage --save
python3 GraphifyStenoMD/agents/analytics_agent.py --type activity --save
python3 GraphifyStenoMD/agents/analytics_agent.py --type trends --save
```

---

## Graph Location

Main graph file:
```
Graphify/graphify-out/graph.json
```

Query using `/graphify` with `--graph` flag:
```
/graphify query "TERM" --graph Graphify/graphify-out/graph.json
```

---

## File Structure

```
GraphifyStenoMD/
├── agents/
│   ├── scraper_agent.py
│   ├── enrichment_agent.py  
│   ├── validator_agent.py
│   └── analytics_agent.py
├── workflows/
│   ├── daily_scrape.py
│   ├── weekly_report.py
│   ├── missing_data.py
│   ├── health_check.py
│   └── orchestrator.py
├── queries/
│   ├── politician_activity.md
│   ├── law_co_sponsors.md
│   ├── party_members.md
│   ├── gap_analysis.md
│   ├── session_search.md
│   ├── constituency_query.md
│   └── committee_query.md
├── skills/
│   └── (various skills for OpenCode)
├── reports/
│   └── templates/
│       └── coverage_template.md
├── config.yaml
├── SKILL.md
└── README.md
```

---

## Design Philosophy

GraphifyStenoMD is designed for **OptionB**:
- No automatic modifications
- Manual trigger required
- Read-only graph access
- Safe, controlled operations

---

## Testing

Run tests:
```bash
python3 GraphifyStenoMD/tests/test_all.py
```

---

## Troubleshooting

### No graph found
Build the graph first:
```
/graphify vault --output Graphify/graphify-out
```

### Empty results
Check graph has data:
```
python3 GraphifyStenoMD/workflows/daily_scrape.py
```

### Validation errors
Run health check:
```
python3 GraphifyStenoMD/workflows/health_check.py
```

---

## Integration with OpenCode

The skills work with OpenCode when the graphify skill is installed. Use the `/stenomd` commands or direct Python scripts.

---

*GraphifyStenoMD v1.0 - Built for StenoMD project*