# Session Recall Query

> Show complete information about a specific parliamentary session

## Usage

Replace `SESSION_DATE` with the actual session date (e.g., "2025-03-26"):

```dataview
SESSION_DATE = "2025-03-26"  # Change this
```

## Full Profile Recall

```dataview
TABLE
  title as "Title",
  date as "Date",
  chamber as "Chamber",
  legislature as "Legislature",
  word_count as "Word Count"
FROM "sessions"
WHERE date = SESSION_DATE
```

## Sensory Input

```dataview
TABLE
  source_url as "Source URL",
  last_synced as "Last Synced",
  duration_minutes as "Duration (min)",
  attendance_count as "Attendance"
FROM "sessions"
WHERE date = SESSION_DATE
```

## Processing

```dataview
TABLE
  topics_discussed as "Topics",
  sentiment as "Sentiment",
  speakers_identified as "Speakers"
FROM "sessions"
WHERE date = SESSION_DATE
```

## Memory - Participants

```dataview
LIST
FROM "sessions"
WHERE date = SESSION_DATE
FLATTEN participants
```

## Memory - Laws Discussed

```dataview
LIST
FROM "sessions"
WHERE date = SESSION_DATE
FLATTEN laws_discussed
```

## Memory - Key Votes

```dataview
TABLE
  "Law" as "Law Discussed",
  "Votes For" as "For",
  "Votes Against" as "Against"
FROM "sessions"
WHERE date = SESSION_DATE
```

## Action/Output - Query Ready

```dataview
FROM "sessions"
WHERE date = SESSION_DATE
```

## Reverse Links - Who Attended

```dataview
LIST
FROM "politicians"
WHERE contains(sessions, SESSION_DATE)
```

---

## Example: Find Recent Sessions

```dataview
LIST
FROM "sessions"
WHERE date >= "2025-01-01"
SORT date DESC
LIMIT 10
```

## Example: Find Sessions by Chamber

```dataview
LIST
FROM "sessions"
WHERE chamber = "senate"
LIMIT 10
```