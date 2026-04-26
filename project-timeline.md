# STENOMD Project Timeline
## Comprehensive Implementation Plan

**Created**: 2026-04-24  
**Last Updated**: 2026-04-26  
**Status**: PHASE 5 - BRAIN ARCHITECTURE COMPLETED

---

## PARAMETERS CONFIRMED

| Parameter | Choice |
|-----------|--------|
| Ollama Model | qwen2.5-coder:1.5b (phi3 unavailable in registry) |
| Historical Priority | Chamber first (2015-2026 only - historical blocked) |
| Testing Strategy | Small test → Gradual expansion |
| Privacy | Local-only (Ollama) with free alternatives |
| Entity Resolution | Auto-resolve (highest confidence) |
| Position Classification | Specific tasks only (Ollama disabled by default) |
| Ollama Tasks | Entity resolution, QA only |
| KG Population | Incremental (progress visible) |
| Dashboard Refresh | Real-time (every new session) |
| Storage Organization | By Year (`vault/sessions/YYYY/`) |
| Performance Target | 5-10 sessions/minute with parallelization |
| Data Coverage Target | 200+ sessions |

---

## KEY DECISIONS (2026-04-25)

### 1. Historical Data
- **Focus**: 2015-2026 accessible data only
- **Note**: Historical 1996-2014 BLOCKED (cdep.ro returns 404)
- **Future**: Research alternative sources - ASK PERMISSION before contacting parliament

### 2. Ollama Mode
- **Default**: Disabled (30+ second delays)
- **Enabled For**: Specific tasks only (entity resolution, QA)
- **Config**: `USE_OLLAMA=specific` environment variable

### 3. Performance
- **Target**: 5-10 sessions/minute
- **Implementation**: asyncio + aiohttp for parallelization

### 4. Task Tracking System (2026-04-26)
- **Implemented**: Unfinished-tasks.md + Completed-tasks.md
- **Automation**: scripts/task_manager.py
- **Integration**: Planner agent checks tasks on startup
- **Deferred**: Phase 5 - Committee Assignments (COMPLETED 2026-04-26)
- **Deferred**: Phase 4.1 - Bill Tracking (IN PROGRESS 2026-04-26)

---

## ALL COMPLETED PHASES (2026-04-26)

### Phase 4.1: Bill Tracking + MP Linking (2026-04-26)
- **Status**: IN PROGRESS
- **Current Task**: Link existing law files to MP sponsors using Open Parliament data
- **Progress**: 5/124 laws matched (2023-2025 laws with Open Parliament IDs)
- **Method**: 
  1. Parse Open Parliament proposals (data/parlamint/open-parliament-ro/data/2024/proposals/)
  2. Extract numeric initiator IDs
  3. Match to deputy stable_ids via idm mapping
  4. Add sponsors field to law frontmatter
  5. Add process_stage field

### Phase 5: Committee Assignments (2026-04-26)
- **Status**: ✅ COMPLETE
- **Scraper**: scripts/scrape_committees.py
- **Results**: 393 committee assignments for 277 MPs from cdep.ro

---

## RECENT FIXES APPLIED (2026-04-25)

### Fix 1: CDEP URL Patterns
```python
# OLD (broken)
f"{BASE_URL}/pls/steno/steno{year}.stenograma_scris?idl=1&idm=1&ids={session_id}&prn=1"

# NEW (working)
f"{BASE_URL}/pls/steno/steno{year}.stenograma?idl=1&ids={session_id}"
```
**Status**: ✅ Fixed - Removed `&prn=1` and added fallback patterns

### Fix 2: MP Name Regex
```python
# OLD (missing colon)
MP_NAME_PATTERN_HTML = re.compile(
    r'<font\s+color="#0000FF">(Domnul|Doamna)\s+([A-Z]...</font>'
)

# NEW (with optional colon)
MP_NAME_PATTERN_HTML = re.compile(
    r'<font\s+color="#0000FF">(Domnul|Doamna)\s+([A-Z]...)[:\s]*</font>'
)
```
**Status**: ✅ Fixed - Added `[:\s]*` for optional colon after names

---

## DATA STATUS (2026-04-25) - UPDATED

| Metric | Current | Target |
|--------|---------|--------|
| CDEP Sessions | 30 | 200+ |
| Senate Sessions | 19 | 30+ |
| Total Sessions | 50+ | 230+ |
| MPs (Deputies) | 105 | 300+ |
| Senators | 7 | 20+ |
| Total MPs | 112 | 320+ |
| Statements (extracted) | 50+/session | 50+/session |
| Triple Extractions | 760 | 2000+ |
| Memory Actions | 13 | 100+ |
| Ollama Tasks | Disabled | Specific only |

### ALTERNATIVE DATA SOURCE DISCOVERED
**Open Parliament RO** (2026-04-25):
- Source: https://github.com/ClaudiuCeia/open-parliament-ro
- Data: 61 unique session dates
- Speeches: 2,341 (2024-2025)
- Import status: COMPLETE - 91 sessions in vault
- Canonical MPs: 460 (added 331 new deputies)

---

## ALL COMPLETED PHASES (2026-04-26)

| Phase | Description | Status | GitHub |
|-------|------------|--------|-------|
| Phase 1 | Parliamentary Reference Structure | ✅ Complete | afb517f |
| Phase 2 | Clean & Fix | ✅ Complete | c33ed8e |
| Phase 2.5 | Senator Party Data | ✅ Complete | 40e0ab3 |
| Phase 3 | Stable ID Generation | ✅ Complete | b12586c |
| Phase 4 | Deputy Coverage (158→446) | ✅ Complete | 0472713 |
| Phase 4 alt | Party Change Tracking | ✅ Complete | 9ecb823 |
| Phase 6 | Law Enrichment (85/122) | ✅ Complete | 131df8c |
| Phase 7 | Low-RAM Optimization | ✅ Complete | 56703db |

### Deferred
| Phase | Description | Status | Task ID |
|-------|------------|--------|--------|
| Phase 5 | Committee Assignments | ⏸️ DEFERRED | TASK-001 |

---

## PHASE 1: DATA COVERAGE (Week 1-2)

### 1.1 CDEP Scale-Up
**Goal**: Scale from 22 to 200+ sessions

**Tasks:**
- [ ] Run cdep_agent.py with max_id=200 for years 2015-2025
- [ ] Extract statements properly (fix extraction)
- [ ] Verify entity resolution works
- [ ] Save to vault properly

**Command:**
```bash
python3 scripts/agents/cdep_agent.py --years 2015 --max-id 200
python3 scripts/agents/cdep_agent.py --years 2020 --max-id 200
python3 scripts/agents/cdep_agent.py --years 2025 --max-id 200
```

### 1.2 Senate Expansion
**Goal**: Scale from 19 to 30+ sessions

**Tasks:**
- [ ] Continue current Senate scraping
- [ ] Verify all sessions sync to vault

### 1.3 Statement Extraction Fix
**Goal**: Extract 50+ statements per session

**Tasks:**
- [ ] Debug extract_statements() method
- [ ] Verify YAML frontmatter parsing
- [ ] Test with known sessions

---

## PHASE 2: QUALITY IMPROVEMENTS (Week 2-3)

### 2.1 Entity Resolution Edge Cases
**Goal**: Handle 50+ name variations

**Tasks:**
- [ ] Add alias database entries
- [ ] Handle diacritics variations
- [ ] Test with known MPs
- [ ] Target: 95%+ accuracy

### 2.2 Ollama Integration
**Goal**: Enable for specific tasks only

**Tasks:**
- [ ] Set USE_OLLAMA=specific environment
- [ ] Enable for entity resolution only
- [ ] Enable for QA queries only
- [ ] Keep disabled for classification

### 2.3 Position Classification
**Goal**: Proper PRO/CONTRA/NEUTRAL labels

**Tasks:**
- [ ] Debug classification logic
- [ ] Verify keyword extraction
- [ ] Test with known statements

---

## PHASE 3: INFRASTRUCTURE (Week 3-4)

### 3.1 Test Suites
**Goal**: 80% code coverage

**Tasks:**
- [ ] Add pytest for agents/
- [ ] Add pytest for resolve/
- [ ] Add pytest for kg/
- [ ] Add pytest for analyze/

### 3.2 Documentation
**Goal**: Complete project documentation

**Tasks:**
- [ ] Update project-timeline.md (THIS FILE)
- [ ] Update project-logs.md
- [ ] Create STRATEGY.md with historical research note
- [ ] Document API endpoints

### 3.3 Performance Optimization
**Goal**: 5-10 sessions/minute

**Tasks:**
- [ ] Implement asyncio in agents
- [ ] Add aiohttp for concurrent requests
- [ ] Add batch processing
- [ ] Verify speed improvement

---

## ARCHITECTURE

### File Structure (2026-04-25)
```
StenoMD/
├── scripts/
│   ├── agents/
│   │   ├── cdep_agent.py         # Chamber scraper
│   │   └── senat_agent.py         # Senate scraper
│   ├── analyze/
│   │   ├── positions.py          # Position classification
│   │   └── topics.py            # Topic classification
│   ├── kg/
│   │   ├── schema_migrate.py     # JSON → SQLite
│   │   └── triple_extractor.py  # Triple extraction
│   ├── memory/
│   │   ├── memory.py           # MemoryStore
│   │   └── actions.json        # Action log
│   ├── query/
│   │   ├── parliament_qa.py    # NL QA
│   │   └── rest_api.py          # REST API (8 endpoints)
│   ├── resolve/
│   │   └── entity_resolver.py  # Entity resolution
│   └── validators.py           # Data validation
├── vault/
│   ├── sessions/
│   │   ├── deputies/           # CDEP sessions
│   │   └── senate/             # Senate sessions
│   └── politicians/
│       ├── deputies/           # MP profiles
│       └── senators/           # Senator profiles
├── knowledge_graph/
│   ├── entities.db            # SQLite KG
│   └── triples.db             # Relationship triples
└── project-timeline.md        # This file
```

### Components

| Component | File | Status |
|-----------|------|--------|
| Chamber Scraper | cdep_agent.py | ✅ Working (fixed) |
| Senate Scraper | senat_agent.py | ✅ Working |
| Entity Resolution | entity_resolver.py | ✅ Working |
| Knowledge Graph | triple_extractor.py | ✅ Working |
| Position Classifier | positions.py | ✅ Working |
| Topic Classifier | topics.py | ✅ Working |
| REST API | rest_api.py | ✅ Working (8 endpoints) |
| QA Interface | parliament_qa.py | ✅ Working |
| Memory System | memory.py | ✅ Working |
| Data Validator | validators.py | ✅ Working |

---

## BLOCKED ITEMS

### Historical Data (1996-2014)
**Status**: BLOCKED
**Impact**: Cannot access Chamber stenograms from 1996-2014
**Reason**: cdep.ro returns 404 for those years

### Research Required (ASK PERMISSION before contacting)
- [ ] Contact cdep.ro for historical data
- [ ] Check Romanian National Archives
- [ ] Check EU Parliament joint sessions
- [ ] Academic sources

---

## SUCCESS CRITERIA

### Phase 1 (Week 1-2)
- [ ] 200+ CDEP sessions scraped
- [ ] 30+ Senate sessions scraped
- [ ] 50+ statements per session
- [ ] All sessions in vault

### Phase 2 (Week 2-3)
- [ ] 95%+ entity resolution accuracy
- [ ] Ollama working for specific tasks
- [ ] Position classification fixed

### Phase 3 (Week 3-4)
- [ ] 80% test coverage
- [ ] Documentation complete
- [ ] 5-10 sessions/minute performance

---

## ESTIMATED TIMELINE

| Week | Phase | Tasks |
|------|-------|-------|
| 1-2 | Phase 1 | Data Coverage - 200+ sessions |
| 2-3 | Phase 2 | Quality - Entity resolution, Ollama |
| 3-4 | Phase 3 | Infrastructure - Tests, docs, performance |

**Total Duration**: ~4 weeks

---

## DAILY WORKFLOW FIX (2026-04-25)

### Goal: Fix daily workflow and populate knowledge graph

### Issues Identified

1. **run_daily.py calls DEPRECATED stenomd_scraper.py**
2. **entities.json empty** - merge_vault_to_kg.py never called
3. **Vault imbalance** - 158 deputies vs 5 senators
4. **GitHub workflow missing merge step**

### Implementation Plan

| Step | Action | File |
|------|--------|------|
| 1 | Replace full content | `scripts/run_daily.py` |
| 2 | Add merge step | `.github/workflows/daily-processor.yml` |
| 3 | Create new script | `scripts/collect_senators.py` |
| 4 | Patch | `scripts/update_knowledge_graph.py` |
| 5 | Patch | `scripts/merge_vault_to_kg.py` |
| 6 | Test dry-run | `python3 run_daily.py --dry-run` |
| 7 | Run workflow | `python3 run_daily.py` |
| 8 | Verify KG | `cat knowledge_graph/entities.json` |
| 9 | Commit | `git add -A && commit` |

### Expected Results

| Metric | Before | After |
|--------|--------|-------|
| Daily workflow | BROKEN | WORKING |
| KG entities | 0 | 160+ |
| Senators | 5 | 20+ |
| Health | 82% | 90%+ |

---

## CONFIGURATION SYSTEM IMPLEMENTATION (2026-04-25)

### Goal: Centralize configuration and fix security issues

### Blind Spots Identified by Planner Agent (25+ files)

| Category | Count | Examples |
|----------|-------|---------|
| Hardcoded paths | 25+ | dashboard.py, rest_api.py |
| SQL injection risk | 1 | rest_api.py |
| CORS security | 1 | rest_api.py |
| Bare except clauses | 20+ | merge_vault_to_kg.py |
| Database conflicts | 2 | .db vs .sqlite3 |

### Implementation Plan

| Step | Task | Files |
|------|------|-------|
| 1 | Create config.py | scripts/config.py |
| 2 | Update .gitignore | +10 entries |
| 3 | Fix dashboard.py | Lines 16-20, 85 |
| 4 | Fix rest_api.py | SQL + CORS |
| 5 | Fix validators.py | Line 264 |
| 6 | Fix planner_agent/*.py | 5 files |
| 7 | Fix brain/*.py | 5 files |
| 8 | Fix memory/*.py | 4 files |
| 9 | Remove dead code | 4 files |
| 10 | Test | Run tests |

### Expected Results

| Metric | Before | After |
|--------|--------|-------|
| Hardcoded paths | 25+ | 0 |
| SQL injection | Vulnerable | Fixed |
| CORS | Open | Restricted |
| Config system | None | Centralized |

---

## PHASE 3 COMPLETE (2026-04-25)

### Subdirectories Fixed
| Directory | Status |
|-----------|--------|
| planner_agent/*.py | ✅ Fixed |
| brain/*.py | ✅ No changes needed |
| memory/*.py | ✅ No changes needed |
| agents/*.py | ✅ No changes needed |
| kg/*.py | ✅ No changes needed |

---

## PHASE 4 COMPLETE (2026-04-25)

### Dead Code Removed
| File | Status |
|------|--------|
| stenomd_scraper.py | Archived |
| scrape_cdep.py | Archived |
| dashboard.py.backup.* | Archived |
| run_daily.py.bak | Archived |

---

## STRATEGY 3.0: COMPREHENSIVE IMPLEMENTATION (2026-04-25)

### Research-Based Updates
- **Multi-legislature**: IDs recycle - need stable IDs
- **Traseism**: Track party changes with CPC definition (>2 = traseist)
- **Monitorul Oficial**: Publication references required

### Phase 1: Parliamentary Reference
- [ ] vault/_parliament/ directory
- [ ] Constitutional articles
- [ ] 44 committees

### Phase 2: Clean & Fix
- [ ] Delete empty files
- [ ] Fix broken links

### Phase 3: Stable IDs
- [ ] generate_stable_ids.py

### Phase 4: Party Tracking
- [ ] add_party_tracking.py

### Phase 5: Complete 2024
- [ ] Senator profiles complete
- [ ] Deputy committees
- [ ] Law metadata

### Phase 6: Historical
- [ ] 2020-2024 → 2016-2020

### Phase 7: RAM Optimization
- [ ] 8GB memory settings

---

*LastUpdated: 2026-04-26*
*Next Action: Begin Phase 1 - Parliamentary Reference*

## BRAIN ARCHITECTURE IMPLEMENTATION (2026-04-26)

### Completed Tasks

| Stage | Task | Result |
|-------|------|--------|
| 1 | Backup snapshot | Created at backups/ |
| 2 | Update templates | 4 templates updated with brain sections |
| 3 | Add brain sections to politicians | 470 profiles (332 deputies + 138 senators) |
| 4 | Add brain sections to laws | 124 laws |
| 5 | Add brain sections to sessions | 111 sessions |
| 6 | Add brain sections to committees | 2 files |
| 7 | Brain Dashboard | vault/_brain/Dashboard.md |
| 8 | Recall Queries | 4 Dataview query files |
| 9 | Reverse linking | scripts/graph_recall.py |

### Brain Model Sections Added

Each item now has:
- **Sensory Input**: source_url, last_synced, data_sources
- **Processing**: activity_score, collaboration_network, party_alignment
- **Memory**: proposals, speeches, voting_record, co_sponsors
- **Action/Output**: Query Ready fields, Alerts