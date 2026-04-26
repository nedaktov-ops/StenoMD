# StenoMD Task Skill

**Trigger:** `/stenomd task`
**Purpose:** Task management aligned with project tasks

---

## Usage

```
/stenomd task                           # Show task overview
/stenomd task list                    # List active tasks
/stenomd task show TASK_ID            # Show task details
/stenomd task next                    # Show next task
/stenomd task status TASK_ID STATUS  # Update status
/stenomd task linked TASK_ID          # Show graph-linked tasks
```

---

## What It Does

1. **Lists tasks** from Unfinished-tasks.md
2. **Shows graph relevance** for each task
3. **Updates task status** in project
4. **Tracks graph-linked work**

---

## Task Integration

Tasks that benefit from graph queries:

| Task Type | Graph Query |
|-----------|------------|
| Data enrichment | Missing fields via `/stenomd analyze gaps` |
| Validation | Link checks via `/stenomd sync --validate` |
| Coverage | Stats via `/stenomd analyze coverage` |
| Activity | Leaderboard via `/stenomd analyze activity` |

---

## Example Output

### Task List
```
/stenomd task list

=== Active Tasks ===
TASK-010: Missing Law Data [DEFERRED]
  - Missing sponsors for 456 laws
  - Graph query: analyze gaps
  
=== Completed Tasks ===
TASK-007: Deputy Deduplication [COMPLETED]
TASK-008: Duplicate Names Cleanup [COMPLETED]
TASK-009: Senator Missing Party [COMPLETED]
```

### Task Details
```
/stenomd task show TASK-010

=== TASK-010: Missing Law Data ===
Status: DEFERRED
Priority: MEDIUM

Details:
- All 124 laws lack sponsor data
- Would require matching to parlamint proposals

Graph Integration:
- Query: /stenomd analyze gaps
- Result: 456 laws missing sponsors
  
Blocked By:
- Manual data entry required
  
Notes:
- Deferred for manual entry later
```

---

## Status Values

| Status | Meaning | Action Available |
|--------|---------|-----------------|
| READY_TO_START | Ready | Can start work |
| IN_PROGRESS | Working | Update progress |
| DEFERRED | Waiting | Resume later |
| COMPLETED | Done | Archive |

---

## Notes

- Reads from Unfinished-tasks.md
- Updates Completed-tasks.md
- Graph queries for context