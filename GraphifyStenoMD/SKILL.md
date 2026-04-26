# GraphifyStenoMD Unified Skill

**Trigger:** `/stenomd`
**Description:** GraphifyStenoMD - Romanian Parliament Knowledge Brain Enhancements

---

## Quick Reference

| Command | Action |
|---------|-------|
| `/stenomd query "X"` | Query knowledge graph |
| `/stenomd xquery ...` | Extended query patterns |
| `/stenomd analyze` | Show analytics |
| `/stenomd analyze gaps` | Show missing data |
| `/stenomd enrich` | Show enrichment targets |
| `/stenomd sync` | Show sync options |
| `/stenomd task` | Show tasks |
| `/stenomd scrape` | Show scraping priorities |
| `/stenomd report` | Generate reports |

---

## Graph Location

Main graph: `Graphify/graphify-out/graph.json`

Query with: `/graphify query "TERM" --graph Graphify/graphify-out/graph.json`

---

## Skills

### Query Skill
```
/stenomd query "TANASESCU"
```
Searches graph for politician, law, or session.

### XQuery Skill (Extended)
```
/stenomd xquery cross_party          # Cross-party collaborations
/stenomd xquery session --year 2024  # Session search
/stenomd xquery constituency Dolj    # Constituency search
/stenomd xquery committee buget    # Committee search
/stenomd xquery temporal PATTERN   # Time-based patterns
```

### Analyze Skill
```
/stenomd analyze
/stenomd analyze coverage  
/stenomd analyze activity
/stenomd analyze gaps
```
Generates analytics from graph data.

### Report Skill
```
/stenomd report coverage
/stenomd report activity
/stenomd report weekly
/stenomd report trends
```

### Enrich Skill
```
/stenomd enrich --type party
/stenomd enrich --type speeches
```
Shows enrichment targets (doesn't auto-enrich).

### Sync Skill
```
/stenomd sync --validate
/stenomd sync --dry-run
```
Validates vault/graph consistency.

### Task Skill
```
/stenomd task list
/stenomd task show TASK-010
```
Shows project tasks.

---

## Agent Scripts

### Gap-Aware Scraper
```bash
python3 GraphifyStenoMD/agents/scraper_agent.py --analyze
```
Analyzes graph for data gaps.

### Enrichment Agent
```bash
python3 GraphifyStenoMD/agents/enrichment_agent.py --analyze
```
Shows enrichment targets.

### Analytics Agent
```bash
python3 GraphifyStenoMD/agents/analytics_agent.py --type coverage
python3 GraphifyStenoMD/agents/analytics_agent.py --type activity
python3 GraphifyStenoMD/agents/analytics_agent.py --type trends
```
Generates reports.

### Validator
```bash  
python3 GraphifyStenoMD/agents/validator_agent.py --check all
```
Validates data consistency.

---

## Queries

See `queries/` directory for query templates:
- `politician_activity.md`
- `law_co_sponsors.md`  
- `party_members.md`
- `gap_analysis.md`
- `session_search.md`
- `constituency_query.md`
- `committee_query.md`

---

## Workflows

```bash
# Daily analysis
python3 GraphifyStenoMD/workflows/daily_scrape.py

# Weekly report
python3 GraphifyStenoMD/workflows/weekly_report.py

# Save report
python3 GraphifyStenoMD/workflows/weekly_report.py --save
```

---

## Integration

This skill is designed for **OptionB** (standalone, manual trigger):
- No auto-sync to vault
- No auto-enrichment
- Manual confirmation required for all operations
- Read-only graph access