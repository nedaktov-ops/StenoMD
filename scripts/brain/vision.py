"""
Vision Engine - Pattern Recognition Module

Finds patterns, predicts outcomes, detects trends.
Learns from all historical data.
"""

import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from collections import Counter, defaultdict

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from memory import MemoryStore


class VisionEngine:
    """
    Pattern recognition and prediction engine.
    
    Capabilities:
    - Temporal analysis (track issues over time)
    - Causal chains (identify cause-effect)
    - Anomaly detection (spot unusual patterns)
    - Trend detection (improving/degrading metrics)
    - Risk prediction (forecast potential issues)
    """
    
    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path(__file__).parent.parent.parent
        self.memory = MemoryStore(self.project_dir)
        
        # Pattern types
        self.pattern_types = {
            'issue_fix_pair': {
                'description': 'When issue X occurs, fix Y works',
                'weight': 0.4,
                'min_occurrences': 1  # Aggressive learning (1+)
            },
            'file_ripple': {
                'description': 'Changes to file A often affect file B',
                'weight': 0.15,
                'min_occurrences': 2
            },
            'time_to_fix': {
                'description': 'Issue type X typically takes N seconds',
                'weight': 0.1
            },
            'seasonal_issue': {
                'description': 'Issue type X occurs more in context Y',
                'weight': 0.15
            },
            'sequential_fix': {
                'description': 'Fix A often precedes Fix B',
                'weight': 0.1
            }
        }
    
    def find_patterns(self, experiences: List[Dict]) -> List[Dict]:
        """
        Analyze experiences to find actionable patterns.
        
        Args:
            experiences: List of action records from memory
            
        Returns:
            List of detected patterns with confidence scores
        """
        patterns = []
        
        # Group by issue description
        issue_groups = defaultdict(list)
        for exp in experiences:
            desc = exp.get('description', '')
            if desc:
                issue_groups[desc].append(exp)
        
        # Analyze each group
        for issue, actions in issue_groups.items():
            successes = [a for a in actions if a.get('success')]
            
            if successes:
                # Extract common fix
                commands = [a.get('command', '') for a in successes if a.get('command')]
                if commands:
                    most_common_cmd = Counter(commands).most_common(1)[0]
                    
                    pattern = {
                        'type': 'issue_fix_pair',
                        'issue': issue,
                        'fix': most_common_cmd[0],
                        'confidence': len(successes) / len(actions),
                        'times_used': len(actions),
                        'success_rate': len(successes) / len(actions),
                        'avg_duration': sum(a.get('duration_ms', 0) for a in actions) / len(actions) if actions else 0
                    }
                    patterns.append(pattern)
            
            # Analyze failure patterns
            failures = [a for a in actions if not a.get('success')]
            if failures:
                pattern = {
                    'type': 'failure_pattern',
                    'issue': issue,
                    'failures': len(failures),
                    'failure_rate': len(failures) / len(actions),
                    'last_failure': max(a.get('timestamp', '') for a in failures)
                }
                patterns.append(pattern)
        
        # Find file ripple patterns
        patterns.extend(self._find_file_ripples(experiences))
        
        # Find time patterns
        patterns.extend(self._find_time_patterns(experiences))
        
        return sorted(patterns, key=lambda x: x.get('confidence', 0), reverse=True)
    
    def _find_file_ripples(self, experiences: List[Dict]) -> List[Dict]:
        """Find files that often change together."""
        ripples = []
        
        # Group by command
        cmd_groups = defaultdict(list)
        for exp in experiences:
            cmd = exp.get('command', '')
            files = exp.get('files_affected', [])
            if cmd and files:
                cmd_groups[cmd].extend(files)
        
        # Analyze co-occurrence
        for cmd, files_list in cmd_groups.items():
            file_counts = Counter(files_list)
            # Files that appear together with same command
            for file1, count1 in file_counts.items():
                for file2, count2 in file_counts.items():
                    if file1 < file2 and count1 >= 2 and count2 >= 2:
                        ripples.append({
                            'type': 'file_ripple',
                            'file1': file1,
                            'file2': file2,
                            'often_with': cmd,
                            'confidence': min(count1, count2) / sum(file_counts.values())
                        })
        
        return ripples
    
    def _find_time_patterns(self, experiences: List[Dict]) -> List[Dict]:
        """Find patterns related to time."""
        time_patterns = []
        
        # Group by hour of day
        hourly = defaultdict(list)
        for exp in experiences:
            timestamp = exp.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hourly[dt.hour].append(exp)
                except:
                    pass
        
        # Find busy hours
        for hour, actions in hourly.items():
            successes = sum(1 for a in actions if a.get('success'))
            if len(actions) >= 3:
                time_patterns.append({
                    'type': 'time_pattern',
                    'context': f'hour_{hour}',
                    'actions': len(actions),
                    'success_rate': successes / len(actions),
                    'description': f'More issues at {hour}:00'
                })
        
        return time_patterns
    
    def predict_outcome(self, action: Dict) -> Dict:
        """
        Predict likely outcome of proposed action.
        
        Args:
            action: Action to predict
            
        Returns:
            Prediction with confidence and reasoning
        """
        issue_desc = action.get('issue', {}).get('description', '')
        command = action.get('command', '')
        
        # Search for similar past actions
        similar = self.memory.recall(issue_desc or command, limit=10)
        
        if not similar:
            return {
                'prediction': 'unknown',
                'confidence': 0.3,
                'reasoning': 'No similar past actions found'
            }
        
        # Calculate success probability
        successes = sum(1 for a in similar if a.get('success'))
        success_rate = successes / len(similar) if similar else 0
        
        # Find most similar successful action
        most_similar_success = None
        for a in similar:
            if a.get('success'):
                most_similar_success = a
                break
        
        prediction = 'success' if success_rate > 0.5 else 'failure'
        confidence = min(0.9, max(0.1, success_rate + (0.1 if successes > 2 else 0)))
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'success_rate': success_rate,
            'similar_cases': len(similar),
            'reasoning': f'{successes}/{len(similar)} similar actions succeeded',
            'similar_example': most_similar_success.get('command') if most_similar_success else None
        }
    
    def detect_anomalies(self, metrics: Dict) -> List[Dict]:
        """
        Identify unusual patterns in metrics.
        
        Args:
            metrics: Current metrics dictionary
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Get historical stats
        stats = self.memory.episodic.get_statistics()
        
        # Check action count anomaly
        if stats.get('total_actions', 0) > 100:
            recent_trend = self.memory.episodic.get_trends(days=1)
            if recent_trend.get('daily_breakdown'):
                last_day = recent_trend['daily_breakdown'][-1]
                avg_day = recent_trend['daily_breakdown'][-7:-1] if len(recent_trend['daily_breakdown']) > 6 else recent_trend['daily_breakdown'][:-1]
                if avg_day:
                    avg_count = sum(d['count'] for d in avg_day) / len(avg_day)
                    if last_day['count'] > avg_count * 2:
                        anomalies.append({
                            'type': 'activity_spike',
                            'description': f'Unusual activity: {last_day["count"]} actions today vs {avg_count:.1f} average',
                            'severity': 'medium',
                            'metric': 'daily_actions'
                        })
        
        # Check success rate anomaly
        recent_rate = stats.get('success_rate', 0.9)
        if recent_rate < 0.7:
            anomalies.append({
                'type': 'success_rate_drop',
                'description': f'Success rate dropped to {recent_rate:.0%}',
                'severity': 'high',
                'metric': 'success_rate'
            })
        
        # Check for new failure patterns
        patterns = self.memory.procedural.get_least_effective(limit=5)
        for pattern in patterns:
            if pattern.get('failure_count', 0) >= 3:
                anomalies.append({
                    'type': 'repeated_failure',
                    'description': f'Fix "{pattern.get("fix_pattern", "unknown")}" failing {pattern["failure_count"]} times',
                    'severity': 'high',
                    'metric': 'fix_pattern',
                    'fix_pattern': pattern.get('fix_pattern')
                })
        
        return anomalies
    
    def find_related_issues(self, issue: Dict) -> List[Dict]:
        """
        Find issues that often occur together.
        
        Args:
            issue: Current issue dict
            
        Returns:
            List of related issues with correlation strength
        """
        related = []
        
        issue_desc = issue.get('description', '')
        if not issue_desc:
            return related
        
        # Search for co-occurring issues
        similar = self.memory.recall(issue_desc, limit=50)
        
        # Build co-occurrence matrix
        cooccurrence = defaultdict(int)
        for action in similar:
            files = action.get('files_affected', [])
            for f in files:
                cooccurrence[f] += 1
        
        # Find files that appear with this issue
        for file_path, count in cooccurrence.items():
            if count >= 2:
                # Check if there's a pattern for this file
                patterns = self.memory.procedural.find_patterns(issue_desc=file_path)
                if patterns:
                    related.append({
                        'issue': file_path,
                        'correlation': min(1.0, count / len(similar)),
                        'often_with': patterns[0].get('fix_pattern'),
                        'description': f'Often occurs together ({count} times)'
                    })
        
        return sorted(related, key=lambda x: x['correlation'], reverse=True)
    
    def generate_trends(self, days: int = 7) -> Dict:
        """
        Generate trend analysis.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Trend analysis with metrics
        """
        trends = {}
        
        # Get action trends
        action_trends = self.memory.episodic.get_trends(days=days)
        trends['actions'] = {
            'total': sum(d['count'] for d in action_trends.get('daily_breakdown', [])),
            'per_day_avg': action_trends.get('daily_breakdown', []).__len__() and \
                          sum(d['count'] for d in action_trends['daily_breakdown']) / len(action_trends['daily_breakdown']) or 0,
            'success_rate': action_trends.get('recent_success_rate', 0)
        }
        
        # Get pattern effectiveness trends
        effectiveness = self.memory.procedural.get_effectiveness()
        trends['patterns'] = {
            'total': effectiveness.get('total_patterns', 0),
            'avg_success_rate': effectiveness.get('avg_success_rate', 0)
        }
        
        # Compare to previous period
        if days >= 7:
            prev_trends = self.memory.episodic.get_trends(days=days * 2)
            prev_rate = prev_trends.get('recent_success_rate', 0)
            curr_rate = action_trends.get('recent_success_rate', 0)
            
            trends['comparison'] = {
                'success_rate_change': curr_rate - prev_rate,
                'improving': curr_rate > prev_rate
            }
        
        return trends
    
    def get_pattern_insights(self) -> List[str]:
        """
        Generate natural language insights from patterns.
        
        Returns:
            List of insight strings
        """
        insights = []
        
        # Most effective patterns
        effective = self.memory.procedural.get_most_effective(limit=3)
        if effective:
            insights.append("## Most Reliable Fixes")
            for i, p in enumerate(effective, 1):
                rate = p.get('confidence', 0) * 100
                insights.append(f"{i}. {p.get('fix_pattern', 'Unknown')}: {rate:.0f}% success")
        
        # Common issues
        common = self.memory.episodic.get_common_issues(limit=3)
        if common:
            insights.append("\n## Frequently Recurring")
            for issue, count in common:
                insights.append(f"- {issue}: seen {count} times")
        
        # Time patterns
        insights.append("\n## Recommendations")
        
        # Check for patterns needing attention
        least = self.memory.procedural.get_least_effective(limit=3)
        for p in least:
            if p.get('failure_count', 0) >= 2:
                insights.append(f"- Consider alternative for: {p.get('fix_pattern', 'Unknown')} (failing {p['failure_count']} times)")
        
        return insights