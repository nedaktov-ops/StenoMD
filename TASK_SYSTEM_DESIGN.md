# StenoMD Task Tracking System - Design Document

**Created:** 2026-04-26  
**Version:** 1.0

---

## Overview

This document describes the dynamic task tracking system for the StenoMD project, designed for integration with the planner agent and manual workflow management.

---

## Components

### 1. Task Files

| File | Purpose |
|------|---------|
| `Unfinished-tasks.md` | Active/deferred/incomplete tasks |
| `Completed-tasks.md` | History of finished tasks |
| `scripts/task_manager.py` | Python module for automation |
| `vault/tasks/` | Directory for task-related data |

### 2. Task Format Structure

```markdown
### Task 001: <TITLE>
**ID:** TASK-001
**Status:** DEFERRED | IN_PROGRESS | READY_TO_START | COMPLETED
**Priority:** CRITICAL | HIGH | MEDIUM | LOW
**Created:** YYYY-MM-DD
**Last Checked:** YYYY-MM-DD

**Phase Reference:** <SOURCE FILE AND PHASE>

**Instructions:**
1. Step-by-step instructions
2. Another step

**Dependencies:**
- Task-### (description)
- Other dependencies

**Expected Output:**
- What this task produces

**Blocked By:**
- What's blocking this task

**Notes:**
- Additional notes
```

---

## Status Values

| Status | Meaning | Action |
|--------|---------|--------|
| DEFERRED | Waiting on dependencies or more info | Skip until dependencies resolved |
| IN_PROGRESS | Actively being worked on | Continue working |
| READY_TO_START | Can begin immediately | Start if no higher priority |
| COMPLETED | Finished | Move to history |

---

## Priority Values

| Priority | Score | Meaning |
|----------|-------|---------|
| CRITICAL | 100 | Blocks major functionality |
| HIGH | 75 | Important for project goals |
| MEDIUM | 50 | Should be done eventually |
| LOW | 25 | Nice to have |

---

## Integration with Planner Agent

### Startup Integration

The planner agent should check for pending tasks on startup:

```bash
# Option 1: Shell integration
python3 scripts/task_manager.py --startup-report

# Option 2: Python integration
from scripts.task_manager import TaskManager
tm = TaskManager()
report = tm.generate_startup_report()
```

### Suggested Workflow

1. **On each planner run:**
   - Read `Unfinished-tasks.md`
   - Get next task: `tm.get_next_task()`
   - Check dependencies: `tm.check_dependencies(task_id)`
   - If ready, work on task
   - On completion: `tm.update_status(task_id, "COMPLETED", notes="...")`

2. **Manual workflow:**
   - Add new task to `Unfinished-tasks.md`
   - Set status: READY_TO_START or DEFERRED
   - When done: status changes to COMPLETED
   - Task moves to history automatically

---

## Automation Examples

### Check for work
```bash
python3 scripts/task_manager.py --list
python3 scripts/task_manager.py --next
```

### Update task status
```bash
python3 scripts/task_manager.py --update TASK-001:IN_PROGRESS
python3 scripts/task_manager.py --update TASK-001:COMPLETED
```

### Check dependencies
```bash
python3 scripts/task_manager.py --check-deps TASK-001
```

---

## Task Manager API

### Python Module

```python
from scripts.task_manager import TaskManager

tm = TaskManager()

# Get tasks
tasks = tm.get_pending_tasks()  # All pending
tasks = tm.get_all_tasks()       # Including completed
task = tm.get_task_by_id("TASK-001")
next_task = tm.get_next_task()

# Update status
tm.update_status("TASK-001", "IN_PROGRESS")
tm.update_status("TASK-001", "COMPLETED", notes="Done!")

# Check dependencies
result = tm.check_dependencies("TASK-001")

# Reports
report = tm.generate_startup_report()
```

---

## History Tracking

Completed tasks are automatically moved to `Completed-tasks.md` with:
- Original task information
- Completion date
- Notes added at completion
- Timestamp

This provides audit trail and reference for future work.

---

## Current Task

### TASK-001: Phase 5 - Committee Assignments

**Status:** DEFERRED  
**Priority:** HIGH  
**Phase Reference:** STRATEGY.md Phase 5: Complete 2024 Data  

**Instructions:**
1. Scrape committee assignments from cdep.ro and senat.ro
2. Navigate to each MP profile
3. Extract committee memberships
4. Parse roles (member/vice-chair/chair)
5. Update profile files in vault/politicians/

**Dependencies:**
- Open Parliament RO data imported

**Blocked By:**
- Historical data blocked (cdep.ro returns 404 for pre-2015)

---

## Files Created

1. `/home/adrian/Desktop/NEDAILAB/StenoMD/Unfinished-tasks.md` - Active tasks
2. `/home/adrian/Desktop/NEDAILAB/StenoMD/Completed-tasks.md` - Task history  
3. `/home/adrian/Desktop/NEDAILAB/StenoMD/scripts/task_manager.py` - Automation module
4. `/home/adrian/Desktop/NEDAILAB/StenoMD/TASK_SYSTEM_DESIGN.md` - This document

---

## Usage Summary

| Command | Purpose |
|---------|---------|
| `--list` | Show pending tasks |
| `--next` | Show next task to work on |
| `--all` | Show all tasks |
| `--update ID:STATUS` | Update task status |
| `--check-deps ID` | Check dependencies |
| `--startup-report` | Generate startup report |

---

*LastUpdated: 2026-04-26*
