# Sessions by Date Range
query:: Parliamentary sessions organized chronologically

## Recent Sessions (Last 30 Days)

```dataview
TABLE WITHOUT ID
file.link as Session,
date,
chamber,
length(participants) as Speakers,
length(frontmatter.laws_discussed) as Laws
FROM "sessions"
WHERE date >= date(today) - dur(30, "days")
SORT date DESC
```

## Sessions by Chamber

### Senate

```dataview
TABLE date, length(participants) as Speakers
FROM "sessions/senate"
WHERE date >= "2026-01-01"
SORT date DESC
LIMIT 20
```

### Camera Deputatilor

```dataview
TABLE date, length(participants) as Speakers
FROM "sessions/deputies"
WHERE date >= "2024-01-01"
SORT date DESC
LIMIT 20
```

## Session Timeline

```dataview
LIST
FROM "sessions"
WHERE date
SORT date DESC
```