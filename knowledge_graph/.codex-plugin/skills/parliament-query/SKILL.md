---
name: parliament-query
description: Query the complete parliamentary knowledge graph - MPs, sessions, laws, debates. Use when user asks "who said", "what law", "when session", "parliamentary data", "find mp".
allowed-tools: Bash, Read, Grep
---

# Query Parliament Data

Query existing parliamentary data from multiple sources.

## Methods

### 1. Search Vault (grep)
```bash
grep -r "search_term" vault/politicians/
grep -r "search_term" vault/sessions/
```

### 2. Dataview Query
Use Obsidian with dataview queries from:
- `obsidian-plugins/dataview/parliament-queries.md`

### 3. MemPalace Semantic Search
```bash
cd knowledge_graph
mempalace search "query"
```

### 4. Knowledge Graph Query
```bash
python3 scripts/query/parliament_qa.py --question "your question"
```

### 5. REST API
```bash
curl http://localhost:8000/api/mps
curl http://localhost:8000/api/sessions
curl http://localhost:8000/api/laws
```

## Data Sources
- `vault/politicians/` - MP profiles (deputies, senators)
- `vault/sessions/` - Session transcripts  
- `vault/laws/` - Legislation
- `knowledge_graph/entities.json` - Unified KG
- `vault/ai-memory/` - AI-processed summaries

## Example Queries

### "Who talked about 448/2006?"
```bash
grep -r "448/2006" vault/sessions/
```

### "Show PSD deputies with most speeches"
```dataview
TABLE file.name, speeches_count
FROM "politicians/deputies"
WHERE party = "PSD"
SORT speeches_count DESC
LIMIT 10
```

### "Recent sessions"
```dataview
TABLE date, title, chamber
FROM "sessions"
SORT date DESC
LIMIT 10
```