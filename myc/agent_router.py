"""
Roteador Automatico de Agentes.

Analisa a query/intencao do usuario e seleciona automaticamente:
  1. Qual agente usar
  2. Quais plugins vincular
  3. Se precisa criar agente novo

Fluxo:
  myc auto "crie uma API REST" -> dev
  myc auto "escreva artigo"    -> writer
  myc auto "campanha SEO"     -> business (+ plugins marketing)
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()

ROUTER_HISTORY_FILE = Path.home() / ".myc" / "router_history.json"

# Keywords por role — palavras que indicam cada tipo de trabalho
INTENT_KEYWORDS = {
    "dev": [
        "api", "backend", "frontend", "banco de dados", "database", "deploy",
        "docker", "microsservico", "rest", "graphql", "crud", "endpoint",
        "autenticacao", "jwt", "oauth", "servidor", "implement", "codigo",
        "programa", "arquitetura", "teste unitario", "pytest", "refatorar",
        "bug", "debug", "refactor", "clt", "css", "html", "javascript",
        "typescript", "react", "vue", "angular", "django", "flask",
        "fastapi", "express", "node", "python", "java", "go", "rust",
        "dockerfile", "container", "kubernetes", "k8s", "pipeline", "ci/cd",
        "servidor", "server", "endpoint", "route", "query", "sqlite",
        "postgres", "mongodb", "redis", "orm", "model", "swagger",
    ],
    "artist": [
        "ui", "ux", "interface", "designer", "design", "visual", "grafico",
        "arte", "icone", "logo", "banner", "mockup", "wireframe", "figma",
        "ilustracao", "sprite", "pixel", "modelo 3d", "textura", "animacao",
        "personagem", "cenario", "paleta", "identidade visual", "marca",
        "branding", "game design", "gamedesign", "nivel", "level",
    ],
    "writer": [
        "escreva", "escrever", "artigo", "post", "blog", "copywriting",
        "copy", "redacao", "traducao", "traduzir", "resumo", "relatorio",
        "ebook", "livro", "capitulo", "roteiro", "tutorial", "guia",
        "documentacao", "documentar", "newsletter", "comunicado", "manual",
        "texto", "conteudo", "paragrafo", "editorial", "whitepaper",
    ],
    "researcher": [
        "pesquisa", "pesquisar", "investigar", "coletar", "osint",
        "analise de dados", "data", "estatistica", "metrica", "kpi",
        "dashboard", "relatorio analitico", "benchmark", "concorrencia",
        "concorrente", "seguranca", "pentest", "vulnerabilidade", "owasp",
        "auditoria de seguranca", "forense", "rastreio",
    ],
    "educator": [
        "aula", "ensinar", "explicar", "explicacao", "didatica", "curso",
        "plano de aula", "atividade", "exercicio", "prova", "avaliacao",
        "aprendizado", "estudo", "questao", "quiz", "gabarito", "corrigir",
        "educacao", "pedagogia", "elearning",
    ],
    "musician": [
        "musica", "compor", "acorde", "melodia", "harmonia", "ritmo",
        "producao musical", "mixagem", "masterizacao", "beat",
        "trilha sonora", "audio", "letra", "cancao", "arranjo", "tablatura",
        "partitura", "instrumental",
    ],
    "business": [
        "venda", "vender", "pitch", "funil", "campanha", "marketing",
        "growth", "startup", "negocio", "lucro", "receita", "roi",
        "custo", "orcamento", "investimento", "cliente", "lead", "conversao",
        "persona", "publico", "seo", "instagram", "facebook", "linkedin",
        "redes sociais", "landing page", "email marketing", "crm", "swot",
        "plano de negocio", "modelo de negocio", "empreendedor",
        "growth hacking", "funil de vendas", "campanha de marketing",
    ],
}

# Mapeia role -> bundles recomendados
ROLE_TO_BUNDLES = {
    "dev": ["fullstack", "software_engineering", "computer_engineering", "data_engineering", "app_mobile"],
    "artist": ["gamedesign", "visao_computacional"],
    "writer": ["jornalismo", "advocacia"],
    "researcher": ["osint", "bugbounty", "seguranca_web"],
    "educator": ["professor"],
    "musician": [],
    "business": ["vendas", "ideias", "marketing"],
}

# Mapeia role -> empresas recomendadas
ROLE_TO_COMPANIES = {
    "dev": ["dev_agency", "devops_company", "data_company"],
    "business": ["marketing_agency_company", "sales_company"],
    "writer": ["news_media_company"],
    "researcher": ["security_company", "bounty_company"],
}

# Keywords por empresa para matching mais fino
COMPANY_EXTRA_KEYWORDS = {
    "dev_agency": ["software", "api", "agencia", "tech lead", "frontend", "backend", "deploy", "microservico"],
    "design_studio": ["design", "visual", "marca", "identidade", "logo", "ui", "ux"],
    "marketing_agency_company": ["campanha", "marketing", "social media", "seo", "instagram"],
    "game_studio_company": ["jogo", "game", "unity", "game design", "gameplay", "mecanica"],
}

# Bundles que tem keywords extras pra matching fino
BUNDLE_EXTRA_KEYWORDS = {
    "fullstack": ["api", "backend", "frontend", "crud", "api rest", "site", "web app"],
    "software_engineering": ["arquitetura", "design pattern", "clean code", "refatorar", "clean", "padrao"],
    "computer_engineering": ["iot", "hardware", "embarcado", "raspberry", "arduino", "esp32"],
    "data_engineering": ["etl", "pipeline de dados", "data warehouse", "spark", "airflow", "dados"],
    "gamedesign": ["jogo", "game", "mecanica", "gameplay", "game design"],
    "advocacia": ["lei", "contrato", "peticao", "juridico", "legislacao", "direito"],
    "jornalismo": ["pauta", "reportagem", "noticia", "jornalismo", "redacao"],
    "osint": ["investigacao", "rastreio", "osint", "fonte aberta", "perfil"],
    "seguranca_web": ["seguranca", "pentest", "owasp", "vulnerabilidade", "auditoria"],
    "bugbounty": ["bug", "exploit", "cve", "triagem", "bug bounty"],
    "visao_computacional": ["visao computacional", "cnn", "opencv", "detecao", "imagem", "yolo"],
    "app_mobile": ["mobile", "app", "react native", "flutter", "android", "ios"],
    "ideias": ["brainstorm", "ideia", "validacao", "mvp", "prototipo", "design thinking"],
    "vendas": ["pitch", "venda", "funil", "growth", "crescimento", "crm"],
    "professor": ["aula", "prova", "exercicio", "plano de aula", "educacao"],
    "marketing": ["seo", "instagram", "campanha", "social", "redes sociais", "email marketing"],
}

# Pesos por tipo de acao
ACTION_WEIGHT = {
    "crie": 1.5, "criar": 1.5, "faca": 1.3, "implemente": 2.0,
    "desenvolva": 2.0, "escreva": 1.5, "escrever": 1.3,
    "analise": 1.8, "investigue": 2.0, "pesquise": 1.5,
    "ensine": 1.5, "explique": 1.3,
}


def _tokenize_and_expand(query: str) -> set[str]:
    """Tokeniza a query e gera n-grams para match multi-palavra."""
    q = query.lower()
    tokens = set(re.findall(r"[a-z0-9#+/\-]+", q))
    # Bigrams e trigrams
    words = re.findall(r"[a-z0-9]+", q)
    for i in range(len(words) - 1):
        tokens.add(f"{words[i]} {words[i+1]}")
    if len(words) > 2:
        for i in range(len(words) - 2):
            tokens.add(f"{words[i]} {words[i+1]} {words[i+2]}")
    return tokens


def _detect_action_weight(query: str) -> float:
    """Detecta peso baseado no verbo de acao na query."""
    q = query.lower()
    for action, weight in ACTION_WEIGHT.items():
        if action in q:
            return weight
    return 1.0


def score_roles(query: str) -> list[tuple[str, float]]:
    """Retorna lista de (role, score) ordenada por score."""
    tokens = _tokenize_and_expand(query)
    action_w = _detect_action_weight(query)
    scores: dict[str, float] = {}

    for role, keywords in INTENT_KEYWORDS.items():
        score = 0.0
        for kw in keywords:
            if kw in tokens:
                weight = 1.0 if len(kw) > 3 else 0.5
                score += weight
        scores[role] = round(score * action_w, 1)

    return sorted(scores.items(), key=lambda x: -x[1])


def _find_agent_for_role(role: str) -> str | None:
    """Busca um agente com o role especificado."""
    from myc.agent import _load_agents
    agents = _load_agents()
    for name, profile in agents.items():
        if profile.get("role") == role:
            return name
    return None


def _find_all_agents() -> list[dict]:
    """Retorna lista de agentes com seus roles e plugins."""
    from myc.agent import _load_agents
    agents = _load_agents()
    return [
        {"name": n, "role": p.get("role", "generalist"), "plugins": p.get("plugin_filter", []) or p.get("plugins", [])}
        for n, p in agents.items()
    ]


def score_bundles(query: str, top_role: str) -> list[dict]:
    """Score de bundles baseado em match de keywords extras + role match."""
    tokens = _tokenize_and_expand(query)
    scored = []

    bundles_for_role = ROLE_TO_BUNDLES.get(top_role, [])
    all_bundle_ids = set(list(BUNDLE_EXTRA_KEYWORDS.keys()) + bundles_for_role)

    for bid in all_bundle_ids:
        score = 0.0
        # Role match bonus
        if bid in bundles_for_role:
            score += 3.0

        # Keyword match
        keywords = BUNDLE_EXTRA_KEYWORDS.get(bid, [])
        for kw in keywords:
            if kw in tokens:
                score += 1.5

        if score > 0:
            scored.append({"id": bid, "score": round(score, 1)})

    scored.sort(key=lambda x: -x["score"])
    return scored


def _load_companies() -> list[dict]:
    """Lista companies instaladas."""
    from myc.agent_plugins import list_companies
    try:
        return list_companies()
    except Exception:
        return []


def score_companies(query: str, top_role: str) -> list[dict]:
    """Score de empresas baseado em role + keyword match nos specialists."""
    tokens = _tokenize_and_expand(query)
    scored = []

    companies_for_role = ROLE_TO_COMPANIES.get(top_role, [])
    companies = _load_companies()

    for co in companies:
        co_id = co.get("id", "")
        score = 0.0

        # Role match bonus
        if co_id in companies_for_role:
            score += 4.0

        # Keyword match nos specialists
        for sp in co.get("specialists", []):
            sp_role = sp.get("role", "").lower()
            sp_dept = sp.get("department", "")

            # Match dept keyword
            if sp_dept and sp_dept.lower() in tokens:
                score += 1.0

            # Match no role (pega palavras chave)
            role_words = re.findall(r"[a-z0-9]+", sp_role)
            for w in role_words:
                if len(w) > 3 and w in tokens:
                    score += 0.3

        # Extra keywords
        extra = COMPANY_EXTRA_KEYWORDS.get(co_id, [])
        for kw in extra:
            if kw in tokens:
                score += 2.0

        if score > 0:
            scored.append({
                "id": co_id,
                "name": co.get("name", co_id),
                "score": round(score, 1),
                "specialists": co.get("specialists", []),
            })

    scored.sort(key=lambda x: -x["score"])
    return scored


def _load_departments() -> list[dict]:
    """Lista departamentos instalados."""
    from myc.department import list_departments
    try:
        return list_departments()
    except Exception:
        return []


def score_departments(query: str, top_company: str | None = None) -> list[dict]:
    """Filtra departamentos relevantes. Se company for dada, filtra por ela."""
    tokens = _tokenize_and_expand(query)
    scored = []
    depts = _load_departments()

    for dept in depts:
        dept_id = dept.get("id", "")
        score = 0.0

        # Filter by company se fornecida
        dept_company = dept.get("parent_company")
        if top_company and dept_company and dept_company != top_company:
            continue

        # Match no nome e descricao
        for term in [dept.get("name", ""), dept.get("description", "")]:
            for w in re.findall(r"[a-z0-9]+", term.lower()):
                if len(w) > 3 and w in tokens:
                    score += 0.5

        # Match nos specialist names
        for sp_id in dept.get("specialists", []):
            if sp_id.lower() in tokens:
                score += 1.0

        if score > 0:
            scored.append({
                "id": dept_id,
                "name": dept.get("name", dept_id),
                "score": round(score, 1),
                "parent_company": dept_company,
                "specialists": dept.get("specialists", []),
            })

    scored.sort(key=lambda x: -x["score"])
    return scored


def analyze(query: str) -> dict:
    """Analisa a query e retorna recomendação completa."""
    role_scores = score_roles(query)
    top_role = role_scores[0][0] if role_scores and role_scores[0][1] > 0 else "generalist"
    top_score = role_scores[0][1] if role_scores else 0

    # Filtra scores relevantes (> 0)
    active_roles = [(r, s) for r, s in role_scores if s > 0]

    bundles = score_bundles(query, top_role)
    agent = _find_agent_for_role(top_role)
    companies = score_companies(query, top_role)
    departments = score_departments(query)

    # Top department
    top_dept = departments[0] if departments else None

    # Se tem empresa top, filtra departamentos dela
    top_company = companies[0] if companies else None
    if top_company:
        dept_in_company = score_departments(query, top_company["id"])
        if dept_in_company:
            departments = dept_in_company
            top_dept = departments[0]

    # Determina o nivel: company > agent > uncertain
    # Se tem empresa com score alto, prioriza company-level
    has_company = bool(top_company) and top_company["score"] > 5
    has_dept = bool(top_dept) and top_dept["score"] > 2

    # Calcula confianca (0-100)
    confidence = min(int(top_score * 15), 100)

    result = {
        "query": query,
        "top_role": top_role,
        "top_score": top_score,
        "confidence": confidence,
        "active_roles": active_roles[:4],
        "agent": agent if not has_company else None,
        "bundles": bundles[:5],
        "companies": companies[:5],
        "departments": departments[:5],
        "top_company": top_company,
        "top_dept": top_dept,
        "action": _determine_action_complex(agent, confidence, has_company, has_dept),
    }

    return result


def _determine_action(agent: str | None, confidence: int) -> str:
    """Decide acao com base na disponibilidade do agente e confianca."""
    if agent and confidence >= 20:
        return "use_existing"
    if agent and confidence < 20:
        return "existing_but_low"
    if confidence >= 15:
        return "suggest_create"
    return "uncertain"


def _determine_action_complex(agent: str | None, confidence: int,
                              has_company: bool, has_dept: bool) -> str:
    """Decide acao considerando companies e departments."""
    if has_company:
        return "use_company"
    if agent and confidence >= 20:
        return "use_existing"
    if agent and confidence < 20:
        return "existing_but_low"
    if confidence >= 15:
        return "suggest_create"
    return "uncertain"


def auto_route(query: str, auto_launch: bool = True) -> int:
    """Fluxo completo: analisa, seleciona, e opcionalmente lança o agente.

    Suporta 3 niveis: empresa, departamento, agente individual.
    """
    import questionary

    result = analyze(query)
    action = result["action"]
    agent_name = result["agent"]
    top_role = result["top_role"]
    confidence = result["confidence"]
    top_company = result.get("top_company")
    top_dept = result.get("top_dept")

    # Mostra analise
    console.print(f"\n[bold cyan]Auto-Router: Analise de Intencao[/bold cyan]")
    console.print(f"[dim]Query: {query}[/dim]\n")

    console.print("[bold]Intencao detectada:[/bold]")
    for role, score in result["active_roles"]:
        bar = "#" * max(1, int(score * 1.5))
        console.print(f"  [cyan]{role}[/cyan]: {score:.1f} {bar}")

    if result["bundles"]:
        console.print(f"\n[bold]Bundles/plugins recomendados:[/bold]")
        for b in result["bundles"]:
            console.print(f"  [green]{b['id']}[/green] (score: {b['score']})")

    if result.get("companies"):
        console.print(f"\n[bold]Empresas recomendadas:[/bold]")
        for c in result["companies"][:3]:
            console.print(f"  [magenta]{c['name']}[/magenta] (score: {c['score']})")

    if result.get("departments"):
        console.print(f"\n[bold]Departamentos recomendados:[/bold]")
        for d in result["departments"][:3]:
            parent = f" ({d['parent_company']})" if d.get("parent_company") else ""
            console.print(f"  [yellow]{d['name']}[/yellow]{parent} (score: {d['score']})")

    console.print(f"\n[bold]Acao:[/bold] {action} (confianca: {confidence}%)")

    # Salva no historico
    _save_routing_history(result)

    # ── CAMINHO 1: Empresa + Departamento ──────────────────────
    if action == "use_company" and top_company:
        company_id = top_company["id"]
        console.print(f"\n[bold magenta]Empresa selecionada: {top_company['name']}[/bold magenta]")

        # Tenta encontrar specialist adequado da empresa
        specs = top_company.get("specialists", [])
        specialists = []
        for s in specs:
            sp_id = s.get("id", "")
            sp_role = s.get("role", "").lower()
            # Score simples: match de keywords da query no role do specialist
            qwords = set(_tokenize_and_expand(query))
            sp_words = set(re.findall(r"[a-z0-9]+", sp_role))
            overlap = len(qwords & sp_words)
            specialists.append((s, overlap))

        specialists.sort(key=lambda x: -x[1])

        # Mostra os top specialists
        console.print("\n[bold]Specialists mais relevantes:[/bold]")
        for s, sc in specialists[:5]:
            console.print(f"  [green]{s['name']}[/green] ({s['id']}) — match: {sc}")

        # Usa o top specialist
        top_spec = specialists[0][0] if specialists else None

        if top_spec:
            console.print(f"\n[dim]Specialist selecionado: {top_spec['name']} ({top_spec['id']})[/dim]")
            if auto_launch:
                to_launch = True
            else:
                to_launch = questionary.confirm("Lancar?", default=True).ask()

            if to_launch:
                return _launch_company_specialist(company_id, top_spec["id"], query)
        else:
            # So mostra a empresa
            from myc.agent_plugins import execute_company_profile
            ctx = execute_company_profile(company_id)
            console.print(ctx)
            return 0

    # ── CAMINHO 2: Departamento independente ──────────────────
    elif action == "use_existing" and top_dept and not agent_name:
        dept_id = top_dept["id"]
        console.print(f"\n[bold yellow]Departamento selecionado: {top_dept['name']}[/bold yellow]")

        if auto_launch:
            to_launch = True
        else:
            to_launch = questionary.confirm("Lancar?", default=True).ask()

        if to_launch:
            return _launch_department(dept_id, query)
        return 0

    # ── CAMINHO 3: Agente individual ──────────────────────────
    elif action in ("use_existing", "existing_but_low") and agent_name:
        console.print(f"[bold green]Agente selecionado: {agent_name}[/bold green] (role: {top_role})")

        all_agents = _find_all_agents()
        profile = None
        for a in all_agents:
            if a["name"] == agent_name:
                profile = a
                break

        if profile:
            from myc.agent import _load_agents, _save_agents, launch_agent
            agents = _load_agents()

            if agent_name not in agents:
                console.print(f"[red]Agente '{agent_name}' nao encontrado.[/red]")
                return 1

            original_plugins = list(agents[agent_name].get("plugin_filter", []) or agents[agent_name].get("plugins", []) or [])

            # Adiciona plugins dos bundles temporariamente
            temp_added = []
            if result["bundles"]:
                from myc.plugin_manager import BUNDLES
                for b in result["bundles"][:3]:
                    if b["id"] in BUNDLES:
                        for plugin_id in BUNDLES[b["id"]]["plugins"]:
                            agents[agent_name].setdefault("plugin_filter", [])
                            if plugin_id not in agents[agent_name]["plugin_filter"]:
                                agents[agent_name]["plugin_filter"].append(plugin_id)
                            agents[agent_name].setdefault("plugins", [])
                            if plugin_id not in agents[agent_name]["plugins"]:
                                agents[agent_name]["plugins"].append(plugin_id)
                            temp_added.append(plugin_id)

            if temp_added:
                _save_agents(agents)
                console.print(f"[dim]+ {len(temp_added)} plugins vinculados temporariamente: {', '.join(temp_added)}[/dim]")

            if auto_launch:
                to_launch = True
            else:
                to_launch = questionary.confirm("Lancar agente?", default=True).ask()

            rc = 0
            if to_launch:
                cwd = agents[agent_name].get("cwd")
                rc = launch_agent(agent_name, cwd=cwd)

            # Restaura plugins originais
            if temp_added:
                agents = _load_agents()
                agents[agent_name]["plugins"] = original_plugins
                agents[agent_name]["plugin_filter"] = original_plugins
                _save_agents(agents)
                console.print(f"\n[dim]Plugins restaurados.[/dim]")

            return rc
        return 1

    elif action == "suggest_create":
        console.print(f"[yellow]Nenhum agente/empresa com role '{top_role}' encontrado.[/yellow]")

        choices = [
            questionary.Choice(f"Criar agente '{top_role}'", value="create"),
            questionary.Choice("Escolher agente existente", value="choose"),
            questionary.Choice("Cancelar", value="cancel"),
        ]
        choice = questionary.select("Opcao:", choices=choices).ask()

        if choice == "create":
            _create_agent_for_role(top_role, result["bundles"], query)
            return 1
        elif choice == "choose":
            agents = _find_all_agents()
            if not agents:
                console.print("[red]Nenhum agente configurado.[/red]")
                return 1
            agent_choices = [
                questionary.Choice(f"{a['name']} (role: {a['role']})", value=a["name"])
                for a in agents
            ]
            chosen = questionary.select("Agente:", choices=agent_choices).ask()
            if chosen:
                from myc.agent import launch_agent
                return launch_agent(chosen)
            return 0
        return 0

    else:  # action == "uncertain"
        console.print(f"[yellow]Intencao nao clara (confianca: {confidence}%). Escolha manualmente:[/yellow]")
        agents = _find_all_agents()
        if not agents:
            console.print("[red]Nenhum agente configurado.[/red]")
            return 1

        choices = [
            questionary.Choice(f"{a['name']} (role: {a['role']})", value=a["name"])
            for a in agents
        ]
        choice = questionary.select("Agente:", choices=choices).ask()
        if choice:
            from myc.agent import launch_agent
            return launch_agent(choice)
        return 0


def _launch_company_specialist(company_id: str, specialist_id: str, query: str) -> int:
    """Lanca um specialist de uma empresa com a query."""
    from myc.agent_plugins import execute_company_profile
    from myc.agent import _load_agents, launch_agent
    from pathlib import Path

    console.print(f"\n[bold dim]Lancando {specialist_id} na empresa {company_id}...[/bold dim]")

    context = execute_company_profile(company_id, specialist_id=specialist_id)
    if not context:
        return 1

    agents = _load_agents()
    if "default" not in agents:
        console.print(f"[yellow]Nenhum agente 'default' configurado. Mostrando contexto:[/yellow]")
        console.print(f"\n[bold]{company_id}/{specialist_id}[/bold]")
        console.print(f"\n## Contexto\n{context}\n\n## Tarefa\n{query}")
        return 0

    # Injeta no CLAUDE.md
    cwd = agents["default"].get("cwd") or str(Path.cwd())
    md_path = Path(cwd) / "CLAUDE.md"
    backup = None
    if md_path.exists():
        backup = md_path.read_text(encoding="utf-8")

    body = f"# Agent: {company_id}/{specialist_id}\n\n{context}\n\n---\n\n## Tarefa\n{query}"
    md_path.write_text(body, encoding="utf-8")

    try:
        rc = launch_agent("default", cwd=cwd)
    finally:
        if backup is not None:
            md_path.write_text(backup, encoding="utf-8")
        else:
            md_path.unlink(missing_ok=True)

    return rc


def _launch_department(dept_id: str, query: str) -> int:
    """Lanca um departamento com a query."""
    from myc.department import get_department_context
    from myc.agent import _load_agents, launch_agent
    from pathlib import Path

    context = get_department_context(dept_id)
    if not context:
        console.print(f"[red]Departamento '{dept_id}' nao encontrado.[/red]")
        return 1

    console.print(f"\n[bold dim]Lancando departamento {dept_id}...[/bold dim]")

    agents = _load_agents()
    if "default" not in agents:
        console.print(f"[yellow]Nenhum agente 'default' configurado. Mostrando contexto:[/yellow]")
        console.print(f"\n[bold]Departamento: {dept_id}[/bold]")
        console.print(f"\n{context}\n\n---\n\n## Tarefa\n{query}")
        return 0

    cwd = agents["default"].get("cwd") or str(Path.cwd())
    md_path = Path(cwd) / "CLAUDE.md"
    backup = None
    if md_path.exists():
        backup = md_path.read_text(encoding="utf-8")

    body = f"# Agent: department/{dept_id}\n\n{context}\n\n---\n\n## Tarefa\n{query}"
    md_path.write_text(body, encoding="utf-8")

    try:
        rc = launch_agent("default", cwd=cwd)
    finally:
        if backup is not None:
            md_path.write_text(backup, encoding="utf-8")
        else:
            md_path.unlink(missing_ok=True)

    return rc


def _create_agent_for_role(role: str, bundles: list[dict], query: str) -> None:
    """Cria um novo agente para um role especifico."""
    from myc.agent import _load_agents, _save_agents
    from datetime import datetime

    name = f"auto_{role}"
    agents = _load_agents()

    # Checa se ja existe
    if name in agents:
        console.print(f"[dim]Agente '{name}' ja existe, atualizando plugins.[/dim]")
        profile = agents[name]
    else:
        profile = {
            "name": name,
            "platform": "openclaude",
            "env": {"CLAUDE_CODE_USE_OPENAI": "1", "OPENAI_BASE_URL": "https://generativelanguage.googleapis.com/v1beta/openai", "OPENAI_API_KEY": "", "OPENAI_MODEL": "gemini-2.5-pro"},
            "cwd": None,
            "initial_context": "",
            "custom_command": None,
            "linked_routines": [],
            "role": role,
            "plugin_filter": [],
            "callable_agents": [],
            "created_at": datetime.now().isoformat(),
        }

    # Instala plugins dos bundles
    if bundles:
        from myc.plugin_manager import BUNDLES
        for b in bundles[:3]:
            if b["id"] in BUNDLES:
                for plugin_id in BUNDLES[b["id"]]["plugins"]:
                    if plugin_id not in profile.setdefault("plugin_filter", []):
                        profile["plugin_filter"].append(plugin_id)
                    if plugin_id not in profile.setdefault("plugins", []):
                        profile["plugins"].append(plugin_id)
        _save_plugins_for_profile(profile)

    agents[name] = profile
    _save_agents(agents)
    console.print(f"[green]Agente '{name}' criado (role: {role}, {len(profile.get('plugins', []))} plugins).[/green]")


def _save_plugins_for_profile(profile: dict) -> None:
    """Instala plugins fisicamente para o profile."""
    from myc.plugin_installer import install_plugin
    from myc.plugin_manager import BUNDLES

    try:
        from myc.agent_plugins import _ensure_plugins_dir
        _ensure_plugins_dir()
    except ImportError:
        pass

    installed = 0
    for plugin_id in profile.get("plugins", []):
        # Tenta install
        try:
            if install_plugin(plugin_id):
                installed += 1
        except Exception:
            pass

    if installed:
        console.print(f"[dim]  {installed} plugins instalados.[/dim]")


def _save_routing_history(result: dict) -> None:
    """Salva decisao de roteamento no historico."""
    if ROUTER_HISTORY_FILE.exists():
        try:
            entries = json.loads(ROUTER_HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            entries = []
    else:
        entries = []

    entries.insert(0, {
        "query": result["query"],
        "top_role": result["top_role"],
        "agent": result["agent"],
        "action": result["action"],
        "confidence": result["confidence"],
        "bundles": [b["id"] for b in result.get("bundles", [])],
        "timestamp": datetime.now().isoformat(),
    })

    ROUTER_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    ROUTER_HISTORY_FILE.write_text(
        json.dumps(entries[:200], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def show_history(limit: int = 20) -> None:
    """Mostra historico de decisoes de roteamento."""
    if ROUTER_HISTORY_FILE.exists():
        try:
            entries = json.loads(ROUTER_HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            entries = []
    else:
        entries = []

    if not entries:
        console.print("[yellow]Nenhum historico de roteamento.[/yellow]")
        return

    entries = entries[:limit]

    table = Table(title="Historico de Auto-Router", show_lines=True)
    table.add_column("Data", style="dim")
    table.add_column("Query", style="cyan", max_width=40)
    table.add_column("Role", style="yellow")
    table.add_column("Agente", style="green")
    table.add_column("Acao", style="magenta")
    table.add_column("Conf.", style="dim")

    for e in entries:
        table.add_row(
            (e.get("timestamp", "") or "")[:19],
            e.get("query", "")[:50],
            e.get("top_role", "?"),
            e.get("agent", "-"),
            e.get("action", "?"),
            f"{e.get('confidence', 0)}%",
        )

    console.print(table)
