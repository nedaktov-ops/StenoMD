"""Decision Engine - Makes decisions based on confidence thresholds."""
import json
from datetime import datetime
from typing import Dict, List, Optional


class DecisionEngine:
    """Makes decisions based on confidence thresholds."""
    
    # Confidence thresholds
    AUTO_FIX_THRESHOLD = 0.90  # Auto-fix without confirmation
    SUGGEST_FIX_THRESHOLD = 0.70  # Suggest with details
    RESEARCH_THRESHOLD = 0.50  # Research more
    REPORT_THRESHOLD = 0.30  # Report uncertainty
    
    def __init__(self):
        self.decision_log = []
        
    def should_auto_fix(self, problem: Dict, solution: Dict) -> bool:
        """Determine if auto-fix should be applied."""
        confidence = solution.get('confidence', 0)
        severity = problem.get('severity', 'low')
        
        # Always auto-fix critical issues with high confidence
        if severity == 'critical' and confidence >= self.AUTO_FIX_THRESHOLD:
            return True
        
        # High severity needs higher confidence
        if severity == 'high' and confidence >= 0.85:
            return True
        
        # Medium severity
        if severity == 'medium' and confidence >= self.AUTO_FIX_THRESHOLD:
            return True
        
        return confidence >= self.AUTO_FIX_THRESHOLD
    
    def select_best_solution(self, solutions: List[Dict]) -> Optional[Dict]:
        """Select best solution based on scoring."""
        if not solutions:
            return None
        
        best = None
        best_score = -1
        
        for solution in solutions:
            confidence = solution.get('confidence', 0)
            
            # Higher confidence wins
            if confidence > best_score:
                best_score = confidence
                best = solution
        
        return best
    
    def make_decision(self, problem: Dict, solutions: List[Dict]) -> Dict:
        """Make decision on what to do with problem."""
        if not solutions:
            return {
                'action': 'research',
                'confidence': 0,
                'message': 'No solutions found - need research',
                'auto_fix': False
            }
        
        best_solution = self.select_best_solution(solutions)
        
        if not best_solution:
            return {
                'action': 'research',
                'confidence': 0,
                'message': 'Could not select solution',
                'auto_fix': False
            }
        
        # Determine action based on confidence
        confidence = best_solution.get('confidence', 0)
        
        if confidence >= self.AUTO_FIX_THRESHOLD:
            action = 'auto_fix'
            message = 'Auto-fix available'
        elif confidence >= self.SUGGEST_FIX_THRESHOLD:
            action = 'suggest'
            message = 'Suggested fix available'
        elif confidence >= self.RESEARCH_THRESHOLD:
            action = 'research'
            message = 'Need more research'
        else:
            action = 'report'
            message = 'Report uncertainty'
        
        decision = {
            'action': action,
            'confidence': confidence,
            'solution': best_solution,
            'auto_fix': self.should_auto_fix(problem, best_solution),
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        self.decision_log.append({
            'problem': problem,
            'decision': decision
        })
        
        return decision
    
    def explain_decision(self, decision: Dict) -> str:
        """Generate human-readable explanation."""
        action = decision.get('action', 'unknown')
        confidence = decision.get('confidence', 0)
        message = decision.get('message', '')
        
        explanation = f"""
Decision: {action.upper()}
Confidence: {confidence:.0%}
{message}
"""
        if decision.get('auto_fix'):
            explanation += "\n→ This will be applied automatically."
        elif action == 'suggest':
            explanation += "\n→ Please confirm to proceed."
        elif action == 'research':
            explanation += "\n→ More research needed."
        else:
            explanation += "\n→ Please review manually."
        
        return explanation
    
    def priority_score(self, problem: Dict, solution: Dict) -> float:
        """Calculate priority score for a problem-solution pair."""
        severity_map = {'critical': 40, 'high': 30, 'medium': 20, 'low': 10}
        
        severity = problem.get('severity', 'low')
        confidence = solution.get('confidence', 0)
        
        # Simple scoring
        severity_score = severity_map.get(severity, 10)
        confidence_score = confidence * 30
        
        impact = problem.get('impact', 1) * 10
        
        return severity_score + confidence_score + impact
    
    def get_statistics(self) -> Dict:
        """Get decision statistics."""
        if not self.decision_log:
            return {
                'total_decisions': 0,
                'auto_fix_rate': 0,
                'avg_confidence': 0
            }
        
        total = len(self.decision_log)
        auto_fixes = sum(1 for d in self.decision_log if d.get('decision', {}).get('auto_fix'))
        avg_conf = sum(d.get('decision', {}).get('confidence', 0) for d in self.decision_log) / total
        
        return {
            'total_decisions': total,
            'auto_fixes': auto_fixes,
            'auto_fix_rate': auto_fixes / total * 100,
            'avg_confidence': avg_conf
        }
    
    def create_plan(self, goal: str, problems: List[Dict], solutions: List[Dict]) -> List[Dict]:
        """Create improvement plan for goal."""
        plan = []
        
        # Match problems to solutions
        for problem in problems:
            problem_id = problem.get('id', 'unknown')
            
            # Find matching solutions
            matching = [s for s in solutions if self.priority_score(problem, s) > 30]
            
            if matching:
                best = self.select_best_solution(matching)
                decision = self.make_decision(problem, matching)
                
                plan.append({
                    'task': f"Fix: {problem.get('description', problem_id)}",
                    'action': decision.get('action'),
                    'solution': best,
                    'priority': self.priority_score(problem, best),
                    'auto_fix': decision.get('auto_fix', False)
                })
        
        # Sort by priority (highest first)
        plan.sort(key=lambda x: x['priority'], reverse=True)
        
        return plan


if __name__ == "__main__":
    engine = DecisionEngine()
    
    # Test with sample problem
    problem = {
        'id': 'test_problem',
        'description': 'cdep.ro returns 404',
        'severity': 'critical',
        'impact': 2
    }
    
    solutions = [
        {'confidence': 0.93, 'description': 'Remove &prn=1 from URL'},
        {'confidence': 0.3, 'description': 'Try alternate source'}
    ]
    
    decision = engine.make_decision(problem, solutions)
    print(engine.explain_decision(decision))
    
    print("\n--- Statistics ---")
    stats = engine.get_statistics()
    print(f"Auto-fix rate: {stats['auto_fix_rate']:.0f}%")