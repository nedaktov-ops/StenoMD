#!/usr/bin/env python3
"""
Build a minimal Graphify-compatible graph.json from StenoMD vault.
This extracts frontmatter attributes for gap analysis without requiring full semantic extraction.
"""

import json
import yaml
from pathlib import Path
from datetime import datetime

PROJECT = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
VAULT = PROJECT / "vault"
OUTPUT = PROJECT / "Graphify" / "graphify-out" / "graph.json"

def parse_frontmatter(content):
    """Parse YAML frontmatter."""
    if not content.startswith('---'):
        return {}, content
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    try:
        fm = yaml.safe_load(parts[1])
        return fm or {}, parts[2]
    except:
        return {}, content

def build_graph():
    nodes = []
    links = []
    
    # Process all markdown files in vault
    for md_file in VAULT.rglob("*.md"):
        if md_file.name == "Index.md":
            continue
        rel_path = md_file.relative_to(VAULT).as_posix()
        
        try:
            content = md_file.read_text(encoding='utf-8')
            fm, body = parse_frontmatter(content)
            
            # Determine node type and attributes
            node = {
                "label": md_file.stem,
                "file_type": "markdown",
                "source_file": rel_path,
                "source_location": "L1",
                "id": rel_path.replace('/', '_').replace('.', '_'),
                "community": 0,
                "norm_label": md_file.stem.lower()
            }
            
            # Extract common attributes from frontmatter
            for key in ['type', 'chamber', 'party', 'party_full', 'constituency',
                        'legislature', 'status', 'stable_id', 'idm',
                        'speeches_count', 'laws_proposed', 'committees',
                        'number', 'title', 'sponsors', 'date', 'speech_count',
                        'deputy_count', 'process_stage']:
                if key in fm:
                    node[key] = fm[key]
            
            # Special handling: sessions/deputies vs sessions/senate
            if 'sessions/deputies' in rel_path or 'sessions/senate' in rel_path:
                # Ensure session nodes have date
                if 'date' in fm:
                    node['date'] = fm['date']
                # Set chamber
                if 'deputies' in rel_path:
                    node['chamber'] = 'deputies'
                else:
                    node['chamber'] = 'senate'
            
            # Count links (basic)
            # Links will be added in a separate pass if needed
            
            nodes.append(node)
        except Exception as e:
            print(f"Error processing {rel_path}: {e}")
    
    # Build simple links: use Obsidian-style [[link]] patterns
    # This is optional but adds basic connectivity
    label_to_node = {node['label']: node for node in nodes}
    
    for node in nodes:
        # Look for wikilinks in body
        body_lower = body.lower() if 'body' in locals() else ''
        # Extract [[link]] patterns
        import re
        links_found = re.findall(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', body_lower)
        for link_target, _ in links_found:
            if link_target in label_to_node:
                links.append({
                    "source": node['id'],
                    "target": label_to_node[link_target]['id'],
                    "type": "wiki_link"
                })
    
    graph = {
        "directed": False,
        "multigraph": False,
        "graph": {},
        "nodes": nodes,
        "links": links
    }
    
    # Ensure output directory exists
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    
    # Write
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)
    
    print(f"Graph built: {len(nodes)} nodes, {len(links)} links")
    print(f"Saved to: {OUTPUT}")
    
    # Also generate report
    report = {
        "generated": datetime.now().isoformat(),
        "total_nodes": len(nodes),
        "total_edges": len(links),
        "node_types": {},
        "missing_fields": {}
    }
    
    for node in nodes:
        # Count by source location
        src = node.get('source_file', '')
        if 'politicians/deputies' in src:
            report['node_types']['deputy'] = report['node_types'].get('deputy', 0) + 1
        elif 'politicians/senators' in src:
            report['node_types']['senator'] = report['node_types'].get('senator', 0) + 1
        elif 'laws/' in src:
            report['node_types']['law'] = report['node_types'].get('law', 0) + 1
        elif 'sessions/' in src:
            report['node_types']['session'] = report['node_types'].get('session', 0) + 1
    
    # Check gaps
    total_missing = 0
    for node in nodes:
        if 'politicians/' in node.get('source_file', '') or 'deputies/' in node.get('source_file', ''):
            if not node.get('party'):
                report['missing_fields']['party'] = report['missing_fields'].get('party', 0) + 1
                total_missing += 1
            if not node.get('speeches_count'):
                report['missing_fields']['speeches_count'] = report['missing_fields'].get('speeches_count', 0) + 1
                total_missing += 1
            if not node.get('committees'):
                report['missing_fields']['committees'] = report['missing_fields'].get('committees', 0) + 1
                total_missing += 1
        if 'laws/' in node.get('source_file', '') and not node.get('sponsors'):
            report['missing_fields']['sponsors'] = report['missing_fields'].get('sponsors', 0) + 1
            total_missing += 1
        if 'sessions/' in node.get('source_file', '') and not node.get('deputy_count'):
            report['missing_fields']['deputy_count'] = report['missing_fields'].get('deputy_count', 0) + 1
            total_missing += 1
    
    report['total_missing'] = total_missing
    
    report_file = OUTPUT.parent / "GRAPH_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Graph Report - StenoMD Vault\n\n")
        f.write(f"**Generated:** {report['generated']}\n\n")
        f.write(f"- Total nodes: {report['total_nodes']}\n")
        f.write(f"- Total edges: {report['total_edges']}\n\n")
        f.write("## Node Types\n\n")
        for t, c in report['node_types'].items():
            f.write(f"- {t}: {c}\n")
        f.write("\n## Missing Data\n\n")
        for field, count in report['missing_fields'].items():
            f.write(f"- {field}: {count}\n")
        f.write(f"\n**Total missing data points:** {total_missing}\n")
    
    print(f"Report saved: {report_file}")

if __name__ == "__main__":
    build_graph()
