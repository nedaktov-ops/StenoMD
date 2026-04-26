---
name: Graphify Project Enhancer
description: use Graphify - Automatic knowledge graph enhancements for StenoMD project
trigger: use Graphify
---

# use Graphify

**Trigger Phrase:** `use Graphify`  
**Purpose:** Automatically enhance your StenoMD project using knowledge graph capabilities

---

## How "use Graphify" Works

When you type `use Graphify [CONTEXT]`, OpenCode will:
1. Analyze your request context
2. Determine the best Graphify workflow to run
3. Execute the appropriate scripts
4. Report findings and recommendations

---

## Context Patterns and Actions

### Pattern 1: Analysis Requests
**Trigger:** `use Graphify analyze [TARGET]` or `use Graphify check [TARGET]`
**Examples:**
- `use Graphify analyze gaps` - Find missing data in your project
- `use Graphify check health` - Validate data consistency
- `use Graphify analyze activity` - Show most active politicians
- `use Graphify analyze coverage` - Data coverage statistics
- `use Graphify analyze scrapers` - Gap analysis for scrapers

**Action:** Run `workflows/missing_data.py` or `scraper_orchestrator.py`

**Example Output:**
```
=== Gap Analysis ===
Missing party: 8223
Missing speeches: 8223
Missing committees: 8223
Total gaps: 28,776
```

---

### Pattern 2: Query Requests
**Trigger:** `use Graphify query [ENTITY]` or `use Graphify find [ENTITY]`
**Examples:**
- `use Graphify query Vasile Citea` - Find politician details
- `use Graphify query 38-2026` - Find law details
- `use Graphify find PSD` - Find party members
- `use Graphify query session 2024-12-21` - Find session details

**Action:** Use graph.json to find entity and connections

---

### Pattern 3: Report Requests
**Trigger:** `use Graphify report [TYPE]` or `use Graphify generate [TYPE]`
**Examples:**
- `use Graphify report coverage` - Generate coverage report
- `use Graphify report weekly` - Generate weekly report
- `use Graphify generate trends` - Generate trend analysis

**Action:** Run `agents/analytics_agent.py`

---

### Pattern 4: Validation Requests
**Trigger:** `use Graphify validate` or `use Graphify check links`
**Examples:**
- `use Graphify validate` - Run full health check
- `use Graphify check links` - Find broken wikilinks
- `use Graphify check yaml` - Validate frontmatter

**Action:** Run `workflows/health_check.py`

---

### Pattern 5: Scraper Requests
**Trigger:** `use Graphify scrape [TARGET]` or `use Graphify scrapers`
**Examples:**
- `use Graphify analyze scrapers` - Show scraper gap priorities
- `use Graphify scrape party` - Run gap-aware party scraper
- `use Graphify scrape speeches` - Run gap-aware speech scraper
- `use Graphify scrapers status` - Show scraper priorities

**Action:** Run `scraper_orchestrator.py` or `scraper_gap_aware.py`

**Example Output:**
```
=== Scraper Status ===
Gap Summary: 16187 total

=== Priorities ===
  1. [HIGH] senat_agent.py: 1929 party
  2. [HIGH] cdep_agent.py: 6293 party
  3. [MEDIUM] speech_extractor.py: 1929 speeches
  4. [MEDIUM] scrape_committees.py: 1929 committees
  5. [LOW] enrich_laws.py: 1976 sponsors
```

---

### Pattern 6: Workflow Requests
**Trigger:** `use Graphify [WORKFLOW]`
**Examples:**
- `use Graphify daily` - Run daily analysis workflow
- `use Graphify weekly` - Run weekly report workflow
- `use Graphify audit` - Run full audit

**Action:** Run `workflows/orchestrator.py`

---

### Pattern 7: Enrichment Awareness
**Trigger:** `use Graphify enrich [TYPE]`
**Examples:**
- `use Graphify enrich party` - Show party enrichment targets
- `use Graphify enrich speeches` - Show speeches targets

**Note:** Shows targets only (OptionB - no auto-enrichment)

---

## Quick Reference

| Your Request | Action | Runs |
|--------------|--------|------|
| `use Graphify analyze gaps` | Gap analysis | missing_data.py |
| `use Graphify analyze scrapers` | Scraper priorities | scraper_orchestrator.py |
| `use Graphify check health` | Validation | health_check.py |
| `use Graphify query NAME` | Search graph | graph.json |
| `use Graphify report coverage` | Coverage report | analytics_agent.py |
| `use Graphify validate` | Full health check | health_check.py |
| `use Graphify daily` | Daily workflow | orchestrator.py |
| `use Graphify scrape party` | Run party scraper | scraper_gap_aware.py |

---

## Example Workflows

### Find Missing Party Data
```
you: use Graphify analyze scrapers
opencode: Runs scraper_orchestrator.py --status, reports priorities
```

### Run Targeted Scraper
```
you: use Graphify scrape party
opencode: Runs scraper_gap_aware.py --type party, scrapes only politicians missing party
```

### Find Missing Data in Project
```
you: use Graphify analyze gaps
opencode: Runs missing_data.py, reports 28,776 missing data points
```

### Generate Report
```
you: use Graphify report activity
opencode: Runs analytics_agent.py --type activity
```

---

## Prerequisites

Before using `use Graphify`, ensure:
- Graph exists at `Graphify/graphify-out/graph.json`
- If no graph: Run `/graphify vault --output Graphify/graphify-out` first

---

## IMPORTANT NOTES

1. **Graph Required**: First run `/graphify vault` if no graph exists

2. **Read-Only**: Most operations are read-only analysis (OptionB design)

3. **No Auto-Fix**: Shows gaps/issues but doesn't auto-fix (manual confirmation required)

4. **Manual Trigger**: Type `use Graphify` followed by context - OpenCode executes appropriate workflow

5. **Scraper Gap-Aware**: New! Use `analyze scrapers` to see which scrapers should run based on graph gaps

---

*GraphifyStenoMD v1.1 - Trigger with Gap-Aware Scraping*