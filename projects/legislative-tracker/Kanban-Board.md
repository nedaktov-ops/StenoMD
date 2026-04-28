# Legislative Tracker Kanban Board

This board tracks the progress of legislative proposals through the parliamentary process.

## How to Use

1. **Add a new task**: Create a new task with appropriate tags and status field:
   ```tasks
   due today
   #law /proposed
   ```
2. **Move tasks between columns**: Change the status field:
   - `#proposed` – Newly submitted proposals
   - `#committee` – Under committee review
   - `#debated` – Chamber debate scheduled/completed
   - `#passed` – Approved by chamber
   - `#rejected` – Voted down or withdrawn
3. **Filter by chamber**: Use `#cdep` or `#senate` tags.
4. **Link to law notes**: Use `[[law-number-title]]` syntax to link to vault `laws/` files.

## Board Columns

<!-- kanban columns: proposed, committee, debated, passed, rejected -->

### Proposed

New legislative initiatives pending formal submission.

```tasks
not done
#law #proposed
sort by due
```

### Committee Review

Assigned to parliamentary committee for analysis.

```tasks
#law #committee
sort by created
```

### Debate

Scheduled for or currently in plenary debate.

```tasks
#law #debated
sort by due
```

### Passed

Approved by one or both chambers.

```tasks
#law #passed
sort by created desc
```

### Rejected

Voted down, withdrawn, or failed to pass.

```tasks
#law #rejected
sort by created desc
```

---

## Statistics

```dataview
TABLE status, count() AS Count
FROM #law
GROUP BY status
SORT Count DESC
```

## Recent Updates

```tasks
due next 7 days
#law
sort by due
```

---

*This board is powered by the Tasks plugin. Tasks are auto-updated based on due dates and tags.*
