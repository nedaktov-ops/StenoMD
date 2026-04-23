#!/usr/bin/env python3
"""
StenoMD Date Normalizer
Standardizes dates from CDEP and Senate sources to ISO format
"""

import re
from datetime import datetime
from typing import Optional, Dict


class DateNormalizer:
    """Normalize dates to ISO 8601 format."""
    
    MONTHS_RO = {
        'ianuarie': '01', 'ian': '01',
        'februarie': '02', 'feb': '02',
        'martie': '03', 'mar': '03',
        'aprilie': '04', 'apr': '04',
        'mai': '05',
        'iunie': '06', 'iun': '06',
        'iulie': '07', 'iul': '07',
        'august': '08', 'aug': '08',
        'septembrie': '09', 'sep': '09',
        'octombrie': '10', 'oct': '10',
        'noiembrie': '11', 'noi': '11',
        'decembrie': '12', 'dec': '12',
    }
    
    DISPLAY_FORMATS = {
        'senate': '{day} {month_ro} {year}',
        'deputies': '{day} {month_ro} {year}',
    }
    
    def __init__(self):
        self.recent_date = datetime.now()
    
    def parse(self, date_str: str) -> Optional[str]:
        """
        Parse various date formats to ISO 8601 (YYYY-MM-DD).
        
        Supported formats:
        - YYYY-MM-DD (already ISO)
        - DD.MM.YYYY (European)
        - "1 aprilie 2026" (Romanian)
        - "1 apr. 2026" (Romanian short)
        """
        if not date_str:
            return None
            
        date_str = date_str.strip()
        
        # Already ISO
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
        
        # DD.MM.YYYY or DD-MM-YYYY
        match = re.match(r'^(\d{1,2})[-.](\d{1,2})[-.](\d{4})$', date_str)
        if match:
            day, month, year = match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Romanian format: "1 aprilie 2026"
        match = re.match(r'^(\d{1,2})\s+(\w+)\s+(\d{4})$', date_str, re.I)
        if match:
            day, month_name, year = match.groups()
            month = self._parse_month(month_name)
            if month:
                return f"{year}-{month}-{day.zfill(2)}"
        
        return None
    
    def to_display(self, iso_date: str, chamber: str = 'senate') -> str:
        """Convert ISO date to Romanian display format."""
        if not iso_date:
            return ''
            
        parts = iso_date.split('-')
        if len(parts) != 3:
            return iso_date
            
        year, month, day = parts
        month_ro = self._get_month_name(month)
        
        return f"{int(day)} {month_ro} {year}"
    
    def _parse_month(self, month_name: str) -> Optional[str]:
        """Convert Romanian month name to number."""
        month_lower = month_name.lower().rstrip('.')
        return self.MONTHS_RO.get(month_lower)
    
    def _get_month_name(self, month_num: str) -> str:
        """Convert month number to Romanian name."""
        months = {
            '01': 'ianuarie', '02': 'februarie', '03': 'martie',
            '04': 'aprilie', '05': 'mai', '06': 'iunie',
            '07': 'iulie', '08': 'august', '09': 'septembrie',
            '10': 'octombrie', '11': 'noiembrie', '12': 'decembrie',
        }
        return months.get(month_num, month_num)
    
    def extract_from_title(self, title: str) -> Optional[str]:
        """Extract date from session title."""
        patterns = [
            r'din\s+(\d{1,2})\s+(\w+)\s+(\d{4})',
            r'din\s+(\d{1,2})[-.](\d{1,2})[-.](\d{4})',
            r'(\d{4})-(\d{2})-(\d{2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.I)
            if match:
                if len(match.groups()) == 3:
                    g = match.groups()
                    if len(g[0]) == 4:  # YYYY-MM-DD
                        return f"{g[0]}-{g[1]}-{g[2]}"
                    else:
                        day, month_name, year = g
                        month = self._parse_month(month_name)
                        if month:
                            return f"{year}-{month}-{day.zfill(2)}"
        
        return None
    
    def validate(self, iso_date: str) -> bool:
        """Validate ISO date is real."""
        try:
            datetime.strptime(iso_date, '%Y-%m-%d')
            return True
        except ValueError:
            return False


def normalize_date(date_str: str) -> Optional[str]:
    """Standalone function for date normalization."""
    normalizer = DateNormalizer()
    return normalizer.parse(date_str)


def normalize_date_display(iso_date: str, chamber: str = 'senate') -> str:
    """Standalone function for display format."""
    normalizer = DateNormalizer()
    return normalizer.to_display(iso_date, chamber)


if __name__ == '__main__':
    normalizer = DateNormalizer()
    
    test_dates = [
        '2026-04-01',
        '01.04.2026',
        '01-04-2026',
        '1 aprilie 2026',
        '30 martie 2026',
        '2026-03-25',
    ]
    
    print("=== Date Normalizer Tests ===")
    for date in test_dates:
        iso = normalizer.parse(date)
        display = normalizer.to_display(iso) if iso else 'INVALID'
        print(f"{date:20} -> {iso or 'FAILED':12} -> {display}")