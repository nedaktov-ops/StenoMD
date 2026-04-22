#!/usr/bin/env python3
"""StenoMD Mobile API - REST API for mobile consumption"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
from pathlib import Path

app = FastAPI(title="StenoMD API")

KG_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/knowledge_graph")
ENTITIES_FILE = KG_DIR / "entities.json"

def load_entities():
    if ENTITIES_FILE.exists():
        with open(ENTITIES_FILE) as f:
            data = json.load(f)
            return {
                "persons": data.get("persons") or data.get("people", []),
                "sessions": data.get("sessions", []),
                "laws": data.get("laws", [])
            }
    return {"persons": [], "sessions": [], "laws": []}

class Politician(BaseModel):
    id: str
    name: str
    party: Optional[str] = None
    legislature: Optional[str] = None

class Session(BaseModel):
    id: str
    date: str
    legislature: str
    chamber: str

class Law(BaseModel):
    id: str
    law_number: str
    title: str
    status: str

@app.get("/api/politicians", response_model=List[Politician])
async def list_politicians():
    entities = load_entities()
    return [Politician(id=p.get("id", ""), name=p.get("name", ""), 
                      party=p.get("party"), legislature=p.get("legislature"))
            for p in entities.get("persons", [])]

@app.get("/api/politicians/{politician_id}")
async def get_politician(politician_id: str):
    entities = load_entities()
    for p in entities.get("persons", []):
        if p.get("id") == politician_id:
            return p
    raise HTTPException(status_code=404, detail="Politician not found")

@app.get("/api/sessions", response_model=List[Session])
async def list_sessions(limit: int = 100):
    entities = load_entities()
    sessions = entities.get("sessions", [])[:limit]
    return [Session(id=s.get("id", ""), date=s.get("date", ""),
                  legislature=s.get("legislature", ""), chamber=s.get("chamber", ""))
            for s in sessions]

@app.get("/api/sessions/{session_date}")
async def get_session(session_date: str):
    entities = load_entities()
    for s in entities.get("sessions", []):
        if s.get("date") == session_date:
            return s
    raise HTTPException(status_code=404, detail="Session not found")

@app.get("/api/laws", response_model=List[Law])
async def list_laws(limit: int = 100):
    entities = load_entities()
    laws = entities.get("laws", [])[:limit]
    return [Law(id=l.get("id", ""), law_number=l.get("law_number", ""),
                title=l.get("title", ""), status=l.get("status", ""))
            for l in laws]

@app.get("/api/search")
async def search(q: str, type: str = "all"):
    entities = load_entities()
    q_lower = q.lower()
    results = {"politicians": [], "sessions": [], "laws": []}
    
    if type in ("all", "politicians"):
        results["politicians"] = [p for p in entities.get("persons", [])
                                 if q_lower in p.get("name", "").lower()]
    if type in ("all", "sessions"):
        results["sessions"] = [s for s in entities.get("sessions", [])
                             if q_lower in s.get("date", "").lower()]
    if type in ("all", "laws"):
        results["laws"] = [l for l in entities.get("laws", [])
                          if q_lower in l.get("title", "").lower()]
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)