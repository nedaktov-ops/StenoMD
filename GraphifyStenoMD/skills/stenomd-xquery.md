# StenoMD Extended Query Skill

**Trigger:** `/stenomd xquery`
**Purpose:** Extended query patterns for complex StenoMD searches

---

## Usage

```
/stenomd xquery cross_party                  # Cross-party collaborations
/stenomd xquery temporal PATTERN          # Time-based patterns
/stenomd xquery search TERM              # Full-text search
/stenomd xquery related ENTITY          # Find related entities
```

---

## Extended Queries

### Cross-Party Collaborations
Finds politicians from different parties who co-sponsored bills or appeared in same sessions.

```
/stenomd xquery cross_party

=== Cross-Party Collaborations ===

PSD-PNL: 23 co-sponsorships
PSD-USR: 8 co-sponsorships
PNL-AUR: 12 co-sponsorships
...
```

### Temporal Patterns
Analyzes activity over time.

```
/stenomd xquery temporal 2024

=== 2024 Patterns ===
Sessions: 89
Active politicians: 234
Most active month: March 2024
Top law: 38/2026
```

### Related Entities
Finds all entities connected to a given entity.

```
/stenomd xquery related "TANASESCU ALINA"

=== Related Entities ===
Direct (2 hops):
- session-20241221
- session-20250115
- PSD
- 38-2026
- 52-2026
```

### Search
Full-text search across graph nodes.

```
/stenomd xquery search "buget"

=== Search Results ===
Nodes containing "buget":
- Comisia pentru buget
- buget finante
- legea bugetului
```