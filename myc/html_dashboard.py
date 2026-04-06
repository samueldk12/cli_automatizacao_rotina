"""Gera pagina HTML interativa para configurar e monitorar MYC."""

import json as _json
from datetime import datetime as _datetime
from pathlib import Path as _Path

CSS = """
:root {
    --bg: #0a0e17;
    --bg-card: #111827;
    --bg-hover: #1e293b;
    --border: #1e293b;
    --text: #f1f5f9;
    --text-dim: #64748b;
    --text-muted: #475569;
    --accent: #3b82f6;
    --accent-glow: rgba(59, 130, 246, 0.15);
    --green: #10b981;
    --green-glow: rgba(16, 185, 129, 0.15);
    --red: #ef4444;
    --red-glow: rgba(239, 68, 68, 0.15);
    --yellow: #f59e0b;
    --yellow-glow: rgba(245, 158, 11, 0.15);
    --purple: #8b5cf6;
    --purple-glow: rgba(139, 92, 246, 0.15);
    --radius: 14px;
    --radius-sm: 8px;
    --shadow: 0 4px 24px rgba(0,0,0,0.25), 0 1px 6px rgba(0,0,0,0.15);
    --shadow-lg: 0 8px 40px rgba(0,0,0,0.35), 0 2px 12px rgba(0,0,0,0.2);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
}

body::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 20% 0%, rgba(59,130,246,0.07), transparent),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(139,92,246,0.05), transparent);
    pointer-events: none;
    z-index: 0;
}

.container {
    position: relative; z-index: 1;
    max-width: 1400px;
    margin: 0 auto;
    padding: 24px 32px;
}

/* NAV */
.topnav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 0 24px; flex-wrap: wrap; gap: 16px;
}
.logo {
    display: flex; align-items: center; gap: 12px;
}
.logo-mark {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, var(--accent), var(--purple));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 18px; color: #fff;
}
.logo h1 {
    font-size: 1.3em; font-weight: 700;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.logo .sub {
    font-size: 0.75em; color: var(--text-muted); letter-spacing: 0.5px;
}
.nav-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.nav-btn {
    background: var(--bg-card); border: 1px solid var(--border);
    color: var(--text-dim); padding: 8px 16px; border-radius: var(--radius-sm);
    cursor: pointer; font-size: 0.82em; font-weight: 500;
    transition: all 0.2s;
}
.nav-btn:hover { background: var(--bg-hover); color: var(--text); border-color: var(--accent); }
.nav-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.nav-btn.primary { background: var(--green); color: #fff; border-color: #059669; }
.nav-btn.primary:hover { background: #059669; }

/* STATS */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px; margin: 24px 0 32px;
}
.stat-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 20px 24px;
    position: relative; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: var(--shadow); }
.stat-card::after {
    content: ''; position: absolute; top: 0; left: 0;
    width: 100%; height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--purple));
}
.stat-card.green::after { background: linear-gradient(90deg, #10b981, #34d399); }
.stat-card.red::after { background: linear-gradient(90deg, #ef4444, #f87171); }
.stat-card.yellow::after { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card.purple::after { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }
.stat-num {
    font-size: 2em; font-weight: 800; line-height: 1; margin-bottom: 6px;
}
.stat-label { font-size: 0.8em; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600; }
.stat-sub { font-size: 0.75em; color: var(--text-muted); margin-top: 4px; }
.stat-sub .up { color: var(--green); }
.stat-sub .down { color: var(--red); }

/* SECTIONS */
.section { display: none; animation: fadeIn 0.3s ease; }
.section.active { display: block; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }

/* CARDS */
.card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 24px; margin-bottom: 16px;
    box-shadow: var(--shadow);
}
.card-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
}
.card-title {
    font-size: 1.05em; font-weight: 600;
    display: flex; align-items: center; gap: 10px;
}
.icon-box {
    width: 32px; height: 32px; border-radius: 8px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0;
}
.card-badge {
    font-size: 0.7em; font-weight: 600; padding: 3px 10px;
    border-radius: 20px; background: var(--accent-glow); color: var(--accent);
}
.badge-green { background: var(--green-glow); color: var(--green); }
.badge-purple { background: var(--purple-glow); color: var(--purple); }
.badge-yellow { background: var(--yellow-glow); color: var(--yellow); }

/* AGENT CARDS */
.agent-card {
    display: grid; grid-template-columns: 1fr auto;
    gap: 20px; align-items: start;
}
.agent-info { min-width: 0; }
.agent-name {
    font-size: 1.15em; font-weight: 700; margin-bottom: 4px;
    display: flex; align-items: center; gap: 10px;
}
.agent-platform {
    font-size: 0.75em; font-weight: 600; padding: 2px 8px;
    border-radius: 6px; background: var(--purple-glow); color: var(--purple);
}
.agent-meta {
    display: flex; gap: 20px; margin-top: 12px; flex-wrap: wrap;
}
.agent-meta-item {
    font-size: 0.78em; color: var(--text-dim);
}
.agent-meta-item strong { color: var(--text); font-weight: 600; }
.env-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 8px; margin-top: 12px;
}
.env-row {
    display: flex; align-items: center; gap: 8px;
    background: var(--bg); border-radius: 6px; padding: 8px 12px;
    font-family: 'Cascadia Code', 'Fira Code', monospace; font-size: 0.78em;
}
.env-key { color: #93c5fd; }
.env-val { color: #94a3b8; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.env-val.secret { filter: blur(3px); cursor: pointer; user-select: none; transition: 0.2s; }
.env-val.secret:hover { filter: none; }
.tag {
    display: inline-block; background: var(--bg-hover); border: 1px solid var(--border);
    padding: 3px 10px; border-radius: 6px; font-size: 0.78em; margin: 2px;
    color: var(--text-dim); transition: 0.2s;
}
.tag:hover { border-color: var(--accent); color: var(--accent); }
.tags-row { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }
.launch-btn {
    background: linear-gradient(135deg, var(--green), #059669);
    border: none; color: #fff; padding: 10px 24px; border-radius: var(--radius-sm);
    cursor: pointer; font-size: 0.85em; font-weight: 600;
    transition: all 0.2s; display: flex; align-items: center; gap: 6px;
}
.launch-btn:hover { box-shadow: 0 4px 16px rgba(16,185,129,0.3); transform: scale(1.02); }
.launch-btn:active { transform: scale(0.98); }
.launch-btn.running { background: var(--yellow); pointer-events: none; }
.launch-btn.success { background: #3b82f6; }
.delete-btn {
    background: transparent; border: 1px solid var(--red); color: var(--red);
    padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 0.78em;
    margin-top: 8px; transition: 0.2s;
}
.delete-btn:hover { background: var(--red); color: #fff; }

/* TABLES */
.table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
table { width: 100%; border-collapse: collapse; }
thead th {
    color: var(--text-muted); font-size: 0.75em; text-transform: uppercase;
    letter-spacing: 0.6px; padding: 10px 12px; text-align: left;
    border-bottom: 1px solid var(--border); font-weight: 600;
    position: sticky; top: 0; background: var(--bg-card);
}
tbody td {
    padding: 10px 12px; border-bottom: 1px solid var(--bg);
    font-size: 0.85em; vertical-align: middle;
}
tbody tr { transition: background 0.15s; }
tbody tr:hover { background: var(--bg-hover); }
code {
    background: var(--bg); padding: 2px 6px; border-radius: 4px;
    font-family: 'Cascadia Code', monospace; font-size: 0.9em;
    color: #93c5fd;
}
.st-ok { color: var(--green); font-weight: 600; }
.st-err { color: var(--red); font-weight: 600; }
.st-warn { color: var(--yellow); font-weight: 600; }

/* PROGRESS */
.progress-bar {
    height: 8px; background: var(--bg); border-radius: 4px;
    overflow: hidden; margin-top: 8px;
}
.progress-fill {
    height: 100%; border-radius: 4px; transition: width 0.4s ease;
    background: linear-gradient(90deg, var(--green), #34d399);
}
.progress-fill.med { background: linear-gradient(90deg, var(--yellow), #fbbf24); }
.progress-fill.low { background: linear-gradient(90deg, var(--red), #f87171); }

/* SEARCH & FILTER */
.search-box {
    background: var(--bg); border: 1px solid var(--border);
    color: var(--text); padding: 8px 14px; border-radius: var(--radius-sm);
    font-size: 0.85em; min-width: 200px; max-width: 400px;
    transition: border-color 0.2s;
}
.search-box:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow); }
.search-box::placeholder { color: var(--text-muted); }

/* EMPTY STATE */
.empty-state {
    text-align: center; padding: 60px 20px; color: var(--text-muted);
}
.empty-state .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
.empty-state h3 { color: var(--text-dim); margin-bottom: 8px; }
.empty-state p { font-size: 0.85em; margin-bottom: 16px; }

/* MODAL */
.modal-overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,0.6);
    backdrop-filter: blur(6px); z-index: 100;
    display: none; align-items: center; justify-content: center;
    opacity: 0; transition: opacity 0.2s;
}
.modal-overlay.show { display: flex; opacity: 1; }
.modal {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 32px;
    width: 90%; max-width: 500px; box-shadow: var(--shadow-lg);
}
.modal h2 { font-size: 1.2em; margin-bottom: 20px; }
.modal label {
    display: block; color: var(--text-dim); font-size: 0.82em;
    margin-bottom: 4px; font-weight: 500;
}
.modal input, .modal select, .modal textarea {
    width: 100%; background: var(--bg); border: 1px solid var(--border);
    color: var(--text); padding: 10px 12px; border-radius: 8px;
    margin-bottom: 14px; font-size: 0.88em; transition: 0.2s;
}
.modal input:focus, .modal select:focus, .modal textarea:focus {
    outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow);
}
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 8px; }
.modal-actions button {
    padding: 9px 20px; border-radius: 8px; cursor: pointer;
    font-weight: 600; font-size: 0.85em; border: none; transition: 0.2s;
}

/* RATES */
.rate-display {
    text-align: center; margin: 16px 0;
}
.rate-cpct {
    font-size: 2.8em; font-weight: 800;
    background: linear-gradient(135deg, var(--green), #34d399);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.rate-label { color: var(--text-dim); font-size: 0.85em; }

/* DAYS */
.day-pips { display: flex; gap: 4px; }
.day-pip {
    width: 10px; height: 10px; border-radius: 50%;
    background: var(--bg); border: 1px solid var(--border);
}
.day-pip.active { background: var(--accent); border-color: var(--accent); }

/* PLUGIN */
.plugin-item {
    display: flex; align-items: center; gap: 14px;
    padding: 14px; border-radius: 10px; margin-bottom: 8px;
    background: var(--bg); border: 1px solid transparent;
    transition: 0.15s;
}
.plugin-item:hover { border-color: var(--border); background: var(--bg-hover); }
.plugin-icon {
    width: 36px; height: 36px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
}
.plugin-name { font-weight: 600; font-size: 0.9em; }
.plugin-desc { font-size: 0.78em; color: var(--text-dim); margin-top: 2px; }

/* RESPONSIVE */
@media (max-width: 768px) {
    .container { padding: 16px; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .agent-card { grid-template-columns: 1fr; }
    .card { padding: 16px; }
    .topnav { flex-direction: column; align-items: flex-start; }
    .nav-actions { width: 100%; justify-content: flex-start; }
}

/* SCROLLBAR */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg); border-radius: 4px; }
::-webkit-scrollbar-thumb { background: var(--bg-hover); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
"""


JS = """
function toggleSecret(el) { el.classList.toggle('secret'); }

function filterTable(tblId, q) {
    q = q.toLowerCase();
    document.querySelectorAll('#' + tblId + ' tbody tr').forEach(r => {
        r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
}

function showSection(id) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn[data-nav]').forEach(b => b.classList.remove('active'));
    var sec = document.getElementById('s-' + id);
    if (sec) sec.classList.add('active');
    var b = document.getElementById('nav-' + id);
    if (b) b.classList.add('active');
}

function launchAgent(name) {
    var btn = document.getElementById('lp-' + name);
    if (!btn) return;
    btn.classList.add('running');
    btn.textContent = 'Executando...';
    fetch('/launch/' + encodeURIComponent(name))
        .then(function(r){return r.json();})
        .then(function(d){
            btn.classList.remove('running');
            btn.classList.add('success');
            btn.textContent = 'Concluido!';
            setTimeout(function(){
                location.reload();
            }, 2000);
        })
        .catch(function(){
            btn.classList.remove('running');
            btn.textContent = 'Erro';
            setTimeout(function(){ location.reload(); }, 1500);
        });
}

function deleteAgent(name) {
    if (!confirm('Remover agente "'+ name +'"?')) return;
    fetch('/delete/' + encodeURIComponent(name), {method:'DELETE'})
        .then(function(){ location.reload(); });
}

function openModal(id) {
    var m = document.getElementById(id);
    if (m) { m.style.display='flex'; requestAnimationFrame(()=>m.classList.add('show')); }
}
function closeModal(id) {
    var m = document.getElementById(id);
    if (m) { m.classList.remove('show'); m.style.display='none'; }
}

function searchInput() {
    return '<input type="text" class="search-box" placeholder="Filtrar..." oninput="filterTable(this.dataset.tbl || this.getAttribute(\\'data-tbl\\'), this.value)">';
}

setInterval(function(){ fetch('/api/stats').catch(()=>{}); }, 60000);

document.addEventListener('keydown', function(e){
    if(e.key==='Escape') {
        document.querySelectorAll('.modal-overlay.show').forEach(m => closeModal(m.id));
    }
});

var now = new Date();
var today = ['Domingo','Segunda-feira','Ter\u00e7a-feira','Quarta-feira','Quinta-feira','Sexta-feira','S\u00e1bado'][now.getDay()];
var el = document.getElementById('today-badge');
if(el) el.textContent = today;
"""


def _stats(agents_list, history_list, routines_count, plugins_count):
    ok = sum(
        1 for h in history_list
        if h.get("status", "").startswith(("ok", "exit_0"))
    )
    errs = len(history_list) - ok
    return {
        "agents": len(agents_list),
        "plugins": plugins_count,
        "routines": routines_count,
        "launches": len(history_list),
        "successful": ok,
        "errors": errs,
    }


def _env_rows(env_vars):
    rows = []
    sensitive = ("KEY", "SECRET", "TOKEN", "PASSWORD", "API_KEY")
    for k, v in env_vars.items():
        is_secret = any(k.endswith(s) for s in sensitive)
        display = "..." + v[-4:] if is_secret and len(v) > 8 else v
        rows.append((k, display, is_secret))
    return rows


def _platform_badge(platform):
    return {
        "openclaude": ("🤖", "badge-purple"),
        "cursor": ("💻", ""),
        "vscode_copilot": ("⚡", ""),
        "codex": ("🧠", "badge-green"),
        "custom": ("⚙️", "badge-yellow"),
    }.get(platform, ("❓", ""))


def _platform_icon(platform):
    return {
        "openclaude": "🤖",
        "cursor": "💻",
        "vscode_copilot": "⚡",
        "codex": "🧠",
        "custom": "⚙️",
    }.get(platform, "📌")


def _plugin_icon_color(idx):
    colors = [
        "var(--accent-glow)", "var(--green-glow)", "var(--purple-glow)", "var(--yellow-glow)",
        "#ec4899"
    ]
    return colors[idx % len(colors)]


def _status_icon(status):
    if status.startswith(("ok", "exit_0")):
        return "status-ok"
    if status == "interrupted":
        return "status-warn st-warn"
    return "status-err st-err"


def _status_text(status):
    if status.startswith(("ok", "exit_0")):
        return "OK"
    if status == "interrupted":
        return "Interrompido"
    return status


DAYS_PT = [
    "Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"
]


def _day_pips(days: list) -> str:
    active_days_pt = {
        "Segunda-feira": 0,
        "Terça-feira": 1,
        "Segunda": 0,
        "Terca": 1,
        "Terça": 1,
        "Quarta-feira": 2,
        "Quarta": 2,
        "Quinta-feira": 3,
        "Quinta": 3,
        "Sexta-feira": 4,
        "Sexta": 4,
        "Sábado": 5,
        "Sabado": 5,
        "Sábado": 5,
        "Domingo": 6,
    }
    active = set()
    for d in days:
        if d in active_days_pt:
            active.add(active_days_pt[d])
    if not active:
        return '<span style="color:var(--text-muted);font-size:0.8em">Todos</span>'
    pips = ""
    for i, label in enumerate(DAYS_PT):
        cls = "day-pip active" if i in active else "day-pip"
        pips += f'<div class="{cls}" title="{label}"></div>'
    return f'<div class="day-pips">{pips}</div>'


def generate_page() -> str:
    import myc.agent as agent_mod
    from myc.agent import _load_agents, _load_history
    from myc.config import load_config
    from myc.plugin_installer import get_plugin_meta

    agents = _load_agents()
    history = _load_history()
    config = load_config()
    commands = config.get("commands", {})

    routine_count = 0
    for grp in commands.values():
        routine_count += len(grp.get("subcommands", {}))

    installed_plugins = 0
    plugin_dir = _Path.home() / ".myc" / "agents" / "plugins"
    plugin_list = []
    if plugin_dir.exists():
        plugin_list = sorted(p for p in plugin_dir.glob("*.py") if not p.name.startswith("_"))
        installed_plugins = len(plugin_list)

    stats = _stats(agents, history, routine_count, installed_plugins)

    # ── Head ──
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MYC Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
""" + CSS + "</style>\n<script>\n" + JS + "\n</script>\n</head>\n<body>\n"

    body = (
        '<div class="container">\n'
        '  <div class="topnav">\n'
        '    <div class="logo">\n'
        '      <div class="logo-mark">MYC</div>\n'
        '      <div><h1>My Commands</h1>\n'
        '        <span class="sub">Painel de Controle</span>\n'
        '        <span class="sub" style="margin-left:8px">●</span>\n'
        '        <span class="sub" id="today-badge" style="margin-left:6px"></span>\n'
        '      </div>\n'
        '    </div>\n'
        '    <div class="nav-actions">\n'
        '      <button class="nav-btn active" id="nav-agents" onclick="showSection(\'agents\')">Agentes</button>\n'
        '      <button class="nav-btn" id="nav-routines" onclick="showSection(\'routines\')">Rotinas</button>\n'
        '      <button class="nav-btn" id="nav-plugins" onclick="showSection(\'plugins\')">Plugins</button>\n'
        '      <button class="nav-btn" id="nav-history" onclick="showSection(\'history\')">Historico</button>\n'
        '      <button class="nav-btn" id="nav-stats" onclick="showSection(\'stats\')">Estatisticas</button>\n'
        '    </div>\n'
        '  </div>\n'
    )

    # ── Stats cards ──
    success_rate = (
        f"{100 * stats['successful'] / stats['launches']:.0f}%"
        if stats["launches"] > 0
        else "—"
    )
    body += """<div class="stats-grid">\n"""
    box_items = [
        ("#58a6ff", stats["agents"], "Agentes", f"{len(agents)} configurados"),
        ("#10b981", stats["plugins"], "Plugins", f"{installed_plugins} ativos"),
        ("#a78bfa", stats["routines"], "Rotinas", f"{routine_count} agendadas"),
        ("#f59e0b", stats["launches"], "Lancamentos", str(stats["launches"]) + " total"),
        ("#10b981", stats["successful"], "Sucessos", f"Taxa {success_rate}"),
        ("#ef4444", stats["errors"], "Erros", str(stats["errors"])),
    ]
    colors_css = ["", "green", "purple", "yellow", "green", "red"]
    for (clr, num, label, sub), color_cls in zip(box_items, colors_css):
        body += (
            f'  <div class="stat-card {color_cls}">\n'
            f'    <div class="stat-num" style="color:{clr}">{num}</div>\n'
            f'    <div class="stat-label">{label}</div>\n'
            f'    <div class="stat-sub">{sub}</div>\n'
            '  </div>\n'
        )
    body += "</div>\n"

    # ── AGENTS SECTION ──
    body += '<div class="section active" id="s-agents">\n'

    body += (
        '<div class="card">\n'
        f"  <div class=\"card-header\">\n"
        f"    <div class=\"card-title\">\n"
        f"      <span>🤖 Agentes Configurados</span>\n"
        f'      <span class="card-badge">{len(agents)}</span>\n'
        f"    </div>\n"
        f'    <div style="display:flex;gap:8px;align-items:center">\n'
        f'      <input type="text" class="search-box" placeholder="Buscar agente..."'
        f'        oninput="filterTable(\'agent-tbl\', this.value)">\n'
        f'      <button class="nav-btn primary" onclick="openModal(\'new-agent-modal\')">+ Novo Agente</button>\n'
        f'    </div>\n'
        f"  </div>\n"
    )

    if agents:
        body += (
            f'<div class="table-wrap"><table id="agent-tbl">\n'
            f'<thead><tr>'
            f'<th>Nome</th><th>Plataforma</th><th>Rotinas</th>'
            f'<th>CWD</th><th>Acoes</th>'
            f'</tr></thead>\n<tbody>\n'
        )
        for name, profile in agents.items():
            plat = profile.get("platform", "?")
            routines = profile.get("linked_routines", [])
            cwd = profile.get("cwd", "-") or "-"
            linked_str = ""
            for r in routines:
                linked_str += f'<span class="tag">{r}</span>'
            icon, badge_cls = _platform_badge(plat)

            body += (
                f'<tr>\n'
                f'  <td><strong style="display:flex;align-items:center;gap:8px">'
                f'<span>{icon}</span> {name}</strong></td>\n'
                f'  <td><span class="{badge_cls}" style="font-size:0.75em;padding:3px 8px;'
                f'border-radius:6px;background:var(--purple-glow);color:var(--purple)">'
                f'{plat}</span></td>\n'
                f'  <td><div class="tags-row">{linked_str if linked_str else "-"}</div></td>\n'
                f'  <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'
                f'font-size:0.82em;color:var(--text-dim)">{cwd}</td>\n'
                f'  <td style="display:flex;gap:6px">\n'
                f'    <button class="launch-btn" id="lp-{name}"'
                f'       onclick="launchAgent(\'{name}\')">Lancar</button>\n'
                f'    <button class="delete-btn" onclick="deleteAgent(\'{name}\')">Remover</button>\n'
                f'  </td>\n'
                f'</tr>\n'
            )
        body += '</tbody></table></div>\n'

        # ── Env vars detail ──
        for name, profile in agents.items():
            env = profile.get("env", {})
            if env:
                body += (
                    f'<div style="margin-top:16px">\n'
                    f'<details style="color:var(--text-dim);font-size:0.85em">\n'
                    f'<summary style="cursor:pointer;padding:6px 0"><strong>{name}</strong> — Variaveis de ambiente</summary>\n'
                    f'<div class="env-grid" style="margin-top:8px">\n'
                )
                for k, v, secret in _env_rows(env):
                    cls = "env-val secret" if secret else "env-val"
                    onck = " onclick=\"toggleSecret(this)\"" if secret else ""
                    body += (
                        f'<div class="env-row"><span class="env-key">{k}</span>'
                        f'<span class="{cls}"{onck}>{v}</span></div>\n'
                    )
                body += '</div></details></div>\n'
    else:
        body += (
            '<div class="empty-state">\n'
            '  <div class="icon">🤖</div>\n'
            '  <h3>Nenhum agente configurado</h3>\n'
            '  <p>Clique em "+ Novo Agente" para criar seu primeiro agente de IA.</p>\n'
            '  <p style="font-size:0.8em;color:var(--text-muted)">Voce tambem pode usar <code>myc agent add</code> no terminal.</p>\n'
            '</div>\n'
        )

    body += '</div></div>\n'

    # ── MODAL: New Agent ──
    plat_options = [
        ("openclaude", "OpenClaude (OpenAI API)"),
        ("cursor", "Cursor Editor"),
        ("vscode_copilot", "VS Code + Copilot"),
        ("codex", "OpenAI Codex"),
        ("custom", "Comando customizado"),
    ]
    modal_opts = ""
    for val, lbl in plat_options:
        icn, _ = _platform_badge(val)
        modal_opts += f'<option value="{val}">{icn} {lbl}</option>'

    body += (
        f'<div class="modal-overlay" id="new-agent-modal">\n'
        f'<div class="modal">\n'
        f'  <h2>Novo Agente</h2>\n'
        f'  <label>Nome</label>\n'
        f'  <input type="text" id="na-name" placeholder="ex: dev, estudo...">\n'
        f'  <label>Plataforma</label>\n'
        f'  <select id="na-plat">{modal_opts}</select>\n'
        f'  <label>Diretorio (vazio = atual)</label>\n'
        f'  <input type="text" id="na-cwd" placeholder="C:\\Users\\samue\\projects...">\n'
        f'  <div class="modal-actions">\n'
        f'    <button style="background:var(--bg);color:var(--text);border:1px solid var(--border)"'
        f'       onclick="closeModal(\'new-agent-modal\')">Cancelar</button>\n'
        f'    <button style="background:var(--accent);color:#fff" onclick="submitAgent()">Criar</button>\n'
        f'  </div>\n'
        '  <script>\n'
        '  function submitAgent(){\n'
        '    var body = {\n'
        '      name: document.getElementById("na-name").value,\n'
        '      platform: document.getElementById("na-plat").value,\n'
        '      cwd: document.getElementById("na-cwd").value,\n'
        '    };\n'
        '    fetch("/api/create-agent", {\n'
        '      method:"POST",\n'
        '      headers:{"Content-Type":"application/json"},\n'
        '      body: JSON.stringify(body)\n'
        '    }).then(function(){ location.reload(); });\n'
        '  }\n'
        '  </script>\n'
        f'</div></div>\n'
    )

    # ── ROUTINES SECTION ──
    body += '<div class="section" id="s-routines">\n'
    if commands:
        for grp_name, grp_data in commands.items():
            subs = grp_data.get("subcommands", {})
            emoji = "📋"
            body += (
                f'<div class="card">\n'
                f'  <div class="card-header">\n'
                f'    <div class="card-title"><span>{emoji}</span> Grupo: {grp_name}'
                f'      <span class="card-badge badge-green">{len(subs)} rotinas</span></div>\n'
                f'    <input type="text" class="search-box" style="max-width:250px"'
                f' placeholder="Filtrar..."'
                f' data-tbl="tbl-{grp_name}"'
                f' oninput="filterTable(\'tbl-{grp_name}\', this.value)">\n'
                f'  </div>\n'
            )
            body += (
                f'<div class="table-wrap"><table id="tbl-{grp_name}">\n'
                f'<thead><tr><th>Subcomando</th><th>Descricao</th><th>Dias</th><th>Acoes</th></tr></thead>\n'
                f'<tbody>\n'
            )
            for sub_name, sub_data in subs.items():
                days = sub_data.get("days", [])
                n_acts = len(sub_data.get("actions", []))
                desc = sub_data.get("description", "-")
                body += (
                    f'<tr>'
                    f'<td><code>{sub_name}</code></td>'
                    f'<td>{desc}</td>'
                    f'<td>{_day_pips(days)}</td>'
                    f'<td style="color:var(--text-dim)">{n_acts} acoes</td>'
                    f'</tr>\n'
                )
            body += "</tbody></table></div>\n</div>\n"
    else:
        body += (
            '<div class="empty-state">\n'
            '  <div class="icon">📋</div>\n'
            '  <h3>Nenhuma rotina cadastrada</h3>\n'
            '  <p>Use <code>myc add</code> para adicionar rotinas.</p>\n'
            '</div>\n'
        )
    body += '</div>\n'

    # ── PLUGINS SECTION ──
    body += '<div class="section" id="s-plugins">\n'
    if plugin_list:
        # Group by bundle if we can read __init__
        body += (
            '<div class="card">\n'
            f'  <div class="card-header">\n'
            f'    <div class="card-title"><span>🔌 Plugins Instalados</span>'
            f'      <span class="card-badge badge-purple">{installed_plugins}</span></div>\n'
            f'    <input type="text" class="search-box" style="max-width:250px"'
            f' placeholder="Filtrar..."'
            f' data-tbl="plug-tbl"'
            f' oninput="filterTable(\'plug-tbl\', this.value)">\n'
            f'  </div>\n'
            f'  <div id="plug-list">\n'
        )
        for i, p in enumerate(plugin_list):
            meta = get_plugin_meta(p.stem)
            pname = meta.get("name", p.stem) if meta else p.stem
            pdesc = meta.get("description", "") if meta else ""
            c = _plugin_icon_color(i)
            body += (
                f'<div class="plugin-item">\n'
                f'  <div class="plugin-icon" style="background:{c}">{_platform_icon(p.stem[:4])}</div>\n'
                f'  <div>\n'
                f'    <div class="plugin-name">{pname}</div>\n'
                f'    <div class="plugin-desc">{pdesc}</div>\n'
                f'    <div style="font-size:0.72em;color:var(--text-muted);margin-top:4px">'
                f'<code>{p.name}</code></div>\n'
                f'  </div>\n'
                f'</div>\n'
            )
        body += '  </div>\n</div>\n'
    else:
        body += (
            '<div class="empty-state">\n'
            '  <div class="icon">🔌</div>\n'
            '  <h3>Nenhum plugin instalado</h3>\n'
            '  <p>Use <code>myc agent bundle-install --all</code> para instalar todos.</p>\n'
            '</div>\n'
        )
    body += '</div>\n'

    # ── HISTORY SECTION ──
    body += '<div class="section" id="s-history">\n'

    if history:
        rate = 100 * stats["successful"] / stats["launches"] if stats["launches"] > 0 else 0
        bar_cls = "med" if rate < 60 else ("low" if rate < 30 else "")
        body += (
            f'<div class="card">\n'
            f'  <div class="card-header">\n'
            f'    <div class="card-title"><span>📈 Taxa de Sucesso</span></div>\n'
            f'  </div>\n'
            f'  <div class="rate-display">\n'
            f'    <div class="rate-cpct">{rate:.0f}%</div>\n'
            f'    <div class="rate-label">{stats["successful"]} de {stats["launches"]} lancamentos</div>\n'
            f'  </div>\n'
            f'  <div class="progress-bar"><div class="progress-fill {bar_cls}" style="width:{rate}%"></div></div>\n'
            f'</div>\n'
        )

        body += (
            f'<div class="card">\n'
            f'  <div class="card-header">\n'
            f'    <div class="card-title"><span>📜 Historico</span>'
            f'      <span class="card-badge badge-yellow">{len(history)} entradas</span></div>\n'
            f'    <input type="text" class="search-box" style="max-width:250px"'
            f' placeholder="Filtrar..."'
            f' data-tbl="hist-tbl"'
            f' oninput="filterTable(\'hist-tbl\', this.value)">\n'
            f'  </div>\n'
            f'  <div class="table-wrap"><table id="hist-tbl">\n'
            f'<thead><tr><th>Data</th><th>Agente</th><th>Plataforma</th>'
            f'<th>Rotina</th><th>Status</th><th>Diretorio</th></tr></thead>\n<tbody>\n'
        )
        for h in history[:100]:
            dt = h.get("timestamp", "")[:16]
            st = h.get("status", "unknown")
            st_class = _status_icon(st)
            st_text = _status_text(st)
            dir_short = h.get("cwd", "-")
            body += (
                f'<tr>'
                f'<td style="white-space:nowrap;font-size:0.82em">{dt}</td>'
                f'<td><strong>{h.get("agent", "?")}</strong></td>'
                f'<td>{h.get("platform", "?")}</td>'
                f'<td>{h.get("routine", "-")}</td>'
                f'<td><span class="{st_class}">{st_text}</span></td>'
                f'<td style="font-size:0.78em;color:var(--text-dim);max-width:180px;'
                f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{dir_short}</td>'
                f'</tr>\n'
            )
        body += "</tbody></table></div>\n</div>\n"
    else:
        body += (
            '<div class="empty-state">\n'
            '  <div class="icon">📜</div>\n'
            '  <h3>Nenhum registro no historico</h3>\n'
            '  <p>Os lancamentos de agentes aparecerão aqui.</p>\n'
            '</div>\n'
        )
    body += '</div>\n'

    # ── STATS SECTION ──
    body += '<div class="section" id="s-stats">\n'

    # Agent summary
    agents_launch_count = {}
    for h in history:
        an = h.get("agent", "?")
        agents_launch_count[an] = agents_launch_count.get(an, 0) + 1

    body += (
        f'<div class="card">\n'
        f'  <div class="card-header">\n'
        f'    <div class="card-title"><span>📊 Distribuicao por Agente</span></div>\n'
        f'  </div>\n'
    )
    max_count = max(agents_launch_count.values()) if agents_launch_count else 1
    for an, cnt in sorted(agents_launch_count.items(), key=lambda x: -x[1]):
        pct = 100 * cnt / max_count
        body += (
            f'<div style="margin-bottom:12px">\n'
            f'  <div style="display:flex;justify-content:space-between;font-size:0.85em">'
            f'<strong>{an}</strong><span style="color:var(--text-dim)">{cnt} lancamentos</span></div>\n'
            f'  <div class="progress-bar"><div class="progress-fill" style="width:{pct}%"></div></div>\n'
            f'</div>\n'
        )
    if not agents_launch_count:
        body += '<p style="color:var(--text-muted);font-size:0.85em;text-align:center">Sem dados de lancamento.</p>\n'
    body += '</div>\n'

    # Platform breakdown
    plat_counts = {}
    for h in history:
        p = h.get("platform", "?")
        plat_counts[p] = plat_counts.get(p, 0) + 1
    if plat_counts:
        body += (
            f'<div class="card" style="margin-top:16px">\n'
            f'  <div class="card-header">\n'
            f'    <div class="card-title"><span>⚡ Por Plataforma</span></div>\n'
            f'  </div>\n'
        )
        for plat, cnt in sorted(plat_counts.items(), key=lambda x: -x[1]):
            icn = _platform_icon(plat)
            body += (
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'padding:10px 0;border-bottom:1px solid var(--bg)">'
                f'<span style="font-size:0.9em">{icn} {plat}</span>'
                f'<strong style="color:var(--text-dim)">{cnt}</strong>'
                f'</div>\n'
            )
        body += '</div>\n'

    body += '</div>\n'

    # Close container and body/html
    body += (
        '</div>\n'  # close container
        '</body>\n'
        '</html>\n'
    )

    return body


def serve_dashboard(port: int = 8787) -> None:
    """Servidor HTTP local que entrega o dashboard."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading
    import webbrowser
    from urllib.parse import urlparse

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/" or path == "/index.html":
                self._send_html(generate_page())
            elif path.startswith("/launch/"):
                name = path.split("/launch/")[1].split("?")[0]
                self._handle_launch(name)
            elif path == "/api/stats":
                self._send_json({"ok": True, "msg": "Dashboard ativo"})
            else:
                self.send_error(404)

        def do_POST(self):
            path = urlparse(self.path).path
            if path == "/api/create-agent":
                self._handle_create_agent()

        def do_DELETE(self):
            path = urlparse(self.path).path
            if path.startswith("/delete/"):
                name = path.rsplit("/", 1)[-1]
                self._handle_delete_agent(name)
            else:
                self.send_error(404)

        def _send_html(self, content: str):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(content.encode("utf-8")))
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))

        def _send_json(self, data: dict):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(_json.dumps(data).encode("utf-8"))

        def _handle_launch(self, name: str):
            from myc.agent import launch_agent
            threading.Thread(target=lambda: launch_agent(name), daemon=True).start()
            self._send_json({"status": "launching", "agent": name})

        def _handle_create_agent(self):
            try:
                import questionary
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                data = _json.loads(body)
                name = data.get("name", "").strip()
                platform = data.get("platform", "openclaude")
                cwd = data.get("cwd", "").strip() or None

                if not name or " " in name:
                    self.send_response(400)
                    self.end_headers()
                    return

                from myc.agent import _load_agents, _save_agents
                agents = _load_agents()
                agents[name] = {
                    "name": name,
                    "platform": platform,
                    "env": {},
                    "cwd": cwd,
                    "initial_context": "",
                    "custom_command": None,
                    "linked_routines": [],
                    "created_at": _datetime.now().isoformat(),
                }
                _save_agents(agents)
                self._send_json({"status": "created", "agent": name})
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))

        def _handle_delete_agent(self, name: str):
            try:
                from myc.agent import _load_agents, _save_agents
                agents = _load_agents()
                if name in agents:
                    del agents[name]
                    _save_agents(agents)
                    self._send_json({"status": "deleted"})
                else:
                    self.send_error(404)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))

        def log_message(self, fmt, *args):
            pass

    url = f"http://localhost:{port}"
    print(f"\n[bold cyan]Dashboard MYC:[/bold cyan] {url}\n[dim]Abra no navegador ou aguarde abertura automatica...[/dim]")
    threading.Thread(target=lambda: webbrowser.open(url), daemon=True).start()

    server = HTTPServer(("127.0.0.1", port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
