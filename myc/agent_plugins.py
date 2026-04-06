"""
Sistema de plugins para agentes.

Dois tipos de plugins:
  1. Especialistas (specialists) — um agente especialista em um conteudo especifico.
     Cada plugin exporta NAME, DESCRIPTION, PRE_LAUNCH, POST_LAUNCH, CONTEXT.

  2. Empresas (companies) — uma empresa com multiplos agentes especialistas.
     Cada plugin de empresa exporta NAME, DESCRIPTION, SPECIALISTS (lista de
     sub-agentes), cada sub-agente com seu proprio prompt e lista de specialists
     que pode reutilizar. Tambem gera um prompt melhorado com padrao corporativo.

Cada especialista e um arquivo Python em ~/.myc/agents/plugins/ que exporta:
  - NAME: str                    — nome do plugin
  - DESCRIPTION: str             — descricao curta
  - PRE_LAUNCH(agent_profile)    — hook antes de lancar o agente
  - POST_LAUNCH(agent_profile)   — hook apos o agente iniciar (opcional)
  - CONTEXT(agent_profile) -> str  — texto extra para injetar no CLAUDE.md

Cada empresa e um arquivo Python em ~/.myc/agents/companies/ que exporta:
  - NAME: str                    — nome da empresa
  - DESCRIPTION: str             — descricao curta
  - SPECIALISTS: list[dict]      — lista de sub-agentes especialistas na empresa
    Cada sub-agente tem:
      - id: str                  — identificador unico do sub-agente
      - name: str                — nome display
      - role: str                — papel/descricao detalhada (prompt base)
      - specialists: list[str]   — IDs de plugins specialists que reutiliza
      - context: str (opt)       — contexto adicional especifico da empresa
  - COMPANY_CONTEXT() -> str     — contexto geral da empresa (opcional)
"""

import importlib.util
import shutil
import sys
from pathlib import Path
from typing import Any

from rich.console import Console

console = Console()

PLUGINS_DIR = Path.home() / ".myc" / "agents" / "plugins"
COMPANIES_DIR = Path.home() / ".myc" / "agents" / "companies"

# Plugins built-in dentro do pacote
def _get_pkg_plugins_dir(subfolder: str = "specialists") -> Path:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / "plugins" / subfolder
    return Path(__file__).parent.parent / "plugins" / subfolder

MYC_SPECIALISTS = _get_pkg_plugins_dir("specialists")
MYC_COMPANIES = _get_pkg_plugins_dir("companies")


def _ensure_plugins_dir() -> None:
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_companies_dir() -> None:
    COMPANIES_DIR.mkdir(parents=True, exist_ok=True)


def _load_plugin_file(filepath: Path) -> Any | None:
    """Carrega um modulo plugin a partir do arquivo .py."""
    spec = importlib.util.spec_from_file_location(filepath.stem, filepath)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── Specialists ──────────────────────────────────────────────

def list_plugins() -> list:
    """Lista todos os specialists disponiveis com seus metadados."""
    _ensure_plugins_dir()
    plugins = []
    for f in PLUGINS_DIR.glob("*.py"):
        if f.stem.startswith("_"):
            continue
        try:
            mod = _load_plugin_file(f)
            if mod and hasattr(mod, "NAME"):
                plugins.append({
                    "id": f.stem,
                    "name": getattr(mod, "NAME", f.stem),
                    "description": getattr(mod, "DESCRIPTION", ""),
                    "file": str(f),
                })
        except Exception as e:
            plugins.append({
                "id": f.stem,
                "name": f"[ERRO] {f.name}",
                "description": str(e),
                "file": str(f),
            })
    return plugins


def execute_plugins(agent_profile: dict, hook: str = "PRE_LAUNCH") -> str:
    """Executa o hook de todos os specialists listados no perfil do agente.

    Retorna texto extra de contexto gerado pelos specialists (para CLAUDE.md).
    """
    plugins_list = agent_profile.get("plugins", [])
    if not plugins_list:
        return ""

    _ensure_plugins_dir()
    context_parts = []

    for plugin_id in plugins_list:
        plugin_file = PLUGINS_DIR / f"{plugin_id}.py"

        # Fallback para builtin specialists
        if not plugin_file.exists() and (MYC_SPECIALISTS / f"{plugin_id}.py").exists():
            shutil.copy2(str(MYC_SPECIALISTS / f"{plugin_id}.py"), str(plugin_file))

        if not plugin_file.exists():
            console.print(f"[yellow]Specialist '{plugin_id}' nao encontrado, ignorando.[/yellow]")
            continue

        try:
            mod = _load_plugin_file(plugin_file)
            if not mod:
                continue

            hook_fn = getattr(mod, hook, None)
            if hook_fn:
                try:
                    result = hook_fn(agent_profile)
                    if hook != "PRE_LAUNCH" and result:
                        console.print(f"[green]Specialist '{getattr(mod, 'NAME', plugin_id)}' ({hook}) executado.[/green]")
                except Exception as e:
                    console.print(f"[red]Specialist '{getattr(mod, 'NAME', plugin_id)}' ({hook}) falhou: {e}[/red]")

            ctx_fn = getattr(mod, "CONTEXT", None)
            if ctx_fn:
                try:
                    extra = ctx_fn(agent_profile)
                    if extra:
                        context_parts.append(f"### Specialist: {getattr(mod, 'NAME', plugin_id)}\n\n{extra}")
                except Exception as e:
                    console.print(f"[red]Specialist '{getattr(mod, 'NAME', plugin_id)}' CONTEXT falhou: {e}[/red]")

        except Exception as e:
            console.print(f"[red]Erro no specialist '{plugin_id}': {e}[/red]")

    return "\n\n".join(context_parts)


# ── Companies ────────────────────────────────────────────────

def list_companies() -> list:
    """Lista todas as companies disponiveis com seus metadados."""
    _ensure_companies_dir()
    companies = []
    for f in COMPANIES_DIR.glob("*.py"):
        if f.stem.startswith("_"):
            continue
        try:
            mod = _load_plugin_file(f)
            if mod and hasattr(mod, "NAME"):
                companies.append({
                    "id": f.stem,
                    "name": getattr(mod, "NAME", f.stem),
                    "description": getattr(mod, "DESCRIPTION", ""),
                    "specialists": getattr(mod, "SPECIALISTS", []),
                    "file": str(f),
                })
        except Exception as e:
            companies.append({
                "id": f.stem,
                "name": f"[ERRO] {f.name}",
                "description": str(e),
                "file": str(f),
            })
    return companies


def _resolve_specialist_context(specialist_id: str) -> str:
    """Carrega o CONTEXT de um specialist pelo ID."""
    plugin_file = PLUGINS_DIR / f"{specialist_id}.py"

    if not plugin_file.exists() and (MYC_SPECIALISTS / f"{specialist_id}.py").exists():
        shutil.copy2(str(MYC_SPECIALISTS / f"{specialist_id}.py"), str(plugin_file))

    if not plugin_file.exists():
        return ""

    try:
        mod = _load_plugin_file(plugin_file)
        if not mod:
            return ""
        ctx_fn = getattr(mod, "CONTEXT", None)
        if ctx_fn:
            return ctx_fn({})
    except Exception:
        pass
    return ""


def execute_company_profile(company_id: str, specialist_id: str | None = None) -> str:
    """Executa o perfil de uma empresa, gerando o contexto do specialist selecionado.

    Se specialist_id for fornecido, gera o contexto daquele sub-agente especifico
    da empresa, incluindo:
      - O contexto geral da empresa (COMPANY_CONTEXT se existir)
      - O role/prompt do sub-agente
      - Os contexts dos specialists reutilizados pelo sub-agente

    Se specialist_id for None, retorna o contexto geral da empresa com lista
    de todos os sub-agentes disponiveis.

    Retorna o contexto pronto para injetar no CLAUDE.md.
    """
    _ensure_companies_dir()
    company_file = COMPANIES_DIR / f"{company_id}.py"

    if not company_file.exists() and (MYC_COMPANIES / f"{company_id}.py").exists():
        shutil.copy2(str(MYC_COMPANIES / f"{company_id}.py"), str(company_file))

    if not company_file.exists():
        console.print(f"[red]Empresa '{company_id}' nao encontrada.[/red]")
        return ""

    try:
        mod = _load_plugin_file(company_file)
        if not mod:
            return ""

        company_name = getattr(mod, "NAME", company_id)
        specialists = getattr(mod, "SPECIALISTS", [])

        # Contexto geral da empresa
        parts = []
        company_ctx_fn = getattr(mod, "COMPANY_CONTEXT", None)
        if company_ctx_fn:
            parts.append(company_ctx_fn())

        if specialist_id is None:
            # Lista todos os sub-agentes
            lines = [f"Especialistas disponiveis na empresa '{company_name}':\n"]
            for s in specialists:
                lines.append(f"  - **{s['name']}** (`{s['id']}`): {s.get('role', '')[:120]}...")
            lines.append("\nUse `myc agent launch-company <empresa> <sub-agente>` para lancar um especialista.")
            parts.append("\n".join(lines))
        else:
            # Encontra o sub-agente especifico
            target = None
            for s in specialists:
                if s["id"] == specialist_id:
                    target = s
                    break

            if target is None:
                ids = [s["id"] for s in specialists]
                console.print(f"[red]Sub-agente '{specialist_id}' nao encontrado na empresa '{company_id}'. Disponiveis: {', '.join(ids)}[/red]")
                return ""

            # Monta contexto do sub-agente
            sub_parts = []
            sub_parts.append(f"Voce e '{target['name']}' na empresa '{company_name}'.")
            sub_parts.append(target.get("role", ""))

            # Adiciona contexto extra do sub-agente se existir
            if target.get("context"):
                sub_parts.append(target["context"])

            # Reutiliza especialistas do outro plugin (specialists)
            if target.get("specialists"):
                sub_parts.append("\n---\nVoce tambem tem acesso aos seguintes conhecimentos especializados:\n")
                for sp_id in target["specialists"]:
                    ctx = _resolve_specialist_context(sp_id)
                    if ctx:
                        sub_parts.append(ctx)

            parts.append("\n".join(sub_parts))

        return "\n\n".join(parts)

    except Exception as e:
        console.print(f"[red]Erro ao executar empresa '{company_id}': {e}[/red]")
        return ""


# ── Wizard de Criacao de Plugin ──────────────────────────────

def create_plugin_wizard() -> None:
    """Wizard para criar um arquivo de plugin basico (specialist)."""
    import questionary

    console.print("\n[bold cyan]Criar Plugin Specialist[/bold cyan]")

    name_id = questionary.text(
        "ID do plugin (ex: git_helper, notion_sync):",
        validate=lambda x: (len(x) > 0 and " " not in x) or "Sem espacos",
    ).ask()
    if not name_id:
        return

    display_name = questionary.text("Nome display:", default=name_id.replace("_", " ").title()).ask() or name_id
    description = questionary.text("Descricao:").ask() or ""

    # Tipo de plugin
    plugin_types = [
        ("Pre-launch: modifica perfil/env vars antes do agente iniciar", "pre_launch"),
        ("Context: injecta texto extra no CLAUDE.md", "context"),
        ("Post-launch: acao apos agente iniciar (background)", "post_launch"),
        ("Todos os hooks", "full"),
    ]
    ptype = questionary.select(
        "Tipo do plugin:",
        choices=[questionary.Choice(label, value=v) for label, v in plugin_types],
    ).ask()

    if ptype == "pre_launch":
        body = questionary.text(
            "Codigo do hook PRE_LAUNCH(profile). profile e dict.\nEx: print(profile) para debug.",
            default="def PRE_LAUNCH(profile):\n    # Suas modificacoes no perfil aqui\n    pass\n",
        ).ask() or "    pass"
    elif ptype == "context":
        body = questionary.text(
            "Codigo do hook CONTEXT(profile). Retorna str com info extra.",
            default='def CONTEXT(profile):\n    return "Info do plugin"\n',
        ).ask() or '    return ""'
    elif ptype == "post_launch":
        body = questionary.text(
            "Codigo do hook POST_LAUNCH(profile). Executa em background.",
            default="def POST_LAUNCH(profile):\n    import subprocess\n    # subprocess.Popen(['echo', 'hello'])\n    pass\n",
        ).ask() or "    pass"
    else:
        body = questionary.text(
            "Cole o corpo do plugin aqui (FIM para terminar):",
            default="def PRE_LAUNCH(profile):\n    print('pre-launch:', profile)\n\ndef CONTEXT(profile):\n    return 'Plugin active'\n\n",
        ).ask() or "    pass"

    template = f'''"""
Plugin: {display_name}
Descricao: {description}
Instalacao: automatico em ~/.myc/agents/plugins/{name_id}.py
"""

NAME = "{display_name}"
DESCRIPTION = "{description}"


{body}
'''

    _ensure_plugins_dir()
    target = PLUGINS_DIR / f"{name_id}.py"
    target.write_text(template, encoding="utf-8")
    console.print(f"[green]Plugin criado em {target}[/green]")
    console.print(f"[dim]Vincule ao agente adicionando '{name_id}' na lista 'plugins' do perfil.[/dim]")

    # Pergunta se quer vincular a um agente
    from myc.agent import _load_agents, _save_agents
    agents = _load_agents()
    if agents:
        agent_choices = [questionary.Choice(a, value=a) for a in agents]
        chosen = questionary.select("Vincular a qual agente?", choices=agent_choices).ask()
        if chosen:
            profile = agents[chosen]
            plugins = profile.setdefault("plugins", [])
            if name_id not in plugins:
                plugins.append(name_id)
                _save_agents(agents)
                console.print(f"[green]Plugin vinculado ao agente '{chosen}'.[/green]")


def create_company_wizard() -> None:
    """Wizard para criar um plugin de empresa com sub-agentes especialistas."""
    import questionary

    console.print("\n[bold cyan]Criar Plugin Empresa[/bold cyan]")

    name_id = questionary.text(
        "ID da empresa (ex: minha_agencia, minha_dev_house):",
        validate=lambda x: (len(x) > 0 and " " not in x) or "Sem espacos",
    ).ask()
    if not name_id:
        return

    display_name = questionary.text("Nome da empresa:", default=name_id.replace("_", " ").title()).ask() or name_id
    description = questionary.text("Descricao da empresa:").ask() or ""

    company_context = questionary.text(
        "Contexto geral da empresa (opcional, sera o prompt base para todos):",
        default="",
    ).ask() or ""

    # Coletar sub-agentes
    specialists = []
    console.print("\n[cyan]Agora adicione os sub-agentes especialistas da empresa.[/cyan]")

    while True:
        console.print(f"\n[bold]Sub-agente #{len(specialists) + 1}[/bold]")

        sub_id = questionary.text(
            "ID do sub-agente (ex: copywriter_social, dev_backend):",
            validate=lambda x: (len(x) > 0 and " " not in x) or "Sem espacos",
        ).ask()
        if not sub_id:
            break

        sub_name = questionary.text("Nome do sub-agente:", default=sub_id.replace("_", " ").title()).ask() or sub_id
        sub_role = questionary.text(
            "Papel/descricao detalhada (prompt base do sub-agente):",
            default="",
        ).ask() or ""

        # Specialists que reutiliza
        available_specialists = list_plugins()
        if available_specialists:
            console.print("\n[dim]Selecione specialists existentes que este sub-agente reutiliza (opcional):[/dim]")
            spec_choices = [
                questionary.Choice(f"{s['name']} ({s['id']})", value=s["id"])
                for s in available_specialists
            ]
            reused = questionary.checkbox(
                "Especialistas reutilizados:",
                choices=spec_choices,
            ).ask() or []
        else:
            reused = []

        specialists.append({
            "id": sub_id,
            "name": sub_name,
            "role": sub_role,
            "specialists": reused,
        })

        more = questionary.confirm("Adicionar outro sub-agente?", default=False).ask()
        if not more:
            break

    if not specialists:
        console.print("[yellow]Nenhum sub-agente adicionado. Criando empresa vazia.[/yellow]")

    # Gera o arquivo
    import json

    # Gera COMPANY_CONTEXT
    ctx_block = ""
    if company_context:
        ctx_block = f'''
def COMPANY_CONTEXT():
    return """{company_context}"""
'''

    template = f'''"""
Empresa: {display_name}
Descricao: {description}
Especialistas: {len(specialists)} sub-agentes

Sub-agentes:
'''
    for s in specialists:
        template += f"  - {s['name']} ({s['id']}): {s['role'][:80]}\n"
    template += f'''"""

NAME = "{display_name}"
DESCRIPTION = "{description}"

SPECIALISTS = {json.dumps(specialists, indent=4, ensure_ascii=False)}
{ctx_block}
'''

    _ensure_companies_dir()
    target = COMPANIES_DIR / f"{name_id}.py"
    target.write_text(template, encoding="utf-8")
    console.print(f"[green]Empresa criada em {target} com {len(specialists)} sub-agentes.[/green]")
    console.print(f"[dim]Lance com: myc agent launch-company {name_id} <sub-agente-id>[/dim]")
