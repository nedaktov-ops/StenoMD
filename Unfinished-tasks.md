# StenoMD Unfinished Tasks

**Last Updated:** 2026-04-26  
**Status:** ACTIVE  
**Total Pending:** 1

---

## DEFERRED TASKS

### Task 001: Phase 5 - Committee Assignments
**ID:** TASK-001  
**Status:** DEFERRED
**Priority:** HIGH  
**Created:** 2026-04-24  
**Last Checked:** 2026-04-26

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

*No tasks currently in progress.*

---

## READY TO START

*No tasks ready to start.*

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
