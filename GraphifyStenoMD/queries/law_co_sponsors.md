# Law Co-Sponsors Query

**Trigger:** `/stenomd query law "NUMBER"`
**Purpose:** Find co-sponsors and discussions for a specific law

---

## Usage

```
/stenomd query law "38-2026"
/stenomd query law "448-2006"
/stenomd query law "全部" --limit 20
```

---

## Query Logic

1. Find law node by number
2. Extract sponsors
3. Find co-sponsors
4. List sessions where discussed
5. Show party cross-references

---

## Example Output

```
=== Law: 38/2026 ===

Details:
- Title: Proiect de Lege privind aprobarea Ordonanţei...
- Chamber: Senate
- Status: Lege 245/2024
- Year: 2026

Sponsors:
- Primary: Government (Guvern)

Co-Sponsors:
- (List from graph)

Sessions Discussed:
- session-20241221.md
- session-20250115.md

Party Cross-References:
- PSD: 3 mentions
- PNL: 2 mentions
- AUR: 1 mention
```

---

## Graph Edges

| Edge Type | Meaning |
|----------|---------|
| `--discussed_in-->` | Law debated in session |
| `--sponsored_by-->` | Proposed by politician |