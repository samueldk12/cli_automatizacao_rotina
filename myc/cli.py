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


@agent_cmd.command(name="bundle-install")
@click.argument("bundles", nargs=-1, required=False)
@click.option("--all", "all_bundles", is_flag=True, help="Instala todos os bundles")
@click.option("--agent", "-a", default=None, help="Vincula ao agente especifico")
def agent_bundle_install(bundles: tuple, all_bundles: bool, agent: Optional[str]) -> None:
    """Instala bundles de plugins e vincula a um agente.

    \b
    Exemplos:
      myc agent bundle-install --all
      myc agent bundle-install bugbounty --agent dev
      myc agent bundle-install marketing visao_computacional --agent default
    """
    from myc.plugin_manager import install_bundles, register_bundle_install

    if all_bundles or (not bundles and not agent):
        install_bundles(all_=all_bundles)
        return

    bundle_list = list(bundles)
    install_bundles(names=bundle_list)

    if agent:
        for b in bundle_list:
            register_bundle_install(b, agent)


@agent_cmd.command(name="bundles")
def agent_bundles_list() -> None:
    """Lista bundles disponiveis e status de instalacao."""
    from myc.plugin_manager import list_bundles
    list_bundles()


@agent_cmd.command(name="install-plugin")
@click.argument("filepath")
def agent_install_plugin_file(filepath: str) -> None:
    """Instala um plugin a partir de um arquivo .py local.

    \b
    Exemplo:
      myc agent install-plugin ~/meu_plugin.py
    """
    from myc.plugin_installer import install_plugin_from_file
    install_plugin_from_file(filepath)


# ─── automate ─────────────────────────────

@main.command(name="automate")
@click.argument("agent_name")
@click.option("--group", "-g", default=None, help="Executa comandos de um grupo MYC")
@click.option("--subcommand", "-s", default=None, help="Subcomando especifico")
def automate_cmd(agent_name: str, group: Optional[str], subcommand: Optional[str]) -> None:
    """Lanca um agente e executa rotinas MYC como contexto.

    \b
    Exemplos:
      myc automate dev --group estudar
      myc automate dev --group trabalhar --subcommand daily-standup
    """
    from myc.agent import launch_with_myc_tasks
    launch_with_myc_tasks(agent_name, group=group, subcommand=subcommand)
