# Vault Templates

This document describes the frontmatter fields used in StenoMD vault notes.

All frontmatter is YAML (`---` delimiters). Fields are capitalized for consistency.

---

## Deputy & Senator Profiles (`politicians/deputies/*.md`, `politicians/senators/*.md`)

**Example:**

```yaml
---
name: Mihai Tudose
type: deputy
party: PSD
party_full: Partidul Social Democrat
constituency: Neamț
idm: 123
stable_id: dep-123
speeches_count: 42
laws_proposed: 5
committees:
  - Comisia pentru buget, finanțe și bănci
photo_url: https://...
url: https://www.cdep.ro/deputat/123
brain:
  activity_score: 0.85
  collaboration_network: []
  party_alignment: {}
---
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Full name (required) |
| `type` | `deputy` / `senator` | Required |
| `party` | string | Party abbreviation (required) |
| `party_full` | string | Full party name (optional) |
| `constituency` | string | Electoral district (required for deputies) |
| `idm` | integer | Unique numeric ID from cdep.ro/senat.ro (required) |
| `stable_id` | string | Persistent ID across legislatures (`dep-` or `sen-` prefix) |
| `speeches_count` | integer | Number of speeches/statements (0 if none) |
| `laws_proposed` | integer | Number of laws initiated (0 if none) |
| `committees` | list of strings | Committee assignments |
| `photo_url` | string | URL to official portrait |
| `url` | string | Official profile page |
| `brain` | mapping | AI-friendly fields: `activity_score` (float 0-1), `collaboration_network` (list of names), `party_alignment` (party → float) |

---

## Session Notes (`sessions/deputies/*.md`, `sessions/senate/*.md`)

**Example:**

```yaml
---
date: 2024-01-15
chamber: deputies
title: Ședința Camerei Deputaților
participants:
  - Mihai Tudose
  - Ana Birchall
deputy_count: 320
statements_count: 45
laws_discussed:
  - 20/2024
source_url: https://cdep.ro/stenograma/...
---
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `date` | string (ISO `YYYY-MM-DD`) | Required |
| `chamber` | `deputies` / `senate` | Required |
| `title` | string | Display title (required) |
| `participants` | list of strings | Names of MPs present |
| `deputy_count` | integer | Number of deputies attending (senate sessions may omit) |
| `statements_count` | integer | Number of extracted statements |
| `laws_discussed` | list of `NN/YYYY` | Laws referenced in the session |
| `source_url` | string | Original stenogram URL |

---

## Law Profiles (`laws/*.md`)

**Example:**

```yaml
---
number: 20/2024
title: Legea responsabilității instituționale...
status: adoptată
date: 2024-03-10
sponsors:
  - Mihai Tudose
proposals:
  - L20/2024
source_url: https://cdep.ro/...
---
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `number` | string (`NN/YYYY`) | Required, unique |
| `title` | string | Short title (required) |
| `status` | string | e.g., adoptată, respinsă, în dezbatere |
| `date` | string (ISO) | Date of final vote or promulgation |
| `sponsors` | list of strings | MP names who sponsored |
| `proposals` | list of strings | Proposal identifiers (if available) |
| `source_url` | string | Official law text or proposal page |

---

## Committee Notes (`_parliament/committees/*.md`)

**Example:**

```yaml
---
name: Comisia pentru buget, finanțe și bănci
chamber: deputies
members:
  - Mihai Tudose
  - Elena Lasconi
leader: Ion Popescu
---
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Full committee name |
| `chamber` | `deputies` / `senate` / `joint` |
| `members` | list of strings | Deputy or senator names |
| `leader` | string | Committee chair (optional) |

---

## General Conventions

- Filenames use kebab-case (e.g., `mihai-tudose.md`, `20-2024.md`).
- Dates are always ISO 8601 (`YYYY-MM-DD`).
- Lists are YAML arrays (`- item`).
- Multi-line text in frontmatter should be folded with `|` or quoted.

---

## Validation

Use `scripts/validators.py` to check frontmatter completeness:

```bash
python3 scripts/validators.py --vault vault/
```

The merge pipeline also logs missing required fields.

---

## Template Files

Physical template files are stored in `config/templates/` (to be added). QuickAdd uses these templates when creating new notes.
