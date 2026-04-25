#!/usr/bin/env python3
"""
Unit tests for Smart Planner Agent
"""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

PROJECT_DIR = Path(__file__).parent.parent.parent


class TestPlannerAgent(unittest.TestCase):
    """Test cases for Smart Planner Agent."""
    
    def test_planner_import(self):
        """Test planner agent can be imported."""
        from planner_agent import main
        self.assertIsNotNone(main)
    
    def test_health_check(self):
        """Test health check output."""
        agent_dir = PROJECT_DIR / "scripts" / "planner_agent"
        self.assertTrue(agent_dir.exists())
    
    def test_problem_analyzer_exists(self):
        """Test problem_analyzer module exists."""
        from planner_agent import problem_analyzer
        self.assertIsNotNone(problem_analyzer)
    
    def test_solution_researcher_exists(self):
        """Test solution_researcher module exists."""
        from planner_agent import solution_researcher
        self.assertIsNotNone(solution_researcher)
    
    def test_decision_engine_exists(self):
        """Test decision_engine module exists."""
        from planner_agent import decision_engine
        self.assertIsNotNone(decision_engine)
    
    def test_auto_fixer_exists(self):
        """Test auto_fixer module exists."""
        from planner_agent import auto_fixer
        self.assertIsNotNone(auto_fixer)
    
    def test_pattern_miner_exists(self):
        """Test pattern_miner module exists."""
        from planner_agent import pattern_miner
        self.assertIsNotNone(pattern_miner)
    
    def test_notifications_exists(self):
        """Test notifications module exists."""
        from planner_agent import notifications
        self.assertIsNotNone(notifications)


class TestProjectStructure(unittest.TestCase):
    """Test cases for project structure."""
    
    def test_vault_exists(self):
        """Test vault directory exists."""
        self.assertTrue((PROJECT_DIR / "vault").exists())
    
    def test_kg_exists(self):
        """Test knowledge graph directory exists."""
        self.assertTrue((PROJECT_DIR / "knowledge_graph").exists())
    
    def test_agents_exists(self):
        """Test agents directory exists."""
        self.assertTrue((PROJECT_DIR / "scripts" / "agents").exists())
    
    def test_analyze_exists(self):
        """Test analyze directory exists."""
        self.assertTrue((PROJECT_DIR / "scripts" / "analyze").exists())
    
    def test_memory_exists(self):
        """Test memory directory exists."""
        self.assertTrue((PROJECT_DIR / "scripts" / "memory").exists())


class TestComponents(unittest.TestCase):
    """Test cases for core components."""
    
    def test_cdep_agent_exists(self):
        """Test cdep_agent exists."""
        from agents import cdep_agent
        self.assertIsNotNone(cdep_agent)
    
    def test_senat_agent_exists(self):
        """Test senat_agent exists."""
        from agents import senat_agent
        self.assertIsNotNone(senat_agent)
    
    def test_validators_exists(self):
        """Test validators module exists."""
        from validators import DataValidator
        self.assertIsNotNone(DataValidator)


if __name__ == '__main__':
    unittest.main()