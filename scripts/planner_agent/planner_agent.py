#!/usr/bin/env python3
"""StenoMD Planner Agent - Smart project planning and analysis."""
import sys
import argparse
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from problem_analyzer import ProblemAnalyzer
from solution_researcher import SolutionResearcher
from decision_engine import DecisionEngine
from auto_fixer import AutoFixer
from pattern_miner import PatternMiner
from notifications import NotificationService


class PlannerAgent:
    """Smart Planner Agent for StenoMD project."""
    
    def __init__(self, project_root: str = "/home/adrian/Desktop/NEDAILAB/StenoMD"):
        self.project_root = Path(project_root)
        
        self.analyzer = ProblemAnalyzer(project_root)
        self.researcher = SolutionResearcher(project_root)
        self.decision_engine = DecisionEngine()
        self.auto_fixer = AutoFixer(project_root)
        self.pattern_miner = PatternMiner(project_root)
        self.notifier = NotificationService()
        
    def analyze(self, deep: bool = False) -> str:
        self.notifier.info("Starting project analysis...")
        analysis = self.analyzer.analyze_all()
        
        if deep:
            self.notifier.info("Running deep analysis...")
            suggestions = self.pattern_miner.suggest_improvements()
        
        report = self.analyzer.generate_report()
        
        if deep and suggestions:
            report += "\n## Suggestions\n"
            for s in suggestions:
                report += f"- [{s['priority']}] {s['description']}\n"
        
        return report
    
    def research(self, problem: str) -> str:
        self.notifier.info(f"Researching: {problem}")
        results = self.researcher.research_fix(problem)
        if results['research_complete']:
            # Get confidence from results
            conf = results.get('best_confidence', results.get('found_solutions', 0) / 100)
            return f"Solution found (confidence: {conf:.0%})"
        return "No solution - research required"
    
    def auto_fix(self, keywords: str = "", fix_id: str = "") -> str:
        if fix_id:
            result = self.auto_fixer.apply_fix(fix_id)
        else:
            result = self.auto_fixer.try_auto_fix(keywords)
        return result['message']
    
    def fix_all(self) -> str:
        fixes = self.auto_fixer.list_available_fixes()
        successes = 0
        for f in fixes:
            result = self.auto_fixer.apply_fix(f['id'])
            if result['success']:
                successes += 1
        return f"Applied {successes}/{len(fixes)} fixes"
    
    def plan_goal(self, goal: str) -> str:
        analysis = self.analyzer.analyze_all()
        blockers = analysis.get('blockers', [])
        solutions = self.researcher.get_known_fixes()
        
        problems = [{'id': b['id'], 'description': b['description'], 
                    'severity': b.get('severity', 'medium')} for b in blockers]
        
        plan = self.decision_engine.create_plan(goal, problems, solutions)
        
        output = f"# Plan: {goal}\n\n"
        for i, task in enumerate(plan, 1):
            output += f"{i}. {task['task']} ({task['priority']:.0f})\n"
            output += f"   Auto: {'Yes' if task['auto_fix'] else 'No'}\n\n"
        return output
    
    def health_check(self) -> str:
        health = self.analyzer.calculate_health_score()
        return f"Health: {health['total']}% - {health['status'].upper()}"


def main():
    parser = argparse.ArgumentParser(description="StenoMD Planner Agent")
    parser.add_argument('--analyze', action='store_true', help='Analyze project')
    parser.add_argument('--deep', action='store_true', help='Deep analysis')
    parser.add_argument('--research', type=str, help='Research problem')
    parser.add_argument('--auto-fix', type=str, help='Auto-fix')
    parser.add_argument('--fix-id', type=str, help='Fix by ID')
    parser.add_argument('--fix-all', action='store_true', help='Fix all')
    parser.add_argument('--plan', type=str, help='Plan for goal')
    parser.add_argument('--health', action='store_true', help='Health check')
    parser.add_argument('--project-root', type=str, default='/home/adrian/Desktop/NEDAILAB/StenoMD')
    
    args = parser.parse_args()
    
    agent = PlannerAgent(args.project_root)
    
    if args.health:
        print(agent.health_check())
    elif args.analyze:
        print(agent.analyze(deep=args.deep))
    elif args.research:
        print(agent.research(args.research))
    elif args.auto_fix:
        print(agent.auto_fix(keywords=args.auto_fix))
    elif args.fix_id:
        print(agent.auto_fix(fix_id=args.fix_id))
    elif args.fix_all:
        print(agent.fix_all())
    elif args.plan:
        print(agent.plan_goal(args.plan))
    else:
        print("StenoMD Planner Agent")
        print("Options: --health, --analyze, --research, --fix-all, --plan")


if __name__ == "__main__":
    main()