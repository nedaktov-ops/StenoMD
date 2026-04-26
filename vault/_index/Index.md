# 🧠 Brain Vault Index

> Consolidated index with filtering support for the StenoMD Brain Vault

---

## Quick Navigation

| Find | Link |
|------|------|
| All Deputies | [[politicians/deputies]] |
| All Senators | [[politicians/senators]] |
| All Proposals | [[proposals]] |
| All Committees | [[committees]] |
| Dashboard | [[_brain/Dashboard]] |

---

## Filter by Party

### PSD Deputies

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  constituency as "Constituency",
  laws_proposed + speeches_count as "Activity"
FROM "politicians/deputies"
WHERE party = "PSD" AND party != null
SORT laws_proposed DESC
LIMIT 20
```

### PNL Deputies

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  constituency as "Constituency",
  laws_proposed + speeches_count as "Activity"
FROM "politicians/deputies"
WHERE party = "PNL"
SORT laws_proposed DESC
LIMIT 20
```

### AUR Deputies

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  constituency as "Constituency",
  laws_proposed + speeches_score as "Activity"
FROM "politicians/deputies"
WHERE party = "AUR"
SORT laws_proposed DESC
LIMIT 20
```

### USR Deputies

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  constituency as "Constituency", 
  laws_proposed + speeches_count as "Activity"
FROM "politicians/deputies"
WHERE party = "USR"
SORT laws_proposed DESC
LIMIT 20
```

---

## Filter by Constituency

### București Deputies

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  party as "Party",
  laws_proposed + speeches_count as "Activity"
FROM "politicians/deputies"
WHERE constituency = "BUCUREŞTI"
SORT laws_proposed DESC
LIMIT 20
```

### Iași Deputies

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  party as "Party",
  laws_proposed + speeches_count as "Activity"
FROM "politicians/deputies"
WHERE constituency = "IAŞI"
SORT laws_proposed DESC
LIMIT 20
```

### Constanța Deputies

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  party as "Party",
  laws_proposed + speeches_count as "Activity"
FROM "politicians/deputies"
WHERE constituency = "CONSTANŢA"
SORT laws_proposed DESC
LIMIT 20
```

---

## Activity Rankings

### Most Active Deputies (Overall)

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  party as "Party",
  constituency as "Constituency",
  laws_proposed + speeches_count as "Activity Score"
FROM "politicians/deputies"
WHERE party != null
SORT laws_proposed + speeches_count DESC
LIMIT 25
```

### Most Prolific Speakers

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  party as "Party",
  speeches_count as "Speeches"
FROM "politicians/deputies"
WHERE speeches_count > 0
SORT speeches_count DESC
LIMIT 20
```

---

## Senator Index

### All Senators

```dataview
TABLE WITHOUT ID
  file.link as "Senator",
  party as "Party",
  constituency as "Constituency"
FROM "politicians/senators"
WHERE party != null
LIMIT 30
```

### Senators by Party

```dataview
TABLE WITHOUT ID
  party as "Party",
  length(file) as "Members"
FROM "politicians/senators"
GROUP BY party
FLATTEN
SORT length(file) DESC
```

---

## Proposal Index

### Recent Proposals

```dataview
TABLE WITHOUT ID
  file.link as "Proposal",
  status as "Status"
FROM "proposals"
WHERE idp >= 22000
SORT idp DESC
LIMIT 20
```

### Proposals by Status

```dataview
TABLE WITHOUT ID
  status as "Status",
  length(file) as "Count"
FROM "proposals"
GROUP BY status
FLATTEN
```

---

## Committee Directory

### All Committees

```dataview
LIST
FROM "committees"
WHERE file.name != "Index"
```

### Committee Members

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  committee as "Committee",
  role as "Role"
FROM "politicians/deputies"
FLATTEN committees
WHERE committee != null
LIMIT 30
```

---

## AI Query Templates

### Search by Name

```dataview
TABLE WITHOUT ID
  file.link as "Name",
  party as "Party",
  constituency as "Constituency"
FROM "politicians/deputies"
WHERE contains(file.name, "NAME")
```

### Search by Activity Score

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  activity_score as "Score"
FROM "politicians/deputies"
WHERE activity_score > 20
SORT activity_score DESC
```

---

*Last Updated: 2026-04-26 | [[_brain/Dashboard|Dashboard]]*