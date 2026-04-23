#!/usr/bin/env python3
"""StenoMD Web Dashboard - Statistics and Manual Scrape Control"""

import json
import os
import subprocess
import threading
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="StenoMD Dashboard")

BASE_DIR = Path("/home/adrian/Desktop/NEDAILAB/StenoMD")
VAULT_DIR = BASE_DIR / "vault"
DATA_DIR = BASE_DIR / "data"
SCRIPTS_DIR = BASE_DIR / "scripts"
PROGRESS_FILE = Path("/tmp/stenomd_progress.json")

scrape_status = {
    "cdep": {"running": False, "last_run": None, "result": None},
    "senate": {"running": False, "last_run": None, "result": None},
}


def count_files(directory: Path, pattern: str = "*.md", exclude_index: bool = True) -> int:
    if not directory.exists():
        return 0
    files = []
    for f in directory.rglob(pattern):
        if exclude_index and f.name == "Index.md":
            continue
        files.append(f)
    return len(files)


def get_latest_file(directory: Path, pattern: str = "*.md") -> str | None:
    if not directory.exists():
        return None
    files = list(directory.rglob(pattern))
    if not files:
        return None
    latest = max(files, key=os.path.getmtime)
    return datetime.fromtimestamp(os.path.getmtime(latest)).strftime("%Y-%m-%d %H:%M")


def get_statistics() -> dict:
    import sys
    sys.path.insert(0, str(BASE_DIR / "scripts"))
    from validators import DataValidator
    
    validator = DataValidator(VAULT_DIR)
    
    senators_dir = VAULT_DIR / "politicians" / "senators"
    deputies_dir = VAULT_DIR / "politicians" / "deputies"
    senates_sessions_dir = VAULT_DIR / "sessions" / "senate"
    deputies_sessions_dir = VAULT_DIR / "sessions" / "deputies"
    
    # Count excluding Index.md files
    senators = count_files(senators_dir, exclude_index=True)
    deputies = count_files(deputies_dir, exclude_index=True)
    all_politicians = senators + deputies
    
    senate_sessions = count_files(senates_sessions_dir, exclude_index=True)
    deputy_sessions = count_files(deputies_sessions_dir, exclude_index=True)
    total_sessions = senate_sessions + deputy_sessions
    
    # Get knowledge graph stats
    kg_file = BASE_DIR / "knowledge_graph" / "entities.json"
    kg_persons = 0
    kg_sessions = 0
    kg_entities = 0
    kg_triples = 0
    kg_relationship_types = []
    
    if kg_file.exists():
        try:
            kg_data = json.loads(kg_file.read_text())
            kg_persons = len(kg_data.get("persons", []))
            kg_sessions = len(kg_data.get("sessions", []))
        except:
            pass
    
    # Try SQLite KG for rich stats
    kg_sqlite_path = BASE_DIR / "knowledge_graph" / "knowledge_graph.sqlite3"
    if not kg_sqlite_path.exists():
        # Check default location
        kg_sqlite_path = Path.home() / ".mempalace" / "knowledge_graph.sqlite3"
    
    if kg_sqlite_path.exists():
        try:
            import sqlite3
            conn = sqlite3.connect(kg_sqlite_path)
            cur = conn.cursor()
            
            # Get entity count
            cur.execute("SELECT COUNT(*) FROM entities")
            kg_entities = cur.fetchone()[0] or 0
            
            # Get triple count
            cur.execute("SELECT COUNT(*) FROM triples")
            kg_triples = cur.fetchone()[0] or 0
            
            # Get relationship types
            cur.execute("SELECT DISTINCT predicate FROM triples")
            rels = cur.fetchall()
            kg_relationship_types = [r[0] for r in rels]
            
            conn.close()
        except Exception as e:
            pass
    
    return {
        "senators": senators,
        "deputies": deputies,
        "total_politicians": all_politicians,
        "senate_sessions": senate_sessions,
        "deputy_sessions": deputy_sessions,
        "total_sessions": total_sessions,
        "last_senate_session": get_latest_file(senates_sessions_dir),
        "last_deputy_session": get_latest_file(deputies_sessions_dir),
        "complete_senate": len([s for s in validator._existing_sessions.values() if s['chamber'] == 'senate' and s['is_complete']]),
        "complete_deputy": len([s for s in validator._existing_sessions.values() if s['chamber'] == 'deputies' and s['is_complete']]),
        "kg_persons": kg_persons,
        "kg_sessions": kg_sessions,
        "kg_entities": kg_entities,
        "kg_triples": kg_triples,
        "kg_relationship_types": kg_relationship_types,
    }


def run_scrape(chamber: str, params: dict = None):
    """Run scrape in background thread"""
    global scrape_status
    params = params or {}
    
    scrape_status[chamber]["running"] = True
    scrape_status[chamber]["last_run"] = datetime.now().isoformat()
    
    try:
        if chamber == "cdep":
            years = params.get("years", "2024,2025,2026")
            max_id = params.get("max_id", 30)
            cmd = ["python3", str(SCRIPTS_DIR / "agents" / "cdep_agent.py"), 
                   "--years", str(years), "--max-id", str(max_id), "--json-output"]
        else:
            year = params.get("year", 2026)
            max_sessions = params.get("max", 10)
            cmd = ["python3", str(SCRIPTS_DIR / "agents" / "senat_agent.py"), 
                   "--year", str(year), "--max", str(max_sessions), "--sync-vault", "--json-output"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        summary = {}
        if result.stdout:
            for line in reversed(result.stdout.strip().split('\n')):
                try:
                    summary = json.loads(line)
                    if summary.get("status") == "complete":
                        break
                except:
                    continue
        
        scrape_status[chamber]["result"] = {
            "success": result.returncode == 0,
            "summary": summary,
            "output": result.stdout[-2000:] if result.stdout else "",
            "error": result.stderr[-1000:] if result.stderr else "",
        }
    except Exception as e:
        scrape_status[chamber]["result"] = {
            "success": False,
            "output": "",
            "error": str(e),
        }
    finally:
        scrape_status[chamber]["running"] = False


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    stats = get_statistics()
    
    html = f"""<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StenoMD - Romanian Parliament Knowledge Brain</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        
        header {{ text-align: center; margin-bottom: 3rem; }}
        h1 {{ font-size: 2.5rem; color: #38bdf8; margin-bottom: 0.5rem; }}
        .subtitle {{ color: #94a3b8; font-size: 1.1rem; }}
        
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }}
        .stat-card {{ background: #1e293b; border-radius: 12px; padding: 1.5rem; border: 1px solid #334155; }}
        .stat-card h3 {{ color: #94a3b8; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; }}
        .stat-card .value {{ font-size: 2.5rem; font-weight: bold; color: #38bdf8; }}
        .stat-card .value.senate {{ color: #22c55e; }}
        .stat-card .value.deputy {{ color: #f59e0b; }}
        .stat-card .value.sessions {{ color: #a855f7; }}
        
        .section {{ background: #1e293b; border-radius: 12px; padding: 2rem; margin-bottom: 2rem; border: 1px solid #334155; }}
        .section h2 {{ color: #fff; margin-bottom: 1.5rem; font-size: 1.5rem; }}
        
        .scrape-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }}
        .scrape-card {{ background: #0f172a; border-radius: 8px; padding: 1.5rem; border: 1px solid #334155; }}
        .scrape-card h3 {{ color: #38bdf8; margin-bottom: 0.5rem; }}
        .scrape-card p {{ color: #94a3b8; font-size: 0.9rem; margin-bottom: 1rem; }}
        
        .btn {{ display: inline-block; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; text-decoration: none; cursor: pointer; border: none; transition: all 0.2s; }}
        .btn-primary {{ background: #38bdf8; color: #0f172a; }}
        .btn-primary:hover {{ background: #0ea5e9; transform: translateY(-1px); }}
        .btn-primary:disabled {{ background: #475569; cursor: not-allowed; transform: none; }}
        .btn-senate {{ background: #22c55e; color: #0f172a; }}
        .btn-senate:hover {{ background: #16a34a; }}
        .btn-deputy {{ background: #f59e0b; color: #0f172a; }}
        .btn-deputy:hover {{ background: #d97706; }}
        
        .status {{ margin-top: 1rem; padding: 1rem; border-radius: 8px; font-size: 0.9rem; }}
        .status.idle {{ background: #1e293b; color: #94a3b8; }}
        .status.running {{ background: #fef3c7; color: #92400e; }}
        .status.success {{ background: #dcfce7; color: #166534; }}
        .status.error {{ background: #fee2e2; color: #991b1b; }}
        
        .footer {{ text-align: center; color: #475569; margin-top: 2rem; padding-top: 2rem; border-top: 1px solid #1e293b; }}
        
        .recent-activity {{ margin-top: 1rem; }}
        .activity-item {{ padding: 0.75rem 0; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; }}
        .activity-item:last-child {{ border-bottom: none; }}
        .activity-date {{ color: #64748b; font-size: 0.85rem; }}
        
        .chamber-info {{ display: flex; gap: 2rem; margin-bottom: 1rem; }}
        .chamber-stat {{ flex: 1; }}
        .chamber-stat .label {{ color: #64748b; font-size: 0.85rem; }}
        .chamber-stat .count {{ font-size: 1.5rem; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>�� StenoMD Dashboard</h1>
            <p class="subtitle">Romanian Parliament Knowledge Brain</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Senatori</h3>
                <div class="value senate">{stats['senators']}</div>
            </div>
            <div class="stat-card">
                <h3>Deputați</h3>
                <div class="value deputy">{stats['deputies']}</div>
            </div>
            <div class="stat-card">
                <h3>Sedințe Senat</h3>
                <div class="value senate">{stats['senate_sessions']}</div>
            </div>
            <div class="stat-card">
                <h3>Sedințe Camera</h3>
                <div class="value deputy">{stats['deputy_sessions']}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🏛️ Manual Scrape</h2>
            <div class="scrape-grid">
                <div class="scrape-card">
                    <h3>Senat (senat.ro)</h3>
                    <p>Extrage stenogramele Senatului României pentru anul curent</p>
                    <div class="controls">
                        <label>An: <input type="number" id="senate-year" value="2026" min="2020" max="2026" style="width: 70px;"></label>
                        <label>Max: <input type="number" id="senate-max" value="10" min="1" max="50" style="width: 50px;"></label>
                    </div>
                    <button id="btn-senate" class="btn btn-senate" onclick="runScrape('senate')">
                        ▶ Extrage Date Senat
                    </button>
                    <div id="status-senate" class="status idle">⏳ Idle</div>
                </div>
                <div class="scrape-card">
                    <h3>Camera Deputatilor (cdep.ro)</h3>
                    <p>Extrage stenogramele Camerei Deputatilor pentru 2024-2026</p>
                    <div class="controls">
                        <label>Ani: <input type="text" id="cdep-years" value="2024,2025,2026" style="width: 120px;"></label>
                        <label>Max ID: <input type="number" id="cdep-max-id" value="30" min="1" max="200" style="width: 50px;"></label>
                    </div>
                    <button id="btn-cdep" class="btn btn-deputy" onclick="runScrape('cdep')">
                        ▶ Extrage Date Camera
                    </button>
                    <div id="status-cdep" class="status idle">⏳ Idle</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📁 Vault Statistics</h2>
            <div class="chamber-info">
                <div class="chamber-stat">
                    <div class="label">Total Politicieni</div>
                    <div class="count">{stats['total_politicians']}</div>
                </div>
                <div class="chamber-stat">
                    <div class="label">Total Sedințe</div>
                    <div class="count">{stats['total_sessions']}</div>
                </div>
                <div class="chamber-stat">
                    <div class="label">Sedințe Complete Senat</div>
                    <div class="count" style="color: #22c55e;">{stats['complete_senate']}</div>
                </div>
                <div class="chamber-stat">
                    <div class="label">Sedințe Complete Camera</div>
                    <div class="count" style="color: #f59e0b;">{stats['complete_deputy']}</div>
                </div>
            </div>
            <div style="margin-top: 1rem; padding: 1rem; background: #0f172a; border-radius: 8px;">
                <h4 style="color: #38bdf8; margin-bottom: 0.5rem;">Ultimele Sedințe</h4>
                <div style="display: flex; gap: 2rem;">
                    <div>
                        <span style="color: #64748b;">Senat: </span>
                        <span>{stats['last_senate_session'] or 'N/A'}</span>
                    </div>
                    <div>
                        <span style="color: #64748b;">Camera: </span>
                        <span>{stats['last_deputy_session'] or 'N/A'}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🧠 Knowledge Graph</h2>
            <div class="chamber-info">
                <div class="chamber-stat">
                    <div class="label">Persoane in KG</div>
                    <div class="count">{stats.get('kg_persons', 0)}</div>
                </div>
                <div class="chamber-stat">
                    <div class="label">Sesiuni in KG</div>
                    <div class="count">{stats.get('kg_sessions', 0)}</div>
                </div>
            </div>
            <div style="margin-top: 1rem;">
                <button class="btn btn-primary" onclick="refreshStats()">🔄 Reîmprospătează</button>
            </div>
        </div>
        
        <div class="footer">
            <p>StenoMD v1.0 • Actualizat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><a href="https://cdep.ro" target="_blank" style="color: #38bdf8;">cdep.ro</a> • <a href="https://senat.ro" target="_blank" style="color: #38bdf8;">senat.ro</a></p>
        </div>
    </div>
    
    <script>
        async function runScrape(chamber) {{
            const btn = document.getElementById('btn-' + chamber);
            const status = document.getElementById('status-' + chamber);
            
            // Get parameters from inputs
            const params = chamber === 'senate' 
                ? {{ year: parseInt(document.getElementById('senate-year').value) || 2026,
                    max: parseInt(document.getElementById('senate-max').value) || 10 }}
                : {{ years: document.getElementById('cdep-years').value || "2024,2025,2026",
                    max_id: parseInt(document.getElementById('cdep-max-id').value) || 30 }};
            
            btn.disabled = true;
            btn.textContent = '⏳ Se procesează...';
            status.className = 'status running';
            status.textContent = '⏳ Procesare în curs...';
            
            try {{
                const response = await fetch('/api/scrape/' + chamber, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(params)
                }});
                const data = await response.json();
                
                if (data.status === 'started') {{
                    status.className = 'status running';
                    status.textContent = '⏳ ' + data.message;
                    
                    // Poll for completion
                    setTimeout(() => checkStatus(chamber), 2000);
                }} else {{
                    status.className = data.success ? 'status success' : 'status error';
                    status.textContent = data.success ? '✅ Succes' : '❌ Eroare: ' + data.error;
                    btn.disabled = false;
                    btn.textContent = chamber === 'senate' ? '▶ Extrage Date Senat' : '▶ Extrage Date Camera';
                }}
            }} catch (e) {{
                status.className = 'status error';
                status.textContent = '❌ Eroare: ' + e.message;
                btn.disabled = false;
            }}
        }}
        
        async function checkStatus(chamber) {{
            const status = document.getElementById('status-' + chamber);
            const btn = document.getElementById('btn-' + chamber);
            
            try {{
                const response = await fetch('/api/status/' + chamber);
                const data = await response.json();
                
                if (data.running) {{
                    status.textContent = '⏳ Se procesează... (' + data.elapsed + ')';
                    setTimeout(() => checkStatus(chamber), 3000);
                }} else {{
                    status.className = data.result?.success ? 'status success' : 'status error';
                    status.textContent = data.result?.success ? '✅ Succes' : '❌ ' + (data.result?.error || 'Eroare');
                    btn.disabled = false;
                    btn.textContent = chamber === 'senate' ? '▶ Extrage Date Senat' : '▶ Extrage Date Camera';
                    if (data.result?.success) {{
                        // Force refresh after successful scrape
                        setTimeout(() => {{
                            window.location.href = window.location.href;
                        }}, 1500);
                    }}
                }}
            }} catch (e) {{
                btn.disabled = false;
            }}
        }}
        
        async function refreshStats() {{
            try {{
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                // Update stat cards
                const statCards = document.querySelectorAll('.stat-card .value');
                if (statCards[0]) statCards[0].textContent = data.senators;
                if (statCards[1]) statCards[1].textContent = data.deputies;
                if (statCards[2]) statCards[2].textContent = data.senate_sessions;
                if (statCards[3]) statCards[3].textContent = data.deputy_sessions;
                
                // Update chamber stats
                document.querySelectorAll('.chamber-stat .count').forEach((el, i) => {{
                    if (i === 0) el.textContent = data.total_politicians;
                    if (i === 1) el.textContent = data.total_sessions;
                    if (i === 2) el.textContent = data.complete_senate;
                    if (i === 3) el.textContent = data.complete_deputy;
                }});
                
                alert('Stats refreshed! Senators: ' + data.senators + ', Deputies: ' + data.deputies + ', Sessions: ' + data.total_sessions);
            }} catch (e) {{
                alert('Error refreshing: ' + e.message);
            }}
        }}
    </script>
</body>
</html>"""
    return html


@app.get("/api/stats")
async def api_stats():
    return get_statistics()


@app.post("/api/scrape/{chamber}")
async def api_scrape(chamber: str, request: Request):
    if chamber not in ["cdep", "senate"]:
        return {"status": "error", "error": "Invalid chamber"}
    
    if scrape_status[chamber]["running"]:
        return {"status": "running", "message": "Scrape already in progress"}
    
    try:
        body = await request.json()
    except:
        body = {}
    
    thread = threading.Thread(target=run_scrape, args=(chamber, body))
    thread.start()
    
    return {"status": "started", "message": f"Started {chamber} scrape"}


@app.get("/api/status/{chamber}")
async def api_status(chamber: str):
    if chamber not in ["cdep", "senate"]:
        return {"error": "Invalid chamber"}
    
    status = scrape_status[chamber]
    elapsed = "0s"
    
    if status["last_run"]:
        run_time = datetime.fromisoformat(status["last_run"])
        elapsed = str(datetime.now() - run_time)
    
    return {
        "running": status["running"],
        "last_run": status["last_run"],
        "elapsed": elapsed,
        "result": status["result"],
    }


@app.get("/api/scrape/progress")
async def api_scrape_progress():
    """Get current scrape progress."""
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text())
        except:
            pass
    return {"status": "idle", "chamber": None, "current": 0, "total": 0, "session": ""}


@app.post("/api/scrape/progress/clear")
async def api_clear_progress():
    """Clear progress file after scrape completes."""
    if PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()
    return {"status": "cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)