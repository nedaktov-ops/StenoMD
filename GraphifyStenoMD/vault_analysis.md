# Obsidian Vault Architecture Analysis

**Project:** StenoMD - Romanian Parliament Knowledge Brain  
**Generated:** 2026-04-26

---

## Vault Structure Overview

```
vault/
├── _brain/           # Brain queries and analytics
├── committees/       # Committee documentation
├── dashboards/       # Visual dashboards
├── docs/             # Documentation
├── laws/             # Law profiles (124 files)
├── politicians/      # MP profiles (524 files)
├── politics/         # Political content (72 files)
├── proposals/        # Legislative proposals (1039 files)
├── sessions/         # Parliamentary sessions (172 files)
├── _parliament/      # Parliamentary reference
├── _templates/       # File templates
└── _scripts/        # Automation scripts
```

---

## Directory Breakdown

| Directory | Files | Purpose |
|-----------|-------|---------|
| `politicians/` | 524 | Senator & deputy profiles |
| `proposals/` | 1,039 | Legislative proposals |
| `laws/` | 124 | Law documents |
| `sessions/` | 172 | Parliamentary sessions |
| `politics/` | 72 | Political content |
| `committees/` | 15 | Committee docs |
| `dashboards/` | 5 | Dashboard views |
| `_brain/` | 7 | Brain queries |
| `_parliament/` | 6 | Reference docs |
| `_templates/` | 4 | File templates |
| `_scripts/` | 14 | Automation |

**Total: ~2,000+ markdown files**

---

## Entity Types

### Politicians (524 files)
- **Senators:** ~137 files in `politicians/senators/`
- **Deputies:** ~330+ files in `politicians/deputies/` and `politicians/`
- **Parties:** 9 party files (PSD, PNL, AUR, USR, UDMR, SOS, POT, Unknown, Grupul)

### Laws (124 files)
- **Year range:** 1973-2026
- **Status categories:** Proposed, Adopted, Rejected

### Sessions (172 files)
- **Date range:** 1998-2025
- **Chambers:** Deputies, Senate, Joint

### Proposals (1,039 files)
- **Legislative proposals** from parliament

---

## Schema Analysis

### Politician Frontmatter Schema
```yaml
---
stable_id: pol_509571a0e0a6      # Unique ID
original_elected_party: PSD        # Original party
type: senator                     # senator|deputy
chamber: senate                  # senate|chamber
party: PSD                        # Current party
party_full: Partidul Social Democrat
constituency: Dolj              # Electoral constituency
legislature: 2024-2028          # Current legislature
status: active                  # active|inactive
url: https://senat.ro/...        # Source URL
party_affiliations: []          # Historical affiliations
ai_friendly_name: NAME          # AI-optimized name
search_aliases: []              # Search variations
activity_score: 0               # Computed score
idm: 9018                      # ID from parliament
speeches_count: 12              # Speech count
laws_proposed: 0                 # Laws proposed
committees: []                   # Committee memberships
---
```

### Law Frontmatter Schema
```yaml
---
tags: [law]
law_number: "38/2026"
title: "Law title"
title_short: "Law 38"
chamber: senate|chamber
status: ...
year: 2026
date_proposed: ""
date_adopted: ""
sessions_count: 1
---
```

### Session Frontmatter Schema
```yaml
---
date: "2025-09-17"
session_date: "2025-09-17"
chamber: Chamber of Deputies
legislature: 2024-2028
speech_count: 49
deputy_count: 49
---
```

---

## Link Architecture

### Internal Links (Wikilinks)
- `[[politicians/deputies]]` - Cross-reference deputies
- `[[politicians/senators]]` - Cross-reference senators
- `[[laws]]` - Law index
- `[[committees]]` - Committee index

### External Links
- **senat.ro** - Senate profiles
- **cdep.ro** - Chamber of Deputies profiles

---

## Data Quality Issues (from Health Check)

### Current Issues Found
- **5,127 broken wikilinks** - Links to non-existent files
- **144 incomplete YAML** - Missing required frontmatter fields

### Common Issues
1. **Missing party data** in politician profiles
2. **Missing speeches_count** - Needs scraping
3. **Missing committees** - Needs committee data
4. **Unknown parties** - Many deputies have `party: Unknown`

---

## Architecture Recommendations

### 1. Data Consistency
- Fix broken links (use health_check.py)
- Complete missing frontmatter fields
- Standardize party names

### 2. Structure Enhancement
- Add dataview fields for queries
- Include computed fields (activity_score)
- Add temporal fields (last_updated)

### 3. Query Optimization
- Use `_brain/` queries for analytics
- Create dedicated dashboards
- Optimize dataview indexes

### 4. Automation
- Use `_scripts/` for batch operations
- Implement hooks for auto-updates

---

## Data Flow

```
[cdep.ro] --> [Scrapers] --> [vault/]
                            |
                            v
                      [Graphify]
                            |
                            v
                    [GraphifyStenoMD]
                   (gap-aware analysis)
```

---

## Recommendations for Improvement

| Area | Action | Priority |
|------|--------|----------|
| Link Fixes | Run health_check.py to find broken links | HIGH |
| Party Data | Fill missing party fields | HIGH |
| Committee Links | Link committees to members | MEDIUM |
| Session Activity | Complete session data | MEDIUM |
| Search | Add search aliases | LOW |

---

*Analysis generated by GraphifyStenoMD*