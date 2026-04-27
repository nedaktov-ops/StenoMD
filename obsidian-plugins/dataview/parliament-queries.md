# Dataview Parliament Queries

Pre-built queries for parliament data in Obsidian.

## Active MPs (by speeches)

```dataview
TABLE WITHOUT ID
FROM "politicians"
WHERE speeches_count > 20
SORT speeches_count DESC
LIMIT 10
```

## Recent Sessions

```dataview
TABLE WITHOUT ID
FROM "sessions"
WHERE date >= date("2024-01-01")
SORT date DESC
LIMIT 20
```

## Law Proposals by Party

```dataview
TABLE WITHOUT ID
FROM "laws"
WHERE contains(sponsors, "PSD")
LIMIT 10
```

## MPs by Party

```dataview
TABLE WITHOUT ID
FROM "politicians/deputies"
WHERE party = "PSD"
LIMIT 20
```

## Session Participation

```dataview
TABLE WITHOUT ID
FROM "sessions"
WHERE contains(participants, "Vasile Citea")
SORT date DESC
```