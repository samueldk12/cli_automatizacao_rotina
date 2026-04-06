"""Gera pagina HTML interativa para configurar e monitorar MYC."""

import json
import os
import sys
import subprocess
from pathlib import Path

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #0d1117;
    color: #e6edf3;
    min-height: 100vh;
    padding: 20px;
}
.container { max-width: 1200px; margin: 0 auto; }
h1 {
    text-align: center;
    font-size: 2em;
    margin-bottom: 8px;
    background: linear-gradient(90deg, #58a6ff, #bc8cff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.subtitle { text-align: center; color: #8b949e; margin-bottom: 30px; font-size: 0.9em; }
.header-actions {
    display: flex; justify-content: center; gap: 10px; margin-bottom: 30px; flex-wrap: wrap;
}
.header-actions button {
    background: #238636; border: none; color: #fff; padding: 10px 20px;
    border-radius: 8px; cursor: pointer; font-size: 0.9em; font-weight: 600;
}
.header-actions button:hover { background: #2ea043; }
.header-actions button.secondary { background: #21262d; border: 1px solid #30363d; }
.header-actions button.secondary:hover { background: #30363d; }
.card {
    background: #161b22; border: 1px solid #30363d; border-radius: 12px;
    padding: 20px; margin-bottom: 20px;
}
.card h2 {
    font-size: 1.2em; margin-bottom: 15px; padding-bottom: 10px;
    border-bottom: 1px solid #21262d; display: flex; align-items: center; gap: 8px;
}
.card h2 .badge {
    font-size: 0.7em; background: #238636; padding: 2px 8px; border-radius: 10px;
    font-weight: 400;
}
.stats-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px; margin-bottom: 20px;
}
.stat-box {
    background: #0d1117; border: 1px solid #21262d; border-radius: 10px;
    padding: 15px; text-align: center;
}
.stat-box .num { font-size: 2em; font-weight: 700; color: #58a6ff; }
.stat-box .label { font-size: 0.8em; color: #8b949e; margin-top: 4px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #21262d; }
th { color: #8b949e; font-size: 0.8em; text-transform: uppercase; letter-spacing: 0.5px; }
td { font-size: 0.9em; }
.status-ok { color: #3fb950; }
.status-err { color: #f85149; }
.status-warn { color: #d29922; }
.tag {
    display: inline-block; background: #1f2937; border: 1px solid #30363d;
    padding: 2px 8px; border-radius: 6px; font-size: 0.8em; margin: 2px;
}
.btn {
    background: #21262d; border: 1px solid #30363d; color: #e6edf3;
    padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.8em;
}
.btn:hover { background: #30363d; }
.env-row {
    display: flex; gap: 10px; margin: 8px 0; align-items: center;
    font-family: 'Cascadia Code', monospace; font-size: 0.85em;
}
.env-key { color: #79c0ff; min-width: 200px; }
.env-val { color: #a5d6ff; }
.env-val.hidden { filter: blur(4px); cursor: pointer; user-select: none; }
.progress-bar {
    height: 4px; background: #21262d; border-radius: 2px; margin-top: 6px; overflow: hidden;
}
.progress-fill { height: 100%; background: #3fb950; border-radius: 2px; }
.filter-input {
    background: #0d1117; border: 1px solid #30363d; color: #e6edf3;
    padding: 8px 12px; border-radius: 8px; width: 100%; max-width: 300px;
    margin-bottom: 15px; font-size: 0.9em;
}
.filter-input:focus { outline: none; border-color: #58a6ff; }
.tabs { display: flex; gap: 4px; margin-bottom: 15px; flex-wrap: wrap; }
.tab {
    background: #21262d; border: 1px solid #30363d; padding: 6px 14px;
    border-radius: 6px; cursor: pointer; font-size: 0.85em; color: #8b949e;
}
.tab.active { background: #1f6feb; color: #fff; border-color: #1f6feb; }
.tab:hover:not(.active) { background: #30363d; }
.section { display: none; }
.section.active { display: block; }
</style>
"""

JS = """
<script>
function toggleSecret(el) { el.classList.toggle('hidden'); }

function filterTable(tableId, query) {
    const q = query.toLowerCase();
    document.querySelectorAll('#' + tableId + ' tbody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
}

function showSection(id) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('s-' + id).classList.add('active');
    document.getElementById('t-' + id).classList.add('active');
}

function launchAgent(name) {
    const btn = document.getElementById('btn-launch-' + name);
    if (!btn) return;
    btn.textContent = 'Lancando...';
    btn.style.background = '#1f6feb';
    fetch('/launch/' + name)
        .then(r => r.json())
        .then(data => {
            btn.textContent = 'Lancado!';
            btn.style.background = '#238636';
            setTimeout(() => {
                btn.textContent = 'Lancar';
                btn.style.background = '';
                location.reload();
            }, 2000);
        })
        .catch(err => {
            btn.textContent = 'Erro';
            btn.style.background = '#f85149';
        });
}

async function refreshStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        console.log('Stats refreshed:', data);
    } catch(e) {}
}
setInterval(refreshStats, 30000);
</script>
"""


def _stats(agents, history, routines, plugins_count):
    ok = sum(1 for h in history if h.get("status", "").startswith(("ok", "exit_0")))
    errs = len(history) - ok
    return {
        "agents": len(agents),
        "plugins": plugins_count,
        "routines": routines,
        "launches": len(history),
        "successful": ok,
        "errors": errs,
    }


def _env_rows(env_vars):
    rows = []
    for k, v in env_vars.items():
        masked = k.endswith(("KEY", "SECRET", "TOKEN", "PASSWORD"))
        display = "..." + v[-4:] if masked and len(v) > 8 else v
        is_secret = masked
        rows.append((k, display, is_secret))
    return rows


def generate_page() -> str:
    import myc.agent as agent_mod
    from myc.agent import _load_agents, _load_history, _load_agents
    from myc.config import load_config
    from myc.plugin_installer import get_plugin_meta, BUILTIN_DIR

    agents = _load_agents()
    history = _load_history()
    config = load_config()
    commands = config.get("commands", {})

    routine_count = 0
    for grp in commands.values():
        routine_count += len(grp.get("subcommands", {}))

    installed_plugins = 0
    for p in Path.home().glob(".myc/agents/plugins/*.py"):
        if not p.name.startswith("_"):
            installed_plugins += 1

    stats = _stats(agents, history, routine_count, installed_plugins)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MYC — Painel de Configuracao</title>
{CSS}
{JS}
</head>
<body>
<div class="container">
<h1>MYC — My Commands</h1>
<p class="subtitle">Painel de Controle &bull; Gerado em {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>

<div class="header-actions">
    <button class="secondary" onclick="location.reload()">&#x21bb; Atualizar</button>
    <button class="secondary" onclick="showSection('agents')">Agentes</button>
    <button class="secondary" onclick="showSection('routines')">Rotinas</button>
    <button class="secondary" onclick="showSection('plugins')">Plugins</button>
    <button class="secondary" onclick="showSection('history')">Historico</button>
</div>

<div class="stats-grid">
    <div class="stat-box"><div class="num">{stats['agents']}</div><div class="label">Agentes</div></div>
    <div class="stat-box"><div class="num">{stats['plugins']}</div><div class="label">Plugins</div></div>
    <div class="stat-box"><div class="num">{stats['routines']}</div><div class="label">Rotinas</div></div>
    <div class="stat-box"><div class="num">{stats['launches']}</div><div class="label">Lancamentos</div></div>
    <div class="stat-box"><div class="num" style="color:#3fb950">{stats['successful']}</div><div class="label">Sucessos</div></div>
    <div class="stat-box"><div class="num" style="color:#f85149">{stats['errors']}</div><div class="label">Erros</div></div>
</div>

<div class="tabs">
    <div class="tab active" id="t-agents" onclick="showSection('agents')">Agentes</div>
    <div class="tab" id="t-routines" onclick="showSection('routines')">Rotinas</div>
    <div class="tab" id="t-plugins" onclick="showSection('plugins')">Plugins</div>
    <div class="tab" id="t-history" onclick="showSection('history')">Historico</div>
</div>

<!-- AGENTS -->
<div class="section active" id="s-agents">
"""

    for name, profile in agents.items():
        platform = profile.get("platform", "?")
        env = profile.get("env", {})
        linked = profile.get("linked_routines", [])
        plugins = profile.get("plugins", [])

        html += f'<div class="card">\n<h2>Agente: {name} <span class="badge">{platform}</span> <span style="float:right"><button class="btn" id="btn-launch-{name}" onclick="launchAgent(\'{name}\')">Lancar</button></span></h2>\n'

        if env:
            html += '<div class="table-wrap"><table><tr><th>Variavel</th><th>Valor</th></tr>\n'
            for k, v, secret in _env_rows(env):
                onclick = f' onclick="toggleSecret(this)"' if secret else ''
                cls = ' env-val hidden' if secret else ' env-val'
                html += f'<tr><td class="env-key">{k}</td><td><span class="{cls}"{onclick}>{v}</span></td></tr>\n'
            html += '</table></div>\n'

        if linked:
            html += f'<div style="margin-top:10px"><strong style="color:#8b949e;font-size:0.85em">Rotinas vinculadas:</strong>'
            for r in linked:
                html += f' <span class="tag">{r}</span>'
            html += '</div>\n'

        if plugins:
            html += f'<div style="margin-top:10px"><strong style="color:#8b949e;font-size:0.85em">Plugins ativos:</strong>'
            for p in plugins:
                html += f' <span class="tag">{p}.py</span>'
            html += '</div>\n'

        html += '</div>\n'

    if not agents:
        html += '<div class="card"><p style="color:#8b949e">Nenhum agente configurado. Use <code>myc install openclaude</code> ou <code>myc agent add</code>.</p></div>\n'

    html += '</div>\n\n'

    html += '<div class="section" id="s-routines">\n'

    if commands:
        for grp_name, grp_data in commands.items():
            subs = grp_data.get("subcommands", {})
            html += f'<div class="card">\n<h2>Grupo: {grp_name} <span class="badge">{len(subs)} rotinas</span></h2>\n'

            if subs:
                html += '<input type="text" class="filter-input" placeholder="Filtrar..." oninput="filterTable(\'tbl-' + grp_name + '\', this.value)">'
                html += f'<div class="table-wrap"><table id="tbl-{grp_name}"><tr><th>Subcomando</th><th>Descricao</th><th>Dias</th><th>Acoes</th></tr>\n'
                for sub_name, sub_data in subs.items():
                    days = sub_data.get("days", [])
                    days_str = ", ".join(days) if days else "todos"
                    n_acts = len(sub_data.get("actions", []))
                    html += f'<tr><td><code>{sub_name}</code></td><td>{sub_data.get("description", "-")}</td><td>{days_str}</td><td>{n_acts} acoes</td></tr>\n'
                html += '</table></div>\n'
            html += '</div>\n'
    else:
        html += '<div class="card"><p style="color:#8b949e">Nenhuma rotina cadastrada. Use <code>myc add</code>.</p></div>\n'

    html += '</div>\n\n'

    html += '<div class="section" id="s-plugins">\n'

    plugin_dir = Path.home() / ".myc" / "agents" / "plugins"
    if plugin_dir.exists():
        plist = sorted(p for p in plugin_dir.glob("*.py") if not p.name.startswith("_"))
        html += f'<div class="card">\n<h2>Plugins instalados <span class="badge">{len(plist)}</span>'
        html += '<input type="text" class="filter-input" style="margin-left:20px" placeholder="Filtrar..." oninput="filterTable(\'plug-tbl\', this.value)">'
        html += f'</h2>\n'
        html += '<div class="table-wrap"><table id="plug-tbl"><tr><th>Plugin</th><th>Nome</th><th>Descricao</th></tr>\n'
        for p in plist:
            meta = get_plugin_meta(p.stem)
            pname = (meta.get("name", p.stem) if meta else p.stem)
            pdesc = (meta.get("description", "") if meta else "")
            html += f'<tr><td><code>{p.name}</code></td><td>{pname}</td><td>{pdesc}</td></tr>\n'
        html += '</table></div>\n</div>\n'
    else:
        html += '<div class="card"><p style="color:#8b949e">Nenhum plugin instalado. Use <code>myc agent bundle-install --all</code>.</p></div>\n'

    html += '</div>\n\n'

    html += '<div class="section" id="s-history">\n'

    if history:
        html += f'<div class="card">\n<h2>Historico de Lancamentos <span class="badge">{len(history)} entradas</span>'
        html += '<input type="text" class="filter-input" style="margin-left:20px" placeholder="Filtrar..." oninput="filterTable(\'hist-tbl\', this.value)">'
        html += '</h2>\n'
        html += '<div class="table-wrap"><table id="hist-tbl"><tr><th>Data</th><th>Agente</th><th>Plataforma</th><th>Rotina</th><th>Status</th></tr>\n'
        for h in history[:50]:
            dt = h.get("timestamp", "")[:19]
            st = h.get("status", "")
            st_cls = "status-ok" if st.startswith(("ok", "exit_0")) else "status-warn" if st == "interrupted" else "status-err"
            html += f'<tr><td>{dt}</td><td>{h.get("agent", "?")}</td><td>{h.get("platform", "?")}</td><td>{h.get("routine", "-")}</td><td class="{st_cls}">{st}</td></tr>\n'
        html += '</table></div>\n</div>\n'

        success_rate = 100 * stats["successful"] / stats["launches"] if stats["launches"] > 0 else 0
        html += f'<div class="card">\n<h2>Taxa de Sucesso</h2>\n'
        html += f'<div style="font-size:1.5em;margin-bottom:8px">{success_rate:.0f}%</div>\n'
        html += f'<div class="progress-bar"><div class="progress-fill" style="width:{success_rate}%"></div></div>\n'
        html += '</div>\n'
    else:
        html += '<div class="card"><p style="color:#8b949e">Nenhum historico ainda.</p></div>\n'

    html += '</div>\n\n'

    html += '</div>\n</body>\n</html>'
    return html


def serve_dashboard(port: int = 8787) -> None:
    """Servidor HTTP local que entrega o dashboard."""
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import threading
    import webbrowser
    import json as _json
    from urllib.parse import urlparse

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/" or path == "/index.html":
                self._send_html(generate_page())
            elif path.startswith("/launch/"):
                name = path.split("/launch/")[1].split("?")[0]
                self._handle_launch(name)
            elif path == "/api/stats":
                self._send_json({"ok": True})
            else:
                self.send_error(404)

        def _send_html(self, content: str):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))

        def _send_json(self, data: dict):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(_json.dumps(data).encode("utf-8"))

        def _handle_launch(self, name: str):
            from myc.agent import launch_agent
            import subprocess as _sub
            try:
                threading.Thread(target=lambda: launch_agent(name), daemon=True).start()
                self._send_json({"status": "launching", "agent": name})
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)})

        def log_message(self, fmt, *args):
            pass

    url = f"http://localhost:{port}"
    print(f"\n[bold cyan]Dashboard MYC:[/bold cyan] [link]{url}[/link]\n[dim]Abra no navegador ou aguarde abertura automatica...[/dim]")
    threading.Thread(target=lambda: webbrowser.open(url), daemon=True).start()

    server = HTTPServer(("127.0.0.1", port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
