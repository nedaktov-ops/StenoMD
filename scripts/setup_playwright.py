#!/usr/bin/env python3
"""
Playwright Fallback Setup - Alternative to Docker-based Auto-Browser

Usage:
    python3 scripts/setup_playwright.py --install    # Install Playwright
    python3 scripts/setup_playwright.py --test     # Test installation
    python3 scripts/setup_playwright.py --scrape URL  # Quick scrape test
"""

import subprocess
import sys
import argparse
from pathlib import Path


def install():
    """Install Playwright and chromium."""
    print("Installing Playwright...")
    
    # Install playwright
    result = subprocess.run([
        sys.executable, "-m", "pip", "install", "playwright"
    ], capture_output=True)
    
    if result.returncode != 0:
        print(f"❌ Install failed: {result.stderr.decode()}")
        return False
    
    # Install chromium
    result = subprocess.run([
        "playwright", "install", "chromium"
    ], capture_output=True)
    
    if result.returncode != 0:
        print(f"❌ Chromium install failed: {result.stderr.decode()}")
        return False
    
    print("✅ Playwright installed successfully")
    return True


def test():
    """Test Playwright installation."""
    test_code = '''
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com")
    print(f"Title: {page.title()}")
    browser.close()
'''
    result = subprocess.run([sys.executable, "-c", test_code], capture_output=True)
    
    if result.returncode == 0:
        print(f"✅ {result.stdout.decode().strip()}")
        return True
    else:
        print(f"❌ Test failed: {result.stderr.decode()}")
        return False


def scrape(url: str):
    """Quick scrape test."""
    code = f'''
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("{url}")
    print(f"Title: {{page.title()}}")
    print(f"Content length: {{len(page.content())}}")
    browser.close()
'''
    result = subprocess.run([sys.executable, "-c", code], capture_output=True)
    
    if result.returncode == 0:
        print(result.stdout.decode().strip())
        return True
    else:
        print(f"❌ Failed: {result.stderr.decode()}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Playwright Fallback")
    parser.add_argument("--install", action="store_true", help="Install Playwright")
    parser.add_argument("--test", action="store_true", help="Test installation")
    parser.add_argument("--scrape", type=str, help="Quick scrape URL")
    
    args = parser.parse_args()
    
    if args.install:
        install()
    elif args.test:
        test()
    elif args.scrape:
        scrape(args.scrape)
    else:
        parser.print_help()