"""
Gerencia agentes de IA — multi-plataforma, com historico e integracao MYC.

Plataformas suportadas:
  - openclaude  : CLI generico via OpenAI/Anthropic API
  - claude_desktop : Claude Desktop (Anthropic)
  - cursor      : Cursor editor
  - vscode_copilot : VS Code + GitHub Copilot
  - codex       : OpenAI Codex CLI
  - custom      : Comando customizado definido pelo usuario
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()
AGENTS_DIR = Path.home() / ".myc" / "agents"
HISTORY_FILE = AGENTS_DIR / "history.json"


def _load_agents() -> dict:
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    idx_file = AGENTS_DIR / "agents.json"
    if idx_file.exists():
        try:
            return json.loads(idx_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_agents(data: dict) -> None:
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    idx_file = AGENTS_DIR / "agents.json"
    idx_file.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _load_history() -> list:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_history(entries: list) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _record_history(agent_name: str, platform: str, cwd: str,
                    routine: str | None, status: str) -> None:
    entries = _load_history()
    entries.insert(0, {
        "agent": agent_name,
        "platform": platform,
        "cwd": cwd,
        "routine": routine,
        "status": status,
        "timestamp": datetime.now().isoformat(),
    })
    # Mantém no maximo 500 entradas
    _save_history(entries[:500])



PLATFORM_COMMANDS = {
    "openclaude": "openclaude",
    "claude_desktop": "claude-desktop",       # nao usado diretamente
    "cursor": "cursor",
    "vscode_copilot": "code",
    "codex": "codex",
}


KNOWN_NPM_PATHS = [
    str(Path.home() / "AppData" / "Roaming" / "npm"),
    str(Path.home() / "bin"),
    "/usr/local/bin",
    str(Path.home() / ".npm-global/bin"),
]


def _find_command(name: str, extra_paths: list[str] | None = None) -> str | None:
    search_paths = os.environ.get("PATH", "").split(os.pathsep) + KNOWN_NPM_PATHS
    if extra_paths:
        search_paths.extend(extra_paths)
    for path in search_paths:
        candidate = Path(path) / name
        if candidate.exists():
            return str(candidate)
        for ext in (".cmd", ".bat", ".exe"):
            c = candidate.with_suffix(ext)
            if c.exists():
                return str(c)
    return None


def _find_binary(platform: str) -> str | None:
    """Retorna o caminho do binario da plataforma."""
    cmd_name = PLATFORM_COMMANDS.get(platform)
    if not cmd_name:
        return None
    return _find_command(cmd_name)



def create_agent_wizard() -> None:
    """Wizard interativo para criar perfil de agente."""
    import questionary

    console.print("\n[bold cyan]Criar Novo Agente de IA[/bold cyan]")
    console.print("[dim]Configure um agente para integrar com suas rotinas MYC.[/dim]\n")

    # Nome
    name = questionary.text(
        "Nome do agente (ex: dev, estudo, pesquisa):",
        validate=lambda x: (len(x) > 0 and " " not in x) or "Nome sem espacos",
    ).ask()
    if not name:
        return

    # Plataforma
    platforms = [
        questionary.Choice("OpenClaude (CLI, qualquer modelo via OpenAI API)", value="openclaude"),
        questionary.Choice("Cursor (editor de codigo com IA)", value="cursor"),
        questionary.Choice("VS Code + GitHub Copilot", value="vscode_copilot"),
        questionary.Choice("OpenAI Codex CLI", value="codex"),
        questionary.Choice("Comando customizado", value="custom"),
    ]
    platform = questionary.select("Plataforma do agente:", choices=platforms).ask()
    if not platform:
        return

    env_vars: dict = {}
    custom_cmd: str | None = None

    # ── Configuracao por plataforma ───

    if platform == "openclaude":
        env_vars = _wizard_env_openai_or()

    elif platform == "cursor":
        console.print("[dim]Cursor usa conta do Cursor. Sem variaveis obrigatorias.[/dim]")

    elif platform == "vscode_copilot":
        console.print("[dim]Copilot usa autenticacao do GitHub. Sem variaveis obrigatorias.[/dim]")

    elif platform == "codex":
        api_key = questionary.password("OPENAI_API_KEY:").ask()
        if api_key:
            env_vars["OPENAI_API_KEY"] = api_key

    elif platform == "custom":
        console.print("[yellow]Informe o comando completo para lancar seu agente.[/yellow]")
        custom_cmd = questionary.text(
            "Comando (ex: claude, gemini, ...):",
            validate=lambda x: len(x) > 0 or "Comando obrigatorio",
        ).ask()
        if not custom_cmd:
            return
        # Variaveis extras opcionais
        while questionary.confirm("Adicionar variavel de ambiente?", default=False).ask():
            var_name = questionary.text("Nome da variavel:").ask()
            if var_name:
                var_value = questionary.password(f"Valor para {var_name}:").ask()
                if var_value:
                    env_vars[var_name.strip()] = var_value
            more = questionary.confirm("Outra variavel?", default=False).ask()
            if not more:
                break

    # Diretorio de trabalho
    cwd = questionary.text(
        "Diretorio de trabalho (ENTER = atual):",
        default="",
    ).ask() or None

    # Instrucoes iniciais
    console.print("\n[dim]Instrucoes/contexto inicial para o agente (multi-line).[/dim]")
    console.print("[dim]Deixe vazio para pular. Digite 'FIM' sozinho na linha para terminar.[/dim]")

    instr_lines: list[str] = []
    while True:
        line = questionary.text(
            "" if not instr_lines else "Proxima linha (FIM = terminar):",
            default="",
        ).ask()
        if line is None:
            break
        if line.strip() == "FIM" and instr_lines:
            break
        if line == "" and not instr_lines:
            break
        instr_lines.append(line)

    initial_context = "\n".join(instr_lines).strip()

    from myc.config import load_config

    config = load_config()
    commands = config.get("commands", {})
    if commands:
        console.print("\n[dim]Vincule rotinas MYC a este agente (opcional).[/dim]")
        routine_choices = []
        for grp, grp_data in commands.items():
            for sub in grp_data.get("subcommands", {}):
                routine_choices.append(
                    questionary.Choice(f"{grp} / {sub}", value=f"{grp}:{sub}")
                )
        if routine_choices:
            linked_routines = questionary.checkbox(
                "Rotinas vinculadas (ENTER = pronto):",
                choices=routine_choices,
            ).ask() or []
        else:
            linked_routines = []
    else:
        linked_routines = []

    # Role do agente (tipo de trabalho que faz)
    role_choices = [
        questionary.Choice("Desenvolvedor (código, APIs, apps)", value="dev"),
        questionary.Choice("Designer/Artista (UI, arte visual, gráficos)", value="artist"),
        questionary.Choice("Escritor/Redator (textos, copy, conteúdo)", value="writer"),
        questionary.Choice("Pesquisador/Analista (dados, OSINT, relatórios)", value="researcher"),
        questionary.Choice("Professor/Educador (aulas, explicações)", value="educator"),
        questionary.Choice("Músico/Compositor (áudio, música, som)", value="musician"),
        questionary.Choice("Consultor de Negócios (estratégia, vendas)", value="business"),
        questionary.Choice("Generalista (todos os tipos)", value="generalist"),
    ]
    role = questionary.select("Papel principal do agente:", choices=role_choices).ask() or "generalist"

    # Plugins que este agente trata
    import json
    from myc.agent_plugins import list_plugins
    available_plugins = listPlugins()
    if available_plugins:
        console.print("\nSelecione quais plugins este agente vai tratar (ENTER = todos):")
        plugin_choices = [
            questionary.Choice(f"{p['name']} ({p['id']})", value=p["id"])
            for p in available_plugins
        ]
        plugin_filter = questionary.checkbox(
            "Filtro de plugins:",
            choices=plugin_choices,
        ).ask() or []
    else:
        plugin_filter = []

    # Agentes que este pode chamar
    agents = _load_agents()
    if agents:
        console.print("\nSelecione outros agentes que este pode chamar (ENTER = nenhum):")
        agent_call_choices = [
            questionary.Choice(n, value=n)
            for n in agents
        ]
        callable_agents = questionary.checkbox(
            "Agentes chamáveis:",
            choices=agent_call_choices,
        ).ask() or []
    else:
        callable_agents = []

    agents = _load_agents()
    profile = {
        "name": name,
        "platform": platform,
        "env": env_vars,
        "cwd": cwd,
        "initial_context": initial_context,
        "custom_command": custom_cmd,
        "linked_routines": linked_routines,
        "role": role,
        "plugin_filter": plugin_filter,
        "callable_agents": callable_agents,
        "created_at": datetime.now().isoformat(),
    }
    agents[name] = profile
    _save_agents(agents)

    # Feedback
    console.print("\n[bold green]Agente criado com sucesso![/bold green]")
    console.print(f"  Nome:       [cyan]{name}[/cyan]")
    console.print(f"  Plataforma: [yellow]{platform}[/yellow]")
    if linked_routines:
        console.print(f"  Rotinas:    {[r for r in linked_routines]}")

    launch = questionary.confirm("Lancar agora?", default=True).ask()
    if launch:
        launch_agent(name)


def _wizard_env_openai_or() -> dict:
    """Wizard para provedores compatíveis com OpenAI API."""
    import questionary

    providers = [
        ("OpenAI", "openai"),
        ("Ollama (local)", "ollama"),
        ("OpenRouter (multi-modelo)", "openrouter"),
        ("Gemini / Google AI", "gemini"),
        ("Outro endpoint custom", "custom"),
    ]
    prov_display, prov_value = questionary.select(
        "Provedor da API:",
        choices=[questionary.Choice(d, value=v) for d, v in providers],
    ).ask() or ("", "")

    if not prov_value:
        return {}

    env = {"CLAUDE_CODE_USE_OPENAI": "1"}

    if prov_value == "openai":
        env["OPENAI_API_KEY"] = questionary.password("OPENAI_API_KEY:").ask() or ""
        env["OPENAI_MODEL"] = questionary.text("Modelo (padrao: gpt-4o):", default="gpt-4o").ask() or "gpt-4o"
        base = questionary.text("OPENAI_BASE_URL (vazio = padrao):", default="").ask()
        if base:
            env["OPENAI_BASE_URL"] = base

    elif prov_value == "ollama":
        host = questionary.text("URL do Ollama:", default="http://localhost:11434").ask()
        env["OPENAI_BASE_URL"] = host.rstrip("/") + "/v1"
        env["OPENAI_API_KEY"] = "ollama"
        env["OPENAI_MODEL"] = questionary.text("Modelo:", default="llama3").ask() or "llama3"

    elif prov_value == "openrouter":
        env["OPENAI_API_KEY"] = questionary.password("OPENROUTER_API_KEY:").ask() or ""
        env["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"
        env["OPENAI_MODEL"] = questionary.text("Modelo (ex: openai/gpt-4o):").ask() or ""

    elif prov_value == "gemini":
        env["OPENAI_API_KEY"] = questionary.password("GEMINI_API_KEY:").ask() or ""
        env["OPENAI_BASE_URL"] = "https://generativelanguage.googleapis.com/v1beta/openai"
        env["OPENAI_MODEL"] = questionary.text("Modelo (ex: gemini-2.5-pro):", default="gemini-2.5-pro").ask() or "gemini-2.5-pro"

    elif prov_value == "custom":
        env["OPENAI_API_KEY"] = questionary.password("API_KEY:").ask() or ""
        env["OPENAI_BASE_URL"] = questionary.text("Base URL:").ask() or ""
        env["OPENAI_MODEL"] = questionary.text("Modelo:").ask() or ""

    return env



def list_agents() -> None:
    """Lista todos os agentes salvos."""
    from rich.table import Table

    agents = _load_agents()
    if not agents:
        console.print("[yellow]Nenhum agente configurado.[/yellow]")
        console.print("Use [cyan]myc agent add[/cyan] para criar um.")
        return

    table = Table(title="Agentes Configurados", show_lines=True)
    table.add_column("Nome", style="cyan")
    table.add_column("Plataforma", style="yellow")
    table.add_column("Rotinas", style="green")
    table.add_column("CWD", style="dim")

    for name, profile in agents.items():
        routines = ", ".join(profile.get("linked_routines", [])) or "-"
        cwd = profile.get("cwd") or "-"
        table.add_row(name, profile.get("platform", "?"), routines, cwd)

    console.print(table)



def delete_agent(name: str) -> None:
    """Remove um agente."""
    import questionary

    agents = _load_agents()
    if name not in agents:
        console.print(f"[red]Agente '{name}' nao encontrado.[/red]")
        return

    if questionary.confirm(f"Remover agente '{name}'?", default=False).ask():
        del agents[name]
        _save_agents(agents)
        console.print(f"[green]Agente '{name}' removido.[/green]")



def _write_claude_md(work_dir: Path, agent_name: str,
                     context: str, myc_tasks: str | None = None) -> bool:
    """Gera/clausula CLAUDE.md com contexto e tarefas MYC."""
    marker = f"# Agent: {agent_name}"
    target: str = marker
    if myc_tasks:
        target += "\n\n## MYC Tasks\n\n" + myc_tasks
    body = context + "\n" + target if context else target

    md_path = work_dir / "CLAUDE.md"
    if md_path.exists():
        existing = md_path.read_text(encoding="utf-8")
        if marker in existing:
            return False  # ja existe contexto deste agente
        # Backup
        md_path.with_suffix(".md.bak").write_text(existing, encoding="utf-8")
        md_path.write_text(existing + "\n\n---\n\n" + body, encoding="utf-8")
    else:
        md_path.write_text(body, encoding="utf-8")
    return True


def _summarize_myc_routine(group: str | None = None,
                            subcommand: str | None = None) -> str:
    """Gera resumo legivel das rotinas MYC para injetar como contexto."""
    from myc.config import load_config
    from myc.runner import DAYS_DISPLAY

    config = load_config()
    commands = config.get("commands", {})
    if not commands:
        return ""

    lines = ["## MYC Routines (context)"]
    for grp, grp_data in commands.items():
        if group and grp != group:
            continue
        subs = grp_data.get("subcommands", {})
        if not subs:
            continue
        lines.append(f"\n### group: {grp}")
        for sub_name, sub_data in subs.items():
            if subcommand and sub_name != subcommand:
                continue
            days = sub_data.get("days", [])
            acts = sub_data.get("actions", [])
            day_str = ", ".join(DAYS_DISPLAY.get(d, d) for d in days) if days else "todos os dias"
            lines.append(f"  - {sub_name}: {sub_data.get('description', '')} | dias: {day_str} | {len(acts)} acoes")
    return "\n".join(lines)


def launch_agent(name: str, cwd: str | None = None,
                 group: str | None = None,
                 subcommand: str | None = None) -> int:
    """Lanca um agente com suas configuracoes.

    Returns:
        Codigo de saida (0 = sucesso).
    """
    agents = _load_agents()
    if name not in agents:
        console.print(f"[red]Agente '{name}' nao encontrado.[/red]")
        return 1

    profile = agents[name]
    platform = profile.get("platform", "openclaude")
    env_vars: dict = profile.get("env", {})
    custom_cmd: str | None = profile.get("custom_command")
    agent_cwd = cwd or profile.get("cwd")
    context = profile.get("initial_context", "")

    work_dir = Path(agent_cwd) if agent_cwd else Path.cwd()
    if not work_dir.exists() or not work_dir.is_dir():
        console.print(f"[red]Diretorio invalido: {work_dir}[/red]")
        return 1

    # Contexto MYC
    myc_tasks = _summarize_myc_routine(group=group, subcommand=subcommand)

    # Injeta CLAUDE.md para openclaude, codex
    if platform in ("openclaude", "codex") and (context or myc_tasks):
        wrote = _write_claude_md(work_dir, name, context, myc_tasks)
        if wrote:
            console.print(f"[green]CLAUDE.md injetado em {work_dir}[/green]")
        else:
            console.print(f"[dim]CLAUDE.md ja continha contexto deste agente.[/dim]")

    # Executa plugins pre-launch e coleta contexto extra
    from myc.agent_plugins import execute_plugins
    plugin_context = execute_plugins(profile, "PRE_LAUNCH")

    # Se plugins geraram contexto, adiciona ao CLAUDE.md
    if plugin_context and platform in ("openclaude", "codex"):
        md_path = work_dir / "CLAUDE.md"
        extra_section = f"\n\n---\n\n## Agent Plugins\n\n{plugin_context}"
        if md_path.exists():
            if "## Agent Plugins" not in md_path.read_text(encoding="utf-8"):
                md_path.write_text(md_path.read_text(encoding="utf-8") + extra_section, encoding="utf-8")

    # Monta o comando
    env = os.environ.copy()
    env.update(env_vars)

    if plat_cmd := _build_launch_cmd(platform, custom_cmd):
        cmd, shell = plat_cmd
    else:
        console.print(f"[red]Plataforma '{platform}' nao suportada ou binario nao encontrado.[/red]")
        _record_history(name, platform, str(work_dir), group, "failed: no binary")
        return 1

    # Verifica se o binario existe
    bin_check = _find_binary(platform) if platform != "custom" else _find_custom_binary(custom_cmd)
    if platform != "custom" and not bin_check:
        console.print(f"[red]Binario de '{platform}' nao encontrado no PATH.[/red]")
        _record_history(name, platform, str(work_dir), group, "failed: binary not found")
        return 1

    console.print(f"\n[bold cyan]Lancando agente '{name}' ([yellow]{platform}[/yellow])...[/bold cyan]")
    console.print(f"  Diretorio: [dim]{work_dir}[/dim]")

    try:
        process = subprocess.Popen(
            cmd,
            env=env,
            cwd=str(work_dir),
            shell=shell,
        )
        rc = process.wait()
        status = "ok" if rc == 0 else f"exit_{rc}"
        routine_ref = f"{group}:{subcommand}" if group else None
        _record_history(name, platform, str(work_dir), routine_ref, status)
        return rc

    except FileNotFoundError:
        console.print(f"[red]Comando nao encontrado: {cmd[0]}[/red]")
        _record_history(name, platform, str(work_dir), None, "failed: FileNotFoundError")
        return 1
    except KeyboardInterrupt:
        console.print("\n[yellow]Agente interrompido.[/yellow]")
        process.terminate()
        try:
            process.wait(timeout=5)
        except Exception:
            process.kill()
        _record_history(name, platform, str(work_dir), None, "interrupted")
        return 130


def _build_launch_cmd(platform: str,
                       custom_cmd: str | None) -> tuple[list, bool] | None:
    """Retorna (lista de argumentos, shell_bool) ou None."""
    if platform == "openclaude":
        bin_path = _find_binary(platform)
        if bin_path:
            use_shell = bin_path.endswith((".cmd", ".bat"))
            return ([bin_path], use_shell)
        return (["openclaude"], True)
    if platform == "cursor":
        bin_path = _find_binary(platform)
        return ([bin_path if bin_path else "cursor", "."], False)
    if platform == "vscode_copilot":
        bin_path = _find_binary(platform)
        return ([bin_path if bin_path else "code", "."], False)
    if platform == "codex":
        bin_path = _find_binary(platform)
        if bin_path:
            use_shell = bin_path.endswith((".cmd", ".bat"))
            return ([bin_path], use_shell)
        return (["codex"], True)
    if platform == "custom" and custom_cmd:
        return (custom_cmd, True)
    return None


def _find_c_binary(cmd_str: str) -> str | None:
    """Tenta resolver o primeiro token de um comando custom."""
    if not cmd_str:
        return None
    token = cmd_str.strip().split()[0]
    return _find_command(token)


def launch_with_myc_tasks(agent_name: str,
                          group: str | None = None,
                          subcommand: str | None = None) -> int:
    """Alias para launch_agent com contexto de rotinas MYC."""
    return launch_agent(agent_name, group=group, subcommand=subcommand)



def show_agent_history(agent_filter: str | None = None,
                       limit: int = 20) -> None:
    """Mostra historico de uso dos agentes."""
    from rich.table import Table

    entries = _load_history()

    if agent_filter:
        entries = [e for e in entries if e.get("agent") == agent_filter]

    if not entries:
        console.print("[yellow]Nenhum registro no historico.[/yellow]")
        return

    entries = entries[:limit]

    table = Table(title="Historico de Agentes", show_lines=True)
    table.add_column("Data/Hora", style="dim")
    table.add_column("Agente", style="cyan")
    table.add_column("Plataforma", style="yellow")
    table.add_column("Dir", style="dim", max_width=40)
    table.add_column("Rotina", style="green")
    table.add_column("Status", style="magenta")

    for e in entries:
        dt = e.get("timestamp", "?")[:19]
        table.add_row(
            dt,
            e.get("agent", "?"),
            e.get("platform", "?"),
            e.get("cwd", "-"),
            e.get("routine") or "-",
            e.get("status", "?"),
        )

    console.print(table)

    # Resumo rapido
    agents_seen = set(e["agent"] for e in entries)
    console.print(f"\n[dim]{len(entries)} entradas | {len(agents_seen)} agente(s): {', '.join(sorted(agents_seen))}[/dim]")


# ── Roteamento de Plugins para Agentes ─────────────────────

ROLE_TO_BUNDLES = {
    "dev": ["fullstack", "software_engineering", "computer_engineering", "data_engineering"],
    "artist": ["gamedesign", "visao_computacional"],
    "writer": ["jornalismo", "advocacia"],
    "researcher": ["osint", "bugbounty", "seguranca_web"],
    "educator": ["professor"],
    "musician": [],
    "business": ["vendas", "ideias", "marketing"],
    "generalist": list(BUNDLES.keys()) if "BUNDLES" in dir() else [],
}


def auto_assign_plugins(agent_name: str) -> None:
    """Auto-vincula plugins a um agente baseado no seu role."""
    agents = _load_agents()
    if agent_name not in agents:
        console.print(f"[red]Agente '{agent_name}' nao encontrado.[/red]")
        return

    profile = agents[agent_name]
    role = profile.get("role", "generalist")

    # Mapeia role para bundles
    if role == "dev":
        bundle_ids = ["fullstack", "software_engineering", "computer_engineering", "data_engineering"]
    elif role == "artist":
        bundle_ids = ["gamedesign"]
    elif role == "writer":
        bundle_ids = ["jornalismo", "advocacia"]
    elif role == "researcher":
        bundle_ids = ["osint", "bugbounty", "seguranca_web"]
    elif role == "educator":
        bundle_ids = ["professor"]
    elif role == "musician":
        bundle_ids = []
    elif role == "business":
        bundle_ids = ["vendas", "ideias", "marketing"]
    else:
        bundle_ids = list(BUNDLES.keys())

    from myc.plugin_manager import BUNDLES

    all_plugins = []
    for bid in bundle_ids:
        if bid in BUNDLES:
            all_plugins.extend(BUNDLES[bid]["plugins"])

    existing = set(profile.get("plugins", []))
    new_plugins = [p for p in all_plugins if p not in existing]
    profile.setdefault("plugins", []).extend(new_plugins)
    _save_agents(agents)

    console.print(f"[green]{len(new_plugins)} plugins auto-atribuidos ao agente '{agent_name}' (role: {role})[/green]")


def link_plugin_to_agent(agent_name: str, plugin_id: str) -> None:
    """Vincula explicitamente um plugin a um agente."""
    agents = _load_agents()
    if agent_name not in agents:
        console.print(f"[red]Agente '{agent_name}' nao encontrado.[/red]")
        return

    profile = agents[agent_name]
    plugins = profile.setdefault("plugins", [])
    if plugin_id in plugins:
        console.print(f"[dim]Plugin '{plugin_id}' ja vinculado a '{agent_name}'.[/dim]")
        return

    plugins.append(plugin_id)
    # Registra qual plugin vai para qual agente
    agent_plugin_map = profile.setdefault("agent_plugin_map", {})
    agent_plugin_map[plugin_id] = agent_name

    _save_agents(agents)
    console.print(f"[green]Plugin '{plugin_id}' vinculado ao agente '{agent_name}'.[/green]")


def link_agent_to_agent(agent_name: str, target_agent: str, bidirectional: bool = False) -> None:
    """Permite que um agente chame outro agente."""
    agents = _load_agents()
    if agent_name not in agents:
        console.print(f"[red]Agente '{agent_name}' nao encontrado.[/red]")
        return
    if target_agent not in agents:
        console.print(f"[red]Agente '{target_agent}' nao encontrado.[/red]")
        return

    # Vincula双向
    callable_list = agents[agent_name].setdefault("callable_agents", [])
    if target_agent not in callable_list:
        callable_list.append(target_agent)

    if bidirectional:
        rev_list = agents[target_agent].setdefault("callable_agents", [])
        if agent_name not in rev_list:
            rev_list.append(agent_name)

    _save_agents(agents)
    console.print(f"[green]Agente '{agent_name}' pode agora chamar '{target_agent}'.[/green]")


def unlink_plugin_from_agent(agent_name: str, plugin_id: str) -> None:
    """Desvincula um plugin de um agente."""
    agents = _load_agents()
    if agent_name not in agents:
        console.print(f"[red]Agente '{agent_name}' nao encontrado.[/red]")
        return

    profile = agents[agent_name]
    plugins = profile.get("plugins", [])
    if plugin_id in plugins:
        plugins.remove(plugin_id)
        _save_agents(agents)
        console.print(f"[green]Plugin '{plugin_id}' desvinculado de '{agent_name}'.[/green]")
    else:
        console.print(f"[yellow]Plugin '{plugin_id}' nao estava vinculado.[/yellow]")


def unlink_agent_from_agent(agent_name: str, target_agent: str) -> None:
    """Remove a capacidade de um agente chamar outro."""
    agents = _load_agents()
    if agent_name not in agents:
        console.print(f"[red]Agente '{agent_name}' nao encontrado.[/red]")
        return

    callable_list = agents[agent_name].get("callable_agents", [])
    if target_agent in callable_list:
        callable_list.remove(target_agent)
        _save_agents(agents)
        console.print(f"[green]Agente '{agent_name}' nao pode mais chamar '{target_agent}'.[/green]")
    else:
        console.print(f"[yellow]Agente '{agent_name}' nao chamava '{target_agent}'.[/yellow]")


def call_agent(agent_name: str, query: str, called_by: str | None = None) -> int:
    """Lanca um agente com uma query, opcionalmente chamado por outro agente.

    Isso permite que agentes chamem outros agentes. Por exemplo:
    - Um agente 'dev' chama o agente 'artist' para criar UI
    - Um agente 'researcher' chama o agente 'writer' para escrever relatorio
    """
    agents = _load_agents()
    if agent_name not in agents:
        console.print(f"[red]Agente '{agent_name}' nao encontrado.[/red]")
        return 1

    # Verifica se caller tem permissao
    if called_by:
        caller_profile = agents.get(called_by, {})
        caller_can_call = caller_profile.get("callable_agents", [])
        if agent_name not in caller_can_call:
            console.print(f"[yellow]Agente '{called_by}' nao tem permissao para chamar '{agent_name}'.[/yellow]")
            console.print("[dim]Use 'myc agent link-agent <caller> <target>' para liberar.[/dim]")
            # Continua mesmo assim por enquanto, mas loga

    # Injeta contexto de origem
    context_prefix = ""
    if called_by:
        context_prefix = f"[Chamado pelo agente '{called_by}']\n\n"

    # Grava no CLAUDE.md como sempre
    profile = agents[agent_name]
    cwd = profile.get("cwd") or str(Path.cwd())
    work_dir = Path(cwd)
    md_path = work_dir / "CLAUDE.md"

    context = profile.get("initial_context", "")
    full_context = f"{context_prefix}{context}" if context_prefix else context

    if full_context or query:
        body = f"# Agent: {agent_name}\n\n{full_context}\n\n---\n\n## Tarefa\n\n{context_prefix}{query}"
        if md_path.exists():
            existing = md_path.read_text(encoding="utf-8")
            backup = existing
            md_path.write_text(body, encoding="utf-8")
        else:
            md_path.write_text(body, encoding="utf-8")
            backup = None

    console.print(f"\n[bold cyan]Chamando agente '{agent_name}'[/bold cyan]")
    if called_by:
        console.print(f"[dim]  Solicitado por: {called_by}[/dim]")

    rc = launch_agent(agent_name, cwd=cwd)
    # Restaura CLAUDE.md
    if backup is not None:
        md_path.write_text(backup, encoding="utf-8")
    elif md_path.exists() and body in md_path.read_text(encoding="utf-8"):
        md_path.unlink(missing_ok=True)

    return rc


def list_agents_detailed() -> None:
    """Lista agentes com detalhes: role, plugins, callable agents."""
    from rich.table import Table

    agents = _load_agents()
    if not agents:
        console.print("[yellow]Nenhum agente configurado.[/yellow]")
        return

    table = Table(title="Agentes Configurados", show_lines=True)
    table.add_column("Nome", style="cyan")
    table.add_column("Plataforma", style="yellow")
    table.add_column("Role", style="magenta")
    table.add_column("Plugins", style="green")
    table.add_column("Chamáveis", style="dim")

    for name, profile in agents.items():
        role = profile.get("role", "generalist")
        plugins = profile.get("plugins", [])
        callable_list = profile.get("callable_agents", [])
        plugin_str = ", ".join(plugins) if plugins else "-"
        callable_str = ", ".join(callable_list) if callable_list else "-"

        table.add_row(name, profile.get("platform", "?"), role, plugin_str, callable_str)

    console.print(table)
