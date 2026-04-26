# MP Activity Overview

> Query to see all MP activity in one view

```dataview
TABLE WITHOUT ID
  file.link as Deputy,
  party,
  speeches_count,
  laws_proposed,
  committees,
  party_affiliations,
  legislature
FROM "politicians/deputies"
WHERE file.name != "Index.md"
SORT speeches_count DESC
LIMIT 50
```

---

## Most Active MPs by Speeches

```dataview
LIST FROM "politicians/deputies"
WHERE speeches_count > 20
SORT speeches_count DESC
```

## MPs by Party with Committee Activity

```dataview
TABLE party, length(committees) as Committees, speeches_count
FROM "politicians/deputies"
WHERE party != null
SORT speeches_count DESC
```

## Find MPs Who Discussed Specific Topics

> Note: This requires topics to be extracted from speeches

```dataview
LIST
FROM "politicians/deputies"
WHERE contains(party_affiliations, "PSD")
WHERE speeches_count > 10
```

## Cross-Party Committee Memberships

```dataview
TABLE WITHOUT ID
  file.link as Deputy,
  party,
  committees[0].name as Committee,
  committees[0].position as Role
FROM "politicians/deputies"
WHERE committees
WHERE committees[0].position = "Chairperson"
SORT party
```