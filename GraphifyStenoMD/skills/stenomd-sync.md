# StenoMD Sync Skill

**Trigger:** `/stenomd sync`
**Purpose:** Sync graph with vault (on demand, manual trigger)

---

## Usage

```
/stenomd sync                           # Show sync options
/stenomd sync --dry-run               # Show what would sync
/stenomd sync --to-graph              # Vault -> graph
/stenomd sync --to-vault              # Graph -> vault
/stenomd sync --validate              # Validate only
/stenomd sync --backup              # Create backup first
```

---

## What It Does

1. **Validates** both vault and graph consistency
2. **Compares** entities between systems
3. **Reports differences** (dry-run mode)
4. **Syncs on demand** with manual confirmation

---

## Sync Types

| Type | Direction | Description |
|------|-----------|-------------|
| `--to-graph` | Vault → Graph | Add vault entities to graph |
| `--to-vault` | Graph → Vault | Add graph edges to vault |
| `--validate` | Both | Check consistency only |

---

## Example Output

### Dry Run
```
/stenomd sync --dry-run

=== Vault entities ===
Politicians: 944
Sessions: 2131
Laws: 1976

=== Graph entities ===
Nodes: 16834
Edges: 25094

=== Differences ===
New politician profiles: 0
New sessions: 0
New laws: 0

=== Would sync ===
Nothing to sync (OptionB: manual confirmation required)
```

### Validation
```
/stenomd sync --validate

=== Validation Results ===
✓ All politician links resolve
✓ All session links resolve
✓ All law links resolve
✓ YAML frontmatter valid
✗ 12 politicians missing party data
✗ 234 politicians missing speeches_count
✓ Graph structure valid
```

---

## Safety Features

- **Dry-run default**: No changes without --confirm
- **Backup option**: Always creates backup first
- **Validation first**: Checks before applying
- **OptionB**: Manual trigger only

---

## Notes

- Does NOT auto-sync (OptionB design)
- Requires manual confirmation
- Creates backup before any changes
- Logs all sync operations