"""
Pattern Definitions

Defines known patterns for issue-fix matching.
Used by procedural memory and vision engine.
"""

from typing import Dict, List


class PatternDefinitions:
    """
    Known patterns for matching issues to fixes.
    
    These patterns help the system recognize common problems
    and suggest appropriate solutions.
    """
    
    # Issue type to keywords mapping
    ISSUE_KEYWORDS = {
        'empty': ['empty', 'blank', 'no content', 'null', 'undefined'],
        'duplicate': ['duplicate', 'redundant', 'multiple', 'copy', 'extra'],
        'migration': ['migration', 'migrate', 'convert', 'transform', 'rename'],
        'format': ['format', 'date', 'encoding', 'structure'],
        'import': ['import', 'module', 'dependency', 'missing', 'not found'],
        'syntax': ['syntax', 'error', 'parse', 'indent'],
        'permission': ['permission', 'access', 'denied', 'forbidden'],
        'connection': ['connection', 'network', 'timeout', 'unreachable'],
        'data': ['data', 'integrity', 'corrupt', 'invalid']
    }
    
    # Issue type to fix command mapping
    FIX_COMMANDS = {
        'empty': {
            'description': 'Remove empty files',
            'command': 'find {dir} -name "*.md" -empty -delete',
            'severity': 'low'
        },
        'duplicate': {
            'description': 'Merge duplicates using migration script',
            'command': 'python3 scripts/migrate_vault.py',
            'severity': 'high'
        },
        'migration': {
            'description': 'Run date migration script',
            'command': 'python3 scripts/migrate_dates.py',
            'severity': 'medium'
        },
        'format': {
            'description': 'Standardize file formats',
            'command': 'python3 scripts/migrate_dates.py',
            'severity': 'medium'
        },
        'import': {
            'description': 'Install missing dependencies',
            'command': 'pip install beautifulsoup4 lxml requests',
            'severity': 'high'
        },
        'merge': {
            'description': 'Merge knowledge graph',
            'command': 'python3 scripts/stenomd_master.py --merge',
            'severity': 'critical'
        }
    }
    
    # Fix pattern to success rate
    FIX_SUCCESS_RATES = {
        'migrate_vault.py': 0.95,
        'migrate_dates.py': 0.92,
        'stenomd_master.py --merge': 0.90,
        'pip install': 0.88,
        'find -delete': 0.85
    }
    
    # Pattern severity multipliers
    SEVERITY_MULTIPLIERS = {
        'critical': 1.5,
        'high': 1.2,
        'medium': 1.0,
        'low': 0.8
    }
    
    @classmethod
    def get_issue_type(cls, description: str) -> str:
        """
        Classify issue type from description.
        
        Args:
            description: Issue description
            
        Returns:
            Issue type string
        """
        desc_lower = description.lower()
        
        for issue_type, keywords in cls.ISSUE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    return issue_type
        
        return 'unknown'
    
    @classmethod
    def get_fix_for_issue(cls, issue_type: str) -> Dict:
        """
        Get recommended fix for issue type.
        
        Args:
            issue_type: Type of issue
            
        Returns:
            Fix recommendation dict
        """
        return cls.FIX_COMMANDS.get(issue_type, {
            'description': 'Unknown fix needed',
            'command': 'Investigate issue',
            'severity': 'medium'
        })
    
    @classmethod
    def get_fix_success_rate(cls, fix_command: str) -> float:
        """
        Get historical success rate for fix.
        
        Args:
            fix_command: Command string
            
        Returns:
            Success rate (0-1)
        """
        for fix, rate in cls.FIX_SUCCESS_RATES.items():
            if fix in fix_command:
                return rate
        return 0.7  # Default rate
    
    @classmethod
    def calculate_pattern_confidence(cls, issue_type: str, fix_command: str, 
                                     historical_count: int, historical_successes: int) -> float:
        """
        Calculate confidence for a pattern.
        
        Args:
            issue_type: Type of issue
            fix_command: Fix command
            historical_count: Number of times pattern used
            historical_successes: Number of successful uses
            
        Returns:
            Confidence score (0-1)
        """
        # Base confidence from known patterns
        base_rate = cls.get_fix_success_rate(fix_command)
        
        # Historical success rate
        if historical_count > 0:
            historical_rate = historical_successes / historical_count
        else:
            historical_rate = base_rate
        
        # Weight recent experiences more heavily
        if historical_count >= 3:
            confidence = (historical_rate * 0.7) + (base_rate * 0.3)
        elif historical_count >= 1:
            confidence = (historical_rate * 0.5) + (base_rate * 0.5)
        else:
            confidence = base_rate
        
        # Apply severity multiplier
        severity = cls.FIX_COMMANDS.get(issue_type, {}).get('severity', 'medium')
        multiplier = cls.SEVERITY_MULTIPLIERS.get(severity, 1.0)
        
        return min(1.0, confidence * multiplier)
    
    @classmethod
    def get_all_patterns(cls) -> List[Dict]:
        """Get all known patterns."""
        patterns = []
        
        for issue_type, fix_info in cls.FIX_COMMANDS.items():
            patterns.append({
                'issue_type': issue_type,
                'description': fix_info['description'],
                'command': fix_info['command'],
                'severity': fix_info['severity'],
                'success_rate': cls.FIX_SUCCESS_RATES.get(fix_info['command'].split()[-1], 0.7)
            })
        
        return patterns