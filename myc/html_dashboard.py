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
    --pink: #ec4899;
    --pink-glow: rgba(236, 72, 153, 0.15);
    --cyan: #06b6d4;
    --cyan-glow: rgba(6, 182, 212, 0.15);
    --orange: #f97316;
    --orange-glow: rgba(249, 115, 22, 0.15);
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

/* TABS within sections */
.sub-tabs {
    display: flex; gap: 4px; margin-bottom: 16px; flex-wrap: wrap;
    background: var(--bg); border-radius: var(--radius-sm); padding: 4px;
}
.sub-tab {
    background: transparent; border: none; color: var(--text-dim);
    padding: 6px 14px; border-radius: 6px; cursor: pointer;
    font-size: 0.8em; font-weight: 500; transition: 0.2s;
}
.sub-tab:hover { color: var(--text); background: var(--bg-hover); }
.sub-tab.active { background: var(--accent); color: #fff; }

.sub-panel { display: none; }
.sub-panel.active { display: block; }

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
.stat-card.pink::after { background: linear-gradient(90deg, #ec4899, #f472b6); }
.stat-card.cyan::after { background: linear-gradient(90deg, #06b6d4, #22d3ee); }
.stat-card.orange::after { background: linear-gradient(90deg, #f97316, #fb923c); }
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
.badge-pink { background: var(--pink-glow); color: var(--pink); }
.badge-cyan { background: var(--cyan-glow); color: var(--cyan); }
.badge-orange { background: var(--orange-glow); color: var(--orange); }

/* AGENT CARDS */
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
.tag-green { background: var(--green-glow); color: var(--green); border-color: rgba(16,185,129,0.3); }
.tag-purple { background: var(--purple-glow); color: var(--purple); border-color: rgba(139,92,246,0.3); }
.tag-pink { background: var(--pink-glow); color: var(--pink); border-color: rgba(236,72,153,0.3); }
.tag-cyan { background: var(--cyan-glow); color: var(--cyan); border-color: rgba(6,182,212,0.3); }
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
    width: 90%; max-width: 600px; max-height: 85vh; overflow-y: auto;
    box-shadow: var(--shadow-lg);
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
.modal .checkbox-group {
    max-height: 150px; overflow-y: auto; margin-bottom: 14px;
    background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 10px;
}
.modal .checkbox-group label {
    display: flex; align-items: center; gap: 8px; cursor: pointer;
    padding: 4px 0; font-size: 0.85em; margin-bottom: 0;
}
.modal .checkbox-group label:hover { color: var(--accent); }

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

/* PLUGIN ITEMS */
.plugin-item {
    display: flex; align-items: center; gap: 14px;
    padding: 14px; border-radius: 10px; margin-bottom: 8px;
    background: var(--bg); border: 1px solid transparent;
    transition: 0.15s;
}
.plugin-item:hover { border-color: var(--border); background: var(--bg-hover); }
.plugin-icon {
    width: 40px; height: 40px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
}
.plugin-name { font-weight: 600; font-size: 0.9em; }
.plugin-desc { font-size: 0.78em; color: var(--text-dim); margin-top: 2px; }

/* COMPANY CARD */
.company-card {
    background: var(--bg); border-radius: 10px; padding: 16px; margin-bottom: 12px;
    border: 1px solid var(--border);
}
.company-card h4 {
    font-size: 0.95em; margin-bottom: 4px;
    display: flex; align-items: center; gap: 8px;
}
.dept-section { margin-top: 12px; }
.dept-title {
    font-size: 0.8em; color: var(--text-muted); text-transform: uppercase;
    letter-spacing: 0.5px; font-weight: 600; margin-bottom: 6px;
    padding-bottom: 4px; border-bottom: 1px solid var(--border);
}
.specialist-chips { display: flex; flex-wrap: wrap; gap: 4px; }
.spec-chip {
    font-size: 0.72em; padding: 3px 8px; border-radius: 5px;
    background: var(--bg-card); border: 1px solid var(--border);
    color: var(--text-dim); transition: 0.2s;
}
.spec-chip:hover { border-color: var(--accent); color: var(--accent); }

/* BUNDLE CARD */
.bundle-card {
    display: flex; align-items: center; gap: 16px;
    padding: 16px; border-radius: 10px; margin-bottom: 8px;
    background: var(--bg); border: 1px solid var(--border);
    transition: 0.15s;
}
.bundle-card:hover { border-color: var(--accent); background: var(--bg-hover); }
.bundle-icon {
    width: 48px; height: 48px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; flex-shrink: 0;
}
.bundle-info { flex: 1; min-width: 0; }
.bundle-name { font-weight: 600; font-size: 0.95em; }
.bundle-desc { font-size: 0.78em; color: var(--text-dim); margin-top: 2px; }
.bundle-plugins { font-size: 0.72em; color: var(--text-muted); margin-top: 4px; }
.bundle-actions { display: flex; gap: 8px; flex-shrink: 0; }
.install-btn {
    background: var(--accent); border: none; color: #fff;
    padding: 6px 14px; border-radius: 6px; cursor: pointer;
    font-size: 0.78em; font-weight: 600; transition: 0.2s;
}
.install-btn:hover { background: #2563eb; }
.install-btn:disabled { opacity: 0.5; cursor: default; background: var(--green); }

/* DOCS */
.doc-section {
    margin-bottom: 20px;
}
.doc-section h3 {
    font-size: 1em; margin-bottom: 8px;
    padding-left: 12px; border-left: 3px solid var(--accent);
}
.doc-section p, .doc-section li {
    font-size: 0.85em; color: var(--text-dim); line-height: 1.6;
}
.doc-section code {
    font-size: 0.85em;
}
.doc-section pre {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; padding: 12px; margin: 8px 0;
    overflow-x: auto; font-size: 0.78em; line-height: 1.5;
}
.doc-section ul { padding-left: 20px; }
.doc-section li { margin-bottom: 4px; }

/* RESPONSIVE */
@media (max-width: 768px) {
    .container { padding: 16px; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
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

function filterNodes(containerId, q) {
    q = q.toLowerCase();
    document.querySelectorAll('#' + containerId + ' > *').forEach(function(el) {
        el.style.display = el.textContent.toLowerCase().includes(q) ? '' : 'none';
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

function showSubPanel(group, panel) {
    var parent = document.getElementById('ps-' + group);
    if (parent) parent.querySelectorAll('.sub-panel').forEach(p => p.classList.remove('active'));
    var target = document.getElementById('panel-' + group + '-' + panel);
    if (target) target.classList.add('active');
    var btns = parent ? parent.querySelectorAll('.sub-tab') : [];
    btns.forEach(function(b) {
        b.classList.toggle('active', b.dataset.sub === panel);
    });
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
            setTimeout(function(){ location.reload(); }, 2000);
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

function installPlugin(pluginId) {
    if (!confirm('Instalar plugin "' + pluginId + '"?')) return;
    fetch('/install-plugin/' + encodeURIComponent(pluginId), {method:'POST'})
        .then(function(r){return r.json();})
        .then(function(d){
            if (d.ok) { alert('Plugin instalado!'); location.reload(); }
            else { alert('Erro: ' + d.error); }
        }).catch(function(){ alert('Erro ao instalar plugin'); });
}

function installCompanyPlugin(companyId) {
    if (!confirm('Instalar empresa "' + companyId + '"?')) return;
    fetch('/install-company/' + encodeURIComponent(companyId), {method:'POST'})
        .then(function(r){return r.json();})
        .then(function(d){
            if (d.ok) { alert('Empresa instalada!'); location.reload(); }
            else { alert('Erro: ' + d.error); }
        }).catch(function(){ alert('Erro ao instalar empresa'); });
}

function uninstallPlugin(pluginId) {
    if (!confirm('Desinstalar plugin "' + pluginId + '"?')) return;
    fetch('/uninstall-plugin/' + encodeURIComponent(pluginId), {method:'POST'})
        .then(function(r){return r.json();})
        .then(function(d){
            if (d.ok) { location.reload(); }
            else { alert('Erro: ' + d.error); }
        }).catch(function(){ alert('Erro ao desinstalar'); });
}

function openModal(id) {
    var m = document.getElementById(id);
    if (m) { m.style.display='flex'; requestAnimationFrame(function(){m.classList.add('show');}); }
}
function closeModal(id) {
    var m = document.getElementById(id);
    if (m) { m.classList.remove('show'); m.style.display='none'; }
}

document.addEventListener('keydown', function(e){
    if(e.key==='Escape') {
        document.querySelectorAll('.modal-overlay.show').forEach(function(m){ closeModal(m.id); });
    }
});

var now = new Date();
var today = ['Domingo','Segunda-feira','Ter\\u00e7a-feira','Quarta-feira','Quinta-feira','Sexta-feira','S\\u00e1bado'][now.getDay()];
var el = document.getElementById('today-badge');
if(el) el.textContent = today;

var ts = new Date();
var tsEl = document.getElementById('gen-ts');
if (tsEl) tsEl.textContent = ts.toLocaleString('pt-BR');
"""


def _stats(agents_list, history_list, routines_count, plugins_count, companies_count, middlewares_count):
    ok = sum(
        1 for h in history_list
        if h.get("status", "").startswith(("ok", "exit_0"))
    )
    errs = len(history_list) - ok
    return {
        "agents": len(agents_list),
        "plugins": plugins_count,
        "companies": companies_count,
        "middlewares": middlewares_count,
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
        "openclaude": ("\\U0001f916", "badge-purple"),
        "cursor": ("\\U0001f4bb", ""),
        "vscode_copilot": ("\\u26a1", ""),
        "codex": ("\\U0001f9e0", "badge-green"),
        "custom": ("\\u2699\\ufe0f", "badge-yellow"),
    }.get(platform, ("\\u2753", ""))


def _platform_icon(platform):
    return {
        "openclaude": "\\U0001f916",
        "cursor": "\\U0001f4bb",
        "vscode_copilot": "\\u26a1",
        "codex": "\\U0001f9e0",
        "custom": "\\u2699\\ufe0f",
    }.get(platform, "\\U0001f4cc")


def _plugin_icon_color(idx):
    colors = [
        "var(--accent-glow)", "var(--green-glow)", "var(--purple-glow)",
        "var(--yellow-glow)", "var(--pink-glow)", "var(--cyan-glow)", "var(--orange-glow)",
    ]
    return colors[idx % len(colors)]


def _company_icon(idx):
    icons = [
        "\\U0001f3e2", "\\U0001f3d7\\ufe0f", "\\U0001f3a8", "\\U0001f4bc",
        "\\U0001f52c", "\\U0001f4da", "\\U0001f3ae", "\\U0001f4f0",
        "\\u2696\\ufe0f", "\\U0001f3b5", "\\U0001f3c6", "\\U0001f449\\U0001f448",
    ]
    return icons[idx % len(icons)]


def _middleware_icon(idx):
    icons = ["\\U0001f500", "\\U0001f6e1\\ufe0f", "\\U0001faf6"]
    return icons[idx % len(icons)]


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
        "Segunda-feira": 0, "Ter\\u00e7a-feira": 1,
        "Segunda": 0, "Terca": 1, "Ter\\u00e7a": 1,
        "Quarta-feira": 2, "Quarta": 2,
        "Quinta-feira": 3, "Quinta": 3,
        "Sexta-feira": 4, "Sexta": 4,
        "S\\u00e1bado": 5, "Sabado": 5,
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


# ── Bundle metadata for dashboard ──

BUNDLE_META = {
    "marketing": {
        "name": "Agencia de Marketing",
        "description": "Redes sociais, SEO, copywriting, campanhas, analytics",
        "plugins": ["social_media", "seo_analyst", "copywriter", "campaign_manager"],
        "icon": "\\U0001f4e3",
        "color": "var(--pink-glow)",
    },
    "gamedesign": {
        "name": "Estudio de Game Design",
        "description": "Level design, narrativa interativa, mecanicas, balanco, UX de jogo",
        "plugins": ["level_designer", "game_narrative", "mechanics_balancer", "game_ux"],
        "icon": "\\U0001f3ae",
        "color": "var(--purple-glow)",
    },
    "advocacia": {
        "name": "Escritorio de Advocacia (BR)",
        "description": "Legislacao brasileira, contratos, peticoes, jurisprudencia",
        "plugins": ["legislacao_br", "contratos_br", "peticoes", "jurisprudencia"],
        "icon": "\\u2696\\ufe0f",
        "color": "var(--cyan-glow)",
    },
    "jornalismo": {
        "name": "Redacao Jornalistica",
        "description": "Pautas, reportagens, fact-checking, redacao, editoriais",
        "plugins": ["pauta_journal", "fact_checker", "redacao_news", "editorial"],
        "icon": "\\U0001f4f0",
        "color": "var(--yellow-glow)",
    },
    "osint": {
        "name": "Inteligencia OSINT",
        "description": "Investigacao digital, fonte aberta, analise de dados publicos",
        "plugins": ["osint_collector", "source_analyzer", "digital_footprint", "data_correlator"],
        "icon": "\\U0001f50d",
        "color": "var(--accent-glow)",
    },
    "seguranca_web": {
        "name": "Seguranca Web",
        "description": "Auditoria web, OWASP, pentest, hardening",
        "plugins": ["web_auditor", "owasp_checker", "pentest_helper", "hardening_guide"],
        "icon": "\\U0001f6e1\\ufe0f",
        "color": "var(--green-glow)",
    },
    "bugbounty": {
        "name": "Bug Bounty Hunter",
        "description": "Recon, exploit writing, report, triagem",
        "plugins": ["recon", "exploit_writer", "bounty_report", "vuln_triage"],
        "icon": "\\U0001f41b",
        "color": "var(--orange-glow)",
    },
    "visao_computacional": {
        "name": "Engenharia de Visao Computacional",
        "description": "CNN, deteccao de objetos, segmentacao, OpenCV, PyTorch",
        "plugins": ["cv_architect", "dataset_builder", "model_trainer", "cv_deployer"],
        "icon": "\\U0001f441\\ufe0f",
        "color": "var(--purple-glow)",
    },
    "fullstack": {
        "name": "Desenvolvimento Full Stack",
        "description": "Frontend, backend, banco de dados, deploy, DevOps",
        "plugins": ["frontend_dev", "backend_dev", "database_designer", "devops_deploy"],
        "icon": "\\U0001f4bb",
        "color": "var(--accent-glow)",
    },
    "app_mobile": {
        "name": "Desenvolvimento de App Mobile",
        "description": "React Native, Flutter, iOS, Android, UI/UX mobile",
        "plugins": ["mobile_architect", "ui_mobile", "native_bridge", "app_store_prep"],
        "icon": "\\U0001f4f1",
        "color": "var(--green-glow)",
    },
    "ideias": {
        "name": "Gerador de Ideias",
        "description": "Brainstorming, design thinking, validacao, prototipagem rapida",
        "plugins": ["brainstorm", "design_thinking", "idea_validator", "mvp_builder"],
        "icon": "\\U0001f4a1",
        "color": "var(--yellow-glow)",
    },
    "vendas": {
        "name": "Vendas e Empreendedorismo",
        "description": "Pitch, funil de vendas, modelo de negocio, growth hacking",
        "plugins": ["sales_pitch", "sales_funnel", "business_model", "growth_hacker"],
        "icon": "\\U0001f4b5",
        "color": "var(--green-glow)",
    },
    "data_engineering": {
        "name": "Engenharia de Dados",
        "description": "ETL, pipelines, data warehouse, Spark, Airflow",
        "plugins": ["etl_builder", "pipeline_designer", "data_quality", "warehouse_architect"],
        "icon": "\\U0001f5c4\\ufe0f",
        "color": "var(--cyan-glow)",
    },
    "software_engineering": {
        "name": "Engenharia de Software",
        "description": "Arquitetura, clean code, design patterns, testes, CI/CD",
        "plugins": ["software_architect", "code_reviewer", "test_engineer", "ci_cd_expert"],
        "icon": "\\u2699\\ufe0f",
        "color": "var(--accent-glow)",
    },
    "computer_engineering": {
        "name": "Engenharia da Computacao",
        "description": "Sistemas embarcados, IoT, redes, sistemas operacionais, hardware",
        "plugins": ["embedded_dev", "iot_engineer", "network_analyzer", "os_internals"],
        "icon": "\\U0001f4e1",
        "color": "var(--orange-glow)",
    },
    "professor": {
        "name": "Professor / Educador",
        "description": "Planejamento de aula, avaliacoes, didatica, conteudo educativo",
        "plugins": ["lesson_planner", "exam_creator", "didatica", "content_creator_edu"],
        "icon": "\\U0001f4da",
        "color": "var(--yellow-glow)",
    },
}

COMPANY_BUNDLE_META = {
    "agencia_marketing_full": {
        "name": "Agencia Marketing Full",
        "description": "Equipe completa de marketing — social media, SEO, copy, campanhas",
        "specialists": ["social_media", "seo_analyst", "copywriter", "campaign_manager"],
        "icon": "\\U0001f4e3",
    },
    "dev_house_full": {
        "name": "Dev House",
        "description": "Equipe de desenvolvimento completa — frontend, backend, database, DevOps",
        "specialists": ["frontend_dev", "backend_dev", "database_designer", "devops_deploy"],
        "icon": "\\U0001f4bb",
    },
    "security_team": {
        "name": "Equipe de Seguranca",
        "description": "Time completo de seguranca — auditoria, OWASP, pentest, hardening",
        "specialists": ["web_auditor", "owasp_checker", "pentest_helper", "hardening_guide"],
        "icon": "\\U0001f6e1\\ufe0f",
    },
}


def _discover_builtin_plugins():
    """Lista plugins built-in disponiveis (specialists)."""
    repo_root = _Path(__file__).parent.parent / "plugins" / "specialists"
    found = []
    if repo_root.exists():
        for p in sorted(repo_root.glob("*.py")):
            if not p.name.startswith("_"):
                found.append(p.stem)
    return found


def _discover_builtin_companies():
    """Lista empresas built-in disponiveis."""
    repo_root = _Path(__file__).parent.parent / "plugins" / "companies"
    found = []
    if repo_root.exists():
        for p in sorted(repo_root.glob("*.py")):
            if not p.name.startswith("_"):
                found.append(p.stem)
    return found


def _discover_builtin_middlewares():
    """Lista middlewares built-in disponiveis."""
    repo_root = _Path(__file__).parent.parent / "plugins" / "middlewares"
    found = []
    if repo_root.exists():
        for p in sorted(repo_root.glob("*.py")):
            if not p.name.startswith("_"):
                found.append(p.stem)
    return found


def _get_specialists_for_company(company_id):
    """Extrai lista de especialistas de um plugin de empresa."""
    from myc.plugin_installer import COMPANIES_DIR, COMPANIES_BUILTIN, get_company_meta

    # Tenta encontrar o arquivo (instalado primeiro, depois builtin)
    source = COMPANIES_DIR / f"{company_id}.py"
    if not source.exists():
        source = COMPANIES_BUILTIN / f"{company_id}.py"
    if not source.exists():
        meta = get_company_meta(company_id)
        if meta and meta.get("specialists"):
            return meta["specialists"]
        return []

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(company_id, source)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            specs = getattr(mod, "SPECIALISTS", [])
            return [s.get("id", s) if isinstance(s, dict) else s for s in specs]
    except Exception:
        pass
    return []


def _get_departments_for_company(company_id):
    """Extrai departamentos e especialistas de um plugin de empresa."""
    from myc.plugin_installer import COMPANIES_DIR, COMPANIES_BUILTIN

    source = COMPANIES_DIR / f"{company_id}.py"
    if not source.exists():
        source = COMPANIES_BUILTIN / f"{company_id}.py"
    if not source.exists():
        return {}

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(company_id, source)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            specs = getattr(mod, "SPECIALISTS", [])
            depts = {}
            for s in specs:
                if isinstance(s, dict):
                    dept = s.get("department", "geral")
                    depts.setdefault(dept, []).append(s)
            return depts
    except Exception:
        pass
    return {}


DOC_SECTION = """
<div class="doc-section">
  <h3>Arquitetura de Plugins MYC</h3>
  <p>O sistema MYC utiliza um ecossistema de plugins modular que permite estender funcionalidades de agentes de IA. Os plugins sao organizados em tres categorias principais:</p>
</div>
<div class="doc-section">
  <h3>1. Specialists (Plugins de Especialista)</h3>
  <p>Plugins individuais que adicionam capacidades especificas a um agente. Cada specialist tem hooks como <code>PRE_LAUNCH</code>, <code>POST_LAUNCH</code> e <code>CONTEXT</code>.</p>
  <ul>
    <li><strong>Local:</strong> <code>~/.myc/agents/plugins/&lt;nome&gt;.py</code></li>
    <li><strong>Source:</strong> <code>plugins/specialists/&lt;nome&gt;.py</code></li>
    <li><strong>Instalacao:</strong> <code>myc agent bundle-install --all</code> ou via Dashboard</li>
  </ul>
  <p>Os specialists sao agrupados em <strong>Bundles</strong> tematicos (ex: marketing, fullstack, osint) para instalacao rapida.</p>
</div>
<div class="doc-section">
  <h3>2. Companies (Empresas)</h3>
  <p>Plugins que definem equipes multi-especialista com contexto compartilhado. Uma empresa agrupa varios specialists organizados por departamentos.</p>
  <ul>
    <li><strong>Local:</strong> <code>~/.myc/agents/companies/&lt;nome&gt;.py</code></li>
    <li><strong>Source:</strong> <code>plugins/companies/&lt;nome&gt;.py</code></li>
    <li><strong>Estrutura:</strong> <code>NAME</code>, <code>DESCRIPTION</code>, <code>SPECIALISTS</code> (lista com id, name, role, department)</li>
  </ul>
  <p>Empresas disponiveis incluem: Dev Agency, Game Studio, Marketing Agency, Law Firm, Accounting Firm, e mais.</p>
</div>
<div class="doc-section">
  <h3>3. Middlewares</h3>
  <p>Camadas intermediarias que modificam o comportamento do agente. Exemplo: <code>guided_flow</code> transforma o agente em um consultor que faz perguntas antes de responder.</p>
  <ul>
    <li><strong>Local:</strong> <code>~/.myc/agents/middlewares/&lt;nome&gt;.py</code></li>
    <li><strong>Source:</strong> <code>plugins/middlewares/&lt;nome&gt;.py</code></li>
    <li><strong>Tipo:</strong> <code>prompt_modifier</code> — modifica o prompt antes do envio</li>
  </ul>
</div>
<div class="doc-section">
  <h3>Comandos Principais</h3>
  <pre>myc agent add                    # Criar agente via wizard
myc agent list                   # Listar agentes
myc agent bundle-install --all   # Instalar todos os bundles
myc agent bundle-install marketing fullstack  # Instalar bundles especificos
myc agent add-plugin &lt;plugin&gt;    # Instalar um specialist
myc agent link-plugin &lt;agente&gt; &lt;plugin&gt;  # Vincular plugin a agente
myc agent docs                   # Abrir esta documentacao</pre>
</div>
<div class="doc-section">
  <h3>Criando um Plugin Customizado</h3>
  <p>Um plugin specialist minimo:</p>
  <pre>NAME = "Meu Plugin"
DESCRIPTION = "Descricao do que o plugin faz"

def PRE_LAUNCH(agent_profile):
    # Executado antes do agente lancar
    print(f"Plugin rodando para {agent_profile.get('name')}")
    return {"extra_context": "Dados do plugin"}

def POST_LAUNCH(agent_profile, result):
    # Executado apos o agente terminar
    print(f"Resultado: {result}")

def CONTEXT(agent_profile):
    # Retorna texto para injetar no CLAUDE.md
    return "Contexto adicional do plugin"</pre>
  <p>Um plugin de empresa minimo:</p>
  <pre>NAME = "Minha Empresa"
DESCRIPTION = "Descricao da empresa"

SPECIALISTS = [
    {
        "id": "especialista_1",
        "name": "Nome do Especialista",
        "role": "Voce e o especialista...",
        "specialists": ["plugin_dependencies"],
        "department": "departamento"
    }
]</pre>
</div>
"""


def generate_page() -> str:
    import myc.agent as agent_mod
    from myc.agent import _load_agents, _load_history
    from myc.config import load_config
    from myc.plugin_installer import (
        get_plugin_meta, get_company_meta, get_middleware_meta,
        PLUGINS_DIR, COMPANIES_DIR, MIDDLEWARES_DIR,
        COMPANIES_BUILTIN,
    )

    agents = _load_agents()
    history = _load_history()
    config = load_config()
    commands = config.get("commands", {})

    routine_count = 0
    for grp in commands.values():
        routine_count += len(grp.get("subcommands", {}))

    # Installed plugins
    plugin_list_installed = sorted(PLUGINS_DIR.glob("*.py")) if PLUGINS_DIR.exists() else []
    installed_plugin_ids = {p.stem for p in plugin_list_installed if not p.name.startswith("_")}
    plugin_meta = {}
    for pid in installed_plugin_ids:
        m = get_plugin_meta(pid)
        plugin_meta[pid] = m if m else {"name": pid, "description": "", "hooks": []}

    # Installed companies
    company_list_installed = sorted(COMPANIES_DIR.glob("*.py")) if COMPANIES_DIR.exists() else []
    installed_company_ids = {p.stem for p in company_list_installed if not p.name.startswith("_")}
    company_meta = {}
    for cid in installed_company_ids:
        m = get_company_meta(cid)
        company_meta[cid] = m if m else {"name": cid, "description": "", "specialists": []}

    # Available companies built-in
    available_company_ids = _discover_builtin_companies()

    # Installed middlewares
    mw_list_installed = sorted(MIDDLEWARES_DIR.glob("*.py")) if MIDDLEWARES_DIR.exists() else []
    installed_mw_ids = {p.stem for p in mw_list_installed if not p.name.startswith("_")}
    mw_meta = {}
    for mid in installed_mw_ids:
        m = get_middleware_meta(mid)
        mw_meta[mid] = m if m else {"name": mid, "description": "", "middleware_type": "unknown"}

    # Available middlewares built-in
    available_mw_ids = _discover_builtin_middlewares()

    # Counts
    builtin_specialist_ids = set(_discover_builtin_plugins())
    builtin_company_ids = set(available_company_ids)
    builtin_mw_ids = set(available_mw_ids)

    stats = _stats(
        agents, history, routine_count,
        len(installed_plugin_ids), len(installed_company_ids), len(installed_mw_ids),
    )

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
        '        <span class="sub" id="gen-ts" style="margin-left:6px;font-size:0.9em;color:var(--text-muted)"></span>\n'
        '      </div>\n'
        '    </div>\n'
        '    <div class="nav-actions">\n'
        '      <button class="nav-btn active" id="nav-agents" onclick="showSection(\'agents\')">Agentes</button>\n'
        '      <button class="nav-btn" id="nav-routines" onclick="showSection(\'routines\')">Rotinas</button>\n'
        '      <button class="nav-btn" id="nav-plugins" onclick="showSection(\'plugins\')">Plugins</button>\n'
        '      <button class="nav-btn" id="nav-companies" onclick="showSection(\'companies\')">Empresas</button>\n'
        '      <button class="nav-btn" id="nav-history" onclick="showSection(\'history\')">Historico</button>\n'
        '      <button class="nav-btn" id="nav-stats" onclick="showSection(\'stats\')">Estatisticas</button>\n'
        '      <button class="nav-btn" id="nav-docs" onclick="showSection(\'docs\')">Docs</button>\n'
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
        ("#10b981", stats["plugins"], "Specialists", f"{len(builtin_specialist_ids)} disponiveis"),
        ("#a78bfa", stats["companies"], "Empresas", f"{len(installed_company_ids)} instaladas"),
        ("#ec4899", stats["middlewares"], "Middlewares", f"{len(installed_mw_ids)} ativos"),
        ("#f59e0b", stats["launches"], "Lancamentos", str(stats["launches"]) + " total"),
        ("#10b981", stats["successful"], "Sucessos", f"Taxa {success_rate}"),
        ("#ef4444", stats["errors"], "Erros", str(stats["errors"])),
    ]
    color_classes = ["", "green", "purple", "pink", "yellow", "green", "red"]
    for (clr, num, label, sub), color_cls in zip(box_items, color_classes):
        body += (
            f'  <div class="stat-card {color_cls}">\n'
            f'    <div class="stat-num" style="color:{clr}">{num}</div>\n'
            f'    <div class="stat-label">{label}</div>\n'
            f'    <div class="stat-sub">{sub}</div>\n'
            '  </div>\n'
        )
    body += "</div>\n"

    # ═══════════════════════════════════════════════════════
    # ── AGENTS SECTION ──
    # ═══════════════════════════════════════════════════════
    body += '<div class="section active" id="s-agents">\n'

    body += (
        '<div class="card">\n'
        f'  <div class="card-header">\n'
        f'    <div class="card-title">\n'
        f'      <span>\\U0001f916 Agentes Configurados</span>\n'
        f'      <span class="card-badge">{len(agents)}</span>\n'
        f'    </div>\n'
        f'    <div style="display:flex;gap:8px;align-items:center">\n'
        f'      <input type="text" class="search-box" placeholder="Buscar agente..."'
        f'        oninput="filterTable(\'agent-tbl\', this.value)">\n'
        f'      <button class="nav-btn primary" onclick="openModal(\'new-agent-modal\')">+ Novo Agente</button>\n'
        f'    </div>\n'
        f'  </div>\n'
    )

    if agents:
        body += (
            f'<div class="table-wrap"><table id="agent-tbl">\n'
            f'<thead><tr>'
            f'<th>Nome</th><th>Plataforma</th><th>Role</th><th>Plugins</th>'
            f'<th>Rotinas</th><th>CWD</th><th>Acoes</th>'
            f'</tr></thead>\n<tbody>\n'
        )
        for name, profile in agents.items():
            plat = profile.get("platform", "?")
            role = profile.get("role", "generalist")
            routines = profile.get("linked_routines", [])
            plugins = profile.get("plugins", [])
            cwd = profile.get("cwd", "-") or "-"
            linked_str = "".join(f'<span class="tag">{r}</span>' for r in routines)
            plugin_str = ""
            for pid in plugins:
                if pid in installed_plugin_ids:
                    plugin_str += f'<span class="tag tag-green">{pid}</span>'
                elif pid in builtin_specialist_ids:
                    plugin_str += f'<span class="tag tag-purple">{pid}*</span>'
                else:
                    plugin_str += f'<span class="tag">{pid}</span>'
            if not plugin_str:
                plugin_str = '<span style="color:var(--text-muted)">-</span>'
            icon, _ = _platform_badge(plat)

            body += (
                f'<tr>\n'
                f'  <td><strong style="display:flex;align-items:center;gap:8px">'
                f'<span>{icon}</span> {name}</strong></td>\n'
                f'  <td><span style="font-size:0.78em;color:var(--text-dim)">{plat}</span></td>\n'
                f'  <td><span class="tag tag-cyan">{role}</span></td>\n'
                f'  <td>{plugin_str}</td>\n'
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
            '  <div class="icon">\\U0001f916</div>\n'
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

    role_options = [
        ("dev", "Desenvolvedor"), ("artist", "Designer/Artista"),
        ("writer", "Escritor/Redator"), ("researcher", "Pesquisador/Analista"),
        ("educator", "Professor/Educador"), ("musician", "Musico/Compositor"),
        ("business", "Consultor de Negocios"), ("generalist", "Generalista"),
    ]
    role_opts = "".join(f'<option value="{v}">{l}</option>' for v, l in role_options)

    # Plugin checkboxes
    plugin_checks = ""
    all_plugin_ids = sorted(builtin_specialist_ids | installed_plugin_ids)
    if all_plugin_ids:
        plugin_checks = '<div class="checkbox-group" id="na-plugins">'
        for pid in all_plugin_ids:
            installed = pid in installed_plugin_ids
            tag = "" if installed else ' title="Nao instalado"'
            plugin_checks += (
                f'<label{tag}>'
                f'<input type="checkbox" value="{pid}"> '
                f'{pid}{"" if installed else " (*)"}'
                f'</label>'
            )
        plugin_checks += '</div><p style="font-size:0.72em;color:var(--text-muted);margin-top:-8px;margin-bottom:12px">(*) ainda nao instalado</p>'

    body += (
        f'<div class="modal-overlay" id="new-agent-modal">\n'
        f'<div class="modal">\n'
        f'  <h2>Novo Agente</h2>\n'
        f'  <label>Nome</label>\n'
        f'  <input type="text" id="na-name" placeholder="ex: dev, estudo...">\n'
        f'  <label>Plataforma</label>\n'
        f'  <select id="na-plat">{modal_opts}</select>\n'
        f'  <label>Role (tipo de trabalho)</label>\n'
        f'  <select id="na-role">{role_opts}</select>\n'
        f'  <label>Diretorio (vazio = atual)</label>\n'
        f'  <input type="text" id="na-cwd" placeholder="C:\\\\Users\\\\samue\\\\projects...">\n'
        f'  <label>Plugins vinculados</label>\n'
        f'  {plugin_checks}\n'
        f'  <div class="modal-actions">\n'
        f'    <button style="background:var(--bg);color:var(--text);border:1px solid var(--border)"'
        f'       onclick="closeModal(\'new-agent-modal\')">Cancelar</button>\n'
        f'    <button style="background:var(--accent);color:#fff" onclick="submitAgent()">Criar</button>\n'
        f'  </div>\n'
        '  <script>\n'
        '  function submitAgent(){\n'
        '    var plugins = [];\n'
        '    var pc = document.getElementById("na-plugins");\n'
        '    if (pc) pc.querySelectorAll("input:checked").forEach(function(c){plugins.push(c.value);});\n'
        '    var body = {\n'
        '      name: document.getElementById("na-name").value,\n'
        '      platform: document.getElementById("na-plat").value,\n'
        '      role: document.getElementById("na-role").value,\n'
        '      cwd: document.getElementById("na-cwd").value,\n'
        '      plugins: plugins\n'
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

    # ═══════════════════════════════════════════════════════
    # ── ROUTINES SECTION ──
    # ═══════════════════════════════════════════════════════
    body += '<div class="section" id="s-routines">\n'
    if commands:
        for grp_name, grp_data in commands.items():
            subs = grp_data.get("subcommands", {})
            emoji = "\\U0001f4cb"
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
            f'  <div class="icon">\\U0001f4cb</div>\n'
            '  <h3>Nenhuma rotina cadastrada</h3>\n'
            '  <p>Use <code>myc add</code> para adicionar rotinas.</p>\n'
            '</div>\n'
        )
    body += '</div>\n'

    # ═══════════════════════════════════════════════════════
    # ── PLUGINS SECTION (Specialists + Bundles) ──
    # ═══════════════════════════════════════════════════════
    body += '<div class="section" id="s-plugins">\n'

    # Sub-tabs: Installed | Available | Bundles
    body += (
        '<div class="sub-tabs" id="ps-plugins">\n'
        '  <button class="sub-tab active" data-sub="installed" onclick="showSubPanel(\'plugins\',\'installed\')">Instalados</button>\n'
        '  <button class="sub-tab" data-sub="available" onclick="showSubPanel(\'plugins\',\'available\')">Disponiveis</button>\n'
        '  <button class="sub-tab" data-sub="bundles" onclick="showSubPanel(\'plugins\',\'bundles\')">Bundles</button>\n'
        '</div>\n'
    )

    # ── Installed plugins ──
    body += '<div class="sub-panel active" id="panel-plugins-installed">\n'
    if plugin_list_installed:
        body += (
            f'  <div class="card">\n'
            f'    <div class="card-header">\n'
            f'      <div class="card-title"><span>\\U0001f50c Specialists Instalados</span>'
            f'        <span class="card-badge badge-green">{len(plugin_list_installed)}</span></div>\n'
            f'      <input type="text" class="search-box" style="max-width:250px"'
            f' placeholder="Filtrar..."'
            f' oninput="filterNodes(\'plug-installed-list\', this.value)">\n'
            f'    </div>\n'
            f'    <div id="plug-installed-list">\n'
        )
        for i, p in enumerate(plugin_list_installed):
            m = plugin_meta.get(p.stem, {})
            pname = m.get("name", p.stem)
            pdesc = m.get("description", "")
            hooks = m.get("hooks", [])
            c = _plugin_icon_color(i)
            hooks_str = "".join(f'<span class="tag">{h}</span>' for h in hooks) if hooks else ""
            hooks_html = f'<div class="tags-row" style="margin-top:6px">{hooks_str}</div>' if hooks_str else ""
            delete_btn = f'<button class="delete-btn" style="flex-shrink:0" onclick="uninstallPlugin(\'{p.stem}\')">Remover</button>'
            body += (
                f'    <div class="plugin-item">\n'
                f'      <div class="plugin-icon" style="background:{c}">&#9881;</div>\n'
                f'      <div style="flex:1;min-width:0">\n'
                f'        <div class="plugin-name">{pname} <code style="font-size:0.8em">{p.stem}</code></div>\n'
                f'        <div class="plugin-desc">{pdesc}</div>\n'
                f'        {hooks_html}\n'
                f'      </div>\n'
                f'      {delete_btn}\n'
                f'    </div>\n'
            )
        body += '    </div>\n  </div>\n'
    else:
        body += (
            '<div class="empty-state">\n'
            f'  <div class="icon">\\U0001f50c</div>\n'
            '  <h3>Nenhum specialist instalado</h3>\n'
            '  <p>Instale via abas "Disponiveis" ou "Bundles" acima.</p>\n'
            '</div>\n'
        )
    body += '</div>\n'

    # ── Available plugins ──
    body += '<div class="sub-panel" id="panel-plugins-available">\n'
    body += (
        f'  <div class="card">\n'
        f'    <div class="card-header">\n'
        f'      <div class="card-title"><span>\\U0001f4e6 Specialists Disponiveis (built-in)</span>'
        f'        <span class="card-badge badge-purple">{len(builtin_specialist_ids)}</span></div>\n'
        f'      <input type="text" class="search-box" style="max-width:250px"'
        f' placeholder="Filtrar..."'
        f' oninput="filterNodes(\'plug-available-list\', this.value)">\n'
        f'    </div>\n'
        f'    <div id="plug-available-list">\n'
    )
    all_plugin_list = sorted(builtin_specialist_ids)
    for i, pid in enumerate(all_plugin_list):
        is_installed = pid in installed_plugin_ids
        meta_p = plugin_meta.get(pid, get_plugin_meta(pid))
        pname = meta_p.get("name", pid) if meta_p else pid
        pdesc = meta_p.get("description", "") if meta_p else ""
        c = _plugin_icon_color(i)
        status_badge = ''
        if is_installed:
            status_badge = '<span class="card-badge badge-green" style="font-size:0.65em">Instalado</span>'
            btn_html = f'<button class="install-btn" disabled>Instalado</button>'
        else:
            btn_html = f'<button class="install-btn" onclick="installPlugin(\'{pid}\')">Instalar</button>'
        body += (
            f'      <div class="plugin-item">\n'
            f'        <div class="plugin-icon" style="background:{c}">&#9881;</div>\n'
            f'        <div style="flex:1;min-width:0">'
            f'          <div class="plugin-name">{pname} {status_badge}</div>\n'
            f'          <div class="plugin-desc">{pdesc}</div>\n'
            f'          <div style="font-size:0.72em;color:var(--text-muted);margin-top:4px">'
            f'            <code>{pid}.py</code></div>\n'
            f'        </div>\n'
            f'        {btn_html}\n'
            f'      </div>\n'
        )
    body += '    </div>\n  </div>\n'
    body += '</div>\n'

    # ── Bundles ──
    body += '<div class="sub-panel" id="panel-plugins-bundles">\n'
    body += (
        f'  <div class="card">\n'
        f'    <div class="card-header">\n'
        f'      <div class="card-title"><span>\\U0001f4e6 Bundles de Specialists</span>'
        f'        <span class="card-badge badge-yellow">{len(BUNDLE_META)}</span></div>\n'
        f'    </div>\n'
    )
    for bid, bmeta in BUNDLE_META.items():
        plugins_in_bundle = bmeta["plugins"]
        installed_count = sum(1 for p in plugins_in_bundle if p in installed_plugin_ids)
        total = len(plugins_in_bundle)
        is_complete = installed_count == total
        bcolor = bmeta.get("color", "var(--accent-glow)")
        body += (
            f'    <div class="bundle-card">\n'
            f'      <div class="bundle-icon" style="background:{bcolor}">{bmeta["icon"]}</div>\n'
            f'      <div class="bundle-info">\n'
            f'        <div class="bundle-name">{bmeta["name"]}</div>\n'
            f'        <div class="bundle-desc">{bmeta["description"]}</div>\n'
            f'        <div class="bundle-plugins">'
            f'          {installed_count}/{total} instalados — '
            f'          {", ".join(plugins_in_bundle)}'
            f'        </div>\n'
            f'        <div class="progress-bar" style="max-width:200px;margin-top:4px">'
            f'          <div class="progress-fill" style="width:{100*installed_count/total}%"></div>'
            f'        </div>\n'
            f'      </div>\n'
            f'      <div class="bundle-actions">\n'
        )
        if is_complete:
            body += f'        <button class="install-btn" disabled>Completo</button>\n'
        else:
            body += f'        <button class="install-btn" onclick="alert(\'Execute: myc agent bundle-install {bid}\')">Instalar</button>\n'
        body += (
            f'      </div>\n'
            f'    </div>\n'
        )
    body += '  </div>\n'
    body += '</div>\n'

    body += '</div>\n'  # close plugins section

    # ═══════════════════════════════════════════════════════
    # ── COMPANIES SECTION ──
    # ═══════════════════════════════════════════════════════
    body += '<div class="section" id="s-companies">\n'

    body += (
        '<div class="sub-tabs" id="ps-companies">\n'
        '  <button class="sub-tab active" data-sub="installed" onclick="showSubPanel(\'companies\',\'installed\')">Instaladas</button>\n'
        '  <button class="sub-tab" data-sub="available" onclick="showSubPanel(\'companies\',\'available\')">Disponiveis</button>\n'
        '  <button class="sub-tab" data-sub="bundles" onclick="showSubPanel(\'companies\',\'bundles\')">Company Bundles</button>\n'
        '</div>\n'
    )

    # ── Installed Companies ──
    body += '<div class="sub-panel active" id="panel-companies-installed">\n'
    if company_list_installed:
        body += (
            f'  <div class="card">\n'
            f'    <div class="card-header">\n'
            f'      <div class="card-title"><span>\\U0001f3e2 Empresas Instaladas</span>'
            f'        <span class="card-badge badge-purple">{len(company_list_installed)}</span></div>\n'
            f'    </div>\n'
        )
        for i, p in enumerate(company_list_installed):
            m = company_meta.get(p.stem, {})
            cname = m.get("name", p.stem)
            cdesc = m.get("description", "")
            cicon = _company_icon(i)
            depts = _get_departments_for_company(p.stem)

            body += (
                f'    <div class="company-card">\n'
                f'      <h4><span>{cicon}</span> {cname} '
                f'        <span class="card-badge badge-purple" style="font-size:0.65em">{p.stem}</span></h4>\n'
                f'      <div class="plugin-desc">{cdesc}</div>\n'
            )
            if depts:
                for dept_name, members in depts.items():
                    body += (
                        f'      <div class="dept-section">\n'
                        f'        <div class="dept-title">{dept_name}</div>\n'
                        f'        <div class="specialist-chips">\n'
                    )
                    for sp in members:
                        sp_name = sp.get("name", sp.get("id", "?")) if isinstance(sp, dict) else sp
                        body += f'          <span class="spec-chip">{sp_name}</span>\n'
                    body += '        </div>\n      </div>\n'
            body += (
                f'      <button class="delete-btn" style="margin-top:12px" '
                f'onclick="alert(\'Remover empresa via CLI: remova {p.name}\')">Remover</button>\n'
                f'    </div>\n'
            )
        body += '  </div>\n'
    else:
        body += (
            '<div class="empty-state">\n'
            '  <div class="icon">\\U0001f3e2</div>\n'
            '  <h3>Nenhuma empresa instalada</h3>\n'
            '  <p>Instale via aba "Disponiveis" abaixo.</p>\n'
            '</div>\n'
        )
    body += '</div>\n'

    # ── Available Companies ──
    body += '<div class="sub-panel" id="panel-companies-available">\n'
    body += (
        f'  <div class="card">\n'
        f'    <div class="card-header">\n'
        f'      <div class="card-title"><span>\\U0001f4e6 Empresas Disponiveis (built-in)</span>'
        f'        <span class="card-badge badge-purple">{len(builtin_company_ids)}</span></div>\n'
        f'    </div>\n'
    )
    all_company_list = sorted(builtin_company_ids)
    # Pre-load all builtin company metadata
    company_meta_cache = {}
    repo_companies = _Path(__file__).parent.parent / "plugins" / "companies"
    all_sources = list(set([str(COMPANIES_BUILTIN), str(repo_companies)]))

    for cid in all_company_list:
        # Try installed first
        m = company_meta.get(cid) or get_company_meta(cid)
        if m:
            company_meta_cache[cid] = m
            continue
        # Try builtin sources
        loaded = False
        for src_dir_str in all_sources:
            src = _Path(src_dir_str) / f"{cid}.py"
            if src.exists():
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(cid, src)
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        specs_raw = getattr(mod, "SPECIALISTS", [])
                        company_meta_cache[cid] = {
                            "name": getattr(mod, "NAME", cid),
                            "description": getattr(mod, "DESCRIPTION", ""),
                            "specialists": specs_raw,
                            "spec_count": len(specs_raw),
                        }
                        loaded = True
                        break
                except Exception:
                    pass
        if not loaded and cid not in company_meta_cache:
            company_meta_cache[cid] = {"name": cid, "description": "", "specialists": [], "spec_count": 0}

    for i, cid in enumerate(all_company_list):
        is_installed = cid in installed_company_ids
        cm = company_meta_cache.get(cid, {})
        c_name = cm.get("name", cid)
        c_desc = cm.get("description", "")
        cicon = _company_icon(i)
        specialist_count = cm.get("spec_count", 0)
        if not specialist_count:
            specs_raw = cm.get("specialists", [])
            specialist_count = len([s for s in specs_raw if isinstance(s, dict) or isinstance(s, str)])

        status_badge = ''
        if is_installed:
            status_badge = '<span class="card-badge badge-green" style="font-size:0.65em">Instalada</span>'
            btn_html = f'<button class="install-btn" disabled>Instalada</button>'
        else:
            btn_html = f'<button class="install-btn" onclick="installCompanyPlugin(\'{cid}\')">Instalar</button>'

        body += (
            f'    <div class="bundle-card">\n'
            f'      <div class="bundle-icon" style="background:var(--purple-glow)">{cicon}</div>\n'
            f'      <div class="bundle-info">\n'
            f'        <div class="bundle-name">{c_name} {status_badge}</div>\n'
            f'        <div class="bundle-desc">{c_desc}</div>\n'
            f'        <div class="bundle-plugins">{specialist_count} especialistas</div>\n'
            f'      </div>\n'
            f'      {btn_html}\n'
            f'    </div>\n'
        )
    body += '  </div>\n'
    body += '</div>\n'

    # ── Company Bundles ──
    body += '<div class="sub-panel" id="panel-companies-bundles">\n'
    body += (
        f'  <div class="card">\n'
        f'    <div class="card-header">\n'
        f'      <div class="card-title"><span>\\U0001f3e2 Company Bundles</span>'
        f'        <span class="card-badge badge-yellow">{len(COMPANY_BUNDLE_META)}</span></div>\n'
        f'    </div>\n'
    )
    for cbid, cbmeta in COMPANY_BUNDLE_META.items():
        specs = cbmeta["specialists"]
        installed_specs = sum(1 for s in specs if s in installed_plugin_ids)
        body += (
            f'    <div class="bundle-card">\n'
            f'      <div class="bundle-icon" style="background:var(--purple-glow)">{cbmeta["icon"]}</div>\n'
            f'      <div class="bundle-info">\n'
            f'        <div class="bundle-name">{cbmeta["name"]}</div>\n'
            f'        <div class="bundle-desc">{cbmeta["description"]}</div>\n'
            f'        <div class="bundle-plugins">'
            f'          Specialists: {", ".join(specs)}'
            f'        </div>\n'
            f'      </div>\n'
            f'      <button class="install-btn" onclick="alert(\'Execute: myc agent bundle-company {cbid}\')">Instalar</button>\n'
            f'    </div>\n'
        )
    body += '  </div>\n'
    body += '</div>\n'

    body += '</div>\n'  # close companies section

    # ═══════════════════════════════════════════════════════
    # ── MIDDLEWARES SECTION ──
    # ═══════════════════════════════════════════════════════
    body += '<div class="section" id="s-middlewares">\n'

    if mw_list_installed or available_mw_ids:
        body += (
            f'  <div class="card">\n'
            f'    <div class="card-header">\n'
            f'      <div class="card-title"><span>\\U0001f500 Middlewares</span>'
            f'        <span class="card-badge badge-cyan">{len(installed_mw_ids)} instalados / {len(builtin_mw_ids)} disponiveis</span></div>\n'
            f'    </div>\n'
        )

        if mw_list_installed:
            body += '<div style="margin-bottom:16px;font-size:0.85em;color:var(--text-dim)"><strong>Instalados:</strong></div>'
            for i, p in enumerate(mw_list_installed):
                m = mw_meta.get(p.stem, {})
                mw_name = m.get("name", p.stem) if m else p.stem
                mw_desc = m.get("description", "") if m else ""
                mw_type = m.get("middleware_type", "") if m else ""
                mw_runs = m.get("runs_when", "") if m else ""
                mic = _middleware_icon(i)
                body += (
                    f'    <div class="plugin-item">\n'
                    f'      <div class="plugin-icon" style="background:var(--cyan-glow)">{mic}</div>\n'
                    f'      <div style="flex:1;min-width:0">\n'
                    f'        <div class="plugin-name">{mw_name} <code style="font-size:0.8em">{p.stem}</code></div>\n'
                    f'        <div class="plugin-desc">{mw_desc}</div>\n'
                    f'        <div class="tags-row">\n'
                    f'          <span class="tag tag-cyan">{mw_type}</span>\n'
                    f'          <span class="tag">{mw_runs}</span>\n'
                    f'        </div>\n'
                    f'      </div>\n'
                    f'      <button class="delete-btn" style="flex-shrink:0" onclick="alert(\'Remover middleware via CLI\')">Remover</button>\n'
                    f'    </div>\n'
                )

        # Available middlewares
        not_installed_mw = sorted(builtin_mw_ids - installed_mw_ids)
        if not_installed_mw:
            body += '<div style="margin-top:20px;margin-bottom:12px;font-size:0.85em;color:var(--text-dim)"><strong>Disponiveis (nao instalados):</strong></div>'
            for i, mid in enumerate(not_installed_mw):
                m = mw_meta.get(mid) or get_middleware_meta(mid)
                mw_name = m.get("name", mid) if m else mid
                mw_desc = m.get("description", "") if m else ""
                mic = _middleware_icon(i + len(mw_list_installed))
                body += (
                    f'    <div class="plugin-item">\n'
                    f'      <div class="plugin-icon" style="background:var(--cyan-glow);opacity:0.6">{mic}</div>\n'
                    f'      <div style="flex:1;min-width:0">\n'
                    f'        <div class="plugin-name">{mw_name}</div>\n'
                    f'        <div class="plugin-desc">{mw_desc}</div>\n'
                    f'        <div style="font-size:0.72em;color:var(--text-muted);margin-top:4px">'
                    f'          <code>{mid}.py</code></div>\n'
                    f'      </div>\n'
                    f'      <button class="install-btn" onclick="alert(\'Instale via CLI: myc agent install-middleware {mid}\')">Instalar</button>\n'
                    f'    </div>\n'
                )

        body += '  </div>\n'
    else:
        body += (
            '<div class="empty-state">\n'
            f'  <div class="icon">\\U0001f500</div>\n'
            '  <h3>Nenhum middleware disponivel</h3>\n'
            '</div>\n'
        )
    body += '</div>\n'

    # ═══════════════════════════════════════════════════════
    # ── HISTORY SECTION ──
    # ═══════════════════════════════════════════════════════
    body += '<div class="section" id="s-history">\n'

    if history:
        rate = 100 * stats["successful"] / stats["launches"] if stats["launches"] > 0 else 0
        bar_cls = "med" if rate < 60 else ("low" if rate < 30 else "")
        body += (
            f'<div class="card">\n'
            f'  <div class="card-header">\n'
            f'    <div class="card-title"><span>\\U0001f4c8 Taxa de Sucesso</span></div>\n'
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
            f'    <div class="card-title"><span>\\U0001f4dc Historico</span>'
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
            '  <div class="icon">\\U0001f4dc</div>\n'
            '  <h3>Nenhum registro no historico</h3>\n'
            '  <p>Os lancamentos de agentes aparecerão aqui.</p>\n'
            '</div>\n'
        )
    body += '</div>\n'

    # ═══════════════════════════════════════════════════════
    # ── STATS SECTION ──
    # ═══════════════════════════════════════════════════════
    body += '<div class="section" id="s-stats">\n'

    # Agent distribution
    agents_launch_count = {}
    for h in history:
        an = h.get("agent", "?")
        agents_launch_count[an] = agents_launch_count.get(an, 0) + 1

    if agents_launch_count:
        body += (
            f'<div class="card">\n'
            f'  <div class="card-header">\n'
            f'    <div class="card-title"><span>\\U0001f4ca Distribuicao por Agente</span></div>\n'
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
            f'    <div class="card-title"><span>\\u26a2 Por Plataforma</span></div>\n'
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

    # Plugin ecosystem summary
    body += (
        f'<div class="card" style="margin-top:16px">\n'
        f'  <div class="card-header">\n'
        f'    <div class="card-title"><span>\\U0001f50c Ecossistema de Plugins</span></div>\n'
        f'  </div>\n'
    )
    eco_items = [
        ("Specialists built-in", len(builtin_specialist_ids), "var(--accent-glow)"),
        ("Specialists instalados", len(installed_plugin_ids), "var(--green-glow)"),
        ("Empresas disponiveis", len(builtin_company_ids), "var(--purple-glow)"),
        ("Empresas instaladas", len(installed_company_ids), "var(--purple-glow)"),
        ("Middlewares disponiveis", len(builtin_mw_ids), "var(--cyan-glow)"),
        ("Middlewares instalados", len(installed_mw_ids), "var(--cyan-glow)"),
        ("Agente com mais plugins", max(
            ((n, len(p.get("plugins", []))) for n, p in agents.items()),
            key=lambda x: x[1],
            default=("nenhum", 0),
        )[0] if agents else "nenhum", ""),
    ]
    for label, value, color in eco_items:
        body += (
            f'<div style="display:flex;align-items:center;justify-content:space-between;'
            f'padding:8px 0;border-bottom:1px solid var(--bg);font-size:0.88em">'
            f'<span style="color:var(--text-dim)">{label}</span>'
            f'<strong style="color:{color if color else "var(--text)"}">{value}</strong>'
            f'</div>\n'
        )
    body += '</div>\n'

    body += '</div>\n'

    # ═══════════════════════════════════════════════════════
    # ── DOCS SECTION ──
    # ═══════════════════════════════════════════════════════
    body += '<div class="section" id="s-docs">\n'

    body += (
        f'<div class="card">\n'
        f'  <div class="card-header">\n'
        f'    <div class="card-title"><span>\\U0001f4da Documentacao do Sistema de Plugins</span></div>\n'
        f'  </div>\n'
    )
    body += DOC_SECTION
    body += '</div>\n'

    body += '</div>\n'  # close docs section

    # Close container and body/html
    body += (
        '</div>\n'  # close container
        '<script>\n'
        '/* Auto-init sub-tabs */\n'
        'document.querySelectorAll(".sub-tabs .sub-tab.active").forEach(function(btn){\n'
        '  var parent = btn.closest(".sub-tabs");\n'
        '  var psId = parent ? parent.id.replace("ps-","") : "";\n'
        '  var sub = btn.dataset.sub;\n'
        '  if (psId && sub) showSubPanel(psId, sub);\n'
        '});\n'
        '</script>\n'
        '</body>\n'
        '</html>\n'
    )

    return html + body


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
            elif path == "/export":
                self._handle_export()
            else:
                self.send_error(404)

        def do_POST(self):
            path = urlparse(self.path).path
            if path == "/api/create-agent":
                self._handle_create_agent()
            elif path.startswith("/install-plugin/"):
                plugin_id = path.split("/install-plugin/")[1].split("?")[0]
                self._handle_install_plugin(plugin_id)
            elif path.startswith("/install-company/"):
                company_id = path.split("/install-company/")[1].split("?")[0]
                self._handle_install_company(company_id)
            elif path.startswith("/uninstall-plugin/"):
                plugin_id = path.split("/uninstall-plugin/")[1].split("?")[0]
                self._handle_uninstall_plugin(plugin_id)
            elif path.startswith("/install-bundle/"):
                bundle_id = path.split("/install-bundle/")[1].split("?")[0]
                self._handle_install_bundle(bundle_id)

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
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                data = _json.loads(body)
                name = data.get("name", "").strip()
                platform = data.get("platform", "openclaude")
                role = data.get("role", "generalist")
                cwd = data.get("cwd", "").strip() or None
                plugins = data.get("plugins", [])

                if not name or " " in name:
                    self.send_response(400)
                    self.end_headers()
                    return

                from myc.agent import _load_agents, _save_agents
                agents = _load_agents()
                agents[name] = {
                    "name": name,
                    "platform": platform,
                    "role": role,
                    "env": {},
                    "cwd": cwd,
                    "initial_context": "",
                    "custom_command": None,
                    "plugins": plugins,
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

        def _handle_install_plugin(self, plugin_id: str):
            try:
                from myc.plugin_installer import install_plugin
                result = install_plugin(plugin_id)
                self._send_json({"ok": result})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)})

        def _handle_install_company(self, company_id: str):
            try:
                from myc.plugin_installer import install_company_plugin
                result = install_company_plugin(company_id)
                self._send_json({"ok": result})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)})

        def _handle_uninstall_plugin(self, plugin_id: str):
            try:
                from myc.plugin_installer import uninstall_plugin
                result = uninstall_plugin(plugin_id)
                self._send_json({"ok": result})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)})

        def _handle_install_bundle(self, bundle_id: str):
            try:
                if bundle_id in BUNDLE_META:
                    installed = 0
                    from myc.plugin_installer import install_plugin
                    for pid in BUNDLE_META[bundle_id]["plugins"]:
                        if install_plugin(pid):
                            installed += 1
                    self._send_json({"ok": True, "installed": installed})
                else:
                    self._send_json({"ok": False, "error": f"Bundle '{bundle_id}' nao encontrado"})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)})

        def _handle_export(self):
            """Exporta pagina estatica para download."""
            html = generate_page()
            self._send_html(html)

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


def export_static_html(output_path: str | None = None) -> str:
    """Exporta o dashboard como arquivo HTML estatico para referencia.

    Args:
        output_path: Caminho de saida (default: dashboard_myc.html no diretorio atual).

    Returns:
        Caminho do arquivo gerado.
    """
    html = generate_page()
    if output_path is None:
        output_path = "dashboard_myc.html"
    _Path(output_path).write_text(html, encoding="utf-8")
    return output_path