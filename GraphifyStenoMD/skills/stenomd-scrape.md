# StenoMD Scrape Skill

**Trigger:** `/stenomd scrape`
**Purpose:** Run gap-aware scraping to fill missing data

---

## Usage

```
/stenomd scrape                          # Analyze gaps, show priorities
/stenomd scrape --chamber cdep        # Scrape Chamber of Deputies
/stenomd scrape --chamber senat        # Scrape Senate
/stenomd scrape --years 2024,2025       # Specific years
/stenomd scrape --agents               # Show gap analysis
```

---

## What It Does

1. **Analyzes graph** for missing data
2. **Prioritizes** scraping based on gaps
3. **Runs scraping** with existing agents (cdep_agent, senat_agent)
4. **Reports** what was added

---

## Gap Analysis

The skill reads the knowledge graph to find:
- Politicians without profiles
- Sessions not yet scraped
- Laws without sponsor data
- Missing speeches

---

## Example Output

```
=== Gap Analysis ===
Politicians: 944 profiles, 12 missing party data
Sessions: 2131 tracked, 89 not scraped
Laws: 1976 documented, 456 missing sponsors

=== Priority Queue ===
1. Chamber of Deputies 2025 (142 new sessions)
2. Senate 2025 (89 new sessions)  
3. Add sponsor data to 456 laws

=== Scraping ===
[scrape_parliament_activity.py --chamber cdep --years 2025]
```

---

## Integration

Uses existing scripts:
- `scripts/agents/cdep_agent.py`
- `scripts/agents/senat_agent.py`
- `scripts/stenomd_master.py`

---

## Notes

- Does NOT auto-sync to vault (OptionB)
- Shows what WOULD be done first
- Manual confirmation required
- Read-only graph access