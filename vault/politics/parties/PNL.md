---
tags:
- party
party_name: PNL
---

# Party: PNL

## Overview

| Metric | Value |
|--------|-------|
| Members | 72 |
| Total Activity Score | 2269 |
| Total Speeches | 1152 |
| Total Laws Proposed | 1549 |

## Chamber Breakdown

| Chamber | Members |
|---------|---------|
| Chamber of Deputies | 45 |
| Senate | 27 |

## Top Members by Activity

| Deputy | Activity | Speeches | Laws |
|--------|----------|---------|------|
| [[politicians/deputies/Raluca TURCAN]] | 326 | 304 | 22 |
| [[politicians/deputies/Gabriel ANDRONACHE]] | 173 | 65 | 108 |
| [[politicians/deputies/Adrian-Felician COZMAvicepreşedinte al Camerei Deputaţilor]] | 122 | 58 | 64 |
| [[politicians/deputies/Adrian-Virgil CIOBANU]] | 101 | 3 | 98 |
| [[politicians/deputies/George SCARLAT]] | 76 | 3 | 73 |
| [[politicians/deputies/Răzvan-Olimpiu CADAR]] | 76 | 4 | 72 |
| [[politicians/deputies/Lucian Nicolae BODE]] | 75 | 23 | 52 |
| [[politicians/deputies/Florin-Claudiu ROMAN]] | 69 | 26 | 43 |
| [[politicians/deputies/Ilie-Aurelian COTINESCU]] | 67 | 8 | 59 |
| [[politicians/deputies/Dragoş-Fănică CIOBOTARU]] | 61 | 6 | 55 |
| [[politicians/deputies/Călin-Graţian GAL]] | 60 | 8 | 52 |
| [[politicians/deputies/Marian CRUŞOVEANU]] | 57 | 2 | 55 |
| [[politicians/deputies/Andrei Daniel GHEORGHE]] | 57 | 33 | 24 |
| [[politicians/deputies/Alina-Ştefania GORGHIU]] | 54 | 14 | 40 |
| [[politicians/deputies/Patricia-Simina-Arina MOŞsecretar al Camerei Deputaţilor]] | 54 | 23 | 31 |

## Dataview Query

```dataview
TABLE party, activity_score, speeches_count, laws_proposed
FROM "vault/politicians"
WHERE party = "PNL"
SORT activity_score DESC
```
