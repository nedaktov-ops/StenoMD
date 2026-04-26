---
tags:
- party
party_name: UDMR
---

# Party: UDMR

## Overview

| Metric | Value |
|--------|-------|
| Members | 32 |
| Total Activity Score | 1041 |
| Total Speeches | 193 |
| Total Laws Proposed | 936 |

## Chamber Breakdown

| Chamber | Members |
|---------|---------|
| Chamber of Deputies | 22 |
| Senate | 10 |

## Top Members by Activity

| Deputy | Activity | Speeches | Laws |
|--------|----------|---------|------|
| [[politicians/deputies/CSÉP Éva-Andrea]] | 94 | 11 | 83 |
| [[politicians/deputies/MARKÓ Attila-Gábor]] | 79 | 2 | 77 |
| [[politicians/deputies/HAJDU Gábor]] | 67 | 2 | 65 |
| [[politicians/deputies/MIKLÓS Zoltán]] | 60 | 3 | 57 |
| [[politicians/deputies/BENDE Sándor]] | 59 | 7 | 52 |
| [[politicians/deputies/CSOMA Botond]] | 59 | 18 | 41 |
| [[politicians/deputies/GÁL Károly]] | 55 | 2 | 53 |
| [[politicians/deputies/KÖNCZEI Csaba]] | 53 | 2 | 51 |
| [[politicians/deputies/VASS Levente]] | 51 | 11 | 40 |
| [[politicians/deputies/SZABÓ Ödön]] | 48 | 13 | 35 |
| [[politicians/deputies/KÁNTOR Boglárka]] | 44 | 2 | 42 |
| [[politicians/deputies/MAGYAR Loránd-Bálintchestor al Camerei Deputaţilor]] | 42 | 4 | 38 |
| [[politicians/deputies/BIRÓ Rozália-Ibolya]] | 40 | 1 | 39 |
| [[politicians/deputies/MOLNAR Andrei]] | 39 | 1 | 38 |
| [[politicians/deputies/KULCSÁR-TERZA József-György]] | 38 | 1 | 37 |

## Dataview Query

```dataview
TABLE party, activity_score, speeches_count, laws_proposed
FROM "vault/politicians"
WHERE party = "UDMR"
SORT activity_score DESC
```
