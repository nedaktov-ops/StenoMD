#!/usr/bin/env python3
"""
GraphifyStenoMD Validator Agent
Validates data consistency across vault and graph.

Usage:
    python3 agents/validator_agent.py --check all
    python3 agents/validator_agent.py --check linked
    python3 agents/validator_agent.py --check yaml
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

# Add project scripts to path for centralized config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

try:
    from config import get_config
    config = get_config()
    PROJECT_DIR = config.PROJECT_ROOT
    VAULT_DIR = config.VAULT_DIR
    KG_DIR = config.KG_DIR
    ENTITIES_FILE = config.ENTITIES_FILE
except ImportError:
    PROJECT_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
    VAULT_DIR = PROJECT_DIR / "vault"
    KG_DIR = PROJECT_DIR / "knowledge_graph"
    ENTITIES_FILE = KG_DIR / "entities.json"

GRAPH_FILE = PROJECT_DIR / "Graphify" / "graphify-out" / "graph.json"

class ValidatorAgent:
    def __init__(self):
        self.graph_data = None
        self.load_graph()
    
    def load_graph(self):
        """Load existing graph."""
        if GRAPH_FILE.exists():
            with open(GRAPH_FILE) as f:
                self.graph_data = json.load(f)
            print(f"Loaded graph: {len(self.graph_data.get('nodes', []))} nodes")
        else:
            print("No graph found")
            self.graph_data = {"nodes": [], "links": []}
    
    def validate_links(self):
        """Validate wikilinks in vault."""
        issues = {
            "broken_links": [],
            "missing_targets": [],
            "circular_links": [],
        }
        
        # Check politician files for broken links
        pol_dir = VAULT_DIR / "politicians"
        if pol_dir.exists():
            for md_file in pol_dir.rglob("*.md"):
                content = md_file.read_text()
                # Find wikilinks [[...]]
                links = re.findall(r'\[\[([^\]]+)\]\]', content)
                for link in links:
                    # Check if link target exists
                    target_path = self.resolve_wikilink(link, md_file.parent)
                    if target_path and not target_path.exists():
                        issues["broken_links"].append({
                            "file": str(md_file.relative_to(VAULT_DIR)),
                            "link": link
                        })
        
        return issues
    
    def resolve_wikilink(self, link, base_dir):
        """Resolve wikilink to file path."""
        # Simple resolution
        link = link.strip()
        
        # Handle pipes in links: [[target|Display]]
        if "|" in link:
            link = link.split("|")[0]
        
        # Try various extensions
        for ext in ["", ".md"]:
            path = base_dir / f"{link}{ext}"
            if path.exists():
                return path
            
            # Try relative to vault root
            path = VAULT_DIR / f"{link}{ext}"
            if path.exists():
                return path
        
        return None
    
    def validate_yaml(self):
        """Validate YAML frontmatter."""
        issues = {
            "missing_frontmatter": [],
            "invalid_yaml": [],
            "missing_required": [],
        }
        
        required_fields = {
            "politicians": ["stable_id", "type", "party"],
            "sessions": ["date", "chamber"],
            "laws": ["law_number", "title", "year"],
        }
        
        for category, fields in required_fields.items():
            cat_dir = VAULT_DIR / category
            if not cat_dir.exists():
                continue
            
            for md_file in cat_dir.rglob("*.md"):
                content = md_file.read_text()
                
                # Check for frontmatter
                if not content.startswith("---"):
                    issues["missing_frontmatter"].append(str(md_file.relative_to(VAULT_DIR)))
                    continue
                
                # Try to parse frontmatter
                try:
                    import yaml
                    # Simple frontmatter extraction
                    fm_match = re.match(r'^---\n(.+?)\n---', content, re.DOTALL)
                    if fm_match:
                        fm = yaml.safe_load(fm_match.group(1))
                        if not fm:
                            issues["invalid_yaml"].append(str(md_file.relative_to(VAULT_DIR)))
                        else:
                            # Check required fields
                            for field in fields:
                                if field not in fm:
                                    issues["missing_required"].append({
                                        "file": str(md_file.relative_to(VAULT_DIR)),
                                        "field": field
                                    })
                except Exception as e:
                    issues["invalid_yaml"].append(str(md_file.relative_to(VAULT_DIR)))
        
        return issues
    
    def validate_duplicates(self):
        """Check for duplicate IDs."""
        issues = {
            "duplicate_stable_id": [],
            "duplicate_idm": [],
        }
        
        stable_ids = defaultdict(list)
        idms = defaultdict(list)
        
        pol_dir = VAULT_DIR / "politicians"
        if pol_dir.exists():
            for md_file in pol_dir.rglob("*.md"):
                content = md_file.read_text()
                
                # Extract stable_id
                match = re.search(r'stable_id:\s*(\S+)', content)
                if match:
                    stable_ids[match.group(1)].append(str(md_file.relative_to(VAULT_DIR)))
                
                # Extract idm
                match = re.search(r'idm:\s*(\S+)', content)
                if match:
                    idms[match.group(1)].append(str(md_file.relative_to(VAULT_DIR)))
        
        # Find duplicates
        for sid, files in stable_ids.items():
            if len(files) > 1:
                issues["duplicate_stable_id"].append({"id": sid, "files": files})
        
        for idm_val, files in idms.items():
            if len(files) > 1:
                issues["duplicate_idm"].append({"id": idm_val, "files": files})
        
        return issues
    
    def validate_graph(self):
        """Validate graph structure."""
        issues = {
            "orphaned_nodes": [],
            "invalid_edges": [],
            "self_loops": [],
        }
        
        node_ids = {n["id"] for n in self.graph_data.get("nodes", [])}
        
        for edge in self.graph_data.get("links", []):
            src = edge.get("source")
            tgt = edge.get("target")
            
            # Check for self-loops
            if src == tgt:
                issues["self_loops"].append(src)
                continue
            
            # Check for invalid edges
            if src not in node_ids:
                issues["invalid_edges"].append(f"Missing source: {src}")
            if tgt not in node_ids:
                issues["invalid_edges"].append(f"Missing target: {tgt}")
        
        # Find orphaned nodes (degree = 0)
        degrees = defaultdict(int)
        for edge in self.graph_data.get("links", []):
            degrees[edge.get("source")] += 1
            degrees[edge.get("target")] += 1
        
        for node in self.graph_data.get("nodes", []):
            if degrees.get(node["id"], 0) == 0:
                issues["orphaned_nodes"].append(node.get("label"))
        
        return issues
    
    def run(self, check_type="all"):
        """Run validation."""
        print(f"\n=== Validation: {check_type} ===")
        
        results = {}
        
        if check_type in ["all", "links"]:
            print("\n--- Checking Links ---")
            results["links"] = self.validate_links()
            print(f"Broken links: {len(results['links']['broken_links'])}")
        
        if check_type in ["all", "yaml"]:
            print("\n--- Checking YAML ---")
            results["yaml"] = self.validate_yaml()
            print(f"Missing frontmatter: {len(results['yaml']['missing_frontmatter'])}")
            print(f"Invalid: {len(results['yaml']['invalid_yaml'])}")
            print(f"Missing fields: {len(results['yaml']['missing_required'])}")
        
        if check_type in ["all", "duplicates"]:
            print("\n--- Checking Duplicates ---")
            results["duplicates"] = self.validate_duplicates()
            print(f"Duplicate stable_id: {len(results['duplicates']['duplicate_stable_id'])}")
            print(f"Duplicate idm: {len(results['duplicates']['duplicate_idm'])}")
        
        if check_type in ["all", "graph"]:
            print("\n--- Checking Graph ---")
            results["graph"] = self.validate_graph()
            print(f"Orphaned nodes: {len(results['graph']['orphaned_nodes'])}")
            print(f"Self-loops: {len(results['graph']['self_loops'])}")
        
        # Summary
        print("\n=== Summary ===")
        total_issues = sum(len(v) for r in results.values() for v in r.values() if isinstance(v, list))
        print(f"Total issues: {total_issues}")
        
        return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validator agent")
    parser.add_argument("--check", choices=["all", "links", "yaml", "duplicates", "graph"], default="all", help="Check type")
    
    args = parser.parse_args()
    
    agent = ValidatorAgent()
    agent.run(args.check)


if __name__ == "__main__":
    main()