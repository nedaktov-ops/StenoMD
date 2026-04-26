# Bill and Legislation

> Queries for tracking bills through the legislative process

## Bills by Process Stage

```dataview
TABLE WITHOUT ID
  file.link as Bill,
  law_number,
  process_stage,
  length(sponsors) as Sponsors
FROM "laws"
WHERE process_stage != null
SORT process_stage
```

## Bills in Committee

```dataview
LIST
FROM "laws"
WHERE process_stage = "in_committee"
```

## Adopted Laws (This Legislature)

```dataview
LIST
FROM "laws"
WHERE process_stage = "adopted"
```

## Bills by Sponsor

```dataview
TABLE law_number, party, process_stage
FROM "laws"
WHERE contains(sponsors.party, "PSD")
```

## Most Active Sponsors

```dataview
TABLE party, length(rows) as Bills
FROM "laws"
WHERE sponsors
FLATTEN sponsors.party as party
GROUP BY party
SORT Bills DESC
```

## Bills Needing Action

```dataview
LIST
FROM "laws"
WHERE process_stage = "proposed"
WHERE date_proposed > "2025-01-01"
```