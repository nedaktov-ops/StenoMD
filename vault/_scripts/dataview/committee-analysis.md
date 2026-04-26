# Committee Analysis

```dataview
TABLE WITHOUT ID
  link(file.link, name) as Deputy,
  party,
  constituency,
  committees[0].name as Committee,
  committees[0].role as Role,
  laws_proposed as "Laws",
  motions as "Motions"
FROM "politicians/deputies"
WHERE committees
FLATTEN committees[0] as primary_committee
SORT primary_committee.name ASC
LIMIT 50
```

## Committees Breakdown

| Committee | Members | PSD | PNL | AUR | USR | Other |
|-----------|---------|-----|-----|-----|-----|-------|
| %%TABLE rows: this WHERE type="deputy" AND committees FLATTEN this.committees[0].name as c GROUP BY c%%