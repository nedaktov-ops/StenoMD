---
tags:
- dashboard
- leaderboard
---

# Activity Leaderboard

## Top Deputies by Activity Score

```dataview
TABLE ai_friendly_name, party, constituency, activity_score, speeches_count, laws_proposed
FROM "vault/politicians/deputies"
SORT activity_score DESC
LIMIT 25
```

## Top Senators by Activity Score

```dataview
TABLE ai_friendly_name, party, constituency, activity_score, speeches_count
FROM "vault/politicians/senators"
SORT activity_score DESC
LIMIT 25
```

## Party Activity Rankings

| Party | Total Activity | Members |
|-------|---------------|---------|
| PSD | 3664 | 115 |
| PNL | 2269 | 72 |
| AUR | 2377 | 81 |
| USR | 1970 | 57 |
| UDMR | 1041 | 32 |
| SOS | 1004 | 27 |
| POT | 756 | 28 |
| MIN | 428 | 15 |
