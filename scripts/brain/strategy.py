"""
Strategy Planner Module

Data-driven strategy planning with priority scoring,
dependency analysis, effort estimation, and risk assessment.
"""

import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from memory import MemoryStore


class StrategyPlanner:
    """
    Strategy planning engine with data-driven recommendations.
    
    Features:
    - Priority scoring (0-100 based on severity, impact, confidence)
    - Dependency analysis (safe execution order)
    - Time estimation (based on historical data)
    - Risk assessment (potential pitfalls)
    - Success prediction (confidence scoring)
    """
    
    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path(__file__).parent.parent.parent
        self.memory = MemoryStore(self.project_dir)
        
        # Severity weights
        self.severity_weights = {
            'critical': 40,
            'high': 30,
            'medium': 20,
            'low': 10
        }
        
        # Priority weights for scoring
        self.weights = {
            'severity': 0.35,
            'confidence': 0.25,
            'recency': 0.20,
            'impact': 0.20
        }
    
    def calculate_priority(self, issue: Dict, context: Dict = None) -> Dict:
        """
        Calculate priority score for an issue.
        
        Args:
            issue: Issue dict with description, severity, etc.
            context: Additional context for scoring
            
        Returns:
            Priority dict with score and breakdown
        """
        score = 0
        breakdown = {}
        
        # Severity score (0-40)
        severity = issue.get('severity', 'medium')
        severity_score = self.severity_weights.get(severity, 20)
        score += severity_score
        breakdown['severity'] = severity_score
        
        # Confidence score (0-30) - based on known fix
        confidence_score = 0
        if issue.get('description'):
            patterns = self.memory.procedural.find_patterns(
                issue_desc=issue['description']
            )
            if patterns:
                confidence_score = patterns[0].get('confidence', 0) * 30
                breakdown['confidence'] = confidence_score
                breakdown['known_fix'] = patterns[0].get('fix_pattern')
            else:
                breakdown['confidence'] = 0
                breakdown['known_fix'] = None
        else:
            breakdown['confidence'] = 0
        
        score += confidence_score
        
        # Impact score (0-20) - based on files affected
        files_affected = issue.get('files_affected', [])
        impact_score = min(20, len(files_affected) * 2)
        score += impact_score
        breakdown['impact'] = impact_score
        
        # Recency score (0-10) - based on similar recent issues
        recency_score = 0
        if issue.get('description'):
            similar = self.memory.episodic.get_similar(issue['description'], limit=10)
            if similar:
                recent = [s for s in similar if s.get('timestamp', '') > 
                         (datetime.now() - timedelta(days=7)).isoformat()]
                if recent:
                    recency_score = 10
                elif len(similar) >= 3:
                    recency_score = 5
                else:
                    recency_score = 2
        score += recency_score
        breakdown['recency'] = recency_score
        
        return {
            'score': min(100, max(0, score)),
            'max': 100,
            'breakdown': breakdown,
            'priority_level': self._get_priority_level(score)
        }
    
    def _get_priority_level(self, score: int) -> str:
        """Get priority level from score."""
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'
    
    def analyze_dependencies(self, issues: List[Dict]) -> Dict:
        """
        Analyze dependencies between issues.
        
        Args:
            issues: List of issues to analyze
            
        Returns:
            Dependency graph with safe execution order
        """
        # Build dependency graph
        graph = {}
        order = []
        processed = set()
        
        # Categorize issues
        consolidation = [i for i in issues if 'duplicate' in i.get('description', '').lower()]
        migration = [i for i in issues if 'migration' in i.get('description', '').lower()]
        merge = [i for i in issues if 'merge' in i.get('description', '').lower() or 'entities' in i.get('description', '').lower()]
        cleanup = [i for i in issues if 'empty' in i.get('description', '').lower() or 'delete' in i.get('description', '').lower()]
        
        # Define order: cleanup -> consolidation -> migration -> merge
        dependency_order = [
            ('cleanup', cleanup),
            ('consolidation', consolidation),
            ('migration', migration),
            ('merge', merge)
        ]
        
        for phase_name, phase_issues in dependency_order:
            for issue in phase_issues:
                if issue not in processed:
                    order.append(issue)
                    processed.add(id(issue))
                    graph[phase_name] = phase_issues
        
        return {
            'execution_order': order,
            'phases': [p[0] for p in dependency_order if p[1]],
            'dependencies': graph,
            'can_parallelize': len(order) <= 3
        }
    
    def estimate_effort(self, issue: Dict) -> Dict:
        """
        Estimate effort required for issue.
        
        Args:
            issue: Issue dict
            
        Returns:
            Effort estimation with time breakdown
        """
        description = issue.get('description', '').lower()
        files = issue.get('files_affected', [])
        
        # Base time estimates (in seconds)
        base_times = {
            'merge': 30,
            'entities': 30,
            'migration': 120,
            'duplicate': 300,
            'consolidat': 300,
            'empty': 10,
            'delete': 10,
            'fix': 60,
            'error': 120
        }
        
        base_time = 60  # Default
        for keyword, time in base_times.items():
            if keyword in description:
                base_time = time
                break
        
        # Adjust by file count
        if files:
            base_time += len(files) * 5
        
        # Look up historical data
        similar = self.memory.recall(description, limit=5)
        if similar:
            durations = [s.get('duration_ms', 0) / 1000 for s in similar if s.get('duration_ms')]
            if durations:
                # Use weighted average (60% historical, 40% estimate)
                avg_historical = sum(durations) / len(durations)
                estimated = (avg_historical * 0.6) + (base_time * 0.4)
                base_time = estimated
        
        return {
            'estimated_seconds': base_time,
            'estimated_formatted': self._format_duration(base_time),
            'confidence': 0.8 if similar else 0.5,
            'based_on': 'historical' if similar else 'default'
        }
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration as human-readable string."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"
    
    def assess_risk(self, issue: Dict) -> Dict:
        """
        Evaluate risk for addressing an issue.
        
        Args:
            issue: Issue dict
            
        Returns:
            Risk assessment with level and mitigations
        """
        risks = []
        risk_level = 'low'
        
        # Check for risky patterns
        description = issue.get('description', '').lower()
        
        if 'delete' in description:
            risks.append({
                'type': 'destructive',
                'description': 'Operation may delete data',
                'severity': 'medium',
                'mitigation': 'Ensure backup before execution'
            })
            risk_level = 'medium'
        
        if 'migration' in description:
            risks.append({
                'type': 'data_loss',
                'description': 'Migration may lose data if interrupted',
                'severity': 'high',
                'mitigation': 'Run with checkpointing enabled'
            })
            risk_level = 'high'
        
        if 'merge' in description:
            risks.append({
                'type': 'overwrite',
                'description': 'May overwrite existing data',
                'severity': 'low',
                'mitigation': 'Git provides rollback capability'
            })
        
        # Check historical failure rate
        patterns = self.memory.procedural.find_patterns(issue_desc=description)
        if patterns:
            success_rate = patterns[0].get('success_rate', 1.0)
            if success_rate < 0.7:
                risks.append({
                    'type': 'low_success_rate',
                    'description': f'Only {success_rate:.0%} success rate historically',
                    'severity': 'high',
                    'mitigation': 'Test on small sample first'
                })
                risk_level = 'high'
        
        # Check for side effects
        if patterns and patterns[0].get('side_effects'):
            risks.append({
                'type': 'known_side_effects',
                'description': 'Has caused side effects in past',
                'severity': 'medium',
                'mitigation': 'Review previous side effects'
            })
        
        return {
            'level': risk_level,
            'risks': risks,
            'can_proceed': risk_level != 'high',
            'requires_confirmation': risk_level == 'high'
        }
    
    def generate_plan(self, issues: List[Dict], context: Dict = None) -> Dict:
        """
        Generate prioritized action plan.
        
        Args:
            issues: List of issues to address
            context: Additional context
            
        Returns:
            Strategic plan with prioritized actions
        """
        # Calculate priorities
        scored_issues = []
        for issue in issues:
            priority = self.calculate_priority(issue, context)
            effort = self.estimate_effort(issue)
            risk = self.assess_risk(issue)
            
            # Get known fix from patterns
            patterns = self.memory.procedural.find_patterns(
                issue_desc=issue.get('description', '')
            )
            known_fix = patterns[0].get('fix_pattern') if patterns else None
            
            scored_issues.append({
                'issue': issue,
                'priority': priority,
                'effort': effort,
                'risk': risk,
                'known_fix': known_fix,
                'confidence': patterns[0].get('confidence', 0.5) if patterns else 0.5
            })
        
        # Sort by priority score
        scored_issues.sort(key=lambda x: x['priority']['score'], reverse=True)
        
        # Analyze dependencies
        dependencies = self.analyze_dependencies(issues)
        
        # Build plan
        plan = {
            'total_issues': len(issues),
            'estimated_total_time': sum(s['effort']['estimated_seconds'] for s in scored_issues),
            'highest_risk': max(s['risk']['level'] for s in scored_issues),
            'recommendations': scored_issues,
            'execution_order': dependencies['execution_order'],
            'phases': dependencies['phases'],
            'dependencies': dependencies['dependencies']
        }
        
        # Add best practices from memory
        insights = self.memory.get_insights()
        if insights:
            plan['learned_insights'] = insights
        
        return plan
    
    def get_execution_summary(self, plan: Dict) -> str:
        """
        Generate human-readable execution summary.
        
        Args:
            plan: Plan dict from generate_plan
            
        Returns:
            Markdown-formatted summary
        """
        lines = []
        
        lines.append("## Execution Summary")
        lines.append(f"- **Total Issues:** {plan['total_issues']}")
        lines.append(f"- **Estimated Time:** {self._format_duration(plan['estimated_total_time'])}")
        lines.append(f"- **Risk Level:** {plan['highest_risk']}")
        lines.append("")
        
        lines.append("### Recommended Actions (Priority Order)")
        lines.append("")
        lines.append("| Rank | Issue | Priority | Confidence | Time | Fix |")
        lines.append("|------|-------|----------|-------------|------|-----|")
        
        for i, rec in enumerate(plan['recommendations'], 1):
            issue_desc = rec['issue'].get('description', 'Unknown')[:40]
            priority = rec['priority']['priority_level']
            confidence = f"{rec['confidence']:.0%}"
            time = rec['effort']['estimated_formatted']
            fix = rec['known_fix'] or rec['issue'].get('command', 'N/A')[:30]
            
            lines.append(f"| {i} | {issue_desc} | {priority} | {confidence} | {time} | {fix} |")
        
        if plan.get('phases'):
            lines.append("")
            lines.append("### Execution Phases")
            for phase in plan['phases']:
                lines.append(f"- {phase.title()}")
        
        return "\n".join(lines)