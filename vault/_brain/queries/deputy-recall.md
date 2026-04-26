# Deputy Recall Query

> Show complete information about a specific deputy

## Usage

Replace `DEPUTY_NAME` with the actual deputy name, or use the query below with IDM:

```dataview
DEPUTY_IDM = "148"  # Change this IDM
```

## Full Profile Recall

```dataview
TABLE
  name as "Name",
  party as "Party",
  constituency as "Constituency",
  legislature as "Legislature",
  activity_score as "Activity Score"
FROM "politicians/deputies"
WHERE idm = DEPUTY_IDM
```

## Sensory Input

```dataview
TABLE
  source_url as "Source URL",
  last_synced as "Last Synced",
  data_sources as "Data Sources"
FROM "politicians/deputies"
WHERE idm = DEPUTY_IDM
```

## Processing

```dataview
TABLE
  collaboration_network as "Party Alignment",
  party as "Party"
FROM "politicians/deputies"
WHERE idm = DEPUTY_IDM
```

## Memory - Proposals

```dataview
LIST
FROM "proposals"
WHERE contains(sponsors, DEPUTY_IDM)
LIMIT 20
```

## Memory - Sessions Attended

```dataview
LIST
FROM "sessions/deputies"
WHERE contains(participants, "NAME_FROM_SESSIONS")
LIMIT 20
```

## Memory - Speeches

```dataview
LIST
FROM "sessions/deputies"
WHERE contains(speakers, "DEPUTY_NAME")
SORT date DESC
LIMIT 10
```

## Memory - Voting Record

```dataview
TABLE
  file.link as "Session",
  vote as "Vote",
  law as "Law"
FROM "sessions/deputies"
WHERE contains(voters, DEPUTY_IDM)
LIMIT 20
```

## Memory - Committees

```dataview
LIST
FROM ""
WHERE contains(committees, "COMMITTEE_NAME")
```

## Action/Output - Query Ready

```dataview
FROM "politicians/deputies"
WHERE idm = DEPUTY_IDM
```

## Reverse Links - What References This Deputy

```dataview
LIST
FROM ""
WHERE contains(file.inlinks, "DEPUTY_FILE")
```

---

## Example: Find Deputy by Name

```dataview
LIST
FROM "politicians/deputies"
WHERE contains(name, "Ion")
LIMIT 20
```