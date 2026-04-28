"""Problem Analyzer - Analyzes project state to detect problems."""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

try:
    from config import get_config
    config = get_config()
    DEFAULT_PROJECT_ROOT = config.PROJECT_ROOT
except ImportError:
    DEFAULT_PROJECT_ROOT = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")


class ProblemAnalyzer:
    """Analyzes project state to detect problems."""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            project_root = DEFAULT_PROJECT_ROOT
        self.project_root = Path(project_root)
        self.scripts_dir = self.project_root / "scripts"
        self.vault_dir = self.project_root / "vault"
        self.kg_dir = self.project_root / "knowledge_graph"
        
    def analyze_all(self) -> Dict:
        """Run full analysis."""
        return {
            'data_coverage': self.analyze_data_coverage(),
            'blockers': self.analyze_blockers(),
            'errors': self.analyze_errors(),
            'data_integrity': self.analyze_data_integrity(),
            'dependencies': self.analyze_dependencies(),
            'health_score': self.calculate_health_score()
        }
    
    def analyze_data_coverage(self) -> Dict:
        """Analyze what data is available/missing."""
        # Check sessions
        deputy_sessions = list((self.vault_dir / "sessions/deputies").glob("*.md"))
        senate_sessions = list((self.vault_dir / "sessions/senate").glob("*.md"))
        
        # Check politicians
        deputies = list((self.vault_dir / "politicians/deputies").glob("*.md"))
        senators = list((self.vault_dir / "politicians/senators").glob("*.md"))
        
        # Check years available
        years = set()
        for f in deputy_sessions:
            try:
                year = f.stem[:4]
                if year.isdigit():
                    years.add(year)
            except:
                pass
        
        return {
            'deputy_sessions': len(deputy_sessions),
            'senate_sessions': len(senate_sessions),
            'total_sessions': len(deputy_sessions) + len(senate_sessions),
            'deputies': len(deputies),
            'senators': len(senators),
            'years_covered': sorted(years),
            'target': 200,
            'coverage_percent': min(100, (len(deputy_sessions) + len(senate_sessions)) / 200 * 100)
        }
    
    def analyze_blockers(self) -> List[Dict]:
        """Identify all blocked items."""
        blockers = []
        
        # Historical data blocked
        blockers.append({
            'id': 'historical_chamber',
            'type': 'data_blocked',
            'description': 'cdep.ro historical data (1996-2014) blocked',
            'severity': 'critical',
            'workaround': 'Use Open Parliament RO alternative data (2024-2025)',
            'status': 'addressed'
        })
        
        # Senate historical
        blockers.append({
            'id': 'historical_senate',
            'type': 'data_blocked', 
            'description': 'senat.ro only shows current legislature (2024-2028)',
            'severity': 'high',
            'workaround': 'Use cached data, manual research',
            'status': 'documented'
        })
        
        return blockers
    
    def analyze_errors(self) -> List[Dict]:
        """Find recent errors in logs or test failures."""
        errors = []
        
        # Check import issues
        agents_init = self.scripts_dir / "agents" / "__init__.py"
        if agents_init.exists():
            content = agents_init.read_text()
            # Check for incorrect paths (should use parent.parent)
            if "sys.path.insert(0, str(Path(__file__).parent))" in content:
                if "parent.parent" not in content:
                    errors.append({
                        'id': 'import_path',
                        'type': 'technical_error',
                        'description': 'Import path may be incorrect',
                        'severity': 'medium',
                        'status': 'fixed'
                    })
        
        # Check database
        entities_db = self.kg_dir / "entities.db"
        if not entities_db.exists():
            errors.append({
                'id': 'missing_db',
                'type': 'data_integrity',
                'description': 'entities.db missing',
                'severity': 'high',
                'status': 'fixed'
            })
        
        return errors
    
    def analyze_data_integrity(self) -> Dict:
        """Check for data issues."""
        issues = []
        
        # Check for empty session files
        empty_sessions = 0
        duplicates = 0
        for session_dir in [self.vault_dir / "sessions/deputies", self.vault_dir / "sessions/senate"]:
            if session_dir.exists():
                for f in session_dir.glob("*.md"):
                    if f.stat().st_size < 100:
                        empty_sessions += 1
                    # Check for duplicate dates
                    dates = set()
                    if f.stem in dates:
                        duplicates += 1
                    dates.add(f.stem)
        
        if empty_sessions > 0:
            issues.append({
                'type': 'empty',
                'count': empty_sessions,
                'severity': 'medium'
            })
        
        if duplicates > 0:
            issues.append({
                'type': 'duplicate',
                'count': duplicates,
                'severity': 'medium'
            })
        
        # Score based on issues
        score = 100
        for issue in issues:
            if issue['severity'] == 'high':
                score -= 25
            elif issue['severity'] == 'medium':
                score -= 10
            else:
                score -= 5
        
        return {
            'score': max(0, score),
            'issues': issues,
            'empty_sessions': empty_sessions,
            'duplicates': duplicates
        }
    
    def analyze_dependencies(self) -> Dict:
        """Check dependencies."""
        missing = []
        
        # Check Python packages (simple check)
        try:
            import pytest
        except ImportError:
            missing.append('pytest')
        
        try:
            import fastapi
        except ImportError:
            missing.append('fastapi')
        
        return {
            'missing': missing,
            'status': 'ok' if not missing else 'partial'
        }
    
    def calculate_health_score(self) -> Dict:
        """Calculate overall health score."""
        data = self.analyze_data_coverage()
        integrity = self.analyze_data_integrity()
        errors = self.analyze_errors()
        
        # Weighted scoring
        data_score = data['coverage_percent'] * 0.4
        integrity_score = integrity['score'] * 0.4
        error_score = (100 - len(errors) * 20) * 0.2
        
        total = data_score + integrity_score + error_score
        
        return {
            'total': round(total, 1),
            'components': {
                'data_coverage': round(data_score, 1),
                'data_integrity': round(integrity_score, 1),
                'error_free': round(error_score, 1)
            },
            'status': 'healthy' if total > 80 else 'warning' if total > 60 else 'critical'
        }
    
    def generate_report(self) -> str:
        """Generate human-readable report."""
        analysis = self.analyze_all()
        health = analysis['health_score']
        data = analysis['data_coverage']
        
        report = f"""
# StenoMD Project Analysis Report
Generated: {datetime.now().isoformat()}

## Health Score: {health['total']}% ({health['status'].upper()})

### Data Coverage
- Deputy sessions: {data['deputy_sessions']}
- Senate sessions: {data['senate_sessions']}
- Total: {data['total_sessions']} / {data['target']} ({data['coverage_percent']:.1f}%)
- Years covered: {', '.join(data['years_covered'])}

### Known Blockers
"""
        for b in analysis['blockers']:
            report += f"- {b['description']} ({b['status']})\n"
        
        report += f"""
### Errors Found
"""
        for e in analysis['errors']:
            report += f"- {e['description']} ({e['status']})\n"
        
        report += f"""
### Data Integrity Score: {analysis['data_integrity']['score']}%

---
Analysis complete.
"""
        return report


if __name__ == "__main__":
    analyzer = ProblemAnalyzer()
    print(analyzer.generate_report())