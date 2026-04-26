# StenoMD Unfinished Tasks

**Last Updated:** 2026-04-26  
**Status:** ACTIVE  
**Total Pending:** 2

---

## DEFERRED TASKS

### Task 001: Phase 5 - Committee Assignments
**ID:** TASK-001  
**Status:** COMPLETED
**Priority:** HIGH  
**Created:** 2026-04-24  
**Last Checked:** 2026-04-26

**Completion Notes:**
- Scraped 393 committee assignments for 277 MPs from cdep.ro
- 324/446 deputy profiles updated with committees field
- Scripts: scrape_committees.py, add_committee_data.py

### Task 002: Phase 4.1 - Bill Tracking
**ID:** TASK-002  
**Status:** IN PROGRESS
**Priority:** HIGH  
**Created:** 2026-04-26  
**Last Checked:** 2026-04-26

**Completion Notes:**
- 5/124 laws matched with Open Parliament proposals (2023-2025)
- Sponsor fields added to 5 law files
- Limited by data format - most laws don't have Open Parliament IDs

### Task 003: Phase 4.2 - Voting Records
**ID:** TASK-003  
**Status:** DEFERRED
**Priority:** MEDIUM  
**Created:** 2026-04-26  
**Last Checked:** 2026-04-26

**Reason for Deferral:**
- cdep.ro voting page HTML has complex table structure
- Would require detailed parsing with Selenium/Playwright
- Open Parliament RO doesn't include voting data yet
- Alternative: parlament.openpolitics.ro (site unreachable)

**Recommended Next Steps:**
1. Try again when Open Parliament adds voting data
2. Use manual tracking for key votes
3. Research parliamentary API options

---

### Task 004: Historical Bill Backfill (2020-2023)
**ID:** TASK-004  
**Status:** DEFERRED
**Priority:** LOW  
**Created:** 2026-04-26  
**Last Checked:** 2026-04-26

**Instructions:**
Backfill bill data for 2020-2023 legislature
- Requires web scraping from cdep.ro
- Open Parliament data available for this period
- Large effort - deferred until resources available

**Phase Reference:** STRATEGY.md Phase 5: Complete 2024 Data  

**Instructions:**
Scrape committee assignments for all MPs from cdep.ro and senat.ro
1. Navigate to each MP profile on cdep.ro/senat.ro
2. Extract committee memberships from profile pages
3. Parse the committee names and roles (member vs vice-chair vs chair)
4. Update deputy/senator profile files in vault/politicians/
5. Store in structured format:

**Data Structure:**
```yaml
committees:
  - name: "Comisia pentru buget, finanţe, bănci"
    role: "member"  # member | vice_presedinte | presedinte
    start_date: "2024-12-20"
    end_date: null
```

**Dependencies:**
- Task-002 (prerequisite for parsing profiles)
- Open Parliament RO data imported

**Source URLs:**
- Chamber: https://www.cdep.ro/pls/parlam/ structs for 2024-2028
- Senate: https://www.senat.ro/Files/Deputat/Lista-Deputati.aspx

**Expected Output:**
- 330 deputy committee assignments
- 136 senator committee assignments
- Committee reference: vault/_parliament/committees/

**Blocked By:**
- Historical data blocked (cdep.ro returns 404 for pre-2015)

**Notes:**
- Requires web scraping (not in current agents)
- May need Selenium or Playwright for dynamic content
- Alternative: Use Open Parliament RO if committee data available

---

## IN PROGRESS

### Task 002: Phase 4.1 - Bill Tracking + MP Linking
**ID:** TASK-002  
**Status:** IN PROGRESS
**Priority:** HIGH  
**Created:** 2026-04-26  
**Last Checked:** 2026-04-26

**Phase Reference:** STRATEGY.md Phase 4.1: Bill Tracking

**Instructions:**
Link bill sponsors to MP profiles:
1. Load Open Parliament proposals data
2. Extract law registration numbers
3. Match to vault law files
4. Extract initiator IDs → stable_ids mapping
5. Add sponsors field to law frontmatter
6. Add process_stage based on status

**Notes:**
- Limited matching: Only 5/124 laws have Open Parliament IDs (2023-2025 only)
- Requires web scraping for additional bills (deferred)
- Current legislature coverage: 2024 proposals available

---

## READY TO START

### Task 003: Phase 4.2 - Voting Records
**ID:** TASK-003  
**Status:** READY_TO_START
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
