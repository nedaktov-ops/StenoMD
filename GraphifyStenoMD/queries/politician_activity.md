# Politician Activity Query

**Trigger:** `/stenomd query politician "NAME"`
**Purpose:** Find all sessions and activity for a specific politician

---

## Usage

```
/stenomd query politician "TANASESCU"
/stenomd query politician "VASILE"
/stenomd query politician "全部" --limit 20
```

---

## Query Logic

1. Search for nodes matching name
2. Follow session edges
3. Count speeches
4. List laws proposed
5. Show party membership

---

## Example Output

```
=== Politician: TĂNĂSESCU Alina-Elena ===

Profile:
- Type: senator
- Chamber: senate
- Party: PSD
- Constituency: Dolj
- Legislature: 2024-2028

Activity:
- Sessions attended: 12
- Total speeches: 8
- Laws proposed: 2

Sessions:
- session-20241221.md
- session-20250115.md
- ...

Laws Sponsored:
- 38/2026
- 52/2026
```

---

## Graph Edges

| Edge Type | Meaning |
|----------|---------|
| `--speaks_in-->` | Politician spoke in session |
| `--proposes-->` | Politician proposed law |
| `--member_of-->` | Member of party |
| `--represents-->` | Represents constituency |