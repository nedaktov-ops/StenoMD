# STENOMD Project Timeline
## Comprehensive Implementation Plan

**Created**: 2026-04-24  
**Last Updated**: 2026-04-25  
**Status**: IN PROGRESS

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

## DATA STATUS (2026-04-25)

| Metric | Current | Target |
|--------|---------|--------|
| CDEP Sessions | 22 | 200+ |
| Senate Sessions | 19 | 30+ |
| Total Sessions | 41 | 230+ |
| MPs (Deputies) | 105 | 300+ |
| Senators | 7 | 20+ |
| Total MPs | 112 | 320+ |
| Statements (extracted) | 0/session | 50+/session |
| Triple Extractions | 760 | 2000+ |
| Memory Actions | 13 | 100+ |
| Ollama Tasks | Disabled | Specific only |

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

*LastUpdated: 2026-04-25*
*Next Action: Run Phase 1 - CDEP scale-up with max_id=200*