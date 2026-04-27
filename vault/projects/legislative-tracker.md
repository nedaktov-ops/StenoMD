---
title: Legislative Process Tracker
tags: [kanban, laws, process]
kanban-plugin: board
---

# Legislative Process Tracking Board

## Proposed
Drag laws here when first created.

```kanban
## Proposed
BUILTIN
{{query FROM "laws" WHERE process_stage = "proposed" OR process_stage = null}}
```

## Committee Review
Laws under committee examination.

```kanban
## Committee
BUILTIN
{{query FROM "laws" WHERE process_stage = "in_committee"}}
```

## Chamber Debate
Laws debated in Chamber of Deputies.

```kanban
## Chamber
BUILTIN
{{query FROM "laws" WHERE process_stage = "in_chamber"}}
```

## Senate Review
Laws sent to Senate for approval.

```kanban
## Senate
BUILTIN
{{query FROM "laws" WHERE process_stage = "in_senate"}}
```

## Promulgated
Laws signed by President, awaiting publication in Monitorul Oficial.

```kanban
## Promulgated
BUILTIN
{{query FROM "laws" WHERE process_stage = "promulgated"}}
```

## In Force
Laws published in Monitorul Oficial and in effect.

```kanban
## In Force
BUILTIN
{{query FROM "laws" WHERE process_stage = "in_force"}}
```

---

## Usage Instructions

1. Create a new law note using QuickAdd or template
2. Set `process_stage` in frontmatter to one of:
   - `proposed` (default)
   - `in_committee`
   - `in_chamber`
   - `in_senate`
   - `promulgated`
   - `in_force`
   - `rejected`
3. The law card will automatically appear in the correct column
4. Drag to manually change status (updates frontmatter if configured)

**Tip:** Use the QuickAdd "New Law" script for fastest entry.

---

_This board auto-updates based on `process_stage` frontmatter field. Last refreshed: `system_date`_
