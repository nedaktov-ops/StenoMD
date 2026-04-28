#!/usr/bin/env python3
"""Integration tests for merge_vault_to_kg.py - full vault merge simulation."""

import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from merge_vault_to_kg import merge_vault_to_kg, parse_frontmatter


def test_merge_vault_to_kg_full_integration(tmp_path):
    """Test full merge with a realistic mini-vault."""
    # Create fake vault structure
    vault = tmp_path / "vault"
    deputies_dir = vault / "politicians" / "deputies"
    senators_dir = vault / "politicians" / "senators"
    sessions_dep_dir = vault / "sessions" / "deputies"
    sessions_sen_dir = vault / "sessions" / "senate"
    laws_dir = vault / "laws"
    
    for d in [deputies_dir, senators_dir, sessions_dep_dir, sessions_sen_dir, laws_dir]:
        d.mkdir(parents=True)
    
    # Create deputy profile
    (deputies_dir / "ion-popescu.md").write_text("""---
name: Ion Popescu
idm: 123
party: PSD
speeches_count: 10
laws_proposed: 2
---
""")
    
    # Create senator profile
    (senators_dir / "ana-birchall.md").write_text("""---
name: Ana Birchall
stable_id: sen_456
party: PNL
speeches_count: 5
---
""")
    
    # Create deputy session with participants in body and laws in frontmatter
    (sessions_dep_dir / "2024-11-05.md").write_text("""---
date: '2024-11-05'
title: Sedința
chamber: deputies
laws_discussed: 123/2024, 456/2025
---
Debate content.

participants:
  - Ion Popescu
""")
    
    # Create senate session
    (sessions_sen_dir / "2024-11-06.md").write_text("""---
date: '2024-11-06'
title: Senat session
chamber: senate
---
Senate content.

participants:
  - Ana Birchall
""")
    
    # Create law file
    (laws_dir / "123-2024.md").write_text("""---
number: 123/2024
title: First Law
sponsors:
  - Ion Popescu
---
Law text.
""")
    
    # Prepare a fake existing KG to test merging
    kg_file = tmp_path / "knowledge_graph" / "entities.json"
    kg_file.parent.mkdir()
    existing_kg = {
        "metadata": {"version": "2.0"},
        "persons": [],
        "sessions": [],
        "laws": []
    }
    kg_file.write_text(json.dumps(existing_kg))
    
    # Patch config to point to our temp dirs
    with patch('merge_vault_to_kg.PROJECT_DIR', tmp_path):
        with patch('merge_vault_to_kg.VAULT_DIR', vault):
            with patch('merge_vault_to_kg.KG_FILE', kg_file):
                result = merge_vault_to_kg()
    
    # Validate results
    assert result is not None
    persons = result['persons']
    sessions = result['sessions']
    laws = result['laws']
    
    # Debug output
    print(f"\nPersons: {[p['name'] for p in persons]}")
    print(f"Sessions IDs: {[s['id'] for s in sessions]}")
    print(f"Laws: {[l['number'] for l in laws]}")
    
    # Should have 2 persons (deputy + senator)
    assert len(persons) >= 2
    person_names = [p['name'] for p in persons]
    assert 'Ion Popescu' in person_names
    assert 'Ana Birchall' in person_names
    
    # Should have 2 sessions
    assert len(sessions) == 2
    # Session IDs may include quotes from YAML parsing; normalize
    session_ids = [s['id'].strip("'\"") for s in sessions]
    assert '2024-11-05' in session_ids
    assert '2024-11-06' in session_ids
    
    # Session should have participants (lookup by normalized ID)
    dep_session = next(s for s in sessions if s['id'].strip("'\"") == '2024-11-05')
    assert 'Ion Popescu' in dep_session['participants']
    assert dep_session['chamber'] == 'deputies'
    
    # Senate session
    sen_session = next(s for s in sessions if s['id'].strip("'\"") == '2024-11-06')
    assert sen_session['chamber'] == 'senate'
    
    # Check KG file was written
    assert kg_file.exists()
    saved_kg = json.loads(kg_file.read_text())
    assert len(saved_kg['persons']) >= 2
    assert len(saved_kg['sessions']) == 2
    # Should contain the law we created
    law_numbers = [l['number'].strip("'\"") for l in saved_kg['laws']]
    assert '123/2024' in law_numbers
    print(f"Integration test passed: {len(saved_kg['persons'])} persons, {len(saved_kg['sessions'])} sessions, {len(saved_kg['laws'])} laws")


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        from pathlib import Path
        test_merge_vault_to_kg_full_integration(Path(tmpdir))
    print("All merge_vault_to_kg integration tests passed!")
