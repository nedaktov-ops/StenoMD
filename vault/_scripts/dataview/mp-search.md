# MP Search & Discovery

Search templates for finding specific MPs in the vault.

## Find by Name

```dataview
LIST FROM "politicians/deputies"
WHERE contains(file.name, "Ciolacu")
```

## Find by Party

```dataview
LIST FROM "politicians/deputies"
WHERE party = "PSD"
SORT laws_proposed DESC
```

```dataview
LIST FROM "politicians/deputies"
WHERE party = "PNL"
SORT laws_proposed DESC
```

## Find by Constituency

```dataview
LIST FROM "politicians/deputies"
WHERE contains(constituency, "BUCUREŞTI")
```

## Find by Activity Level

### Most Active Speakers
```dataview
LIST FROM "politicians/deputies"
WHERE speeches_count > 30
SORT speeches_count DESC
LIMIT 20
```

### Most Prolific Sponsors
```dataview
LIST FROM "politicians/deputies"
WHERE laws_proposed > 50
SORT laws_proposed DESC
LIMIT 20
```

## Find by Committee

```dataview
LIST FROM "politicians/deputies"
WHERE contains(committees[0].name, "Buget")
```

## Find by Stable ID

```dataview
LIST FROM "politicians"
WHERE stable_id = "pol_f9c1959c508c"
```

## Find Inactive MPs

```dataview
LIST FROM "politicians/deputies"
WHERE !speeches_count
```