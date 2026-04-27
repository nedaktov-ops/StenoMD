#!/usr/bin/env python3
"""
StenoMD REST API
FastAPI-based HTTP endpoints for parliamentary data

Usage:
    python3 rest_api.py
    # or with uvicorn:
    uvicorn rest_api:app --reload --port 5000

Endpoints:
    GET /api/stats           - Statistics
    GET /api/triples         - Knowledge graph triples
    GET /api/mp/{name}       - MP profile
    GET /api/session/{date}  - Session details  
    GET /api/law/{number}    - Law info
    GET /api/search          - Search sessions
    GET /api/topics          - Topic statistics
    GET /api/positions       - Position statistics
    GET /                    - API documentation
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import unquote

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent

import sys
sys.path.insert(0, str(PROJECT_DIR / "scripts"))

from config import get_config, VAULT_DIR, KG_DIR, KG_DB, ALLOWED_ORIGIN

from parliament_qa import ParliamentQA


app = FastAPI(
    title="StenoMD API",
    description="Romanian Parliament Knowledge Brain API",
    version="3.0.0",
    docs_url="/",
    redoc_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TripleQuery(BaseModel):
    subject: Optional[str] = None
    predicate: Optional[str] = None
    object: Optional[str] = None
    limit: int = 100


@app.get("/api/stats")
def get_stats() -> Dict[str, Any]:
    """Get system statistics."""
    return ParliamentQA().get_stats()


@app.get("/api/triples")
def get_triples(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    predicate: Optional[str] = Query(None, description="Filter by predicate"),
    object: Optional[str] = Query(None, description="Filter by object"),
    limit: int = Query(100, ge=1, le=1000, description="Max results")
) -> Dict[str, Any]:
    """Get knowledge graph triples with optional filters."""
    conn = sqlite3.connect(KG_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    q = "SELECT * FROM triples WHERE 1=1"
    params = []
    
    if subject:
        q += " AND subject LIKE ?"
        params.append(f"%{subject}%")
    if predicate:
        q += " AND predicate = ?"
        params.append(predicate)
    if object:
        q += " AND object LIKE ?"
        params.append(f"%{object}%")
    
    params.append(limit)
    q += " LIMIT ?"
    
    cursor.execute(q, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"triples": results, "count": len(results)}


@app.get("/api/mp/{name}")
def get_mp(name: str) -> Dict[str, Any]:
    """Get MP profile by name."""
    name = unquote(name)
    result = ParliamentQA().search_mp(name)
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result)
    return result


@app.get("/api/session/{date}")
def get_session(
    date: str,
    chamber: str = Query("deputies", description="Chamber: deputies or senate")
) -> Dict[str, Any]:
    """Get session details by date."""
    date = unquote(date)
    result = ParliamentQA().get_session(date, chamber)
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result)
    return result


@app.get("/api/law/{law_number}")
def get_law(law_number: str) -> Dict[str, Any]:
    """Get law info by number."""
    law_number = unquote(law_number)
    return ParliamentQA().get_law(law_number)


@app.get("/api/search")
def search(
    q: str = Query(..., description="Search query"),
    chamber: Optional[str] = Query(None, description="Filter by chamber")
) -> Dict[str, Any]:
    """Search sessions by query."""
    if not q:
        raise HTTPException(status_code=400, detail="Missing query parameter 'q'")
    
    results = ParliamentQA().search_sessions(q, chamber)
    return {"results": results, "count": len(results)}


@app.get("/api/topics")
def get_topics() -> Dict[str, Any]:
    """Get topic statistics."""
    conn = sqlite3.connect(KG_DB)
    cursor = conn.cursor()
    
    cursor.execute("SELECT topic, COUNT(*) as cnt FROM topics GROUP BY topic ORDER BY cnt DESC")
    topics = [{"topic": r[0], "count": r[1]} for r in cursor.fetchall()]
    
    cursor.execute("SELECT COUNT(DISTINCT statement_id) FROM topics")
    statements = cursor.fetchone()[0]
    
    conn.close()
    
    return {"topics": topics, "statements_classified": statements}


@app.get("/api/positions")
def get_positions() -> Dict[str, Any]:
    """Get position statistics."""
    conn = sqlite3.connect(KG_DB)
    cursor = conn.cursor()
    
    cursor.execute("SELECT position, COUNT(*) as cnt FROM positions GROUP BY position")
    positions = [{"position": r[0], "count": r[1]} for r in cursor.fetchall()]
    
    cursor.execute("SELECT method, COUNT(*) as cnt FROM positions GROUP BY method")
    methods = [{"method": r[0], "count": r[1]} for r in cursor.fetchall()]
    
    conn.close()
    
    return {"positions": positions, "methods": methods}


@app.get("/api/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": "3.0.0"}


def main():
    import argparse
    import uvicorn
    
    parser = argparse.ArgumentParser(description='StenoMD REST API (FastAPI)')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    args = parser.parse_args()
    
    print(f"Starting StenoMD API on http://{args.host}:{args.port}")
    print(f"API docs available at http://{args.host}:{args.port}/")
    print("\nEndpoints:")
    print("  GET /api/stats        - Statistics")
    print("  GET /api/triples      - Knowledge graph triples")
    print("  GET /api/mp/{name}    - MP profile")
    print("  GET /api/session/{date} - Session details")
    print("  GET /api/law/{number} - Law info")
    print("  GET /api/search       - Search sessions")
    print("  GET /api/topics       - Topic stats")
    print("  GET /api/positions    - Position stats")
    print("  GET /api/health       - Health check")
    print("\nPress Ctrl+C to stop")
    
    uvicorn.run(
        "rest_api:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == '__main__':
    main()