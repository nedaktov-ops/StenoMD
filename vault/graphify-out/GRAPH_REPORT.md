# Graph Report - vault  (2026-04-27)

## Corpus Check
- 1 files · ~398,470 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 10 nodes · 15 edges · 4 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]

## God Nodes (most connected - your core abstractions)
1. `load_entities()` - 5 edges
2. `search_politician()` - 4 edges
3. `search_session()` - 4 edges
4. `search_law()` - 4 edges
5. `main()` - 4 edges
6. `Load entities from knowledge graph.` - 1 edges
7. `Search for politician by name.` - 1 edges
8. `Search for session by date.` - 1 edges
9. `Search for law by number.` - 1 edges

## Surprising Connections (you probably didn't know these)
- `Load entities from knowledge graph.` --rationale_for--> `load_entities()`  [EXTRACTED]
  vault/_scripts/query-brain.py → _scripts/query-brain.py
- `Search for politician by name.` --rationale_for--> `search_politician()`  [EXTRACTED]
  vault/_scripts/query-brain.py → _scripts/query-brain.py
- `Search for session by date.` --rationale_for--> `search_session()`  [EXTRACTED]
  vault/_scripts/query-brain.py → _scripts/query-brain.py
- `Search for law by number.` --rationale_for--> `search_law()`  [EXTRACTED]
  vault/_scripts/query-brain.py → _scripts/query-brain.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.67
Nodes (3): main(), Search for law by number., search_law()

### Community 1 - "Community 1"
Cohesion: 1.0
Nodes (2): load_entities(), Load entities from knowledge graph.

### Community 2 - "Community 2"
Cohesion: 1.0
Nodes (2): Search for politician by name., search_politician()

### Community 3 - "Community 3"
Cohesion: 1.0
Nodes (2): Search for session by date., search_session()

## Knowledge Gaps
- **4 isolated node(s):** `Load entities from knowledge graph.`, `Search for politician by name.`, `Search for session by date.`, `Search for law by number.`
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 1`** (2 nodes): `load_entities()`, `Load entities from knowledge graph.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 2`** (2 nodes): `Search for politician by name.`, `search_politician()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 3`** (2 nodes): `Search for session by date.`, `search_session()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_entities()` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`?**
  _High betweenness centrality (0.333) - this node is a cross-community bridge._
- **Why does `search_politician()` connect `Community 2` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.236) - this node is a cross-community bridge._
- **Why does `search_session()` connect `Community 3` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.236) - this node is a cross-community bridge._
- **What connects `Load entities from knowledge graph.`, `Search for politician by name.`, `Search for session by date.` to the rest of the system?**
  _4 weakly-connected nodes found - possible documentation gaps or missing edges._