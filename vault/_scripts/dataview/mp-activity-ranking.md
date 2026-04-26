# MP Activity Overview

Query all politicians and rank by parliamentary activity (speeches + proposals + motions).

```dataview
TABLE WITHOUT ID
  link(file.link, name) as Deputy,
  party,
  constituency,
  speeches_count + laws_proposed + motions as "Total Activity",
  speeches_count as Speeches,
  laws_proposed as Proposals,
  motions as Motions,
  committees[0].name as "Primary Committee"
FROM "politicians"
WHERE type = "deputy"
SORT (speeches_count + laws_proposed + motions) DESC
LIMIT 25
```

## Top 25 Most Active Deputies (2024 Legislature)

| Deputy | Party | Constituency | Activity | Speeches | Proposals | Motions | Committee |
|--------|-------|-------------|----------|---------|-----------|--------|-----------|
| %%TABLE rows: this WHERE type="deputy" SORT this.speeches_count + this.laws_proposed + this.motions DESC LIMIT 25%%