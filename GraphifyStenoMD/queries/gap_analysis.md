# Gap Analysis Query

**Trigger:** `/stenomd query gaps`
**Purpose:** Identify missing data across the project

---

## Usage

```
/stenomd query gaps
/stenomd analyze gaps
```

---

## What It Finds

| Category | Missing Fields | Impact |
|----------|-------------|--------|
| Politicians | party | HIGH |
| Politicians | speeches_count | MEDIUM |
| Politicians | committees | MEDIUM |
| Politicians | stable_id | HIGH |
| Laws | sponsors | MEDIUM |
| Sessions | deputy_count | LOW |

---

## Example Output

```
=== Gap Analysis ===

Politicians (944 total):
- Missing party: 12
- Missing speeches: 234  
- Missing committees: 156
- Missing stable_id: 0

Laws (1976 total):
- Missing sponsors: 456

Sessions (2131 total):
- Missing deputy_count: 89

=== Priority ===
1. Add party data (12, critical)
2. Add stable_id (0, complete)
3. Fill speeches (234, medium)
```

---

## Resolution Paths

| Gap | Resolution Tool |
|-----|--------------|
| Missing party | `/stenomd enrich --type party` |
| Missing speeches | `/stenomd enrich --type speeches` |
| Missing committees | `/stenomd enrich --type committees` |
| Missing sponsors | `/stenomd enrich --type sponsors` |