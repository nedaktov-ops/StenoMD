# Notebook Navigator Setup

Obsidian's Notebook feature (v1.5+) allows you to create curated collections of notes for specific contexts. StenoMD can use notebooks to organize session workflows, legislative research, and topic-based investigations.

## Why Use Notebooks?

- **Session Preparation**: Gather all relevant laws, MP profiles, and committee info for an upcoming session.
- **Legislative Research**: Compile notes on a specific law or topic across multiple sources.
- **Topic Deep Dives**: Track all discussions about a particular policy area (e.g., energy, education).

---

## Creating a Notebook

1. Open Obsidian Settings → "Notebooks".
2. Click "Add new notebook".
3. Name: `Session 2024-01-15 - Energy Debate` (example).
4. Set a cover color or icon (optional).
5. Set a filter (optional) to auto-include notes by tag or folder.

Alternatively, use the command palette: `Notebooks: Create new notebook from search`.

---

## Recommended Notebooks

### Session Notebooks

For each major session, create a notebook that includes:

- The session note itself (`sessions/deputies/2024-01-15.md`)
- Laws discussed (`laws/20-2024.md`)
- MPs who spoke (links to `politicians/deputies/*.md`)
- Related committee notes (`_parliament/committees/*.md`)

**How to build**: Search for session date or laws discussed, then add notes to notebook.

---

### Legislative Track

Create a notebook per law number to track its journey:

- Proposal documents
- Amendments
- Voting records
- Related sessions

**Filter**: `#law` AND `"20/2024"` in title.

---

### Policy Topic Notebooks

For ongoing policy areas:

- Energy & Environment
- Education Reform
- Healthcare
- Defense & Security

**Filter**: Use relevant tags from `_parliament/` notes and session statements.

---

## Workflow Integration

**Before a session:**

1. Open the session's notebook.
2. Review all linked notes: laws, MP backgrounds, committee reports.
3. Use the notebook's "Context" view to see all content at once.

**During research:**

1. Open a topic notebook (e.g., "Energy Policy").
2. Quickly find all sessions discussing energy, all laws on the topic, and key actors.
3. Add new notes to the notebook as you discover them.

---

## Notebook Settings

- **Sort notes by**: `Last modified` (default) or `Title`.
- **Show note preview**: Enabled for quick scanning.
- **Include subfolders**: Enable if you want entire sub-trees.

---

## Sharing & Collaboration

Notebooks are stored in `.obsidian/notebooks/` as JSON. You can share them by committing that folder to the repository. However, note that notebook definitions are local to the machine; if you work across multiple machines, you'll need to copy the notebook config.

Alternatively, use the community plugin "Notebooks from query" to define notebooks as saved Dataview queries, which are portable.

---

## Advanced: Notebooks from Query

Install the "Notebooks from query" plugin if you want dynamic notebooks based on Dataview queries. Example query for a dynamic "Active Laws" notebook:

```dataview
FROM #law
WHERE status != "adoptată" AND status != "respinsă"
SORT date DESC
```

This automatically updates as law statuses change in the frontmatter.

---

## Known Issues

- Notebooks are not vault-synced by default; back up `.obsidian/notebooks/` if you use multiple devices.
- Filters using tags work best; content filters (full-text) may be slower on large vaults.
- The native Notebooks feature is still evolving; plugin alternatives may provide more flexibility.

---

**Next**: Create a "Quick Reference" notebook with your most-used queries and links to `docs/DATAVIEW_EXAMPLES.md`.
