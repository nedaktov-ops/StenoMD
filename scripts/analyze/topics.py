#!/usr/bin/env python3
"""
Topic Classifier for StenoMD
Classifies parliamentary statements by topic

Topics: Economy, Health, Education, Justice, Defense, Environment, Social, European

Usage:
    python3 topics.py --classify
    python3 topics.py --stats
"""

import re
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
VAULT_DIR = PROJECT_DIR / "vault"
KG_DIR = PROJECT_DIR / "knowledge_graph"
KG_DB = KG_DIR / "knowledge_graph.db"


class TopicClassifier:
    """Classifies statements by topic."""
    
    TOPICS = {
        'economie': {
            'keywords': [
                'economie', 'economic', 'buget', 'finanțe', 'bani', 'investiții', 'PIB',
                'inflație', 'taxe', 'impozite', 'TVA', 'accize', 'datorie publică',
                'deficit', 'creștere economică', 'comerț', 'export', 'import',
                'euro', 'lei', 'RON', 'EUR', 'monedă', 'BNR', 'bancă',
                'afaceri', 'antreprenor', 'firmă', 'companie', 'profit',
                ' piață', 'concurență', 'liberalizare', 'privatizare'
            ],
            'description': 'Economy and Finance'
        },
        'sanatate': {
            'keywords': [
                'sănătate', 'medical', 'spital', 'doctor', 'pacienți', 'vaccin',
                'CNAS', 'asigurare', 'asigurări', 'sanitar', 'medicament',
                'tratament', 'diagnostic', 'terapie', 'intervenție', 'operație',
                'epidemie', 'pandemie', 'covid', 'virus', 'boală', 'sănătate publică',
                ' Ministerul Sănătății', 'MS', 'DSP', 'ambulance', 'URGENT'
            ],
            'description': 'Health'
        },
        'educatie': {
            'keywords': [
                'educație', 'învățământ', 'școală', 'universitate', 'studenți',
                'elev', 'profesor', 'învățător', 'educațional', 'școlar',
                'universitar', 'academic', ' facultate', ' liceu', ' gimnaziu',
                ' MEN', ' Ministerul Educației', 'bursă', 'grant', ' scholarship',
                'curriculum', 'programă', 'examen', 'bacalaureat', 'admitere'
            ],
            'description': 'Education'
        },
        'justitie': {
            'keywords': [
                'justiție', 'judicial', 'instanță', 'judecătorie', 'penal',
                'DNA', 'DIICOT', 'ICCJ', 'CSM', 'judecător', 'procuror',
                'proces', 'sentință', 'hotărâre', 'dosar', 'anchetă',
                'corupție', 'fraudă', 'abuz', 'infracțiune', 'pedeapsă',
                'legislație', 'cod penal', 'cod civil', 'lege', 'ordonanță'
            ],
            'description': 'Justice and Law'
        },
        'aparare': {
            'keywords': [
                'apărare', 'armată', 'militar', 'NATO', 'securitate',
                'defense', 'armament', 'tanc', 'avion', 'rachetă',
                'soldat', 'militar', 'veteran', 'rezervist', 'apărării',
                'MApN', 'Ministerul Apărării', 'strategie', 'securitate națională',
                'război', 'conflict', 'amenințare', 'terorism', 'inteligență'
            ],
            'description': 'Defense and Security'
        },
        'mediu': {
            'keywords': [
                'mediu', 'climă', 'poluare', 'verde', 'ecologie', 'ecologic',
                'ambient', 'deșeu', 'reciclare', 'emisiile', 'carbon', 'CO2',
                'Pământ', 'natură', 'faună', 'floră', 'protecția mediului',
                ' Ministerul Mediului', 'MM', 'APM', 'GNM', 'pădure', 'apă', 'râu'
            ],
            'description': 'Environment'
        },
        'social': {
            'keywords': [
                'social', 'pensie', 'alocație', 'beneficiu', 'asistență',
                'pensii', 'salariu', 'minim', 'venit', 'ajutor', 'socială',
                'sărăcie', 'marginalizare', 'vulnerabil', 'nevoie',
                'Ministerul Muncii', 'MMSS', 'ANPIS', 'asigurări sociale',
                'copil', 'familia', 'căsătorie', 'divorț', 'violență domestică'
            ],
            'description': 'Social Affairs'
        },
        'europa': {
            'keywords': [
                'european', 'UE', 'Bruxelles', 'euro', 'comisar',
                'europeni', 'Comisia Europeană', 'Consiliul European',
                'Parlamentul European', 'PE', 'directivă', 'regulament',
                ' fonduri europene', 'POIM', 'PNRR', 'MFE', '吸引',
                'integrare europeană', 'aderare', 'tratat', 'acord'
            ],
            'description': 'European Affairs'
        },
        'agricultura': {
            'keywords': [
                'agricultură', 'fermier', 'fermă', 'agricol', 'cultivare',
                'recoltă', 'porumb', 'grâu', 'tritur', 'viticultură',
                'zootehnie', 'creștere animale', 'bovine', 'ovine', 'porcine',
                'MADR', 'Ministerul Agriculturii', 'subvenție', 'plată',
                'SAPS', 'APIA', 'dezvoltare rurală', 'PDRP'
            ],
            'description': 'Agriculture'
        },
        'infrastructura': {
            'keywords': [
                'infrastructură', 'drum', 'autostradă', 'drumuri', 'șosea',
                'feroviar', 'cale ferată', 'tren', 'metrou', 'transport',
                ' CFR', 'Compania Națională de Căi Ferate', 'aeroport',
                'port', 'navigație', 'energic', 'energie', 'electricitate',
                'gaze', 'petrol', 'carburanți', 'combustibil'
            ],
            'description': 'Infrastructure'
        },
        'cultura': {
            'keywords': [
                'cultură', 'cultural', 'artă', 'artist', 'teatru', 'cinema', 'film',
                'muzee', 'muzeu', 'monument', 'patrimoniu', 'conservare',
                'CARANTINA', 'spectacol', 'concert', 'festival', 'carantină',
                'carantare', 'izolare', 'distanțare', 'restricții',
                'patrimoniu cultural', 'teatru', 'operă', 'balet'
            ],
            'description': 'Culture and Arts'
        },
        'cercetare': {
            'keywords': [
                'cercetare', 'cercetător', 'știință', 'scientific', 'inovare',
                'ANCSI', 'UEFISCDI', 'INCD', 'Institutul Național',
                'grant', 'proiect de cercetare', 'competiție',
                'doctorat', 'postdoctorat', 'laborator',
                'experIMENT', 'studiu clinic', 'trial',
                'inovație', 'tehnologie', 'high-tech'
            ],
            'description': 'Research and Innovation'
        },
        'transport': {
            'keywords': [
                'transport', 'transporturi', 'transport public',
                'metrou', 'autobuz', 'tramvai', 'troleibuz',
                'CFR', ' CFR Calatori', 'STB', 'metrorex',
                'șofer', 'conducător', 'vehicul', 'masina',
                'trafic', 'circulație', 'pod', 'pasarelă',
                'siguranța rutieră', 'accident', 'CNSU'
            ],
            'description': 'Transportation'
        },
        'energie': {
            'keywords': [
                'energie', 'energie electrică', 'energie regenerabilă',
                'electric', 'electricitate', 'curent',
                'ANRE', 'Transelectrica', 'Termoelectrica',
                'nuclear', 'centrală nucleară', 'Cernavodă',
                'eolian', 'vânt', 'turbină', 'parc eolian',
                'solar', 'fotovoltaic', 'panou solar',
                'hidroelectric', 'hidrocentralka',
                'gaz', 'gaze naturale', 'transgaz', 'romgaz',
                'petrol', 'țitei', 'extractie',
                'consum', 'consumator', 'factură', 'preț'
            ],
            'description': 'Energy'
        },
        'administratie': {
            'keywords': [
                'administrație', 'administratie publică', 'guvern',
                'minister', 'ministerul', 'departament', 'agenție',
                'Prefectura', 'prefect', 'primar', 'primărie',
                'consiliu', 'consiliul local', 'consiliul judetean',
                'CJ', 'CL', 'hotărâre', 'decizie',
                'ordine', 'ordonanță', 'HG', 'OG', 'OUG'
            ],
            'description': 'Public Administration'
        },
        'munca': {
            'keywords': [
                'muncă', 'lucru', 'angajare', 'angajat', 'angajator',
                'SOMAJ', 'șomaj', 'șomere', 'neangajat',
                'contract', 'contract de muncă', 'CIM',
                'salariu', 'brut', 'net', 'leafă',
                'relații de muncă', 'codul muncii',
                'inspectorat', 'ITM', 'control', 'amendă',
                'drepturi', 'obligații', 'pază', 'securitate'
            ],
            'description': 'Labor and Employment'
        }
    }
    
    def __init__(self):
        self._init_db()
    
    def _init_db(self):
        """Initialize topic database."""
        conn = sqlite3.connect(KG_DB)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                statement_id TEXT,
                topic TEXT,
                confidence REAL,
                keyword_matched TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_topics_statement ON topics(statement_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_topics_topic ON topics(topic)")
        
        conn.commit()
        conn.close()
    
    def classify(self, text: str) -> List[Tuple[str, float, str]]:
        """Classify text by topics.
        
        Returns list of (topic, confidence, keyword_matched) tuples
        """
        text_lower = text.lower()
        results = []
        
        for topic, config in self.TOPICS.items():
            matches = []
            for keyword in config['keywords']:
                if keyword.lower() in text_lower:
                    matches.append(keyword)
            
            if matches:
                confidence = min(0.5 + (len(matches) * 0.1), 1.0)
                results.append((topic, confidence, matches[0]))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
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
            
            # Extract text from content
            text_blocks = self._extract_text_blocks(content)
            
            for block_id, text in text_blocks:
                topics = self.classify(text)
                
                for topic, confidence, keyword in topics[:3]:  # Top 3 topics
                    cursor.execute("""
                        INSERT INTO topics 
                        (statement_id, topic, confidence, keyword_matched)
                        VALUES (?, ?, ?, ?)
                    """, (f"{session_file.stem}_{block_id}", topic, confidence, keyword))
                    classified += 1
        
        conn.commit()
        conn.close()
        print(f"Classified {classified} topic assignments")
        return classified
    
    def _extract_text_blocks(self, content: str) -> List[Tuple[int, str]]:
        """Extract text blocks from content."""
        blocks = []
        
        # Remove YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) > 2:
                content = parts[2]
        
        # Split by sections
        lines = content.split('\n')
        current_block = []
        block_id = 0
        
        for line in lines:
            # Skip headers and metadata
            if line.startswith('#') or line.startswith('**') or line.startswith('|'):
                if current_block and len(' '.join(current_block)) > 50:
                    blocks.append((block_id, ' '.join(current_block)))
                    block_id += 1
                current_block = []
            elif line.strip():
                current_block.append(line.strip())
        
        # Last block
        if current_block and len(' '.join(current_block)) > 50:
            blocks.append((block_id, ' '.join(current_block)))
        
        return blocks
    
    def get_stats(self) -> Dict:
        """Get topic classification statistics."""
        conn = sqlite3.connect(KG_DB)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(DISTINCT statement_id) FROM topics")
        stats['statements_with_topics'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT topic, COUNT(*) FROM topics GROUP BY topic ORDER BY COUNT(*) DESC")
        stats['by_topic'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT keyword_matched, COUNT(*) FROM topics GROUP BY keyword_matched ORDER BY COUNT(*) DESC LIMIT 20")
        stats['top_keywords'] = dict(cursor.fetchall())
        
        conn.close()
        return stats


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Topic Classifier')
    parser.add_argument('--classify', action='store_true', help='Classify statements')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--chamber', default='deputies', help='Chamber to process')
    parser.add_argument('--limit', type=int, default=100, help='Limit sessions')
    
    args = parser.parse_args()
    
    classifier = TopicClassifier()
    
    if args.classify:
        classifier.classify_from_vault(args.chamber, args.limit)
    
    if args.stats:
        stats = classifier.get_stats()
        print("=== Topic Classification Stats ===")
        print(f"Statements with topics: {stats['statements_with_topics']}")
        print(f"By topic: {stats['by_topic']}")
        print(f"Top keywords: {stats['top_keywords']}")


if __name__ == '__main__':
    main()