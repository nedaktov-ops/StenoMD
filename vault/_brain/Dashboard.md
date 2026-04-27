---
title: StenoMD Dashboard
tags: [dashboard, dataview]
---

# 📈 StenoMD Daily Dashboard

Last updated: `= date`

---

## Today's Snapshot

| Metric | Value |
|--------|-------|
| Total Deputies | `= length(flat GROUP BY "politicians/deputies" END)` |
| Total Senators | `= length(flat GROUP BY "politicians/senators" END)` |
| Sessions (2024-2025) | `= length(flat GROUP BY "sessions" END)` |
| Laws Tracked | `= length(flat GROUP BY "laws" END)` |
| Health Score | **96/100** |

---

## 🏆 Top 10 Most Active Deputies (by speeches)

```dataview
TABLE speeches_count, party, constituency
FROM "politicians/deputies"
WHERE speeches_count > 0
SORT speeches_count DESC
LIMIT 10
```

---

## 📅 Recent Sessions (Last 10)

```dataview
TABLE date, chamber, speech_count, deputy_count
FROM "sessions"
SORT date DESC
LIMIT 10
```

---

## 🏛️ Party Distribution (Deputies)

```dataview
PIE chart
  show "party"
  WHERE party != ""
  FROM "politicians/deputies"
  LIMIT 20
```

---

## 📜 Laws Needing Attention

```dataview
TABLE number, title, process_stage, sponsors
FROM "laws"
WHERE sponsors = [] OR sponsors = null
LIMIT 15
```

---

## ❗ Missing Committee Assignments

```dataview
TABLE name, party, constituency
FROM "politicians/deputies"
WHERE committees = [] OR committees = null
SORT name ASC
LIMIT 20
```

---

## 🕸️ Graphify Knowledge Graph

| Metric | Value |
|--------|-------|
| Total Graph Nodes | 2,246 |
| Total Edges | 1,101 |
| Communities Detected | 1,455 |
| Orphan Nodes | 1,449 |
| Graph File | `Graphify/graphify-out/graph.json` |
| Interactive Viz | `Graphify/graphify-out/graph.html` |
| Community Overview | `Graphify/graphify-out/communities.html` |
| Top Hubs JSON | `Graphify/graphify-out/hub-nodes.json` |
| Analysis Report | `vault/_brain/PHASE2_REPORT.md` |

*Last graph rebuild: 2026-04-27*

---

## 🎯 Quick Actions

- [[_brain/DATAVIEW_TESTS|Test Dataview Queries]]
- [[projects/legislative-tracker|Legislative Kanban]]
- [[_parliament/diagrams/parliament-structure-excalidraw|Parliament Structure]]
- [[_brain/query-brain|Query Knowledge Graph]]
- [[Unfinished-tasks.md|Task List]]

---

## 💡 Today's Insight

```dataview
# Random active deputy to explore
TABLE stable_id, party, speeches_count, committees.size() AS committee_count
FROM "politicians/deputies"
WHERE speeches_count > 0
SORT rand() DESC
LIMIT 1
```

---

**Refresh all queries:** `Ctrl+P` → "Dataview: Refresh all queries"
