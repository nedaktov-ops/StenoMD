# Obsidian Setup for StenoMD

This guide explains how to configure Obsidian to work with the StenoMD vault effectively.

## Prerequisites

- Obsidian installed (v1.0+).
- The StenoMD repository cloned locally.
- Vault path: `StenoMD/vault`.

## Initial Setup

1. **Open Obsidian** → "Open folder as vault" → select `StenoMD/vault`.
2. **Enable Community Plugins** in Settings → "Core plugins" → turn on (if not already).
3. **Install the following plugins** from Community Plugins:
   - **Dataview** (v0.6.0+) – powerful querying of markdown frontmatter.
   - **QuickAdd** (v2.12.0+) – rapid note creation with templates.
   - **Calendar** – navigate sessions by date.
   - **Tasks** – manage to-do items across vault.
   - **Metadata Menu** – quick frontmatter editing.
   - **Graph Analysis** (optional) – explore connections.

   Install via Settings → Community plugins → Browse → search and install. Enable each after installation.

## Plugin Configuration

### QuickAdd

Import the provided configuration:

```bash
cp config/quickadd-config.json .obsidian/plugins/quickadd/quickadd-config.json
```

If `.obsidian/plugins/quickadd/` doesn't exist, create it:

```bash
mkdir -p .obsidian/plugins/quickadd
```

Restart Obsidian or reload plugins (`Ctrl+P` → "Reload plugins without saving").

**Contexts**:

- **QuickAdd Deputy** (`Ctrl+Shift+D`): creates a new deputy profile in `politicians/deputies/`.
- **QuickAdd Senator** (`Ctrl+Shift+S`): creates a new senator profile in `politicians/senators/`.
- **QuickAdd Law** (`Ctrl+Shift+L`): creates a new law note in `laws/`.
- **QuickAdd Session** (`Ctrl+Shift+E`): creates a new session note in `sessions/{chamber}/`.

After creation, enrich data by running enrichment scripts.

### Dataview

No special configuration required. Use JavaScript queries to filter and sort notes.

**Example:** List deputies with `speeches_count` > 50:

```dataviewjs
dv.pages('#deputy')
  .where(p => p.speeches_count > 50)
  .sort(p => p.speeches_count, 'desc')
  .limit(10)
  .display()
```

See `docs/DATAVIEW_EXAMPLES.md` for more.

### Calendar

1. Open the Calendar plugin settings.
2. Set **Week start** to Monday (Romanian standard).
3. Under "Calendar folder", leave blank or set to `sessions/deputies` if you want daily notes. It's optional.
4. Use the Calendar pane to click dates and view linked session notes.

### Tasks

Default settings are fine. Tasks appear from `#todo` tags in notes. Use the Tasks panel to see all todos across the vault.

### Metadata Menu

Enable for `politicians/`, `sessions/`, `laws/` folders. It adds a sidebar pane to edit frontmatter fields via UI.

## Vault Structure

The vault includes:

- `Index.md` – main dashboard with latest updates and quick links.
- `_brain/` – smart queries showing activity, top speakers, recent laws.
- `_parliament/` – reference: committees, constitutional articles.
- `politicians/deputies/` and `senators/` – individual politician profiles.
- `sessions/deputies/` and `senate/` – session transcripts with statements.
- `laws/` – law profiles with metadata.

### Daily Workflow

1. **Check the Dashboard**: Open `Index.md` to see health and latest additions.
2. **Create notes** via QuickAdd hotkeys if adding new entities.
3. **Enrich profiles**: Run `fix_deputy_data_from_op.py` and similar scripts to fill missing fields.
4. **Update Knowledge Graph**: Run `scripts/merge_vault_to_kg.py` after vault changes.
5. **Regenerate Graphify** (optional): `python3 scripts/build_vault_graph_fixed.py` for visual exploration.

## Hotkeys Cheat Sheet

| Action                  | Hotkey           |
|-------------------------|------------------|
| QuickAdd Deputy         | Ctrl+Shift+D     |
| QuickAdd Senator        | Ctrl+Shift+S     |
| QuickAdd Law            | Ctrl+Shift+L     |
| QuickAdd Session        | Ctrl+Shift+E     |
| Open Command Palette    | Ctrl+P           |
| Reload plugins          | Ctrl+P → command |
| Toggle source mode      | Ctrl+E           |
| Toggle preview          | Ctrl+R           |

---

## Useful Dataview Views

Create notes in `_brain/` to store useful queries.

**Top 10 Most Active Deputies (by speeches_count):**

```dataview
TABLE speeches_count, party, constituency
FROM #deputy
SORT speeches_count DESC
LIMIT 10
```

**Recent Sessions (last 7 days):**

```dataview
TABLE file.day as Date, participants, statements_count
FROM "#session"
WHERE file.day >= this weeks - 7
SORT file.day DESC
```

**Laws by Status:**

```dataview
TABLE title, date, sponsors
FROM #law
SORT status DESC
```

---

## Troubleshooting

**QuickAdd contexts not showing:** Ensure `quickadd-config.json` is in `.obsidian/plugins/quickadd/` and restart Obsidian.

**Dataview queries return no results:** Check that frontmatter fields match case (`speeches_count` not `speechesCount`). Use developer console (`Ctrl+Shift+I`) to see query errors.

**Vault too large / performance:** Disable unused plugins, increase cache size in settings, exclude `Graphify` outputs if not needed.

**Calendar not linking sessions:** Ensure session files have proper `date` in frontmatter (ISO format) and are located in `sessions/deputies/` or `sessions/senate/`.

---

## Advanced: Graph View

The vault is connected: MPs referenced in sessions, laws sponsored, committee memberships. Use Dataview's graph view or Graph Analysis plugin to explore relationships. For a richer interactive graph, generate `Graphify` HTML from the codebase.

---

**Next Steps:** Explore `Index.md`, browse `_brain/Dashboard.md`, and start querying!
