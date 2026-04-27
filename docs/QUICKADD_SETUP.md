# QuickAdd Setup for StenoMD

This guide explains how to install the QuickAdd configuration for rapid note creation.

## Prerequisites

- Obsidian with QuickAdd plugin (v2.12.0+) installed and enabled.
- Vault open at `StenoMD/vault`.

## Installation

1. **Copy the configuration file:**
   ```bash
   cp config/quickadd-config.json .obsidian/plugins/quickadd/quickadd-config.json
   ```
   Create the target directory if it doesn't exist:
   ```bash
   mkdir -p .obsidian/plugins/quickadd
   ```

2. **Restart Obsidian** or reload plugins (`Ctrl+P` → "Reload plugins without saving").

3. Verify that the QuickAdd contexts appear in the command palette (`Ctrl+P` → "QuickAdd: Select context").

## QuickAdd Contexts

Four contexts are provided:

| Context | Hotkey | What it creates |
|---------|--------|-----------------|
| QuickAdd Deputy | Ctrl+Shift+D | A new deputy note in `politicians/deputies/` |
| QuickAdd Senator | Ctrl+Shift+S | A new senator note in `politicians/senators/` |
| QuickAdd Law | Ctrl+Shift+L | A new law note in `laws/` |
| QuickAdd Session | Ctrl+Shift+E | A new session note in `sessions/{chamber}/` |

Each context prompts for necessary fields (name, number, title, date) and creates a markdown file with minimal frontmatter. Fields like `stable_id`, `idm`, `party`, etc., are set to empty or default values to be filled later via enrichment scripts (e.g., `fix_deputy_data_from_op.py`).

## Usage

1. Trigger a context via hotkey or `Ctrl+P` → "QuickAdd: Select context".
2. Fill the prompted values.
3. A new note is created automatically in the appropriate vault subfolder.
4. Optionally run `merge_vault_to_kg.py` to update `knowledge_graph/entities.json`.
5. Optionally regenerate the Graphify graph: `python3 scripts/build_vault_graph_fixed.py`.

## Notes

- Deputy and Senator names are converted to kebab-case for filename (e.g., "Vasile Daniel Suciu" → `vasile-daniel-suciu.md`).
- Law filenames use the law number slug (e.g., "20/2026" → `20-2026.md`). This matches existing naming.
- Session notes are placed under `sessions/{chamber}/` with pattern `session-YYYY-MM-DD.md`.
- After creation, you can enrich deputy/senator data by running scheduled scrapers or the enrichment agent.
