#!/usr/bin/env python3
"""StenoMD Planner Agent - Smart project planning and analysis."""

import sys
import argparse
from pathlib import Path

# Add scripts to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(scripts_dir.parent))

from planner_agent.problem_analyzer import ProblemAnalyzer
from planner_agent.solution_researcher import SolutionResearcher
from planner_agent.decision_engine import DecisionEngine
from planner_agent.auto_fixer import AutoFixer
from planner_agent.pattern_miner import PatternMiner
from planner_agent.notifications import NotificationService
from task_manager import TaskManager


class PlannerAgent:
    """Smart Planner Agent for StenoMD project."""
    
    def __init__(self, project_root: str = "/home/adrian/Desktop/NEDAILAB/StenoMD"):
        self.project_root = Path(project_root)
        
        # Initialize components
        self.analyzer = ProblemAnalyzer(project_root)
        self.researcher = SolutionResearcher(project_root)
        self.decision_engine = DecisionEngine()
        self.auto_fixer = AutoFixer(project_root)
        self.pattern_miner = PatternMiner(project_root)
        self.notifier = NotificationService()
        self.task_manager = TaskManager(project_root)
        
    def check_tasks(self) -> str:
        """Check pending tasks and return report."""
        return self.task_manager.generate_startup_report()
    
    def analyze(self, deep: bool = False) -> str:
        """Analyze project state."""
        self.notifier.info("Starting project analysis...")
        
        analysis = self.analyzer.analyze_all()
        
        if deep:
            self.notifier.info("Running deep analysis...")
            patterns = self.pattern_miner.mine_data_patterns()
            suggestions = self.pattern_miner.suggest_improvements()
        
        report = self.analyzer.generate_report()
        
        if deep and suggestions:
            report += "\n## Suggestions\n"
            for s in suggestions:
                report += f"- [{s['priority']}] {s['description']}\n"
        
        return report
    
    def research(self, problem: str) -> str:
        """Research solution for problem."""
        self.notifier.info(f"Researching solution for: {problem}")
        
        results = self.researcher.research_fix(problem)
        
        if results['research_complete']:
            solution = results['recommended']
            self.notifier.info(f"Found solution (confidence: {solution['confidence'] if solution else 0:.0%})")
            return f"Solution: {solution['description'] if solution else 'None found'}"
        else:
            self.notifier.warning("No solution found in existing knowledge")
            return "Research required - no known solution"
    
    def auto_fix(self, problem_keywords: str = "", fix_id: str = "") -> str:
        """Apply auto-fix."""
        if fix_id:
            result = self.auto_fixer.apply_fix(fix_id)
        else:
            result = self.auto_fixer.try_auto_fix(problem_keywords)
        
        if result['success']:
            self.notifier.info(f"Auto-fix applied: {result['message']}")
        else:
            self.notifier.error(f"Auto-fix failed: {result['message']}")
        
        return result['message']
    
    def fix_all_known(self) -> str:
        """Fix all known issues automatically."""
        self.notifier.info("Checking for known issues...")
        
        fixes = self.auto_fixer.list_available_fixes()
        results = []
        
        for fix in fixes:
            result = self.auto_fixer.apply_fix(fix['id'])
            results.append(result)
        
        successes = sum(1 for r in results if r['success'])
        return f"Applied {successes}/{len(fixes)} fixes"
    
    def plan_goal(self, goal: str) -> str:
        """Create improvement plan for goal."""
        self.notifier.info(f"Creating plan for goal: {goal}")
        
        analysis = self.analyzer.analyze_all()
        blockers = analysis.get('blockers', [])
        
        solutions = self.researcher.get_known_fixes()
        
        problems = [{'id': b['id'], 'description': b['description'], 
                   'severity': b.get('severity', 'medium')} for b in blockers]
        
        plan = self.decision_engine.create_plan(goal, problems, solutions)
        
        output = f"# Improvement Plan: {goal}\n\n"
        for i, task in enumerate(plan, 1):
            output += f"{i}. [{task['priority']:.0f}] {task['task']}\n"
            output += f"   Action: {task['action']}\n"
            output += f"   Auto-fix: {'Yes' if task['auto_fix'] else 'No'}\n\n"
        
        return output
    
    def health_check(self) -> str:
        """Quick health check."""
        health = self.analyzer.calculate_health_score()
        
        output = f"""
# StenoMD Health Check

Overall: {health['total']}% - {health['status'].upper()}

Data Coverage: {health['components']['data_coverage']:.1f}%
Data Integrity: {health['components']['data_integrity']:.1f}%  
Error Free: {health['components']['error_free']:.1f}%
"""
        return output
    
    def learn(self, problem: str, solution: str, success: bool, details: str = "") -> str:
        """Learn from outcome."""
        self.notifier.info(f"Learning: {problem} -> {solution} = {success}")
        return "Learned successfully"


def main():
    parser = argparse.ArgumentParser(description="StenoMD Planner Agent")
    parser.add_argument('--analyze', action='store_true', help='Analyze project state')
    parser.add_argument('--deep', action='store_true', help='Deep analysis (includes patterns)')
    parser.add_argument('--research', type=str, help='Research solution for problem')
    parser.add_argument('--auto-fix', type=str, help='Apply auto-fix for keyword')
    parser.add_argument('--fix-id', type=str, help='Apply specific fix by ID')
    parser.add_argument('--fix-all', action='store_true', help='Fix all known issues')
    parser.add_argument('--plan', type=str, help='Create improvement plan for goal')
    parser.add_argument('--health', action='store_true', help='Quick health check')
    parser.add_argument('--tasks', action='store_true', help='Check pending tasks')
    parser.add_argument('--learn', nargs=4, metavar=('PROBLEM', 'SOLUTION', 'SUCCESS', 'DETAILS'), help='Learn from outcome')
    parser.add_argument('--project-root', type=str, default='/home/adrian/Desktop/NEDAILAB/StenoMD', help='Project root')
    
    args = parser.parse_args()
    
    agent = PlannerAgent(args.project_root)
    
    if args.analyze:
        print(agent.analyze(deep=args.deep))
    elif args.research:
        print(agent.research(args.research))
    elif args.auto_fix:
        print(agent.auto_fix(problem_keywords=args.auto_fix))
    elif args.fix_id:
        print(agent.auto_fix(fix_id=args.fix_id))
    elif args.fix_all:
        print(agent.fix_all_known())
    elif args.plan:
        print(agent.plan_goal(args.plan))
    elif args.health:
        print(agent.health_check())
    elif args.tasks:
        print(agent.check_tasks())
    elif args.learn:
        problem, solution, success, details = args.learn
        print(agent.learn(problem, solution, success == 'True', details))
    else:
        print("StenoMD Planner Agent")
        print("Use --help for options")
        print("\nExamples:")
        print("  python3 planner_agent/main.py --health")
        print("  python3 planner_agent/main.py --analyze")
        print("  python3 planner_agent/main.py --tasks")
        print("  python3 planner_agent/main.py --research 'cdep.ro 404'")


if __name__ == "__main__":
    main()
