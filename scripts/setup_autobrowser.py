#!/usr/bin/env python3
"""
Auto-Browser Setup Script

Usage:
    python3 scripts/setup_autobrowser.py --install    # Clone and setup
    python3 scripts/setup_autobrowser.py --start    # Start services
    python3 scripts/setup_autobrowser.py --stop     # Stop services
    python3 scripts/setup_autobrowser.py --status  # Check status
"""

import subprocess
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
AUTO_BROWSER_DIR = PROJECT_ROOT / "auto-browser"


def install():
    """Clone Auto-Browser repository."""
    if AUTO_BROWSER_DIR.exists():
        print("Auto-Browser already exists at auto-browser/")
        print("To update: cd auto-browser && git pull")
        return
    
    result = subprocess.run([
        "git", "clone", 
        "https://github.com/LvcidPsyche/auto-browser.git",
        str(AUTO_BROWSER_DIR)
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Cloned to {AUTO_BROWSER_DIR}")
    else:
        print(f"❌ Error: {result.stderr}")


def start():
    """Start Auto-Browser services."""
    if not AUTO_BROWSER_DIR.exists():
        print("Auto-Browser not installed. Run --install first.")
        return False
    
    print("Starting Auto-Browser services...")
    result = subprocess.run(
        ["docker", "compose", "up", "-d"],
        cwd=AUTO_BROWSER_DIR,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Services started")
        print("  API: http://127.0.0.1:8000/docs")
        print("  Dashboard: http://127.0.0.1:8000/dashboard")
        print("  noVNC: http://127.0.0.1:6080/vnc.html")
        return True
    else:
        print(f"❌ Error: {result.stderr}")
        return False


def stop():
    """Stop Auto-Browser services."""
    if not AUTO_BROWSER_DIR.exists():
        return False
    
    result = subprocess.run(
        ["docker", "compose", "down"],
        cwd=AUTO_BROWSER_DIR,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Services stopped")
        return True
    else:
        print(f"❌ Error: {result.stderr}")
        return False


def status():
    """Check Auto-Browser status."""
    result = subprocess.run(
        ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}", "--filter", "name=auto-browser"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        output = result.stdout.strip()
        if output:
            print("Auto-Browser Containers:")
            print(output)
        else:
            print("No containers running")
        return True
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-Browser Setup")
    parser.add_argument("--install", action="store_true", help="Clone Auto-Browser")
    parser.add_argument("--start", action="store_true", help="Start services")
    parser.add_argument("--stop", action="store_true", help="Stop services")
    parser.add_argument("--status", action="store_true", help="Check status")
    
    args = parser.parse_args()
    
    if args.install:
        install()
    elif args.start:
        start()
    elif args.stop:
        stop()
    elif args.status:
        status()
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python3 scripts/setup_autobrowser.py --install")
        print("  python3 scripts/setup_autobrowser.py --start")
        print("  python3 scripts/setup_autobrowser.py --status")