# Migration Guide

This guide helps users upgrade from earlier versions of StenoMD to the current version (v3.x).

## Upgrading to v3.0

v3.0 introduces a centralized configuration system, a canonical Mem Palace knowledge graph, and a split between vault and analytical Graphify overlay.

### Step-by-Step Upgrade

1. **Backup your vault** before making any changes.

2. **Pull the latest code**:

   ```bash
   git pull origin main
   ```

3. **Install new dependencies** (if not already installed):

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables** (optional):

   - `STENOMD_DIR`: Override project root if needed.
   - `STENOMD_ALLOWED_ORIGIN`: Set for REST API CORS (default: localhost).
   - See `scripts/config.py` for full list.

5. **Run configuration sanity check**:

   ```bash
   python3 scripts/config.py
   ```

   All required directories should be found.

6. **Merge vault changes**:

   The knowledge graph schema changed in v3.0. After pulling, run:

   ```bash
   python3 scripts/kg/schema_migrate.py
   ```

   This updates `knowledge_graph.db` to the latest schema.

7. **Re-sync entities.json**:

   The canonical Mem Palace (`knowledge_graph/entities.json`) is now the source of truth for the API. Regenerate it from your vault:

   ```bash
   python3 scripts/merge_vault_to_kg.py
   ```

8. **Recreate `entities.db` symlink if missing**:

   The API expects `knowledge_graph/entities.db` to point to `knowledge_graph.db`. Create symlink:

   ```bash
   cd knowledge_graph
   ln -sf knowledge_graph.db entities.db
   ```

9. **Update custom scripts**:

   If you have local scripts that import `config` or use project paths, ensure they import from `scripts.config` and use `PROJECT_ROOT` rather than hardcoded strings. See `docs/DEVELOPMENT.md` for guidelines.

10. **Test the API**:

    ```bash
    python3 scripts/query/rest_api.py --port 5000
    curl http://localhost:5000/api/health
    ```

    Should return `{"status":"healthy","version":"3.0.0"}`.

11. **Regenerate Graphify overlay** (optional):

    The Graphify graph is analytical and should be regenerated on demand:

    ```bash
    python3 scripts/build_vault_graph_fixed.py
    ```

12. **Verify vault templates**: Ensure your markdown notes contain the required frontmatter fields described in `docs/TEMPLATES.md`. Missing fields may affect queries.

---

## Version History

### v3.0 (2026-04-28)

- Centralized configuration (`scripts/config.py`)
- Canonical Mem Palace (`knowledge_graph/entities.json`)
- API security hardening (CORS restricted, parameterized SQL)
- Planner agent v2 with self-learning
- Graphify as separate analytical overlay
- Comprehensive test suite (45+ tests)

### v2.5 (2026-04-25)

- Brain architecture: AI-friendly fields in profiles.
- QuickAdd workflows.
- FastAPI REST API introduced.

### v2.0 (2026-04-20)

- Vault-based storage with markdown frontmatter.
- Knowledge graph extraction from vault.
- Entity resolution and position classification.

### v1.0 (2025-12)

- Initial cdep.ro scraping and session storage.

---

## Common Issues

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `ImportError: No module named 'config'` | Running script from wrong directory | Use `python3 scripts/...` or ensure `scripts/` is on PYTHONPATH |
| API returns 500 errors | `knowledge_graph.db` schema outdated | Run `schema_migrate.py` |
| `entities.json` is empty | Merge not run | `python3 scripts/merge_vault_to_kg.py` |
| Graphify graph missing nodes | Vault not synced | Re-run `build_vault_graph_fixed.py` |
| Missing fields in profiles | Templates outdated | Update files to match `docs/TEMPLATES.md` |

---

## Future Migrations

Future versions may introduce changes to the vault schema or Graphify format. Always read release notes before upgrading.
