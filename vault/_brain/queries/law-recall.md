# Law Recall Query

> Show complete information about a specific law

## Usage

Replace `LAW_NUMBER` with the actual law number (e.g., "101/2026"):

```dataview
LAW_NUMBER = "101/2026"  # Change this
```

## Full Profile Recall

```dataview
TABLE
  law_number as "Number",
  title as "Title",
  status as "Status",
  chamber as "Chamber",
  year as "Year"
FROM "laws"
WHERE law_number = LAW_NUMBER
```

## Sensory Input

```dataview
TABLE
  source_url as "Source URL",
  last_synced as "Last Synced",
  submitted_date as "Submitted Date"
FROM "laws"
WHERE law_number = LAW_NUMBER
```

## Processing

```dataview
TABLE
  processing_time_days as "Processing Time",
  bottleneck_stage as "Bottleneck",
  current_stage as "Current Stage"
FROM "laws"
WHERE law_number = LAW_NUMBER
```

## Memory - Status History

```dataview
TABLE
  date_proposed as "Proposed",
  date_adopted as "Adopted"
FROM "laws"
WHERE law_number = LAW_NUMBER
```

## Memory - Sponsors

```dataview
LIST
FROM ""
WHERE contains(sponsors, "DEPUTY_NAME")
```

## Memory - Debates

```dataview
LIST
FROM "sessions"
WHERE contains(laws_discussed, LAW_NUMBER)
```

## Action/Output - Query Ready

```dataview
FROM "laws"
WHERE law_number = LAW_NUMBER
```

## Reverse Links - What References This Law

```dataview
LIST
FROM ""
WHERE contains(file.inlinks, "LAW_FILE")
```

---

## Example: Find Laws by Status

```dataview
LIST
FROM "laws"
WHERE status = "promulgated"
LIMIT 20
```

## Example: Find Laws by Year

```dataview
LIST
FROM "laws"
WHERE year = "2026"
LIMIT 20
```

## Example: Find Laws by Chamber

```dataview
LIST
FROM "laws"
WHERE chamber = "senate"
LIMIT 20
```