# Gap-Aware Scraper - Usage Guide

## Quick Start

### 1. Analyze Gap Priorities
```bash
cd /home/adrian/Desktop/NEDAILAB/StenoMD
python3 scripts/scraper_orchestrator.py --status
```

Output:
```
=== Scraper Status ===
Graph nodes: 16834
Graph edges: 25094

=== Gap Summary ===
Total missing data points: 16187

=== Priorities ===
  1. [HIGH] senat_agent.py: 1929 party
  2. [HIGH] cdep_agent.py: 6293 party
  3. [MEDIUM] speech_extractor.py: 1929 speeches
  4. [MEDIUM] scrape_committees.py: 1929 committees
  5. [LOW] enrich_laws.py: 1976 sponsors
```

### 2. Run Gap-Aware Scraper

```bash
# Scrape only missing party data
python3 scripts/scraper_gap_aware.py --type party --limit 50

# Scrape only missing committees
python3 scripts/scraper_gap_aware.py --type committees --limit 30
```

---

## How It Works

### 1. Load Graph
First time: `/graphify vault --output Graphify/graphify-out`

### 2. Analyze Gaps
`scraper_orchestrator.py --status` reads graph.json and finds:
- Which politicians need party data
- Which need speeches
- Which need committees
- Which laws need sponsors

### 3. Run Targeted Scraper
`scraper_gap_aware.py --type X` targets ONLY entities missing that data

---

## Priority Workflow

### Daily Workflow
```bash
# 1. Check gaps
python3 scripts/scraper_orchestrator.py --status

# 2. Auto-select best scraper
python3 scripts/scraper_orchestrator.py --auto
```

### Specific Target
```bash
# Party data for senators
python3 scripts/scraper_gap_aware.py --type party --limit 20

# Then update graph
/graphify vault --update
```

---

## Scripts Created

| Script | Purpose | Usage |
|--------|---------|-------|
| `scraper_orchestrator.py` | Analyzes gaps, sets priorities | `--status`, `--auto` |
| `scraper_gap_aware.py` | Targets specific data type | `--type party --limit 50` |

---

## Example Use Cases

### Use Case 1: Find What Needs Data Most
```bash
python3 scripts/scraper_orchestrator.py --status
```
Shows priorities based on gaps.

### Use Case 2: Scrape Only What Needs Party
```bash
python3 scripts/scraper_gap_aware.py --type party --limit 30
```
Only scrapes 30 politicians missing party data.

### Use Case 3: Batch Scrape All Party Data
```bash
python3 scripts/scraper_gap_aware.py --type party --limit 200
```
Scrapes 200 politicians (adjust as needed).

### Use Case 4: After Scraping, Update Graph
```bash
/graphify vault --update
```
Updates graph.json with new data.

---

## Post-Scraping Workflow

After running a scraper:
1. Review scraped data in `data/gap_aware/`
2. Import into vault if valid
3. Update graph: `/graphify vault --update`
4. Check new gaps: `python3 scripts/scraper_orchestrator.py --status`