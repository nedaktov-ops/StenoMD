#!/usr/bin/env python3
"""
Lightweight MemPalace Backend for StenoMD
Stores actions as JSONL lines for future retrieval.
Optional semantic search can be added later (ChromaDB).
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class MemPalaceBackend:
    """Simple file‑based palace for verbatim memory storage."""
    
    def __init__(self, storage_dir: Path):
        self.enabled = True
        self.palace_dir = storage_dir / ".mempalace" / "stenomd"
        self.palace_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.palace_dir / "memories.jsonl"
        print(f"[MemPalace] Initialized at {self.palace_dir}")
    
    def learn(self, action: Dict[str, Any], outcome: Dict[str, Any]) -> str:
        """Append an action outcome to the palace log."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "outcome": outcome
        }
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return "ok"
        except Exception as e:
            print(f"[MemPalace] Learn error: {e}")
            return None
    
    def recall(self, query: str, limit: int = 5) -> List[Dict]:
        """Keyword search over stored memories (case‑insensitive)."""
        results = []
        try:
            if not self.log_path.exists():
                return []
            q = query.lower()
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    # Combine searchable text
                    text = json.dumps(entry, ensure_ascii=False).lower()
                    if q in text:
                        results.append({
                            "id": entry["timestamp"],
                            "timestamp": entry["timestamp"],
                            "text": json.dumps(entry, ensure_ascii=False),
                            "metadata": {
                                "type": entry["action"].get("type", ""),
                                "success": entry["outcome"].get("success", False),
                                "command": entry["action"].get("command", ""),
                            }
                        })
                    if len(results) >= limit:
                        break
        except Exception as e:
            print(f"[MemPalace] Recall error: {e}")
        return results
