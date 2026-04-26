---
tags:
- party
party_name: POT
---

# Party: POT

## Overview

| Metric | Value |
|--------|-------|
| Members | 28 |
| Total Activity Score | 756 |
| Total Speeches | 847 |
| Total Laws Proposed | 598 |

## Chamber Breakdown

| Chamber | Members |
|---------|---------|
| Chamber of Deputies | 21 |
| Senate | 7 |

## Top Members by Activity

| Deputy | Activity | Speeches | Laws |
|--------|----------|---------|------|
| [[politicians/deputies/Anamaria GAVRILĂ]] | 67 | 44 | 23 |
| [[politicians/deputies/Andrei CSILLAG]] | 65 | 1 | 64 |
| [[politicians/deputies/Aurora-Tasica SIMU]] | 63 | 20 | 43 |
| [[politicians/deputies/Lucian-Nicolae ANDRUŞCĂ]] | 53 | 9 | 44 |
| [[politicians/deputies/Cristian-Emanuel CÎMPAN]] | 50 | 10 | 40 |
| [[politicians/deputies/Dumitriţa ALBU]] | 49 | 14 | 35 |
| [[politicians/deputies/Codruţa-Maria CORCHEŞ]] | 46 | 7 | 39 |
| [[politicians/deputies/Gabriela PORUMBOIU]] | 42 | 15 | 27 |
| [[politicians/deputies/Răzvan-Mirel CHIRIŢĂ]] | 35 | 5 | 30 |
| [[politicians/deputies/Bianca-Eugenia GAVRILĂ]] | 32 | 2 | 30 |
| [[politicians/deputies/Gheorghe-Petru PÎCLIŞAN]] | 31 | 4 | 27 |
| [[politicians/deputies/Monica IONESCU]] | 29 | 4 | 25 |
| [[politicians/deputies/Sebastian-Andrei KRONCSIŞ]] | 28 | 2 | 26 |
| [[politicians/deputies/Andrei-Ionuţ TESLARIU]] | 27 | 1 | 26 |
| [[politicians/deputies/Călin-Florin GROZA]] | 26 | 1 | 25 |

## Dataview Query

```dataview
TABLE party, activity_score, speeches_count, laws_proposed
FROM "vault/politicians"
WHERE party = "POT"
SORT activity_score DESC
```
