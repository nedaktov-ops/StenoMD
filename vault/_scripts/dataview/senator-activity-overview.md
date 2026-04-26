# Senator Activity Overview

Query all senators and rank by party and activity.

```dataview
TABLE WITHOUT ID
  link(file.link, name) as Senator,
  party,
  constituency,
  legislature,
  status
FROM "politicians"
WHERE type = "senator"
SORT party ASC
LIMIT 50
```

## Senators by Party (2024 Legislature)

| Party | Count |
| %%=length(filter(this, t => t.type = "senator" AND t.party = "PSD"))%% | PSD |
| %%=length(filter(this, t => t.type = "senator" AND t.party = "PNL"))%% | PNL |
| %%=length(filter(this, t => t.type = "senator" AND t.party = "AUR"))%% | AUR |
| %%=length(filter(this, t => t.type = "senator" AND t.party = "USR"))%% | USR |
| %%=length(filter(this, t => t.type = "senator" AND t.party = "UDMR"))%% | UDMR |

---

## All Active Senators

%%TABLE rows: this WHERE type="senator" AND status = "active" SORT this.party ASC%%