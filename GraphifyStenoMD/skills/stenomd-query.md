# StenoMD Query Skill

**Trigger:** `/stenomd query`
**Purpose:** Query the knowledge graph for insights

---

## Usage

```
/stenomd query "SEARCH_TERM"           # Search graph
/stenomd query "politician NAME"        # Find politician details
/stenomd query "law NUMBER"             # Find law
/stenomd query "session DATE"            # Find session
/stenomd query --type politician       # Limit to politician type
/stenomd query --type session         # Limit to session type
/stenomd query --type law           # Limit to law type
/stenomd query --depth 3             # Set traversal depth
/stenomd query --limit 20             # Limit results
```

---

## What It Does

1. **Finds matching nodes** in the knowledge graph
2. **Traverses connections** up to specified depth
3. **Reports findings** with confidence levels
4. **Shows path** to each connection

---

## Query Types

| Pattern | Example | Result |
|---------|---------|--------|
| Politician | `TANASESCU` | Profile + sessions + laws |
| Law | `38-2026` | Law details + sponsors + sessions |
| Session | `2024-12-21` | Session details + speakers + debates |
| Party | `PSD` | All PSD politicians |
| Committee | `comisia buget` | Committee members |

---

## Example Outputs

### Politician Query
```
/stenomd query "TANASESCU ALINA"

=== Results (3 nodes) ===
Node: TĂNĂSESCU Alina-Elena
  Type: senator
  Chamber: senate
  Party: PSD
  Constituency: Dolj
  Sessions: 12
  Speeches: 8
  Laws Proposed: 2

Connections:
  -session--> 20241221 (confidence: EXTRACTED)
  -party--> PSD (confidence: EXTRACTED)
  -sponsor--> 38-2026 (confidence: EXTRACTED)
```

### Activity Query
```
/stenomd query "most active"

=== Results ===
Top 10 most active politicians:
1. ANDREI DANIEL GHEORGHE (87 speeches)
2. ANAMARIA GAVRILĂ (72 speeches)
3. VERGINIA VEDINAŞ (65 speeches)
...
```

---

## Limitations

- Read-only graph access
- Uses existing graph at `Graphify/graphify-out/graph.json`
- No semantic extraction (use --mode deep in full AI session)