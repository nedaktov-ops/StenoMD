---
tags:
- party
party_name: AUR
---

# Party: AUR

## Overview

| Metric | Value |
|--------|-------|
| Members | 81 |
| Total Activity Score | 2377 |
| Total Speeches | 1559 |
| Total Laws Proposed | 1714 |

## Chamber Breakdown

| Chamber | Members |
|---------|---------|
| Chamber of Deputies | 53 |
| Senate | 28 |

## Top Members by Activity

| Deputy | Activity | Speeches | Laws |
|--------|----------|---------|------|
| [[politicians/deputies/Gianina ŞERBANvicepreşedinte al Camerei Deputaţilor]] | 211 | 179 | 32 |
| [[politicians/deputies/Nelu-Valentin BADEA]] | 108 | 2 | 106 |
| [[politicians/deputies/Mihai-Adrian ENACHE]] | 99 | 36 | 63 |
| [[politicians/deputies/Cristina-Emanuela DASCĂLU]] | 87 | 15 | 72 |
| [[politicians/deputies/Ilie-Alin COLEŞA]] | 86 | 45 | 41 |
| [[politicians/deputies/Ariadna-Elena CÎRLIGEANU]] | 77 | 7 | 70 |
| [[politicians/deputies/Daniel-Răzvan BIRO]] | 73 | 7 | 66 |
| [[politicians/deputies/Cristina-Irina BUTURĂ]] | 70 | 7 | 63 |
| [[politicians/deputies/Ştefăniţă-Alin AVRĂMESCU]] | 69 | 4 | 65 |
| [[politicians/deputies/George BECALI]] | 63 | 1 | 62 |
| [[politicians/deputies/Florin-Eugen CÎRLIGEA]] | 62 | 1 | 61 |
| [[politicians/deputies/Sorin-Titus MUNCACIU]] | 60 | 31 | 29 |
| [[politicians/deputies/Daniel-Cătălin CIORNEI]] | 59 | 12 | 47 |
| [[politicians/deputies/Silviu-Octavian GURLUI]] | 57 | 17 | 40 |
| [[politicians/deputies/Cosmin-Ioan CORENDEA]] | 57 | 19 | 38 |

## Dataview Query

```dataview
TABLE party, activity_score, speeches_count, laws_proposed
FROM "vault/politicians"
WHERE party = "AUR"
SORT activity_score DESC
```
