#!/usr/bin/env python3
"""
REST API for StenoMD
Provides HTTP endpoints for parliamentary data

Usage:
    python3 rest_api.py
    python3 rest_api.py --port 5000

Endpoints:
    GET /api/stats           - Statistics
    GET /api/mp/<name>       - MP profile
    GET /api/session/<date>  - Session details  
    GET /api/law/<number>    - Law info
    GET /api/search?q=<query> - Search sessions
    GET /api/triples         - Knowledge graph triples
"""

import json
import sqlite3
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys

# Add parent to path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_DIR / "scripts"))

from parliament_qa import ParliamentQA

# Use centralized configuration
try:
    from config import get_config
    config = get_config()
    VAULT_DIR = config.VAULT_DIR
    KG_DIR = config.KG_DIR
    KG_DB = config.KG_DB
    ALLOWED_ORIGIN = config.ALLOWED_ORIGIN
except ImportError:
    # Fallback for backward compatibility
    VAULT_DIR = PROJECT_DIR / "vault"
    KG_DIR = PROJECT_DIR / "knowledge_graph"
    KG_DB = KG_DIR / "knowledge_graph.db"
    ALLOWED_ORIGIN = "localhost"


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler."""
    
    def _get_qa(self):
        """Get QA instance."""
        if not hasattr(self, '_qa'):
            self._qa = ParliamentQA()
        return self._qa
    
    def _set_cors_headers(self):
        """Set CORS headers from config."""
        self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_GET(self):
        """Handle GET requests."""
        self._set_cors_headers()
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        qa = self._get_qa()
        
        try:
            if path == '/api/stats':
                self._handle_stats()
            elif path == '/api/triples':
                self._handle_triples(query)
            elif path.startswith('/api/mp/'):
                name = path[9:]  # Remove '/api/mp/'
                self._handle_mp(name)
            elif path.startswith('/api/session/'):
                date = path[13:]  # Remove '/api/session/'
                self._handle_session(date, query.get('chamber', ['deputies'])[0])
            elif path.startswith('/api/law/'):
                law = path[10:]  # Remove '/api/law/'
                self._handle_law(law)
            elif path == '/api/search':
                q = query.get('q', [''])[0]
                self._handle_search(q, query.get('chamber', [None])[0])
            elif path == '/api/topics':
                self._handle_topics()
            elif path == '/api/positions':
                self._handle_positions()
            else:
                self._send_json({'error': 'Not found'}, status=404)
        except Exception as e:
            self._send_json({'error': str(e)}, status=500)
    
    def _send_json(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def _handle_stats(self):
        """Get statistics."""
        stats = self._get_qa().get_stats()
        self._send_json(stats)
    
    def _handle_triples(self, query):
        """Get knowledge graph triples."""
        subject = query.get('subject', [None])[0]
        predicate = query.get('predicate', [None])[0]
        obj = query.get('object', [None])[0]
        limit = int(query.get('limit', [100])[0])
        
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
        if obj:
            q += " AND object LIKE ?"
            params.append(f"%{obj}%")
        
        # Use parameterized query for LIMIT
        limit = min(max(1, int(limit)), 100)  # Sanitize and cap at 100
        params.append(limit)
        q += " LIMIT ?"
        
        cursor.execute(q, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        self._send_json({'triples': results, 'count': len(results)})
    
    def _handle_mp(self, name):
        """Get MP profile."""
        # URL decode
        import urllib.parse
        name = urllib.parse.unquote(name)
        
        result = self._get_qa().search_mp(name)
        if 'error' in result:
            self._send_json(result, status=404)
        else:
            self._send_json(result)
    
    def _handle_session(self, date, chamber):
        """Get session details."""
        import urllib.parse
        date = urllib.parse.unquote(date)
        
        result = self._get_qa().get_session(date, chamber)
        if 'error' in result:
            self._send_json(result, status=404)
        else:
            self._send_json(result)
    
    def _handle_law(self, law):
        """Get law info."""
        import urllib.parse
        law = urllib.parse.unquote(law)
        
        result = self._get_qa().get_law(law)
        self._send_json(result)
    
    def _handle_search(self, query, chamber):
        """Search sessions."""
        if not query:
            self._send_json({'error': 'Missing query parameter'}, status=400)
            return
        
        results = self._get_qa().search_sessions(query, chamber)
        self._send_json({'results': results, 'count': len(results)})
    
    def _handle_topics(self):
        """Get topic statistics."""
        conn = sqlite3.connect(KG_DB)
        cursor = conn.cursor()
        
        cursor.execute("SELECT topic, COUNT(*) as cnt FROM topics GROUP BY topic ORDER BY cnt DESC")
        topics = [{'topic': r[0], 'count': r[1]} for r in cursor.fetchall()]
        
        cursor.execute("SELECT COUNT(DISTINCT statement_id) FROM topics")
        statements = cursor.fetchone()[0]
        
        conn.close()
        
        self._send_json({'topics': topics, 'statements_classified': statements})
    
    def _handle_positions(self):
        """Get position statistics."""
        conn = sqlite3.connect(KG_DB)
        cursor = conn.cursor()
        
        cursor.execute("SELECT position, COUNT(*) as cnt FROM positions GROUP BY position")
        positions = [{'position': r[0], 'count': r[1]} for r in cursor.fetchall()]
        
        cursor.execute("SELECT method, COUNT(*) as cnt FROM positions GROUP BY method")
        methods = [{'method': r[0], 'count': r[1]} for r in cursor.fetchall()]
        
        conn.close()
        
        self._send_json({'positions': positions, 'methods': methods})
    
    def log_message(self, format, *args):
        """Override to reduce noise."""
        pass


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='StenoMD REST API')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    
    args = parser.parse_args()
    
    server = HTTPServer((args.host, args.port), RequestHandler)
    print(f"Starting StenoMD API on http://{args.host}:{args.port}")
    print("Endpoints:")
    print("  GET /api/stats        - Statistics")
    print("  GET /api/triples      - Knowledge graph triples")
    print("  GET /api/mp/<name>    - MP profile")
    print("  GET /api/session/<date> - Session details")
    print("  GET /api/law/<number> - Law info")
    print("  GET /api/search?q=    - Search sessions")
    print("  GET /api/topics       - Topic stats")
    print("  GET /api/positions    - Position stats")
    print("\nPress Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.shutdown()


if __name__ == '__main__':
    main()