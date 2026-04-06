"""
Executor — Executa os agentes de uma empresa/departamento seguindo o plano.

Fluxo:
  1. Planner gera o plano
  2. Usuario aprova
  3. Executor executa fase por fase (sequencial ou paralelo)
  4. Output de cada agente e salvo na memoria da empresa
  5. Proxima fase pode usar memoria da fase anterior como contexto
  6. Gera relatorio final com todos os outputs
"""

import json
import os
from datetime import datetime
from pathlib import Path

from rich.console import Console

console = Console()


def _get_default_agent() -> dict | None:
    """Pega o agente default para execucao."""
    from myc.agent import _load_agents
    agents = _load_agents()
    return agents.get("default")


def _launch_agent_with_context(
    agent_name: str,
    context: str,
    query: str,
    cwd: str | None = None,
) -> int:
    """Lanca agente com contexto e query."""
    from myc.agent import _load_agents, launch_agent

    agents = _load_agents()
    profile = agents.get(agent_name)
    if not profile:
        console.print(f"[red]Agente '{agent_name}' nao encontrado.[/red]")
        return 1

    work_cwd = cwd or profile.get("cwd") or str(Path.cwd())
    md_path = Path(work_cwd) / "CLAUDE.md"

    backup = None
    if md_path.exists():
        backup = md_path.read_text(encoding="utf-8")

    full_context = (
        f"# Agent Work Session\n\n"
        f"## Contexto\n{context}\n\n"
        f"## Tarefa\n{query}"
    )
    md_path.write_text(full_context, encoding="utf-8")

    try:
        return launch_agent(agent_name, cwd=work_cwd)
    finally:
        if backup is not None:
            md_path.write_text(backup, encoding="utf-8")
        else:
            md_path.unlink(missing_ok=True)


def _build_department_context(
    company_id: str,
    department: str,
    specialists: list[dict],
    plan: dict,
) -> str:
    """Constrói contexto para um departamento, incluindo memoria anterior."""
    parts = []

    # Contexto da empresa
    from myc.agent_plugins import execute_company_profile, list_companies
    companies = list_companies()
    company_name = company_id

    for c in companies:
        if c["id"] == company_id:
            company_name = c.get("name", company_id)
            break

    parts.append(f"Voce esta trabalhando na empresa '{company_name}' ({company_id}).")
    parts.append(f"Departamento: {department}")

    # Carrega contexto da empresa
    try:
        company_ctx = execute_company_profile(company_id)
        if company_ctx:
            parts.append(f"\nContexto da empresa:\n{company_ctx}")
    except Exception:
        pass

    # Carrega contexto dos specialists
    for sp in specialists:
        sp_id = sp.get("id", "")
        sp_name = sp.get("name", sp_id)
        sp_role = sp.get("role", "")
        if sp_role:
            parts.append(f"\nEspecialista: {sp_name}")
            parts.append(f"Papel: {sp_role}")

    # Adiciona memoria de fases anteriores
    from myc.company_memory import get_for_department
    mem_items = get_for_department(company_id, department)
    if mem_items:
        from myc.company_memory import get_full
        parts.append("\n=== MEMORIA DA EMPRESA (contexto de fases anteriores) ===")
        for item in mem_items:
            full = get_full(company_id, item["key"])
            if full:
                val = full.get("value")
                parts.append(f"\n[De: {item['department']}] {item['key']}:")
                if isinstance(val, str):
                    parts.append(val)
                else:
                    parts.append(json.dumps(val, ensure_ascii=False, indent=2))

    # Dependencias do plano
    deps = []
    for phase in plan.get("phases", []):
        if phase["department"] == department:
            deps.extend(phase.get("depends_on", []))
            break

    if deps:
        parts.append(f"\n=== DEPENDENCIAS ===")
        parts.append(f"Este departamento depende de: {', '.join(deps)}")
        parts.append("Revise os outputs daqueles departamentos antes de prosseguir.")

    return "\n\n".join(parts)


def _build_department_only_context(
    department_id: str,
    plan: dict,
) -> str:
    """Contexto para departamento independente (sem empresa)."""
    from myc.department import get_department_context

    context = get_department_context(department_id)
    if not context:
        return f"Voce e o departamento '{department_id}'."

    return f"{context}\n\n## Tarefa\n{plan.get('query', '')}"


def execute_plan(plan: dict, company_id: str | None = None,
                 department_id: str | None = None,
                 dry_run: bool = False, confirmed: bool = False) -> dict:
    """Executa o plano de uma empresa ou departamento.

    Args:
        plan: plano gerado pelo planner
        company_id: ID da empresa
        department_id: ID do departamento (independente)
        dry_run: se True, so mostra o plano sem executar

    Returns:
        Relatorio de execucao.
    """
    query = plan.get("query", "")
    phases = plan.get("phases", [])
    exec_mode = plan.get("execution_mode", "generic")

    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]EXECUTANDO PLANO[/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")

    from rich.table import Table
    table = Table(title="Plano de Execucao")
    table.add_column("Fase", style="cyan")
    table.add_column("Departamento", style="yellow")
    table.add_column("Agentes", style="green")
    table.add_column("Acao", style="dim")
    table.add_column("Dependencias", style="magenta")
    table.add_column("Status", style="bold")

    for phase in phases:
        specs = phase.get("specialists", [])
        spec_str = ", ".join(
            s.get("name", s.get("id", "?")) for s in specs[:5]
        )
        if len(specs) > 5:
            spec_str += f" +{len(specs) - 5}"

        deps = phase.get("depends_on", [])
        dep_str = ", ".join(deps) if deps else "-"

        table.add_row(
            str(phase["phase"]),
            phase["department"],
            spec_str or "-",
            phase.get("action", "")[:50],
            dep_str,
            "[yellow]PENDING[/yellow]",
        )

    console.print(table)

    if dry_run:
        console.print(f"\n[yellow][DRY RUN] Execucao simulada. Nada foi lancado.[/yellow]")
        return {"status": "dry_run", "query": query}

    # Pede confirmacao
    if not confirmed:
        import questionary
        do_execute = questionary.confirm("Executar este plano?", default=True).ask()
        if not do_execute:
            console.print("[yellow]Execucao cancelada.[/yellow]")
            return {"status": "cancelled"}

    # Executa fase por fase
    report: dict = {
        "query": query,
        "company_id": company_id,
        "phases": [],
        "started_at": datetime.now().isoformat(),
        "status": "running",
    }

    for phase in phases:
        phase_phase = phase["phase"]
        dept_name = phase["department"]
        specs = phase.get("specialists", [])

        console.print(f"\n[bold]{'='*50}[/bold]")
        console.print(f"[bold]FASE {phase_phase}: [cyan]{dept_name}[/cyan][/bold]")
        console.print(f"[dim]Acao: {phase['action']}[/dim]")

        phase_report = {
            "phase": phase_phase,
            "department": dept_name,
            "agents": [],
            "status": "running",
        }

        if company_id:
            # Modo empresa
            console.print(f"\n[dim]Construindo contexto com memoria da empresa...[/dim]")
            context = _build_department_context(
                company_id, dept_name, specs, plan
            )

            console.print(f"[dim]Contexto: {len(context)} chars[/dim]")

            # Para cada specialist, executa sequencialmente
            for i, sp in enumerate(specs):
                sp_id = sp.get("id", "")
                sp_name = sp.get("name", sp_id)
                sp_role = sp.get("role", "")

                console.print(f"\n  [green]Agente {i+1}/{len(specs)}: {sp_name}[/green]")

                sp_context = f"{context}\n\nVoce agora e o especialista '{sp_name}' neste momento:"
                sp_query = f"Como {sp_name}, execute sua contribuicao para esta tarefa: {query}"
                if sp_role:
                    sp_context += f"\n\nSeu papel: {sp_role}"

                result = _dispatch_agent(sp_context, sp_query, company_id, dept_name, sp_id)

                phase_report["agents"].append({
                    "id": sp_id,
                    "name": sp_name,
                    "result": result,
                })

            phase_report["status"] = "completed"

        else:
            # Departamento independente
            context = _build_department_only_context(dept_name, plan)
            sp_query = f"Como o departamento {dept_name}, execute: {query}"

            result = _dispatch_agent(context, sp_query, company_id, dept_name, dept_name)
            phase_report["agents"].append({
                "id": dept_name,
                "name": dept_name,
                "result": result,
            })
            phase_report["status"] = "completed"

        report["phases"].append(phase_report)

    report["status"] = "completed"
    report["completed_at"] = datetime.now().isoformat()

    console.print(f"\n[bold green]{'='*50}[/bold green]")
    console.print(f"[bold green]PLANO EXECUTADO COM SUCESSO[/bold green]")
    console.print(f"[bold green]{'='*50}[/bold green]")

    # Gera relatorio final
    console.print(f"\n[dim]Gerando relatorio final...[/dim]")
    from myc.report_generator import generate_final_report, display_report, save_report
    final_report = generate_final_report(query, company_id, plan, report)
    display_report(final_report)
    report_path = save_report(final_report)
    console.print(f"[dim]Relatorio salvo em: {report_path}[/dim]")

    # Mostra resumo de memoria
    if company_id:
        from myc.company_memory import list_keys
        mem_items = list_keys(company_id)
        if mem_items:
            console.print(f"\n[dim]Memoria da empresa atualizada: {len(mem_items)} itens salvos.[/dim]")
            for item in mem_items[:5]:
                console.print(f"  [cyan]{item['key']}[/cyan] ({item['department']})")

    return report


def _dispatch_agent(context: str, query: str,
                    company_id: str | None,
                    dept_name: str,
                    agent_key: str) -> dict:
    """Despacha um agente com o contexto dado, captura output via --print."""
    from myc.agent import _load_agents, _find_command, launch_agent
    from myc.company_memory import save as mem_save
    import subprocess

    agents = _load_agents()
    if "default" not in agents:
        console.print(f"  [yellow]Nenhum agente 'default'.[/yellow]")
        return {"status": "no_agent", "skipped": True}

    agent = agents["default"]
    cwd = agent.get("cwd") or str(Path.cwd())
    platform = agent.get("platform", "openclaude")
    env_vars = dict(agent.get("env", {}))

    # Monta o prompt completo para o LLM
    full_prompt = (
        f"Voce esta atuando como '{agent_key}' no departamento '{dept_name}'.\n\n"
        f"## Contexto da Empresa\n{context}\n\n"
        f"## Sua Tarefa\n{query}\n\n"
        f"IMPORTANTE: Ao final, descreva brevemente o que foi feito "
        f"e quais foram seus outputs principais. Isso sera salvo na "
        f"memoria da empresa para uso de outros departamentos."
    )

    console.print(f"\n  [dim]Enviando prompt ({len(full_prompt)} chars) ao agente...[/dim]")

    # Tenta modo headless --print
    claude_cmd = _find_command("claude")
    if claude_cmd and claude_cmd.endswith((".cmd", ".bat")):
        # Build env
        env = os.environ.copy()
        env.update(env_vars)

        console.print(f"  [dim]Executando em modo headless (--print)...[/dim]")
        try:
            result = subprocess.run(
                ["cmd.exe", "/c", claude_cmd, "-p", full_prompt],
                env=env,
                cwd=str(Path(cwd)),
                capture_output=True,
                text=True,
                timeout=120,
                encoding="utf-8",
                errors="replace",
            )
            output = (result.stdout + result.stderr).strip()

            if output and result.returncode == 0:
                # Salva output real na memoria
                if company_id:
                    mem_save(
                        company_id,
                        f"{dept_name}_{agent_key}_output",
                        output,
                        dept=dept_name,
                        source=agent_key,
                    )
                console.print(f"  [dim]Output capturado: {len(output)} chars[/dim]")
                # Mostra preview
                preview = output[:300]
                console.print(f"  [dim]Preview: {preview}{'...' if len(output) > 300 else ''}[/dim]")
                return {"status": "completed", "exit_code": 0, "output": output}
        except subprocess.TimeoutExpired:
            console.print(f"  [yellow]Timeout no modo headless, tentando modo interativo...[/yellow]")
        except Exception as e:
            console.print(f"  [yellow]Erro no modo headless: {e}[/yellow]")

    # Fallback: modo interativo (sem captura de output)
    console.print(f"  [yellow]Usando modo interativo (fallback)[/yellow]")
    backup_path = Path(cwd) / "CLAUDE.md"
    backup = None
    if backup_path.exists():
        backup = backup_path.read_text(encoding="utf-8")

    md_path = backup_path
    md_path.write_text(full_prompt, encoding="utf-8")

    try:
        rc = launch_agent(agent["name"], cwd=cwd)
    finally:
        if backup is not None:
            md_path.write_text(backup, encoding="utf-8")
        else:
            md_path.unlink(missing_ok=True)

    if company_id and rc == 0:
        mem_save(
            company_id,
            f"{dept_name}_{agent_key}_output",
            f"Agente {agent_key} executou em modo interativo. Verifique relatorio HTML para detalhes.",
            dept=dept_name,
            source=agent_key,
        )

    return {"status": "completed" if rc == 0 else "failed", "exit_code": rc}
