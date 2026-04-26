---
tags:
- party
party_name: MIN
---

# Party: MIN

## Overview

| Metric | Value |
|--------|-------|
| Members | 15 |
| Total Activity Score | 428 |
| Total Speeches | 72 |
| Total Laws Proposed | 356 |

## Chamber Breakdown

| Chamber | Members |
|---------|---------|
| Chamber of Deputies | 15 |

## Top Members by Activity

| Deputy | Activity | Speeches | Laws |
|--------|----------|---------|------|
| [[politicians/deputies/Ştefan BOUDA]] | 51 | 5 | 46 |
| [[politicians/deputies/Adrian-Miroslav MERKA]] | 46 | 4 | 42 |
| [[politicians/deputies/Ognean CRÎSTICI]] | 44 | 1 | 43 |
| [[politicians/deputies/Silviu VEXLER]] | 42 | 10 | 32 |
| [[politicians/deputies/Silviu FEODOR]] | 38 | 3 | 35 |
| [[politicians/deputies/Nicolae-Miroslav PETREŢCHI]] | 37 | 20 | 17 |
| [[politicians/deputies/Giureci-Slobodan GHERA]] | 29 | 8 | 21 |
| [[politicians/deputies/Dragoş Gabriel ZISOPOL]] | 28 | 4 | 24 |
| [[politicians/deputies/Ionel STANCU]] | 26 | 2 | 24 |
| [[politicians/deputies/Ghervazen LONGHER]] | 21 | 2 | 19 |
| [[politicians/deputies/Ioana GROSARU]] | 21 | 3 | 18 |
| [[politicians/deputies/Iulius Marian FIRCZAK]] | 14 | 2 | 12 |
| [[politicians/deputies/Iusein IBRAM]] | 13 | 1 | 12 |
| [[politicians/deputies/Gheorghe NACOV]] | 13 | 5 | 8 |
| [[politicians/deputies/Bogdan-Alin STOICA]] | 5 | 2 | 3 |

## Dataview Query

```dataview
TABLE party, activity_score, speeches_count, laws_proposed
FROM "vault/politicians"
WHERE party = "MIN"
SORT activity_score DESC
```
