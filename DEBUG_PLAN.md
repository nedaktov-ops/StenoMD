# StenoMD Debug Plan
## Last Updated: 2026-04-24 - Comprehensive Audit

---

## 📊 PROJECT STATUS SUMMARY

| Metric | Value | Status |
|--------|-------|--------|
| Senators | 5 | ✅ WORKING |
| Deputies | 126 | ✅ WORKING |
| Senate Sessions | 20 | ✅ WORKING |
| Deputy Sessions | 24 | ✅ WORKING |
| Knowledge Graph Entities | 0 | ❌ BROKEN |
| Dashboard | http://localhost:8080 | ✅ UPDATED |
| MP Profiles | 0 | ❌ BROKEN |
| Scraper Agents | 2 | ✅ WORKING |

---

## 🔴 COMPREHENSIVE AUDIT FINDINGS (2026-04-24)

### Working Components
1. **CDEP Agent** (`cdep_agent.py`) - Session discovery, MP extraction, law detection ✅
2. **Senate Agent** (`senat_agent.py`) - ASP.NET form handling, senator extraction ✅
3. **Data Validator** (`validators.py`) - Duplicate detection, metadata parsing ✅
4. **Dashboard API** - All endpoints working ✅
5. **Vault Sessions** - 17 deputy + 9+ senate sessions saved ✅

### Broken Components
1. **Knowledge Graph** - Disconnected from scrapers, entities.json empty ❌
2. **MP Profiles** - No files created despite scraping ❌
3. **Dashboard-KG Connection** - Shows empty stats ❌
4. **Daily Pipeline** - Uses deprecated scraper ❌

---

## 🔴 CRITICAL ISSUES

### CRITICAL-001: Knowledge Graph Disconnected - FIXED ✅
**Problem:** Scraper agents and KG were NOT connected, entities.json was empty
**Solution:** Created `scripts/merge_vault_to_kg.py` to populate KG from existing vault files
**Result:** KG now has 128 persons, 38 sessions
**Verification:**
```bash
python3 scripts/merge_vault_to_kg.py
# Output: KG: 128 persons, 38 sessions, 0 laws
curl -s http://localhost:8080/api/stats | jq .kg_persons, .kg_sessions
# Output: 128, 38
```

---

### CRITICAL-002: MP Profiles Not Created
**Problem:** Despite scraping MPs, no MP files exist
**Evidence:**
```
vault/politicians/deputies/   <- EMPTY
vault/politicians/senators/   <- EMPTY
```
**Root Cause:** `_save_mp_note()` is either:
- Not being called properly
- Failing silently

**Fix Required:**
1. Add debug output to `_save_mp_note()`
2. Verify method is called in scraping flow

---

### CRITICAL-003: Dashboard Stats Not Refreshing - FIXED ✅
**Problem:** Numbers didn't update after scraping operations
**Solution:** 
1. Replaced page reload with `refreshStats()` call
2. Added cache busting to API endpoint
3. Added KG stats update
4. Added normalizeMistralResponse helper
**Result:** Dashboard refreshes stats without page reload
**Files Modified:** `scripts/dashboard.py`

---

## 🟠 HIGH PRIORITY ISSUES

### HIGH-001: Daily Pipeline Uses Deprecated Scraper
**File:** `scripts/run_daily.py`
**Problem:** Calls `stenomd_scraper.py` (deprecated) instead of `agents/cdep_agent.py`
**Fix Required:** Update to use canonical agent

### HIGH-002: Empty/Placeholder Session Files
**Files to Remove:**
- `sessions/deputies/20260421.md` (empty)
- `sessions/deputies/20260423.md` (empty)
- `sessions/senate/20260422.md` (empty)
- `sessions/*/Unknown.md` (placeholder)

### HIGH-003: Mixed Date Formats in Sessions
**Issue:** Date sorting broken
| Format | Status |
|--------|--------|
| ISO 8601 (`2024-11-05.md`) | ✅ CORRECT |
| Romanian (`11-martie-2026.md`) | ⚠️ NEEDS MIGRATION |
| YYYYMMDD (`20260422.md`) | ❌ BROKEN |

---

## 🟡 MEDIUM PRIORITY ISSUES

### MEDIUM-001: Code Quality - Silent Failures
**Locations:**
- `get_statistics()` line 82-84 - catches all exceptions silently
- `update_knowledge_graph.py` - bare `except: pass`
- Multiple agents - no error logging

### MEDIUM-002: Path Hardcoding
**Files:**
- `dashboard.py` lines 16-20 - hardcoded paths
- `sync_vault.py` lines 8-9 - hardcoded paths
- Should use relative paths from project root

### MEDIUM-003: Duplicate Scraping Scripts
**Issue:** 3 scripts do same thing
| Script | Status |
|--------|--------|
| `scrape_cdep.py` | DUPLICATE |
| `stenomd_scraper.py` | DUPLICATE |
| `agents/cdep_agent.py` | CANONICAL ✅ |

---

## 🧪 DEBUGGING STRATEGY

### Phase 1: Diagnostics (Completed)
```bash
# Check entities.json
cat knowledge_graph/entities.json

# Count politician locations
echo "Root politicians: $(ls vault/politicians/*.md 2>/dev/null | wc -l)"
echo "Deputy politicians: $(ls vault/politicians/deputies/*.md 2>/dev/null | wc -l)"

# Check dashboard
curl -s http://localhost:8080/api/stats
```

### Phase 2: Fix Execution Order

| Step | Action | Status | Notes |
|------|--------|--------|-------|
| 2.1 | Fix dashboard refresh | ✅ DONE | refreshStats() now works |
| 2.2 | Add debug logging to agents | ⏳ NEXT | Track MP profile creation |
| 2.3 | Fix entities.json population | ⏳ PENDING | Debug update_knowledge_graph() |
| 2.4 | Remove empty/placeholder files | ⏳ PENDING | Cleanup vault |
| 2.5 | Update run_daily.py | ⏳ PENDING | Use canonical agents |
| 2.6 | Fix date formats | ⏳ PENDING | Migrate to ISO |
| 2.7 | Verify all stats | ⏳ PENDING | End-to-end test |

### Phase 3: Verification Tests
```bash
# Test 1: Entities populated
python3 -c "import json; d=json.load(open('knowledge_graph/entities.json')); print(f'Persons: {len(d[\"persons\"])}')"

# Test 2: Dashboard stats
curl -s http://localhost:8080/api/stats | python3 -m json.tool

# Test 3: No empty files
find vault/sessions -name '*.md' -empty
```

---

## 🔧 FIX COMMANDS

### Fix 1: Remove Empty Files
```bash
find vault/sessions -name '*.md' -empty -delete
find vault/sessions -name 'Unknown.md' -delete
```

### Fix 2: Update Daily Pipeline
```bash
# Replace stenomd_scraper.py with cdep_agent.py in run_daily.py
```

### Fix 3: Knowledge Graph Merge
```bash
python3 scripts/stenomd_master.py --merge
```

### Fix 4: Verify Dashboard
```bash
curl -s http://localhost:8080/api/stats
```

---

## ✅ FIXES APPLIED (2026-04-24)

| ID | Fix | Status | File |
|----|-----|--------|------|
| FIX-024 | Dashboard refresh fix | ✅ DONE | dashboard.py |
| FIX-025 | Remove alert from refreshStats | ✅ DONE | dashboard.py |
| FIX-026 | Replace page reload with refreshStats() | ✅ DONE | dashboard.py |
| FIX-027 | Add cache busting | ✅ DONE | dashboard.py |
| FIX-028 | Add normalizeMistralResponse | ✅ DONE | dashboard.py |
| FIX-029 | Backup dashboard | ✅ DONE | dashboard.py.backup.2026-04-24 |

---

## 🎯 SUCCESS CRITERIA

After executing debug plan:
- [ ] entities.json contains persons, sessions, laws
- [ ] MP profiles created in vault
- [ ] Dashboard refresh works without page reload
- [ ] No empty/Unknown.md files
- [ ] Daily pipeline uses canonical agents
- [ ] All date formats in ISO

---

## 📋 REVERT INSTRUCTIONS

If dashboard breaks:
```bash
cp scripts/dashboard.py.backup.2026-04-24 scripts/dashboard.py
python3 scripts/dashboard.py
```

---

## 📁 RELEVANT FILES

| File | Purpose | Status |
|------|---------|--------|
| `scripts/dashboard.py` | Web dashboard | UPDATED ✅ |
| `scripts/agents/cdep_agent.py` | CDEP scraper | WORKING |
| `scripts/agents/senat_agent.py` | Senate scraper | WORKING |
| `scripts/validators.py` | Validation | WORKING |
| `scripts/run_daily.py` | Daily pipeline | NEEDS UPDATE |
| `knowledge_graph/entities.json` | KG data | EMPTY ❌ |
| `knowledge_graph/mempalace/` | MemPalace KG | NOT CONNECTED |

---

## 🔗 REFERENCES

- **Dashboard:** http://localhost:8080
- **GitHub:** https://github.com/nedaktov-ops/StenoMD
- **DevstralUpdates.md:** Logs all Devstral changes

---

## 🧠 PLANNER AGENT INTEGRATION

The planner agent (`scripts/planner_agent.py`) should be used for:
1. `--health` - Quick health check
2. `--manual` - Full analysis
3. `--deep` - Comprehensive audit
4. `--recall` - Find similar past issues

Usage:
```bash
python3 scripts/planner_agent.py --health
python3 scripts/planner_agent.py --manual
```

---

*End of Debug Plan*
*Next update: After Phase 2 fixes applied*
*Last Audit: 2026-04-24*