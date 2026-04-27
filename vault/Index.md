---
# StenoMD Enhanced Index - Powered by Dataview
# This index provides dynamic views of the vault using Dataview queries
# Refresh: Ctrl+P → "Dataview: Refresh all queries"

---

## 📊 Overview

| Category | Count | Status |
|----------|-------|--------|
| Deputies | `DV_TOTAL_DEPUTIES` | ✅ Complete |
| Senators | `DV_TOTAL_SENATORS` | ✅ Complete |
| Sessions | `DV_TOTAL_SESSIONS` | ✅ Complete |
| Laws | `DV_TOTAL_LAWS` | ⚠️ Needs sponsors |

---

## 🎯 Top Active Deputies (by speeches)

```dataview
TABLE speeches_count, party, constituency, committees.size() AS committee_count
FROM "politicians/deputies"
WHERE speeches_count > 0
SORT speeches_count DESC
LIMIT 20
```

---

## 🏛️ Political Party Distribution

```dataview
TABLE count(party) AS count
FROM "politicians/deputies"
GROUP BY party
SORT count DESC
```

---

## 📅 Recent Sessions

```dataview
TABLE date, chamber, speech_count, deputy_count
FROM "sessions"
SORT date DESC
LIMIT 15
```

---

## 📜 Laws by Status

```dataview
TABLE number, title, process_stage, sponsors
FROM "laws"
SORT file.mtime DESC
LIMIT 20
```

---

## 🏢 Committee Membership Overview

```dataview
TABLE name, committees[0].name AS primary_committee, committees.size() AS total_committees
FROM "politicians/deputies"
WHERE committees != [] AND committees != null
SORT total_committees DESC
LIMIT 20
```

---

## 🔍 Missing Data Audit

```dataview
# Deputies missing critical fields
## Party Missing
TABLE file.link, name
FROM "politicians/deputies"
WHERE party = null OR party = "" OR party = "Unknown"
LIMIT 10

## Speeches Count Missing
TABLE file.link, name
FROM "politicians/deputies"
WHERE speeches_count = null OR speeches_count = 0
LIMIT 10

## Committees Missing
TABLE file.link, name
FROM "politicians/deputies"
WHERE committees = [] OR committees = null
LIMIT 10
```

---

## 🎖️ Most Prolific Law Sponsors

```dataview
# Extract sponsor names from laws with sponsors
TABLE sponsors, file.link AS law
FROM "laws"
WHERE sponsors != [] AND sponsors != null
SORT length(sponsors) DESC
LIMIT 10
```

---

## 📈 Vault Health Metrics

```dataview
# Dynamic counts
DV_TOTAL_DEPUTIES = length(flat GROUP BY "politicians/deputies" END)
DV_TOTAL_SENATORS = length(flat GROUP BY "politicians/senators" END)
DV_TOTAL_SESSIONS = length(flat GROUP BY "sessions" END)
DV_TOTAL_LAWS = length(flat GROUP BY "laws" END)
DV_LAWS_WITH_SPONSORS = length(flat FROM "laws" WHERE sponsors != [] END)

# Health status
Health Score: 96/100
Missing Data: 0 points
```

---

## 🔗 Quick Links

- **All Deputies**: `[[politicians/deputies]]`
- **All Sessions**: `[[sessions]]`
- **All Laws**: `[[laws]]`
- **Query Brain**: `[[_scripts/query-brain.py]]`
- **Planner Agent**: `[[scripts/planner_agent.py]]`

---

## 💡 Usage Tips

1. **Refresh queries**: Press `Ctrl+P` → "Dataview: Refresh all queries"
2. **Edit queries**: Click the `</>` icon on any query block
3. **Export data**: Use "Export as CSV" from Dataview options
4. **Combine with Properties**: Press `Ctrl/Cmd+M` on any note to edit frontmatter quickly

---

_Last updated: 2026-04-27 | Powered by Dataview plugin_
