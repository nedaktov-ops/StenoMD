# StenoMD Debug Plan
## Last Updated: 2026-04-23 14:30

---

## 📊 PROJECT STATUS SUMMARY

| Metric | Value | Status |
|--------|-------|--------|
| Senators | 5 | ✅ |
| Deputies | 126 | ✅ |
| Senate Sessions | 20 | ✅ |
| Deputy Sessions | 24 | ✅ |
| Knowledge Graph Entities | 76 | ⚠️ |
| Dashboard | http://localhost:8080 | ✅ |

---

## 🔴 CRITICAL ISSUES

### ISSUE-001: entities.json Empty Despite Vault Data
**ID:** CRITICAL-001
**Impact:** Knowledge graph not populated, dashboard shows empty stats
**Root Cause:** Merge function not running or not finding vault files
**Evidence:**
```json
// knowledge_graph/entities.json
{
  "persons": [],
  "sessions": [],
  "laws": []
}
```
**Fix Required:**
1. Verify `merge_knowledge_graph()` in stenomd_master.py reads vault files
2. Check that vault file paths match expected paths
3. Ensure entities.json is writable

---

### ISSUE-002: Duplicate Politician Files
**ID:** CRITICAL-002
**Impact:** Data duplication, confusion about canonical source
**Location:** `vault/politicians/` root vs `deputies/` subdirectory
**Files Affected:** ~85 files exist in both locations

**Example:**
- `vault/politicians/Adrian-Echert.md` (root - DEPRECATED)
- `vault/politicians/deputies/Adrian-Echert.md` (subdir - CANONICAL)

**Fix Required:**
1. Run `migrate_vault.py` to consolidate root files to subdirectories
2. Delete deprecated root-level politician files
3. Update .gitignore to prevent re-addition

---

## 🟠 HIGH PRIORITY ISSUES

### ISSUE-003: Mixed Date Formats in Sessions
**ID:** HIGH-001
**Impact:** Date sorting and querying broken
**Location:** `vault/sessions/senate/`

| Format | Example | Status |
|--------|---------|--------|
| ISO 8601 | `2024-11-05.md` | ✅ CORRECT |
| Romanian | `11-martie-2026.md` | ⚠️ NEEDS MIGRATION |
| YYYYMMDD | `20260422.md` | ❌ BROKEN |

**Fix Required:**
1. Run `migrate_dates.py` to convert Romanian to ISO
2. Rename YYYYMMDD files to proper ISO format
3. Verify date parsing in `validators.py`

---

### ISSUE-004: Empty/Invalid Session Files
**ID:** HIGH-002
**Impact:** Placeholder files clutter vault, confuse queries
**Location:** `vault/sessions/deputies/`, `vault/sessions/senate/`

**Files to Remove:**
- `sessions/deputies/20260421.md` (14 lines, empty)
- `sessions/deputies/20260423.md` (14 lines, empty)
- `sessions/senate/20260422.md` (14 lines, empty)
- `sessions/deputies/Unknown.md` (placeholder)
- `sessions/senate/Unknown.md` (placeholder)

**Fix Required:**
```bash
rm vault/sessions/deputies/20260421.md
rm vault/sessions/deputies/20260423.md
rm vault/sessions/senate/20260422.md
rm vault/sessions/*/Unknown.md
```

---

### ISSUE-005: Duplicate Scraping Scripts
**ID:** HIGH-003
**Impact:** Code confusion, maintenance burden
**Location:** `scripts/`

| Script | Purpose | Status |
|--------|---------|--------|
| `scrape_cdep.py` | Basic CDEP scrape | DUPLICATE |
| `stenomd_scraper.py` | Enhanced CDEP | DUPLICATE |
| `agents/cdep_agent.py` | Full-featured agent | **CANONICAL** |

**Recommended Actions:**
1. Mark `scrape_cdep.py` and `stenomd_scraper.py` as deprecated
2. Add deprecation warnings to these scripts
3. Update documentation to reference `cdep_agent.py`

---

## 🟡 MEDIUM PRIORITY ISSUES

### ISSUE-006: Duplicate Politician Names
**ID:** MEDIUM-001
**Impact:** Conflicting vault notes for same person
**Location:** `vault/politicians/`

**Example:**
- `Daniel-Razvan-Biro.md` (without diacritics)
- `Daniel-Răzvan-Biro.md` (with diacritics)

**Fix Required:**
1. Detect duplicates with normalized names
2. Merge content from both files
3. Delete duplicate entry

---

### ISSUE-007: .gitignore Excludes entities.json
**ID:** MEDIUM-002
**Impact:** Essential KG data not versioned
**Location:** `.gitignore` line 10

**Current:**
```
knowledge_graph/entities.json
```

**Issue:** This file contains scraped data that should be tracked

**Recommendation:** Remove from .gitignore OR establish clear data management strategy

---

## 🟢 LOW PRIORITY (KNOWN LIMITATIONS)

### LIMIT-001: Senate Historical Data BLOCKED
**Impact:** Cannot scrape 2020-2024 Senate sessions
**Cause:** senat.ro only shows current legislature
**Workaround:** Use cached CDEP data for historical

### LIMIT-002: Rate Limiting Required
**Impact:** ~3-5 seconds per session
**Workaround:** Random delays in agents

---

## 🧪 DEBUGGING STRATEGY

### Phase 1: Diagnostics
Run these commands to diagnose issues:

```bash
# 1. Check entities.json status
cat knowledge_graph/entities.json | python3 -m json.tool

# 2. Count politician locations
echo "Root politicians: $(ls vault/politicians/*.md 2>/dev/null | wc -l)"
echo "Deputy politicians: $(ls vault/politicians/deputies/*.md 2>/dev/null | wc -l)"
echo "Senator politicians: $(ls vault/politicians/senators/*.md 2>/dev/null | wc -l)"

# 3. Check date format distribution
echo "ISO dates: $(ls vault/sessions/*/*.md | grep -E '[0-9]{4}-[0-9]{2}-[0-9]{2}' | wc -l)"
echo "Romanian dates: $(ls vault/sessions/*/*.md | grep -E '[0-9]+-[a-z]+-[0-9]{4}' | wc -l)"
echo "YYYYMMDD dates: $(ls vault/sessions/*/*.md | grep -E '^[0-9]{8}\.md$' | wc -l)"

# 4. Check for empty/placeholder files
echo "Empty files: $(find vault/sessions -name '*.md' -empty | wc -l)"
echo "Unknown files: $(find vault/sessions -name 'Unknown.md' | wc -l)"

# 5. Dashboard health check
curl -s http://localhost:8080/api/stats | python3 -m json.tool
```

### Phase 2: Fix Execution Order

| Step | Action | Priority | Estimated Time |
|------|--------|----------|----------------|
| 2.1 | Remove empty/placeholder files | HIGH | 1 min |
| 2.2 | Run date migration | HIGH | 2 min |
| 2.3 | Consolidate root politicians | CRITICAL | 5 min |
| 2.4 | Run merge to populate entities.json | CRITICAL | 3 min |
| 2.5 | Deprecate duplicate scripts | MEDIUM | 2 min |
| 2.6 | Resolve duplicate MP names | MEDIUM | 5 min |
| 2.7 | Verify dashboard stats | HIGH | 1 min |

### Phase 3: Verification Tests

After fixes, run these tests:

```bash
# Test 1: Entities populated
python3 -c "import json; d=json.load(open('knowledge_graph/entities.json')); print(f'Persons: {len(d[\"persons\"])}, Sessions: {len(d[\"sessions\"])}, Laws: {len(d[\"laws\"])}')"

# Test 2: No duplicates in politicians
duplicates=$(ls vault/politicians/*.md | xargs -n1 basename | sort | uniq -d | wc -l)
echo "Duplicate files in root: $duplicates"

# Test 3: Date format consistency
iso_count=$(ls vault/sessions/*/*.md | grep -E '[0-9]{4}-[0-9]{2}-[0-9]{2}' | wc -l)
total_count=$(ls vault/sessions/*/*.md 2>/dev/null | wc -l)
echo "ISO format: $iso_count / $total_count"

# Test 4: Dashboard shows correct counts
curl -s http://localhost:8080/api/stats
```

---

## 📋 FIX COMMANDS

### Fix 1: Remove Empty Files
```bash
cd /home/adrian/Desktop/NEDAILAB/StenoMD
find vault/sessions -name '*.md' -empty -delete
find vault/sessions -name 'Unknown.md' -delete
echo "Empty files removed"
```

### Fix 2: Date Migration
```bash
python3 scripts/migrate_dates.py
```

### Fix 3: Vault Consolidation
```bash
python3 scripts/migrate_vault.py
```

### Fix 4: Knowledge Graph Merge
```bash
python3 scripts/stenomd_master.py --merge
```

### Fix 5: Verify Dashboard
```bash
curl -s http://localhost:8080/api/stats
```

---

## ✅ BUGS FIXED (2026-04-22)

| ID | Bug | Fix | File |
|----|-----|-----|------|
| FIX-001 | requirements.txt missing beautifulsoup4 | Added `beautifulsoup4>=4.12.0` | requirements.txt |
| FIX-002 | stenomd_master.py wrong signature | `run(years=[year], max_id=max_sessions)` | stenomd_master.py |
| FIX-003 | Senator malformed filenames | Added name filtering + split | senat_agent.py |
| FIX-004 | Wrong vault paths | Updated to `politicians/senators/` | senat_agent.py |
| FIX-005 | soup.title AttributeError | Added try/except | update_knowledge_graph.py |
| FIX-006 | Date parse regex | Fixed participant pattern | validators.py |
| FIX-007 | CDEP session vault sync | Added _save_session_to_vault() | cdep_agent.py |
| FIX-008 | Date extraction broken | Rewrote extract_date_from_title() | cdep_agent.py |

---

## 🎯 SUCCESS CRITERIA

After executing debug plan:
- [ ] entities.json contains 100+ persons, 40+ sessions, 15+ laws
- [ ] No politician files in root `vault/politicians/` (all in subdirs)
- [ ] All session dates in ISO format (YYYY-MM-DD)
- [ ] No empty or Unknown.md files in sessions/
- [ ] Dashboard shows accurate counts
- [ ] No duplicate MP names (normalized comparison)

---

## 📁 RELEVANT FILES

| File | Purpose |
|------|---------|
| `scripts/migrate_dates.py` | Date format migration |
| `scripts/migrate_vault.py` | Vault consolidation |
| `scripts/validators.py` | Data validation |
| `scripts/stenomd_master.py` | Master controller + merge |
| `scripts/dashboard.py` | Web dashboard |
| `knowledge_graph/entities.json` | KG data store |

---

## 🔗 USEFUL REFERENCES

- **Dashboard:** http://localhost:8080
- **GitHub:** https://github.com/nedaktov-ops/StenoMD
- **Commit:** 4808403 - "feat: Add Planner agent, fix empty files"

---

*End of Debug Plan*
*Next update: After Phase 2 fixes applied*