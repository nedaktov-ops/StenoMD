"""Pattern Miner - Automatically discovers patterns."""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from collections import Counter

try:
    from config import get_config
    config = get_config()
    DEFAULT_PROJECT_ROOT = config.PROJECT_ROOT
except ImportError:
    DEFAULT_PROJECT_ROOT = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")


class PatternMiner:
    """Automatically discovers patterns in project."""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            project_root = DEFAULT_PROJECT_ROOT
        self.project_root = Path(project_root)
        self.scripts_dir = self.project_root / "scripts"
        self.memory_dir = self.scripts_dir / "memory"
        
    def mine_success_patterns(self) -> List[Dict]:
        """Find patterns in successful actions."""
        patterns = []
        
        # Check memory actions
        actions_file = self.memory_dir / "actions.json"
        if actions_file.exists():
            try:
                with open(actions_file) as f:
                    actions = json.load(f)
                    
                    # Find successful actions
                    for action in actions:
                        if action.get('outcome', {}).get('success'):
                            patterns.append({
                                'type': 'success',
                                'action': action.get('action', {}),
                                'frequency': 1
                            })
            except:
                pass
        
        return patterns
    
    def mine_failure_patterns(self) -> List[Dict]:
        """Find patterns in failures."""
        patterns = []
        
        # Check memory for failures
        actions_file = self.memory_dir / "actions.json"
        if actions_file.exists():
            try:
                with open(actions_file) as f:
                    actions = json.load(f)
                    
                    for action in actions:
                        if not action.get('outcome', {}).get('success', True):
                            patterns.append({
                                'type': 'failure',
                                'action': action.get('action', {}),
                                'error': action.get('outcome', {}).get('error', 'unknown')
                            })
            except:
                pass
        
        return patterns
    
    def mine_code_patterns(self) -> List[Dict]:
        """Find patterns in code."""
        patterns = []
        
        # Find common patterns in agents
        for agent_file in [self.scripts_dir / "agents/cdep_agent.py",
                          self.scripts_dir / "agents/senat_agent.py"]:
            if agent_file.exists():
                content = agent_file.read_text()
                
                # Find regex patterns
                import re
                regexes = re.findall(r'\w+_PATTERN.*?=.*?re\.compile', content)
                if regexes:
                    patterns.append({
                        'type': 'regex',
                        'file': agent_file.name,
                        'patterns': len(regexes)
                    })
        
        return patterns
    
    def mine_data_patterns(self) -> List[Dict]:
        """Find patterns in data."""
        patterns = []
        
        # Check sessions directory
        vault = self.project_root / "vault/sessions"
        if vault.exists():
            for chamber in ['deputies', 'senate']:
                chamber_dir = vault / chamber
                if chamber_dir.exists():
                    sessions = list(chamber_dir.glob("*.md"))
                    
                    # Extract year patterns
                    years = Counter()
                    for s in sessions:
                        try:
                            year = s.stem[:4]
                            if year.isdigit():
                                years[year] += 1
                        except:
                            pass
                    
                    patterns.append({
                        'type': 'sessions_by_year',
                        'chamber': chamber,
                        'distribution': dict(years)
                    })
        
        return patterns
    
    def suggest_improvements(self) -> List[Dict]:
        """Suggest improvements based on patterns."""
        suggestions = []
        
        # Check data coverage
        patterns = self.mine_data_patterns()
        for pattern in patterns:
            if pattern['type'] == 'sessions_by_year':
                dist = pattern['distribution']
                # If only recent years, suggest historical research
                if max([int(y) for y in dist.keys()], default=0) < 2020:
                    suggestions.append({
                        'type': 'data_gap',
                        'description': 'Limited historical data (pre-2020)',
                        'priority': 'high',
                        'action': 'Research alternative historical sources'
                    })
        
        # Check failures
        failures = self.mine_failure_patterns()
        if failures:
            suggestions.append({
                'type': 'error_pattern',
                'description': f'{len(failures)} failure patterns detected',
                'priority': 'medium',
                'action': 'Review error patterns'
            })
        
        return suggestions
    
    def generate_report(self) -> str:
        """Generate pattern analysis report."""
        successes = self.mine_success_patterns()
        failures = self.mine_failure_patterns()
        code = self.mine_code_patterns()
        data = self.mine_data_patterns()
        suggestions = self.suggest_improvements()
        
        report = f"""
# StenoMD Pattern Analysis Report
Generated: {datetime.now().isoformat()}

## Found Patterns

### Success Patterns
- Count: {len(successes)}

### Failure Patterns  
- Count: {len(failures)}

### Code Patterns
- Files with patterns: {len(code)}

### Data Patterns
"""
        for d in data:
            report += f"- {d['chamber']}: {sum(d['distribution'].values())} sessions\n"
        
        report += "\n## Suggestions\n"
        for s in suggestions:
            report += f"- [{s['priority']}] {s['description']}\n"
        
        return report


if __name__ == "__main__":
    miner = PatternMiner()
    print(miner.generate_report())