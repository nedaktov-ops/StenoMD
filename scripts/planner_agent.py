#!/usr/bin/env python3
"""
StenoMD Master Strategist Agent v2.0

An intelligent, self-learning agent with full cognitive capabilities:
- Memory: Perfect recall of all past actions and outcomes
- Vision: Pattern recognition across entire project history
- Strategy: Data-driven decision making based on experience
- Execution: Actionable, prioritized recommendations
- Analytics: Real-time project health diagnostics
- Debugging: Intelligent root cause analysis

Modes:
    --auto     : Run after each action (post-hook), learns from outcome
    --manual   : Run on-demand with full analysis
    --schedule : Run daily health check
    --deep     : Comprehensive analysis (slower, more thorough)
    --debug    : Debug assistance mode
    --learn    : Record a learning instance
    --recall   : Recall similar past experiences
    --health   : Quick health check

Usage:
    python3 scripts/planner_agent.py --manual
    python3 scripts/planner_agent.py --auto
    python3 scripts/planner_agent.py --health
    python3 scripts/planner_agent.py --recall "entities.json empty"
"""

import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add project paths
PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
sys.path.insert(0, str(PROJECT_DIR / "scripts"))

# Import brain modules
from brain import Cortex, VisionEngine, StrategyPlanner, AnalyticsEngine, DebuggingEngine
from memory import MemoryStore


class MasterStrategist:
    """
    Ultimate Planner Agent combining all cognitive capabilities.
    
    This is the main interface for the Master Strategist system.
    """
    
    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or PROJECT_DIR
        self.project_dir = Path(self.project_dir)
        
        # Initialize all modules
        self.cortex = Cortex(self.project_dir)
        self.memory = self.cortex.memory
        self.vision = self.cortex.vision
        self.strategy = self.cortex.strategy
        self.analytics = self.cortex.analytics
        self.debugger = self.cortex.debugger
        
        # Strategy file for output
        self.strategy_file = self.project_dir / "STRATEGY.md"
    
    def run(self, mode: str, context: Dict = None) -> Dict:
        """
        Main entry point for all agent operations.
        
        Args:
            mode: Operation mode (auto, manual, schedule, deep, debug, learn, recall, health)
            context: Optional context dictionary
            
        Returns:
            Result dictionary
        """
        context = context or {}
        context['mode'] = mode
        
        if mode == "auto":
            return self._run_auto(context)
        elif mode == "manual":
            return self._run_manual(context)
        elif mode == "schedule":
            return self._run_scheduled(context)
        elif mode == "deep":
            return self._run_deep(context)
        elif mode == "debug":
            return self._run_debug(context)
        elif mode == "learn":
            return self._run_learn(context)
        elif mode == "recall":
            return self._run_recall(context)
        elif mode == "health":
            return self._run_health(context)
        elif mode == "stats":
            return self._run_stats(context)
        else:
            return self._run_default(context)
    
    def _run_auto(self, context: Dict) -> Dict:
        """Auto mode: Run after each action, learn from outcome."""
        print("[STRATEGIST] Running in AUTO mode (learning from outcome)...")
        
        # Get action and outcome from context
        action = context.get('action')
        outcome = context.get('outcome')
        
        if action and outcome:
            # Learn from this action
            self.cortex.learn(action, outcome)
            print(f"[STRATEGIST] Learned from action: {action.get('type', 'unknown')}")
            print(f"[STRATEGIST] Outcome: {'SUCCESS' if outcome.get('success') else 'FAILURE'}")
            
            # Check for similar past issues
            if not outcome.get('success'):
                similar = self.memory.suggest({
                    'issue': {'description': action.get('issue', {}).get('description', '')}
                })
                if similar:
                    print("[STRATEGIST] Similar successful fixes found:")
                    for s in similar[:3]:
                        print(f"  - {s.get('fix', 'Unknown')} ({s.get('confidence', 0)*100:.0f}% confidence)")
        
        # Quick health check
        health = self.analytics.calculate_health_score()
        print(f"[STRATEGIST] Health Score: {health['score']:.0f}/100 ({health['grade']})")
        
        if health['score'] < 70:
            print("[STRATEGIST] Warning: Health score below 70, recommendations available")
            return {'mode': 'auto', 'health': health, 'needs_attention': True}
        
        return {'mode': 'auto', 'health': health, 'needs_attention': False}
    
    def _run_manual(self, context: Dict) -> Dict:
        """Manual mode: Full analysis with recommendations."""
        print("[STRATEGIST] Running in MANUAL mode (full analysis)...")
        print()
        
        # Run full thinking process
        thought = self.cortex.think({
            'mode': 'full',
            'context': context
        })
        
        # Generate and display report
        report = self.cortex.generate_report(thought, format='console')
        print(report)
        print()
        
        # Write to strategy file
        self._write_strategy(thought)
        
        return {
            'mode': 'manual',
            'thought': thought.to_dict(),
            'confidence': thought.confidence
        }
    
    def _run_scheduled(self, context: Dict) -> Dict:
        """Scheduled mode: Daily health check."""
        print(f"[STRATEGIST] Running in SCHEDULED mode (daily check: {datetime.now().strftime('%Y-%m-%d %H:%M')})")
        
        # Get health
        health = self.analytics.calculate_health_score()
        
        # Generate recommendations
        recommendations = self.analytics.generate_recommendations()
        
        # Get trends
        trends = self.vision.generate_trends(days=7)
        
        # Get memory stats
        mem_stats = self.memory.get_stats()
        
        print()
        print(f"Health Score: {health['score']:.0f}/100 ({health['grade']})")
        print(f"Issues Found: {health['breakdown']}")
        print(f"Memory: {mem_stats['episodic_count']} actions, {mem_stats['patterns_count']} patterns")
        print(f"Trends: {trends}")
        
        if recommendations:
            print()
            print("Top Recommendations:")
            for rec in recommendations[:3]:
                print(f"  - [{rec.get('priority', 'medium').upper()}] {rec.get('recommendation', 'Unknown')}")
        
        return {
            'mode': 'schedule',
            'health': health,
            'recommendations': recommendations,
            'trends': trends,
            'memory_stats': mem_stats
        }
    
    def _run_deep(self, context: Dict) -> Dict:
        """Deep mode: Comprehensive analysis."""
        print("[STRATEGIST] Running in DEEP mode (comprehensive analysis)...")
        print()
        
        # Get comprehensive metrics
        metrics = self.analytics.get_comprehensive_metrics()
        
        # Generate health report
        health_report = self.analytics.generate_health_report()
        
        # Get all patterns
        all_patterns = self.memory.procedural.get_effectiveness()
        
        # Get insights
        insights = self.memory.get_insights()
        
        # Generate trends
        trends = self.vision.generate_trends(days=14)
        
        print("=" * 60)
        print("COMPREHENSIVE ANALYSIS REPORT")
        print("=" * 60)
        print()
        print(health_report)
        print()
        print("=" * 60)
        print("LEARNED PATTERNS")
        print("=" * 60)
        print()
        print(insights)
        print()
        print("=" * 60)
        print("TRENDS (14 DAYS)")
        print("=" * 60)
        print(json.dumps(trends, indent=2, default=str))
        
        # Generate markdown report
        report = f"""# StenoMD Deep Analysis Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Mode:** Deep Analysis

## Health Report
{health_report}

## Pattern Effectiveness
- Total Patterns: {all_patterns.get('total_patterns', 0)}
- Average Success Rate: {all_patterns.get('avg_success_rate', 0)*100:.0f}%
- Top Fix: {all_patterns.get('top_fix', {}).get('fix_pattern', 'N/A')}

## Insights
{insights}

## Trends (14 Days)
{json.dumps(trends, indent=2, default=str)}

---
*Generated by StenoMD Master Strategist v2.0*
"""
        
        self._write_strategy_report(report)
        
        return {
            'mode': 'deep',
            'metrics': metrics,
            'health_report': health_report,
            'patterns': all_patterns,
            'insights': insights,
            'trends': trends
        }
    
    def _run_debug(self, context: Dict) -> Dict:
        """Debug mode: Debugging assistance."""
        error = context.get('error')
        
        if not error:
            print("[STRATEGIST] Debug mode requires --error parameter")
            return {'mode': 'debug', 'error': 'No error provided'}
        
        print(f"[STRATEGIST] Running in DEBUG mode...")
        print()
        
        # Run debugging
        debug_report = self.debugger.debug(error)
        
        # Format and display
        report = self.debugger.format_debug_report(debug_report)
        print(report)
        
        # Learn from this debug session
        if context.get('fix_worked') is not None:
            self.debugger.learn_from_debug(
                error,
                context['fix_worked'],
                context.get('fix_command')
            )
        
        return {
            'mode': 'debug',
            'report': debug_report,
            'root_cause': debug_report['root_cause']
        }
    
    def _run_learn(self, context: Dict) -> Dict:
        """Learn mode: Record a learning instance."""
        action = context.get('action', {})
        outcome = context.get('outcome', {})
        
        if not action:
            print("[STRATEGIST] Learn mode requires --action parameter")
            return {'mode': 'learn', 'error': 'No action provided'}
        
        print("[STRATEGIST] Learning from action...")
        
        # Store in memory
        action_id = self.memory.learn(action, outcome)
        
        print(f"[STRATEGIST] Learned: {action.get('type', 'unknown')}")
        print(f"[STRATEGIST] Result: {'SUCCESS' if outcome.get('success') else 'FAILURE'}")
        print(f"[STRATEGIST] Stored with ID: {action_id}")
        
        # Get suggestions for similar issues
        suggestions = self.memory.suggest({
            'issue': {'description': action.get('issue', {}).get('description', '')}
        })
        
        if suggestions:
            print()
            print("Related suggestions:")
            for s in suggestions[:3]:
                print(f"  - {s.get('fix', 'Unknown')} ({s.get('confidence', 0)*100:.0f}%)")
        
        return {
            'mode': 'learn',
            'action_id': action_id,
            'success': outcome.get('success', False)
        }
    
    def _run_recall(self, context: Dict) -> Dict:
        """Recall mode: Find similar past experiences."""
        query = context.get('query', '')
        
        if not query:
            print("[STRATEGIST] Recall mode requires --query parameter")
            return {'mode': 'recall', 'error': 'No query provided'}
        
        print(f"[STRATEGIST] Searching for: '{query}'")
        print()
        
        # Recall from memory
        results = self.memory.recall(query, limit=10)
        
        if not results:
            print("No similar experiences found.")
            return {'mode': 'recall', 'query': query, 'results': []}
        
        print(f"Found {len(results)} similar experiences:")
        print()
        
        for i, result in enumerate(results[:5], 1):
            success = "✅" if result.get('success') else "❌"
            cmd = result.get('command', 'N/A')[:50]
            desc = result.get('description', 'N/A')[:60]
            print(f"{i}. {success} {desc}")
            print(f"   Command: {cmd}")
            print(f"   Time: {result.get('timestamp', 'Unknown')}")
            print()
        
        return {
            'mode': 'recall',
            'query': query,
            'results': results
        }
    
    def _run_health(self, context: Dict) -> Dict:
        """Health mode: Quick health check."""
        print("[STRATEGIST] Running HEALTH check...")
        print()
        
        health = self.analytics.calculate_health_score()
        
        print(f"Overall Score: {health['score']:.0f}/100 ({health['grade']})")
        print()
        print("Component Scores:")
        for component, score in health['breakdown'].items():
            bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
            print(f"  {component.title():20} {bar} {score:.0f}")
        
        return {
            'mode': 'health',
            'health': health
        }
    
    def _run_stats(self, context: Dict) -> Dict:
        """Stats mode: Show memory statistics."""
        print("[STRATEGIST] Memory Statistics")
        print()
        
        stats = self.memory.get_stats()
        print(f"Episodic Memory: {stats['episodic_count']} actions")
        print(f"Procedural Memory: {stats['patterns_count']} patterns")
        print(f"Semantic Memory: {stats['knowledge_count']} entries")
        print(f"Cache: {stats['cache_size']} items ({stats['cache_hit_rate']:.1f}% hit rate)")
        print()
        
        effectiveness = self.memory.analyze_effectiveness()
        print("Pattern Effectiveness:")
        print(f"  Total Patterns: {effectiveness.get('total_patterns', 0)}")
        print(f"  Avg Success Rate: {effectiveness.get('avg_success_rate', 0)*100:.0f}%")
        print(f"  Avg Uses: {effectiveness.get('avg_uses', 0):.1f}")
        
        if effectiveness.get('top_fix'):
            print(f"  Best Fix: {effectiveness['top_fix'].get('fix_pattern', 'N/A')}")
        
        return {
            'mode': 'stats',
            'stats': stats,
            'effectiveness': effectiveness
        }
    
    def _run_default(self, context: Dict) -> Dict:
        """Default mode: Basic information."""
        print("StenoMD Master Strategist v2.0")
        print()
        print("Available modes:")
        print("  --auto     : Learn from action outcomes (post-hook)")
        print("  --manual   : Full analysis with recommendations")
        print("  --schedule : Daily health check")
        print("  --deep     : Comprehensive analysis")
        print("  --debug    : Debugging assistance")
        print("  --learn    : Record a learning instance")
        print("  --recall   : Recall similar past experiences")
        print("  --health   : Quick health check")
        print("  --stats    : Show memory statistics")
        print()
        print("Run with --help for more options")
        
        return {'mode': 'default'}
    
    def _write_strategy(self, thought) -> str:
        """Write strategy to STRATEGY.md file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        content = f"""# StenoMD Strategy - Auto-generated by Master Strategist
**Generated:** {timestamp}
**Mode:** {thought.analysis.get('mode', 'manual')}
**Confidence:** {thought.confidence * 100:.0f}%

---

## Health Score
{thought.strategy.get('health', {}).get('score', 'N/A')}/100 ({thought.strategy.get('health', {}).get('grade', 'N/A')})

## Strategic Recommendations

"""
        
        recommendations = thought.strategy.get('recommendations', [])
        for i, rec in enumerate(recommendations[:10], 1):
            if isinstance(rec, dict):
                desc = rec.get('issue', {}).get('description', 'Unknown')
                priority = rec.get('priority', {}).get('priority_level', 'medium')
                conf = rec.get('confidence', 0.5) * 100
                time = rec.get('effort', {}).get('estimated_formatted', 'N/A')
                fix = rec.get('known_fix', 'N/A')
                content += f"{i}. **[{priority.upper()}]** {desc}\n"
                content += f"   - Confidence: {conf:.0f}% | Time: {time} | Fix: {fix}\n\n"
        
        if thought.patterns:
            content += "\n## Learned Patterns\n\n"
            for p in thought.patterns[:5]:
                content += f"- {p.get('issue', 'Unknown')} → {p.get('fix', 'N/A')} ({p.get('confidence', 0)*100:.0f}%)\n"
        
        content += "\n---\n*Auto-generated by Master Strategist*\n"
        
        # Read existing
        existing = self.strategy_file.read_text() if self.strategy_file.exists() else ""
        # Remove old auto-generated section
        if "<!-- AUTO-GENERATED -->" in existing:
            existing = existing.split("<!-- AUTO-GENERATED -->")[0]
        
        # Prepend new content
        self.strategy_file.write_text(content + "\n\n<!-- AUTO-GENERATED -->\n\n" + existing)
        print(f"[STRATEGIST] Strategy written to {self.strategy_file}")
        
        return str(self.strategy_file)
    
    def _write_strategy_report(self, report: str):
        """Write comprehensive report to strategy file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        existing = self.strategy_file.read_text() if self.strategy_file.exists() else ""
        if "<!-- DEEP ANALYSIS -->" in existing:
            existing = existing.split("<!-- DEEP ANALYSIS -->")[0]
        
        self.strategy_file.write_text(report + "\n\n<!-- DEEP ANALYSIS -->\n\n" + existing)
        print(f"[STRATEGIST] Deep analysis written to {self.strategy_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="StenoMD Master Strategist Agent v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/planner_agent.py --manual
  python3 scripts/planner_agent.py --auto --action '{"type":"fix","command":"python3 scripts/merge.py"}'
  python3 scripts/planner_agent.py --recall --query "entities.json empty"
  python3 scripts/planner_agent.py --debug --error "ModuleNotFoundError: No module named 'bs4'"
  python3 scripts/planner_agent.py --health
        """
    )
    
    # Mode arguments
    parser.add_argument("--auto", action="store_true", help="Run as post-action hook (learn from outcome)")
    parser.add_argument("--manual", action="store_true", help="Full analysis with recommendations")
    parser.add_argument("--schedule", action="store_true", help="Daily scheduled health check")
    parser.add_argument("--deep", action="store_true", help="Comprehensive deep analysis")
    parser.add_argument("--debug", action="store_true", help="Debugging assistance mode")
    parser.add_argument("--learn", action="store_true", help="Record a learning instance")
    parser.add_argument("--recall", action="store_true", help="Recall similar past experiences")
    parser.add_argument("--health", action="store_true", help="Quick health check")
    parser.add_argument("--stats", action="store_true", help="Show memory statistics")
    
    # Context arguments
    parser.add_argument("--action", type=str, help="Action JSON for learning")
    parser.add_argument("--outcome", type=str, help="Outcome JSON for learning")
    parser.add_argument("--query", type=str, help="Search query for recall")
    parser.add_argument("--error", type=str, help="Error to debug")
    parser.add_argument("--fix-worked", type=bool, help="Whether fix worked")
    parser.add_argument("--fix-command", type=str, help="Command used to fix")
    
    # Output arguments
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--quiet", action="store_true", help="Suppress console output")
    
    args = parser.parse_args()
    
    # Parse mode
    mode = "default"
    if args.auto:
        mode = "auto"
    elif args.manual:
        mode = "manual"
    elif args.schedule:
        mode = "schedule"
    elif args.deep:
        mode = "deep"
    elif args.debug:
        mode = "debug"
    elif args.learn:
        mode = "learn"
    elif args.recall:
        mode = "recall"
    elif args.health:
        mode = "health"
    elif args.stats:
        mode = "stats"
    
    # Build context
    context = {}
    
    if args.action:
        try:
            context['action'] = json.loads(args.action)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --action")
            sys.exit(1)
    
    if args.outcome:
        try:
            context['outcome'] = json.loads(args.outcome)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --outcome")
            sys.exit(1)
    
    if args.query:
        context['query'] = args.query
    
    if args.error:
        context['error'] = args.error
    
    if args.fix_worked is not None:
        context['fix_worked'] = args.fix_worked
    
    if args.fix_command:
        context['fix_command'] = args.fix_command
    
    # Run strategist
    strategist = MasterStrategist()
    result = strategist.run(mode, context)
    
    # Output
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    
    return result


if __name__ == "__main__":
    main()