---
title: QuickAdd Setup
description: Instructions for installing and using QuickAdd workflows
category: docs
---

# QuickAdd Setup for StenoMD

This note describes how to set up the QuickAdd plugin for fast note creation in the StenoMD vault.

## Overview

QuickAdd allows you to create new politicians, laws, and sessions with a single hotkey. It uses the `create_note.py` script to generate properly formatted markdown files with frontmatter.

## Installation

1. Ensure the QuickAdd plugin is installed in Obsidian.
2. Copy the provided configuration:
   ```bash
   cp ../config/quickadd-config.json .obsidian/plugins/quickadd/quickadd-config.json
   ```
   (Adjust paths as needed.)
3. Restart Obsidian or reload plugins.

## Available Hotkeys

- `Ctrl+Shift+D` — Create Deputy
- `Ctrl+Shift+S` — Create Senator
- `Ctrl+Shift+L` — Create Law
- `Ctrl+Shift+E` — Create Session

Each hotkey opens a prompt, you fill in the required fields, and the note appears in the appropriate vault folder.

## What Gets Created

- **Deputy/Senator**: Note in `politicians/deputies/` or `politicians/senators/` with basic frontmatter (name, type, chamber, legislature, source, speeches_count=0, laws_proposed=0, committees=[], party=Unknown, etc.). Stable ID and IDM are left blank for later enrichment.
- **Law**: Note in `laws/` with `law_number`, `title`, and empty `sponsors` and `process_stage`.
- **Session**: Note in `sessions/{chamber}/` with `date`, `chamber`, `deputy_count=0`, `speech_count=0`.

## After Creation

- Run `python3 scripts/merge_vault_to_kg.py` to update `knowledge_graph/entities.json`.
- Optionally run `python3 scripts/build_vault_graph_fixed.py` to regenerate the Graphify graph.
- Enrich deputy/senator data later using `fix_deputy_data_from_op.py` and `add_committees.py`.

## Configuration File

The QuickAdd config is located at `config/quickadd-config.json`. Feel free to modify prompts or add new contexts.

## Troubleshooting

- If hotkeys don't work, check that no other plugin conflicts.
- If notes are not created, ensure the script path `{{vault}}/../scripts/create_note.py` is correct relative to your vault.
- Check Obsidian console (`Ctrl+Shift+I`) for errors.
