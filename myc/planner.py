"""
Planner — Gera e gerencia planos de execucao para empresas e departamentos.

Fluxo:
  1. Usuario passa query para empresa ou departamento
  2. Planner analisa os specialists disponiveis + a query
  3. Gera um plano com:
     - Fases sequenciais e paralelas
     - Dependencias entre agentes/departamentos
     - O que cada um vai fazer
  4. Usuario aprova o plano
  5. Executor executa os agentes na ordem definida

Memoria compartilhada da empresa permite que o output de um
agente seja input do proximo na cadeia.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()

MEMORY_DIR = Path.home() / ".myc" / "company_memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# Keywords usadas para detectar em qual depto/enquadramento a query se encaixa
DEPT_KEYWORDS = {
    "negocios": [
        "mercado", "concorrente", "swot", "estrategia", "viabilidade",
        "revenue", "preco", "pricing", "oportunidade", "risco",
        "vantagem", "fraqueza", "posicionamento", "segmento",
        "target", "publico-alvo", "persona", "analise",
    ],
    "gestao": [
        "sprint", "roadmap", "okrs", "kpi", "priorizar",
        "organizar", "timeline", "cronograma", "stack", "arquitetura",
        "revisar", "mentoria", "padrao", "scrum", "agile",
    ],
    "marketing": [
        "campanha", "seo", "instagram", "tiktok", "youtube",
        "redes sociais", "email marketing", "landing page",
        "social media", "calendario editorial", "influencer",
        "brand", "marca", "posicionamento de marca", "anuncio",
        "facebook ads", "google ads", "ads", "copywriting", "copy",
    ],
    "vendas": [
        "venda", "pitch", "funil", "crm", "lead", "conversao",
        "proposta", "comercial", "cliente", "contrato comercial",
        "upsell", "cross-sell", "receita", "quota",
    ],
    "desenvolvimento": [
        "api", "backend", "frontend", "codigo", "implementar",
        "banco de dados", "deploy", "docker", "kubernetes",
        "microservico", "teste", "bug", "feature", "endpoint",
        "rest", "graphql", "react", "vue", "angular",
        "python", "java", "javascript", "typescript",
    ],
    "financeiro": [
        "orcamento", "custo", "faturamento", "imposto", "nfe",
        "contabilidade", "lucro", "margem", "balanco",
        "folha", "salario", "investimento", "capex",
    ],
    "rh": [
        "contratar", "recru", "entrevista", "onboarding",
        "feedback", "avaliacao de desempenho", "treinamento",
        "cultura", "clima", "lideranca",
    ],
    "design": [
        "design", "visual", "mockup", "ui", "ux", "wireframe",
        "prototipo", "figma", "identidade visual", "logo",
        "paleta", "layout", "tipografia",
    ],
    "educacao": [
        "ensinar", "aula", "curso", "didatica", "exercicio",
        "prova", "quiz", "turma", "plano de aula",
        "avaliacao", "gabarito", "corrigir",
    ],
    "conteudo": [
        "artigo", "post", "blog", "texto", "newsletter",
        "ebook", "whitepaper", "manual", "documentacao",
        "tutorial", "guia", "roteiro", "video", "podcast",
    ],
}

# Dependencias padrao entre departamentos
DEFAULT_DEPT_DEPS = {
    "negocios": [],              # negocios nao depende de ninguem
    "dados": [],                 # dados é análise pura
    "seo": [],                   # seo é análise pura
    "gestao": ["negocios"],      # gestao precisa da analise de negocios
    "vendas": ["negocios", "marketing"],
    "marketing": ["negocios", "dados"],
    "financeiro": ["negocios", "vendas"],
    "design": ["gestao", "marketing"],
    "desenvolvimento": ["gestao", "design"],
    "rh": ["gestao"],
    "educacao": ["gestao"],
    "conteudo": ["marketing", "design"],
    "social": ["marketing"],     # social depende da estrategia de marketing
    "infra": ["desenvolvimento"],
}

# Departamentos de análise (sempro vem primeiro)
ANALYSIS_DEPTS = {"negocios", "dados", "seo", "financeiro"}

# Departamentos de execução (dependem da análise)
EXEC_DEPTS = {"marketing", "vendas", "design", "desenvolvimento", "conteudo", "social", "infra", "rh", "educacao", "gestao"}


def _tokenize(query: str) -> set[str]:
    """Tokeniza query em palavras e bigrams."""
    q = query.lower()
    tokens = set(re.findall(r"[a-z0-9/#+\-]+", q))
    words = re.findall(r"[a-z0-9]+", q)
    for i in range(len(words) - 1):
        tokens.add(f"{words[i]} {words[i+1]}")
    return tokens


def _match_departments(query: str, company_id: str | None = None) -> list[dict]:
    """Identifica quais departamentos sao relevantes para a query."""
    tokens = _tokenize(query)

    if company_id:
        from myc.agent_plugins import execute_company_profile
        from myc.agent_plugins import list_companies

        companies = list_companies()
        co = None
        for c in companies:
            if c["id"] == company_id:
                co = c
                break

        if co:
            # Extrai departamentos dos specialists da empresa
            dept_map: dict[str, list[dict]] = {}
            for sp in co.get("specialists", []):
                dept_name = sp.get("department", "geral")
                dept_map.setdefault(dept_name, []).append(sp)

            result = []
            for dept_name, specialists in dept_map.items():
                score = 0.0
                # Match keywords do depto
                dept_kw = DEPT_KEYWORDS.get(dept_name, [])
                for kw in dept_kw:
                    if kw in tokens:
                        score += 1.5
                    for w in re.findall(r"[a-z0-9]+", kw):
                        if w in tokens:
                            score += 0.3

                # Match nos roles dos specialists
                for sp in specialists:
                    role_words = set(re.findall(r"[a-z0-9]+", sp.get("role", "").lower()))
                    score += len(tokens & role_words) * 0.2

                if score > 0:
                    result.append({
                        "department": dept_name,
                        "specialists": specialists,
                        "score": round(score, 1),
                    })

            result.sort(key=lambda x: -x["score"])
            return result

    # Sem empresa especifica, tenta departamentos globais
    from myc.department import list_departments
    depts = list_departments(company_id=company_id)

    result = []
    for dept in depts:
        dept_name = dept.get("id", "")
        dept_kw = DEPT_KEYWORDS.get(dept_name, [])
        score = 0.0
        for kw in dept_kw:
            if kw in tokens:
                score += 1.5
            for w in re.findall(r"[a-z0-9]+", kw):
                if w in tokens:
                    score += 0.3

        if score > 0:
            result.append({
                "department": dept_name,
                "specialists": [{"id": sp} for sp in dept.get("specialists", [])],
                "score": round(score, 1),
            })

    return result


def _build_execution_graph(dept_matches: list[dict], query: str = "") -> list[dict]:
    """Constrói grafo de execucao com logica inteligente paralelo/sequencial.

    Regras:
      - Fase 0 (ANALISE): departamentos de análise rodam em paralelo entre si
      - Fase 1+ (EXECUCAO): departamentos de execucao ordenados por dependencias
      - Dentro de cada fase, departamentos sem dependencia entre si rodam em paralelo
      - Departamentos de execucao que dependem apenas de análise vão para Fase 1
      - Departamentos que dependem de outros de execucao vão para Fase 2+
    """
    matched_names = {m["department"] for m in dept_matches}

    # Separa análise e execução
    analysis_depts = [m for m in dept_matches if m["department"] in ANALYSIS_DEPTS]
    exec_depts = [m for m in dept_matches if m["department"] in EXEC_DEPTS]

    # Se só tem análise, todos rodam em paralelo
    if not exec_depts:
        for m in dept_matches:
            m["phase"] = 0
            m["depends_on"] = []
            m["execution_mode"] = "parallel"
            m["action"] = _dept_action(m["department"])
        return dept_matches

    # Se só tem execução, resolve dependencias normalmente
    if not analysis_depts:
        return _resolve_exec_phases(dept_matches)

    # Caso misto: análise primeiro, depois execução
    result = []

    # Fase 0: todos os de análise em paralelo
    for m in analysis_depts:
        result.append({
            "department": m["department"],
            "specialists": m["specialists"],
            "score": m["score"],
            "depends_on": [],
            "phase": 0,
            "action": _dept_action(m["department"]),
            "status": "pending",
            "execution_mode": "parallel",
        })

    # Resolve fases dos de execução
    exec_result = _resolve_exec_phases(exec_depts, analysis_dept_names=set(m["department"] for m in analysis_depts))
    for phase_info in exec_result:
        # Shift phases: se depends_on analysis depts, fase base = 1
        phase_info["phase"] += 1  # offset porque análise é fase 0

        # Exec departments implicitamente dependem de análise
        phase_info["depends_on"] = list(set(phase_info["depends_on"] + [m["department"] for m in analysis_depts]))

        result.append(phase_info)

    # Recalcula phases com dependencias cruzadas (análise -> execução)
    changed = True
    phase_map = {p["department"]: p for p in result}
    while changed:
        changed = False
        for name, phase_info in phase_map.items():
            if not phase_info["depends_on"]:
                new_phase = 0
            else:
                dep_phases = [phase_map[d]["phase"] for d in phase_info["depends_on"]
                             if d in phase_map]
                new_phase = max(dep_phases) + 1
            if new_phase != phase_info["phase"]:
                phase_info["phase"] = new_phase
                changed = True

    # Determina modo de execucao por fase
    from collections import Counter
    phase_counts = Counter(p["phase"] for p in result)
    for p in result:
        if phase_counts[p["phase"]] > 1:
            p["execution_mode"] = "parallel"
        else:
            p["execution_mode"] = "sequential"

    return list(phase_map.values())


def _resolve_exec_phases(exec_matches: list[dict], analysis_dept_names: set[str] | None = None) -> list[dict]:
    """Resolve fases para departamentos de execucao."""
    phase_map = {}
    all_exec = {m["department"] for m in exec_matches}

    for m in exec_matches:
        raw_deps = DEFAULT_DEPT_DEPS.get(m["department"], [])
        # Só considera deps entre os departamentos de execucao matching
        relevant_deps = [d for d in raw_deps if d in all_exec]
        analysis_deps = [d for d in raw_deps if d in ANALYSIS_DEPTS]

        phase_map[m["department"]] = {
            "department": m["department"],
            "specialists": m["specialists"],
            "score": m["score"],
            "depends_on": list(set(relevant_deps + analysis_deps)),
            "phase": 0,
            "action": _dept_action(m["department"]),
            "status": "pending",
            "execution_mode": "sequential",
        }

    # Resolve fases iterativamente
    changed = True
    while changed:
        changed = False
        for name, phase_info in phase_map.items():
            exec_deps = [d for d in phase_info["depends_on"] if d in phase_map]
            if not exec_deps:
                new_phase = 0
            else:
                dep_phases = [phase_map[d]["phase"] for d in exec_deps]
                new_phase = max(dep_phases) + 1
            if new_phase != phase_info["phase"]:
                phase_info["phase"] = new_phase
                changed = True

    from collections import Counter
    phase_counts = Counter(p["phase"] for p in phase_map.values())
    for p in phase_map.values():
        if phase_counts[p["phase"]] > 1:
            p["execution_mode"] = "parallel"

    return list(phase_map.values())


def _dept_action(dept: str) -> str:
    """Retorna descricao da acao do departamento."""
    actions = {
        "negocios": "Analise de mercado, concorrencia, viabilidade e definicao de publico-alvo",
        "gestao": "Planejamento, definicao de prioridades, organizacao do roadmap",
        "marketing": "Criacao de estrategia de marketing, conteudo e canais de aquisicao",
        "vendas": "Estrategia comercial, funil de vendas, abordagem de clientes",
        "design": "Criacao de identidade visual, mockups e prototipos",
        "desenvolvimento": "Implementacao tecnica, desenvolvimento e testes",
        "conteudo": "Producao de conteudo textual, artigos e materiais",
        "financeiro": "Analise financeira, orcamento e viabilidade economica",
        "rh": "Recursos humanos, contratacao e capacitacao",
        "educacao": "Criacao de material educativo e didatico",
        "dados": "Coleta, limpeza e analise de dados para embasar decisoes",
        "seo": "Analise de SEO, keywords, backlinks e performance organica",
        "social": "Gerenciamento de redes sociais e engajamento com publico",
        "infra": "Infraestrutura, deploy, monitoramento e escalabilidade",
    }
    return actions.get(dept, f"Execucao de tarefas de {dept}")


def generate_plan(
    query: str,
    company_id: str | None = None,
    department_id: str | None = None,
) -> dict[str, Any]:
    """Gerar plano de execucao completo.

    Args:
        query: tarefa do usuario
        company_id: empresa (opcional)
        department_id: departamento especifico (opcional)

    Returns:
        Plano com fases, agentes, e acoes.
    """
    # Se department_id especifico, foca apenas nele
    if department_id and not company_id:
        from myc.department import get_department_context, list_departments
        depts = list_departments()
        dept_data = None
        for d in depts:
            if d["id"] == department_id:
                dept_data = d
                break
        if dept_data:
            context = get_department_context(department_id)
            plan = {
                "query": query,
                "type": "department",
                "target": department_id,
                "created_at": datetime.now().isoformat(),
                "summary": f"Departamento '{department_id}' vai executar a tarefa.",
                "phases": [
                    {
                        "phase": 0,
                        "department": department_id,
                        "action": f"Executar tarefa via departamento {department_id}",
                        "specialists": dept_data.get("specialists", []),
                        "depends_on": [],
                        "status": "pending",
                    }
                ],
                "execution_mode": "single",
                "context": context or "",
            }
            return plan

    # Empresa ou global
    dept_matches = _match_departments(query, company_id)
    if not dept_matches:
        # Fallback: todos os departamentos da empresa ou apenas a query
        if company_id:
            from myc.agent_plugins import list_companies
            companies = list_companies()
            for c in companies:
                if c["id"] == company_id:
                    dept_matches = []
                    dept_map: dict[str, list] = {}
                    for sp in c.get("specialists", []):
                        d = sp.get("department", "geral")
                        dept_map.setdefault(d, []).append(sp)
                    for dn, specs in dept_map.items():
                        dept_matches.append({
                            "department": dn,
                            "specialists": specs,
                            "score": 1.0,
                        })
                    break

    if not dept_matches:
        return {
            "query": query,
            "type": "generic",
            "created_at": datetime.now().isoformat(),
            "summary": "Nenhum departamento especifico identificado. Execucao generica.",
            "phases": [],
            "execution_mode": "generic",
        }

    phases = _build_execution_graph(dept_matches, query)

    # Gerente de Projeto coordena antes e depois
    # Fase 0: Gerente de Projeto planeja e delega aos gerentes de departamento
    # Ultimas fases: Gerente de Projeto consolida resultados

    # Adiciona contexto de gerente em cada fase
    for p in phases:
        p["department_manager"] = f"Gerente de {p['department']}"
        p["task"] = f"Como Gerente de {p['department']}, coordene sua equipe para: {query}"

    # Gerente de Projeto como fase especial de coordenacao
    project_manager_phase = {
        "department": "gerente_projeto",
        "specialists": [{"id": "project_manager", "name": "Gerente de Projeto", "role": "Coordena todas as fases, delega tarefas aos gerentes de departamento e consolida resultados"}],
        "phase": -1,  # marker - runs before everything
        "action": "Coordenacao geral: analisa a tarefa, delega aos gerentes de departamento, acompanha execucao e consolida relatorio final",
        "depends_on": [],
        "status": "pending",
        "execution_mode": "coordinator",
    }

    # Fase de consolidacao (gerente revisa tudo ao final)
    consolidation_phase = {
        "department": "consolidacao",
        "specialists": [{"id": "consolidation", "name": "Consolidador de Resultados", "role": "Consolida outputs de todos os departamentos em relatorio final"}],
        "phase": max((p["phase"] for p in phases), default=0) + 1,
        "action": "Consolidacao final: revisa todos os outputs, gera relatorio executivo com insights cruzados",
        "depends_on": [p["department"] for p in phases if p["phase"] == max((pp["phase"] for pp in phases), default=0)],
        "status": "pending",
        "execution_mode": "sequential",
    }

    phases.insert(0, project_manager_phase)
    phases.append(consolidation_phase)

    # Determina modo de execucao
    regular_phases = [p for p in phases if p["phase"] >= 0]
    max_phase = max((p["phase"] for p in regular_phases), default=0)

    if max_phase == 0:
        exec_mode = "parallel"
    else:
        exec_mode = "sequential_with_parallel"

    # Gera resumo
    regular = [p for p in phases if p["phase"] >= 0]
    phase_summary_parts = []
    for phase_num in sorted(set(p["phase"] for p in regular)):
        depts_in_phase = [p["department"] for p in regular if p["phase"] == phase_num]
        mode = regular[0]["execution_mode"] if len(depts_in_phase) == 1 else "paralelo"
        phase_summary_parts.append(f"F{phase_num}:{','.join(depts_in_phase)}")

    summary = f"PM -> {' -> '.join(phase_summary_parts)} -> Consolidacao"

    plan = {
        "query": query,
        "type": "company" if company_id else "department",
        "company_id": company_id,
        "department_id": department_id,
        "created_at": datetime.now().isoformat(),
        "summary": summary,
        "phases": phases,
        "execution_mode": exec_mode,
        "total_agents": sum(len(p["specialists"]) for p in phases),
    }

    return plan


def display_plan(plan: dict) -> None:
    """Mostra o plano em formato visual bonito."""
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]PLANO DE EXECUCAO[/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")

    console.print(f"\n[dim]Tarefa:[/dim] {plan['query']}")
    console.print(f"[dim]Tipo:[/dim] {plan.get('type', '?')}")
    console.print(f"[dim]Modo:[/dim] ", end="")
    mode = plan.get("execution_mode", "?")
    if mode == "sequential":
        console.print("[yellow]Sequencial (fases dependentes)[/yellow]")
    elif mode == "parallel":
        console.print("[green]Paralelo (todos ao mesmo tempo)[/green]")
    elif mode == "sequential_with_parallel":
        console.print("[cyan]Misto (analise em paralelo, execucao sequencial com paralelismo)[/cyan]")
    else:
        console.print(f"[dim]{mode}[/dim]")

    if plan.get("summary"):
        console.print(f"\n[bold]Fluxo:[/bold] {plan['summary']}")

    if plan.get("phases"):
        console.print(f"\n[bold]Fases ({len(plan['phases'])}):\n")

        # Group by phase number
        from collections import defaultdict
        grouped: dict[int, list[dict]] = defaultdict(list)
        for p in plan["phases"]:
            grouped[p["phase"]].append(p)

        for phase_num in sorted(grouped.keys()):
            items = grouped[phase_num]

            if phase_num == -1:
                console.print(f"  [bold magenta]COORDENACAO: Gerente de Projeto[/bold magenta]")
                item = items[0]
                console.print(f"    [dim]{item['action']}[/dim]")
                console.print()
                continue

            if phase_num == 0 and any(i["department"] == "gerente_projeto" for i in items):
                continue  # ja exibido acima

            mode_label = items[0].get("execution_mode", "?")
            mode_icon = "[green]|| PARALELO[/green]" if mode_label == "parallel" else "[yellow]-> SEQUENCIAL[/yellow]"

            console.print(f"  [bold]Fase {phase_num}[/bold] {mode_icon}")

            for item in items:
                dept = item["department"]
                action = item["action"]
                specs = item["specialists"]
                deps = item.get("depends_on", [])
                mgr = item.get("department_manager", "")

                dep_str = f" [dim](deps: {', '.join(deps)})[/dim]" if deps else ""
                console.print(f"    [cyan]{dept}[/cyan]{dep_str}")
                if mgr:
                    console.print(f"      [dim]Gerente:[/dim] {mgr}")
                console.print(f"      [dim]Acao:[/dim] {action}")

                if specs:
                    spec_names = [s.get("name", s.get("id", "?")) for s in specs]
                    console.print(f"      [dim]Equipe:[/dim] {', '.join(spec_names)}")
                console.print()

    if plan.get("total_agents"):
        console.print(f"[bold]Total de agentes envolvidos:[/bold] {plan['total_agents']}")
        console.print()


def save_plan(plan: dict) -> str:
    """Salva o plano em disco para referencia futura."""
    plan_id = plan.get("company_id") or plan.get("department_id") or "generic"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_file = MEMORY_DIR / f"plan_{plan_id}_{ts}.json"
    plan_file.parent.mkdir(parents=True, exist_ok=True)
    plan_file.write_text(
        json.dumps(plan, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return str(plan_file)


def load_plans(plan_id: str | None = None, limit: int = 10) -> list[dict]:
    """Carrega planos salvos."""
    plans = []
    for f in sorted(MEMORY_DIR.glob("plan_*.json"), reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if plan_id and plan_id not in str(f):
                continue
            plans.append(data)
        except Exception:
            pass
        if len(plans) >= limit:
            break
    return plans
