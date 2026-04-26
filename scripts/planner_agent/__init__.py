"""StenoMD Planner Agent - Smart project planning and analysis."""
__version__ = "1.0.0"

import sys
from pathlib import Path

# Add parent directory to path for task_manager import
sys.path.insert(0, str(Path(__file__).parent.parent))

from .problem_analyzer import ProblemAnalyzer
from .solution_researcher import SolutionResearcher
from .decision_engine import DecisionEngine
from .auto_fixer import AutoFixer
from .pattern_miner import PatternMiner
from .notifications import NotificationService
from task_manager import TaskManager

__all__ = [
    "ProblemAnalyzer",
    "SolutionResearcher",
    "DecisionEngine",
    "AutoFixer",
    "PatternMiner",
    "NotificationService",
    "TaskManager",
]
