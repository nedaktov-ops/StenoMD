---
name: stenomd-mobile-api
description: "REST/GraphQL API for mobile consumption of Romanian Parliament knowledge"
risk: low
source: custom
date_added: "2026-04-21"
---

# StenoMD Mobile API

REST API skill for mobile applications to consume the Romanian Parliament knowledge brain.

## 1️⃣ Purpose & Scope

- REST endpoints for mobile app consumption
- GraphQL for flexible queries
- Caching layer for offline access
- Optimized queries for mobile use cases

## 2️⃣ Pre-Requisites

- knowledge_graph/ populated with entities
- Python 3.12+ with FastAPI

## 3️⃣ Usage

```bash
cd skills/skills/stenomd-mobile-api
pip install -r requirements.txt
uvicorn main:app --reload
```

API available at http://localhost:8000

## 4️⃣ REST Endpoints

| Method | Endpoint | Description |
|--------|----------|------------|
| GET | /api/politicians | List all MPs |
| GET | /api/politicians/{id} | Get MP details |
| GET | /api/sessions | List sessions |
| GET | /api/sessions/{date} | Get session |
| GET | /api/laws | List laws |
| GET | /api/laws/{id} | Get law details |
| GET | /api/search | Search all |

## 5️⃣ GraphQL

```graphql
query {
  politicians(limit: 10) {
    name
    party
    statements {
      date
      content
    }
  }
}
```

## 6️⃣ Configuration

```env
KG_PATH=/path/to/knowledge_graph
API_HOST=0.0.0.0
API_PORT=8000
REDIS_URL=redis://localhost:6379
```