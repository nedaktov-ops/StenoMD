---
tags:
- dashboard
- recent
---

# Recent Parliamentary Activity

## Latest Sessions

```dataview
TABLE date, speech_count, deputy_count
FROM "vault/sessions"
SORT date DESC
LIMIT 15
```

## Most Recent Laws

```dataview
TABLE law_number, title_short, status
FROM "vault/laws"
LIMIT 15
```

## Recently Active Deputies

```dataview
TABLE ai_friendly_name, party, speeches_count, laws_proposed
FROM "vault/politicians/deputies"
WHERE speeches_count > 0
SORT speeches_count DESC
LIMIT 15
```
