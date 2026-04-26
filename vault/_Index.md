---
title: Vault Link Index
type: index
description: Overview of all linked entities in the StenoMD vault
---

# Vault Link Index

This index shows how all items in the vault are interconnected.

## Entity Counts

| Category | Count | Links |
|----------|------|------|
| [[politicians/deputies\|Deputies]] | 332 | 7,473 |
| [[politicians/senators\|Senators]] | 138 | 419 |
| [[laws\|Laws]] | 124 | 387 |
| [[sessions\|Sessions]] | 111 | 2,542 |
| [[committees\|Committees]] | - | - |

## Link Types

### Politicians → Proposals
- Deputies linked to their legislative proposals via `## Proposals` section
- 331 deputies have proposal links

### Politicians → Committees
- Linked via `## Committees` section
- 275 deputies have committee links

### Politicians → Sessions
- Appearances in parliamentary sessions tracked

### Politicians → Categories
- `## Categories` section with links to:
  - Party pages (`politicians/parties/PSD`, etc.)
  - Constituency pages (`politicians/constituencies/BUCUREŞTI`, etc.)

## Top Referenced Entities

1. proposals/22345 - 85 references
2. proposals/22277 - 77 references  
3. politicians/parties/PSD - 76 references
4. proposals/21209 - 74 references
5. politicians/parties/PNL - varies

## Query Examples

```dataview
# deputies with most proposals
LIST WHERE type = "deputy" 
SORT laws_proposed DESC
LIMIT 20

# politicians by party
LIST FROM "politicians"
WHERE party = "PSD"

# sessions with most appearances
LIST FROM "sessions"
SORT length(file.inlinks) DESC
```

## Categories

- [[politicians/deputies|Deputies]] - All 332 deputies
- [[politicians/senators|Senators]] - All 138 senators
- [[politicians/parties|Political Parties]] - PSD, PNL, USR, AUR, UDMR
- [[politicians/constituencies|Constituencies]] - By electoral district
- [[laws|Laws]] - Legislative proposals and laws
- [[sessions|Parliamentary Sessions]] - Chamber and Senate sessions
- [[committees|Parliamentary Committees]] - Standing committees