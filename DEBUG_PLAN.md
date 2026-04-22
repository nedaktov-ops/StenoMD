# StenoMD Debug Plan
## Last Updated: 2026-04-22 03:30

---

## ✅ BUGS FIXED

### Critical Fixes

| ID | Bug | Fix | File |
|----|-----|-----|------|
| FIX-001 | requirements.txt missing beautifulsoup4 | Added `beautifulsoup4>=4.12.0` | requirements.txt |
| FIX-002 | stenomd_master.py wrong signature | `run(years=[year], max_id=max_sessions)` | stenomd_master.py |
| FIX-003 | Senator malformed filenames | Added name filtering + split | senat_agent.py |
| FIX-004 | Wrong vault paths | Updated to `politicians/senators/` | senat_agent.py |
| FIX-005 | soup.title AttributeError | Added try/except | update_knowledge_graph.py |

---

## 🔴 REMAINING ISSUES

### High Priority

| ID | Issue | Impact | Workaround |
|----|-------|--------|-----------|
| ISSUE-001 | CDEP `max_id=3` returns 0 | Blocked scraping | Use `max_id=100+` |
| ISSUE-002 | entities.json empty | KG not populated | Run `--merge` after scrape |

### Medium Priority

| ID | Issue | Impact | Workaround |
|----|-------|--------|-----------|
| ISSUE-003 | Senate historical blocked | No 2020-2024 data | Use cached data |
| ISSUE-004 | CDEP vault sync missing | deputies/ sessions empty | Manual sync |

### Low Priority (Known Limitations)

| ID | Limitation | Impact | Notes |
|----|----------|--------|-------|
| LIMIT-001 | Senate only 2026+ | Historical not available | Website limitation |
| LIMIT-002 | CDEP calendar slow | ~3 sec per ID | Random delays added |

---

## 📋 RECOMMENDED COMMANDS

```bash
# Full CDEP extraction (2024-2026)
cd /home/adrian/Desktop/NEDAILAB/StenoMD
python3 scripts/agents/cdep_agent.py --years 2024,2025,2026 --max-id 100

# Senate for current sessions
python3 scripts/agents/senat_agent.py --year 2024 --max 10 --sync-vault

# Master controller (all in one)
python3 scripts/stenomd_master.py --all --max 50 --sync-vault --merge

# Check status
python3 scripts/stenomd_master.py --status
```

---

## 🧪 VERIFICATION RESULTS

| Component | Status | Notes |
|-----------|--------|-------|
| requirements.txt | ✅ | beautifulsoup4 added |
| stenomd_master.py | ✅ | Correct signature |
| senat_agent.py | ✅ | Name filtering works |
| cdep_agent.py | ✅ | 22 MPs from 5 sessions |
| update_knowledge_graph.py | ✅ | Error handling added |
| Syntax check | ✅ | All files pass |

---

## 📁 FILES MODIFIED

1. `requirements.txt` - Added dependencies
2. `scripts/stenomd_master.py` - Fixed function call
3. `scripts/agents/senat_agent.py` - Multiple fixes
4. `scripts/update_knowledge_graph.py` - Error handling
5. `STRATEGY.md` - Debug plan added
6. `project-logs.md` - Updated with fixes

---

## 🚀 NEXT STEPS

1. [ ] Run CDEP with `max_id=100` for full 2024 data
2. [ ] Run Senate for fresh 2026 sessions
3. [ ] Verify entities.json population
4. [ ] Create CDEP session sync to vault
5. [ ] Test GitHub Actions workflow

---

*End of Debug Plan*