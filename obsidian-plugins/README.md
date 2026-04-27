# StenoMD Obsidian Plugins

Copied and verified Obsidian plugins for StenoMD integration.

## Plugins (7 verified)

| Plugin | Size | Purpose |
|--------|------|--------|
| copilot | 5.3MB | PRIMARY AI - Chat, semantic search |
| dataview | 1.2MB | Live queries on frontmatter |
| quickadd | 4.1MB | Quick capture commands |
| templater | 0.3MB | Template processing |
| omnisearch | 0.6MB | Enhanced search |
| obsidian-git | 0.7MB | Backup automation |
| metadata-menu | 1.0MB | Frontmatter management |

## Usage

```bash
# Verify plugins
python3 scripts/obsidian_plugin_manager.py --verify

# List plugins
python3 scripts/obsidian_plugin_manager.py --list
```

## Bridge Scripts

Located in `integration/`:

- `copilot-bridge.py` - Sync vault ↔ ai-memory ↔ MemPalace
- `kg-export.py` - Export knowledge graph for AI
- `vault-sync.py` - Plugin ↔ vault sync

## Integration Points

- Copilot memory: `vault/ai-memory/`
- Knowledge Graph: `knowledge_graph/entities.json`
- MemPalace: `knowledge_graph/mempalace/`

## Status

- Phase 1: ✅ COMPLETE

---
Updated: 2026-04-27