# StenoMD Unfinished Tasks

**Last Updated:** 2026-04-26  
**Status:** ACTIVE  
**Total Pending:** 3

---

## MAINTENANCE REQUIRED

### Task 007: Deputy Deduplication  
**ID:** TASK-007  
**Status:** IN_PROGRESS  
**Priority:** HIGH

**Issues Found:**
- 115 extra deputy profiles (447 vs 332 expected in 2024 legislature)
- 7 files have same IDM but different names (ID conflicts)
- 146 profiles without idm field (likely obsolete)

**Run:** `python3 scripts/dedupe_analysis.py`

### Task 008: Duplicate Names Cleanup
**ID:** TASK-008  
**Status:** READY_TO_START

**Issues:**
- "index" duplicate name exists (politicians/deputies/Index.md)

### Task 009: Senator Missing Party
**ID:** TASK-009  
**Status:** READY_TO_START

**Details:**
- 1 senator profile missing party field

---

## COMPLETED (2026-04-26 Session)

### TASK-FIX: Field Enrichment
- Fix deputies.py: 300 files updated with idm/party
- add_committees.py: 251 profiles with committees
- analyze_vault.py: Full diagnostic created

---

## COMPLETED

### Task 002: Phase 4.1 - Bill Tracking + MP Linking
**ID:** TASK-002  
**Status:** COMPLETED  
**Priority:** HIGH  
**Created:** 2026-04-26  
**Last Checked:** 2026-04-26

**Completion Notes:**
- Aggregated Open Parliament proposals (1039) by idm
- Enriched 285 deputy profiles with laws_proposed
- Created mp-activity-ranking.md Dataview query
- Scripts: aggregate_deputy_activity.ts, enrich_deputies_with_activity.ts

### Task 005: Senator Profile Enrichment
**ID:** TASK-005  
**Status:** COMPLETED  
**Priority:** HIGH  
**Created:** 2026-04-26  
**Last Checked:** 2026-04-26

**Completion Notes:**
- Matched 126/138 senator profiles using fuzzy name matching
- Added party, party_full, constituency from senators_2024_full.json
- Updated 32 profiles with new data
- Script: enrich_senators.ts

### Task 006: Motion Data Linking
**ID:** TASK-006  
**Status:** COMPLETED  
**Priority:** HIGH  
**Created:** 2026-04-26  
**Last Checked:** 2026-04-26

**Completion Notes:**
- Linked 9 motions (from deputy_motions.json) to deputy profiles
- Updated 91 profiles with motion counts
- Note: Only 9 motions in current Open Parliament data (2024 legislature)
- Script: link_motions.ts

---

## IN PROGRESS

(None currently - all done)

---

## READY TO START

### Task 003: Phase 4.2 - Voting Records
**ID:** TASK-003  
**Status:** DEFERRED  
**Priority:** MEDIUM  
**Created:** 2026-04-26  
**Last Checked:** 2026-04-26

**Research Notes (Final):**
- cdep.ro: Voting endpoints return 404 or complex JavaScript-rendered HTML
- senat.ro: Has working vote pages but requires browser automation (ASP.NET)
- parlament.openpolitics.ro: Data exports for 2017 only (database was offline)
- Open Parliament RO: Voting data on roadmap but not yet implemented
- GitHub issue filed: ClaudiuCeia/open-parliament-ro

**Solution:**
1. **Wait** - Open Parliament RO adding votes in future releases
2. **Historical** - Use parlament.openpolitics.ro 2017 data (limited)
3. **Manual** - Track key votes when needed
4. **Placeholder** - Created scrape_senate_votes.ts for future implementation
**Priority:** MEDIUM  
**Created:** 2026-04-26  
**Last Checked:** 2026-04-26

**Phase Reference:** STRATEGY.md Phase 4.2: Voting Records

**Instructions:**
Scrape voting records from cdep.ro:
1. Find vote pages per session
2. Extract individual votes per MP
3. Link to bill via vote_id
4. Build individual voting records per MP
5. Calculate party cohesion metrics

**Notes:**
- BLOCKED until cdep.ro scraping verified
- Consider parlament.openpolitics.ro data if available

---

## NOTE: TASK TEMPLATE

Use this format for new tasks:

```
### USE THIS FORMAT FOR NEW TASKS
**ID:** TASK-###
**Status:** <DEFERRED|IN_PROGRESS|READY_TO_START>
**Priority:** <CRITICAL|HIGH|MEDIUM|LOW>
**Created:** YYYY-MM-DD
**Last Checked:** YYYY-MM-DD

**Phase Reference:** <SOURCE FILE AND PHASE>

**Instructions:**
1. <Step-by-step instructions>

**Dependencies:**
- Task-### (description)
- <Other dependencies>

**Expected Output:**
- <What this task produces>

**Blocked By:**
- <What's blocking this task>

**Notes:**
- <Additional notes>
```

---

## STATUS LEGEND

| Status | Meaning |
|--------|---------|
| DEFERRED | Put on hold (waiting for dependencies or more info) |
| IN_PROGRESS | Actively being worked on |
| READY_TO_START | Can begin immediately |
| COMPLETED | Finished (moved to Completed-tasks.md) |

## PRIORITY LEGEND

| Priority | Score | Meaning |
|----------|-------|---------|
| CRITICAL | 100 | Blocks major functionality |
| HIGH | 75 | Important for project goals |
| MEDIUM | 50 | Should be done eventually |
| LOW | 25 | Nice to have |

---

*LastUpdated: 2026-04-26*
*Next Action: Review Task 001 for scraping approach*
