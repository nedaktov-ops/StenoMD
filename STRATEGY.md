# StenoMD Strategy - Comprehensive 3.0

**Generated:** 2026-04-25
**Mode:** Build
**Version:** 3.0 (Complete Overhaul)

---

## Project Vision

Transform StenoMD from a simple "warehouse" to a logical "brain" for Romanian Parliament analysis.

### Key Principles
1. **Logical Connections**: Events linked across legislatures and chambers
2. **Multi-Legislature Tracking**: Stable IDs, not recycled IDs
3. **Party Change Tracking**: Traseism monitoring
4. **Process Awareness**: Full legislative process metadata
5. **RAM Optimization**: Works on 8GB systems

---

## Research Summary

### Parliament Structure (2024-2028)
| Chamber | Seats | Committees |
|--------|------|------------|
| Senate | 136 | 15 |
| Chamber | 330 | 17 |
| Joint | ~12 | - |

### Legislative Process
```
INITIATION → COMMITTEE → PLENARY → SECOND CHAMBER → PROMULGATION → MONITORUL OFICIAL → EFFECT
```

### Multi-Legislature
- IDs recycle each legislature → MUST use stable IDs
- Same person: Deputy (one legislature) → Senator (another)

### Traseism (Floor-Crossing)
- Legal for parliamentarians
- CPC definition: >2 party changes = traseist
- Must track: original_elected_party vs current_party

### Monitorul Oficial Parts
| Part | Content |
|------|---------|
| I | Laws (entry into force) |
| II | Stenograms |
| III-VII | Announcements |

---

## Implementation Phases

### Phase 1: Parliamentary Reference Structure
- [ ] Create vault/_parliament/ directory
- [ ] Constitutional articles (58-79, 113-114)
- [ ] Key term definitions
- [ ] Committee structures (44 committees)
- [ ] Legislative process reference
- [ ] All legislatures (1990-2024)

### Phase 2: Clean & Fix
- [ ] Delete empty files (Budget-Finance.md)
- [ ] Fix broken session links
- [ ] Standardize session naming
- [ ] Add legislature fields

### Phase 3: Stable ID Generation
- [ ] scripts/generate_stable_ids.py
- [ ] Generate: hash(name + birth_year + birthplace)
- [ ] Link across legislatures

### Phase 4: Party Change Tracking (NEW!)
- [ ] scripts/add_party_tracking.py
- [ ] Add party_affiliations array
- [ ] Add traseism_metrics
- [ ] Track original_elected_party vs current

### Phase 5: Complete 2024 Data
- [ ] Senators: Add party/constituency to 137 profiles
- [ ] Deputies: Add committees to 330 profiles
- [ ] Add parliamentary groups
- [ ] Add leadership positions
- [ ] Laws: Add process metadata

### Phase 6: Historical Scraping
- [ ] Priority: 2024-2028 → 2020-2024 → 2016-2020
- [ ] Single legislature at a time
- [ ] Compare with existing, fill gaps

### Phase 7: Low-RAM Optimization
- [ ] Memory limits for 8GB (i5-7200U)
- [ ] phi3:3.5b model vs qwen2.5-coder
- [ ] Reduce batch sizes

---

## Expected Outcomes

| Metric | Current | After |
|--------|---------|-------|
| Parliamentary reference | Incomplete | Complete |
| Stable IDs | No | Yes |
| Party change tracking | No | Yes |
| Traseism calculation | No | Yes |
| Committee data | 0 | 44 |
| Law process stages | 0 | 6 |
| Monitorul Oficial | 0 | Yes |
| Multi-legislature | No | Yes |
| Historical data | 2024 | 2024+ |

---

## Current Status

**NOT STARTED** - Strategy 3.0 ready for implementation

---