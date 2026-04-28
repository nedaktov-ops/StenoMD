#!/usr/bin/env python3
"""
Repomix Wrapper for StenoMD

Generates a single AI‑friendly file packing the most important parts
of the project (scripts, vault, knowledge graph). Uses Repomix
(https://github.com/yamadashy/repomix) to produce a token‑optimized
representation suitable for LLM context.

Usage:
    python3 scripts/repomix_wrapper.py [--output OUTPUT] [--compress]

Requires: repomix (install with: npm install -g repomix)
"""

import subprocess
import sys
from pathlib import Path


DEFAULT_INCLUDE = [
    "scripts/**",
    "vault/**",
    "knowledge_graph/**",
    "docs/**",
]
DEFAULT_EXCLUDE = [
    "**/__pycache__/**",
    "**/.pytest_cache/**",
    "**/node_modules/**",
    "**/.venv/**",
    "**/.git/**",
    "**/*.pyc",
    "**/coverage.xml",
    "**/.coverage",
    "knowledge_graph/*.db",
    "vault/_brain/**/*.json",  # large logs
    "data/**",  # raw scraped data can be huge
]


def run_repomix(output_path: Path, compress: bool = False) -> int:
    """Invoke repomix with the given options."""
    cmd = ["repomix", "--output", str(output_path)]
    for pattern in DEFAULT_INCLUDE:
        cmd.extend(["--include", pattern])
    for pattern in DEFAULT_EXCLUDE:
        cmd.extend(["--exclude", pattern])
    if compress:
        cmd.append("--compress")
    
    print(f"[Repomix] Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            print(f"[Repomix] Output written to: {output_path}")
            # Print token count if possible (repomix prints to stdout)
            # Optionally parse output for token count
        return result.returncode
    except FileNotFoundError:
        print("[Repomix] Error: 'repomix' command not found.")
        print("  Install with: npm install -g repomix")
        return 1


def main():
    import argparse
    parser = argparse.ArgumentParser(description="StenoMD Repomix Wrapper")
    parser.add_argument("--output", default="ai_context/stenomix_context.xml",
                        help="Output file path (default: ai_context/stenomix_context.xml)")
    parser.add_argument("--compress", action="store_true",
                        help="Use Tree-sitter compression to reduce token count")
    parser.add_argument("--no-compress", action="store_false", dest="compress",
                        help="Disable compression (default)")
    parser.set_defaults(compress=False)
    args = parser.parse_args()
    
    output_path = Path(args.output)
    return run_repomix(output_path, args.compress)


if __name__ == "__main__":
    sys.exit(main())
