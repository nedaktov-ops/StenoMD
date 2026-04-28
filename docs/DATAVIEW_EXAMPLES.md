# Dataview Query Examples

This collection provides ready-to-use Dataview queries for common insights in StenoMD.

All queries assume you are inside the Obsidian vault and have the Dataview plugin enabled.

---

## Contents

- [Politicians](#politicians)
- [Sessions](#sessions)
- [Laws](#laws)
- [Committees](#committees)
- [Brain Dashboard](#brain-dashboard)
- [Search Tips](#search-tips)

---

## Politicians

### Top 10 Deputies by Speeches Count

```dataview
TABLE speeches_count, party, constituency
FROM #deputy
WHERE speeches_count > 0
SORT speeches_count DESC
LIMIT 10
```

### Senators with Highest Laws Proposed

```dataview
TABLE laws_proposed, party
FROM #senator
WHERE laws_proposed > 0
SORT laws_proposed DESC
LIMIT 10
```

### All Deputies in a Given Party

```dataview
TABLE name, speeches_count, laws_proposed, constituency
FROM #deputy
WHERE party = "PSD"
SORT name ASC
```

### Deputies with Missing Committee Assignments

```dataview
TABLE name, party
FROM #deputy
WHERE committees = null OR len(committees) = 0
```

### Politicians Who Changed Parties (Traseism)

If `party_history` field is present:

```dataview
TABLE name, current_party, party_history
FROM #deputy OR #senator
WHERE len(party_history) > 1
```

---

## Sessions

### Recent Sessions (Last 7 Days)

```dataview
TABLE file.day as Date, chamber, participants, statements_count
FROM #session
WHERE file.day >= this weeks - 7
SORT file.day DESC
```

### Sessions with Most Participants

```dataview
TABLE file.day as Date, chamber, deputy_count
FROM #session
WHERE deputy_count > 0
SORT deputy_count DESC
LIMIT 10
```

### Sessions Discussing a Specific Law

```dataview
TABLE file.day as Date, chamber, statements_count
FROM #session
WHERE contains(laws_discussed, "20/2024")
```

### Sessions Attended by a Specific MP

Assuming `participants` list:

```dataview
TABLE file.day as Date, chamber
FROM #session
WHERE contains(participants, "Mihai Tudose")
SORT file.day DESC
```

---

## Laws

### Laws by Status

```dataview
TABLE title, date, sponsors
FROM #law
WHERE status = "adoptată"
SORT date DESC
```

### Most Sponsored Laws

```dataview
TABLE number, title, sponsors
FROM #law
WHERE len(sponsors) > 0
SORT len(sponsors) DESC
LIMIT 10
```

### Laws with Missing Sponsors

```dataview
TABLE number, title
FROM #law
WHERE sponsors = null OR len(sponsors) = 0
```

---

## Committees

### Committee Membership Count

```dataview
TABLE name AS Committee, len(members) AS MemberCount
FROM #committee
SORT len(members) DESC
```

### Deputies Serving on Multiple Committees

```dataview
TABLE name, len(committees) AS CommitteeCount
FROM #deputy
WHERE committees != null
SORT len(committees) DESC
LIMIT 10
```

---

## Brain Dashboard

### Activity Score Distribution

```dataview
TABLE name, brain.activity_score AS Score
FROM #deputy OR #senator
WHERE brain.activity_score > 0
SORT brain.activity_score DESC
LIMIT 15
```

### Top Collaborators (from collaboration_network)

If `brain.collaboration_network` is a list of frequently co-occurring names:

```dataview
TABLE name, len(brain.collaboration_network) AS CollaborationSize
FROM #deputy OR #senator
WHERE len(brain.collaboration_network) > 0
SORT len(brain.collaboration_network) DESC
LIMIT 10
```

---

## Search Tips

- Use `#tag` to filter by note type (e.g., `#deputy`, `#session`).
- Field names are case-sensitive as defined in frontmatter.
- `contains(list, value)` checks membership in YAML arrays.
- `file.day` extracts date from filename if frontmatter `date` is absent.
- Combine filters with `AND`/`OR`:

  ```dataview
  FROM #deputy
  WHERE party = "PSD" AND speeches_count > 20
  ```

- For full-text search over note content, use `dv.pages().where(p => p.file.name.includes("tudose"))`.

---

## Dynamic Queries with Parameters

You can use `$= dv.current()` to get dynamic results. Example: "Deputies with activity score above the average":

```dataview
TABLE name, brain.activity_score AS Score
FROM #deputy
WHERE brain.activity_score > avg(#deputy.brain.activity_score)
SORT Score DESC
```

---

## Troubleshooting

If a query returns no results:

- Check field names and case (use exact names from frontmatter).
- Ensure files have the expected tags (`#deputy`, `#session`, etc.).
- Verify that the fields are not null or empty.
- Use the Dataview developer console (`Ctrl+Shift+I`) to see parsing errors.

Explore existing queries in `vault/_brain/` for live examples.
