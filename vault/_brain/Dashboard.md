# Brain Vault Dashboard

> Interactive dashboard for the Romanian Parliament Brain Vault

---

## Quick Navigation

| Search | Link |
|--------|------|
| All Deputies | [[politicians/deputies]] |
| All Senators | [[politicians/senators]] |
| All Proposals | [[proposals]] |
| All Committees | [[committees]] |
| Sessions Index | [[sessions/deputies/Index]] |
| Brain Queries | [[_brain/queries]] |

---

## 🚀 Start Here

### Find a Politician

```dataview
TABLE WITHOUT ID
  file.link as "Name",
  party as "Party",
  constituency as "Constituency"
FROM "politicians/deputies"
WHERE contains(file.name, "PUT_NAME_HERE")
LIMIT 10
```

### Find by Party

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  constituency as "Constituency",
  laws_proposed as "Proposals"
FROM "politicians/deputies"
WHERE party = "PSD"
SORT laws_proposed DESC
LIMIT 20
```

### Find by Constituency

```dataview
TABLE WITHOUT ID  
  file.link as "Deputy",
  party as "Party",
  laws_proposed as "Proposals"
FROM "politicians/deputies"
WHERE constituency = "BUCUREŞTI"
SORT laws_proposed DESC
```

---

## 📊 Vault Overview

| Metric | Count |
|--------|-------|
| Deputies | 332 |
| Senators | 138 |
| Proposals | 1,039 |
| Sessions | 91 |
| Committees | 15 |
| Laws | 124 |

---

## 🏆 Top Active Politicians

### Most Proposals Sponsored

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  party as "Party",
  laws_proposed as "Proposals"
FROM "politicians/deputies"
WHERE laws_proposed > 0
SORT laws_proposed DESC
LIMIT 15
```

### Most Speeches

```dataview
TABLE WITHOUT ID
  file.link as "Deputy", 
  party as "Party",
  speeches_count as "Speeches"
FROM "politicians/deputies"
WHERE speeches_count > 0
SORT speeches_count DESC
LIMIT 15
```

### Most Active Overall (Proposals + Speeches)

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  party as "Party",
  laws_proposed + speeches_count as "Activity"
FROM "politicians/deputies"
SORT laws_proposed + speeches_count DESC
LIMIT 15
```

---

## ⚖️ Party Statistics

### Deputies by Party

```dataview
TABLE WITHOUT ID
  party as "Party",
  length(file) as "Members",
  sum(laws_proposed) as "Proposals",
  sum(speeches_count) as "Speeches"
FROM "politicians/deputies"
GROUP BY party
FLATTEN
SORT length(file) DESC
```

### Party Activity Comparison

```dataview
TABLE WITHOUT ID
  party as "Party",
  round(sum(laws_proposed) / length(file), 1) as "Avg Proposals",
  round(sum(speeches_count) / length(file), 1) as "Avg Speeches"
FROM "politicians/deputies"
GROUP BY party
FLATTEN
SORT sum(laws_proposed) DESC
```

---

## 📋 Proposal Browser

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

## 👥 Committee Directory

### All Committees with Members

```dataview
LIST
FROM "committees"
WHERE file.name != "Index"
LIMIT 15
```

### Find Committee Members

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  committee as "Committee",
  role as "Role"
FROM "politicians/deputies"
FLATTEN committees
WHERE committee != null
SORT committee
LIMIT 30
```

---

## 📅 Session Timeline

### Recent Sessions

```dataview
LIST
FROM "sessions/deputies"
WHERE date >= "2025-01-01"
SORT date DESC
LIMIT 15
```

### Session Count by Month

```dataview
TABLE WITHOUT ID
  date[0:7] as "Month",
  length(file) as "Sessions"
FROM "sessions/deputies"
GROUP BY date[0:7]
FLATTEN
SORT date DESC
LIMIT 12
```

---

## 🔍 Advanced Queries

### Deputies Without Speeches

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  party as "Party",
  constituency as "Constituency"
FROM "politicians/deputies"
WHERE speeches_count = 0
LIMIT 20
```

### Cross-Party Collaboration (co-sponsors)

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  party as "Party",
  "Co-Sponsors" as "Network"
FROM "politicians/deputies"
WHERE file.name != null
LIMIT 20
```

### Find Politicians by Committee

```dataview
TABLE WITHOUT ID
  file.link as "Deputy",
  party as "Party",
  role as "Role"
FROM "politicians/deputies"
WHERE contains(committees, "Budget")
FLATTEN committees
LIMIT 20
```

---

## 🎯 Use Cases

### 1. Find all proposals by "Nicolae"
```
Replace "NICOLA E" in the name search query above
```

### 2. Find PSD deputies from BUCUREŞTI
```
Change party = "PSD" AND constituency = "BUCUREŞTI"
```

### 3. See who is on the Budget Committee
```
Use the Committee Directory query above
```

### 4. Find most active AUR member
```
WHERE party = "AUR" SORT laws_proposed DESC
```

### 5. Find recent legislative activity
```
Check Recent Proposals section
```

---

## 📈 Analytics

### Activity by Constituency

```dataview
TABLE WITHOUT ID
  constituency as "Constituency",
  length(file) as "Deputies",
  sum(laws_proposed) as "Total Proposals"
FROM "politicians/deputies"
WHERE constituency != ""
GROUP BY constituency
FLATTEN
SORT sum(laws_proposed) DESC
LIMIT 20
```

### Top Constituencies by Activity

```dataview
TABLE WITHOUT ID
  constituency as "Constituency",
  sum(laws_proposed) / length(file) as "Avg Proposals"
FROM "politicians/deputies"
GROUP BY constituency  
FLATTEN
WHERE length(file) > 2
SORT sum(laws_proposed) DESC
LIMIT 10
```

---

*Updated: 2026-04-26 | [[_brain/Dashboard|Refresh]]*