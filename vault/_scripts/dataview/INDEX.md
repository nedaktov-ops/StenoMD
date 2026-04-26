# StenoMD Dataview Queries

> Query library for the Romanian Parliament Knowledge Vault

## Quick Reference

| Category | Query File | Purpose |
|----------|-----------|---------|
| MP Activity | `mp-activity-overview.md` | Speeches, laws, committees |
| MP Ranking | `mp-activity-ranking.md` | Top 25 by total activity |
| MP Search | `mp-search.md` | Find MPs by name, party, constituency |
| Party Analysis | `party-analysis.md` | Party totals and breakdowns |
| Committee Analysis | `committee-analysis.md` | Committee membership |
| Constituency Analysis | `constituency-analysis.md` | Geographic distribution |
| Political Network | `political-network-analysis.md` | Party cohesion, cross-party |
| Legislation | `legislation-tracking.md` | Bills through process |
| Network Graph | `graph-network.md` | Visual relationships |
| MPs by Party | `mps-by-party.md` | Party membership |
| Laws by Sponsor | `laws-by-sponsor.md` | Bill sponsorships |
| Sessions | `sessions-by-date.md` | Parliamentary sessions |

## Common Queries

### Find an MP
```dataview
LIST
FROM "politicians/deputies"
WHERE contains(file.name, "Weber")
```

### Active MPs by Party
```dataview
TABLE party, 
  sum(rows.speeches_count) as Speeches,
  length(rows) as MPs
FROM "politicians/deputies"
GROUP BY party
SORT Speeches DESC
```

### Committee Composition
```dataview
TABLE party, length(rows) as Members
FROM "politicians/deputies"
WHERE committees
FLATTEN committees[0].name as comm
GROUP BY party
```

## Usage in Obsidian

1. Copy queries to your vault or reference them
2. Install Dataview plugin
3. Create new notes with query blocks

## Example: Create Dashboard Note

```markdown
# Parliament Dashboard

## Party Activity
```dataview
TABLE party, sum(rows.speeches_count) as Speeches
FROM "politicians/deputies"
GROUP BY party
```

## Active Legislators
```dataview
LIST
FROM "politicians/deputies"
WHERE speeches_count > 20
SORT speeches_count DESC
```
```

---
*Generated: 2026-04-26*
*For StenoMD Project*