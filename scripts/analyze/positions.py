#!/usr/bin/env python3
"""
Position Classifier for StenoMD
Hybrid approach: keyword rules + Ollama for ambiguous cases

Classifies MP statements as PRO, CONTRA, or NEUTRAL

Usage:
    python3 positions.py --classify
    python3 positions.py --stats
"""

import re
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
VAULT_DIR = PROJECT_DIR / "vault"
KG_DIR = PROJECT_DIR / "knowledge_graph"
KG_DB = KG_DIR / "knowledge_graph.db"


@dataclass
class Classification:
    """Statement classification result."""
    statement_id: str
    speaker: str
    position: str  # 'PRO', 'CONTRA', 'NEUTRAL'
    confidence: float
    method: str  # 'keyword', 'ollama'
    keywords_found: List[str]


class PositionClassifier:
    """Classifies MP statements by position."""
    
    # PRO keywords (supporting position)
    PRO_KEYWORDS = [
        'sunt de acord', 'sunt în acord', 'susțin', 'susțin propunerea',
        'vot pentru', 'vot în favoare', 'sunt favorabil', 'sunt favorabilă',
        'aprobat', 'aprob', 'agree', 'favor', 'da', 'exact', 'corect',
        'este necesar', 'este important', 'sprijin', 'sprijină',
        'benefic', 'util', 'oportun', 'necesar', 'justificat',
        'proiectul este bun', 'legea este necesară', 'votăm pentru'
    ]
    
    # CONTRA keywords (opposing position)
    CONTRA_KEYWORDS = [
        'nu sunt de acord', 'nu sunt în acord', 'nu susțin',
        'vot împotrivă', 'vot contra', 'mă opun', 'se opun',
        'resping', 'respingeți', 'respingem', 'nu votez',
        'nu este corect', 'nu este justificat', 'nu este necesar',
        'nu este oportun', 'dăunător', 'dăunătoare', 'periculos',
        'împotriva', 'contra', 'negative', 'defavorabil',
        'proiectul este rău', 'legea nu este necesară', 'nu putem accepts'
    ]
    
    def __init__(self):
        self.ollama_model = self._get_ollama_model()
        self._init_db()
    
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
    
    def _init_db(self):
        """Initialize classification database."""
        conn = sqlite3.connect(KG_DB)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                statement_id TEXT,
                speaker TEXT,
                position TEXT,
                confidence REAL,
                method TEXT,
                keywords_found TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_positions_speaker ON positions(speaker)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_positions_position ON positions(position)")
        
        conn.commit()
        conn.close()
    
    def classify_with_keywords(self, text: str) -> Tuple[str, List[str]]:
        """Classify using keyword matching."""
        text_lower = text.lower()
        
        pro_count = 0
        pro_found = []
        for keyword in self.PRO_KEYWORDS:
            if keyword in text_lower:
                pro_count += 1
                pro_found.append(keyword)
        
        contra_count = 0
        contra_found = []
        for keyword in self.CONTRA_KEYWORDS:
            if keyword in text_lower:
                contra_count += 1
                contra_found.append(keyword)
        
        all_found = pro_found + contra_found
        
        if pro_count > contra_count:
            return 'PRO', all_found
        elif contra_count > pro_count:
            return 'CONTRA', all_found
        elif pro_count > 0 and contra_count > 0:
            return 'NEUTRAL', all_found  # Tie
        else:
            return 'NEUTRAL', []
    
    def classify_with_ollama(self, text: str, speaker: str) -> str:
        """Classify using Ollama for ambiguous cases."""
        import subprocess
        
        if not self.ollama_model:
            return 'NEUTRAL'
        
        prompt = f"""Analyze this statement by {speaker} in Romanian Parliament.

Statement: "{text[:500]}..."

Is this statement SUPPORTING (PRO), OPPOSING (CONTRA), or NEUTRAL?

Just answer with one word: PRO, CONTRA, or NEUTRAL
"""
        
        try:
            result = subprocess.run(
                ['ollama', 'run', self.ollama_model, prompt],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                answer = result.stdout.strip().upper()
                if 'PRO' in answer:
                    return 'PRO'
                elif 'CONTRA' in answer or 'IMPOTRIVA' in answer:
                    return 'CONTRA'
        except Exception:
            pass
        
        return 'NEUTRAL'
    
    def classify(self, statement_id: str, speaker: str, text: str, 
                 use_ollama_if_ambiguous: bool = False) -> Classification:
        """Classify a statement.
        
        Note: Ollama is disabled by default to avoid timeouts.
        Set use_ollama_if_ambiguous=True to enable.
        """
        # First try keyword classification
        position, keywords_found = self.classify_with_keywords(text)
        
        if keywords_found:
            # Keyword match found
            confidence = 0.9 if keywords_found else 0.5
            return Classification(
                statement_id=statement_id,
                speaker=speaker,
                position=position,
                confidence=confidence,
                method='keyword',
                keywords_found=keywords_found
            )
        
        # No keywords found
        if use_ollama_if_ambiguous and self.ollama_model:
            # Try Ollama for ambiguous cases
            position = self.classify_with_ollama(text, speaker)
            return Classification(
                statement_id=statement_id,
                speaker=speaker,
                position=position,
                confidence=0.6,
                method='ollama',
                keywords_found=[]
            )
        
        # Default to neutral
        return Classification(
            statement_id=statement_id,
            speaker=speaker,
            position='NEUTRAL',
            confidence=0.3,
            method='default',
            keywords_found=[]
        )
    
    def classify_from_vault(self, chamber: str = 'deputies', limit: int = 100):
        """Classify statements from vault sessions."""
        chamber_dir = VAULT_DIR / "sessions" / chamber
        
        if not chamber_dir.exists():
            print(f"No vault directory for {chamber}")
            return 0
        
        conn = sqlite3.connect(KG_DB)
        cursor = conn.cursor()
        
        classified = 0
        sessions = list(chamber_dir.glob("*.md"))[:limit]
        
        for session_file in sessions:
            content = session_file.read_text(encoding='utf-8')
            
            # Extract statements (look for quoted text or speaker blocks)
            statements = self._extract_statements(content)
            
            for stmt_id, speaker, text in statements:
                classification = self.classify(stmt_id, speaker, text)
                
                cursor.execute("""
                    INSERT INTO positions 
                    (statement_id, speaker, position, confidence, method, keywords_found)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    classification.statement_id,
                    classification.speaker,
                    classification.position,
                    classification.confidence,
                    classification.method,
                    json.dumps(classification.keywords_found)
                ))
                classified += 1
        
        conn.commit()
        conn.close()
        print(f"Classified {classified} statements")
        return classified
    
    def _extract_statements(self, content: str) -> List[Tuple[str, str, str]]:
        """Extract statements from session content."""
        statements = []
        
        # Extract YAML frontmatter first
        yaml_section = ""
        if content.startswith('---'):
            yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if yaml_match:
                yaml_section = yaml_match.group(1)
        
        # Extract participants from YAML
        participants = []
        if yaml_section:
            for line in yaml_section.split('\n'):
                stripped = line.strip()
                if stripped.startswith('- '):
                    name = stripped[2:].strip()
                    if name:
                        participants.append(name)
        
        # Get content after frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) > 2:
                content = parts[2]
        
        # Get session content for statements
        if participants:
            # Get laws discussed
            laws_match = re.search(r'laws_discussed:\s*(.+)', yaml_section)
            laws = laws_match.group(1) if laws_match else ""
            
            # Get session title
            title_match = re.search(r'title:\s*(.+)', yaml_section)
            title = title_match.group(1) if title_match else ""
            
            # Use laws and title as content for classification
            session_text = f"{title}. Laws discussed: {laws}"
            
            # Create statement entries for each participant
            for participant in participants[:10]:  # Limit to first 10
                statements.append((
                    f"stmt_{len(statements)}",
                    participant,
                    session_text[:500]
                ))
        
        return statements
    
    def get_stats(self) -> Dict:
        """Get classification statistics."""
        conn = sqlite3.connect(KG_DB)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM positions")
        stats['total'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT position, COUNT(*) FROM positions GROUP BY position")
        stats['by_position'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT method, COUNT(*) FROM positions GROUP BY method")
        stats['by_method'] = dict(cursor.fetchall())
        
        cursor.execute("""
            SELECT speaker, position, COUNT(*) as cnt 
            FROM positions 
            GROUP BY speaker, position 
            ORDER BY cnt DESC 
            LIMIT 10
        """)
        stats['top_speakers'] = [{'speaker': r[0], 'position': r[1], 'count': r[2]} for r in cursor.fetchall()]
        
        conn.close()
        return stats


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Position Classifier')
    parser.add_argument('--classify', action='store_true', help='Classify statements')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--chamber', default='deputies', help='Chamber to process')
    parser.add_argument('--limit', type=int, default=100, help='Limit sessions')
    
    args = parser.parse_args()
    
    classifier = PositionClassifier()
    
    if args.classify:
        classifier.classify_from_vault(args.chamber, args.limit)
    
    if args.stats:
        stats = classifier.get_stats()
        print("=== Position Classification Stats ===")
        print(f"Total classified: {stats['total']}")
        print(f"By position: {stats.get('by_position', {})}")
        print(f"By method: {stats.get('by_method', {})}")
        print(f"Top speakers: {stats.get('top_speakers', [])}")


if __name__ == '__main__':
    main()