# StenoMD Unfinished Tasks

**Last Updated:** 2026-04-28
**Status:** ACTIVE
**Total Pending:** 12

---

## COMPLETED (RECENT)

No new completions to report.

---

## PHASE A: DATA COMPLETENESS (IN PROGRESS)

### Task A.1: Fill Committee Assignments for All Deputies
**ID:** TASK-A1
**Status:** READY_TO_START
**Priority:** CRITICAL
**Created:** 2026-04-28

**Phase Reference:** project-timeline.md Phase A

**Instructions:**
1. Run `python3 scripts/add_committees.py --missing-only`
2. Verify with `python3 scripts/analyze_vault.py --check-committees`
3. Confirm all 788 deputies have non-empty `committees` field

**Dependencies:**
- TASK-A1.1: Verify current committee coverage count

**Expected Output:**
- 0 deputies with empty committees
- Health score increase +2-3 points

---

### Task A.2: Complete speeches_count for All Politicians
**ID:** TASK-A2
**Status:** READY_TO_START
**Priority:** CRITICAL
**Created:** 2026-04-28

**Phase Reference:** project-timeline.md Phase A

**Instructions:**
1. Run `python3 scripts/fix_deputy_data_from_op.py` for full vault
2. Fallback: Compute from vault sessions if OP incomplete
   - `python3 scripts/generate_activity_from_sessions.py`
3. Verify: `python3 scripts/analyze_vault.py --check-speeches`

**Expected Output:**
- All 788+ politicians have `speeches_count` >= 0
- Zero "NaN" or empty values

---

### Task A.3: Add deputy_count to All Sessions
**ID:** TASK-A3
**Status:** READY_TO_START
**Priority:** HIGH
**Created:** 2026-04-28

**Phase Reference:** project-timeline.md Phase A

**Instructions:**
1. Update `scripts/merge_vault_to_kg.py` to extract unique deputies from session frontmatter
2. Re-run: `python3 scripts/merge_vault_to_kg.py`
3. Verify: `jq '.[] | select(.deputy_count == null)' knowledge_graph/entities.json`

**Expected Output:**
- All 152 sessions have `deputy_count` populated
- Accurate counts per session

---

### Task A.4: Resolve Remaining Missing Party Fields
**ID:** TASK-A4
**Status:** READY_TO_START
**Priority:** HIGH
**Created:** 2026-04-28

**Phase Reference:** project-timeline.md Phase A

**Instructions:**
1. Run `python3 scripts/final_reconciliation_v2.py --fix-missing-party`
2. Add fallback: if no party found, set to "Independent/Unknown"
3. Verify: `grep -r 'party: ""' vault/politicians/ | wc -l` should be 0

**Expected Output:**
- 0 politicians with empty `party` field

---

## PHASE B: INFRASTRUCTURE (READY)

### Task B.1: Implement Test Suite
**ID:** TASK-B1
**Status:** READY_TO_START
**Priority:** HIGH
**Created:** 2026-04-28

**Phase Reference:** project-timeline.md Phase B

**Instructions:**
1. Create `tests/` directory with subfolders: agents/, kg/, analyze/, resolve/
2. Write unit tests for:
   - Entity extraction (cdep/senate)
   - Knowledge graph merging
   - Data validation
   - Entity resolution
3. Add pytest configuration (pytest.ini)
4. Add coverage reporting (pytest-cov)
5. Integrate into GitHub Actions

**Expected Output:**
- ≥80% code coverage
- CI passing on all pushes
- `make test` or `pytest` command works

**Dependencies:**
- B1.1: Choose test structure (pytest vs unittest)

---

### Task B.2: Performance Optimization (Async I/O)
**ID:** TASK-B2
**Status:** READY_TO_START
**Priority:** HIGH
**Created:** 2026-04-28

**Phase Reference:** project-timeline.md Phase B

**Instructions:**
1. Convert `cdep_agent.py` to asyncio + aiohttp
2. Convert `senat_agent.py` similarly
3. Implement worker pool (5-10 concurrent)
4. Add rate limiting (respectful delays)
5. Benchmark: measure sessions/minute before/after

**Expected Output:**
- 5-10 sessions/minute sustained
- No increase in error rates
- Progress indicators accurate

---

### Task B.3: Configuration Audit
**ID:** TASK-B3
**Status:** READY_TO_START
**Priority:** MEDIUM
**Created:** 2026-04-28

**Phase Reference:** project-timeline.md Phase B

**Instructions:**
1. Search for hardcoded paths: `grep -r "/home/adrian" scripts/ | grep -v config.py`
2. Replace with `config.VAULT_PATH`, `config.DATA_PATH`, etc.
3. Verify: `scripts/validators.py` passes all checks

**Expected Output:**
- 0 hardcoded paths in production scripts
- All scripts import from `scripts/config.py`

---

### Task B.4: API Security Hardening
**ID:** TASK-B4
**Status:** READY_TO_START
**Priority:** MEDIUM
**Created:** 2026-04-28

**Phase Reference:** project-timeline.md Phase B

**Instructions:**
1. Review `scripts/rest_api.py` for SQL injection
2. Convert all SQL to parameterized queries
3. Restrict CORS to localhost or specific origins
4. Add input validation/sanitization
5. Run security scan (bandit)

**Expected Output:**
- No SQL injection vulnerabilities
- CORS locked down to trusted origins
- Bandit score acceptable

---

## PHASE C: DOCUMENTATION (READY)

### Task C.1: API Reference Documentation
**ID:** TASK-C1
**Status:** READY_TO_START
**Priority:** HIGH
**Created:** 2026-04-28

**Phase Reference:** project-timeline.md Phase C

**Instructions:**
1. Document all REST endpoints (`scripts/rest_api.py`): paths, methods, params, examples
2. Document MCP server (`knowledge_graph/mempalace/mcp_server.py`)
3. Document query-brain CLI (`vault/_scripts/query-brain.py`)
4. Create `docs/API_REFERENCE.md` with examples and authentication notes

**Expected Output:**
- Complete API docs with curl examples
- Markdown file in docs/

---

### Task C.2: Developer Guide
**ID:** TASK-C2
**Status:** READY_TO_START
**Priority:** HIGH
**Created:** 2026-04-28

**Instructions:**
1. Architecture overview (component diagram)
2. How to add new scrapers (step-by-step)
3. Knowledge graph schema explanation
4. Testing guidelines
5. Contributing guidelines (CODE_OF_CONDUCT, PR template)

**Output**: `docs/DEVELOPMENT.md`

---

### Task C.3: Obsidian Setup Guide
**ID:** TASK-C3
**Status:** READY_TO_START
**Priority:** MEDIUM
**Created:** 2026-04-28

**Instructions:**
1. Step-by-step plugin installation (Dataview, QuickAdd, Calendar, Tasks, Metadata Menu)
2. Screenshots for each configuration step
3. Troubleshooting common issues
4. Hotkey cheat sheet

**Output**: `docs/OBSIDIAN_SETUP.md`

---

### Task C.4: Migration & Changelog
**ID:** TASK-C4
**Status:** READY_TO_START
**Priority:** LOW
**Created:** 2026-04-28

**Instructions:**
1. `docs/MIGRATION.md`: How to upgrade from previous versions
2. `docs/CHANGELOG.md`: Auto-generated from git commits or manual entries

---

### Task C.5: Template Gallery
**ID:** TASK-C5
**Status:** READY_TO_START
**Priority:** MEDIUM
**Created:** 2026-04-28

**Instructions:**
1. Document each template: politician.md, session.md, law.md, committee.md
2. Field-by-field descriptions with examples
3. Link to `docs/TEMPLATES.md`

---

### Task C.6: Dataview Query Examples
**ID:** TASK-C6
**Status:** READY_TO_START
**Priority:** MEDIUM
**Created:** 2026-04-28

**Instructions:**
1. Collect useful queries from `_brain/` andpilogs
2. Categorize: activity rankings, party breakdown, session timelines, law tracking
3. Create `docs/DATAVIEW_EXAMPLES.md` with 20+ examples

---

## DEFERRED LOW-PRIORITY

### Task Z.1: Excalidraw Diagrams
**ID:** TASK-Z1
**Status:** DEFERRED
**Priority:** LOW
**Created:** 2026-04-28

**Notes:** Optional enhancement; create parliament structure, committee networks, party alignment drawings in `vault/_parliament/diagrams/`

---

### Task Z.2: Legislative Kanban Board
**ID:** TASK-Z2
**Status:** DEFERRED
**Priority:** LOW
**Created:** 2026-04-28

**Notes:** Setup Tasks plugin board in `projects/legislative-tracker/` with columns: Proposed → Committee → Debated → Passed → Rejected

---

### Task Z.3: Notebook Navigator Setup
**ID:** TASK-Z3
**Status:** DEFERRED
**Priority:** LOW
**Created:** 2026-04-28

**Notes:** Configure Obsidian Notebook feature for session workflow; create notebooks per legislature or year

---

## BLOCKED (External Dependencies)

### Task BLOCKED-001: Voting Records (TASK-003)
**ID:** TASK-003
**Status:** DEFERRED
**Priority:** MEDIUM
**Created:** 2026-04-26

**Details:**
- cdep.ro voting endpoints return 404
- parlament.openpolitics.ro has only 2017 data (limited)
- Open Parliament RO: voting data on roadmap but not yet implemented

**Solution:** Wait for Open Parliament RO to add voting data; periodically check GitHub issue.

---

### Task BLOCKED-002: Historical Data Pre-2015
**ID:** BLOCKED-002
**Status:** BLOCKED
**Priority:** LOW
**Created:** 2026-04-28

**Reason:** cdep.ro returns 404 for 1996-2014

**Research Required (ASK PERMISSION before contacting):**
- Contact cdep.ro for historical data
- Check Romanian National Archives
- Check EU Parliament joint sessions
- Academic sources

---

### Task BLOCKED-003: Senate Historical Backfill
**ID:** BLOCKED-003
**Status:** BLOCKED
**Priority:** LOW
**Created:** 2026-04-28

**Reason:** senat.ro only shows current 2024-2028 legislature; PDFs for 2020-2024 are 404

**Action:** Accept limitation; focus on 2024-2028 only.

---

## STATUS LEGEND

| Status | Meaning |
|--------|---------|
| DEFERRED | Put on hold (waiting for dependencies or more info) |
| IN_PROGRESS | Actively being worked on |
| READY_TO_START | Can begin immediately |
| COMPLETED | Finished (moved to Completed-tasks.md) |
| BLOCKED | Blocked by external factor outside our control |

## PRIORITY LEGEND

| Priority | Score | Meaning |
|----------|-------|---------|
| CRITICAL | 100 | Blocks major functionality, must do first |
| HIGH | 75 | Important for project goals |
| MEDIUM | 50 | Should be done eventually |
| LOW | 25 | Nice to have, can defer indefinitely |

---

*LastUpdated: 2026-04-28 00:45*
*Next Action: Start Task A.1 (Fill Committee Assignments)*