"""
Cortex - Main Orchestration Module

Coordinates all brain modules to provide unified intelligence.
This is the main interface for the Master Strategist.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from .vision import VisionEngine
from .strategy import StrategyPlanner
from .analytics import AnalyticsEngine
from .debugger import DebuggingEngine


class Thought:
    """Represents a complete thought process result."""
    
    def __init__(self, analysis: Dict, strategy: Dict, patterns: List, confidence: float):
        self.analysis = analysis
        self.strategy = strategy
        self.patterns = patterns
        self.confidence = confidence
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            'analysis': self.analysis,
            'strategy': self.strategy,
            'patterns': self.patterns,
            'confidence': self.confidence,
            'timestamp': self.timestamp
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)


class Cortex:
    """
    Main orchestration engine - the "brain" of the Master Strategist.
    
    Coordinates:
    - Vision: Pattern recognition
    - Strategy: Planning and prioritization
    - Analytics: Metrics and health
    - Debugger: Debug assistance
    
    Provides unified interface for intelligent decision-making.
    """
    
    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path(__file__).parent.parent.parent
        
        # Initialize all brain modules
        self.vision = VisionEngine(self.project_dir)
        self.strategy = StrategyPlanner(self.project_dir)
        self.analytics = AnalyticsEngine(self.project_dir)
        self.debugger = DebuggingEngine(self.project_dir)
        
        # Memory store (shared reference)
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from memory import MemoryStore
        self.memory = MemoryStore(self.project_dir)
    
    def think(self, context: Dict) -> Thought:
        """
        Main thinking process - analyze and generate response.
        
        Args:
            context: Context dictionary with:
                - issues: List of issues to address
                - mode: 'diagnose', 'plan', 'debug', 'full'
                - query: Optional search query
                - error: Optional error to debug
                
        Returns:
            Thought object with complete analysis
        """
        mode = context.get('mode', 'full')
        
        if mode == 'debug' and context.get('error'):
            return self._think_debug(context)
        elif mode == 'plan':
            return self._think_plan(context)
        elif mode == 'diagnose':
            return self._think_diagnose(context)
        else:
            return self._think_full(context)
    
    def _think_debug(self, context: Dict) -> Thought:
        """Think about debugging."""
        error = context.get('error')
        
        debug_report = self.debugger.debug(error)
        
        # Learn from this debug session
        if context.get('fix_worked') is not None:
            self.debugger.learn_from_debug(
                error,
                context['fix_worked'],
                context.get('fix_command')
            )
        
        analysis = {
            'mode': 'debug',
            'error_type': debug_report['analysis'].get('type'),
            'root_cause': debug_report['root_cause'].get('primary_cause')
        }
        
        strategy = {
            'solutions': debug_report['solutions'],
            'guide': debug_report['guide']
        }
        
        return Thought(
            analysis=analysis,
            strategy=strategy,
            patterns=[],
            confidence=debug_report['root_cause'].get('confidence', 0.5)
        )
    
    def _think_plan(self, context: Dict) -> Thought:
        """Think about planning."""
        issues = context.get('issues', [])
        
        # Generate strategic plan
        plan = self.strategy.generate_plan(issues, context)
        
        # Find patterns for each issue
        patterns = []
        for issue in issues:
            desc = issue.get('description', '')
            if desc:
                found = self.memory.procedural.find_patterns(issue_desc=desc)
                patterns.extend(found[:3])
        
        # Calculate confidence
        if patterns:
            confidence = sum(p.get('confidence', 0) for p in patterns) / len(patterns)
        else:
            confidence = 0.5
        
        analysis = {
            'mode': 'plan',
            'issue_count': len(issues),
            'phases': plan.get('phases', [])
        }
        
        return Thought(
            analysis=analysis,
            strategy=plan,
            patterns=patterns,
            confidence=confidence
        )
    
    def _think_diagnose(self, context: Dict) -> Thought:
        """Think about diagnosing issues."""
        # Get health analysis
        health = self.analytics.calculate_health_score()
        metrics = self.analytics.get_comprehensive_metrics()
        
        # Detect anomalies
        anomalies = self.vision.detect_anomalies(metrics)
        
        analysis = {
            'mode': 'diagnose',
            'health_score': health['score'],
            'health_grade': health['grade'],
            'anomalies': anomalies,
            'issues_found': len(anomalies)
        }
        
        # Generate recommendations
        recommendations = self.analytics.generate_recommendations()
        
        strategy = {
            'health': health,
            'recommendations': recommendations
        }
        
        return Thought(
            analysis=analysis,
            strategy=strategy,
            patterns=[],
            confidence=health['score'] / 100
        )
    
    def _think_full(self, context: Dict) -> Thought:
        """Full thinking process - all modules active."""
        issues = context.get('issues', [])
        
        # Step 1: Analyze current state
        health = self.analytics.calculate_health_score()
        metrics = self.analytics.get_comprehensive_metrics()
        anomalies = self.vision.detect_anomalies(metrics)
        
        # Step 2: Generate strategy
        if issues:
            plan = self.strategy.generate_plan(issues, context)
        else:
            plan = self.strategy.generate_plan(
                [{'description': a.get('description'), 'severity': 'medium'} 
                 for a in anomalies] if anomalies else [],
                context
            )
        
        # Step 3: Find patterns
        patterns = self.vision.find_patterns(
            self.memory.episodic.get_recent(limit=50)
        )
        
        # Step 4: Generate recommendations
        recommendations = self.analytics.generate_recommendations()
        
        # Calculate confidence
        confidence = (
            health['score'] / 100 * 0.4 +
            (plan.get('recommendations', [{}])[0].get('confidence', 0.5) if plan.get('recommendations') else 0.5) * 0.4 +
            len(patterns) / 100 * 0.2
        )
        
        analysis = {
            'mode': 'full',
            'health_score': health['score'],
            'health_grade': health['grade'],
            'issues_found': len(anomalies),
            'patterns_found': len(patterns),
            'recommendations_count': len(recommendations)
        }
        
        strategy = {
            'plan': plan,
            'health': health,
            'recommendations': recommendations
        }
        
        return Thought(
            analysis=analysis,
            strategy=strategy,
            patterns=patterns,
            confidence=min(1.0, confidence)
        )
    
    def generate_report(self, thought: Thought, format: str = 'markdown') -> str:
        """
        Generate formatted report from thought.
        
        Args:
            thought: Thought object
            format: 'markdown', 'json', or 'console'
            
        Returns:
            Formatted report string
        """
        if format == 'json':
            return thought.to_json()
        
        elif format == 'console':
            return self._format_console(thought)
        
        else:  # markdown
            return self._format_markdown(thought)
    
    def _format_console(self, thought: Thought) -> str:
        """Format thought for console output."""
        lines = []
        
        lines.append("┌" + "─" * 63 + "┐")
        lines.append("│" + " 🧠 STENOMD MASTER STRATEGIST v2.0".ljust(63) + "│")
        
        confidence_pct = thought.confidence * 100
        mode = thought.analysis.get('mode', 'full')
        lines.append("│" + f" Mode: {mode.title()} | Confidence: {confidence_pct:.0f}%".ljust(63) + "│")
        lines.append("├" + "─" * 63 + "┤")
        
        # Health info
        if 'health_score' in thought.analysis:
            score = thought.analysis['health_score']
            grade = thought.analysis.get('health_grade', 'N/A')
            issues = thought.analysis.get('issues_found', 0)
            patterns = thought.analysis.get('patterns_found', 0)
            lines.append("│" + f" 📊 Health: {score:.0f}/100 ({grade})  Issues: {issues}  Patterns: {patterns}".ljust(63) + "│")
        
        lines.append("├" + "─" * 63 + "┤")
        lines.append("│" + " 🎯 RECOMMENDATIONS".ljust(63) + "│")
        lines.append("│" + " " + "─" * 61 + " │")
        
        # Top recommendations
        recommendations = thought.strategy.get('recommendations', thought.strategy.get('plan', {}).get('recommendations', []))
        for i, rec in enumerate(recommendations[:5], 1):
            if isinstance(rec, dict):
                desc = rec.get('issue', {}).get('description', 'Unknown')[:30]
                priority = rec.get('priority', {}).get('priority_level', 'medium')
                conf = rec.get('confidence', 0.5) * 100
                lines.append("│" + f" {i}. [{priority.upper()[:4]:>4}] {desc}".ljust(63) + "│")
                lines.append("│" + f"    ⭐{conf:.0f}%  {rec.get('known_fix', 'N/A')[:45]}".ljust(63) + "│")
        
        lines.append("├" + "─" * 63 + "┤")
        lines.append("│" + " 📈 INSIGHTS".ljust(63) + "│")
        lines.append("│" + " " + "─" * 61 + " │")
        
        # Insights
        if thought.patterns:
            top_pattern = thought.patterns[0]
            lines.append("│" + f" • Best fix: {top_pattern.get('fix', 'N/A')[:50]}".ljust(63) + "│")
            lines.append("│" + f"   Success rate: {top_pattern.get('confidence', 0) * 100:.0f}%".ljust(63) + "│")
        
        lines.append("└" + "─" * 63 + "┘")
        
        return "\n".join(lines)
    
    def _format_markdown(self, thought: Thought) -> str:
        """Format thought as markdown."""
        lines = []
        
        confidence_pct = thought.confidence * 100
        
        lines.append("# StenoMD Master Strategist Report")
        lines.append(f"**Generated:** {thought.timestamp}")
        lines.append(f"**Mode:** {thought.analysis.get('mode', 'full').title()}")
        lines.append(f"**Confidence:** {confidence_pct:.0f}%")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        if 'health_score' in thought.analysis:
            lines.append(f"| Metric | Value |")
            lines.append(f"|--------|-------|")
            lines.append(f"| Health Score | {thought.analysis['health_score']:.0f}/100 ({thought.analysis.get('health_grade', 'N/A')}) |")
            lines.append(f"| Issues Found | {thought.analysis.get('issues_found', 0)} |")
            lines.append(f"| Patterns Learned | {thought.analysis.get('patterns_found', 0)} |")
        
        lines.append("")
        
        # Strategic Recommendations
        lines.append("## Strategic Recommendations")
        lines.append("")
        
        recommendations = thought.strategy.get('recommendations', thought.strategy.get('plan', {}).get('recommendations', []))
        if recommendations:
            lines.append("| Rank | Issue | Priority | Confidence | Estimated Time |")
            lines.append("|------|-------|----------|-------------|----------------|")
            
            for i, rec in enumerate(recommendations[:5], 1):
                if isinstance(rec, dict):
                    desc = rec.get('issue', {}).get('description', 'Unknown')[:40]
                    priority = rec.get('priority', {}).get('priority_level', 'medium')
                    conf = rec.get('confidence', 0.5) * 100
                    time = rec.get('effort', {}).get('estimated_formatted', 'N/A')
                    lines.append(f"| {i} | {desc} | {priority} | {conf:.0f}% | {time} |")
        
        lines.append("")
        
        # Patterns Learned
        if thought.patterns:
            lines.append("## Patterns Learned")
            lines.append("")
            for pattern in thought.patterns[:5]:
                lines.append(f"- **{pattern.get('issue', 'Unknown')}** → {pattern.get('fix', 'N/A')}")
                lines.append(f"  - Success Rate: {pattern.get('confidence', 0) * 100:.0f}%")
                lines.append(f"  - Times Used: {pattern.get('times_used', 0)}")
        
        lines.append("")
        lines.append("---")
        lines.append("*Generated by StenoMD Master Strategist v2.0*")
        
        return "\n".join(lines)
    
    def learn(self, action: Dict, outcome: Dict):
        """
        Learn from an action and its outcome.
        
        Args:
            action: Action details
            outcome: Outcome details
        """
        self.memory.learn(action, outcome)
    
    def get_memory_stats(self) -> Dict:
        """Get memory statistics."""
        return self.memory.get_stats()
    
    def get_health_check(self) -> Dict:
        """Get quick health check."""
        return self.analytics.calculate_health_score()


def create_cortex(project_dir: str = None) -> Cortex:
    """Factory function to create Cortex instance."""
    return Cortex(Path(project_dir) if project_dir else None)