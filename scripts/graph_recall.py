#!/usr/bin/env python3
"""
Reverse Linking System - Graph Traversal for Vault

Given any item (deputy, law, session), trace ALL connections:
- What items link TO it (inlinks)?
- What items link FROM it (outlinks)?
- Full connection path tracing

This provides the "reverse engineering" ability to understand
how any item in the vault connects to everything else.
"""

import re
from pathlib import Path
from collections import defaultdict

VAULT_DIR = Path("vault")

def extract_wiki_links(content):
    """Extract all [[wiki-style links]] from content."""
    return re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)

def extract_field(content, field_name):
    """Extract field from frontmatter."""
    pattern = rf'^{field_name}:\s*(.+)$'
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else None

def get_file_type(filepath):
    """Determine file type from path."""
    if '/deputies/' in str(filepath):
        return 'deputy'
    elif '/senators/' in str(filepath):
        return 'senator'
    elif '/laws/' in str(filepath):
        return 'law'
    elif '/sessions/' in str(filepath):
        return 'session'
    elif '/committees/' in str(filepath):
        return 'committee'
    return 'unknown'

def build_link_graph():
    """Build complete link graph from vault."""
    graph = {
        'outlinks': defaultdict(set),  # file -> set of files it links to
        'inlinks': defaultdict(set),   # file -> set of files that link to it
        'metadata': {},              # file -> metadata
    }
    
    # Iterate all MD files
    for md_file in VAULT_DIR.rglob("*.md"):
        if md_file.stat().st_size == 0:
            continue
        
        rel_path = str(md_file.relative_to(VAULT_DIR))
        
        try:
            content = md_file.read_text(encoding='utf-8')
        except:
            continue
        
        # Get metadata
        file_type = get_file_type(md_file)
        name = extract_field(content, 'title') or md_file.stem
        idm = extract_field(content, 'idm')
        
        graph['metadata'][rel_path] = {
            'name': name,
            'type': file_type,
            'idm': idm,
        }
        
        # Get links from content
        links = extract_wiki_links(content)
        
        for link in links:
            graph['outlinks'][rel_path].add(link)
            graph['inlinks'][link].add(rel_path)
    
    return graph

def trace_item(item_name, graph, max_depth=3):
    """Trace all connections for an item."""
    results = {
        'name': item_name,
        'direct_out': [],
        'direct_in': [],
        'paths': [],
    }
    
    # Find matching files
    target_files = set()
    for fp, meta in graph['metadata'].items():
        if item_name.lower() in meta['name'].lower() or item_name == fp:
            target_files.add(fp)
    
    for target in target_files:
        # Direct outgoing links
        results['direct_out'] = list(graph['outlinks'].get(target, []))
        
        # Direct incoming links
        results['direct_in'] = list(graph['inlinks'].get(target, []))
    
    return results

def print_recall(item_name):
    """Print complete recall for an item."""
    print("=" * 60)
    print(f"RECALL: {item_name}")
    print("=" * 60)
    
    # Build graph
    graph = build_link_graph()
    
    # Find the item
    target_files = set()
    for fp, meta in graph['metadata'].items():
        if item_name.lower() in meta['name'].lower() or item_name in fp:
            target_files.add(fp)
    
    if not target_files:
        print(f"Item '{item_name}' not found in vault")
        return
    
    for target in target_files:
        meta = graph['metadata'].get(target, {})
        print(f"\n📁 File: {target}")
        print(f"   Type: {meta.get('type', 'unknown')}")
        print(f"   IDM: {meta.get('idm', 'N/A')}")
        
        # Outgoing links (what this item links to)
        out = graph['outlinks'].get(target, set())
        print(f"\n   📤 Links TO ({len(out)} items):")
        for link in sorted(list(out))[:15]:
            print(f"      → {link}")
        if len(out) > 15:
            print(f"      ... and {len(out) - 15} more")
        
        # Incoming links (what links to this item)
        inbound = graph['inlinks'].get(target, set())
        print(f"\n   📥 Referenced BY ({len(inbound)} items):")
        for link in sorted(list(inbound))[:15]:
            print(f"      ← {link}")
        if len(inbound) > 15:
            print(f"      ... and {len(inbound) - 15} more")
        
        # Trace back through the graph
        print(f"\n   🔗 Full Connection Chain:")
        
        # Level 1: Direct connections
        all_connections = set()
        all_connections.update(out)
        all_connections.update(inbound)
        
        # Level 2: Connections of connections
        for conn in list(all_connections)[:5]:
            level2 = graph['outlinks'].get(conn, set())
            all_connections.update(level2)
        
        print(f"      Total connected items: {len(all_connections)}")
        
        # Find connected politicians
        connected_pols = []
        for conn in all_connections:
            m = graph['metadata'].get(conn, {})
            if m.get('type') in ['deputy', 'senator']:
                connected_pols.append(m.get('name', conn))
        
        if connected_pols:
            print(f"      Politicians: {connected_pols[:10]}")
        
        print()

def full_vault_analysis():
    """Print analysis of entire vault connections."""
    graph = build_link_graph()
    
    print("\n" + "=" * 60)
    print("VAULT CONNECTION ANALYSIS")
    print("=" * 60)
    
    # Count by type
    type_counts = defaultdict(int)
    for fp, meta in graph['metadata'].items():
        type_counts[meta.get('type', 'unknown')] += 1
    
    print(f"\n📊 Files by Type:")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"   {t}: {c}")
    
    # Most linked items
    print(f"\n🔗 Most Referenced Items (inlinks):")
    sorted_in = sorted(graph['inlinks'].items(), key=lambda x: -len(x[1]))[:10]
    for fp, links in sorted_in:
        meta = graph['metadata'].get(fp, {})
        print(f"   {meta.get('name', fp)}: {len(links)} references")
    
    print(f"\n📤 Most Outgoing Links:")
    sorted_out = sorted(graph['outlinks'].items(), key=lambda x: -len(x[1]))[:10]
    for fp, links in sorted_out:
        meta = graph['metadata'].get(fp, {})
        print(f"   {meta.get('name', fp)}: {len(links)} outgoing")

def main():
    """Main function."""
    import sys
    
    if len(sys.argv) > 1:
        # Recall specific item
        item_name = " ".join(sys.argv[1:])
        print_recall(item_name)
    else:
        # Full analysis
        full_vault_analysis()

if __name__ == "__main__":
    main()