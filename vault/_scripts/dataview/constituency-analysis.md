# Constituency Analysis

```dataview
TABLE WITHOUT ID
  link(file.link, name) as Deputy,
  party,
  constituency,
  speeches_count,
  laws_proposed
FROM "politicians/deputies"
WHERE type = "deputy" AND constituency != null
SORT constituency ASC
LIMIT 50
```

## Electoral Circumscriptions

| Code | Deputies | Party Distribution |
| -----|---------|----------------|
| %%=length(filter(this, t => t.type = "deputy" AND t.constituency = "ALBA"))%% | ALBA | PSD(0) PNL(0) AUR(0) USR(0) |
| %%=length(filter(this, t => t.type = "deputy" AND t.constituency = "ARAD"))%% | ARAD | |
| %%=length(filter(this, t => t.type = "deputy" AND t.constituency = "ARGEŞ"))%% | ARGEŞ | |
| %%=length(filter(this, t => t.type = "deputy" AND t.constituency = "BACĂU"))%% | BACĂU | |
| %%=length(filter(this, t => t.type = "deputy" AND t.constituency = "BIHOR"))%% | BIHOR | |
| %%=length(filter(this, t => t.type = "deputy" AND t.constituency = "BOTOŞANI"))%% | BOTOŞANI | |
| %%=length(filter(this, t => t.type = "deputy" AND t.constituency = "BRASILOV"))%% | BRAŞOV | |

## Most Active by Constituency

```dataview
TABLE constituency, party, name, speeches_count + laws_proposed as Activity
FROM "politicians/deputies"
WHERE type = "deputy" AND constituency != null
SORT speeches_count DESC
LIMIT 20
```