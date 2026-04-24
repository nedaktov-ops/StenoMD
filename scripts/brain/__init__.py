"""
Brain Module for StenoMD Master Strategist

Provides cognitive capabilities:
- Vision: Pattern recognition engine
- Strategy: Strategy planning engine
- Analytics: Metrics and health engine
- Debugger: Debug assistance engine
- Cortex: Main orchestration

Usage:
    from brain import Cortex, VisionEngine, StrategyPlanner
    cortex = Cortex()
    result = cortex.think(context)
"""

from .cortex import Cortex
from .vision import VisionEngine
from .strategy import StrategyPlanner
from .analytics import AnalyticsEngine
from .debugger import DebuggingEngine

__all__ = [
    'Cortex',
    'VisionEngine',
    'StrategyPlanner',
    'AnalyticsEngine',
    'DebuggingEngine'
]