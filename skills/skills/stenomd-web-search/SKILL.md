---
name: stenomd-web-search
description: "Web interface for browsing and searching the Romanian Parliament knowledge graph"
risk: low
source: custom
date_added: "2026-04-21"
---

# StenoMD Web Search

Web interface skill for browsing the Romanian Parliament stenogram knowledge brain.

## 1️⃣ Purpose & Scope

- Serve knowledge graph search via web browser
- Provide faceted browsing by date, speaker, topic, law
- Real-time search using mempalace searcher

## 2️⃣ Pre-Requisites

- knowledge_graph/ populated with entities
- Node.js 18+ for web server

## 3️⃣ Usage

```bash
cd skills/skills/stenomd-web-search
npm install
npm run dev
```

Then open http://localhost:3000

## 4️⃣ Features

- Search MPs by name
- Browse sessions by date
- Filter laws by status
- Committee listings
- Real-time results

## 5️⃣ Configuration

Set environment variables:

```env
KG_PATH=/path/to/knowledge_graph
PORT=3000
```