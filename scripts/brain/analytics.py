"""
Analytics Engine - Metrics and Health Module

Provides real-time project health diagnostics,
metrics tracking, and intelligent recommendations.
"""

import re
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from memory import MemoryStore


class AnalyticsEngine:
    """
    Real-time project analytics and health scoring.
    
    Metrics Tracked:
    - Code Quality: Syntax errors, issues, lint violations
    - Data Integrity: Duplicates, empty files, format consistency
    - Performance: Agent execution time, API response time
    - Coverage: Vault completeness, KG population rate
    - Health: Error rates, crash frequency, recovery time
    """
    
    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path(__file__).parent.parent.parent
        self.memory = MemoryStore(self.project_dir)
        
        # Health score weights
        self.health_weights = {
            'code_quality': 0.25,
            'data_integrity': 0.25,
            'agent_performance': 0.20,
            'vault_coverage': 0.15,
            'learning_progress': 0.15
        }
    
    def calculate_health_score(self) -> Dict:
        """
        Calculate overall project health (0-100).
        
        Returns:
            Health score with breakdown
        """
        scores = {}
        total_weight = sum(self.health_weights.values())
        
        # Code Quality (0-100)
        code_quality = self._analyze_code_quality()
        scores['code_quality'] = code_quality['score']
        
        # Data Integrity (0-100)
        data_integrity = self._analyze_data_integrity()
        scores['data_integrity'] = data_integrity['score']
        
        # Agent Performance (0-100)
        performance = self._analyze_agent_performance()
        scores['agent_performance'] = performance['score']
        
        # Vault Coverage (0-100)
        coverage = self._analyze_vault_coverage()
        scores['vault_coverage'] = coverage['score']
        
        # Learning Progress (0-100)
        learning = self._analyze_learning_progress()
        scores['learning_progress'] = learning['score']
        
        # Calculate weighted total
        total_score = sum(
            scores[key] * self.health_weights.get(key, 0) / total_weight
            for key in scores
        )
        
        return {
            'score': round(total_score, 1),
            'max': 100,
            'grade': self._get_grade(total_score),
            'breakdown': scores,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_grade(self, score: float) -> str:
        """Get letter grade from score."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _analyze_code_quality(self) -> Dict:
        """Analyze code quality metrics."""
        score = 100
        issues = []
        
        # Check for syntax errors in Python files
        syntax_errors = 0
        for py_file in self.project_dir.glob('scripts/**/*.py'):
            try:
                result = subprocess.run(
                    ['python3', '-m', 'py_compile', str(py_file)],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode != 0:
                    syntax_errors += 1
            except:
                pass
        
        if syntax_errors > 0:
            score -= syntax_errors * 10
            issues.append(f'{syntax_errors} syntax errors found')
        
        # Check for TODO/FIXME comments
        todo_count = 0
        for py_file in self.project_dir.glob('scripts/**/*.py'):
            try:
                content = py_file.read_text()
                todo_count += len(re.findall(r'(TODO|FIXME|HACK)', content))
            except:
                pass
        
        if todo_count > 10:
            score -= 5
            issues.append(f'{todo_count} TODO/FIXME comments')
        
        return {
            'score': max(0, score),
            'issues': issues,
            'details': {
                'syntax_errors': syntax_errors,
                'todo_count': todo_count
            }
        }
    
    def _analyze_data_integrity(self) -> Dict:
        """Analyze data integrity metrics."""
        score = 100
        issues = []
        
        # Check for empty files
        empty_files = list(self.project_dir.glob('vault/**/*.md'))
        empty_count = sum(1 for f in empty_files if f.stat().st_size == 0)
        if empty_count > 0:
            score -= empty_count * 5
            issues.append(f'{empty_count} empty files')
        
        # Check for duplicates
        duplicates = self._find_duplicates()
        if duplicates:
            score -= len(duplicates) * 3
            issues.append(f'{len(duplicates)} duplicate entries')
        
        # Check for format inconsistencies
        format_issues = self._check_format_consistency()
        if format_issues:
            score -= len(format_issues) * 2
            issues.extend(format_issues)
        
        return {
            'score': max(0, score),
            'issues': issues,
            'details': {
                'empty_files': empty_count,
                'duplicates': len(duplicates),
                'format_issues': len(format_issues)
            }
        }
    
    def _find_duplicates(self) -> List[str]:
        """Find duplicate entries in vault."""
        duplicates = []
        
        # Check for duplicate politician names (diacritics variants)
        deputies_dir = self.project_dir / 'vault' / 'politicians' / 'deputies'
        if deputies_dir.exists():
            names = {}
            for f in deputies_dir.glob('*.md'):
                name = f.stem.lower()
                # Normalize diacritics
                normalized = name.replace('ă', 'a').replace('â', 'a').replace('î', 'i').replace('ș', 's').replace('ț', 't')
                if normalized in names:
                    duplicates.append(name)
                else:
                    names[normalized] = name
        
        return duplicates
    
    def _check_format_consistency(self) -> List[str]:
        """Check for format inconsistencies."""
        issues = []
        
        # Check session date formats
        sessions_dir = self.project_dir / 'vault' / 'sessions'
        for chamber in ['senate', 'deputies']:
            chamber_dir = sessions_dir / chamber
            if chamber_dir.exists():
                for f in chamber_dir.glob('*.md'):
                    name = f.stem
                    # Check for non-ISO dates
                    if re.match(r'^\d{4}-\d{2}-\d{2}$', name):
                        continue  # ISO format - OK
                    elif re.match(r'^\d{8}$', name):
                        issues.append(f'{chamber}/{f.name}: YYYYMMDD format')
                    elif re.match(r'^\d+-[a-z]+-\d{4}$', name, re.IGNORECASE):
                        issues.append(f'{chamber}/{f.name}: Romanian date format')
        
        return issues
    
    def _analyze_agent_performance(self) -> Dict:
        """Analyze agent performance metrics."""
        score = 100
        issues = []
        
        # Get action statistics
        stats = self.memory.episodic.get_statistics()
        
        # Success rate impact
        success_rate = stats.get('success_rate', 1.0)
        if success_rate < 0.8:
            score -= (0.8 - success_rate) * 100
            issues.append(f'Success rate: {success_rate:.0%}')
        
        # Average duration
        avg_duration = stats.get('avg_duration_ms', 0)
        if avg_duration > 60000:  # Over 1 minute average
            score -= 10
            issues.append(f'Avg duration: {avg_duration/1000:.1f}s')
        
        return {
            'score': max(0, score),
            'issues': issues,
            'details': {
                'success_rate': success_rate,
                'avg_duration_ms': avg_duration,
                'total_actions': stats.get('total_actions', 0)
            }
        }
    
    def _analyze_vault_coverage(self) -> Dict:
        """Analyze vault completeness."""
        score = 100
        issues = []
        
        # Count vault files
        politicians_dir = self.project_dir / 'vault' / 'politicians'
        senators = len(list((politicians_dir / 'senators').glob('*.md'))) if (politicians_dir / 'senators').exists() else 0
        deputies = len(list((politicians_dir / 'deputies').glob('*.md'))) if (politicians_dir / 'deputies').exists() else 0
        
        sessions_dir = self.project_dir / 'vault' / 'sessions'
        senate_sessions = len(list((sessions_dir / 'senate').glob('*.md'))) if (sessions_dir / 'senate').exists() else 0
        deputy_sessions = len(list((sessions_dir / 'deputies').glob('*.md'))) if (sessions_dir / 'deputies').exists() else 0
        
        # Score based on content
        if senators < 5:
            score -= 15
            issues.append(f'Only {senators} senators (expected 5+)')
        
        if deputies < 100:
            score -= 10
            issues.append(f'Only {deputies} deputies (expected 100+)')
        
        if senate_sessions < 10:
            score -= 10
            issues.append(f'Only {senate_sessions} Senate sessions')
        
        if deputy_sessions < 10:
            score -= 10
            issues.append(f'Only {deputy_sessions} Deputy sessions')
        
        return {
            'score': max(0, score),
            'issues': issues,
            'details': {
                'senators': senators,
                'deputies': deputies,
                'senate_sessions': senate_sessions,
                'deputy_sessions': deputy_sessions
            }
        }
    
    def _analyze_learning_progress(self) -> Dict:
        """Analyze learning system progress."""
        score = 50  # Start neutral
        
        # Get memory statistics
        stats = self.memory.get_stats()
        
        # Pattern count bonus
        pattern_count = stats.get('patterns_count', 0)
        if pattern_count >= 10:
            score += 20
        elif pattern_count >= 5:
            score += 10
        elif pattern_count >= 1:
            score += 5
        
        # Learning effectiveness
        effectiveness = self.memory.analyze_effectiveness()
        avg_success = effectiveness.get('avg_success_rate', 0)
        if avg_success >= 0.8:
            score += 20
        elif avg_success >= 0.6:
            score += 10
        
        # Cache utilization
        cache_stats = stats.get('cache_size', 0)
        if cache_stats > 50:
            score += 10
        
        return {
            'score': min(100, score),
            'issues': [],
            'details': {
                'patterns_learned': pattern_count,
                'avg_success_rate': avg_success,
                'cache_size': cache_stats
            }
        }
    
    def get_comprehensive_metrics(self) -> Dict:
        """Get all tracked metrics."""
        health = self.calculate_health_score()
        trends = self._get_trends()
        
        return {
            'health': health,
            'trends': trends,
            'memory_stats': self.memory.get_stats(),
            'code_quality': self._analyze_code_quality(),
            'data_integrity': self._analyze_data_integrity(),
            'agent_performance': self._analyze_agent_performance(),
            'vault_coverage': self._analyze_vault_coverage(),
            'learning_progress': self._analyze_learning_progress()
        }
    
    def _get_trends(self) -> Dict:
        """Get metric trends."""
        trends = {}
        
        # Action trends
        action_trends = self.memory.episodic.get_trends(days=7)
        trends['actions'] = {
            'total': sum(d['count'] for d in action_trends.get('daily_breakdown', [])),
            'success_rate': action_trends.get('recent_success_rate', 0)
        }
        
        # Pattern growth
        patterns = self.memory.procedural.get_effectiveness()
        trends['patterns'] = {
            'count': patterns.get('total_patterns', 0),
            'avg_success': patterns.get('avg_success_rate', 0)
        }
        
        return trends
    
    def generate_recommendations(self) -> List[Dict]:
        """Generate improvement recommendations based on analysis."""
        recommendations = []
        
        health = self.calculate_health_score()
        
        # Low health areas
        for component, score in health['breakdown'].items():
            if score < 70:
                recommendations.append({
                    'priority': 'high' if score < 50 else 'medium',
                    'component': component,
                    'score': score,
                    'recommendation': self._get_recommendation(component, score)
                })
        
        # Check for anomalies
        from .vision import VisionEngine
        vision = VisionEngine(self.project_dir)
        anomalies = vision.detect_anomalies(self.get_comprehensive_metrics())
        
        for anomaly in anomalies:
            recommendations.append({
                'priority': anomaly.get('severity', 'medium'),
                'component': 'anomaly',
                'anomaly_type': anomaly.get('type'),
                'description': anomaly.get('description'),
                'recommendation': f'Investigate: {anomaly.get("description")}'
            })
        
        return sorted(recommendations, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x['priority'], 1))
    
    def _get_recommendation(self, component: str, score: float) -> str:
        """Get recommendation for low-scoring component."""
        recommendations = {
            'code_quality': 'Run syntax check on all Python files',
            'data_integrity': 'Run vault cleanup and consolidation',
            'agent_performance': 'Review failed actions for patterns',
            'vault_coverage': 'Scrape more sessions to expand vault',
            'learning_progress': 'Use the agent more to build patterns'
        }
        return recommendations.get(component, 'Investigate and fix')
    
    def generate_health_report(self) -> str:
        """Generate human-readable health report."""
        health = self.calculate_health_score()
        metrics = self.get_comprehensive_metrics()
        
        lines = []
        lines.append("# StenoMD Health Report")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Overall Score:** {health['score']}/100 ({health['grade']})")
        lines.append("")
        
        lines.append("## Component Scores")
        for component, score in health['breakdown'].items():
            bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
            lines.append(f"- **{component.title()}:** {bar} {score}/100")
        
        lines.append("")
        lines.append("## Issues")
        
        all_issues = []
        for component in ['code_quality', 'data_integrity', 'agent_performance', 'vault_coverage']:
            comp_data = metrics.get(component, {})
            all_issues.extend(comp_data.get('issues', []))
        
        if all_issues:
            for issue in all_issues:
                lines.append(f"- {issue}")
        else:
            lines.append("- No issues detected")
        
        lines.append("")
        lines.append("## Recommendations")
        recommendations = self.generate_recommendations()
        for rec in recommendations[:5]:
            lines.append(f"- [{rec['priority'].upper()}] {rec['recommendation']}")
        
        return "\n".join(lines)