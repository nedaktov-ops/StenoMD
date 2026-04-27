# StenoMD Architecture

**Romanian Parliament Knowledge Brain**  
**Version:** 3.0 (Complete Overhaul)  
**Status:** OPERATIONAL - Production Ready  
**Health Score:** 96/100 (Grade A)

---

## 1. Project Overview

**Purpose:** Transform raw Romanian parliamentary stenograms (transcripts) from cdep.ro and senat.ro into a comprehensive, searchable knowledge brain integrated with Obsidian.

**What It Does:**
1. Scrapes parliamentary session transcripts from Chamber of Deputies (cdep.ro) and Senate (senat.ro)
2. Extracts MP names, statements, party affiliations, laws discussed
3. Creates structured markdown in Obsidian vault
4. Builds knowledge graph with temporal entity relationships
5. Provides REST API and AI-powered queries

**Target Users:** Researchers, journalists, analysts, and AI assistants who need to query Romanian parliamentary proceedings.

---

## 2. Directory Structure

```
StenoMD/
├── scripts/                    # Core automation (50+ Python files)
│   ├── agents/               # Scrapers
│   │   ├── cdep_agent.py    # Chamber of Deputies scraper
│   │   └── senat_agent.py   # Senate scraper
│   ├── kg/                 # Knowledge graph operations
│   ├── resolve/            # Entity resolution
│   ├── analyze/            # Position/topic classification
│   ├── query/             # REST API (FastAPI), QA interface
│   ├── memory/            # Memory store, action logs
│   ├── config.py          # Centralized configuration
│   ├── run_daily.py       # Daily update pipeline
│   ├── stenomd_master.py  # Master controller
│   ├── merge_vault_to_kg.py  # Vault → KG sync
│   ├── sync_vault.py     # Vault synchronization
│   ├── dashboard.py     # Real-time monitoring
│   └── validators.py   # Data validation
│
├── vault/                     # Obsidian vault (markdown)
│   ├── politicians/          # MP profiles
│   │   ├── deputies/       # 463 canonical deputies
│   │   └── senators/       # 138 senators
│   ├── sessions/           # Session records
│   │   ├── deputies/       # CDEP sessions (200+)
│   │   └── senate/        # Senate sessions (50+)
│   ├── laws/             # Legislation (124 laws)
│   ├── committees/       # Committee info (44 committees)
│   ├── _brain/          # AI brain sections
│   ├── _templates/       # Reusable templates
│   ├── _index/          # Dataview indices
│   ├── dashboards/      # Dashboard queries
│   └── Welcome.md        # Entry point
│
├── data/                     # Raw data and JSON outputs
│   ├── cdep/            # Cached HTML stenograms
│   ├── stenogram_*.html   # Sample transcripts
│   ├── deputies_2024.json
│   ├── senators_2024_party.json
│   ├── law_proposals_enhanced.json
│   ├── party_abbreviations.json
│   └── parlamint/       # Open Parliament RO data
│
├── knowledge_graph/           # MemPalace knowledge system
│   ├── entities.json     # Unified entity store
│   ├── triples.db      # SQLite KG for temporal triples
│   ├── benchmarks/    # Reproducible benchmarks
│   ├── examples/      # MCP setup, mining examples
│   ├── hooks/        # Auto-save hooks
│   └── tests/        # Test suite
│
├── archive/                   # Archived obsolete scripts
├── backups/                  # Backup snapshots
├── graphify-out/            # Graphify analysis output
├── Graphify/               # Graphify integration
├── GraphifyStenoMD/        # Project-specific Graphify
├── PSBRO/                 # Related project
├── .github/               # GitHub workflows
├── requirements.txt         # Python dependencies
├── STRATEGY.md            # Implementation strategy
├── project-timeline.md     # Development roadmap
├── OBSIDIAN_SETUP.md      # Obsidian usage guide
└── CONFIG_SYSTEM_DESIGN.md  # Configuration design

```

---

## 3. Core Components

### 3.1 Scraper Agents

**`scripts/agents/cdep_agent.py`** - Chamber of Deputies
- Fetches session calendar, iterates session IDs
- Extracts: MP names (with Romanian diacritics), party affiliations, statements, laws discussed
- Features: caching, retry with backoff, checkpoint resume, year-range support
- Output: Raw HTML → parsed sessions → markdown files

**`scripts/agents/senat_agent.py`** - Senate
- Similar to cdep_agent but for senat.ro
- Extracts senator data separately

### 3.2 Knowledge Graph (MemPalace-based)

**Architecture:** "The Palace" system with:
- **Wings:** Projects, persons, topics
- **Rooms:** Specific subjects within wings
- **Halls:** Memory types (facts, events, discoveries, preferences, advice)
- **Closets:** Summaries pointing to original content
- **Drawers:** Raw verbatim files

**Files:**
- `knowledge_graph/entities.json` - Unified entity store (persons, sessions, laws)
- `knowledge_graph/triples.db` - SQLite temporal triples (subject, predicate, object, valid_from, valid_to)

**Features:**
- Temporal validity windows (query "as of" a date)
- Semantic search via ChromaDB (96.6% LongMemEval recall)
- 19 MCP tools for AI integration
- AAAK dialect for compression (experimental)

### 3.3 Obsidian Vault

**Structure:**
```
politicians/
├── deputies/Vasile-Citea.md    # Individual MP profiles
├── deputies/Alexandra-Hu.md
├── senators/
│   └── [senator name].md
sessions/
├── deputies/2024/                 # Organized by year
│   └── 2024-10-15.md
├── senate/
laws/
├── Index.md             # Law index
└── 448-2006.md       # Law files
committees/
├── Index.md
└── buget-finte.md     # Committee files
_brain/                # AI brain sections
├── Dashboard.md
├── queries/
├── Sensory-Input/
├── Processing/
├── Memory/
└── Action-Output/
```

**Auto-Sync:** When scraping completes, `sync_vault.py` copies new data to vault.

### 3.4 Enrichment Pipeline

| Script | Purpose |
|--------|---------|
| `fix_deputy_data_from_op.py` | Match to Open Parliament RO (314 fixed) |
| `scrape_committees.py` | Committee assignments (275 MPs) |
| `add_party_tracking.py` | Traseism monitoring |
| `generate_stable_ids.py` | Hash-based stable IDs |
| `add_brain_sections.py` | Add AI fields to profiles |
| `link_proposal_sponsors.py` | Link laws to sponsors |

**AI Fields Added:**
- `ai_friendly_name` - Searchable name
- `search_aliases` - Alternative names
- `activity_score` - Numeric activity rating
- `collaboration_network` - Co-sponsor relations

### 3.5 REST API

**File:** `scripts/query/rest_api.py`

**Endpoints:**
```
GET  /api/status              - Health check
GET  /api/mps                 - List all MPs
GET  /api/mps/{name}          - MP details
GET  /api/sessions           - List sessions
GET  /api/sessions/{date}   - Session details
GET  /api/laws             - List laws
GET  /api/laws/{number}    - Law details
POST /api/query             - Natural language query
```

**Run:** `uvicorn scripts.query.rest_api:app --reload`

### 3.6 Dashboard

**File:** `scripts/dashboard.py`

**Metrics:**
- Health score (96/100)
- Data coverage (sessions, MPs, laws)
- Connectivity (cross-references)
- Placeholder count
- Last updated timestamp

---

## 4. Data Model

### 4.1 Person (MP)

```yaml
---
id: "mp_001"
idm: 1803                    # cdep.ro ID
stable_id: "v-cite-1965-bz"   # hash(name+birth_year+birthplace)
name: "Vasile Citea"
ai_friendly_name: "Vasile Citea"
chamber: "deputies"
party: "PSD"
party_full: "Partidul Social Democrat"
constituency: "Teleorman"
committees:
  - "Comisia pentru buget"
speeches_count: 47
laws_proposed: 12
photo_url: "https://www.cdep.ro/pls/steno/..."
url: "https://www.cdep.ro/pls/steno/..."
sponsorships:
  - law_448_2006
activity_score: 85
collaboration_network:
  - "Boris Volosatii"
search_aliases:
  - "Vasile"
  - "Citea Vasile"
---
```

### 4.2 Session

```yaml
---
id: "2024-10-15"
date: "2024-10-15"
title: "Stenograma sedintei Camerei Deputatilor"
chamber: "deputies"
url: "https://www.cdep.ro/pls/steno/..."
participants:
  - "Vasile Citea"
  - "Alexandra Hu"
laws_discussed:
  - "448/2006"
  - "212/2024"
statements_extracted: 47
source: "cdep.ro"
last_synced: "2026-04-27"
---
```

### 4.3 Law

```yaml
---
id: "law_448_2006"
number: "448/2006"
title: "Legea protectiei drepturilor"
process_stage: "promulgat"
chamber: "Camera Deputatilor"
sponsors:
  - "Vasile Citea"
  - "Boris Volosatii"
date_proposed: "2006-03-15"
date_promulgated: "2006-06-20"
monitorul_oficial: "Parte I, nr. 515"
source: "cdep.ro"
---
```

### 4.4 Temporal Triple

```sql
-- SQLite table in triples.db
CREATE TABLE triples (
    subject TEXT,
    predicate TEXT,
    object TEXT,
    valid_from DATE,
    valid_to DATE,
    source TEXT,
    confidence REAL DEFAULT 1.0
);

-- Example entries
INSERT INTO triples VALUES ('Vasile Citea', 'member_of', 'PSD', '2020-12-21', NULL, 'cdep.ro', 1.0);
INSERT INTO triples VALUES ('Vasile Citea', 'elected_in', 'Teleorman', '2020-12-21', NULL, 'cdep.ro', 1.0);
```

---

## 5. Configuration

### 5.1 Centralized Config

**File:** `scripts/config.py`

**Environment Variables:**
```bash
STENOMD_DIR           # Project root (default: auto-detect)
STENOMD_ALLOWED_ORIGIN # CORS origin (default: localhost)
STENOMD_MAX_ID       # Max session ID (default: 200)
STENOMD_CACHE_TTL    # Cache TTL seconds (default: 3600)
STENOMD_LOG_LEVEL    # Logging (default: INFO)
STENOMD_DEBUG       # Debug mode (default: false)
STENOMD_OLLAMA_MODEL # Ollama model (default: qwen2.5-coder:1.5b)
```

**Usage in scripts:**
```python
from config import get_config
config = get_config()
VAULT_DIR = config.VAULT_DIR
KG_DIR = config.KG_DIR
```

### 5.2 Important Paths

| Variable | Default Path |
|----------|-------------|
| `PROJECT_ROOT` | `/home/adrian/Desktop/NEDAILAB/StenoMD` |
| `VAULT_DIR` | `PROJECT_ROOT/vault` |
| `KG_DIR` | `PROJECT_ROOT/knowledge_graph` |
| `DATA_DIR` | `PROJECT_ROOT/data` |
| `ENTITIES_FILE` | `KG_DIR/entities.json` |
| `TRIPLES_DB` | `KG_DIR/triples.db` |

---

## 6. Workflows

### 6.1 Daily Update Pipeline

**File:** `scripts/run_daily.py`

**Flow:**
```
1. Run cdep_agent.py (2024-2026, 50 sessions, sync-vault)
2. Run senat_agent.py (2026, 30 sessions, sync-vault)
3. Run merge_vault_to_kg.py (populate entities.json)
4. Run validate_knowledge_graph.py (compute health)
5. Run stenomd_master.py --status (show stats)
```

**Command:**
```bash
cd /home/adrian/Desktop/NEDAILAB/StenoMD
python3 scripts/run_daily.py
# or dry-run:
python3 scripts/run_daily.py --dry-run
```

### 6.2 Scraping Flow

**cdep_agent.py:**
```
1. Fetch calendar page for year
2. Extract session IDs and dates
3. For each session ID:
   a. Fetch HTML from cdep.ro/pls/steno/...
   b. Parse HTML (BeautifulSoup)
   c. Extract MP names with regex
   d. Extract statements between MP names
   e. Extract law numbers discussed
   f. Create/update session markdown
   g. Create/update MP profile markdown
4. Save to vault
5. Update checkpoint
```

### 6.3 Knowledge Graph Sync

**merge_vault_to_kg.py:**
```
1. Read all vault markdown files
2. Parse YAML frontmatter
3. Extract persons, sessions, laws
4. Load existing entities.json
5. Merge with new data
6. Save updated entities.json
```

---

## 7. Current Status

### 7.1 Metrics (April 27, 2026)

| Metric | Value |
|--------|-------|
| **Overall Health Score** | 96/100 (A) |
| **Data Integrity** | 100/100 |
| **CDEP Sessions** | 200+ |
| **Senate Sessions** | 50+ |
| **Deputies (canonical)** | 463 |
| **Senators** | 138 |
| **Laws** | 124 |
| **Committee Assignments** | 393 (275 MPs) |
| **Placeholders** | 0 |
| **Duplicate Files** | 0 |

### 7.2 Known Issues (Resolved)

- Historical data 1996-2014 blocked (cdep.ro returns 404)
- Some URL patterns fixed (removed `prn=1`)
- MP name regex fixed (added optional colon)
- All placeholders replaced with real data
- Party/constituency fields normalized

---

## 8. Key Features

### 8.1 Multi-Legislature Tracking
- IDs recycle each legislature
- Solution: Stable IDs (hash of name+birth_year+birthplace)
- Links same person across legislatures

### 8.2 Party Change Tracking (Traseism)
- Legal for parliamentarians
- CPC definition: >2 party changes = traseist
- Track: `original_elected_party` vs `current_party`

### 8.3 Legislative Process
```
INITIATION → COMMITTEE → PLENARY → SECOND CHAMBER → PROMULGATION → MONITORUL OFICIAL → EFFECT
```
- Monitorul Oficial Parts: I (laws), II (stenograms), III-VII (announcements)

### 8.4 Low-RAM Optimization
- Target: 8GB systems
- Ollama disabled by default (30+ second delays)
- Enabled for specific tasks only (entity resolution, QA)
- Model: qwen2.5-coder:1.5b (not phi3)

---

## 9. Technical Stack

- **Python 3.9+**
- **FastAPI** + **Uvicorn** - REST API
- **BeautifulSoup4** + **lxml** - HTML parsing
- **ChromaDB** - Vector storage, semantic search
- **SQLite** - Triples, metadata
- **PyYAML** - Frontmatter parsing
- **Requests** - HTTP client
- **Obsidian** - Vault interface (run from command line)

---

## 10. Usage Commands

### 10.1 Daily Workflow
```bash
# Run daily update
cd /home/adrian/Desktop/NEDAILAB/StenoMD
python3 scripts/run_daily.py

# Open vault in Obsidian
/opt/Obsidian/obsidian /home/adrian/Desktop/NEDAILAB/StenoMD/vault

# View status
python3 scripts/stenomd_master.py --status
```

### 10.2 API
```bash
# Start REST API
cd /home/adrian/Desktop/NEDAILAB/StenoMD
uvicorn scripts.query.rest_api:app --reload

# Test endpoint
curl http://localhost:8000/api/status
```

### 10.3 Manual Scraping
```bash
# Chamber only
python3 scripts/agents/cdep_agent.py --years 2024,2025 --max-id 50 --sync-vault

# Senate only
python3 scripts/agents/senat_agent.py --year 2026 --max 30 --sync-vault

# Parallel
python3 scripts/stenomd_master.py --parallel --years 2024,2025 --workers 4
```

### 10.4 Knowledge Graph
```bash
# Merge vault to KG
python3 scripts/merge_vault_to_kg.py

# Validate
python3 scripts/validate_knowledge_graph.py

# Query entities
python3 scripts/query/parliament_qa.py
```

---

## 11. Important Files Reference

| File | Purpose |
|------|---------|
| `scripts/run_daily.py` | Daily update pipeline |
| `scripts/stenomd_master.py` | Master controller |
| `scripts/agents/cdep_agent.py` | Chamber scraper |
| `scripts/agents/senat_agent.py` | Senate scraper |
| `scripts/merge_vault_to_kg.py` | Vault → KG sync |
| `scripts/sync_vault.py` | Vault synchronization |
| `scripts/config.py` | Centralized config |
| `scripts/dashboard.py` | Real-time metrics |
| `scripts/validators.py` | Data validation |
| `scripts/query/rest_api.py` | REST API |
| `OBSIDIAN_SETUP.md` | Vault usage guide |
| `STRATEGY.md` | Implementation strategy |
| `project-timeline.md` | Development roadmap |

---

## 12. Dependencies

```
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
requests>=2.28.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
pyyaml>=6.0
```

Install: `pip install -r requirements.txt`

---

## 13. GitHub Integration

The project is version-controlled with GitHub. Key workflows:
- Daily processor: Runs `run_daily.py` on schedule
- Auto-commit: Commits updated vault data

**Sync script:** `.github/workflows/daily-processor.yml`

---

## 14. Development Notes

### Current Priorities
1. Phase 1: Parliamentary Reference Structure - Complete
2. Phase 2: Clean & Fix - Complete
3. Phase 3: Stable IDs - Complete
4. Phase 4: Deputy Coverage (158→463) - Complete
5. Phase 5: Committee Assignments - Complete
6. Phase 6: Law Enrichment - In Progress
7. Phase 7: Low-RAM Optimization - Complete

### Next Actions
- Continue law enrichment with process metadata
- Add more historical sessions (2020-2024)
- Refine entity resolution accuracy

---

## 15. Quick Start for AI/Coding Tools

When opening this project:

1. **Read this file first** - It contains everything you need to know
2. **Use centralized config** - Import from `scripts/config.py`, never hardcode paths
3. **Check `scripts/config.py`** for paths before writing new code
4. **Use existing patterns** - Look at similar scripts before implementing
5. **Run `python3 scripts/stenomd_master.py --status`** to get current state
6. **Test with `--dry-run`** before making changes

**Key principle:** All paths should come from `config.get_config()`, not hardcoded strings.

---

*Last Updated: 2026-04-27*  
*Generated by: OpenCode AI Analysis*  
*Purpose: Immediate project reference for AI tools*