"""
Memory Module for StenoMD Master Strategist

Provides multi-layer memory system:
- Episodic: Action history with full context
- Semantic: Knowledge graph integration
- Procedural: Learned patterns and methods
- Cache: Fast LRU access to frequent items

Usage:
    from memory import MemoryStore
    memory = MemoryStore()
    memory.learn(action, outcome)
    suggestions = memory.suggest(context)
"""

from .episodic import EpisodicMemory
from .semantic import SemanticMemory
from .procedural import ProceduralMemory
from .cache import FastCache
from .schema import DatabaseSchema

__all__ = [
    'EpisodicMemory',
    'SemanticMemory', 
    'ProceduralMemory',
    'FastCache',
    'DatabaseSchema',
    'MemoryStore'
]


class MemoryStore:
    """
    Unified memory store combining all memory types.
    
    This is the main interface for the Planner Agent.
    """
    
    def __init__(self, project_dir: str = None):
        from pathlib import Path
        self.project_dir = Path(project_dir) if project_dir else Path(__file__).parent.parent.parent
        self.memory_dir = self.project_dir / 'scripts' / 'memory'
        
        # Initialize all memory layers
        self.episodic = EpisodicMemory(self.memory_dir)
        self.semantic = SemanticMemory(self.memory_dir)
        self.procedural = ProceduralMemory(self.memory_dir)
        self.cache = FastCache(max_size=100)
        
    def learn(self, action: dict, outcome: dict):
        """
        Record an action and its outcome, updating all memory layers.
        
        Args:
            action: Dict with action details (type, command, params, etc.)
            outcome: Dict with result (success, duration, etc.)
        """
        # Store in episodic memory
        action_id = self.episodic.store(action, outcome)
        
        # Extract and store patterns
        if outcome.get('success'):
            self.procedural.learn_fix(action, outcome)
        else:
            self.procedural.learn_failure(action, outcome)
            
        # Update semantic knowledge
        self.semantic.add_knowledge(action, outcome)
        
        # Update cache
        key = f"{action.get('type')}:{action.get('issue', {}).get('description', '')[:50]}"
        self.cache.put(key, {'action_id': action_id, 'success': outcome.get('success')})
        
        return action_id
    
    def recall(self, query: str, limit: int = 10) -> list:
        """
        Recall relevant memories based on query.
        
        Args:
            query: Search query string
            limit: Maximum results to return
            
        Returns:
            List of relevant memories with context
        """
        results = []
        
        # Search episodic memory
        episodic_results = self.episodic.search(query, limit)
        results.extend(episodic_results)
        
        # Search procedural memory
        procedural_results = self.procedural.search(query, limit)
        results.extend(procedural_results)
        
        # Search semantic memory
        semantic_results = self.semantic.search(query, limit)
        results.extend(semantic_results)
        
        # Sort by relevance (simplified - based on recency)
        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return results[:limit]
    
    def suggest(self, context: dict, limit: int = 5) -> list:
        """
        Suggest actions based on learned patterns.
        
        Args:
            context: Current context (issue description, type, etc.)
            limit: Maximum suggestions to return
            
        Returns:
            List of suggested actions with confidence scores
        """
        suggestions = []
        
        issue_desc = context.get('issue', {}).get('description', '')
        issue_type = context.get('issue', {}).get('type', '')
        severity = context.get('issue', {}).get('severity', '')
        
        # Find matching patterns
        patterns = self.procedural.find_patterns(
            issue_desc=issue_desc,
            issue_type=issue_type,
            severity=severity
        )
        
        for pattern in patterns:
            suggestions.append({
                'fix': pattern.get('fix_pattern'),
                'confidence': pattern.get('confidence', 0.5),
                'success_rate': pattern.get('success_rate', 0),
                'times_used': pattern.get('times_used', 0),
                'avg_duration': pattern.get('avg_duration_ms', 0),
                'last_used': pattern.get('last_used')
            })
        
        return sorted(suggestions, key=lambda x: x['confidence'], reverse=True)[:limit]
    
    def get_stats(self) -> dict:
        """Get memory statistics."""
        return {
            'episodic_count': self.episodic.count(),
            'patterns_count': self.procedural.count(),
            'knowledge_count': self.semantic.count(),
            'cache_size': self.cache.size(),
            'cache_hit_rate': self.cache.hit_rate()
        }
    
    def analyze_effectiveness(self) -> dict:
        """Analyze which strategies work best."""
        return self.procedural.get_effectiveness()
    
    def get_insights(self) -> str:
        """Generate natural language insights from memory."""
        insights = []
        
        # Most effective fix patterns
        effective = self.procedural.get_most_effective(limit=5)
        if effective:
            insights.append("## Top Performing Fixes")
            for i, pattern in enumerate(effective, 1):
                rate = pattern.get('success_rate', 0) * 100
                insights.append(f"{i}. **{pattern.get('fix_pattern', 'Unknown')}**: {rate:.0f}% success rate")
        
        # Common issues
        common = self.episodic.get_common_issues(limit=5)
        if common:
            insights.append("\n## Frequently Occurring Issues")
            for issue, count in common:
                insights.append(f"- {issue}: occurred {count} times")
        
        # Learning progress
        stats = self.get_stats()
        insights.append(f"\n## Memory Progress")
        insights.append(f"- Total actions learned: {stats['episodic_count']}")
        insights.append(f"- Patterns established: {stats['patterns_count']}")
        insights.append(f"- Knowledge entries: {stats['knowledge_count']}")
        
        return "\n".join(insights)