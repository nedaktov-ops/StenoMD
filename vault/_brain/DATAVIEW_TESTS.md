# Dataview Test Queries

**Purpose:** Verify Dataview plugin is working correctly with StenoMD data.

**Instructions:** Run each query in a code block with `dataview` language. Check for errors and verify results match expected output.

---

## Deputy Tests

### Test 1: Basic Deputy List

```dataview
LIST FROM "politicians/deputies" LIMIT 10
```

**Expected:** List of 10 deputy file links.
**Actual:** _____________________

---

### Test 2: Table with Frontmatter Fields

```dataview
TABLE stable_id, party, constituency, speeches_count, committees
FROM "politicians/deputies"
LIMIT 10
```

**Expected:** Table showing fields, no errors.
**Actual:** _____________________

---

### Test 3: Filter by Party

```dataview
LIST FROM "politicians/deputies"
WHERE party = "PSD"
SORT name ASC
LIMIT 10
```

**Expected:** 10 PSD deputies.
**Actual:** _____________________

---

### Test 4: Party Distribution

```dataview
TABLE party, count(party) AS count
FROM "politicians/deputies"
GROUP BY party
SORT count DESC
```

**Expected:** Party distribution table with counts.
**Actual:** _____________________

---

### Test 5: Deputies with Committee Assignments

```dataview
TABLE name, committees
FROM "politicians/deputies"
WHERE committees != [] AND committees != null
LIMIT 10
```

**Expected:** Deputies with committee assignments.
**Actual:** _____________________

---

### Test 6: Edge Case - Missing Stable ID

```dataview
TABLE name, stable_id
FROM "politicians/deputies"
WHERE stable_id = null OR stable_id = ""
```

**Expected:** List of deputies missing stable_id (should be empty or minimal).
**Actual:** _____________________
**Note:** All deputies should have stable_id for unique identification.

---

### Test 7: Edge Case - Special Characters in Names

```dataview
LIST FROM "politicians/deputies"
WHERE contains(name, "-") OR contains(name, "Ă") OR contains(name, "Ș")
SORT name ASC
LIMIT 10
```

**Expected:** Deputies with diacritics or hyphens in names.
**Actual:** _____________________
**Note:** Verify names display correctly in Obsidian.

---

## Session Tests

### Test 8: Recent Sessions

```dataview
LIST FROM "sessions"
SORT date DESC
LIMIT 5
```

**Expected:** Most recent 5 sessions.
**Actual:** _____________________

---

### Test 9: Session Count by Chamber

```dataview
TABLE chamber, count(chamber) AS count
FROM "sessions"
GROUP BY chamber
```

**Expected:** Distribution of sessions by chamber (deputies/senate/joint).
**Actual:** _____________________

---

### Test 10: Sessions with Attendance Data

```dataview
TABLE date, chamber, attendance_count, duration_minutes
FROM "sessions"
WHERE attendance_count > 0
SORT date DESC
LIMIT 10
```

**Expected:** Sessions with attendance and duration data.
**Actual:** _____________________

---

### Test 11: Edge Case - Missing Date

```dataview
TABLE file.name, date
FROM "sessions"
WHERE date = null OR date = ""
```

**Expected:** Sessions missing date (should be none).
**Actual:** _____________________

---

## Law Tests

### Test 12: Laws by Status

```dataview
TABLE status, count(status) AS count
FROM "laws"
GROUP BY status
SORT count DESC
```

**Expected:** Distribution of laws by status (proposed, passed, rejected, etc.)
**Actual:** _____________________

---

### Test 13: Laws with Sponsors

```dataview
TABLE proposal_number, title, sponsors
FROM "laws"
WHERE sponsors != [] AND sponsors != null
LIMIT 10
```

**Expected:** Laws with sponsor data.
**Actual:** _____________________

---

### Test 14: Laws by Chamber

```dataview
TABLE chamber, count(chamber) AS count
FROM "laws"
GROUP BY chamber
```

**Expected:** Distribution of laws by originating chamber.
**Actual:** _____________________

---

### Test 15: Edge Case - Missing Proposal Number

```dataview
TABLE file.name, proposal_number
FROM "laws"
WHERE proposal_number = null OR proposal_number = ""
```

**Expected:** Laws missing proposal number (should be none).
**Actual:** _____________________

---

## Committee Tests

### Test 16: Committee List

```dataview
LIST FROM "committees"
SORT file.name ASC
```

**Expected:** List of all committees.
**Actual:** _____________________

---

### Test 17: Committee Details

```dataview
TABLE name, chamber, member_count, meeting_frequency
FROM "committees"
LIMIT 10
```

**Expected:** Committee metadata table.
**Actual:** _____________________

---

## Performance & Aggregation Tests

### Test 18: Deputy Activity Metrics

```dataview
TABLE avg(activity_score) AS avg_score, max(activity_score) AS max_score, min(activity_score) AS min_score
FROM "politicians/deputies"
```

**Expected:** Activity score statistics.
**Actual:** _____________________

---

### Test 19: Legislative Output by Legislature

```dataview
TABLE legislature, count(*) AS total_laws, avg(processing_time_days) AS avg_days
FROM "laws"
WHERE processing_time_days > 0
GROUP BY legislature
```

**Expected:** Law processing metrics by legislature.
**Actual:** _____________________

---

### Test 20: Top Parties by Deputy Count

```dataview
TABLE party, count(party) AS deputy_count
FROM "politicians/deputies"
GROUP BY party
SORT deputy_count DESC
LIMIT 5
```

**Expected:** Top 5 parties by deputy count.
**Actual:** _____________________

---

### Test 21: Monthly Session Volume

```dataview
TABLE dateformat(date, "YYYY-MM") AS month, count(*) AS sessions
FROM "sessions"
GROUP BY month
SORT month DESC
LIMIT 12
```

**Expected:** Session count per month for last year.
**Actual:** _____________________

---

## Health Metrics

**These queries produce numbers for the StenoMD Health Score dashboard.**

### Metric 1: Total Deputies

```dataview
COUNT FROM "politicians/deputies"
```

**Health Score input:** Total deputy count
**Expected:** > 0
**Actual:** _____________________

---

### Metric 2: Total Sessions

```dataview
COUNT FROM "sessions"
```

**Health Score input:** Total session count
**Expected:** > 0
**Actual:** _____________________

---

### Metric 3: Total Laws

```dataview
COUNT FROM "laws"
```

**Health Score input:** Total law count
**Expected:** > 0
**Actual:** _____________________

---

### Metric 4: Deputies with Complete Data

```dataview
COUNT FROM "politicians/deputies"
WHERE stable_id != null AND party != null AND constituency != null
```

**Health Score input:** Percentage of complete deputy records
**Expected:** > 90%
**Actual:** _____________________

---

### Metric 5: Sessions with Attendance

```dataview
COUNT FROM "sessions"
WHERE attendance_count > 0
```

**Health Score input:** Percentage of sessions with attendance data
**Expected:** > 80%
**Actual:** _____________________

---

### Metric 6: Recent Activity (Last 30 Days)

```dataview
COUNT FROM "sessions"
WHERE date >= date(now) - dur(30 days)
```

**Health Score input:** Recent session activity
**Expected:** > 0 (or "No sessions in last 30 days" is valid if vault is up-to-date)
**Actual:** _____________________

---

## Troubleshooting

If any test fails:

1. **Dataview plugin not enabled?** Settings → Core plugins → Dataview
2. **Restart Obsidian** - Sometimes plugin needs reload after installation
3. **Check console** - Ctrl+Shift+I (or Cmd+Shift+I on Mac) for errors
4. **Verify vault path** - Ensure vault root is correct in Obsidian
5. **Check YAML syntax** - Invalid frontmatter breaks Dataview queries
6. **File location** - Confirm files are in correct folders (politicians/deputies, sessions, laws, committees)
7. **Field names** - Dataview is case-sensitive; ensure field names match exactly

---

**Last tested:** 2026-04-27
**Vault version:** StenoMD v2.0
