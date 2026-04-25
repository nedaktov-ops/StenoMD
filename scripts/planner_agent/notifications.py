"""Notification Service - Send alerts on critical issues."""
import sys
from datetime import datetime
from typing import Dict, Optional


class NotificationService:
    """Send alerts on critical issues."""
    
    LEVELS = {
        'DEBUG': 0,
        'INFO': 1,
        'WARNING': 2,
        'ERROR': 3,
        'CRITICAL': 4
    }
    
    def __init__(self, min_level: str = 'WARNING'):
        self.min_level = self.LEVELS.get(min_level, 1)
        self.log = []
        
    def _format_message(self, level: str, message: str, context: Dict) -> str:
        """Format notification message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] {level}: {message}"
    
    def notify(self, level: str, message: str, context: Optional[Dict] = None):
        """Send notification."""
        if self.LEVELS.get(level, 0) < self.min_level:
            return
        
        formatted = self._format_message(level, message, context or {})
        
        # Log to history
        self.log.append({
            'level': level,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'context': context
        })
        
        # Output based on level
        if level in ['ERROR', 'CRITICAL']:
            print(formatted, file=sys.stderr)
        else:
            print(formatted)
    
    def debug(self, message: str, context: Optional[Dict] = None):
        self.notify('DEBUG', message, context)
    
    def info(self, message: str, context: Optional[Dict] = None):
        self.notify('INFO', message, context)
    
    def warning(self, message: str, context: Optional[Dict] = None):
        self.notify('WARNING', message, context)
    
    def error(self, message: str, context: Optional[Dict] = None):
        self.notify('ERROR', message, context)
    
    def critical(self, message: str, context: Optional[Dict] = None):
        self.notify('CRITICAL', message, context)
    
    def get_history(self) -> list:
        """Get notification history."""
        return self.log
    
    def clear_history(self):
        """Clear notification history."""
        self.log = []


# Default instance
notifications = NotificationService()


if __name__ == "__main__":
    # Test notifications
    notifier = NotificationService()
    
    notifier.info("Project analysis started")
    notifier.warning("Limited historical data detected", {'years': '1996-2014'})
    notifier.error("Import path issue found", {'file': 'agents/__init__.py'})
    notifier.critical("Critical error in scraping", {'session': '2024-01-15'})
    
    print(f"\nSent {len(notifier.get_history())} notifications")