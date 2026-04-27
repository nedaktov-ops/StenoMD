#!/usr/bin/env python3
"""Create a new vault note with proper frontmatter."""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT = Path(__file__).parent.parent
VAULT = PROJECT / "vault"

def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    import re
    text = text.strip().lower()
    text = re.sub(r'[^a-z0-9\-]+', '-', text)
    return text.strip('-')

def create_deputy(name: str):
    slug = slugify(name)
    filename = f"{slug}.md"
    dir_path = VAULT / "politicians" / "deputies"
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / filename
    if file_path.exists():
        print(f"Error: {file_path} already exists")
        sys.exit(1)
    import yaml
    frontmatter = {
        "name": name,
        "type": "deputy",
        "chamber": "Chamber of Deputies",
        "legislature": "2024-2028",
        "source": "cdep.ro",
        "stable_id": "",
        "idm": "",
        "party": "Unknown",
        "constituency": "",
        "speeches_count": 0,
        "laws_proposed": 0,
        "committees": []
    }
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("---\n")
        yaml.safe_dump(frontmatter, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        f.write("---\n\n")
    print(f"Created deputy note: {file_path}")

def create_senator(name: str):
    slug = slugify(name)
    filename = f"{slug}.md"
    dir_path = VAULT / "politicians" / "senators"
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / filename
    if file_path.exists():
        print(f"Error: {file_path} already exists")
        sys.exit(1)
    import yaml
    frontmatter = {
        "name": name,
        "type": "senator",
        "chamber": "Senate",
        "legislature": "2024-2028",
        "source": "senat.ro",
        "stable_id": "",
        "idm": "",
        "party": "Unknown",
        "constituency": "",
        "speeches_count": 0,
        "laws_proposed": 0,
        "committees": []
    }
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("---\n")
        yaml.safe_dump(frontmatter, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        f.write("---\n\n")
    print(f"Created senator note: {file_path}")

def create_law(number: str, title: str):
    slug = slugify(number)
    filename = f"{slug}.md"
    dir_path = VAULT / "laws"
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / filename
    if file_path.exists():
        print(f"Error: {file_path} already exists")
        sys.exit(1)
    import yaml
    frontmatter = {
        "law_number": number,
        "title": title,
        "type": "law",
        "chamber": "",
        "sponsors": [],
        "process_stage": ""
    }
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("---\n")
        yaml.safe_dump(frontmatter, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        f.write("---\n\n")
    print(f"Created law note: {file_path}")

def create_session(date_str: str, chamber: str = "deputies"):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print("Error: date must be in YYYY-MM-DD format")
        sys.exit(1)
    slug = f"session-{date_str}"
    filename = f"{slug}.md"
    dir_path = VAULT / "sessions" / chamber
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / filename
    if file_path.exists():
        print(f"Error: {file_path} already exists")
        sys.exit(1)
    import yaml
    frontmatter = {
        "date": date_str,
        "chamber": chamber,
        "type": "session",
        "deputy_count": 0,
        "speech_count": 0
    }
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("---\n")
        yaml.safe_dump(frontmatter, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        f.write("---\n\n")
    print(f"Created {chamber} session note: {file_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["deputy","senator","law","session"], required=True)
    parser.add_argument("--name", help="Name for deputy/senator")
    parser.add_argument("--number", help="Law number (e.g., 20/2026)")
    parser.add_argument("--title", help="Title for law")
    parser.add_argument("--date", help="Date for session (YYYY-MM-DD)")
    parser.add_argument("--chamber", default="deputies", choices=["deputies","senate"], help="Chamber for session")
    args = parser.parse_args()

    if args.type in ("deputy","senator") and not args.name:
        parser.error(f"--name required for {args.type}")
    if args.type == "law":
        if not args.number or not args.title:
            parser.error("--number and --title required for law")
    if args.type == "session":
        if not args.date:
            parser.error("--date required for session")

    if args.type == "deputy":
        create_deputy(args.name)
    elif args.type == "senator":
        create_senator(args.name)
    elif args.type == "law":
        create_law(args.number, args.title)
    elif args.type == "session":
        create_session(args.date, args.chamber)

if __name__ == "__main__":
    main()
