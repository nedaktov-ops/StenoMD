# Graph Network - MP Relationships
query:: Visualize relationships between politicians

## Co-sponsorship Network

```dataview
TABLE WITHOUT ID
file.link as MP,
chamber,
contains(party, "PSD") as PSD,
contains(party, "PNL") as PNL,
contains(party, "USR") as USR,
contains(party, "AUR") as AUR
FROM "politicians"
WHERE party
LIMIT 50
```

## Same-Party Network

```dataview
LIST
FROM "politicians"
WHERE party = "PSD"
SORT file.name
```

## Cross-Chamber Relationships

```dataview
TABLE party, chamber, count() as Count
FROM "politicians"
WHERE party
GROUP BY party, chamber
```

## Relationship Types in Sessions

```dataview
TABLE chamber, length(participants) as Total_Speakers
FROM "sessions"
WHERE date >= "2025-01-01"
GROUP BY chamber
```

## Session Co-attendance

```dataview
LIST
FROM "sessions"
WHERE contains(participants, "Marcel Ciolacu")
WHERE contains(participants, "Nicolae Ciuca")
```

## Activity Summary

```dataview
TABLE WITHOUT ID
file.link as Politician,
party,
chamber,
default(frontmatter.sessions_appeared, []) as Appearances,
length(default(frontmatter.sessions_appeared, [])) as Session_Count
FROM "politicians"
WHERE party
SORT Session_Count DESC
LIMIT 25
```