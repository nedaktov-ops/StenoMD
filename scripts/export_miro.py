#!/usr/bin/env python3
"""
Export StenoMD Knowledge Graph to Miro‑compatible CSV files.

Creates three CSV decks: politicians, sessions, laws.
Each row becomes a card in Miro. Use Miro's CSV import feature
to bring these into a board.

Usage:
    python3 scripts/export_miro.py --outdir miro_export
"""

import csv
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any


def export_persons(persons: List[Dict], out_path: Path):
    """Export politicians as CSV."""
    headers = [
        "ID", "Name", "Chamber", "Party", "Speeches Count",
        "Laws Proposed", "Committees", "Appearances Count", "Source"
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for p in persons:
            metadata = p.get("metadata", {})
            party = metadata.get("party", "")
            if isinstance(party, dict):
                party = party.get("name", "")
            committees = []
            if isinstance(metadata.get("committees"), list):
                for c in metadata["committees"]:
                    if isinstance(c, dict):
                        committees.append(c.get("name", ""))
                    else:
                        committees.append(str(c))
            committees_str = "; ".join(committees)
            writer.writerow({
                "ID": p.get("id", ""),
                "Name": p.get("name", ""),
                "Chamber": p.get("chamber", ""),
                "Party": party,
                "Speeches Count": metadata.get("speeches_count", ""),
                "Laws Proposed": metadata.get("laws_proposed", ""),
                "Committees": committees_str,
                "Appearances Count": len(p.get("appearances", [])),
                "Source": p.get("source", "")
            })


def export_sessions(sessions: List[Dict], out_path: Path):
    """Export parliamentary sessions as CSV."""
    headers = [
        "ID", "Date", "Chamber", "Title", "Deputy Count",
        "Participants Count", "URL", "Source"
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for s in sessions:
            participants = s.get("participants", [])
            writer.writerow({
                "ID": s.get("id", ""),
                "Date": s.get("date", ""),
                "Chamber": s.get("chamber", ""),
                "Title": s.get("title", ""),
                "Deputy Count": s.get("deputy_count", len(participants)),
                "Participants Count": len(participants),
                "URL": s.get("url", ""),
                "Source": s.get("source", "")
            })


def export_laws(laws: List[Dict], out_path: Path):
    """Export laws/proposals as CSV."""
    headers = [
        "Number", "Title", "Chamber", "Sponsors Count", "Source"
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for law in laws:
            writer.writerow({
                "Number": law.get("number", ""),
                "Title": law.get("title", ""),
                "Chamber": law.get("chamber", ""),
                "Sponsors Count": len(law.get("sponsors", [])) if isinstance(law.get("sponsors"), list) else "",
                "Source": law.get("source", "")
            })


def main():
    parser = argparse.ArgumentParser(description="Export KG to Miro‑compatible CSVs")
    parser.add_argument("--outdir", default="miro_export",
                        help="Output directory (default: miro_export)")
    parser.add_argument("--entities", default="knowledge_graph/entities.json",
                        help="Path to entities.json")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    with open(args.entities, "r", encoding="utf-8") as f:
        kg = json.load(f)

    persons = kg.get("persons", [])
    sessions = kg.get("sessions", [])
    laws = kg.get("laws", [])

    export_persons(persons, outdir / "politicians.csv")
    export_sessions(sessions, outdir / "sessions.csv")
    export_laws(laws, outdir / "laws.csv")

    print(f"Exported: {len(persons)} persons, {len(sessions)} sessions, {len(laws)} laws")
    print(f"Files written to: {outdir.resolve()}")


if __name__ == "__main__":
    main()
