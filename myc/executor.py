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


# ─── Fallback quando API falha ───────────────────────────

def _agent_fallback(agent_name: str, agent_role: str, query: str) -> str:
    """Gera um output basico baseado no papel do agente quando a API falha."""
    parts = [
        f"# Relatório: {agent_name}",
        f"\n**Papel:** {agent_role or 'N/A'}",
        f"\n**Tarefa:** {query}",
        "\n## Abordagem",
        f"Como {agent_name}, a abordagem esperada seria:",
        "",
    ]

    if any(w in agent_role.lower() for w in ["analytics", "dados", "data"]):
        parts.extend([
            "1. Coletar métricas do site (tráfego, conversões, bounce rate)",
            "2. Analisar comportamento do usuário com ferramentas como Google Analytics",
            "3. Cruzar dados com benchmarks de mercado",
            "4. Gerar dashboard com KPIs relevantes",
            "5. Identificar tendências e oportunidades de otimização",
        ])
    elif any(w in agent_role.lower() for w in ["seo", "search", "palavra"]):
        parts.extend([
            "1. Auditoria técnica do site (PageSpeed, Core Web Vitals)",
            "2. Pesquisa de palavras-chave relevantes para o nicho",
            "3. Análise de backlinks e autoridade de domínio",
            "4. Análise de concorrentes no ranking orgânico",
            "5. Plano de otimização on-page e link building",
        ])
    elif any(w in agent_role.lower() for w in ["social", "instagram", "tiktok"]):
        parts.extend([
            "1. Definir calendários editoriais mensais",
            "2. Criar estratégia de conteúdo por plataforma",
            "3. Planejar campanhas de engajamento",
            "4. Analisar métricas de redes sociais",
            "5. Identificar influencers e parcerias potenciais",
        ])
    elif any(w in agent_role.lower() for w in ["copy", "texto", "conteudo"]):
        parts.extend([
            "1. Pesquisar público-alvo e tom de voz da marca",
            "2. Criar copies para anúncios usando framework AIDA",
            "3. Desenvolver textos para landing pages",
            "4. Produzir artigos de blog com SEO otimizado",
            "5. Elaborar emails marketing com alto CTR",
        ])
    elif any(w in agent_role.lower() for w in ["gerente", "manager", "coordena"]):
        parts.extend([
            "1. Consolidar briefing da tarefa",
            "2. Delegar responsabilidades por departamento",
            "3. Definir prazos e dependências",
            "4. Acompanhar execução e remover blockers",
            "5. Gerar relatório final com recomendações",
        ])
    else:
        parts.extend([
            "1. Analisar requisitos da tarefa",
            "2. Executar análise do contexto fornecido",
            "3. Produzir deliverables específicos do departamento",
            "4. Documentar insights e recomendações",
        ])

    return "\n".join(parts)


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

                # Se foi um erro (rate limit esgotado), tenta fallback
                if result.get("status") == "failed" and result.get("error"):
                    console.print(f"  [yellow]Usando fallback para '{sp_name}'[/yellow]")
                    fallback = _agent_fallback(sp_name, sp_role, query)
                    if fallback:
                        if company_id:
                            from myc.company_memory import save as mem_save
                            mem_save(company_id, f"{dept_name}_{sp_id}_fallback", fallback, dept=dept_name, source=sp_id)
                        result = {"status": "completed_fallback", "exit_code": 0, "output": fallback}

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


def _call_llm_api(
    prompt: str,
    env_vars: dict,
    timeout: int = 120,
) -> str:
    """Chama o LLM diretamente via API OpenAI-compatible com retry."""
    import time
    import requests

    base_url = env_vars.get("OPENAI_BASE_URL", os.environ.get("OPENAI_BASE_URL", ""))
    api_key = env_vars.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
    model = env_vars.get("OPENAI_MODEL", os.environ.get("OPENAI_MODEL", "gpt-4o"))

    if not api_key:
        raise ValueError("OPENAI_API_KEY nao configurado")

    if base_url and not base_url.endswith("/v1"):
        base_url = base_url.rstrip("/") + "/v1"
    elif base_url:
        pass
    else:
        base_url = "https://api.openai.com/v1"

    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 8000,
        "temperature": 0.7,
    }

    # Retry com backoff exponencial para 429 / 5xx
    max_retries = 5
    for attempt in range(max_retries):
        if attempt > 0:
            wait = min(30 * (2 ** (attempt - 1)), 120)
            console.print(f"  [yellow]Rate limit. Aguardando {wait}s... (tentativa {attempt+1}/{max_retries})[/yellow]")
            time.sleep(wait)

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except requests.HTTPError as e:
            if "429" in str(e) and attempt < max_retries - 1:
                continue
            raise


def _dispatch_agent(context: str, query: str,
                    company_id: str | None,
                    dept_name: str,
                    agent_key: str) -> dict:
    """Despacha um agente com o contexto dado, usando API direta."""
    from myc.agent import _load_agents
    from myc.company_memory import save as mem_save

    agents = _load_agents()
    if "default" not in agents:
        console.print(f"  [yellow]Nenhum agente 'default'.[/yellow]")
        return {"status": "no_agent", "skipped": True}

    agent = agents["default"]
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

    console.print(f"\n  [dim]Chamando API ({len(full_prompt)} chars)...[/dim]")

    try:
        start = datetime.now()
        output = _call_llm_api(full_prompt, env_vars, timeout=120)
        elapsed = (datetime.now() - start).total_seconds()
        console.print(f"  [dim]Resposta recebida: {len(output)} chars ({elapsed:.1f}s)[/dim]")

        # Preview
        preview = output[:300]
        console.print(f"  [dim]Preview: {preview}{'...' if len(output) > 300 else ''}[/dim]")

        # Salva output real na memoria
        if company_id and output:
            mem_save(
                company_id,
                f"{dept_name}_{agent_key}_output",
                output,
                dept=dept_name,
                source=agent_key,
            )

        return {
            "status": "completed",
            "exit_code": 0,
            "output": output,
            "elapsed_s": round(elapsed, 1),
        }

    except Exception as e:
        console.print(f"  [red]Erro ao chamar API: {e}[/red]")
        return {"status": "failed", "error": str(e), "exit_code": 1}
