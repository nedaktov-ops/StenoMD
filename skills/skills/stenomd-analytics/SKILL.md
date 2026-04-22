---
name: stenomd-analytics
description: "Analytics and reporting for Romanian Parliament knowledge graph"
risk: low
source: custom
date_added: "2026-04-21"
---

# StenoMD Analytics

Analytics skill for trend analysis, voting patterns, and reporting.

## 1️⃣ Purpose & Scope

- Voting pattern detection
- Topic evolution tracking
- MP activity analysis
- Exportable visualizations

## 2️⃣ Pre-Requisites

- knowledge_graph/ populated with entities
- Python 3.12+

## 3️⃣ Usage

```bash
cd skills/skills/stenomd-analytics
pip install -r requirements.txt
python analytics.py
```

## 4️⃣ Features

- Top active MPs by session attendance
- Most prolific speakers
- Law sponsorship rankings
- Committee activity reports
- Monthly/quarterly trends

## 5️⃣ Output Formats

- JSON for API consumption
- CSV for spreadsheet analysis
- HTML for web display