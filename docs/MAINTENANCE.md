# StenoMD Maintenance Guide

This document describes routine maintenance tasks to keep StenoMD healthy and up-to-date.

---

## Daily / Weekly Tasks

### 1. Update Knowledge Graph
Whenever you add or edit vault files (politicians, sessions, laws), refresh the canonical KG:

```bash
python3 scripts/merge_vault_to_kg.py
```

This updates `knowledge_graph/entities.json` and `knowledge_graph.db`. Run after any vault changes.

---

### 2. Check Health Score
Quick health diagnostics:

```bash
python3 scripts/planner_agent.py --health
```

Review the output. If score drops below 95, investigate:
- Missing data in KG? Re-run merge.
- Scraper errors? Check logs.
- Test failures? Run pytest.

---

### 3. Scrape New Sessions
To fetch the latest parliamentary sessions:

```bash
# Chamber (CDEP) – last 30 session IDs
python3 scripts/agents/cdep_agent.py --max-id 50 --years 2024,2025,2026

# Senate
python3 scripts/agents/senat_agent.py --max 30 --year 2026
```

Use `--dry-run` to preview. Use `--sync-vault` to save to vault and update KG automatically.

---

### 4. Enrich Data
If new deputies or senators appear, enrich their profiles:

```bash
# Deputies from Open Parliament data
python3 scripts/fix_deputy_data_from_op.py

# Senators (if source available)
python3 scripts/enrich_senator_data.py
```

---

##Monthly Tasks

### 5. Regenerate Graphify Overlay
The Graphify analytical graph is not auto-updated. Rebuild it periodically:

```bash
python3 scripts/build_vault_graph_fixed.py
```

Outputs in `Graphify/graphify-out/`: `graph.html`, `graph.json`, `GRAPH_REPORT.md`.

---

### 6. Rotate Backups
Create a backup of the vault and knowledge graph before major changes:

```bash
tar -czf backups/backup-$(date +%Y%m%d).tar.gz vault/ knowledge_graph/
```

Keep at least 3 recent backups.

---

## Troubleshooting

### KG entities.json empty or outdated
Run merge script (see above). If errors persist, check that vault files have valid frontmatter.

### API returns 500 errors
Ensure `knowledge_graph.db` exists and `knowledge_graph/entities.db` symlink points to it. If missing:
```bash
cd knowledge_graph
ln -sf knowledge_graph.db entities.db
```

### Tests fail after config changes
Run `pytest` from project root. If coverage unexpectedly low, verify that `# pragma: no cover` is used appropriately (only for boilerplate, I/O, external calls). Do not pragma core logic.

### Scrapers rate-limited or failing
Adjust `MIN_DELAY` and `MAX_DELAY` in the scraper scripts. Respectful delays avoid bans. Consider running scrapers during off-hours.

---

## Upgrade Procedure

When updating the codebase from Git:

1. Pull latest changes: `git pull origin main`
2. Check for migration needs in `docs/MIGRATION.md`.
3. If `scripts/config.py` changed, ensure environment variables are set appropriately.
4. Re-run `merge_vault_to_kg.py` to sync any new vault template changes.
5. Run `pytest` to verify all tests pass.

---

## Performance Monitoring

To measure scraping throughput:

```bash
time python3 scripts/agents/cdep_agent.py --max-id 10
```

Target: 5-10 sessions per minute. If slower:
- Reduce `MAX_WORKERS` (parallelization) if you hit rate limits.
- Increase `MIN_DELAY` to be more polite.
- Use a faster internet connection.

---

## Security Checklist

- Keep `ALLOWED_ORIGIN` restricted to localhost or trusted domains.
- Do not expose REST API to the public internet without authentication.
- Regularly audit `scripts/query/rest_api.py` for SQL injection — all queries should use parameterized statements.
- Never commit `.env` files or API keys.

---

## Obsolete / Deprecated Scripts

Some scripts are no longer used:
- `stenomd_scraper.py` – replaced by `agents/cdep_agent.py` and `senat_agent.py`
- `run_daily.py` – orchestrator now handled by daily pipeline
- `dashboard.py` – moved to vault `_brain/Dashboard.md`

Do not remove until confirmed safe.

---

## Support

For issues, consult:
- `docs/API_REFERENCE.md`
- `docs/DEVELOPMENT.md`
- `docs/TROUBLESHOOTING.md` (if exists)
- GitHub Issues: https://github.com/nedaktov-ops/StenoMD/issues
