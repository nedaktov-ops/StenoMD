# StenoMD Developer Guide

This guide covers the architecture, development workflow, testing, and contribution guidelines for StenoMD.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Directory Structure](#directory-structure)
3. [Configuration](#configuration)
4. [Adding a New Scraper](#adding-a-new-scraper)
5. [Knowledge Graph Schema](#knowledge-graph-schema)
6. [Testing](#testing)
7. [Code Style](#code-style)
8. [Contributing](#contributing)

---

## Architecture Overview

StenoMD is a knowledge brain for Romanian parliamentary data. It scrapes session transcripts, extracts statements, resolves entities, classifies positions, and stores everything in a vault and a knowledge graph.

**Core Components:**

- **Scrapers** (`scripts/agents/`): Fetch session data from cdep.ro and senat.ro. Output markdown files to `vault/sessions/`.
- **Merge Pipeline** (`scripts/merge_vault_to_kg.py`): Reads vault files and populates `knowledge_graph/entities.json` and `knowledge_graph.db`.
- **Entity Resolver** (`scripts/resolve/entity_resolver.py`): Normalizes MP names and links mentions to unique IDs.
- **Position Classifier** (`scripts/analyze/positions.py`): Classifies statements as PRO/CONTRA/NEUTRAL.
- **QA System** (`scripts/parliament_qa.py`): Natural language query interface over the knowledge graph.
- **REST API** (`scripts/query/rest_api.py`): HTTP API for external integrations.
- **Planner Agent** (`scripts/planner_agent.py`): Self-learning project strategist.

**Data Flow:**

```
Scrapers → Vault (markdown) → Merge → KG (JSON/SQLite) → QA / API
```

---

## Directory Structure

```
StenoMD/
├── scripts/
│   ├── agents/             # Scrapers: cdep_agent.py, senat_agent.py
│   ├── analyze/            # positions.py, topics.py
│   ├── kg/                 # schema_migrate.py, triple_extractor.py
│   ├── memory/             # memory.py, actions.json
│   ├── query/              # parliament_qa.py, rest_api.py
│   ├── resolve/            # entity_resolver.py
│   ├── validators.py
│   ├── config.py           # Central configuration
│   ├── merge_vault_to_kg.py
│   ├── run_daily.py
│   └── planner_agent/      # Master strategist submodules
├── vault/
│   ├── sessions/
│   │   ├── deputies/
│   │   └── senate/
│   ├── politicians/
│   │   ├── deputies/
│   │   └── senators/
│   ├── laws/
│   └── _brain/             # Dashboard and recall queries
├── knowledge_graph/
│   ├── entities.json       # Mem Palace (canonical)
│   ├── entities.db         # Symlink → knowledge_graph.db
│   ├── knowledge_graph.db  # SQLite triples
│   └── graphify-out/       # Graphify analytical overlay
├── data/                   # Raw scraped data, open-parliament imports
├── docs/                   # Documentation (this file, API ref, etc.)
├── tests/                  # pytest test suite
├── config/                 # Plugin configs (QuickAdd)
└── project-timeline.md     # Project planning

```

---

## Configuration

Use `scripts/config.py` to access paths and settings. Example:

```python
from config import get_config

config = get_config()
PROJECT_ROOT = config.PROJECT_ROOT
VAULT_DIR = config.VAULT_DIR
KG_DIR = config.KG_DIR
```

Environment variables override defaults:

```bash
export STENOMD_DIR=/custom/path
export STENOMD_ALLOWED_ORIGIN=localhost
export STENOMD_MAX_ID=200
export STENOMD_DEBUG=true
```

All core scripts should import config instead of hardcoding paths.

---

## Adding a New Scraper

If you need to scrape a new data source (e.g., committee assignments), follow this pattern:

1. **Create script** in `scripts/agents/` or top-level `scripts/` based on scope.
2. **Use config** for paths:

   ```python
   from config import get_config
   config = get_config()
   OUTPUT_DIR = config.VAULT_DIR / "sessions" / "deputies"
   ```

3. **Follow naming conventions**:
   - Session files: `YYYY-MM-DD.md` under appropriate chamber directory.
   - Politician files: kebab-case full name (e.g., `mihai-tudose.md`).
   - Law files: `NN-YYYY.md`.
4. **Write frontmatter** (YAML) with required fields. See `docs/TEMPLATES.md`.
5. **Update merge pipeline** if new entity types are added (edit `scripts/merge_vault_to_kg.py`).
6. **Add tests** for parsing and validation (in `tests/agents/`).
7. **Update planner agent** if the scraper affects task tracking.

**Example skeleton:**

```python
#!/usr/bin/env python3
"""My scraper: description"""

import json
from pathlib import Path
from datetime import datetime
from config import get_config

def scrape():
    config = get_config()
    output_dir = config.VAULT_DIR / "sessions" / "deputies"
    output_dir.mkdir(parents=True, exist_ok=True)
    # ... scraping logic ...
    file = output_dir / "2024-01-20.md"
    file.write_text(content)

if __name__ == "__main__":
    scrape()
```

---

## Knowledge Graph Schema

The KG consists of:

- **Entities**: persons, parties, sessions, laws, committees, statements.
- **Triples**: subject-predicate-object relationships stored in `knowledge_graph.db` table `triples`.
- **Mem Palace**: `entities.json` is the canonical source for API and QA; syncs from vault.

Key predicates: `participated_in`, `spoken_by`, `spoken_about`, `proposed_by`, `member_of`, `voted_for`, `opposed`, `abstained`.

Schema versioning and migrations handled by `scripts/kg/schema_migrate.py`.

---

## Testing

Run tests with:

```bash
pytest tests/ -v
```

Target: ≥80% coverage for core modules (`config`, `validators`, `entity_resolver`, `positions`, `merge_vault_to_kg`).

Test files mirror package structure:

- `tests/kg/` for knowledge graph modules
- `tests/resolve/` for entity resolution
- `tests/analyze/` for position/topic classification
- `tests/agents/` for scraper pattern tests

Use fixtures in `tests/conftest.py` for common data.

Add tests for new features and bug fixes.

---

## Code Style

- PEP 8 compliance (4 spaces, max line length 88/100).
- Type hints on all function signatures.
- Docstrings for modules, classes, public methods.
- Logging instead of print for long-running scripts (use `logging` module).
- Exceptions: catch specific exceptions, avoid bare `except:`.
- No hardcoded paths – always use `config`.

---

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-feature`).
3. Make changes with clear commit messages.
4. Ensure tests pass (`pytest`).
5. Update documentation if needed.
6. Open a pull request describing the change.

For questions or issues, use GitHub Issues.
