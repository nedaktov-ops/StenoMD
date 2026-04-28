"""Solution Researcher - Researches solutions for problems."""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

try:
    from config import get_config
    config = get_config()
    DEFAULT_PROJECT_ROOT = config.PROJECT_ROOT
except ImportError:
    DEFAULT_PROJECT_ROOT = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")


class SolutionResearcher:
    """Researches solutions for problems."""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            project_root = DEFAULT_PROJECT_ROOT
        self.project_root = Path(project_root)
        self.scripts_dir = self.project_root / "scripts"
        self.memory_dir = self.scripts_dir / "memory"
        
    def search_memory(self, problem: str) -> List[Dict]:
        """Search learned patterns for solutions."""
        solutions = []
        
        # Check memory actions
        actions_file = self.memory_dir / "actions.json"
        if actions_file.exists():
            try:
                with open(actions_file) as f:
                    actions = json.load(f)
                    for action in actions:
                        # Try to match problem with stored actions
                        desc = action.get('description', '').lower()
                        if any(word in desc for word in problem.lower().split()):
                            solutions.append({
                                'source': 'memory',
                                'action': action.get('action', ''),
                                'outcome': action.get('outcome', ''),
                                'confidence': 0.8
                            })
            except:
                pass
        
        return solutions
    
    def search_codebase(self, problem: str) -> List[Dict]:
        """Search existing code for solutions."""
        solutions = []
        
        # Search for relevant files based on keywords
        keywords = problem.lower().split()
        
        # Check key files
        check_files = {
            'cdep_agent': self.scripts_dir / "agents/cdep_agent.py",
            'senat_agent': self.scripts_dir / "agents/senat_agent.py",
            'entity_resolver': self.scripts_dir / "resolve/entity_resolver.py",
            'validators': self.scripts_dir / "validators.py"
        }
        
        for name, path in check_files.items():
            if path.exists():
                content = path.read_text()
                for keyword in keywords:
                    if keyword in content.lower():
                        solutions.append({
                            'source': 'codebase',
                            'file': str(path),
                            'matched': keyword,
                            'confidence': 0.5
                        })
                        break
        
        return solutions
    
    def search_project_docs(self, problem: str) -> List[Dict]:
        """Search project documentation for solutions."""
        solutions = []
        
        docs = [
            self.project_root / "STRATEGY.md",
            self.project_root / "project-timeline.md",
            self.project_root / "project-logs.md"
        ]
        
        keywords = problem.lower().split()
        
        for doc in docs:
            if doc.exists():
                content = doc.read_text()
                for keyword in keywords:
                    if keyword in content.lower():
                        # Find nearby solution text
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if keyword in line.lower():
                                context = '\n'.join(lines[max(0, i-1):min(len(lines), i+2)])
                                solutions.append({
                                    'source': 'documentation',
                                    'file': doc.name,
                                    'context': context[:200],
                                    'confidence': 0.6
                                })
                                break
        
        return solutions
    
    def search_all(self, problem: str) -> Dict:
        """Search all sources for solutions."""
        memory_solutions = self.search_memory(problem)
        codebase_solutions = self.search_codebase(problem)
        doc_solutions = self.search_project_docs(problem)
        
        all_solutions = memory_solutions + codebase_solutions + doc_solutions
        
        return {
            'problem': problem,
            'solutions': all_solutions,
            'count': len(all_solutions),
            'best_confidence': max([s['confidence'] for s in all_solutions], default=0)
        }
    
    def research_fix(self, problem: str) -> Dict:
        """Research complete fix for a problem."""
        # Search all sources
        results = self.search_all(problem)
        
        # Combine unique solutions
        best_solution = None
        for solution in sorted(results['solutions'], key=lambda x: x['confidence'], reverse=True):
            if not best_solution:
                best_solution = solution
        
        return {
            'problem': problem,
            'found_solutions': results['count'],
            'recommended': best_solution,
            'research_complete': results['count'] > 0
        }
    
    def get_known_fixes(self) -> List[Dict]:
        """Get all known fixes from project history."""
        fixes = []
        
        # From STRATEGY.md - extract known fixes
        strategy = self.project_root / "STRATEGY.md"
        if strategy.exists():
            content = strategy.read_text()
            
            # Look for FIX markers
            fix_pattern = r'### Fix \d+: (.+)'
            for match in re.finditer(fix_pattern, content):
                fix_name = match.group(1)
                fixes.append({
                    'name': fix_name,
                    'source': 'STRATEGY.md',
                    'confidence': 0.9
                })
        
        # Add common fixes from experience
        common_fixes = [
            {
                'name': 'Remove &prn=1 from URL',
                'pattern': 'cdep.ro returns 404',
                'confidence': 0.93,
                'description': 'Removes problematic prn parameter from cdep.ro URLs'
            },
            {
                'name': 'Add colon to regex',
                'pattern': 'MP names not matching',
                'confidence': 0.85,
                'description': 'Added [:\\s]* to regex for optional colon'
            },
            {
                'name': 'Fix import path',
                'pattern': 'ModuleNotFoundError in agents',
                'confidence': 0.9,
                'description': 'Use parent.parent in sys.path'
            },
            {
                'name': 'Create entities.db',
                'pattern': 'entities.db missing',
                'confidence': 0.95,
                'description': 'Create symlink to knowledge_graph.db'
            }
        ]
        
        fixes.extend(common_fixes)
        
        return fixes


if __name__ == "__main__":
    researcher = SolutionResearcher()
    
    # Test with known problem
    result = researcher.research_fix("cdep.ro returns 404")
    print(f"Problem: {result['problem']}")
    print(f"Solutions found: {result['found_solutions']}")
    print(f"Research complete: {result['research_complete']}")
    
    # Get known fixes
    print("\n--- Known Fixes ---")
    for fix in researcher.get_known_fixes()[:5]:
        print(f"- {fix['name']} (confidence: {fix['confidence']})")