# StenoMD REST API Reference

**Version:** 3.0.0  
**Base URL:** `http://localhost:5000` (default)  
**Documentation:** Interactive OpenAPI docs available at `/` and `/docs` when server is running.

## Overview

StenoMD provides a FastAPI-based HTTP interface to query parliamentary data, knowledge graph triples, statistics, and search functionality. The API is used by external tools, Obsidian plugins, and custom dashboards.

### Authentication & Security

- No authentication required for local use.
- CORS restricted to `ALLOWED_ORIGIN` (default: `localhost`). Configure via `STENOMD_ALLOWED_ORIGIN` environment variable.
- All SQL queries are parameterized (no injection risk).

### Running the Server

```bash
# Basic
python3 scripts/query/rest_api.py

# Custom host/port
python3 scripts/query/rest_api.py --host 0.0.0.0 --port 5000

# With auto-reload (development)
uvicorn rest_api:app --reload --port 5000
```

The server starts with health check and endpoint logs.

---

## Endpoints

### GET /api/stats

System statistics.

**Response:**
```json
{
  "total_deputies": 788,
  "total_senators": 138,
  "total_sessions": 152,
  "total_laws": 124,
  "total_statements": 760,
  "graph_nodes": 2241,
  "graph_edges": 1518
}
```

---

### GET /api/triples

Query knowledge graph triples with optional filters.

**Query Parameters:**

| Parameter | Type   | Description                          |
|-----------|--------|--------------------------------------|
| subject   | string | Filter subjects containing this text |
| predicate | string | Exact predicate match               |
| object    | string | Filter objects containing this text |
| limit     | int    | Max results (1-1000, default 100)   |

**Example:**

```bash
curl "http://localhost:5000/api/triples?predicate=spoken_by&limit=5"
```

**Response:**
```json
{
  "triples": [
    {
      "id": 1,
      "subject": "statement-2024-01-15-001",
      "predicate": "spoken_by",
      "object": "Mihai Tudose",
      "session_id": "2024-01-15",
      "confidence": 1.0,
      "source_file": "vault/sessions/deputies/2024/2024-01-15.md"
    }
  ],
  "count": 1
}
```

---

### GET /api/mp/{name}

Retrieve a politician's profile by name (URL-encoded). Includes deputy or senator details, activity metrics, and related sessions/laws.

**Path Parameter:** `name` (string) – Full name or partial match.

**Example:**

```bash
curl "http://localhost:5000/api/mp/Mihai%20Tudose"
```

**Response (deputy):**
```json
{
  "name": "Mihai Tudose",
  "type": "deputy",
  "party": "PSD",
  "constituency": "Neamț",
  "idm": 123,
  "stable_id": "dep-123",
  "speeches_count": 42,
  "laws_proposed": 5,
  "committees": [" budaya"], 
  "photo_url": "https://...",
  "url": "https://...",
  "sessions_attended": ["2024-01-15", "2024-02-01"],
  "laws_sponsored": ["18/2024"]
}
```

If not found, returns `404` with error details.

---

### GET /api/session/{date}

Get session details by date and optional chamber.

**Path Parameter:** `date` (ISO 8601 date, e.g., `2024-01-15`)

**Query Parameter:** `chamber` (`deputies` or `senate`, default `deputies`)

**Example:**

```bash
curl "http://localhost:5000/api/session/2024-01-15?chamber=deputies"
```

**Response:**
```json
{
  "date": "2024-01-15",
  "chamber": "deputies",
  "title": "Ședința Camerei Deputaților",
  "participants": ["Mihai Tudose", "Ana Birchall"],
  "deputy_count": 320,
  "statements_count": 45,
  "laws_discussed": ["20/2024"],
  "source_url": "https://cdep.ro/stenograma/...",
  "file": "vault/sessions/deputies/2024/2024-01-15.md"
}
```

---

### GET /api/law/{law_number}

Retrieve law information by law number (e.g., `20/2024`).

**Path Parameter:** `law_number` – string in format `NN/YYYY`.

**Example:**

```bash
curl "http://localhost:5000/api/law/20/2024"
```

**Response:**
```json
{
  "number": "20/2024",
  "title": "Legea responsabilității instituționale...",
  "status": "adoptată",
  "date": "2024-03-10",
  "sponsors": ["Mihai Tudose"],
  "proposals": ["L20/2024"],
  "source_url": "https://cdep.ro/...",
  "file": "vault/laws/20-2024.md"
}
```

---

### GET /api/search

Full-text search over sessions.

**Query Parameter:** `q` (required) – Search terms.

**Optional Query Parameter:** `chamber` (`deputies` or `senate`) to filter.

**Example:**

```bash
curl "http://localhost:5000/api/search?q=energie%20renovabilă&chamber=deputies"
```

**Response:**
```json
{
  "results": [
    {
      "date": "2024-02-15",
      "chamber": "deputies",
      "snippet": "Discuții despre energia regenerabilă și eficiență energetică.",
      "file": "vault/sessions/deputies/2024/2024-02-15.md"
    }
  ],
  "count": 1
}
```

---

### GET /api/topics

Topic classification statistics. Shows counts of statements per topic.

**Response:**
```json
{
  "topics": [
    {"topic": "energie", "count": 152},
    {"topic": "educație", "count": 120}
  ],
  "statements_classified": 760
}
```

---

### GET /api/positions

Position classification statistics (PRO/CONTRA/NEUTRAL) and classification method distribution.

**Response:**
```json
{
  "positions": [
    {"position": "PRO", "count": 420},
    {"position": "CONTRA", "count": 180},
    {"position": "NEUTRAL", "count": 160}
  ],
  "methods": [
    {"method": "keyword", "count": 600},
    {"method": "ollama", "count": 160}
  ]
}
```

---

### GET /api/health

Simple health check. Returns status and version.

**Response:**
```json
{
  "status": "healthy",
  "version": "3.0.0"
}
```

---

## Error Handling

Endpoints return standard HTTP status codes:

- `200` Success
- `400` Bad request (missing parameters)
- `404` Not found (resource doesn't exist)
- `500` Internal server error

Error response body:

```json
{
  "detail": "Error description"
}
```

---

## Configuration

API behavior controlled by `scripts/config.py` and environment variables:

| Variable                | Default | Description                         |
|-------------------------|---------|-------------------------------------|
| `STENOMD_ALLOWED_ORIGIN`| `localhost` | CORS allowed origin              |
| `STENOMD_MAX_ID`        | `200`   | Max session ID for scrapers        |
| `STENOMD_CACHE_TTL`     | `3600`  | Cache TTL in seconds               |
| `STENOMD_LOG_LEVEL`     | `INFO`  | Logging level                      |
| `STENOMD_DEBUG`         | `false` | Enable debug mode                  |

---

## Dependencies

- FastAPI
- uvicorn (server)
- sqlite3 (knowledge graph access)
- scripts.parliament_qa (query engine)

Ensure dependencies are installed:

```bash
pip install fastapi uvicorn
```

---

## Notes

- Endpoints returning large result sets are capped (`limit` param) to protect performance.
- Knowledge graph data is read from `knowledge_graph/knowledge_graph.db`.
- For production deployments, add reverse proxy (nginx) and TLS termination.
