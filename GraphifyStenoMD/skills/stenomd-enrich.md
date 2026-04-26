# StenoMD Enrich Skill

**Trigger:** `/stenomd enrich`
**Purpose:** Run enrichment pipelines to fill missing data fields

---

## Usage

```
/stenomd enrich                          # Show enrichment targets
/stenomd enrich --type party             # Enrich party data only
/stenomd enrich --type speeches         # Enrich speeches count
/stenomd enrich --type committees       # Enrich committees
/stenomd enrich --type sponsors        # Enrich law sponsors
/stenomd enrich --politician "NAME"    # Enrich specific politician
```

---

## What It Does

1. **Scans graph** for missing data fields
2. **Identifies enrichment targets** by impact
3. **Applies enrichment scripts** in priority order
4. **Reports** what was enriched

---

## Enrichment Types

| Type | Target Field | Scripts |
|------|-------------|---------|
| `party` | party, party_affiliations | enrich_profiles.py |
| `speeches` | speeches_count | add_speeches_to_profiles.py |
| `committees` | committees | add_committees.py |
| `sponsors` | sponsors, co_sponsors | enrich_laws.py |
| `stable_id` | stable_id | generate_stable_ids.py |

---

## Example Output

```
=== Enrichment Targets ===
Missing party data: 12 politicians
Missing speeches_count: 234 politicians
Missing committees: 156 politicians
Missing law sponsors: 456 laws

=== Priority ===
1. Add party data (12 politicians, high impact)
2. Add speeches count (234 politicians, medium impact)
3. Add committees (156 politicians, medium impact)
4. Add law sponsors (456 laws, low impact)

=== Enriching party data ===
[enrich_profiles.py --type party]
...
```

---

## Integration

Uses existing scripts:
- `scripts/enrich_profiles.py`
- `scripts/add_speeches_to_profiles.py`
- `scripts/add_committees.py`
- `scripts/enrich_laws.py`
- `scripts/generate_stable_ids.py`

---

## Notes

- Read-only to existing data
- Creates backup before changes
- Logs all enrichment actions