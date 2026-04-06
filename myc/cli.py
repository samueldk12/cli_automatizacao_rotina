import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Garante UTF-8 no stdout/stderr no Windows antes de qualquer output rich/questionary
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import click
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from myc.agent import (
    create_agent_wizard,
    delete_agent,
    launch_agent,
    list_agents,
)
from myc.agent_plugins import (
    create_plugin_wizard,
    list_plugins as list_agent_plugins,
)
from myc.config import BIN_DIR, CONFIG_FILE, load_config, save_config
from myc.monitor import get_monitors
from myc.runner import DAYS_DISPLAY, DAYS_PT, find_browser, run_command
from myc.tui import navigate_tui, show_commands_table

# legacy_windows=False: força modo ANSI/VT100 no Windows 10/11
console = Console(legacy_windows=False)


# ─────────────────────────────────────────────
# Utilitários internos
# ─────────────────────────────────────────────

def _generate_wrapper(group_name: str) -> None:
    """Gera scripts .bat e .ps1 para o grupo no diretório bin."""
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    python_exe = sys.executable

    # CMD (.bat): set PYTHONUTF8=1 para evitar erros de encoding no terminal legado
    bat = BIN_DIR / f"{group_name}.bat"
    bat.write_text(
        f'@echo off\n'
        f'set PYTHONUTF8=1\n'
        f'if "%~1"=="" (\n'
        f'    "{python_exe}" -m myc tui --group {group_name}\n'
        f') else (\n'
        f'    "{python_exe}" -m myc run {group_name} %*\n'
        f')\n',
        encoding="utf-8",
    )

    # PowerShell (.ps1)
    ps1 = BIN_DIR / f"{group_name}.ps1"
    ps1.write_text(
        f'$env:PYTHONUTF8 = "1"\n'
        f'if ($args.Count -eq 0) {{\n'
        f'    & "{python_exe}" -m myc tui --group {group_name}\n'
        f'}} else {{\n'
        f'    & "{python_exe}" -m myc run {group_name} @args\n'
        f'}}\n',
        encoding="utf-8",
    )


def _find_openclaude_binary() -> Optional[str]:
    for path in os.environ.get("PATH", "").split(os.pathsep):
        for name in ("openclaude", "openclaude.cmd", "openclaude.exe"):
            candidate = Path(path) / name
            if candidate.exists():
                return str(candidate)
    return None


def _add_to_path_windows(directory: str) -> bool:
    """Adiciona diretório ao PATH do usuário no registro do Windows."""
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_ALL_ACCESS,
        )
        try:
            current_path, _ = winreg.QueryValueEx(key, "PATH")
        except FileNotFoundError:
            current_path = ""

        if directory.lower() not in current_path.lower():
            new_path = f"{current_path};{directory}" if current_path else directory
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"[OK] PATH atualizado: {directory}")
            print("Reinicie o terminal para o PATH ter efeito.")
        else:
            print(f"Ja esta no PATH: {directory}")

        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"[ERRO] Nao foi possivel atualizar PATH: {e}")
        return False


# ─────────────────────────────────────────────
# CLI principal
# ─────────────────────────────────────────────

@click.group()
def main() -> None:
    """MYC — Gerenciador de Comandos Personalizados\n
    Cadastre sites e apps e execute-os com um comando no terminal.
    """
    pass


# ─── run ─────────────────────────────────────

@main.command(name="run")
@click.argument("group")
@click.argument("rest", nargs=-1)
def run_cmd(group: str, rest: tuple) -> None:
    """Executa: myc run <grupo> [dia] <subcomando>

    \b
    Exemplos:
      myc run estudar visao-computacional
      myc run estudar segunda visao-computacional
    """
    config = load_config()
    commands = config.get("commands", {})

    if not rest:
        # Sem subcomando → TUI filtrada no grupo
        navigate_tui(group_filter=group)
        return

    # Detecta se o primeiro arg é um dia da semana
    if len(rest) >= 2 and rest[0] in DAYS_PT:
        day: Optional[str] = rest[0]
        subcommand = rest[1]
    else:
        day = None
        subcommand = rest[0]

    if not run_command(group, subcommand, day):
        console.print(
            f"[red]Comando não encontrado:[/red] [yellow]{group} {subcommand}[/yellow]"
        )
        # Sugere subcomandos disponíveis
        if group in commands:
            subs = list(commands[group].get("subcommands", {}).keys())
            if subs:
                console.print(f"[dim]Subcomandos disponíveis: {', '.join(subs)}[/dim]")
        sys.exit(1)


# ─── add ─────────────────────────────────────

@main.command(name="add")
def add_command() -> None:
    """Adiciona um novo comando interativamente."""
    config = load_config()
    commands = config.setdefault("commands", {})

    console.print(
        Panel(
            "[bold cyan]Adicionar Novo Comando[/bold cyan]\n"
            "[dim]Siga o assistente para configurar seu comando.[/dim]",
            border_style="cyan",
        )
    )

    # ── Grupo ────────────────────────────────
    existing_groups = list(commands.keys())
    if existing_groups:
        group_choices = [questionary.Choice(f"📁  {g}", value=g) for g in existing_groups]
        group_choices.append(questionary.Choice("➕  Criar novo grupo", value="__new__"))
        group_choice = questionary.select("Grupo:", choices=group_choices).ask()
    else:
        group_choice = "__new__"

    if group_choice is None:
        return

    if group_choice == "__new__":
        group_name = questionary.text(
            "Nome do grupo (sem espaços, ex: estudar):",
            validate=lambda x: (len(x) > 0 and " " not in x) or "Nome inválido",
        ).ask()
        if not group_name:
            return
        group_desc = questionary.text("Descrição do grupo (opcional):").ask() or ""
        commands[group_name] = {"description": group_desc, "subcommands": {}}
    else:
        group_name = group_choice

    group_data = commands[group_name]
    subcommands = group_data.setdefault("subcommands", {})

    # ── Subcomando ────────────────────────────
    sub_name = questionary.text(
        "Nome do subcomando (sem espaços, ex: visao-computacional):",
        validate=lambda x: (len(x) > 0 and " " not in x) or "Nome inválido",
    ).ask()
    if not sub_name:
        return

    sub_desc = questionary.text("Descrição do subcomando (opcional):").ask() or ""

    # ── Dias da semana ────────────────────────
    day_choices = [
        questionary.Choice(display, value=day) for day, display in DAYS_DISPLAY.items()
    ]
    selected_days = (
        questionary.checkbox(
            "Dias disponíveis (vazio = todos os dias):",
            choices=day_choices,
        ).ask()
        or []
    )

    # ── Ações ─────────────────────────────────
    actions = []
    monitors = get_monitors()
    monitor_choices = [
        questionary.Choice(f"Monitor {m.index + 1}  ({m.width}x{m.height})", value=m.index)
        for m in monitors
    ]

    console.print("\n[bold cyan]Configure as ações do comando:[/bold cyan]")
    console.print("[dim]Adicione URLs ou aplicativos que serão abertos ao executar o comando.[/dim]\n")

    while True:
        action_type = questionary.select(
            "Adicionar ação:",
            choices=[
                questionary.Choice("🌐  Abrir URL no navegador", value="browser"),
                questionary.Choice("💻  Abrir aplicativo", value="app"),
                questionary.Choice("✅  Concluir (sem mais ações)", value="done"),
            ],
        ).ask()

        if action_type is None or action_type == "done":
            break

        if action_type == "browser":
            url = questionary.text(
                "URL completa (ex: https://udemy.com/course/...):",
                validate=lambda x: len(x) > 0 or "URL obrigatória",
            ).ask()
            if not url:
                break

            monitor_idx = (
                questionary.select("Em qual monitor abrir?", choices=monitor_choices).ask()
                if len(monitors) > 1
                else 0
            )
            if monitor_idx is None:
                break

            new_window = questionary.confirm("Abrir em nova janela?", default=True).ask()

            browser_choice = questionary.select(
                "Navegador:",
                choices=[
                    questionary.Choice("Google Chrome", value="chrome"),
                    questionary.Choice("Microsoft Edge", value="edge"),
                    questionary.Choice("Firefox", value="firefox"),
                ],
            ).ask() or "chrome"

            actions.append(
                {
                    "type": "browser",
                    "url": url,
                    "monitor": monitor_idx,
                    "new_window": new_window,
                    "browser": browser_choice,
                }
            )
            console.print(f"  [green]✓ URL adicionada:[/green] {url} → Monitor {monitor_idx + 1}")

        elif action_type == "app":
            app_path = questionary.text(
                "Caminho do executável (ex: C:\\Program Files\\...\\app.exe):",
                validate=lambda x: len(x) > 0 or "Caminho obrigatório",
            ).ask()
            if not app_path:
                break

            args_str = questionary.text(
                "Argumentos (separados por espaço, vazio = nenhum):"
            ).ask() or ""
            args = args_str.split() if args_str.strip() else []

            actions.append({"type": "app", "path": app_path, "args": args})
            console.print(f"  [green]✓ App adicionado:[/green] {app_path}")

        more = questionary.confirm("Adicionar mais uma ação?", default=bool(actions)).ask()
        if not more:
            break

    if not actions:
        console.print("[yellow]Nenhuma ação configurada. Comando salvo sem ações.[/yellow]")

    subcommands[sub_name] = {
        "description": sub_desc,
        "days": selected_days,
        "actions": actions,
    }

    save_config(config)
    _generate_wrapper(group_name)

    console.print(
        Panel(
            f"[bold green]✓ Comando criado com sucesso![/bold green]\n\n"
            f"  Grupo:      [cyan]{group_name}[/cyan]\n"
            f"  Subcomando: [yellow]{sub_name}[/yellow]\n"
            f"  Ações:      {len(actions)}\n\n"
            f"[bold]Como usar:[/bold]\n"
            f"  [cyan]{group_name} {sub_name}[/cyan]\n"
            f"  [cyan]{group_name} segunda {sub_name}[/cyan]  (com filtro de dia)",
            border_style="green",
        )
    )


# ─── list ─────────────────────────────────────

@main.command(name="list")
@click.option("--group", "-g", default=None, help="Filtrar por grupo")
def list_commands(group: Optional[str]) -> None:
    """Lista todos os comandos cadastrados."""
    config = load_config()
    commands = config.get("commands", {})

    if not commands:
        console.print("[yellow]Nenhum comando cadastrado.[/yellow]")
        console.print("Use [cyan]myc add[/cyan] para criar seu primeiro comando.")
        return

    if group:
        if group not in commands:
            console.print(f"[red]Grupo '{group}' não encontrado.[/red]")
            return
        commands = {group: commands[group]}

    show_commands_table(commands)


# ─── tui ─────────────────────────────────────

@main.command(name="tui")
@click.option("--group", "-g", default=None, help="Entrar direto em um grupo")
def tui_cmd(group: Optional[str]) -> None:
    """Abre a navegação visual interativa."""
    navigate_tui(group_filter=group)


# ─── delete ─────────────────────────────────

@main.command(name="delete")
@click.argument("group")
@click.argument("subcommand", required=False, default=None)
def delete_command(group: str, subcommand: Optional[str]) -> None:
    """Remove um comando ou grupo completo.

    \b
    Exemplos:
      myc delete estudar visao-computacional
      myc delete estudar
    """
    config = load_config()
    commands = config.get("commands", {})

    if group not in commands:
        console.print(f"[red]Grupo '{group}' não encontrado.[/red]")
        return

    if subcommand:
        subs = commands[group].get("subcommands", {})
        if subcommand not in subs:
            console.print(f"[red]Subcomando '{subcommand}' não encontrado.[/red]")
            return
        if questionary.confirm(f"Remover '{group} {subcommand}'?", default=False).ask():
            del subs[subcommand]
            save_config(config)
            console.print(f"[green]✓ Removido: {group} {subcommand}[/green]")
    else:
        n = len(commands[group].get("subcommands", {}))
        if questionary.confirm(
            f"Remover grupo '{group}' e seus {n} subcomando(s)?", default=False
        ).ask():
            del commands[group]
            save_config(config)
            # Remove wrapper scripts
            for ext in (".bat", ".ps1"):
                f = BIN_DIR / f"{group}{ext}"
                if f.exists():
                    f.unlink()
            console.print(f"[green]✓ Grupo '{group}' removido.[/green]")


# ─── edit ─────────────────────────────────────

@main.command(name="edit")
@click.argument("group")
@click.argument("subcommand")
def edit_command(group: str, subcommand: str) -> None:
    """Edita as ações de um comando existente.

    \b
    Exemplo:
      myc edit estudar visao-computacional
    """
    config = load_config()
    commands = config.get("commands", {})

    if group not in commands:
        console.print(f"[red]Grupo '{group}' não encontrado.[/red]")
        return

    subs = commands[group].get("subcommands", {})
    if subcommand not in subs:
        console.print(f"[red]Subcomando '{subcommand}' não encontrado.[/red]")
        return

    sub_data = subs[subcommand]
    console.print(
        Panel(
            f"Editando: [cyan]{group}[/cyan] / [yellow]{subcommand}[/yellow]\n"
            f"Descrição: {sub_data.get('description', '')}\n"
            f"Dias: {', '.join(sub_data.get('days', [])) or 'todos'}\n"
            f"Ações: {len(sub_data.get('actions', []))}",
            border_style="cyan",
        )
    )

    field = questionary.select(
        "O que deseja editar?",
        choices=[
            questionary.Choice("📝  Descrição", value="desc"),
            questionary.Choice("📅  Dias da semana", value="days"),
            questionary.Choice("🔁  Substituir todas as ações", value="actions"),
            questionary.Choice("❌  Cancelar", value="cancel"),
        ],
    ).ask()

    if field is None or field == "cancel":
        return

    if field == "desc":
        new_desc = questionary.text(
            "Nova descrição:", default=sub_data.get("description", "")
        ).ask()
        if new_desc is not None:
            sub_data["description"] = new_desc

    elif field == "days":
        day_choices = [
            questionary.Choice(display, value=day, checked=(day in sub_data.get("days", [])))
            for day, display in DAYS_DISPLAY.items()
        ]
        new_days = questionary.checkbox("Dias disponíveis:", choices=day_choices).ask() or []
        sub_data["days"] = new_days

    elif field == "actions":
        console.print("[yellow]As ações atuais serão substituídas.[/yellow]")
        if not questionary.confirm("Continuar?", default=False).ask():
            return

        # Reusa o wizard de ações do add
        actions: list = []
        monitors = get_monitors()
        monitor_choices = [
            questionary.Choice(f"Monitor {m.index + 1} ({m.width}x{m.height})", value=m.index)
            for m in monitors
        ]

        while True:
            action_type = questionary.select(
                "Adicionar ação:",
                choices=[
                    questionary.Choice("🌐  Abrir URL", value="browser"),
                    questionary.Choice("💻  Abrir app", value="app"),
                    questionary.Choice("✅  Concluir", value="done"),
                ],
            ).ask()

            if action_type is None or action_type == "done":
                break

            if action_type == "browser":
                url = questionary.text("URL:").ask()
                if not url:
                    break
                monitor_idx = (
                    questionary.select("Monitor:", choices=monitor_choices).ask()
                    if len(monitors) > 1
                    else 0
                )
                new_window = questionary.confirm("Nova janela?", default=True).ask()
                actions.append(
                    {"type": "browser", "url": url, "monitor": monitor_idx, "new_window": new_window, "browser": "chrome"}
                )
            elif action_type == "app":
                path = questionary.text("Caminho:").ask() or ""
                args_str = questionary.text("Argumentos:").ask() or ""
                actions.append({"type": "app", "path": path, "args": args_str.split()})

            if not questionary.confirm("Mais ações?", default=True).ask():
                break

        sub_data["actions"] = actions

    save_config(config)
    console.print("[green]✓ Comando atualizado.[/green]")


# ─── monitors ─────────────────────────────────

@main.command(name="monitors")
def show_monitors() -> None:
    """Lista os monitores detectados no sistema."""
    monitors = get_monitors()
    console.print("\n[bold]Monitores detectados:[/bold]\n")
    for m in monitors:
        tag = " [bold green](primário)[/bold green]" if m.is_primary else ""
        console.print(f"  [cyan]Monitor {m.index + 1}[/cyan]{tag}")
        console.print(f"    Resolução: {m.width}×{m.height}")
        console.print(f"    Posição:   ({m.x}, {m.y})")
        console.print(f"    Nome:      {m.name or '—'}\n")


# ─── setup ────────────────────────────────────

@main.command(name="setup")
@click.option("--auto", is_flag=True, help="Adiciona bin ao PATH automaticamente (Windows)")
def setup_cmd(auto: bool) -> None:
    """Configura o ambiente e gera scripts de atalho."""
    BIN_DIR.mkdir(parents=True, exist_ok=True)

    config = load_config()
    commands = config.get("commands", {})

    generated = 0
    for group_name in commands:
        _generate_wrapper(group_name)
        generated += 1

    console.print(
        Panel(
            f"[bold cyan]Configuração MYC[/bold cyan]\n\n"
            f"Diretório de scripts: [green]{BIN_DIR}[/green]\n"
            f"Config em:            [green]{CONFIG_FILE}[/green]\n"
            f"Scripts gerados:      [green]{generated}[/green]",
            border_style="cyan",
        )
    )

    if auto:
        _add_to_path_windows(str(BIN_DIR))
    else:
        console.print("\n[yellow]Para adicionar ao PATH automaticamente:[/yellow]")
        console.print("  [cyan]myc setup --auto[/cyan]\n")
        console.print("[yellow]Ou manualmente no PowerShell (como Admin):[/yellow]")
        console.print(
            f'  [dim][Environment]::SetEnvironmentVariable('
            f'"PATH", $env:PATH + ";{BIN_DIR}", "User")[/dim]'
        )


# ─── config ───────────────────────────────────

@main.command(name="config")
def config_cmd() -> None:
    """Altera configurações globais (caminho do Chrome, etc.)."""
    config = load_config()
    settings = config.setdefault("settings", {})

    field = questionary.select(
        "Configuração:",
        choices=[
            questionary.Choice("🌐  Caminho do Chrome", value="chrome_path"),
            questionary.Choice("❌  Cancelar", value="cancel"),
        ],
    ).ask()

    if not field or field == "cancel":
        return

    if field == "chrome_path":
        current = settings.get("chrome_path", "")
        detected = find_browser("chrome")
        new_val = questionary.text(
            f"Caminho do Chrome (detectado: {detected}):",
            default=current,
        ).ask()
        if new_val is not None:
            settings["chrome_path"] = new_val
            save_config(config)
            console.print("[green]✓ Configuração salva.[/green]")


@main.command(name="config-html")
@click.option("--port", "-p", default=8787, help="Porta do dashboard (default: 8787)")
def config_html_cmd(port: int) -> None:
    """Abre dashboard web local com todas as configuracoes.

    Mostra agentes, rotinas, plugins, historico e estatisticas
    em uma pagina HTML interativa.
    """
    from myc.html_dashboard import serve_dashboard
    serve_dashboard(port=port)


# ─── agent ────────────────────────────────

@main.group(name="agent")
def agent_cmd() -> None:
    """Gerencia agentes de IA e integra com rotinas MYC."""
    pass


@agent_cmd.command(name="add")
def agent_add() -> None:
    """Cria um novo perfil de agente de IA (wizard interativo)."""
    create_agent_wizard()


@agent_cmd.command(name="list")
def agent_list_cmd() -> None:
    """Lista todos os agentes configurados."""
    list_agents()


@agent_cmd.command(name="launch")
@click.argument("name")
@click.option("--cwd", default=None, help="Diretorio de trabalho do agente")
def agent_launch_cmd(name: str, cwd: Optional[str]) -> None:
    """Lanca um agente salvo no diretorio de trabalho."""
    rc = launch_agent(name, cwd=cwd)
    if rc != 0:
        sys.exit(rc)


@agent_cmd.command(name="delete")
@click.argument("name")
def agent_delete_cmd(name: str) -> None:
    """Remove um agente configurado."""
    delete_agent(name)


@agent_cmd.command(name="history")
@click.option("--agent", "-a", default=None, help="Filtrar por agente")
@click.option("--limit", "-n", default=20, help="Numero de entradas")
def agent_history_cmd(agent: Optional[str], limit: int) -> None:
    """Mostra historico de uso dos agentes."""
    from myc.agent import show_agent_history
    show_agent_history(agent_filter=agent, limit=limit)


@agent_cmd.command(name="plugins")
def agent_plugins_cmd() -> None:
    """Lista plugins disponiveis para agentes."""
    from rich.table import Table
    plugins = list_agent_plugins()
    if not plugins:
        console.print("[yellow]Nenhum plugin instalado.[/yellow]")
        console.print("Use [cyan]myc agent plugin-add[/cyan] para criar um.")
        return
    table = Table(title="Plugins de Agentes", show_lines=True)
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="yellow")
    table.add_column("Descricao", style="green")
    for p in plugins:
        table.add_row(p["id"], p["name"], p["description"])
    console.print(table)


@agent_cmd.command(name="plugin-add")
def agent_plugin_add_cmd() -> None:
    """Cria um novo plugin de agente (wizard)."""
    create_plugin_wizard()


@main.command(name="install")
@click.argument("target")
def install_cmd(target: str) -> None:
    """Instala e configura integracoes.

    \b
    Exemplos:
      myc install openclaude
    """
    if target == "openclaude":
        _install_openclaude()
    else:
        console.print(f"[red]Alvo desconhecido: {target}[/red]")
        console.print("[dim]Alvos disponiveis: openclaude[/dim]")


def _install_openclaude() -> None:
    import subprocess
    import questionary

    console.print(
        Panel(
            "[bold cyan]Instalacao do OpenClaude[/bold cyan]\n\n"
            "O OpenClaude permite usar IA via CLI — qualquer modelo "
            "(GPT, Claude, Gemini, Llama, Qwen).\n\n"
            "[dim]Modelo padrao: qwen/qwen3.6-plus:free (via OpenRouter)[/dim]",
            border_style="cyan",
        )
    )

    if not _find_openclaude_binary():
        if questionary.confirm(
            "Instalar OpenClaude agora? (requer npm)", default=True
        ).ask():
            console.print("\nInstalando OpenClaude via npm...")
            try:
                subprocess.check_call(
                    ["npm", "install", "-g", "@gitlawb/openclaude"],
                    stdout=subprocess.DEVNULL,
                )
                console.print("[green]OpenClaude instalado![/green]")
            except Exception:
                console.print("[yellow]Nao foi possivel instalar via npm.[/yellow]")
                console.print(
                    "Instale manualmente: [cyan]npm install -g @gitlawb/openclaude[/cyan]"
                )
                console.print("\nVeja o tutorial em video:")
                console.print("[link]https://www.youtube.com/watch?v=AxE8gDFeMic[/link]\n")
                return

    console.print("\n[dim]Para configurar sua conta OpenRouter:[/dim]")
    console.print("1. Acesse [link]https://openrouter.ai/[/link]")
    console.print("2. Crie uma conta e gere uma API Key")
    console.print("3. Copie a chave (comeca com sk-or-v1-)")
    console.print("\nVeja o tutorial em video:")
    console.print("[link]https://www.youtube.com/watch?v=AxE8gDFeMic[/link]\n")

    api_key = questionary.password("Cole sua OPENAI_API_KEY do OpenRouter:").ask()
    if not api_key:
        console.print("[yellow]Chave nao informada. O agente default nao funcionara ate voce configurar.[/yellow]")
        console.print("\nPara configurar depois:")
        console.print("  [cyan]myc add-agent --name default[/cyan]")
        return

    model = questionary.text("Modelo (padrao: qwen/qwen3.6-plus:free):", default="qwen/qwen3.6-plus:free").ask() or "qwen/qwen3.6-plus:free"

    from myc.agent import _load_agents, _save_agents
    from datetime import datetime

    agents = _load_agents()
    agents["default"] = {
        "name": "default",
        "platform": "openclaude",
        "env": {
            "CLAUDE_CODE_USE_OPENAI": "1",
            "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
            "OPENAI_API_KEY": api_key,
            "OPENAI_MODEL": model,
        },
        "cwd": None,
        "initial_context": "",
        "custom_command": None,
        "plugins": [],
        "linked_routines": [],
        "created_at": datetime.now().isoformat(),
    }
    _save_agents(agents)

    console.print(
        Panel(
            f"[bold green]Agente 'default' configurado![/bold green]\n\n"
            f"  Modelo:    [cyan]{model}[/cyan]\n"
            f"  Provider:  OpenRouter (openrouter.ai)\n\n"
            f"[bold]Como usar:[/bold]\n"
            f"  [cyan]myc agent launch default[/cyan]         — lancar no diretorio atual\n"
            f"  [cyan]myc agent launch default --cwd X[/cyan] — lancar em outro diretorio\n"
            f"  [cyan]myc automate default --group X[/cyan]   — lancar com contexto MYC",
            border_style="green",
        )
    )


# ─── automate ─────────────────────────────

@main.command(name="automate")
@click.argument("agent_name")
@click.option("--group", "-g", default=None, help="Executa comandos de um grupo MYC")
@click.option("--subcommand", "-s", default=None, help="Subcomando especifico")
def automate_cmd(agent_name: str, group: Optional[str], subcommand: Optional[str]) -> None:
    """Lanca um agente e executa rotinas MYC como contexto."""
    from myc.agent import launch_with_myc_tasks
    launch_with_myc_tasks(agent_name, group=group, subcommand=subcommand)


# ─── agent: bundle ─────────────────────────────

@agent_cmd.command(name="bundle-install")
@click.option("--all", "all_", is_flag=True, help="Instala todos os bundles")
@click.option("--company", is_flag=True, help="Instala bundles de empresas")
@click.argument("names", nargs=-1, required=False)
def agent_bundle_install_cmd(all_: bool, company: bool, names: tuple) -> None:
    """Instala bundles de specialists ou empresas.

    \b
    Exemplos:
      myc agent bundle-install --all
      myc agent bundle-install fullstack professor
      myc agent bundle-install --company dev_house_full
    """
    if company:
        from myc.plugin_manager import COMPANY_BUNDLES, install_company_bundle, list_company_bundles
        if all_ or not names:
            if not names:
                list_company_bundles()
                return
            for bid in COMPANY_BUNDLES:
                install_company_bundle(bid)
        else:
            for bid in names:
                install_company_bundle(bid)
    else:
        from myc.plugin_manager import install_bundles
        install_bundles(all_=all_, names=list(names) if names else None)


@agent_cmd.command(name="bundle-list")
@click.option("--company", is_flag=True, help="Lista bundles de empresas")
def agent_bundle_list_cmd(company: bool) -> None:
    """Lista bundles disponiveis."""
    if company:
        from myc.plugin_manager import list_company_bundles
        list_company_bundles()
    else:
        from myc.plugin_manager import list_bundles
        list_bundles()


# ─── agent: specialist ─────────────────────────

@main.command(name="agent-specialist")
@click.argument("name", required=True)
@click.option("-o", "--middleware", "middlewares", multiple=True, help="Aplica middleware(s)")
@click.argument("command", nargs=-1, required=False)
def agent_specialist_cmd(name: str, middlewares: tuple, command: tuple) -> None:
    """Lanca um especialista com query.

    \b
    Exemplos:
      myc agent-specialist social_media "crie calendario editorial"
      myc agent-specialist frontend_dev -o prompt_enhancer "crie componente login"
      myc agent-specialist backend_dev -o security_checker "implemente auth JWT"
    """
    from myc.agent_plugins import list_plugins, execute_plugins

    available = {p["id"]: p["name"] for p in list_plugins()}
    if name not in available:
        console.print(f"[red]Specialist '{name}' nao encontrado.[/red]")
        console.print(f"Disponiveis: {', '.join(available.keys())}")
        sys.exit(1)

    # Monta query
    query = " ".join(command) if command else ""
    if not query:
        console.print(f"[yellow]Nenhum comando fornecido. Abrindo prompt interativo...[/yellow]")
        import questionary
        query = questionary.text("O que o especialista deve fazer?").ask() or ""
        if not query:
            return

    # Aplica middlewares pre no prompt
    for mw_id in middlewares:
        mw_file = Path.home() / ".myc" / "agents" / "middlewares" / f"{mw_id}.py"
        if mw_file.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(mw_id, mw_file)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                fn = getattr(mod, "PROMPT_MODIFY", None)
                if fn:
                    query = fn(query, {})
                    console.print(f"[dim]Middleware '{mw_id}' aplicado ao prompt.[/dim]")
            except Exception as e:
                console.print(f"[yellow]Middleware '{mw_id}' falhou: {e}[/yellow]")

    # Cria agente temp com o specialist + middlewares
    _launch_specialist_query(name, query, list(middlewares))


def _launch_specialist_query(specialist_id: str, query: str, middleware_ids: list) -> int:
    """Lanca uma query num specialist (usa agente 'default' se existir, senao imprime)."""
    from myc.agent import _load_agents, _write_claude_md, launch_agent
    from myc.agent_plugins import _load_plugin_file
    from pathlib import Path

    PLUGINS_DIR = Path.home() / ".myc" / "agents" / "plugins"

    # Carrega contexto do specialist
    plugin_file = PLUGINS_DIR / f"{specialist_id}.py"
    if not plugin_file.exists():
        from myc.plugin_installer import SPECIALISTS_DIR
        import shutil
        builtin = SPECIALISTS_DIR / f"{specialist_id}.py"
        if builtin.exists():
            shutil.copy2(str(builtin), str(plugin_file))

    context = ""
    if plugin_file.exists():
        try:
            mod = _load_plugin_file(plugin_file)
            if mod:
                ctx_fn = getattr(mod, "CONTEXT", None)
                if ctx_fn:
                    context = ctx_fn({})
                else:
                    name = getattr(mod, "NAME", specialist_id)
                    context = f"Voce e {name}. {getattr(mod, 'DESCRIPTION', '')}"
        except Exception:
            context = f"Voce e o especialista '{specialist_id}'."
    else:
        console.print(f"[red]Plugin specialist '{specialist_id}' nao encontrado.[/red]")
        console.print(f"Instale com: myc agent bundle-install")
        return 1

    final_prompt = f"{context}\n\n---\n\n## Tarefa\n\n{query}"

    # Tenta lancar via agente 'default'
    agents = _load_agents()
    if "default" in agents:
        # Grava CLAUDE.md temporario no cwd
        cwd = agents["default"].get("cwd") or str(Path.cwd())
        md_path = Path(cwd) / "CLAUDE.md"
        if md_path.exists():
            backup = md_path.read_text(encoding="utf-8")
            md_path.write_text(f"# Agent: {specialist_id}\n\n## MYC Tasks\n\n## {specialist_id} Context\n\n{context}\n\n---\n\n## Tarefa\n\n{query}", encoding="utf-8")
            try:
                rc = launch_agent("default", cwd=cwd)
                md_path.write_text(backup, encoding="utf-8")
                return rc
            except Exception:
                md_path.write_text(backup, encoding="utf-8")
                return 1
        else:
            md_path.write_text(f"# Agent: {specialist_id}\n\n## {specialist_id} Context\n\n{context}\n\n---\n\n## Tarefa\n\n{query}", encoding="utf-8")
            try:
                rc = launch_agent("default", cwd=cwd)
                md_path.unlink(missing_ok=True)
                return rc
            except Exception:
                md_path.unlink(missing_ok=True)
                return 1
    else:
        # Sem agente configurado — mostra o prompt
        console.print(f"\n[bold]Specialist: {specialist_id}[/bold]\n")
        console.print(final_prompt)
        console.print("\n[yellow]Nenhum agente 'default' configurado para executar.[/yellow]")
        console.print("Configure com: [cyan]myc agent add[/cyan]")
        return 0


# ─── agent: company ────────────────────────────

@main.command(name="agent-company")
@click.argument("company_name", required=True)
@click.argument("specialist_arg", required=False, default=None)
@click.option("-o", "--middleware", "middlewares", multiple=True, help="Aplica middleware(s)")
@click.argument("command", nargs=-1, required=False)
def agent_company_cmd(company_name: str, specialist_arg: Optional[str], middlewares: tuple, command: tuple) -> None:
    """Lanca empresa com sub-agente especializado.

    \b
    Exemplos:
      myc agent-company dev_agency tech_lead "crie arquitetura microservicos"
      myc agent-company marketing_agency_company social_strategist "planeje campanha Q4"
      myc agent-company dev_agency -o prompt_enhancer "refatore API REST"
      myc agent-company dev_agency  # lista sub-agentes disponiveis
    """
    from myc.agent_plugins import execute_company_profile, list_companies, list_plugins as _list

    available = {c["id"]: c["name"] for c in list_companies()}
    if company_name not in available:
        console.print(f"[red]Empresa '{company_name}' nao encontrada.[/red]")
        console.print(f"Disponiveis: {', '.join(available.keys())}")
        sys.exit(1)

    query = " ".join(command) if command else ""

    if specialist_arg is None:
        # Mostra sub-agentes
        context = execute_company_profile(company_name)
        console.print(f"\n[bold]Empresa: {available[company_name]}[/bold]\n")
        console.print(context)
        return

    if not query:
        import questionary
        query = questionary.text(
            f"O que '{specialist_arg}' na empresa '{company_name}' deve fazer?",
        ).ask() or ""
        if not query:
            return

    # Aplica middlewares pre
    for mw_id in middlewares:
        mw_file = Path.home() / ".myc" / "agents" / "middlewares" / f"{mw_id}.py"
        if mw_file.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(mw_id, mw_file)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                fn = getattr(mod, "PROMPT_MODIFY", None)
                if fn:
                    query = fn(query, {})
                    console.print(f"[dim]Middleware '{mw_id}' aplicado.[/dim]")
            except Exception as e:
                console.print(f"[yellow]Middleware '{mw_id}' falhou: {e}[/yellow]")

    context = execute_company_profile(company_name, specialist_id=specialist_arg)
    if not context:
        return

    _launch_query_as_agent(f"{company_name}/{specialist_arg}", context, query)


# ─── agent: department ─────────────────────────

@main.command(name="agent-department")
@click.argument("department_name", required=True)
@click.option("-o", "--middleware", "middlewares", multiple=True, help="Aplica middleware(s)")
@click.option("-c", "--company", default=None, help="Filtra por empresa")
@click.argument("command", nargs=-1, required=False)
def agent_department_cmd(department_name: str, middlewares: tuple, company: Optional[str], command: tuple) -> None:
    """Lanca departamento ou equipe.

    \b
    Exemplos:
      myc agent-department marketing "crie campanha de vendas"
      myc agent-department marketing -o prompt_enhancer "planeje estrategia SEO"
      myc agent-department dev_frontend -c dev_agency "crie dashboard admin"
      myc agent-department --list  # lista departamentos
    """
    from myc.department import list_departments, get_department_context

    query = " ".join(command) if command else ""

    # Lista se sem comando
    if department_name == "--list":
        depts = list_departments(company_id=company)
        if not depts:
            console.print("[yellow]Nenhum departamento encontrado.[/yellow]")
            return
        from rich.table import Table
        table = Table(title="Departamentos", show_lines=True)
        table.add_column("ID", style="cyan")
        table.add_column("Nome", style="yellow")
        table.add_column("Descricao", style="green")
        table.add_column("Specialists", style="dim")
        table.add_column("Empresa", style="magenta")
        for d in depts:
            table.add_row(
                d["id"],
                d["name"],
                d["description"],
                ", ".join(d.get("specialists", [])) or "-",
                d.get("parent_company") or "independente",
            )
        console.print(table)
        return

    depts = list_departments(company_id=company)
    match = None
    for d in depts:
        if d["id"] == department_name:
            match = d
            break

    if not match:
        console.print(f"[red]Departamento '{department_name}' nao encontrado.[/red]")
        available = [d["id"] for d in depts]
        if available:
            console.print(f"Disponiveis: {', '.join(available)}")
        else:
            console.print("Nenhum departamento disponivel. Crie com departamentos built-in.")
        sys.exit(1)

    if not query:
        import questionary
        query = questionary.text(f"O que o departamento '{department_name}' deve fazer?").ask() or ""
        if not query:
            return

    # Aplica middlewares pre
    for mw_id in middlewares:
        mw_file = Path.home() / ".myc" / "agents" / "middlewares" / f"{mw_id}.py"
        if mw_file.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(mw_id, mw_file)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                fn = getattr(mod, "PROMPT_MODIFY", None)
                if fn:
                    query = fn(query, {})
                    console.print(f"[dim]Middleware '{mw_id}' aplicado.[/dim]")
            except Exception as e:
                console.print(f"[yellow]Middleware '{mw_id}' falhou: {e}[/yellow]")

    context = get_department_context(department_name)
    if not context:
        console.print(f"[red]Nao foi possivel carregar contexto do departamento.[/red]")
        return

    _launch_query_as_agent(f"department/{department_name}", context, query)


# ─── agent: middleware ─────────────────────────

@agent_cmd.command(name="middleware")
@click.option("--list", "list_", is_flag=True, help="Lista middlewares instalados")
def agent_middleware_cmd(list_: bool) -> None:
    """Lista middlewares disponiveis."""
    if not list_:
        console.print("Use [cyan]myc agent middleware --list[/cyan]")
        return

    from rich.table import Table
    from pathlib import Path

    MW_DIR = Path.home() / ".myc" / "agents" / "middlewares"
    MW_BUILTIN = Path(__file__).parent.parent / "plugins" / "middlewares"

    # Auto-instala builtins
    for f in MW_BUILTIN.glob("*.py"):
        if f.stem.startswith("_"):
            continue
        target = MW_DIR / f.name
        if not target.exists():
            import shutil
            shutil.copy2(str(f), str(target))

    table = Table(title="Middlewares", show_lines=True)
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="yellow")
    table.add_column("Descricao", style="green")
    table.add_column("Tipo", style="magenta")
    table.add_column("Quando", style="dim")

    for f in MW_DIR.glob("*.py"):
        if f.stem.startswith("_"):
            continue
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(f.stem, f)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            table.add_row(
                f.stem,
                getattr(mod, "NAME", f.stem),
                getattr(mod, "DESCRIPTION", ""),
                getattr(mod, "MIDDLEWARE_TYPE", "?"),
                getattr(mod, "RUNS_WHEN", "manual"),
            )
        except Exception as e:
            table.add_row(f.stem, f"[ERRO]", str(e), "?", "?")

    console.print(table)


# ─── agent: department create ─────────────────

@agent_cmd.command(name="department-add")
def agent_department_add_cmd() -> None:
    """Cria um novo departamento/equipe (wizard)."""
    from myc.department import create_department_wizard
    create_department_wizard()


@agent_cmd.command(name="company-add")
def agent_company_add_cmd() -> None:
    """Cria uma nova empresa (wizard)."""
    from myc.agent_plugins import create_company_wizard
    create_company_wizard()


def _launch_query_as_agent(agent_label: str, context: str, query: str) -> int:
    """Lanca uma query via agente 'default' com contexto injetado."""
    from myc.agent import _load_agents, launch_agent
    from pathlib import Path

    agents = _load_agents()
    if "default" in agents:
        cwd = agents["default"].get("cwd") or str(Path.cwd())
        md_path = Path(cwd) / "CLAUDE.md"
        backup = None
        if md_path.exists():
            backup = md_path.read_text(encoding="utf-8")
        md_path.write_text(f"# Agent: {agent_label}\n\n{context}\n\n---\n\n## Tarefa\n\n{query}", encoding="utf-8")
        try:
            rc = launch_agent("default", cwd=cwd)
            if backup is not None:
                md_path.write_text(backup, encoding="utf-8")
            else:
                md_path.unlink(missing_ok=True)
            return rc
        except Exception:
            if backup is not None:
                md_path.write_text(backup, encoding="utf-8")
            else:
                md_path.unlink(missing_ok=True)
            return 1
    else:
        console.print(f"\n[bold]{agent_label}[/bold]\n")
        console.print(f"{context}\n\n---\n\n## Tarefa\n\n{query}")
        console.print("\n[yellow]Nenhum agente 'default' configurado.[/yellow]")
        console.print("Configure com: [cyan]myc agent add[/cyan]")
        return 0
