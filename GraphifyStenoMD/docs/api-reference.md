# GraphifyStenoMD API Reference

## Agents

### ScraperAgent

```python
from agents.scraper_agent import GapAwareScraper

agent = GapAwareScraper()
gaps, priorities = agent.run()
suggestions = agent.suggest_scripts(priorities)
```

### EnrichmentAgent

```python
from agents.enrichment_agent import EnrichmentAgent

agent = EnrichmentAgent()
targets = agent.run("party")
```

### ValidatorAgent

```python
from agents.validator_agent import ValidatorAgent

agent = ValidatorAgent()
results = agent.run("all")
```

### AnalyticsAgent

```python
from agents.analytics_agent import AnalyticsAgent

agent = AnalyticsAgent()
report = agent.run("coverage")
agent.save_report("coverage")
```

## Workflows

### Orchestrator

```python
from workflows.orchestrator import WorkflowOrchestrator

orch = WorkflowOrchestrator()
orch.daily_workflow()
orch.weekly_workflow()
orch.analytics_workflow()
```

## Graph Access

```python
import json
from pathlib import Path

GRAPH_FILE = Path("Graphify/graphify-out/graph.json")

with open(GRAPH_FILE) as f:
    graph = json.load(f)

nodes = graph.get("nodes", [])
links = graph.get("links", [])
```

## Configuration

```yaml
# config.yaml
paths:
  project_root: "/home/adrian/Desktop/NEDAILAB/StenoMD"
  vault: "vault"
  output: "GraphifyStenoMD/output"
```