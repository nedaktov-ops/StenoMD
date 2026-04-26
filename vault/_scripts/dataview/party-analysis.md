# Cross-Party Collaboration Analysis

Find MPs from different parties who co-sponsor bills together (by shared proposals).

```dataview
TABLE WITHOUT ID
  link(file.link, name) as Deputy,
  party,
  constituency,
  laws_proposed as Proposals,
  motions as Motions
FROM "politicians/deputies"
WHERE type = "deputy"
SORT laws_proposed DESC
LIMIT 25
```

## Most Productive MPs by Party

### PSD (Social Democrats)
```dataview
LIST FROM "politicians/deputies"
WHERE party = "PSD"
SORT laws_proposed DESC
LIMIT 15
```

### PNL (National Liberals)
```dataview
LIST FROM "politicians/deputies"
WHERE party = "PNL"
SORT laws_proposed DESC
LIMIT 15
```

### AUR (Alliance for Unity)
```dataview
LIST FROM "politicians/deputies"
WHERE party = "AUR"
SORT laws_proposed DESC
LIMIT 15
```

### USR (Save Romania Union)
```dataview
LIST FROM "politicians/deputies"
WHERE party = "USR"
SORT laws_proposed DESC
LIMIT 15
```

## Party Totals

| Party | MPs | Total Proposals | Total Motions | Avg Activity |
|-------|-----|---------------|--------------|-------------|
| %%=length(filter(this, t => t.type = "deputy" AND t.party = "PSD"))%% | PSD | %%sum(filter(this, t => t.type = "deputy" AND t.party = "PSD").laws_proposed%% | %%sum(filter(this, t => t.type = "deputy" AND t.party = "PSD").motions%% | %%sum(filter(this, t => t.type = "deputy" AND t.party = "PSD").laws_proposed / length(filter(this, t => t.type = "deputy" AND t.party = "PSD"))%% |