"""
Debugging Engine Module

Provides intelligent debugging assistance:
- Error analysis and parsing
- Root cause tracing
- Known solution search
- Fix generation
- Step-by-step guides
"""

import re
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from memory import MemoryStore


class DebuggingEngine:
    """
    Intelligent debugging assistance engine.
    
    Capabilities:
    - Error analysis (parse and understand errors)
    - Root cause tracing (trace to original source)
    - Known solutions (find similar past fixes)
    - Fix generation (suggest proven fixes)
    - Step-by-step guides (debugging instructions)
    """
    
    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path(__file__).parent.parent.parent
        self.memory = MemoryStore(self.project_dir)
    
    def analyze_error(self, error: Any) -> Dict:
        """
        Analyze an error and extract key information.
        
        Args:
            error: Error object or string
            
        Returns:
            Analysis with error type, message, context
        """
        analysis = {
            'type': 'unknown',
            'message': '',
            'location': None,
            'context': {},
            'severity': 'medium'
        }
        
        error_str = str(error)
        
        # Parse error type
        if isinstance(error, Exception):
            analysis['type'] = type(error).__name__
        elif 'Error' in error_str:
            match = re.search(r'(\w+Error)', error_str)
            if match:
                analysis['type'] = match.group(1)
        
        # Extract error message
        analysis['message'] = error_str[:200]
        
        # Parse common error patterns
        patterns = [
            (r'File "([^"]+)"', 'file'),
            (r'line (\d+)', 'line'),
            (r'ModuleNotFoundError', 'missing_module'),
            (r'ImportError', 'import'),
            (r'AttributeError', 'attribute'),
            (r'TypeError', 'type'),
            (r'ValueError', 'value'),
            (r'PermissionError', 'permission'),
            (r'FileNotFoundError', 'file_not_found'),
            (r'ConnectionError', 'connection'),
            (r'TimeoutError', 'timeout')
        ]
        
        for pattern, error_type in patterns:
            if re.search(pattern, error_str, re.IGNORECASE):
                analysis['context'][error_type] = True
                
                # Set severity
                if error_type in ['missing_module', 'import', 'permission', 'file_not_found']:
                    analysis['severity'] = 'high'
                elif error_type in ['attribute', 'type', 'value']:
                    analysis['severity'] = 'medium'
                
                break
        
        # Extract file location
        file_match = re.search(r'File "([^"]+)"', error_str)
        line_match = re.search(r'line (\d+)', error_str)
        
        if file_match:
            analysis['location'] = {
                'file': file_match.group(1).split('/')[-1],
                'path': file_match.group(1)
            }
        if line_match:
            if analysis['location']:
                analysis['location']['line'] = int(line_match.group(1))
        
        # Extract specific values
        value_match = re.search(r"'([^']+)'", error_str)
        if value_match:
            analysis['context']['value'] = value_match.group(1)
        
        return analysis
    
    def find_root_cause(self, error: Dict) -> Dict:
        """
        Trace error to its root cause.
        
        Args:
            error: Error analysis dict
            
        Returns:
            Root cause analysis with chain
        """
        root_cause = {
            'primary_cause': None,
            'chain': [],
            'confidence': 0.5
        }
        
        error_type = error.get('type', '')
        error_message = error.get('message', '')
        
        # Common root cause patterns
        cause_patterns = {
            'ModuleNotFoundError': {
                'cause': 'Missing dependency',
                'chain': ['Import statement failed', 'Module not installed', 'Dependencies not set up']
            },
            'ImportError': {
                'cause': 'Import chain broken',
                'chain': ['Module import failed', 'Circular import or missing module', 'Check import statements']
            },
            'AttributeError': {
                'cause': 'Object missing attribute',
                'chain': ['Attribute access failed', 'Object type mismatch', 'Initialize object properly']
            },
            'TypeError': {
                'cause': 'Wrong type passed',
                'chain': ['Type check failed', 'Argument type mismatch', 'Check function signature']
            },
            'FileNotFoundError': {
                'cause': 'File path incorrect',
                'chain': ['File access failed', 'Path does not exist or wrong', 'Verify file path']
            },
            'PermissionError': {
                'cause': 'Access denied',
                'chain': ['Permission check failed', 'Insufficient permissions', 'Check file/directory permissions']
            },
            'KeyError': {
                'cause': 'Missing dictionary key',
                'chain': ['Dictionary access failed', 'Key not present', 'Use .get() with default or add key']
            },
            'IndexError': {
                'cause': 'Index out of range',
                'chain': ['List access failed', 'Index exceeds length', 'Check list length first']
            }
        }
        
        if error_type in cause_patterns:
            pattern = cause_patterns[error_type]
            root_cause['primary_cause'] = pattern['cause']
            root_cause['chain'] = pattern['chain']
            root_cause['confidence'] = 0.85
        else:
            # Generic analysis
            if 'file' in error_message.lower():
                root_cause['primary_cause'] = 'File-related issue'
                root_cause['chain'] = ['File operation failed', 'Check file path', 'Verify file exists']
            elif 'connection' in error_message.lower():
                root_cause['primary_cause'] = 'Network/connection issue'
                root_cause['chain'] = ['Connection failed', 'Check network', 'Retry with timeout']
            else:
                root_cause['primary_cause'] = 'Unknown - needs investigation'
                root_cause['chain'] = ['Error occurred', 'Gather more context', 'Search for similar errors']
        
        return root_cause
    
    def search_known_solutions(self, error: Dict) -> List[Dict]:
        """
        Search for known solutions to similar errors.
        
        Args:
            error: Error analysis dict
            
        Returns:
            List of known solutions with success rates
        """
        solutions = []
        
        error_type = error.get('type', '')
        error_message = error.get('message', '')
        
        # Search memory for similar errors
        query = f"{error_type} {error_message[:50]}"
        similar = self.memory.recall(query, limit=10)
        
        # Filter to failures that were subsequently fixed
        for action in similar:
            if not action.get('success'):
                # This error failed - check if there's a follow-up fix
                fix_actions = self.memory.recall(f"fix {error_type}", limit=5)
                for fix in fix_actions:
                    if fix.get('success'):
                        solutions.append({
                            'fix': fix.get('command', 'Unknown'),
                            'success_rate': 0.9,
                            'similarity': 0.7,
                            'last_used': fix.get('timestamp'),
                            'description': f'Fixed similar {error_type} error'
                        })
        
        # Add known patterns from built-in knowledge
        known_fixes = self._get_known_fixes(error_type)
        solutions.extend(known_fixes)
        
        # Deduplicate and sort by success rate
        seen = set()
        unique_solutions = []
        for sol in solutions:
            fix = sol.get('fix', '')
            if fix not in seen:
                seen.add(fix)
                unique_solutions.append(sol)
        
        return sorted(unique_solutions, key=lambda x: x.get('success_rate', 0), reverse=True)
    
    def _get_known_fixes(self, error_type: str) -> List[Dict]:
        """Get built-in known fixes for common errors."""
        known_fixes = {
            'ModuleNotFoundError': [
                {
                    'fix': 'pip install beautifulsoup4 lxml requests',
                    'success_rate': 0.95,
                    'similarity': 0.6,
                    'description': 'Install missing Python dependencies'
                }
            ],
            'FileNotFoundError': [
                {
                    'fix': 'mkdir -p directory && cd directory',
                    'success_rate': 0.9,
                    'similarity': 0.5,
                    'description': 'Create missing directory'
                }
            ],
            'ImportError': [
                {
                    'fix': 'Check sys.path and import order',
                    'success_rate': 0.7,
                    'similarity': 0.4,
                    'description': 'Review import statements and path'
                }
            ]
        }
        return known_fixes.get(error_type, [])
    
    def generate_fix_guide(self, error: Dict, solutions: List[Dict]) -> Dict:
        """
        Generate step-by-step debugging guide.
        
        Args:
            error: Error analysis dict
            solutions: Known solutions
            
        Returns:
            Step-by-step fix guide
        """
        guide = {
            'title': f"Fixing {error.get('type', 'Unknown Error')}",
            'steps': [],
            'estimated_time': '5 minutes',
            'difficulty': 'medium',
            'solutions': solutions[:3]
        }
        
        error_type = error.get('type', '')
        location = error.get('location') or {}
        
        # Step 1: Understand the error
        guide['steps'].append({
            'step': 1,
            'title': 'Understand the Error',
            'action': f'The error "{error.get("message", "")}" occurred',
            'details': f'Type: {error_type}, Location: {location.get("file", "Unknown")}',
            'command': None
        })
        
        # Step 2: Check specific causes
        if error_type == 'ModuleNotFoundError':
            module_match = re.search(r"Module '([^']+)'", error.get('message', ''))
            if module_match:
                module = module_match.group(1)
                guide['steps'].append({
                    'step': 2,
                    'title': f'Install Missing Module',
                    'action': f'Module "{module}" is not installed',
                    'details': 'Install using pip or check requirements.txt',
                    'command': f'pip install {module}'
                })
        
        elif error_type == 'FileNotFoundError':
            file_match = re.search(r"File '([^']+)'", error.get('message', ''))
            if file_match:
                file_path = file_match.group(1)
                guide['steps'].append({
                    'step': 2,
                    'title': 'Check File Path',
                    'action': f'File "{file_path}" does not exist',
                    'details': 'Verify the file path is correct or create the file',
                    'command': f'ls -la {file_path}' if file_path else None
                })
        
        elif error_type == 'ImportError':
            guide['steps'].append({
                'step': 2,
                'title': 'Check Import Chain',
                'action': 'Review import statements',
                'details': 'Check sys.path, circular imports, and module initialization',
                'command': 'python3 -c "import sys; print(sys.path)"'
            })
        
        elif error_type == 'AttributeError':
            attr_match = re.search(r"'([^']+)' has no attribute '([^']+)'", error.get('message', ''))
            if attr_match:
                obj, attr = attr_match.groups()
                guide['steps'].append({
                    'step': 2,
                    'title': 'Check Object Type',
                    'action': f'Object "{obj}" is missing attribute "{attr}"',
                    'details': 'Verify the object type and how it is initialized',
                    'command': f'type({obj})'
                })
        
        # Step 3: Apply solution
        if solutions:
            best_solution = solutions[0]
            guide['steps'].append({
                'step': 3,
                'title': 'Apply Fix',
                'action': f'Use: {best_solution.get("fix", "See solution above")}',
                'details': best_solution.get('description', ''),
                'command': best_solution.get('fix'),
                'confidence': best_solution.get('success_rate', 0.8)
            })
        
        # Step 4: Verify
        guide['steps'].append({
            'step': 4,
            'title': 'Verify Fix',
            'action': 'Re-run the operation to confirm fix',
            'details': 'Check that the error no longer occurs',
            'command': 'python3 scripts/planner_agent.py --auto'
        })
        
        return guide
    
    def debug(self, error: Any) -> Dict:
        """
        Full debugging flow: analyze -> trace -> search -> guide.
        
        Args:
            error: Error object or string
            
        Returns:
            Complete debug report
        """
        # Analyze error
        analysis = self.analyze_error(error)
        
        # Find root cause
        root_cause = self.find_root_cause(analysis)
        
        # Search for solutions
        solutions = self.search_known_solutions(analysis)
        
        # Generate guide
        guide = self.generate_fix_guide(analysis, solutions)
        
        return {
            'analysis': analysis,
            'root_cause': root_cause,
            'solutions': solutions,
            'guide': guide,
            'timestamp': datetime.now().isoformat()
        }
    
    def learn_from_debug(self, error: Any, fix_worked: bool, fix_command: str = None):
        """
        Learn from a debugging session.
        
        Args:
            error: The error that was debugged
            fix_worked: Whether the fix succeeded
            fix_command: The command that was used
        """
        analysis = self.analyze_error(error)
        
        # Record the debugging experience
        action = {
            'type': 'debug',
            'issue': {
                'description': f"{analysis.get('type')}: {analysis.get('message', '')[:100]}",
                'type': 'bug',
                'severity': analysis.get('severity', 'medium')
            },
            'command': fix_command or analysis.get('type', 'debug'),
            'files_affected': [analysis.get('location', {}).get('path', '')] if analysis.get('location') else []
        }
        
        outcome = {
            'success': fix_worked,
            'duration_ms': 0,
            'result': 'Fixed' if fix_worked else 'Failed'
        }
        
        self.memory.learn(action, outcome)
    
    def format_debug_report(self, report: Dict) -> str:
        """
        Format debug report as readable markdown.
        
        Args:
            report: Debug report dict
            
        Returns:
            Markdown formatted report
        """
        lines = []
        
        analysis = report.get('analysis', {})
        root_cause = report.get('root_cause', {})
        solutions = report.get('solutions', [])
        guide = report.get('guide', {})
        
        lines.append(f"# Debug Report: {analysis.get('type', 'Unknown Error')}")
        lines.append(f"**Generated:** {report.get('timestamp', '')}")
        lines.append("")
        
        lines.append("## Error Analysis")
        lines.append(f"- **Type:** {analysis.get('type')}")
        lines.append(f"- **Message:** {analysis.get('message', '')}")
        lines.append(f"- **Severity:** {analysis.get('severity', 'medium')}")
        if analysis.get('location'):
            loc = analysis['location']
            lines.append(f"- **Location:** {loc.get('file', 'Unknown')} (line {loc.get('line', 'N/A')})")
        
        lines.append("")
        lines.append("## Root Cause")
        lines.append(f"**Primary Cause:** {root_cause.get('primary_cause', 'Unknown')}")
        lines.append(f"**Confidence:** {root_cause.get('confidence', 0) * 100:.0f}%")
        
        if root_cause.get('chain'):
            lines.append("")
            lines.append("**Analysis Chain:**")
            for i, step in enumerate(root_cause['chain'], 1):
                lines.append(f"{i}. {step}")
        
        if solutions:
            lines.append("")
            lines.append("## Known Solutions")
            for i, sol in enumerate(solutions[:3], 1):
                rate = sol.get('success_rate', 0) * 100
                lines.append(f"{i}. **{sol.get('fix', 'Unknown')}** ({rate:.0f}% success)")
                lines.append(f"   {sol.get('description', '')}")
        
        if guide.get('steps'):
            lines.append("")
            lines.append("## Step-by-Step Guide")
            lines.append(f"**Estimated Time:** {guide.get('estimated_time', '5 minutes')}")
            lines.append(f"**Difficulty:** {guide.get('difficulty', 'medium')}")
            lines.append("")
            
            for step in guide['steps']:
                lines.append(f"### Step {step['step']}: {step['title']}")
                lines.append(f"**Action:** {step.get('action', '')}")
                if step.get('details'):
                    lines.append(f"**Details:** {step['details']}")
                if step.get('command'):
                    lines.append(f"**Command:** `{step['command']}`")
                if step.get('confidence'):
                    lines.append(f"**Confidence:** {step['confidence'] * 100:.0f}%")
                lines.append("")
        
        return "\n".join(lines)