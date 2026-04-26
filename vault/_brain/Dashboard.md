# Dashboard Analytics

> Quick overview queries for vault health

## Vault Statistics

| Metric | Count |
|--------|-------|
| Deputies | `= length(filter(folder("politicians/deputies"), (f) => true))` |
| Senators | `= length(filter(folder("politicians/senators"), (f) => true))` |
| Laws | `= length(filter(folder("laws"), (f) => true))` |
| Sessions | `= length(filter(folder("sessions"), (f) => true))` |
| Proposals | `= length(filter(folder("proposals"), (f) => true))` |
| Committees | `= length(filter(folder("committees"), (f) => true))` |

## Top 10 Most Active Deputies

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  party as "Party",
  laws_proposed as "Proposals",
  speeches_count as "Speeches"
FROM "politicians/deputies"
SORT laws_proposed DESC
LIMIT 10
```

## Top 10 Most Active Speakers

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  party as "Party",
  speeches_count as "Speeches"
FROM "politicians/deputies"
SORT speeches_count DESC
LIMIT 10
```

## Party Distribution

```dataview
TABLE WITHOUT ID
  party as "Party",
  length(file) as "Members"
FROM "politicians/deputies"
GROUP BY party
FLATTEN
SORT length(file) DESC
```

## Recent Sessions

```dataview
LIST
FROM "sessions/deputies"
WHERE date >= "2025-01-01"
SORT date DESC
LIMIT 10
```

## Recent L.aws

```dataview
LIST
FROM "laws"
WHERE year >= "2025"
LIMIT 10
```

## Brain Coverage

| Section | Files |
|---------|-------|
| Sensory Input | `= length(filter(folder(""), (f) => contains(f.tags, "sensory")))` |
| Processing | `= length(filter(folder(""), (f) => contains(f.tags, "processing")))` |
| Memory | `= length(filter(folder(""), (f) => contains(f.tags, "memory")))` |
| Action/Output | `= length(filter(folder(""), (f) => contains(f.tags, "action")))` |