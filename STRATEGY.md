# StenoMD Project - Comprehensive Strategy & Action Plan
## Last Updated: 2026-04-23 14:00
## Current Phase: Phase 1 - CRITICAL BUG FIX (Import Error)

---

## 🔧 COMPREHENSIVE IMPROVEMENT PLAN - 14 PHASES

### User Preferences Confirmed (2026-04-23)
| Option | Choice |
|--------|--------|
| Vault Migration | A - Migrate root-level files first |
| Knowledge Graph | B - Use full SQLite mempalace |
| Timeline | A - Implement all in one go |
| Additional Features | BOTH - Dataview queries + Relationship visualization |

### Issues Identified During Analysis
| # | Issue | Severity | Location |
|---|-------|----------|-----------|
| 1 | Import bug (senat_agent.py line 34) | CRITICAL | sys.path BEFORE import |
| 2 | Duplicate sessions in 3 locations | CRITICAL | vault/sessions/ |
| 3 | entities.json concurrent writes | CRITICAL | Multiple writers |
| 4 | Empty entities.json | CRITICAL | KG not updating |
| 5 | Progress file contention | HIGH | /tmp/stenomd_progress.json |
| 6 | DataValidator cache staleness | HIGH | In-memory only |
| 7 | Senate agent no KG update | HIGH | Missing call |
| 8 | Dashboard doesn't use SQLite KG | MEDIUM | Only JSON counts |

---

## PHASE 1: CRITICAL BUG FIX (Import Error)
| Step | Action | File | Line |
|------|--------|------|-------|
| 1.1 | Fix import order | senat_agent.py | Move sys.path BEFORE validators |

```python
# senat_agent.py - FIX at lines 28-35:
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))  # ADD BEFORE validators import
from validators import DataValidator
```

---

## PHASE 2: Vault Consolidation & Migration
| Step | Action | File | Description |
|------|--------|------|-------------|
| 2.1 | Create migrate_vault.py | scripts/migrate_vault.py | NEW - Consolidate |
| 2.2 | Migrate root sessions | vault/sessions/*.md | Move to deputies/ or senate/ |
| 2.3 | Migrate root politicians | vault/politicians/*.md | Move by chamber |
| 2.4 | Clean empty files | vault/* | Remove 0-byte files |

---

## PHASE 3: Standardize Agent Imports
| Step | Action | File | Description |
|------|--------|------|-------------|
| 3.1 | Create agents/__init__.py | agents/__init__.py | NEW - Central hub |
| 3.2 | Update cdep_agent.py | cdep_agent.py | Use module import |
| 3.3 | Update senat_agent.py | senat_agent.py | Use module import |

---

## PHASE 4: Thread-Safe Progress Files
| Step | Action | File | Description |
|------|--------|------|-------------|
| 4.1 | Separate progress files | cdep_agent.py | /tmp/stenomd_progress_cdep.json |
| 4.2 | Separate progress files | senat_agent.py | /tmp/stenomd_progress_senate.json |
| 4.3 | Update dashboard | dashboard.py | Read correct files |

---

## PHASE 5: JSON Output from Agents
| Step | Action | File | Description |
|------|--------|------|-------------|
| 5.1 | Add --json-output flag | cdep_agent.py | CLI flag |
| 5.2 | Add --json-output flag | senat_agent.py | CLI flag |
| 5.3 | Print JSON summary | Both agents | Structured output |

---

## PHASE 6: Dashboard JSON Parsing
| Step | Action | File | Description |
|------|--------|------|-------------|
| 6.1 | Pass --json-output | dashboard.py run_scrape() | Add flag to cmd |
| 6.2 | Parse JSON from stdout | dashboard.py run_scrape() | Parse last line |
| 6.3 | Display in UI | dashboard.js | Show stats |

---

## PHASE 7: SQLite Knowledge Graph Integration
| Step | Action | File | Description |
|------|--------|------|-------------|
| 7.1 | Load mempalace KG | dashboard.py get_statistics() | Import KnowledgeGraph |
| 7.2 | Get entity stats | dashboard.py | Query SQLite |
| 7.3 | Get triple stats | dashboard.py | Relationships |
| 7.4 | Display in UI | dashboard.js | Show KG stats |

---

## PHASE 8: Fix DataValidator Cache
| Step | Action | File | Description |
|------|--------|------|-------------|
| 8.1 | Add refresh method | validators.py | Refresh from disk |
| 8.2 | Use in agents | Both agents | Refresh before check |
| 8.3 | Add file locking | validators.py | Lock during read |

---

## PHASE 9: Fix Senate Agent KG Update
| Step | Action | File | Description |
|------|--------|------|-------------|
| 9.1 | Add update call | senat_agent.py | update_knowledge_graph() |
| 9.2 | Trigger merge | dashboard.py | Run merge after scrape |

---

## PHASE 10: Enhanced Frontmatter Schema
| Step | Action | File | Description |
|------|--------|------|-------------|
| 10.1 | Add party field | templates/politician.md | Party in frontmatter |
| 10.2 | Add sessions_appeared | templates/politician.md | Session links |
| 10.3 | Add laws_discussed | templates/session.md | Law links |
| 10.4 | Add relationships | templates/session.md | Participant graph |

---

## PHASE 11: File Locking (Data Safety)
| Step | Action | File | Description |
|------|--------|------|-------------|
| 11.1 | Add file locking | validators.py | Lock during writes |
| 11.2 | Add atomic writes | agents | Write to .tmp, rename |
| 11.3 | Add verification | agents | Verify write success |

---

## PHASE 12: Dataview Queries (Obsidian)
| Step | Action | File | Description |
|------|--------|------|-------------|
| 12.1 | Create queries/ | vault/_scripts/dataview/ | NEW folder |
| 12.2 | MPs by party | queries/mps-by-party.md | Dataview query |
| 12.3 | Sessions by date | queries/sessions-by-date.md | Dataview query |
| 12.4 | Laws by sponsor | queries/laws-by-sponsor.md | Dataview query |
| 12.5 | Graph network | queries/graph-network.md | Dataview JS |

---

## PHASE 13: Relationship Visualization (Dashboard)
| Step | Action | File | Description |
|------|--------|------|-------------|
| 13.1 | Add D3.js | dashboard.html | Visualization lib |
| 13.2 | Query relationships | dashboard.py | Load from SQLite KG |
| 13.3 | Network chart | dashboard.js | MP graph |
| 13.4 | Timeline chart | dashboard.js | Sessions |
| 13.5 | Law network | dashboard.js | Sponsorship |

---

## PHASE 14: Testing & Cleanup
| Step | Action | File | Description |
|------|--------|------|-------------|
| 14.1 | Test import fix | senat_agent.py | Verify runs |
| 14.2 | Test vault migration | migrate_vault.py | Verify files |
| 14.3 | Test progress | dashboard | Chamber correct |
| 14.4 | Test JSON output | agents | Parse works |
| 14.5 | Test SQLite KG | dashboard | Rich stats |
| 14.6 | Commit & Push | ALL | Push to GitHub |

---

## Success Criteria
After implementation:
- ✅ No import errors when running from dashboard
- ✅ Deduplication works correctly
- ✅ Accurate session counts (4 senators, 105 deputies)
- ✅ Progress shows correct chamber
- ✅ JSON output from agents displayed
- ✅ SQLite KG stats (entities, triples, relationship types)
- ✅ Dataview queries work in Obsidian
- ✅ Relationship visualization in dashboard
- ✅ File locking prevents corruption

---

## 📋 IMPLEMENTATION COMMANDS

```bash
# Phase 1: Test import fix
python3 scripts/agents/senat_agent.py --year 2026 --max 3

# Phase 2: Migrate vault
python3 scripts/migrate_vault.py

# Phase 3-5: Run dashboard
python3 scripts/dashboard.py

# Phase 14: Commit
git add -A && git commit -m "feat: Comprehensive StenoMD improvements"
git push
```

---

## 🔧 DEBUG PLAN - FIXES APPLIED

### Bugs Fixed (2026-04-22)

| Bug | Fix | Status |
|-----|-----|--------|
| requirements.txt missing beautifulsoup4 | Added beautifulsoup4>=4.12.0 | ✅ |
| stenomd_master.py wrong signature | Fixed to `run(years=[year], max_id=max_sessions)` | ✅ |
| Senator malformed filenames | Added name filtering, split multi-names | ✅ |
| Vault paths incorrect | Updated to `politicians/senators/`, `sessions/senate/` | ✅ |
| soup.title AttributeError | Added try/except | ✅ |

### Important Notes

| Issue | Workaround | Status |
|-------|-----------|--------|
| CDEP max_id=3 returns 0 | Use `max_id=100` or higher | ⚠️ Documented |
| Senate historical blocked | Use cached data only | ⚠️ Known |
| entities.json empty | Run `--merge` after scrape | ⚠️ Documented |

### Recommended Commands

```bash
# CDEP with full extraction
python3 scripts/agents/cdep_agent.py --years 2024,2025,2026 --max-id 100

# Senate for current sessions
python3 scripts/agents/senat_agent.py --year 2024 --max 10 --sync-vault

# Master controller
python3 scripts/stenomd_master.py --all --max 50 --sync-vault --merge
```

---

## 🎯 PROJECT OBJECTIVE

Build a Romanian Parliament Knowledge Brain (StenoMD) that:
1. Scrapes real stenogram data from Camera Deputatilor (cdep.ro) and Senate (senat.ro)
2. Extracts MPs, senators, laws, debates, and statements with full details
3. Populates an Obsidian vault with linked, searchable knowledge
4. Runs fully automatic daily updates AFTER full historical backfill

---

## 📊 CURRENT STATE

### Working Components
- ✅ CDEP Agent: Fully extracting speeches, 103 MPs, 394 statements
- ✅ Knowledge Graph: entities.json with v2.0 schema
- ✅ Vault: Synced with 88 MP notes

### Gaps Identified
- ❌ Senate Agent: Only extracting SUMMARY, not full speeches
- ❌ Chamber Separation: Not clearly separating Senate vs Deputies activity
- ❌ AI Summarization: Not yet integrated
- ❌ Parallel Scraping: Not yet implemented
- ❌ Historical Backfill: Not started

---

## 🔍 KEY DISCOVERIES

### senat.ro Structure (Critical) - SOLVED 2026-04-22
```
Page: https://www.senat.ro/StenoPag2.aspx
├── DUAL "Citește" BUTTON SYSTEM:
│   ├── gr2Rezultat$ctl##$Button1 → Summary grid results
│   └── Sumar2$ctl##$Button1 → Detailed stenogram (with GUID)
│
├── Content Location:
│   └── Table index 12 (tables[12]) contains stenogram content
│   └── Marker: "S T E N O G R A M A" (spaced text header)
│
├── Important Notes:
│   ├── Content is SUMMARY only (no full speeches)
│   ├── Full debates require longer sessions (2024-2025)
│   └── Pattern: "domnul NAME, vicepreședinte" for leadership
│
└── Pagination:
    └── __doPostBack('gr2Rezultat','Page$N') for N=2,3,4,...
```

### senat.ro EXTRACTION PROBLEMS & SOLUTIONS

**PROBLEM 1: Romanian Diacritics Not Matched**
```
Symptom: Regex patterns returned 0 matches even though content existed
Cause: Python regex [a-z] does NOT include Romanian diacritics (ăâîșțĂÂÎȘȚ)
Solution: Use explicit character class: [a-zăâîșțA-ZĂÂÎȘȚ]
```

**PROBLEM 2: Content Location Unknown**
```
Symptom: Content existed but couldn't find it in HTML
Cause: Was searching <td> elements individually
Solution: Use tables[12] (index 12 of tables list) for stenogram content
```

**PROBLEM 3: Case Sensitivity**
```
Symptom: "domnul Mihai" matched but "Domnul Mihai" didn't
Cause: Content uses lowercase "domnul" but pattern was uppercase
Solution: Use re.IGNORECASE flag OR match both cases explicitly
```

**PROBLEM 4: Indentation Errors After Edit**
```
Symptom: "unindent does not match any outer indentation level"
Cause: Mixed tabs and spaces after multiple edits
Solution: Re-indent entire file with consistent 4-space indentation
```

**PROBLEM 5: Date Format Not Working**
```
Symptom: Search returned 2026 dates instead of 2024 dates
Cause: Date format DD.MM.YYYY not recognized by form
Solution: Content search works, calendar buttons not needed
```

### Chamber Separation Required
```
vault/politicians/
├── senators/
│   └── [name].md  # Senate-only career
├── deputies/
│   └── [name].md  # Chamber-only career
└── dual/
    └── [name].md  # Served in BOTH - separate sections

vault/sessions/
├── senate/
│   └── [date].md
└── deputies/
    └── [date].md
```

---

## 📋 IMPLEMENTATION ROADMAP

### Phase A: Fix Senate Speech Extraction - COMPLETED 2026-04-22
| Step | Task | Status | Notes |
|------|------|--------|-------|
| A1 | Investigate Sumar2 navigation | ✅ | Content in Table 12 |
| A2 | Build redundancy logic | ✅ | Click both buttons |
| A3 | Extract individual speeches | ✅ | Romanian diacritics fixed |
| A4 | Generate AI summaries | ⏳ | Local Ollama or Groq API |
| A5 | Test with 10 sessions | ⏳ | Verify with 2024-2025 sessions |

### Phase B: Chamber-Separated Vault - COMPLETED 2026-04-22
| Step | Task | Status | Notes |
|------|------|--------|-------|
| B1 | Reorganize vault structure | ✅ | senate/deputies subfolders created |
| B2 | Unified politician profiles | ⏳ | Clear chamber sections |
| B3 | Session templates by chamber | ⏳ | Consistent format |
| B4 | Tags system | ⏳ | #senator, #deputy, #party-* |

### Phase C: Master Controller & Parallel Scraping - COMPLETED 2026-04-22
| Step | Task | Status | Notes |
|------|------|--------|-------|
| C1 | Create stenomd_master.py | ✅ | Working master controller |
| C2 | Implement checkpoint system | ✅ | checkpointer.json saves state |
| C3 | Parallel thread management | ⏳ | Concurrent scraping |
| C4 | Knowledge graph merge | ✅ | merge_knowledge_graph() |
| C3 | Parallel thread management | ⏳ | Concurrent scraping |
| C4 | Knowledge graph merge | ⏳ | Dedupe and correlate |

### Phase D: Historical Backfill - IN PROGRESS
| Step | Task | Status | Priority |
|------|------|--------|---------|
| D1 | Senate historical | ❌ | BLOCKED - only 2026 |
| D2 | CDEP 2024 cached | ✅ | 60 MPs synced |
| D3 | CDEP 2020-2023 | ⏳ | P1 |
| D4 | CDEP 2012-2020 | ⏳ | P2 |

### Phase E: Automation (Final Phase) - COMPLETED
| Step | Task | Status | Notes |
|------|------|--------|-------|
| E1 | GitHub Actions workflow | ✅ | Daily 06:00 UTC |
| E2 | Monitoring dashboard | ⏳ | Alerts on failure |
| E3 | Incremental sync | ✅ | Only new sessions |

---

## 📁 FILE STRUCTURE

```
/home/adrian/Desktop/NEDAILAB/StenoMD/
├── project-logs.md                    # THIS FILE - Current progress
├── STRATEGY.md                      # Comprehensive strategy
├── scripts/
│   ├── agents/
│   │   ├── cdep_agent.py          # ✅ Working - CDEP extraction
│   │   ├── senat_agent.py       # ⚠️ Needs fix - summary only
│   │   └── __init__.py
│   ├── stenomd_master.py        # ⏳ TO CREATE - Master controller
│   ├── sync_vault.py
│   ├── update_knowledge_graph.py
│   └── validate_knowledge_graph.py
├── data/
│   ├── cdep/                    # CDEP stenogram HTML files
│   └── senate/                  # Senate session data
├── vault/                       # Obsidian Brain Vault
│   ├── politicians/              # Politician profiles
│   │   ├── senators/            # Senate-only MPs
│   │   ├── deputies/           # Chamber MPs
│   │   └── dual/               # Served in both
│   ├── sessions/                # Session notes
│   │   ├── senate/             # Senate sessions
│   │   └── deputies/           # CDEP sessions
│   ├── laws/                   # Law notes
│   └── Index.md
├── knowledge_graph/
│   ├── entities.json           # v2.0 schema
│   └── checkpointer.json       # ⏳ TO CREATE - Backfill checkpoints
└── .github/workflows/
    └── daily-processor.yml    # ⏳ TO CONFIGURE
```

---

## 🔧 OBSIDIAN BRAIN OPTIMIZATION

### Dataview Fields (Inline)
```markdown
---
date: 2026-04-01
chamber: senate
participants:
  - Mihai Coteț
  - Vasile Blaga
laws_discussed:
  - 14/2026
  - 95/2026
speech_count: 47
word_count: 10820
---
```

### Tags System
```
#politician        #deputy         #senator
#party-PSD        #party-PNL      #party-AUR
#party-USR        #party-UDMR     #party-SOS
#chamber-senate   #chamber-deputies
#topic-economie   #topic-sanatate  #topic-justitie
#session-2026    #session-2024
#law-adopted     #law-rejected    #law-pending
```

### Wikilinks Structure
```
[[Mihai Coteț]]         → Politician profile
[[senate/2026-04-01]]  → Session note
[[Legea 14/2026]]      → Law note
[[Senat]]              → Chamber index
[[PSD]]                → Party index
```

---

## 🤖 AI SUMMARIZATION

### LLM Decision Matrix
| PC Spec | Recommendation | Notes |
|--------|--------------|-------|
| i5-7200U, 8GB RAM | Ollama + phi3-mini (2.8B) OR Groq API | Limited RAM, prefer cloud |
| No dedicated GPU | Groq API (free tier) | Safer option |
| HDD storage | Cloud API | Slow disk I/O |

### Prompt Template (Romanian)
```
Analizează discursul acestui senator.
Extrage:
1. Poziția (PRO/CONTRA/ABSTINUT/DISCUȚIE)
2. Subiectele principale
3. Argumente cheie
4. Sentimentul

Output JSON: {"position", "topics": [], "key_points": [], "sentiment"}
```

---

## 📌 CHECKPOINT SYSTEM

### Checkpoint Format
```json
{
  "last_updated": "2026-04-22 01:00",
  "cdep": {
    "current_year": 2024,
    "last_session_id": 57,
    "completed_sessions": ["2024_10", "2024_12", ...]
  },
  "senate": {
    "current_year": 2024,
    "last_date": "2026-04-01",
    "completed_dates": ["2026-04-01", "2026-03-30", ...]
  }
}
```

### Save Frequency
- **Every 10 sessions** during backfill
- After each successful scrape cycle
- On error (for resume point)

---

## ❓ RESUME CHECKLIST

If starting from scratch (new OpenCode instance):
1. Read this file (STRATEGY.md) first
2. Read project-logs.md for detailed history
3. Check checkpoint in `knowledge_graph/checkpointer.json`
4. Identify current phase from table above
5. Continue from last incomplete step

### Resume Points
| Phase | Resume From | Status |
|-------|-------------|--------|
| A (COMPLETED) | A1 | ✅ Solved - Table 12 + diacritics |
| B (COMPLETED) | B1 | ✅ Chamber separation done |
| C (COMPLETED) | C1 | ✅ Master controller done |
| D | D1: 2024-2026 backfill | ⏳ NEXT |
| E | E1: GitHub Actions setup | ⏳ |

### Critical Patterns for senat.ro
```
# Romanian diacritics - MUST include in regex:
[a-zăâîșțA-ZĂÂÎȘȚ]

# Content extraction:
tables = soup.find_all('table')
table = tables[12]  # Index 12
content = table.get_text(separator=' ', strip=True)

# Name patterns:
r'domnul\s+([A-ZĂÂÎȘȚ][a-z��âîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)'

# Button names:
gr2Rezultat$ctl##$Button1  # Main Citește
Sumar2$ctl##$sumar_ID       # Summary with GUID
```

### Critical Patterns for cdep.ro
```
# MP name extraction:
<font color="#0000FF">Domnul NAME</font>
<font color="#0000FF">Doamna NAME</font>

# Pattern:
r'<font color="#0000FF">\s*(?:Domnul|Doamna)\s+([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+){1,3})'

# URL format:
/pls/steno/steno{year}.stenograma_scris?idl=1&idm=1&ids={id}&prn=1

# Calendar:
/pls/steno/steno{year}.Calendar?cam=1&an={year}
```

---

## ✅ COMPLETED TASKS LOG

| Date | Task | Result |
|------|------|--------|
| 2026-04-21 | Project initialization | ✅ |
| 2026-04-21 | CDEP website analysis | ✅ |
| 2026-04-21 | CDEP agent development | ✅ |
| 2026-04-21 | Real data extraction | ✅ 11 MPs |
| 2026-04-22 | Enhanced CDEP agent | ✅ 103 MPs, 394 statements |
| 2026-04-22 | Senate website analysis | ✅ |
| 2026-04-22 | Senate agent basic | ✅ Summary extraction |
| 2026-04-22 | Senate agent fix | ✅ 41 laws, 3 senators |
| 2026-04-22 | Strategy documented | ✅ This file |
| 2026-04-22 | Romanian diacritics fixed | ✅ Key discovery |

---

## 🚀 NEXT ACTIONS (Immediate)

1. ⏳ **B1**: Reorganize vault structure (senate/deputies subfolders)
2. ⏳ **Test**: Verify with 2024-2025 sessions (longer debates)
3. ⏳ **B2**: Unified politician profiles
4. ⏳ **C1**: Create stenomd_master.py controller
5. ⏳ **D1**: Begin 2024-2026 backfill

---

*End of Strategy Document*
*Next update: After Phase A completion*