# StenoMD Report Skill

**Trigger:** `/stenomd report`
**Purpose:** Generate project reports from graph data

---

## Usage

```
/stenomd report coverage                 # Data coverage report
/stenomd report activity               # Activity report
/stenomd report weekly              # Weekly summary
/stenomd report monthly             # Monthly summary
/stenomd report trends              # Trend analysis
/stenomd report export --format json # Export as JSON
```

---

## Report Types

### Coverage Report
```
/stenomd report coverage

# Generated: GraphifyStenoMD/reports/coverage_TIMESTAMP.md
```

Shows:
- Politician profiles completeness
- Session documentation coverage
- Law tracking completeness
- Data quality metrics

### Activity Report
```
/stenomd report activity

# Generated: GraphifyStenoMD/reports/activity_TIMESTAMP.md
```

Shows:
- Most active politicians
- Most discussed laws
- Most active sessions
- Party activity comparison

### Weekly Report
```
/stenomd report weekly

# Generated: GraphifyStenoMD/reports/weekly_TIMESTAMP.md
```

Shows:
- New data added this week
- Changes to existing entities
- Gap closure progress

### Trend Report
```
/stenomd report trends

# Generated: GraphifyStenoMD/reports/trends_TIMESTAMP.md
```

Shows:
- Activity over time
- Session frequency
- Law introduction patterns
- Party collaboration trends

---

## Output Formats

| Format | Extension | Use |
|--------|----------|-----|
| Markdown | `.md` | Readable (default) |
| JSON | `.json` | Programmatic |
| HTML | `.html` | Web view |

---

## Report Templates

Place in `reports/templates/`:
- `coverage_template.md`
- `activity_template.md`
- `weekly_template.md`