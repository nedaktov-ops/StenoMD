---
tags:
- party
party_name: PSD
---

# Party: PSD

## Overview

| Metric | Value |
|--------|-------|
| Members | 115 |
| Total Activity Score | 3664 |
| Total Speeches | 1839 |
| Total Laws Proposed | 2487 |

## Chamber Breakdown

| Chamber | Members |
|---------|---------|
| Chamber of Deputies | 77 |
| Senate | 38 |

## Top Members by Activity

| Deputy | Activity | Speeches | Laws |
|--------|----------|---------|------|
| [[politicians/deputies/Vasile-Daniel SUCIU]] | 501 | 489 | 12 |
| [[politicians/deputies/Ciprian-Constantin ŞERBAN]] | 194 | 149 | 45 |
| [[politicians/deputies/Natalia-Elena INTOTEROvicepreşedinte al Camerei Deputaţilor]] | 149 | 108 | 41 |
| [[politicians/deputies/Sorin-Mihai GRINDEANUPreşedintele Camerei Deputaţilor]] | 108 | 33 | 75 |
| [[politicians/deputies/Petru-Bogdan COJOCARU]] | 95 | 12 | 83 |
| [[politicians/deputies/Adrian CÂCIU]] | 87 | 46 | 41 |
| [[politicians/deputies/Augustin-Florin HAGIU]] | 86 | 3 | 83 |
| [[politicians/deputies/Liviu-Bogdan CIUCĂ]] | 80 | 35 | 45 |
| [[politicians/deputies/Simona BUCURA-OPRESCUchestor al Camerei Deputaţilor]] | 67 | 1 | 66 |
| [[politicians/deputies/Alexandru-Mihai GHIGIU]] | 67 | 13 | 54 |
| [[politicians/deputies/Silvia-Claudia MIHALCEAsecretar al Camerei Deputaţilor]] | 66 | 17 | 49 |
| [[politicians/deputies/Sergiu-Mircea CONSTANTINESCU]] | 66 | 2 | 64 |
| [[politicians/deputies/Ştefan-Ovidiu POPA]] | 66 | 28 | 38 |
| [[politicians/deputies/Dumitriţa GLIGA]] | 65 | 2 | 63 |
| [[politicians/deputies/Florin-Ionuţ BARBU]] | 63 | 1 | 62 |

## Dataview Query

```dataview
TABLE party, activity_score, speeches_count, laws_proposed
FROM "vault/politicians"
WHERE party = "PSD"
SORT activity_score DESC
```
