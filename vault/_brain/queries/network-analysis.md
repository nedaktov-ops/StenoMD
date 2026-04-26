# Enhanced Network Analysis Queries

> Advanced queries for brain network analysis

## Activity Overview

### Most Active Deputies by Proposals

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  party as "Party",
  laws_proposed as "Proposals",
  speeches_count as "Speeches"
FROM "politicians/deputies"
WHERE laws_proposed > 0
SORT laws_proposed DESC
LIMIT 25
```

### Most Active Speakers

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  party as "Party",
  speeches_count as "Speeches"
FROM "politicians/deputies"
WHERE speeches_count > 0
SORT speeches_count DESC
LIMIT 20
```

### Party Activity Comparison

```dataview
TABLE WITHOUT ID
  party as "Party",
  length(file) as "Members",
  sum(laws_proposed) as "Total Proposals",
  sum(speeches_count) as "Total Speeches"
FROM "politicians/deputies"
GROUP BY party
FLATTEN
SORT sum(laws_proposed) DESC
```

### Cross-Party Collaboration

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  collaboration_network as "Collaborates With"
FROM "politicians/deputies"
WHERE collaboration_network
LIMIT 20
```

## Session Analysis

### Session Participation

```dataview
TABLE WITHOUT ID
  file.link as "Session",
  date as "Date",
  participant_count as "Attendees"
FROM "sessions/deputies"
SORT date DESC
LIMIT 20
```

### Most Discussed Laws

```dataview
TABLE WITHOUT ID
  file.link as "Law",
  discussions as "Times Discussed"
FROM "laws"
WHERE discussions > 0
SORT discussions DESC
LIMIT 15
```

## Voting Patterns

### Deputy Voting Record

```dataview
TABLE
  deponent as "Deputy",
  COUNT as "Votes Cast"
FROM ""
FLATTEN voting_records
GROUP BY deponent
SORT COUNT DESC
LIMIT 25
```

### Unanimous Votes

```dataview
LIST
FROM "sessions/deputies"
WHERE unanimous = true
LIMIT 10
```

## Network Connections

### Shared committee Members

```dataview
LIST
FROM "politicians/deputies"
WHERE contains(committees, "COMMITTEE_NAME")
LIMIT 30
```

### Co-Sponsorship Network

```dataview
TABLE
  file.link as "Deputy",
  co_sponsors as "Co-Sponsors"
FROM "politicians"
WHERE co_sponsors
LIMIT 20
```

---

*Use these queries to analyze the complete parliamentary network.*