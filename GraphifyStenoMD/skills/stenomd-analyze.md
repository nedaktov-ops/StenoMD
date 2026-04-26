# StenoMD Analyze Skill

**Trigger:** `/stenomd analyze`
**Purpose:** Generate analytics and reports on project data

---

## Usage

```
/stenomd analyze                          # Coverage overview
/stenomd analyze coverage                # Data coverage stats
/stenomd analyze activity              # Activity leaderboard
/stenomd analyze collaboration       # Cross-party patterns
/stenomd analyze gaps                # Missing data analysis
/stenomd analyze trends              # Temporal trends
/stenomd analyze party PSD             # Specific party analysis
/stenomd analyze politician "NAME"   # Specific politician
/stenomd analyze --format json      # JSON output
/stenomd analyze --format md      # Markdown output
```

---

## What It Does

1. **Generates analytics** from graph data
2. **Creates visualizations** when possible
3. **Produces reports** in requested format
4. **Shows insights** not visible in raw data

---

## Analysis Types

| Type | Metrics | Source |
|------|---------|--------|
| `coverage` | % with profiles, sessions, laws | Graph nodes |
| `activity` | speeches, laws proposed, sessions | Node degrees |
| `collaboration` | co-sponsorship, cross-party | Edge patterns |
| `gaps` | missing fields | Node attributes |
| `trends` | over time | Temporal edges |

---

## Example Outputs

### Coverage Analysis
```
/stenomd analyze coverage

=== Data Coverage ===
Politicians: 944 profiles / 467 total = 202%
  - With party: 932 (99%)
  - With speeches: 710 (75%)
  - With committees: 788 (83%)
  - Complete: 654 (69%)

Sessions: 2131 documented
  - With speakers: 1890 (89%)
  - Complete: 1723 (81%)

Laws: 1976 tracked
  - With sponsors: 1520 (77%)
  - With sessions: 1843 (93%)
  - Complete: 1456 (74%)
```

### Activity Leaderboard
```
/stenomd analyze activity

=== Top 20 Most Active Politicians ===
Rank | Name                    | Speeches | Laws | Sessions
-----|------------------------|----------|------|---------
  1  | ANDREI DANIEL GHEORGHE |   87     |  5   |   45
  2  | ANAMARIA GAVRILĂ       |   72     |  3   |   38
  3  | VERGINIA VEDINAŞ       |   65     |  2   |   32
  4  | TUDOR IONESCU         |   58     |  4   |   28
  5  | RALUCA TURCAN         |   52     |  6   |   25
```

### Gap Analysis
```
/stenomd analyze gaps

=== Missing Data ===
Politicians missing party: 12
Politicians missing speeches: 234
Politicians missing committees: 156
Laws missing sponsors: 456
```

---

## Output Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| Markdown | .md | Default, readable |
| JSON | .json | Programmatic |
| HTML | .html | Visualization |

---

## Notes

- Read-only analysis
- Uses graph data only
- No modifications to vault