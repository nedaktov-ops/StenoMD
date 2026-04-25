#!/usr/bin/env python3
"""
Entity Resolver for StenoMD
Uses hybrid approach: keyword rules + Ollama for ambiguous cases

Features:
- Canonical MP database from vault
- Fuzzy name matching with Ollama
- Confidence scoring
- Auto-resolve to highest confidence

Usage:
    python3 entity_resolver.py --resolve
    python3 entity_resolver.py --stats
"""

import json
import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import os

# Get project root (3 levels up from this file: resolve -> scripts -> project)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
VAULT_DIR = PROJECT_DIR / "vault"
KG_DIR = PROJECT_DIR / "knowledge_graph"
RESOLVE_DIR = SCRIPT_DIR
RESOLVE_DIR.mkdir(parents=True, exist_ok=True)

CANONICAL_DB = RESOLVE_DIR / "canonical.db"


@dataclass
class CanonicalMP:
    """Canonical MP entity."""
    id: str
    name: str
    normalized_name: str
    chamber: str  # 'deputies' or 'senate'
    first_session: Optional[str] = None
    last_session: Optional[str] = None
    session_count: int = 0
    aliases: List[str] = field(default_factory=list)
    ollama_confidence: Optional[float] = None


@dataclass
class MatchResult:
    """Result of entity matching."""
    canonical_id: Optional[str]
    canonical_name: str
    confidence: float
    method: str  # 'exact', 'normalized', 'fuzzy', 'ollama'


class EntityResolver:
    """Resolves MP names to canonical entities."""
    
    # Name variations that indicate same person
    HONORIFICS = ['domnul', 'doamna', 'dl', 'dna', 'dr', 'ing.']
    
    # Common name normalizations - expanded for Romanian diacritics
    NAME_NORMALIZATIONS = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ă': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'Î': 'I',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u',
        'ț': 't', 'Ț': 'T', 'ş': 's', 'Ş': 'S',
        'ă': 'a', 'Ă': 'A',
    }
    
    def __init__(self):
        self.canonical_mps: Dict[str, CanonicalMP] = {}
        self.ollama_model = self._get_ollama_model()
        self._load_canonical_db()
    
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
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for matching."""
        # Remove honorifics
        name = name.lower()
        for h in self.HONORIFICS:
            name = name.replace(h, '')
        
        # Normalize diacritics
        for old, new in self.NAME_NORMALIZATIONS.items():
            name = name.replace(old, new)
        
        # Remove extra whitespace and dashes
        name = re.sub(r'[\s\-]+', ' ', name).strip()
        
        return name
    
    def _load_canonical_db(self):
        """Load canonical MP database."""
        if CANONICAL_DB.exists():
            conn = sqlite3.connect(CANONICAL_DB)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM canonical_mps")
            for row in cursor.fetchall():
                mp = CanonicalMP(
                    id=row['id'],
                    name=row['name'],
                    normalized_name=row['normalized_name'],
                    chamber=row['chamber'],
                    first_session=row['first_session'],
                    last_session=row['last_session'],
                    session_count=row['session_count'],
                    aliases=json.loads(row['aliases']) if row['aliases'] else []
                )
                self.canonical_mps[mp.id] = mp
            conn.close()
            print(f"Loaded {len(self.canonical_mps)} canonical MPs")
        else:
            self._build_canonical_db()
    
    def _build_canonical_db(self):
        """Build canonical MP database from vault."""
        print("Building canonical MP database from vault...")
        
        # Collect all MPs from vault
        all_mps = defaultdict(lambda: {'chamber': None, 'sessions': []})
        
        # Load from deputies
        deputies_dir = VAULT_DIR / "politicians" / "deputies"
        print(f"Checking deputies dir: {deputies_dir}")
        if deputies_dir.exists():
            mp_files = list(deputies_dir.glob("*.md"))
            print(f"Found {len(mp_files)} deputy files")
            for mp_file in mp_files:
                name = mp_file.stem.replace('-', ' ')
                all_mps[name]['chamber'] = 'deputies'
        
        # Load from senators
        senators_dir = VAULT_DIR / "politicians" / "senators"
        print(f"Checking senators dir: {senators_dir}")
        if senators_dir.exists():
            mp_files = list(senators_dir.glob("*.md"))
            print(f"Found {len(mp_files)} senator files")
            for mp_file in mp_files:
                name = mp_file.stem.replace('-', ' ')
                all_mps[name]['chamber'] = 'senators'
        
        print(f"Total MPs collected: {len(all_mps)}")
        
        # Create canonical entries
        for idx, (name, data) in enumerate(all_mps.items()):
            mp_id = f"mp_{idx:05d}"
            normalized = self._normalize_name(name)
            
            mp = CanonicalMP(
                id=mp_id,
                name=name,
                normalized_name=normalized,
                chamber=data['chamber'],
                aliases=[name, normalized]
            )
            self.canonical_mps[mp_id] = mp
        
        # Save to database
        self._save_canonical_db()
        print(f"Created {len(self.canonical_mps)} canonical MPs")
    
    def _save_canonical_db(self):
        """Save canonical MP database."""
        conn = sqlite3.connect(CANONICAL_DB)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS canonical_mps (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                normalized_name TEXT,
                chamber TEXT,
                first_session TEXT,
                last_session TEXT,
                session_count INTEGER DEFAULT 0,
                aliases TEXT,
                ollama_confidence REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("DELETE FROM canonical_mps")
        
        for mp in self.canonical_mps.values():
            cursor.execute("""
                INSERT INTO canonical_mps 
                (id, name, normalized_name, chamber, first_session, last_session, session_count, aliases, ollama_confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mp.id, mp.name, mp.normalized_name, mp.chamber,
                mp.first_session, mp.last_session, mp.session_count,
                json.dumps(mp.aliases), mp.ollama_confidence
            ))
        
        conn.commit()
        conn.close()
    
    def resolve(self, name: str, chamber: str = None) -> MatchResult:
        """Resolve a name to canonical MP."""
        normalized = self._normalize_name(name)
        
        # 1. Exact match
        for mp in self.canonical_mps.values():
            if mp.name.lower() == name.lower():
                return MatchResult(mp.id, mp.name, 1.0, 'exact')
        
        # 2. Normalized match
        for mp in self.canonical_mps.values():
            if mp.normalized_name == normalized:
                if chamber and mp.chamber != chamber:
                    continue
                return MatchResult(mp.id, mp.name, 0.95, 'normalized')
        
        # 3. Fuzzy match (simple)
        for mp in self.canonical_mps.values():
            if normalized in mp.normalized_name or mp.normalized_name in normalized:
                if chamber and mp.chamber != chamber:
                    continue
                return MatchResult(mp.id, mp.name, 0.85, 'fuzzy')
        
        # 4. Ollama match for ambiguous cases
        if self.ollama_model:
            return self._resolve_with_ollama(name, normalized, chamber)
        
        # No match found
        return MatchResult(None, name, 0.0, 'none')
    
    def _resolve_with_ollama(self, name: str, normalized: str, chamber: str = None) -> MatchResult:
        """Use Ollama for ambiguous name matching."""
        import subprocess
        
        # Build context with known MPs
        candidates = []
        for mp in list(self.canonical_mps.values())[:20]:
            if chamber and mp.chamber != chamber:
                continue
            candidates.append(mp.name)
        
        if not candidates:
            return MatchResult(None, name, 0.0, 'ollama')
        
        prompt = f"""Match this name from Romanian Parliament: "{name}"

Candidates: {', '.join(candidates[:10])}

Is "{name}" the same person as any candidate? Just answer with the exact candidate name or "NONE".
"""
        
        try:
            result = subprocess.run(
                ['ollama', 'run', self.ollama_model, prompt],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                answer = result.stdout.strip().strip('"')
                
                # Find matched MP
                for mp in self.canonical_mps.values():
                    if mp.name.lower() == answer.lower():
                        return MatchResult(mp.id, mp.name, 0.8, 'ollama')
        
        except Exception as e:
            print(f"Ollama error: {e}")
        
        return MatchResult(None, name, 0.0, 'ollama')
    
    def add_alias(self, canonical_id: str, alias: str):
        """Add alias to canonical MP."""
        if canonical_id in self.canonical_mps:
            mp = self.canonical_mps[canonical_id]
            if alias not in mp.aliases:
                mp.aliases.append(alias)
            self._save_canonical_db()
    
    def get_stats(self) -> Dict:
        """Get resolver statistics."""
        chamber_counts = defaultdict(int)
        for mp in self.canonical_mps.values():
            chamber_counts[mp.chamber] += 1
        
        return {
            'total_mps': len(self.canonical_mps),
            'by_chamber': dict(chamber_counts),
            'ollama_model': self.ollama_model
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Entity Resolver')
    parser.add_argument('--resolve', action='store_true', help='Run resolution')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    parser.add_argument('--name', help='Resolve single name')
    parser.add_argument('--chamber', help='Filter by chamber')
    
    args = parser.parse_args()
    
    resolver = EntityResolver()
    
    if args.stats:
        stats = resolver.get_stats()
        print(f"Total canonical MPs: {stats['total_mps']}")
        print(f"By chamber: {stats['by_chamber']}")
        print(f"Ollama model: {stats['ollama_model']}")
    
    elif args.name:
        result = resolver.resolve(args.name, args.chamber)
        print(f"Name: {args.name}")
        print(f"Resolved to: {result.canonical_name} (ID: {result.canonical_id})")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Method: {result.method}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()