#!/usr/bin/env python3
"""
Obsidian Plugin Copier - Copy verified plugins to obsidian-plugins/

Usage:
    python3 scripts/obsidian_plugin_manager.py --copy
    python3 scripts/obsidian_plugin_manager.py --list
    python3 scripts/obsidian_plugin_manager.py --verify
"""

import shutil
import json
import argparse
from pathlib import Path

PROJECT_ROOT = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
SOURCE_DIR = PROJECT_ROOT / "vault/.obsidian/plugins"
DEST_DIR = PROJECT_ROOT / "obsidian-plugins/functional"

VERIFIED_PLUGINS = [
    {"name": "copilot", "size_mb": 5.4, "status": "pending"},
    {"name": "dataview", "size_mb": 1.3, "status": "pending"},
    {"name": "quickadd", "size_mb": 0.2, "status": "pending"},
    {"name": "templater-obsidian", "size_mb": 0.3, "status": "pending"},
    {"name": "omnisearch", "size_mb": 0.6, "status": "pending"},
    {"name": "obsidian-git", "size_mb": 0.7, "status": "pending"},
    {"name": "metadata-menu", "size_mb": 1.0, "status": "pending"},
]

MAPPING = {
    "templater-obsidian": "templater",
}


def get_plugin_size(plugin_path: Path) -> float:
    """Get total size of plugin in MB."""
    total = 0
    for f in plugin_path.rglob("*"):
        if f.is_file():
            total += f.stat().st_size
    return total / (1024 * 1024)


def copy_plugin(plugin_name: str) -> tuple:
    """Copy single plugin. Returns (success, message)."""
    src = SOURCE_DIR / plugin_name
    dst = DEST_DIR / MAPPING.get(plugin_name, plugin_name)
    
    if not src.exists():
        return False, f"Source {plugin_name} not found"
    
    if not (src / "main.js").exists() and not (src / "manifest.json").exists():
        return False, f"{plugin_name} missing main files"
    
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    
    actual_size = get_plugin_size(dst)
    return True, f"Copied {plugin_name} ({actual_size:.1f}MB)"


def list_plugins() -> list:
    """List available plugins in source."""
    if not SOURCE_DIR.exists():
        return []
    
    plugins = []
    for item in SOURCE_DIR.iterdir():
        if item.is_dir() and (item / "manifest.json" or item / "main.js"):
            plugins.append(item.name)
    return plugins


def create_manifest():
    """Create manifest.json with plugin status."""
    manifest = {
        "version": "1.0",
        "created": "2026-04-27",
        "source": str(SOURCE_DIR),
        "destination": str(DEST_DIR),
        "plugins": []
    }
    
    for plugin in VERIFIED_PLUGINS:
        src = SOURCE_DIR / plugin["name"]
        if src.exists():
            size = get_plugin_size(src)
            dest_name = MAPPING.get(plugin["name"], plugin["name"])
            manifest["plugins"].append({
                "name": plugin["name"],
                "mapped_name": dest_name,
                "size_mb": round(size, 1),
                "status": "copied" if (DEST_DIR / dest_name).exists() else "pending"
            })
    
    manifest_file = DEST_DIR.parent / "manifest.json"
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)
    
    return manifest_file


def copy_all_plugins():
    """Copy all verified plugins."""
    print("=" * 50)
    print("Obsidian Plugin Copier")
    print("=" * 50)
    
    results = []
    for plugin in VERIFIED_PLUGINS:
        success, msg = copy_plugin(plugin["name"])
        status = "✅" if success else "❌"
        print(f"{status} {msg}")
        results.append(success)
    
    manifest_file = create_manifest()
    print(f"\nCreated manifest: {manifest_file}")
    
    success_count = sum(results)
    print(f"\nResult: {success_count}/{len(results)} plugins copied")
    return all(results)


def verify_plugins():
    """Verify copied plugins."""
    print("=" * 50)
    print("Plugin Verification")
    print("=" * 50)
    
    all_verified = True
    for plugin in VERIFIED_PLUGINS:
        name = MAPPING.get(plugin["name"], plugin["name"])
        dst = DEST_DIR / name
        if dst.exists():
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - NOT FOUND")
            all_verified = False
    
    return all_verified


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Obsidian Plugin Copier")
    parser.add_argument("--copy", action="store_true", help="Copy all verified plugins")
    parser.add_argument("--list", action="store_true", help="List available plugins")
    parser.add_argument("--verify", action="store_true", help="Verify copied plugins")
    
    args = parser.parse_args()
    
    if args.list:
        plugins = list_plugins()
        print("Available plugins:")
        for p in plugins:
            print(f"  - {p}")
    elif args.verify:
        verify_plugins()
    elif args.copy:
        copy_all_plugins()
    else:
        parser.print_help()