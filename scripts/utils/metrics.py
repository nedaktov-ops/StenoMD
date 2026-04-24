"""
Metrics Calculator

Provides standardized metrics calculations for analytics.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import Counter


class MetricsCalculator:
    """
    Standardized metrics calculations.
    
    Provides common metric formulas and aggregations.
    """
    
    @staticmethod
    def calculate_success_rate(total: int, successes: int) -> float:
        """Calculate success rate percentage."""
        if total == 0:
            return 0.0
        return (successes / total) * 100
    
    @staticmethod
    def calculate_average(values: List[float]) -> float:
        """Calculate average of values."""
        if not values:
            return 0.0
        return sum(values) / len(values)
    
    @staticmethod
    def calculate_median(values: List[float]) -> float:
        """Calculate median of values."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        else:
            return sorted_values[n // 2]
    
    @staticmethod
    def calculate_percentile(values: List[float], percentile: int) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        lower = int(index)
        upper = lower + 1
        weight = index - lower
        if upper >= len(sorted_values):
            return sorted_values[lower]
        return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight
    
    @staticmethod
    def calculate_trend(current: float, previous: float) -> Dict:
        """
        Calculate trend between two values.
        
        Args:
            current: Current value
            previous: Previous value
            
        Returns:
            Trend dict with change and direction
        """
        if previous == 0:
            change = 100.0 if current > 0 else 0.0
        else:
            change = ((current - previous) / previous) * 100
        
        return {
            'current': current,
            'previous': previous,
            'change': change,
            'direction': 'up' if change > 0 else ('down' if change < 0 else 'stable'),
            'improved': change > 0
        }
    
    @staticmethod
    def calculate_health_score(components: Dict[str, float], 
                                 weights: Dict[str, float] = None) -> Dict:
        """
        Calculate weighted health score.
        
        Args:
            components: Dict of component scores
            weights: Dict of component weights
            
        Returns:
            Health score dict
        """
        if not components:
            return {'score': 0, 'grade': 'F'}
        
        if weights is None:
            # Equal weights
            weights = {k: 1.0 / len(components) for k in components}
        
        total_weight = sum(weights.values())
        weighted_sum = sum(
            components.get(k, 0) * weights.get(k, 0) / total_weight
            for k in components
        )
        
        return {
            'score': round(weighted_sum, 1),
            'max': 100,
            'grade': MetricsCalculator._get_grade(weighted_sum)
        }
    
    @staticmethod
    def _get_grade(score: float) -> str:
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
    
    @staticmethod
    def calculate_confidence(similar_count: int, success_count: int, 
                            total_attempts: int) -> float:
        """
        Calculate confidence score based on history.
        
        Args:
            similar_count: Number of similar past cases
            success_count: Number of successful outcomes
            total_attempts: Total number of attempts
            
        Returns:
            Confidence score (0-1)
        """
        # Base confidence from success rate
        if total_attempts > 0:
            success_rate = success_count / total_attempts
        else:
            success_rate = 0.5  # Neutral
        
        # Boost from similar cases
        if similar_count >= 5:
            similar_boost = 0.15
        elif similar_count >= 3:
            similar_boost = 0.10
        elif similar_count >= 1:
            similar_boost = 0.05
        else:
            similar_boost = 0.0
        
        confidence = (success_rate * 0.8) + similar_boost
        return min(1.0, max(0.0, confidence))
    
    @staticmethod
    def aggregate_durations(durations: List[int]) -> Dict:
        """
        Aggregate duration statistics.
        
        Args:
            durations: List of duration values in milliseconds
            
        Returns:
            Duration statistics dict
        """
        if not durations:
            return {
                'count': 0,
                'min': 0,
                'max': 0,
                'avg': 0,
                'median': 0,
                'p95': 0
            }
        
        return {
            'count': len(durations),
            'min': min(durations),
            'max': max(durations),
            'avg': MetricsCalculator.calculate_average(durations),
            'median': MetricsCalculator.calculate_median(durations),
            'p95': MetricsCalculator.calculate_percentile(durations, 95),
            'p99': MetricsCalculator.calculate_percentile(durations, 99)
        }
    
    @staticmethod
    def group_by_time_bucket(values: List[Dict], time_field: str = 'timestamp',
                            bucket: str = 'day') -> Dict[str, List]:
        """
        Group values by time bucket.
        
        Args:
            values: List of dicts with timestamps
            time_field: Field name containing timestamp
            bucket: 'hour', 'day', 'week', 'month'
            
        Returns:
            Dict of time buckets to value lists
        """
        buckets = {}
        
        for value in values:
            timestamp_str = value.get(time_field, '')
            if not timestamp_str:
                continue
            
            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                
                if bucket == 'hour':
                    key = dt.strftime('%Y-%m-%d %H:00')
                elif bucket == 'day':
                    key = dt.strftime('%Y-%m-%d')
                elif bucket == 'week':
                    key = dt.strftime('%Y-W%U')
                elif bucket == 'month':
                    key = dt.strftime('%Y-%m')
                else:
                    key = dt.strftime('%Y-%m-%d')
                
                if key not in buckets:
                    buckets[key] = []
                buckets[key].append(value)
            except:
                pass
        
        return buckets
    
    @staticmethod
    def calculate_pattern_metrics(actions: List[Dict]) -> Dict:
        """
        Calculate pattern metrics from action list.
        
        Args:
            actions: List of action records
            
        Returns:
            Pattern metrics dict
        """
        if not actions:
            return {
                'total': 0,
                'success_rate': 0,
                'avg_duration': 0,
                'most_common_type': None,
                'trend': 'stable'
            }
        
        successes = sum(1 for a in actions if a.get('success'))
        durations = [a.get('duration_ms', 0) for a in actions if a.get('duration_ms')]
        types = [a.get('type') for a in actions if a.get('type')]
        
        type_counts = Counter(types)
        most_common = type_counts.most_common(1)[0] if type_counts else (None, 0)
        
        return {
            'total': len(actions),
            'success_rate': successes / len(actions) if actions else 0,
            'avg_duration': MetricsCalculator.calculate_average(durations),
            'median_duration': MetricsCalculator.calculate_median(durations),
            'most_common_type': most_common[0],
            'most_common_count': most_common[1],
            'type_distribution': dict(type_counts)
        }
    
    @staticmethod
    def calculate_velocity(completed: int, time_period: float) -> Dict:
        """
        Calculate velocity (completion rate).
        
        Args:
            completed: Number of items completed
            time_period: Time period in seconds
            
        Returns:
            Velocity metrics
        """
        if time_period <= 0:
            return {
                'items': completed,
                'time_seconds': time_period,
                'rate_per_hour': 0,
                'rate_per_day': 0
            }
        
        hours = time_period / 3600
        days = time_period / 86400
        
        return {
            'items': completed,
            'time_seconds': time_period,
            'rate_per_hour': completed / hours if hours > 0 else 0,
            'rate_per_day': completed / days if days > 0 else 0
        }