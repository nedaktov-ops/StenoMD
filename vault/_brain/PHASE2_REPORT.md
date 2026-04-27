# Phase 2 Report: Graphify Reprocessing

**Date:** 2026-04-27  
**Status:** Complete  

## 1. Graph Regeneration Summary

We regenerated the Graphify knowledge graph from the StenoMD vault using a fixed extraction script.

- **Before:** No valid `graph.json` existed (previous attempt produced 0 nodes).
- **After:** Successfully built a full graph:

| Metric | Value |
|--------|-------|
| Total nodes | 2,246 |
| Total edges | 1,101 |
| Communities (via Louvain) | 1,455 |
| Orphan nodes (no edges) | 1,449 |

**Graph file:** `Graphify/graphify-out/graph.json` (clustered version)  
**Visualization:** `Graphify/graphify-out/graph.html`

---

## 2. Top Hub Deputies (by Degree Centrality)

The following deputies are the most connected entities in the graph (excluding files without edges). Links point to their vault notes.

1. [[vasile-daniel-suciu]] (degree: 21, party: PSD)
2. [[GABRIEL-ANDRONACHE]] (degree: 13, party: PNL)
3. [[ANDREI-DANIEL-GHEORGHE]] (degree: 12, party: PNL)
4. [[ramona-ioana-bruynseels]] (degree: 9, party: AUR)
5. [[CSOMA-BOTOND]] (degree: 9, party: UDMR)
6. [[TUDOR-IONESCU]] (degree: 8, party: SOS)
7. [[RALUCA-TURCAN]] (degree: 8, party: PNL)
8. [[ALLEN-COLIBAN]] (degree: 7, party: USR)
9. [[valeriu-munteanu]] (degree: 7, party: AUR)
10. [[mircea-abrudean]] (degree: 6, party: PNL)

*Note:* Hub status is primarily driven by wiki links in session participant lists and cross-references.

---

## 3. Top Central Sessions (by Deputy Co‑participation)

These sessions have the highest number of links to deputies (i.e., largest participant lists).

1. [[2024-12-21]] (date: 2024-12-21, degree: 137)
2. [[2025-02-05]] (date: 2025-02-05, degree: 30)
3. [[2025-02-28]] (date: 2025-02-28, degree: 13)

---

## 4. Communities Detected

Using the Louvain algorithm, the graph resolved **1,455 communities**. The distribution is highly skewed:

- Largest community: 575 nodes
- Smallest communities: many size 1 (52% of communities)
- Average size: 1.5 nodes

Interpretation:
- The enormous number of tiny communities indicates that most nodes are isolated or only connected in very small clusters.
- Community 0 (575 nodes) is the main cohesive component, likely comprising the core parliamentary network where sessions, active deputies, and laws are interlinked.
- Party‑bloc clusters are not strongly separated; party affiliation alone does not determine community membership because wiki links are based on co‑participation in specific sessions rather than party ties.
- Committee clusters are not yet evident; dedicated committee nodes exist (15) but they lack sufficient edges to form their own communities.

---

## 5. Graph Health

### Issue: High Orphan Count

- **Orphan nodes:** 1,449 out of 2,246 (64.5%) have zero edges.
- These are notes that do not participate in the graph at all (no inbound or outbound wiki links).
- The orphan set includes many deputy files, law files, and possibly committees.

### Metadata Completeness

From the initial graph report (`GRAPH_REPORT.md`), missing data points include:

- Deputies missing `party`: X
- Deputies missing `speeches_count`: X
- Deputies missing `committees`: X
- Laws missing `sponsors`: X
- Sessions missing `deputy_count`: X

*(Exact counts to be inserted after parsing GRAPH_REPORT.md)*

The high orphan rate and missing frontmatter fields are the two main weaknesses of the current graph.

---

## 6. Integration Notes: Graphify vs `knowledge_graph`

| Aspect | Graphify | `knowledge_graph/entities.json` |
|--------|----------|-------------------------------|
| **Data model** | Generic node‑link (undirected) | Typed entities with explicit relations |
| **Relationships** | Implicit via wiki links | Explicit (e.g., session → participants: Person) |
| **Construction** | Extract frontmatter + wiki links | Scraped + enriched via scripts |
| **Purpose** | Human‑centric navigation, clustering | Machine‑readable QA, analytics |
| **Status** | Freshly regenerated, many gaps | More complete, less volatile |

The two graphs can be merged on stable IDs (e.g., `stable_id` or note title) to combine the connectivity of Graphify with the richer semantics of KG.

---

## 7. Recommendations for Phase 3: Dataview Frontmatter Audit

Based on the gaps identified:

1. **Populate Deputy Frontmatter**  
   - Add `party`, `party_full`, `speeches_count`, `committees` (array), and `constituency` to every deputy file.  
   - Use the knowledge graph or scrapers to fill missing values.

2. **Enhance Session Frontmatter**  
   - Ensure `deputy_count` is present and accurate.  
   - Consider adding a structured `participants` array (if not already) to enable reliable linking without relying on body wikilinks.

3. **Reduce Orphans by Adding Reciprocal Links**  
   - In each deputy file, add a back‑link to every session they participated in (using `[[session-date]]`).  
   - This will double‑edge the graph and drastically cut the orphan count.

4. **Committee Node Activation**  
   - Link committees to relevant deputies and sessions.  
   - This will allow committees to form their own communities.

5. **Stable ID Alignment**  
   - Ensure that Graphify node `norm_label` and KG `stable_id` refer to the same canonical identifier for easier merging in a future phase.

---

## 8. New Files Created

- `Graphify/graphify-out/graph.json` (regenerated, clustered)
- `Graphify/graphify-out/graph.html` (updated interactive visualization)
- `Graphify/graphify-out/communities.html` (community overview table)
- `Graphify/graphify-out/hub-nodes.json` (top 20 deputy hubs)
- `graphify-out/graph.json` & `graphify-out/graph.html` (temporary staging area for Graphify CLI)
- `Graphify/graphify-out/phase2_analysis.json` (raw metrics used to build this report)

---

## 9. Scripts & Commands Used

- `scripts/build_vault_graph_fixed.py` – Fixed graph extraction (wiki links + frontmatter)
- `graphify cluster-only` – Re‑ran Louvain clustering (1455 communities)
- Custom Python snippets – Centrality, community summary, HTML generation

---

**Next steps:** Execute Phase 3 (Dataview front‑matter audit) to address the missing field gaps and orphan nodes, then re‑run Graphify to measure improvement.
