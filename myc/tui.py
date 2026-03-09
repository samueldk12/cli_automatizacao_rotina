from typing import Optional

import questionary
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from myc.config import load_config
from myc.runner import DAYS_DISPLAY, DAYS_PT, list_day_commands, run_command

console = Console(legacy_windows=False)


# ─────────────────────────────────────────────
# Helpers de exibição
# ─────────────────────────────────────────────

def _action_summary(actions: list) -> str:
    parts = []
    for a in actions:
        if a.get("type") in ("browser", "url"):
            mon = a.get("monitor", 0)
            parts.append(f"🌐 Monitor {mon + 1}")
        elif a.get("type") == "app":
            parts.append(f"💻 {a.get('path', '?')}")
    return "  ".join(parts) if parts else "—"


def show_commands_table(commands: dict) -> None:
    """Exibe tabela formatada de todos os comandos."""
    if not commands:
        console.print("[yellow]Nenhum comando cadastrado.[/yellow]")
        return

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        expand=False,
    )
    table.add_column("Grupo", style="bold green")
    table.add_column("Subcomando", style="yellow")
    table.add_column("Descrição")
    table.add_column("Dias", style="blue")
    table.add_column("Ações")

    for group_name, group_data in commands.items():
        for sub_name, sub_data in group_data.get("subcommands", {}).items():
            days = sub_data.get("days", [])
            days_str = (
                "  ".join(DAYS_DISPLAY.get(d, d)[:3] for d in days)
                if days
                else "[dim]Todos[/dim]"
            )
            table.add_row(
                group_name,
                sub_name,
                sub_data.get("description", ""),
                days_str,
                _action_summary(sub_data.get("actions", [])),
            )

    console.print(table)


def show_day_schedule() -> None:
    """Exibe grade semanal de comandos."""
    config = load_config()
    commands = config.get("commands", {})

    table = Table(
        title="Grade Semanal de Comandos",
        box=box.HEAVY_EDGE,
        show_header=True,
        header_style="bold magenta",
        expand=True,
    )

    for day, display in DAYS_DISPLAY.items():
        table.add_column(display[:3], style="cyan", justify="center")

    rows_by_day: dict[str, list[str]] = {d: [] for d in DAYS_PT}
    for group_name, group_data in commands.items():
        for sub_name, sub_data in group_data.get("subcommands", {}).items():
            days = sub_data.get("days", [])
            entry = f"[green]{group_name}[/green]/\n[yellow]{sub_name}[/yellow]"
            for d in (days if days else DAYS_PT):
                if d in rows_by_day:
                    rows_by_day[d].append(entry)

    max_rows = max(len(v) for v in rows_by_day.values()) if rows_by_day else 0
    for i in range(max_rows):
        row = []
        for day in DAYS_PT:
            entries = rows_by_day[day]
            row.append(entries[i] if i < len(entries) else "")
        table.add_row(*row)

    console.print(table)


# ─────────────────────────────────────────────
# Navegação por grupo
# ─────────────────────────────────────────────

def _navigate_group_subcommands(group_name: str, group_data: dict) -> None:
    subcommands = group_data.get("subcommands", {})
    if not subcommands:
        console.print(f"[yellow]Nenhum subcomando em '{group_name}'.[/yellow]")
        return

    choices = []
    for sub_name, sub_data in subcommands.items():
        days = sub_data.get("days", [])
        days_str = ", ".join(d[:3] for d in days) if days else "todos"
        label = f"▶  {sub_name}  [{days_str}]  —  {sub_data.get('description', '')}"
        choices.append(questionary.Choice(label, value=sub_name))
    choices.append(questionary.Choice("← Voltar", value="_back"))

    sub = questionary.select(
        f"Subcomandos de '{group_name}':",
        choices=choices,
        style=questionary.Style([("selected", "fg:cyan bold"), ("pointer", "fg:cyan bold")]),
    ).ask()

    if sub and sub != "_back":
        console.print(f"\n[bold green]Executando:[/bold green] {group_name} {sub}\n")
        run_command(group_name, sub)


def navigate_by_group(commands: dict) -> None:
    choices = [
        questionary.Choice(
            f"📁  {name}  —  {data.get('description', '')}  ({len(data.get('subcommands', {}))} cmds)",
            value=name,
        )
        for name, data in commands.items()
    ]
    choices.append(questionary.Choice("← Voltar", value="_back"))

    group = questionary.select(
        "Escolha um grupo:",
        choices=choices,
        style=questionary.Style([("selected", "fg:green bold")]),
    ).ask()

    if group and group != "_back":
        _navigate_group_subcommands(group, commands[group])


# ─────────────────────────────────────────────
# Navegação por dia
# ─────────────────────────────────────────────

def navigate_by_day(commands: dict) -> None:
    day_choices = [
        questionary.Choice(f"📅  {display}", value=day)
        for day, display in DAYS_DISPLAY.items()
    ]
    day_choices.append(questionary.Choice("← Voltar", value="_back"))

    day = questionary.select(
        "Escolha o dia da semana:",
        choices=day_choices,
    ).ask()

    if not day or day == "_back":
        return

    config = load_config()
    results = list_day_commands(day, config)

    if not results:
        console.print(
            f"[yellow]Nenhum comando para {DAYS_DISPLAY.get(day, day)}.[/yellow]"
        )
        questionary.press_any_key_to_continue().ask()
        return

    run_choices = [
        questionary.Choice(
            f"▶  {group}/{sub}  —  {data.get('description', '')}",
            value=(group, sub),
        )
        for group, sub, data in results
    ]
    run_choices.append(questionary.Choice("← Voltar", value=("_back", "")))

    choice = questionary.select(
        f"Comandos para {DAYS_DISPLAY.get(day, day)}:",
        choices=run_choices,
    ).ask()

    if choice and choice[0] != "_back":
        group, sub = choice
        console.print(f"\n[bold green]Executando:[/bold green] {group} {sub}\n")
        run_command(group, sub, day)


# ─────────────────────────────────────────────
# Busca
# ─────────────────────────────────────────────

def navigate_search(commands: dict) -> None:
    query = questionary.text("Buscar comando (nome ou descrição):").ask()
    if not query:
        return

    query_lower = query.lower()
    results = []
    for group_name, group_data in commands.items():
        for sub_name, sub_data in group_data.get("subcommands", {}).items():
            if query_lower in sub_name.lower() or query_lower in sub_data.get(
                "description", ""
            ).lower():
                results.append((group_name, sub_name, sub_data))

    if not results:
        console.print(f"[yellow]Sem resultados para '{query}'.[/yellow]")
        questionary.press_any_key_to_continue().ask()
        return

    run_choices = [
        questionary.Choice(
            f"▶  {group}/{sub}  —  {data.get('description', '')}",
            value=(group, sub),
        )
        for group, sub, data in results
    ]
    run_choices.append(questionary.Choice("← Voltar", value=("_back", "")))

    choice = questionary.select("Resultados:", choices=run_choices).ask()
    if choice and choice[0] != "_back":
        group, sub = choice
        console.print(f"\n[bold green]Executando:[/bold green] {group} {sub}\n")
        run_command(group, sub)


# ─────────────────────────────────────────────
# TUI principal
# ─────────────────────────────────────────────

def navigate_tui(group_filter: Optional[str] = None) -> None:
    """
    Abre a navegação visual interativa.

    Args:
        group_filter: Se informado, entra diretamente nos subcomandos do grupo.
    """
    config = load_config()
    commands = config.get("commands", {})

    if not commands:
        console.print(
            Panel(
                "[yellow]Nenhum comando cadastrado ainda.[/yellow]\n\n"
                "Use [cyan bold]myc add[/cyan bold] para criar seu primeiro comando.",
                border_style="yellow",
                title="MYC",
            )
        )
        return

    # Entrada direta em um grupo específico (via wrapper sem args)
    if group_filter:
        if group_filter not in commands:
            console.print(f"[red]Grupo '{group_filter}' não encontrado.[/red]")
            return
        _navigate_group_subcommands(group_filter, commands[group_filter])
        return

    # Menu principal
    while True:
        console.clear()
        console.print(
            Panel(
                "[bold cyan]MYC — My Commands[/bold cyan]\n"
                "[dim]Gerencie e execute seus comandos personalizados[/dim]",
                border_style="cyan",
                padding=(0, 2),
            )
        )

        mode = questionary.select(
            "Como deseja navegar?",
            choices=[
                questionary.Choice("📂  Por grupo de comandos", value="group"),
                questionary.Choice("📅  Por dia da semana", value="day"),
                questionary.Choice("📊  Ver grade semanal", value="week"),
                questionary.Choice("🔍  Buscar comando", value="search"),
                questionary.Choice("📋  Listar todos", value="list"),
                questionary.Choice("❌  Sair", value="exit"),
            ],
            style=questionary.Style([("selected", "fg:cyan bold"), ("pointer", "fg:cyan bold")]),
        ).ask()

        if mode is None or mode == "exit":
            break
        elif mode == "group":
            navigate_by_group(commands)
            # Recarrega config caso tenha mudado
            config = load_config()
            commands = config.get("commands", {})
        elif mode == "day":
            navigate_by_day(commands)
        elif mode == "week":
            console.clear()
            show_day_schedule()
            questionary.press_any_key_to_continue().ask()
        elif mode == "search":
            navigate_search(commands)
        elif mode == "list":
            console.clear()
            show_commands_table(commands)
            questionary.press_any_key_to_continue().ask()
