# Cross-Reference Query

> Find all connections to any item in the vault

## Usage

This query finds everything linked TO a specific item - useful for reverse engineering connections.

## Basic Usage

Replace `ITEM_NAME` with the item you want to trace:

```dataview
ITEM_NAME = "Nicolae Ion"  # Change this
```

## What Links TO This Item?

```dataview
LIST FROM ""
WHERE contains(file.inlinks, "ITEM_NAME")
```

## What Does This Item Link TO?

```dataview
LIST file.outlinks
FROM "ITEM_FILE"
```

---

## Examples

### Find All References to a Deputy

```dataview
LIST FROM "politicians"
WHERE contains(file.inlinks, "ADRIAN-CÂCIU")
```

### Find All References to a Law

```dataview
LIST FROM "laws"
WHERE contains(file.inlinks, "101-2026")
```

### Find All References to a Session

```dataview
LIST FROM "sessions"
WHERE contains(file.inlinks, "2025-03-26")
```

### Find All References to a Committee

```dataview
LIST FROM "committees"
WHERE contains(file.inlinks, "Budget")
```

---

## Full Connection Map

### 1. Get All Outgoing Links

```dataview
TABLE WITHOUT ID
  file.link as "Source File",
  file.outlinks as "Links To"
WHERE file.name = "YOUR_FILE_NAME"
```

### 2. Get All Incoming Links (Reverse)

```dataview
TABLE
  "What References This" as "Source",
  "Link Type" as "Type"
FROM ""
WHERE contains(file.inlinks, "TARGET_NAME")
```

### 3. Create Connection Matrix

```dataview
TABLE
  file.link as "Item",
  length(file.inlinks) as "Incoming",
  length(file.outlinks) as "Outgoing"
FROM "politicians"
SORT length(file.inlinks) + length(file.outlinks) DESC
LIMIT 20
```

---

## Network Analysis

### Most Connected Items

```dataview
TABLE WITHOUT ID
  file.link as "Item",
  "In Links" as "Referenced By",
  "Out Links" as "Links To"
FROM "politicians"
SORT length(file.inlinks) + length(file.outlinks) DESC
LIMIT 25
```

### Connection Paths Between Two Items

```dataview
LIST FROM ""
WHERE contains(file.inlinks, "ITEM_A")
AND contains(file.outlinks, "ITEM_B")
```

### Shared Connections

```dataview
LIST FROM "politicians"
WHERE contains(file.outlinks, "COMMON_TARGET")
```

---

## Graph Traversal Examples

### Deputy → Law → Session Chain

```dataview
LIST FROM ""
WHERE contains(file.inlinks, "DEPUTY_NAME")
  OR contains(file.inlinks, "LAW_NUMBER")
```

### Party Network

```dataview
LIST FROM "politicians"
WHERE party = "PSD"
SORT activity_score DESC
```

### Committee Members

```dataview
LIST FROM "politicians"
WHERE contains(committees, "COMMITTEE_NAME")
```

---

*Use this query to understand the full connection web in your vault.*