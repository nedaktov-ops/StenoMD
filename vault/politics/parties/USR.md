---
tags:
- party
party_name: USR
---

# Party: USR

## Overview

| Metric | Value |
|--------|-------|
| Members | 57 |
| Total Activity Score | 1970 |
| Total Speeches | 1204 |
| Total Laws Proposed | 1386 |

## Chamber Breakdown

| Chamber | Members |
|---------|---------|
| Chamber of Deputies | 37 |
| Senate | 20 |

## Top Members by Activity

| Deputy | Activity | Speeches | Laws |
|--------|----------|---------|------|
| [[politicians/deputies/Cătălin DRULĂvicepreşedinte al Camerei Deputaţilor]] | 235 | 182 | 53 |
| [[politicians/deputies/Alexandru-Paul DIMITRIU]] | 109 | 50 | 59 |
| [[politicians/deputies/Andrei-Florin GHEORGHIU]] | 99 | 6 | 93 |
| [[politicians/deputies/Brian CRISTIAN]] | 88 | 29 | 59 |
| [[politicians/deputies/Marius-Nicolae ALECSANDRU]] | 80 | 9 | 71 |
| [[politicians/deputies/Ştefan TANASĂ]] | 68 | 5 | 63 |
| [[politicians/deputies/Dumitru VĂDUVA]] | 64 | 1 | 63 |
| [[politicians/deputies/Alin-Bogdan STOICA]] | 63 | 12 | 51 |
| [[politicians/deputies/Allen COLIBAN]] | 62 | 19 | 43 |
| [[politicians/deputies/Mihai-Cătălin BOTEZ]] | 62 | 9 | 53 |
| [[politicians/deputies/Diana-Anda BUZOIANU]] | 60 | 19 | 41 |
| [[politicians/deputies/George GIMA]] | 58 | 7 | 51 |
| [[politicians/deputies/Diana STOICA]] | 58 | 17 | 41 |
| [[politicians/deputies/Emanuel-Dumitru UNGUREANU]] | 58 | 26 | 32 |
| [[politicians/deputies/Adrian GIURGIU]] | 56 | 4 | 52 |

## Dataview Query

```dataview
TABLE party, activity_score, speeches_count, laws_proposed
FROM "vault/politicians"
WHERE party = "USR"
SORT activity_score DESC
```
