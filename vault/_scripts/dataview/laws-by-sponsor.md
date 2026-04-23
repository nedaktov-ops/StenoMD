# Laws by Sponsor
query:: Laws and their parliamentary sponsors

## Recent Laws

```dataview
TABLE WITHOUT ID
file.link as Law,
status,
date_passed,
from(date) as Year
FROM "laws"
WHERE status = "active"
SORT date_passed DESC
LIMIT 25
```

## Laws by Sponsor/MP

```dataview
LIST
FROM "laws"
WHERE contains(sponsors, "Ciolacu")
SORT date_passed DESC
```

## Laws Discussed Per Session

```dataview
TABLE WITHOUT ID
file.link as Session,
chamber,
frontmatter.laws_discussed as Laws_Discussed,
length(frontmatter.laws_discussed) as Count
FROM "sessions"
WHERE frontmatter.laws_discussed
SORT file.name DESC
```

## Law Status Summary

```dataview
TABLE status, count() as Number
FROM "laws"
GROUP BY status
```

## Active Legislation

```dataview
LIST
FROM "laws"
WHERE status = "active"
SORT file.name
```