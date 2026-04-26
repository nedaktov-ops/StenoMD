# Political Network Analysis

> Queries for understanding relationships in the Parliament

## MPs by Party Cohesion

```dataview
TABLE party, 
  sum(rows.speeches_count) as TotalSpeeches,
  length(rows) as MPs,
  sum(rows.laws_proposed) as TotalLaws
FROM "politicians/deputies"
WHERE party != null
GROUP BY party
SORT TotalSpeeches DESC
```

## Most Active Deputies

```dataview
TABLE WITHOUT ID
  file.link as Deputy,
  party,
  constituency,
  speeches_count,
  laws_proposed,
  length(committees) as Committees
FROM "politicians/deputies"
WHERE speeches_count > 15
SORT speeches_count DESC
LIMIT 20
```

## Committee Leaders by Party

```dataview
TABLE WITHOUT ID
  file.link as Deputy,
  party,
  committees[0].name as Committee,
  committees[0].position as Position
FROM "politicians/deputies"
WHERE committees
WHERE committees[0].position = "Chairperson"
SORT party
```

## Find Co-Sponsors (Same Party)

> Note: Requires sponsors data in bills

```dataview
LIST
FROM "laws"
WHERE contains(sponsors.party, "PSD")
WHERE process_stage = "in_committee"
```

## Session Attendance Patterns

```dataview
TABLE party, 
  average(rows.speeches_count) as AvgSpeeches,
  sum(rows.speeches_count) / length(rows) as ActivityScore
FROM "politicians/deputies"
WHERE party != null
GROUP BY party
SORT ActivityScore DESC
```

## Cross-Party Committee Members

```dataview
TABLE WITHOUT ID
  file.link as Deputy,
  party,
  committees[0].name as Committee,
  committees[0].position as Role
FROM "politicians/deputies"
WHERE committees
WHERE committees[0].name = "Juridice"
SORT party
```

## Law Initiators by Party

```dataview
TABLE party,
  length(rows) as LawsProposed,
  sum(rows.laws_proposed) as Total
FROM "politicians/deputies"
WHERE laws_proposed > 0
GROUP BY party
SORT Total DESC
```

## Minority/Independent MPs

```dataview
LIST
FROM "politicians/deputies"
WHERE party = "MIN" OR party = "Independent"
```

## New MPs (First Legislature)

```dataview
LIST
FROM "politicians/deputies"
WHERE legislature = "2024-2028"
WHERE speeches_count < 5
```