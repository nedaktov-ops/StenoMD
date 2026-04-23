#!/usr/bin/env python3
"""
StenoMD Planner Agent
Analyzes project, researches best practices, writes strategies.

Modes:
    --auto   : Run after each action (post-hook)
    --manual : Run on-demand
    --schedule: Run daily schedule
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import argparse

PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
STRATEGY_FILE = PROJECT_DIR / "STRATEGY.md"


class PlannerAgent:
    def __init__(self):
        self.project_dir = PROJECT_DIR
        self.strategy_file = STRATEGY_FILE
        
    def git_status(self):
        """Get git status."""
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip() or "clean"
        except Exception as e:
            return f"error: {e}"
    
    def vault_counts(self):
        """Count vault files."""
        counts = {}
        for chamber in ["senators", "deputies"]:
            politicians_dir = self.project_dir / "vault" / "politicians" / chamber
            sessions_dir = self.project_dir / "vault" / "sessions" / chamber
            
            counts[f"politicians_{chamber}"] = len(list(politicians_dir.glob("*.md"))) if politicians_dir.exists() else 0
            counts[f"sessions_{chamber}"] = len(list(sessions_dir.glob("*.md"))) if sessions_dir.exists() else 0
        
        return counts
    
    def check_errors(self):
        """Check for common errors."""
        errors = []
        
        # Check git uncommitted changes
        status = self.git_status()
        if status != "clean":
            errors.append(f"Uncommitted changes: {status[:100]}")
        
        # Check for empty files
        for md in (self.project_dir / "vault").rglob("*.md"):
            if md.stat().st_size == 0:
                errors.append(f"Empty file: {md.relative_to(self.project_dir)}")
        
        # Check Python syntax errors
        for py in (self.project_dir / "scripts").glob("*.py"):
            try:
                result = subprocess.run(
                    ["python3", "-m", "py_compile", str(py)],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode != 0:
                    errors.append(f"Syntax error in: {py.name}")
            except:
                pass
        
        return errors
    
    def analyze_project(self):
        """Run diagnostics and collect status."""
        vault = self.vault_counts()
        git = self.git_status()
        errors = self.check_errors()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "vault": vault,
            "git_status": git,
            "errors": errors,
            "has_issues": len(errors) > 0
        }
    
    def check_dashboard(self):
        """Check if dashboard is running."""
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:8080/api/stats"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() == "200"
        except:
            return False
    
    def research_best_practices(self, topic):
        """Search for best practices (placeholder - returns search URL)."""
        queries = {
            "python web scraping": "https://www.scrapingbee.com/blog/how-to-scrape-any-website/",
            "parliament data": "https://github.com/topics/parliament-data",
            "obsidian automation": "https://help.obsidian.md/Plugins/Dataview",
            "fastapi best practices": "https://fastapi.tiangolo.com/best-practices/",
        }
        return queries.get(topic, f"Search for: {topic}")
    
    def run(self, mode="manual"):
        """Main entry point."""
        print(f"[PLANNER] Running in {mode} mode...")
        
        status = self.analyze_project()
        
        if mode == "manual":
            print("\n=== PROJECT STATUS ===")
            print(f"Timestamp: {status['timestamp']}")
            print(f"Vault: {status['vault']}")
            print(f"Git: {status['git_status']}")
            print(f"Has Issues: {status['has_issues']}")
            if status['errors']:
                print("\nErrors Found:")
                for err in status['errors']:
                    print(f"  - {err}")
            
            dashboard = self.check_dashboard()
            print(f"\nDashboard Running: {dashboard}")
            
            return status
        
        elif mode == "auto":
            if status['has_issues']:
                print(f"[PLANNER] Issues found! Writing strategy...")
                self.write_strategy(status)
            else:
                print("[PLANNER] No issues found. Project healthy.")
            return status
        
        elif mode == "schedule":
            print(f"[PLANNER] Daily check: {status['timestamp']}")
            if status['has_issues']:
                self.write_strategy(status)
            print("[PLANNER] Daily check complete.")
            return status
    
    def write_strategy(self, status):
        """Write improvement strategy to STRATEGY.md."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        content = f"""# StenoMD Strategy - Auto-generated by Planner Agent

**Generated:** {timestamp}
**Mode:** {status.get('mode', 'manual')}

---

## Project Status

```
{json.dumps(status['vault'], indent=2)}
```

## Git Status
```
{status['git_status']}
```

## Issues Found

{chr(10).join(f"- {e}" for e in status['errors']) if status['errors'] else "None"}

## Recommended Improvements

Based on analysis:

1. **High Priority** - Fix any errors found
2. **Medium Priority** - Scale up data collection (2020-2026)
3. **Low Priority** - Enhance dashboard features

## Research References

- Python Scraping: {self.research_best_practices('python web scraping')}
- Obsidian: {self.research_best_practices('obsidian automation')}
- FastAPI: {self.research_best_practices('fastapi best practices')}

---

*Auto-generated by Planner Agent*
"""
        # Read existing content
        existing = self.strategy_file.read_text() if self.strategy_file.exists() else ""
        
        # Prepend new content
        self.strategy_file.write_text(content + "\n\n---\n\n" + existing)
        print(f"[PLANNER] Strategy written to {self.strategy_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StenoMD Planner Agent")
    parser.add_argument("--auto", action="store_true", help="Run as post-action hook")
    parser.add_argument("--manual", action="store_true", help="Run on-demand")
    parser.add_argument("--schedule", action="store_true", help="Run daily schedule")
    args = parser.parse_args()
    
    mode = "manual"
    if args.auto:
        mode = "auto"
    elif args.schedule:
        mode = "schedule"
    
    agent = PlannerAgent()
    agent.run(mode)