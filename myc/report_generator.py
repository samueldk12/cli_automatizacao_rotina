"""
Report Generator — Gera relatório final consolidado após execução do plano.

Combina outputs de todos os departamentos e agentes em um relatório
estruturado com: resumo executivo, detalhes por departamento,
recomendações e próximos passos.
"""

import json
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

REPORT_DIR = Path.home() / ".myc" / "company_memory" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def generate_final_report(
    query: str,
    company_id: str | None,
    plan: dict,
    execution_report: dict,
) -> dict:
    """Gera relatório final consolidado.

    Args:
        query: tarefa original
        company_id: empresa executada
        plan: plano gerado pelo planner
        execution_report: resultado do executor

    Returns:
        Dicionário com relatório estruturado.
    """
    phases = plan.get("phases", [])
    exec_phases = execution_report.get("phases", [])

    # Coleta todos os outputs
    all_outputs = []
    dept_summaries = {}

    for ep in exec_phases:
        dept_name = ep.get("department", "?")
        agents = ep.get("agents", [])

        dept_output = {
            "department": dept_name,
            "phase": ep.get("phase", 0),
            "status": ep.get("status", "?"),
            "agents": [],
        }

        for agent in agents:
            agent_out = {
                "id": agent.get("id", "?"),
                "name": agent.get("name", "?"),
                "status": agent.get("result", {}).get("status", "?"),
            }
            dept_output["agents"].append(agent_out)
            all_outputs.append(agent_out)

        dept_summaries[dept_name] = dept_output

    # Gera resumo executivo
    total_agents = sum(len(ep.get("agents", [])) for ep in exec_phases)
    total_depts = len(set(ep.get("department", "") for ep in exec_phases))
    completed = sum(1 for ep in exec_phases if ep.get("status") == "completed")
    failed = sum(1 for ep in exec_phases if ep.get("status") == "failed")

    started = execution_report.get("started_at", "")
    ended = execution_report.get("completed_at", "")
    duration = _calc_duration(started, ended)

    report = {
        "query": query,
        "company_id": company_id,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_departments": total_depts,
            "total_agents": total_agents,
            "completed": completed,
            "failed": failed,
            "duration": duration,
        },
        "department_reports": dept_summaries,
        "executive_summary": _generate_executive_summary(
            query, company_id, phases, dept_summaries
        ),
        "recommendations": _generate_recommendations(phases, dept_summaries),
    }

    return report


def _calc_duration(started: str, ended: str) -> str:
    """Calcula duração entre dois timestamps."""
    if not started or not ended:
        return "N/A"
    try:
        t_start = datetime.fromisoformat(started)
        t_end = datetime.fromisoformat(ended)
        delta = t_end - t_start
        total_seconds = int(delta.total_seconds())
        mins = total_seconds // 60
        secs = total_seconds % 60
        return f"{mins}m {secs}s"
    except Exception:
        return "N/A"


def _generate_executive_summary(
    query: str, company_id: str | None, phases: list, dept_reports: dict
) -> str:
    """Gera resumo executivo textual."""
    lines = [
        f"Tarefa: {query}",
        f"Empresa: {company_id or 'N/A'}",
        "",
    ]

    # Fases de análise
    analysis_depts = [
        d for d in phases
        if d.get("department") in ("negocios", "dados", "seo", "financeiro")
    ]
    # Fases de execução
    exec_depts = [
        d for d in phases
        if d.get("department") not in ("negocios", "dados", "seo", "financeiro")
    ]

    if analysis_depts:
        lines.append("ANÁLISE REALIZADA:")
        for d in analysis_depts:
            dn = d["department"]
            status = dept_reports.get(dn, {}).get("status", "N/A")
            lines.append(f"  - {dn}: [{status}] {d.get('action', '')}")
        lines.append("")

    if exec_depts:
        lines.append("EXECUÇÃO:")
        for d in exec_depts:
            dn = d["department"]
            status = dept_reports.get(dn, {}).get("status", "N/A")
            lines.append(f"  - {dn}: [{status}] {d.get('action', '')}")

    return "\n".join(lines)


def _generate_recommendations(phases: list, dept_reports: dict) -> list[str]:
    """Gera recomendações baseadas nos departamentos executados."""
    recs = []
    dept_actions = {d["department"]: d.get("action", "") for d in phases}

    if "negocios" in dept_actions:
        recs.append("Revise a análise de mercado antes de lançar campanhas")
    if "seo" in dept_actions:
        recs.append("Monitore métricas SEO por 30 dias após implementação")
    if "marketing" in dept_actions:
        recs.append("Acompanhe ROI das campanhas semanalmente")
    if "conteudo" in dept_actions:
        recs.append("Mantenha calendário editorial atualizado")
    if "desenvolvimento" in dept_actions:
        recs.append("Agende code reviews regulares")
    if "design" in dept_actions:
        recs.append("Valide designs com testes de usabilidade")

    return recs


def display_report(report: dict) -> None:
    """Mostra relatório em tabela visual."""
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]RELATÓRIO FINAL DE EXECUÇÃO[/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")

    s = report.get("summary", {})
    console.print(f"\n[dim]Tarefa:[/dim] {report.get('query', '')[:80]}")
    console.print(f"[dim]Empresa:[/dim] {report.get('company_id', 'N/A')}")
    console.print(f"[dim]Gerado em:[/dim] {report.get('generated_at', '')[:19]}")
    console.print(f"[dim]Duração:[/dim] {s.get('duration', 'N/A')}")
    console.print(f"[dim]Departamentos:[/dim] {s.get('total_departments', 0)}")
    console.print(f"[dim]Agentes:[/dim] {s.get('total_agents', 0)}")
    console.print(f"[dim]Completados:[/dim] [green]{s.get('completed', 0)}[/green]")
    console.print(f"[dim]Falhas:[/dim] [red]{s.get('failed', 0)}[/red]")

    # Resumo executivo
    console.print(f"\n[bold]Resumo Executivo:[/bold]")
    console.print(report.get("executive_summary", ""))

    # Tabela de departamentos
    dept_reports = report.get("department_reports", {})
    if dept_reports:
        table = Table(title="Resultado por Departamento")
        table.add_column("Departamento", style="cyan")
        table.add_column("Fase", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Agentes", style="dim")

        for dept_name, dept_data in dept_reports.items():
            agents = dept_data.get("agents", [])
            agent_str = ", ".join(
                f"{a.get('name', '?')} [{a.get('status', '?')}]"
                for a in agents
            )
            status_icon = "OK" if dept_data["status"] == "completed" else "FALHA"
            table.add_row(
                dept_name,
                str(dept_data.get("phase", "?")),
                f"{dept_data['status']} [{status_icon}]",
                agent_str,
            )
        console.print(table)

    # Recomendações
    recs = report.get("recommendations", [])
    if recs:
        console.print(f"\n[bold]Recomendações:[/bold]")
        for i, rec in enumerate(recs, 1):
            console.print(f"  {i}. {rec}")

    console.print()


def save_report(report: dict) -> str:
    """Salva relatório em arquivo."""
    company = report.get("company_id", "generic")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{company}_{ts}.json"
    filepath = REPORT_DIR / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Also generate HTML
    html_path = REPORT_DIR / f"report_{company}_{ts}.html"
    _generate_html_report(report, html_path)

    return str(filepath)


def _generate_html_report(report: dict, filepath: Path) -> None:
    """Gera versão HTML do relatório."""
    s = report.get("summary", {})
    recs = report.get("recommendations", [])
    dept_reports = report.get("department_reports", {})

    # Table rows
    dept_rows = ""
    for dn, dd in dept_reports.items():
        agents = dd.get("agents", [])
        agent_names = ", ".join(
            f"{a.get('name', '?')} <em>({a.get('status', '?')})</em>"
            for a in agents
        )
        status = dd.get("status", "?")
        status_color = "#22c55e" if status == "completed" else "#ef4444"
        dept_rows += (
            f"<tr>"
            f"<td>{dn}</td>"
            f"<td>{dd.get('phase', '?')}</td>"
            f"<td style='color:{status_color}'>{status}</td>"
            f"<td>{agent_names}</td>"
            f"</tr>\n"
        )

    # Recs
    rec_lines = "\n".join(f"<li>{r}</li>" for r in recs)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>MYC - Relatório {report.get('company_id', 'N/A')}</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 1000px; margin: 40px auto; padding: 20px; background: #fafafa; color: #333; }}
h1 {{ color: #1e40af; border-bottom: 2px solid #1e40af; padding-bottom: 10px; }}
h2 {{ color: #333; margin-top: 30px; }}
.stats {{ display: flex; gap: 20px; flex-wrap: wrap; margin: 20px 0; }}
.stat {{ background: white; padding: 15px 25px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.stat .label {{ color: #666; font-size: 0.85em; }}
.stat .value {{ font-size: 1.5em; font-weight: bold; color: #1e40af; }}
table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
th {{ background: #1e40af; color: white; padding: 12px 15px; text-align: left; }}
td {{ padding: 10px 15px; border-bottom: 1px solid #eee; }}
tr:last-child td {{ border-bottom: none; }}
pre {{ background: #f5f5f5; padding: 15px; border-radius: 8px; white-space: pre-wrap; }}
.recs {{ background: #fef3c7; padding: 15px 20px; border-left: 4px solid #f59e0b; border-radius: 4px; }}
.footer {{ color: #999; font-size: 0.85em; margin-top: 40px; text-align: center; }}
</style>
</head>
<body>
<h1>Relatório de Execução</h1>
<p><strong>Tarefa:</strong> {report.get('query', '')}</p>
<p><strong>Empresa:</strong> {report.get('company_id', 'N/A')}</p>
<p><strong>Gerado em:</strong> {report.get('generated_at', '')[:19]}</p>

<div class="stats">
<div class="stat"><div class="label">Duração</div><div class="value">{s.get('duration', 'N/A')}</div></div>
<div class="stat"><div class="label">Departamentos</div><div class="value">{s.get('total_departments', 0)}</div></div>
<div class="stat"><div class="label">Agentes</div><div class="value">{s.get('total_agents', 0)}</div></div>
<div class="stat"><div class="label">Completados</div><div class="value" style="color:#22c55e">{s.get('completed', 0)}</div></div>
<div class="stat"><div class="label">Falhas</div><div class="value" style="color:#ef4444">{s.get('failed', 0)}</div></div>
</div>

<h2>Resumo Executivo</h2>
<pre>{report.get('executive_summary', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</pre>

<h2>Resultado por Departamento</h2>
<table>
<tr><th>Departamento</th><th>Fase</th><th>Status</th><th>Agentes</th></tr>
{dept_rows}
</table>

<h2>Recomendações</h2>
<div class="recs">
<ol>{rec_lines}</ol>
</div>

<div class="footer">Gerado por MYC — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
</body>
</html>"""

    filepath.write_text(html, encoding="utf-8")
