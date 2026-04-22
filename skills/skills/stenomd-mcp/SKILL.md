---
name: stenomd-mcp
description: "Model Context Protocol server for AI agent integration with the Romanian Parliament knowledge brain"
risk: low
source: custom
date_added: "2026-04-21"
---

# StenoMD MCP

Model Context Protocol server enabling AI agents to query the Romanian Parliament knowledge brain.

## 1️⃣ Purpose & Scope

- Expose knowledge graph as queryable context for LLMs
- Standardized prompts for common parliamentary queries
- MCP protocol for OpenCode, Claude, other AI agents

## 2️⃣ Pre-Requisites

- knowledge_graph/ populated with entities
- Python 3.12+

## 3️⃣ Usage

```bash
cd skills/skills/stenomd-mcp
pip install -r requirements.txt
python server.py
```

MCP endpoints available at:
- `/mcp/search_politician?name=<name>`
- `/mcp/search_session?date=<date>`
- `/mcp/search_law?number=<law_number>`
- `/mcp/get_recent_sessions?limit=<n>`

## 4️⃣ Standard Queries

```
Query: "Find all statements by [MP Name] in 2025"
Query: "What laws did [MP Name] sponsor?"
Query: "List sessions from March 2026"
Query: "Show voting record for Law 123/2025"
```

## 5️⃣ Configuration

```env
KG_PATH=/path/to/knowledge_graph
MCP_HOST=localhost
MCP_PORT=8080
```