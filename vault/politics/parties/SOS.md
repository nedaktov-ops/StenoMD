---
tags:
- party
party_name: SOS
---

# Party: SOS

## Overview

| Metric | Value |
|--------|-------|
| Members | 27 |
| Total Activity Score | 1004 |
| Total Speeches | 595 |
| Total Laws Proposed | 788 |

## Chamber Breakdown

| Chamber | Members |
|---------|---------|
| Chamber of Deputies | 20 |
| Senate | 7 |

## Top Members by Activity

| Deputy | Activity | Speeches | Laws |
|--------|----------|---------|------|
| [[politicians/deputies/Verginia VEDINAŞ]] | 125 | 61 | 64 |
| [[politicians/deputies/Andra-Claudia CONSTANTINESCU]] | 88 | 4 | 84 |
| [[politicians/deputies/Andrei-Cosmin GUŞĂ]] | 79 | 4 | 75 |
| [[politicians/deputies/Mădălin-Laurenţiu FĂGET]] | 68 | 17 | 51 |
| [[politicians/deputies/Sorin-George OLTENAŞU]] | 60 | 11 | 49 |
| [[politicians/deputies/Tudor IONESCU]] | 59 | 34 | 25 |
| [[politicians/deputies/Andreea-Petronela CÎMPIANU]] | 55 | 6 | 49 |
| [[politicians/deputies/Ştefan-Alexandru BĂIŞANU]] | 53 | 2 | 51 |
| [[politicians/deputies/Ana-Marcela BAŞ]] | 52 | 6 | 46 |
| [[politicians/deputies/Mariana VÂRGĂ]] | 50 | 19 | 31 |
| [[politicians/deputies/Cosmin ANDREI]] | 43 | 3 | 40 |
| [[politicians/deputies/Nini-Alexandru PASCALINI]] | 43 | 20 | 23 |
| [[politicians/deputies/Elena-Laura TOADER]] | 39 | 3 | 36 |
| [[politicians/deputies/Florin CARAGAŢĂ]] | 36 | 4 | 32 |
| [[politicians/deputies/Simona-Elena MACOVEI ILIE]] | 33 | 4 | 29 |

## Dataview Query

```dataview
TABLE party, activity_score, speeches_count, laws_proposed
FROM "vault/politicians"
WHERE party = "SOS"
SORT activity_score DESC
```
