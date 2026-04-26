# GraphifyStenoMD Integration Points

## Project Structure Integration

```
StenoMD/
├── vault/                    <-- Graphify reads from here
├── scripts/                 <-- Can use Graphify gap analysis
├── knowledge_graph/         <-- Can sync with Graphify output
├── Graphify/               <-- Main graph output
│   └── graphify-out/
│       └── graph.json
└── GraphifyStenoMD/       <-- Enhancement system (this project)
    ├── skills/
    ├── agents/
    ├── workflows/
    └── ...
```

## Integration Points

### 1. Vault → Graphify (Read)
Graphify analyzes vault content:
```bash
/graphify vault --output Graphify/graphify-out
```

### 2. Graphify → StenoMD Scripts (Gap-Aware)
Scripts use graph for gap analysis:
```python
# In any script:
from pathlib import Path
import json

GRAPH_FILE = Path("Graphify/graphify-out/graph.json")
with open(GRAPH_FILE) as f:
    graph = json.load(f)

# Find missing data
for node in graph.get("nodes", []):
    if "politicians/" in node.get("source_file", ""):
        if not node.get("party"):
            # Gap found!
            pass
```

### 3. Knowledge Graph Sync
Compare Graphify with knowledge_graph/entities.json:
```bash
python3 GraphifyStenoMD/scripts/integrations/knowledge_graph_sync.py --compare
```

### 4. Existing Scripts Gap-Aware
Run existing scripts with gap awareness:
```bash
python3 GraphifyStenoMD/scripts/integrations/run_enrich.py --list
python3 GraphifyStenoMD/scripts/integrations/run_enrich.py --type party
```

## Data Flow

```
[vault/*.md] --> [graphify] --> [graph.json]
                                    |
                                    v
                  [GraphifyStenoMD] <-- Read-only access
                        |
                        v
            [gap analysis] --> [scripts/]
```

## Gap-Aware Script Pattern

```python
import json
from pathlib import Path

# Read gap data from graph
GRAPH_FILE = Path("Graphify/graphify-out/graph.json")

def get_gaps():
    with open(GRAPH_FILE) as f:
        graph = json.load(f)
    
    gaps = []
    for node in graph.get("nodes", []):
        if "politicians/" in node.get("source_file", ""):
            if not node.get("party"):
                gaps.append(node)
    
    return gaps

# Only process gaps
def main():
    gaps = get_gaps()
    print(f"Found {len(gaps)} gaps to fill")
    
    for node in gaps:
        # Process each gap
        pass
```

## Using Existing Scripts

The integration scripts can run existing StenoMD scripts with gap data:

```bash
# List what's available
python3 GraphifyStenoMD/scripts/integrations/run_enrich.py --list

# Run party enrichment
python3 GraphifyStenoMD/scripts/integrations/run_enrich.py --type party --run

# Run scraping
python3 GraphifyStenoMD/scripts/integrations/run_enrich.py --scrape cdep --run
```

## Manual Sync (OptionB)

For manual syncing between systems:

```bash
# Compare both systems
python3 GraphifyStenoMD/scripts/integrations/knowledge_graph_sync.py --compare

# Run enrichments
python3 scripts/enrich_profiles.py --type party
```

---

*All integrations are read-only or require manual confirmation (OptionB design)*