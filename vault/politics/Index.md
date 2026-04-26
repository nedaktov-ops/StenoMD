---
tags:
- dashboard
- overview
---

# Political Overview

## Parliament Summary (2024-2028 Legislature)

| Category | Count |
|----------|-------|
| Chamber of Deputies | 332 |
| Senate | 137 |
| Total MPs | 469 |
| Sessions | 61 |
| Laws | 124 |
| Parties | 8 |
| Constituencies | 63 |

## Quick Links

- [[politicians/deputies|Deputies]] - Browse all deputies
- [[politicians/senators|Senators]] - Browse all senators
- [[vault/sessions|Sessions]] - Browse all parliamentary sessions
- [[laws|Laws]] - Browse all laws
- [[committees|Committees]] - Browse committees
- [[vault/politics/parties|Political Parties]] - Browse parties
- [[vault/politics/constituencies|Constituencies]] - Browse constituencies

## Party Activity

- [[vault/politics/parties/AUR|AUR]]: 81 members, 2377 total activity
- [[vault/politics/parties/MIN|MIN]]: 15 members, 428 total activity
- [[vault/politics/parties/PNL|PNL]]: 72 members, 2269 total activity
- [[vault/politics/parties/POT|POT]]: 28 members, 756 total activity
- [[vault/politics/parties/PSD|PSD]]: 115 members, 3664 total activity
- [[vault/politics/parties/SOS|SOS]]: 27 members, 1004 total activity
- [[vault/politics/parties/UDMR|UDMR]]: 32 members, 1041 total activity
- [[vault/politics/parties/USR|USR]]: 57 members, 1970 total activity

## Dataview Queries

### Top Active Deputies
```dataview
TABLE party, constituency, activity_score
FROM "vault/politicians/deputies"
SORT activity_score DESC
LIMIT 20
```

### Recent Sessions
```dataview
TABLE date, speech_count, deputy_count
FROM "vault/sessions"
SORT date DESC
LIMIT 10
```

### Active Laws
```dataview
TABLE law_number, title_short, status
FROM "vault/laws"
LIMIT 20
```
