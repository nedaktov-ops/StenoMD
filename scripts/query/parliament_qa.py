#!/usr/bin/env python3
"""
Parliament QA - Natural Language Query Interface
Uses Ollama for semantic search and question answering

Usage:
    python3 parliament_qa.py --query "What did Marcel Ciolacu say about economy?"
    python3 parliament_qa.py --interactive
"""

import json
import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
SCRIPTS_DIR = PROJECT_DIR / "scripts"

# Use centralized configuration
try:
    from config import get_config
    config = get_config()
    VAULT_DIR = config.VAULT_DIR
    KG_DIR = config.KG_DIR
    KG_DB = config.KG_DB
except ImportError:
    VAULT_DIR = PROJECT_DIR / "vault"
    KG_DIR = PROJECT_DIR / "knowledge_graph"
    KG_DB = KG_DIR / "knowledge_graph.db"

RESOLVE_DIR = SCRIPTS_DIR / "resolve"


class ParliamentQA:
    """Natural language query interface for parliamentary data."""
    
    def __init__(self):
        self.ollama_model = self._get_ollama_model()
        self._init_connection()
    
    def _get_ollama_model(self) -> Optional[str]:
        """Get available Ollama model."""
        import subprocess
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'phi' in line.lower():
                        return 'phi3'
                    if 'qwen' in line.lower():
                        return 'qwen2.5-coder:1.5b'
            return None
        except Exception:
            return None
    
    def _init_connection(self):
        """Initialize database connection."""
        self.conn = sqlite3.connect(KG_DB)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close database connection."""
        self.conn.close()
    
    def search_sessions(self, query: str, chamber: str = None, limit: int = 5) -> List[Dict]:
        """Search sessions by query."""
        chamber_dir = VAULT_DIR / "sessions"
        
        if chamber:
            chamber_dir = chamber_dir / chamber
        
        if not chamber_dir.exists():
            return []
        
        results = []
        sessions = list(chamber_dir.glob("*.md"))
        
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        for session_file in sessions:
            content = session_file.read_text(encoding='utf-8')
            content_lower = content.lower()
            
            # Simple keyword matching
            matches = sum(1 for word in query_words if word in content_lower)
            
            if matches > 0:
                # Extract title and date
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                date_match = re.search(r'^date:\s+(.+)$', content, re.MULTILINE)
                
                results.append({
                    'file': session_file.name,
                    'date': date_match.group(1) if date_match else session_file.stem,
                    'title': title_match.group(1) if title_match else 'Unknown',
                    'matches': matches,
                    'preview': content[:300]
                })
        
        # Sort by matches
        results.sort(key=lambda x: x['matches'], reverse=True)
        return results[:limit]
    
    def search_mp(self, name: str) -> Dict:
        """Search for MP by name."""
        canonical_db = RESOLVE_DIR / "canonical.db"
        
        if not canonical_db.exists():
            return {'error': 'Canonical database not found'}
        
        conn = sqlite3.connect(canonical_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Search by name or normalized name
        name_lower = name.lower()
        cursor.execute("""
            SELECT * FROM canonical_mps 
            WHERE LOWER(name) LIKE ? OR LOWER(normalized_name) LIKE ?
            LIMIT 10
        """, (f'%{name_lower}%', f'%{name_lower}%'))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'name': row['name'],
                'chamber': row['chamber'],
                'session_count': row['session_count']
            })
        
        conn.close()
        
        # Get session appearances from KG
        if results:
            mp_name = results[0]['name']
            self.cursor.execute("""
                SELECT object as session_date, COUNT(*) as cnt
                FROM triples
                WHERE subject = ? AND predicate = 'spoke_in'
                GROUP BY object
                ORDER BY cnt DESC
                LIMIT 10
            """, (mp_name,))
            
            sessions = [dict(row) for row in self.cursor.fetchall()]
            results[0]['sessions'] = sessions
        
        return results[0] if results else {'error': 'MP not found'}
    
    def get_session(self, date: str, chamber: str = 'deputies') -> Dict:
        """Get session by date."""
        session_file = VAULT_DIR / "sessions" / chamber / f"{date}.md"
        
        if not session_file.exists():
            # Try different extensions
            for ext in ['.md']:
                session_file = VAULT_DIR / "sessions" / chamber / f"{date}{ext}"
                if session_file.exists():
                    break
        
        if not session_file.exists():
            return {'error': 'Session not found'}
        
        content = session_file.read_text(encoding='utf-8')
        
        # Parse session data
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        date_match = re.search(r'^date:\s+(.+)$', content, re.MULTILINE)
        url_match = re.search(r'^url:\s+(.+)$', content, re.MULTILINE)
        laws_match = re.search(r'^laws_discussed:\s*(.+)$', content, re.MULTILINE)
        
        # Extract participants
        participants = []
        for match in re.finditer(r'^- \[{2}([^\]]+)\]\(([^)]+)\)$', content, re.MULTILINE):
            participants.append({'name': match.group(1), 'session': match.group(2)})
        
        # Extract laws
        laws = []
        if laws_match:
            laws_text = laws_match.group(1)
            laws = re.findall(r'\d+/\d{4}', laws_text)
        
        return {
            'date': date_match.group(1) if date_match else date,
            'title': title_match.group(1) if title_match else 'Unknown',
            'url': url_match.group(1) if url_match else None,
            'participants': [p['name'] for p in participants],
            'laws': laws,
            'preview': content[:500]
        }
    
    def get_law(self, law_number: str) -> Dict:
        """Get law information."""
        # Search in triples
        self.cursor.execute("""
            SELECT subject, predicate, object, source
            FROM triples
            WHERE object = ? OR object LIKE ?
            LIMIT 20
        """, (law_number, f'%{law_number}%'))
        
        results = []
        for row in self.cursor.fetchall():
            results.append({
                'session': row['subject'],
                'predicate': row['predicate'],
                'source': row['source']
            })
        
        # Get topics for this law
        self.cursor.execute("""
            SELECT DISTINCT t.topic, t.keyword_matched
            FROM topics t
            JOIN triples tr ON t.statement_id LIKE '%' || tr.subject || '%'
            WHERE tr.object = ?
            LIMIT 10
        """, (law_number,))
        
        topics = [dict(row) for row in self.cursor.fetchall()]
        
        return {
            'law_number': law_number,
            'sessions_discussed': len(results),
            'sessions': results[:5],
            'topics': topics
        }
    
    def get_stats(self) -> Dict:
        """Get overall statistics."""
        stats = {}
        
        # Session counts
        for chamber in ['deputies', 'senate']:
            chamber_dir = VAULT_DIR / "sessions" / chamber
            if chamber_dir.exists():
                stats[f'{chamber}_sessions'] = len(list(chamber_dir.glob("*.md")))
        
        # KG stats
        self.cursor.execute("SELECT COUNT(*) FROM triples")
        stats['triples'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM positions")
        stats['positions_classified'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM topics")
        stats['topics_classified'] = self.cursor.fetchone()[0]
        
        # Top speakers
        self.cursor.execute("""
            SELECT speaker, COUNT(*) as cnt
            FROM positions
            GROUP BY speaker
            ORDER BY cnt DESC
            LIMIT 5
        """)
        stats['top_speakers'] = [dict(row) for row in self.cursor.fetchall()]
        
        return stats
    
    def answer_query(self, query: str) -> str:
        """Answer natural language query using Ollama."""
        if not self.ollama_model:
            return "Ollama not available. Using basic search instead."
        
        import subprocess
        
        # First, get relevant context
        sessions = self.search_sessions(query, limit=3)
        
        context = ""
        if sessions:
            context = "Relevant sessions:\n"
            for s in sessions:
                context += f"- {s['date']}: {s['title'][:100]}\n"
        
        # Build prompt
        prompt = f"""You are a helpful assistant answering questions about Romanian Parliament.

Context:
{context}

Question: {query}

Please provide a helpful answer based on the context and your knowledge.
If you don't have enough information, say so.
"""
        
        try:
            result = subprocess.run(
                ['ollama', 'run', self.ollama_model, prompt],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Parliament QA')
    parser.add_argument('--query', help='Natural language query')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--mp', help='Search MP by name')
    parser.add_argument('--session', help='Get session by date')
    parser.add_argument('--law', help='Get law info')
    parser.add_argument('--stats', action='store_true', help='Get statistics')
    parser.add_argument('--chamber', default='deputies', help='Chamber for session')
    
    args = parser.parse_args()
    
    qa = ParliamentQA()
    
    if args.query:
        # Try to answer with Ollama
        if qa.ollama_model:
            print(f"Query: {args.query}")
            print(f"Using model: {qa.ollama_model}")
            answer = qa.answer_query(args.query)
            print(f"\nAnswer: {answer}")
        else:
            # Fall back to basic search
            results = qa.search_sessions(args.query)
            print(f"Search results for: {args.query}")
            for r in results:
                print(f"  {r['date']}: {r['title'][:60]}")
    
    elif args.mp:
        result = qa.search_mp(args.mp)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.session:
        result = qa.get_session(args.session, args.chamber)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.law:
        result = qa.get_law(args.law)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.stats:
        result = qa.get_stats()
        print(json.dumps(result, indent=2))
    
    elif args.interactive:
        print("Parliament QA - Interactive Mode")
        print("Type 'quit' to exit\n")
        
        while True:
            query = input("Query> ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if qa.ollama_model:
                answer = qa.answer_query(query)
                print(f"\n{answer}\n")
            else:
                results = qa.search_sessions(query)
                print(f"Found {len(results)} sessions:")
                for r in results:
                    print(f"  {r['date']}: {r['title'][:60]}")
                print()
    
    else:
        parser.print_help()
    
    qa.close()


if __name__ == '__main__':
    main()