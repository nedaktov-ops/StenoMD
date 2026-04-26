---
title: Brain Dashboard
type: dashboard
description: StenoMD Vault Analytics - Brain-Analogous Architecture
last_updated: 2026-04-26
---

# 🧠 StenoMD Brain Dashboard

> Brain-analogous vault architecture with sensory input, processing, memory, and action/output

---

## Overview

| Category | Count | Links | Brain Section |
|----------|-------|------|--------------|
| [[politicians/deputies\|Deputies]] | 332 | 7,473 | Prefrontal Cortex |
| [[politicians/senators\|Senators]] | 138 | 419 | Limbic System |
| [[laws\|Laws]] | 124 | 387 | Hippocampus |
| [[sessions\|Sessions]] | 111 | 2,542 | Cortex |
| [[committees\|Committees]] | 14 | ~300 | Cerebellum |
| **Total** | **715** | **~11,000** | |

---

## Brain Model Reference

### 1. Sensory Input (Thalamus)
**Function:** Receives and routes information
- Source URLs tracked
- Last sync timestamps
- Data source attribution

### 2. Processing (Prefrontal Cortex)
**Function:** Analyzes, decides, computes
- Activity scores calculated
- Collaboration networks mapped
- Party alignment tracked

### 3. Memory (Hippocampus)
**Function:** Stores and retrieves information
- Proposals linked
- Speeches indexed
- Voting records accessible

### 4. Action/Output (Motor Cortex)
**Function:** Executes and responds
- Query-ready fields
- Alerts for activity
- Recommendations generated

---

## Activity Metrics

### Top Politicians by Activity

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  party as "Party",
  activity_score as "Score",
  committees as "Committees"
FROM "politicians/deputies"
WHERE activity_score > 0
SORT activity_score DESC
LIMIT 10
```

### Party Distribution

```dataview
TABLE WITHOUT ID
  party as "Party",
  length(file) as "Members",
  sum(atividade_score) as "Total Activity"
FROM "politicians"
GROUP BY party
SORT length(file) DESC
```

### Law Pipeline

```dataview
TABLE WITHOUT ID
  law_number as "Law",
  status as "Status",
  processing_time_days as "Days",
  bottleneck_stage as "Bottleneck"
FROM "laws"
SORT date_proposed DESC
LIMIT 20
```

---

## Memory Recall Functions

### Deputy Recall
```dataview
LIST
FROM "politicians"
WHERE contains(file.inlinks, [[ THIS FILE ]])
```

### Law Recall
```dataview
LIST
FROM "laws"
WHERE contains(file.inlinks, [[ THIS FILE ]])
```

### Session Recall
```dataview
LIST
FROM "sessions"
WHERE date = "2025-03-26"
```

---

## Connection Network

### Cross-Reference Query
```dataview
TABLE
  "Incoming Links" as "Referenced By",
  "Outgoing Links" as "Links To"
FROM ""
WHERE file = "politicians/deputies/name"
```

---

## Alerts

### Inactive Politicians
```dataview
LIST
FROM "politicians"
WHERE activity_score = 0
LIMIT 10
```

### Stalled Laws
```dataview
LIST
FROM "laws"
WHERE !contains(date_adopted, "202") OR !date_adopted
LIMIT 10
```

---

## Quick Links

- [[_brain/queries/deputy-recall|Deputy Recall Query]]
- [[_brain/queries/law-recall|Law Recall Query]]
- [[_brain/queries/session-recall|Session Recall Query]]
- [[_brain/queries/cross-reference|Cross-Reference Query]]

---

*Dashboard last updated: 2026-04-26*
*Vault version: Brain Architecture v1.0*