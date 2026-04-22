#!/usr/bin/env python3
"""Fetch stenograms from Monitorul Oficial"""

import os
import requests
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD/data")
STENOGRAM_BASE_URL = "https://monitoruloficial.md"

def get_date_range():
    """Get date range for fetching (last 7 days)."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return start_date, end_date

def fetch_stenogram(date):
    """Fetch stenogram for a specific date."""
    date_str = date.strftime("%Y-%m-%d")
    filename = f"stenogram_{date_str}.html"
    output_path = DATA_DIR / filename
    
    if output_path.exists():
        print(f"Already exists: {filename}")
        return
    
    print(f"Fetching: {filename}")
    
    try:
        response = requests.get(f"{STENOGRAM_BASE_URL}/api/v2/stenogram/{date_str}", timeout=10)
        
        if response.status_code == 200:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"Saved: {filename}")
        else:
            print(f"Not found: {date_str} (status {response.status_code})")
    except Exception as e:
        print(f"Network error fetching {date_str}: {e}")
        print("Note: Configure STENOGRAM_BASE_URL or add stenogram files manually to data/")

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    start_date, end_date = get_date_range()
    
    current = start_date
    while current <= end_date:
        fetch_stenogram(current)
        current += timedelta(days=1)
    
    print("Fetch complete.")

if __name__ == "__main__":
    main()