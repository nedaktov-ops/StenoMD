---
tags:
- dashboard
- comparison
---

# Party Comparison

## Members by Party

```dataview
TABLE party, count(party) as members
FROM "vault/politicians/deputies"
GROUP BY party
```
