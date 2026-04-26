# Query Reference Card

Quick reference for all GraphifyStenoMD queries.

## Basic Queries

```
/stenomd query "SEARCH_TERM"                    # Find node
/stenomd explain "NODE_NAME"                   # Explain node
/stenomd path "A" "B"                          # Find path A -> B
```

## Extended Queries (xquery)

```
/stenomd xquery cross_party                      # Cross-party collaborations
/stenomd xquery session --year 2024             # Session by year
/stenomd xquery constituency Dolj              # Constituency search
/stenomd xquery committee buget                 # Committee search
/stenomd xquery party PNL                      # Party search
/stenomd xquery temporal PATTERN               # Time patterns
/stenomd xquery search "TERM"                 # Full-text search
/stenomd xquery network "NAME"                 # Network analysis
```

## Analyze Queries

```
/stenomd analyze                              # Overview
/stenomd analyze coverage                     # Data coverage
/stenomd analyze activity                    # Activity leaderboard
/stenomd analyze gaps                         # Missing data
/stenomd analyze trends                       # Trends
```

## Workflow Queries

```
# Via Python scripts
python3 workflows/daily_scrape.py             # Daily gaps
python3 workflows/missing_data.py --enrich    # Missing data
python3 workflows/health_check.py            # Validation
python3 workflows/orchestrator.py daily      # Daily workflow
```

## Report Queries

```
python3 agents/analytics_agent.py --type coverage
python3 agents/analytics_agent.py --type activity
python3 agents/analytics_agent.py --type trends
python3 agents/analytics_agent.py --type coverage --save
```

## Graphify Commands (Native)

```
/graphify query "TERM" --graph Graphify/graphify-out/graph.json
/graphify explain "NODE" --graph Graphify/graphify-out/graph.json
/graphify path "A" "B" --graph Graphify/graphify-out/graph.json
```

---

## Common Patterns

### Find Politician Activity
```
/stenomd query "TANASESCU"
```

### Find Party Members
```
/stenomd xquery party PSD
```

### Find Session by Year
```
/stenomd xquery session --year 2024
```

### Find Cross-Party Collaboration
```
/stenomd xquery cross_party
```

### Check Data Gaps
```
python3 workflows/missing_data.py --enrich
```

### Validate Data
```
python3 workflows/health_check.py
```