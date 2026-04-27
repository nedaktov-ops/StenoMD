# Plugin Validation & Health Checklist

**Purpose:** Verify all required Obsidian plugins are installed, configured, and functioning correctly.

**How to use:** Open your StenoMD vault in Obsidian and check each item below. Mark items as ✅ (working) or ❌ (needs attention).

---

## Installation Summary

| Plugin | Status | Version | Notes |
|--------|--------|---------|-------|
| Dataview | ⬜ | Latest | **Essential** |
| Metadata Menu | ⬜ | Latest | **Essential** |
| Calendar | ⬜ | Latest | Very Useful |
| Tasks | ⬜ | Latest | Very Useful |
| QuickAdd | ⬜ | Latest | Very Useful |
| Kanban | ⬜ | Latest | Optional |
| Excalidraw | ⬜ | Latest | Optional |
| Advanced Tables | ⬜ | Latest | Optional |

---

## Essential Plugins

### 1. Dataview ⭐⭐⭐⭐⭐

**Why:** Powers all dynamic queries in the vault (MP rankings, session lists, law tracking).

**Installation:**
- Settings → Community plugins → Browse → Search "Dataview"
- Install and Enable

**Configuration (should be defaults):**
- [x] JavaScript query engine enabled
- [x] Auto-refresh on file change
- [x] Enable in markdown preview

**Test:** Create a new note with this query:

```dataview
LIST FROM "politicians/deputies" LIMIT 3
```

- ✅ Query executes without errors
- ✅ Results display as clickable links
- ✅ No console errors (Ctrl+Shift+I)

**Known Issues:**
- Queries show "No results" when files are in wrong folder
- YAML syntax errors break all queries
- Field names are case-sensitive

**Troubleshooting:**
1. Restart Obsidian
2. Check that vault contains `politicians/deputies/` folder with deputy files
3. Verify field names match template (use lowercase with underscores)
4. Clear Dataview cache: Settings → Dataview → Reset Cache

---

### 2. Metadata Menu ⭐⭐⭐⭐⭐

**Why:** Edit frontmatter fields visually without YAML editing.

**Installation:**
- Search "Metadata Menu" in Community plugins
- Install and Enable

**Configuration:**
- [x] Enable ribbon icon
- [x] Show for all note types

**Test:**
1. Open any deputy file (e.g., `politicians/deputies/ION-POPESCU.md`)
2. Click the metadata icon (table icon) in the left ribbon
3. Edit fields like `party`, `constituency`, `speeches_count`
4. Save and verify changes persist in YAML

- ✅ Metadata panel opens
- ✅ Fields are editable
- ✅ Changes saved to frontmatter
- ✅ No duplicate or missing fields

**Known Issues:**
- Some custom fields may not appear (add to "Fields to show" in settings)
- Array fields (like `committees`) need special formatting

**Troubleshooting:**
1. Settings → Metadata Menu → Configure fields for each note type
2. Add missing fields: `stable_id`, `party`, `constituency`, `idm`, `speeches_count`
3. Restart plugin

---

## Very Useful Plugins

### 3. Calendar

**Why:** Navigate sessions by date, see weekly/monthly views.

**Installation:**
- Search "Calendar" in Community plugins
- Install and Enable

**Configuration:**
- [x] Set week start to **Monday**
- [x] Link calendar to `vault/sessions/` folder (optional)
- [x] Show week numbers

**Test:**
1. Open Calendar (left ribbon or command palette)
2. Navigate to a date that has a session file
3. Click date - should show session note links

- ✅ Calendar displays correctly
- ✅ Session dates appear as clickable links
- ✅ Navigation works

**Known Issues:**
- Calendar may not show links if files aren't in `sessions/` folder
- Date format must matchYYYY-MM-DD in frontmatter

**Troubleshooting:**
1. Settings → Calendar → Folder: set to `sessions`
2. Ensure session files have proper `date:` field in YAML

---

### 4. Tasks

**Why:** Integrates with the task tracking system (if used).

**Installation:**
- Search "Tasks" in Community plugins
- Install and Enable

**Configuration:**
- [x] Default folder: `tasks/` (if you use tasks)
- [x] Parse tasks in: all notes
- [x] Enable due dates, priorities

**Test:**
1. Create a task: `- [ ] Review deputy data`
2. Check Tasks panel appears
3. Filter by tag, date, etc.

- ✅ Tasks recognized
- ✅ Tasks panel functional
- ✅ Due dates work

**Known Issues:**
- Tasks only work in notes within configured folders
- Custom tag colors may need setup

**Troubleshooting:**
1. Settings → Tasks → Check "Search all vault notes"
2. Restart Obsidian

---

### 5. QuickAdd

**Why:** Rapidly create new deputy/session/law notes with templates.

**Installation:**
- Search "QuickAdd" in Community plugins
- Install and Enable

**Configuration:**
QuickAdd config should be at: `vault/.obsidian/plugins/quickadd/config.yaml`

**✅ CONFIGURATION VALIDATED (2026-04-27):**

| Script | Template | Output Path | Fields |
|--------|----------|-------------|--------|
| New Deputy | `_templates/politician.md` | `politicians/deputies/{{NAME}}-{{DATE}}.md` | Name, Party, Constituency, Stable ID, IDM |
| New Session | `_templates/session.md` | `sessions/{{DATE}}.md` | Chamber, Title, Session Number |
| New Law | `_templates/law.md` | `laws/{{NUMBER}}-{{YEAR}}.md` | Number, Year, Title, Chamber, Proposal Number |

**Test each workflow:**

**New Deputy:**
1. Command palette → "QuickAdd: New Deputy"
2. Fill: Name="Test User", Party="PSD", Constituency="București", Stable ID="pol_test123", IDM="999"
3. Should create: `politicians/deputies/Test User-2026-04-27.md`
4. Open file - verify frontmatter populated correctly

- ✅ Deputy created
- ✅ Frontmatter fields populated
- ✅ Template variables replaced

**New Session:**
1. Command palette → "QuickAdd: New Session"
2. Fill: Chamber="deputies", Title="Test Session", Session Number="1"
3. Should create: `sessions/2026-04-27.md`
4. Verify date auto-filled

- ✅ Session created with correct filename
- ✅ Date format correct (YYYY-MM-DD)

**New Law:**
1. Command palette → "QuickAdd: New Law"
2. Fill: Number="101", Year="2026", Title="Test Law", Chamber="Chamber of Deputies", Proposal Number="101/2026"
3. Should create: `laws/101-2026.md`

- ✅ Law created with correct filename
- ✅ All fields populated

**Known Issues:**
- Templates not found if filename mismatched (✅ all fixed)
- Missing required fields cause incomplete notes (✅ added Stable ID)
- Task script removed (no task template)

**Troubleshooting:**
1. Check config file: `vault/.obsidian/plugins/quickadd/config.yaml`
2. Verify template paths are relative to vault root
3. Restart QuickAdd plugin after config changes

---

## Optional Plugins

### 6. Kanban

**Why:** Visual board for tracking legislation progress (if using kanban method).

**Installation:** Search "Obsidian Kanban" in Community plugins

**Configuration:**
- [x] Enable if using kanban boards
- [ ] Not required for basic StenoMD operation

---

### 7. Excalidraw

**Why:** Create diagrams for committee structures, relationships.

**Installation:** Search "Obsidian Excalidraw Plugin"

**Configuration:**
- [x] Enable if using drawings
- [ ] Not required for basic StenoMD operation

---

### 8. Advanced Tables

**Why:** Better table editing, sorting, alignment.

**Installation:** Search "Advanced Tables"

**Configuration:** Default settings work

**Test:** Edit any markdown table (e.g., in a deputy note)

- ✅ Table editing improved
- ✅ Column alignment works

---

## Validation Tests

### Run these checks after installation:

**Test A: Dataview Integration**
```dataview
TABLE stable_id, party, speeches_count
FROM "politicians/deputies"
WHERE speeches_count > 10
LIMIT 5
```
- ✅ Executes without errors

**Test B: Metadata Menu Sync**
1. Open a deputy note
2. Change `party` field via Metadata Menu
3. Switch to reading view - verify change reflected

- ✅ Changes persist

**Test C: Calendar Links**
1. Open Calendar
2. Find a date with session file
3. Click - should navigate to session

- ✅ Calendar navigation works

**Test D: QuickAdd Creation**
1. Create new deputy via QuickAdd
2. Verify file created in correct folder
3. Open file - check frontmatter

- ✅ New notes created correctly

---

## Health Check Summary

| Category | Status | Notes |
|----------|--------|-------|
| All essential plugins installed | ⬜ | Dataview, Metadata Menu required |
| Plugin versions current | ⬜ | Check Community plugins section |
| Dataview queries work | ⬜ | Run Test A |
| Metadata Menu functional | ⬜ | Run Test B |
| Calendar configured | ⬜ | Run Test C |
| QuickAdd workflows | ⬜ | Run Test D |
| No console errors | ⬜ | Ctrl+Shift+I, check for red errors |
| All templates found | ⬜ | No "Template not found" warnings |

---

## Common Issues & Solutions

### "Dataview not found" or "Block contains invalid code"
**Fix:** Enable Dataview plugin: Settings → Core plugins → Dataview

### "No results" from queries
**Fix:**
1. Check files exist in correct folders
2. Verify frontmatter YAML syntax (use online YAML validator)
3. Restart Obsidian
4. Reset Dataview cache

### QuickAdd "Template not found"
**Fix:**
1. Verify template file exists: `vault/_templates/politician.md`
2. Check config path: `_templates/politician.md` (correct)
3. Path is relative to vault root, NOT `.obsidian/`

### Metadata Menu not showing fields
**Fix:**
1. Settings → Metadata Menu → Configure
2. Add fields for each note type:
   - For deputies: `stable_id`, `party`, `constituency`, `idm`, `speeches_count`, `committees`
3. Restart plugin

### Calendar not showing session links
**Fix:**
1. Settings → Calendar → Set folder to `sessions`
2. Ensure session files have `date:` field in YYYY-MM-DD format
3. Restart Calendar plugin

### Special characters (Ă, Ș, Ţ) display incorrectly
**Fix:** This is normal in Obsidian's markdown preview. The files are correct. Use Reading view for proper display.

---

## Next Steps After Validation

1. ✅ All plugins installed and configured
2. ✅ All checklist items checked
3. ✅ No errors in console (Ctrl+Shift+I)
4. ✅ Dataview test suite passes (see `DATAVIEW_TESTS.md`)
5. ✅ QuickAdd workflows tested with sample data

**Then proceed to:** Phase 2 - Graphify Reprocessing

---

## Version Info

**StenoMD Vault Version:** 2.0
**Docs Date:** 2026-04-27
**Compatible with Obsidian:** 1.5+
**Required Plugin Versions:**
- Dataview: 1.12.0+
- Metadata Menu: 0.8.0+
- QuickAdd: 1.6.0+

Check plugin versions in Settings → Community plugins → Installed

---

**Maintained by:** StenoMD Project
**Last updated:** 2026-04-27
