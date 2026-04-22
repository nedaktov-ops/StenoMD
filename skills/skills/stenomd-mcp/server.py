#!/usr/bin/env python3
"""StenoMD MCP Server - Model Context Protocol for AI agents"""

import os
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

KG_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/knowledge_graph")
ENTITIES_FILE = KG_DIR / "entities.json"

def load_entities():
    """Load entities from knowledge graph."""
    if ENTITIES_FILE.exists():
        with open(ENTITIES_FILE) as f:
            data = json.load(f)
            return {
                "persons": data.get("persons") or data.get("people", []),
                "sessions": data.get("sessions", []),
                "laws": data.get("laws", [])
            }
    return {"persons": [], "sessions": [], "laws": []}

def search_politician(name):
    """Search for politician by name."""
    entities = load_entities()
    name_lower = name.lower()
    return [e for e in entities.get("persons", []) 
            if name_lower in e.get("name", "").lower()]

def search_session(date):
    """Search for session by date."""
    entities = load_entities()
    return [e for e in entities.get("sessions", []) 
            if date in e.get("date", "")]

def search_law(law_num):
    """Search for law by number."""
    entities = load_entities()
    law_str = str(law_num)
    return [e for e in entities.get("laws", []) 
            if law_str in str(e.get("law_number", ""))]

def get_recent_sessions(limit=10):
    """Get recent sessions."""
    entities = load_entities()
    sessions = entities.get("sessions", [])
    return sorted(sessions, key=lambda x: x.get("date", ""), reverse=True)[:limit]

class MCPHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP endpoints."""

    def do_GET(self):
        path = self.path
        if path.startswith("/mcp/"):
            parts = path[4:].split("?")
            endpoint = parts[0]
            query = ""
            if len(parts) > 1:
                query = parts[1]
            
            if endpoint == "search_politician":
                name = query.split("=")[1] if "=" in query else ""
                results = search_politician(name)
            elif endpoint == "search_session":
                date = query.split("=")[1] if "=" in query else ""
                results = search_session(date)
            elif endpoint == "search_law":
                number = query.split("=")[1] if "=" in query else ""
                results = search_law(number)
            elif endpoint == "get_recent_sessions":
                limit = int(query.split("=")[1]) if "=" in query else 10
                results = get_recent_sessions(limit)
            else:
                results = []
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(results, indent=2, ensure_ascii=False).encode())
        else:
            self.send_response(404)
            self.end_headers()

def main():
    port = int(os.getenv("MCP_PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), MCPHandler)
    print(f"StenoMD MCP server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    main()