"""
Configuracoes customizadas para rotinas MYC.

Permite definir perfis customizados com:
  - Handlers de saida (console, arquivo, relatorio HTML)
  - Cadeia de middlewares
  - Caminhos de saida configuraveis
  - Variaveis de contexto

Perfis salvos em ~/.myc/custom_configs.json
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console

console = Console()

CUSTOM_CONFIGS_FILE = Path.home() / ".myc" / "custom_configs.json"
ROUTINE_HISTORY_FILE = Path.home() / ".myc" / "routine_history.json"

DEFAULT_OUTPUT = {
    "console": True,
    "file": False,
    "file_path": "",
    "html_report": False,
    "html_path": "",
}

CUSTOM_CONFIG_HOME = Path.home() / ".myc"
OUTPUT_DIR = CUSTOM_CONFIG_HOME / "output"
LOG_DIR = CUSTOM_CONFIG_HOME / "logs"


def load_custom_configs() -> list[dict]:
    """Carrega todas as configuracoes customizadas."""
    if not CUSTOM_CONFIGS_FILE.exists():
        return []
    try:
        data = json.loads(CUSTOM_CONFIGS_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data.get("configs", [])
        return data
    except (json.JSONDecodeError, OSError):
        return []


def save_custom_configs(configs: list[dict]) -> None:
    """Salva a lista completa de configuracoes customizadas."""
    CUSTOM_CONFIGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    CUSTOM_CONFIGS_FILE.write_text(
        json.dumps({"configs": configs}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get_custom_config(name: str) -> dict | None:
    """Busca uma configuracao customizada pelo ID."""
    for cfg in load_custom_configs():
        if cfg.get("id") == name:
            return cfg
    return None


def save_custom_config(cfg: dict) -> None:
    """Salva ou atualiza uma configuracao customizada."""
    configs = load_custom_configs()
    found = False
    for i, existing in enumerate(configs):
        if existing.get("id") == cfg["id"]:
            configs[i] = cfg
            found = True
            break
    if not found:
        configs.append(cfg)
    save_custom_configs(configs)


def delete_custom_config(name: str) -> bool:
    """Remove uma configuracao customizada. Retorna True se encontrou."""
    configs = load_custom_configs()
    new_configs = [c for c in configs if c.get("id") != name]
    if len(new_configs) < len(configs):
        save_custom_configs(new_configs)
        return True
    return False


def list_custom_configs() -> list[dict]:
    """Retorna lista de configs com metadados resumidos."""
    return load_custom_configs()


def ensure_dirs() -> None:
    """Garante que diretorios de output e logs existem."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_output_handler(cfg: dict) -> "OutputHandler":
    """Factory para o handler de saida baseado na config."""
    output = cfg.get("output", DEFAULT_OUTPUT)
    return OutputHandler(
        console=output.get("console", True),
        write_file=output.get("file", False),
        file_path=output.get("file_path", ""),
        html_report=output.get("html_report", False),
        html_path=output.get("html_path", ""),
        config_name=cfg.get("id", "default"),
    )


class OutputHandler:
    """Gerencia saida de resposta do agente em múltiplos destinos."""

    def __init__(
        self,
        console: bool = True,
        write_file: bool = False,
        file_path: str = "",
        html_report: bool = False,
        html_path: str = "",
        config_name: str = "default",
    ):
        self.console_output = console
        self.write_file = write_file
        self.html_report = html_report
        # Resolve paths
        ensure_dirs()
        if write_file and not file_path:
            self.file_path = str(OUTPUT_DIR / f"{config_name}.txt")
        else:
            self.file_path = file_path
        if html_report and not html_path:
            self.html_path = str(OUTPUT_DIR / f"{config_name}.html")
        else:
            self.html_path = html_path

    def write(self, content: str, label: str = "output") -> None:
        """Escreve conteudo em todos os destinos configurados."""
        if self.console_output:
            console.print(f"\n[bold cyan][{label}][/bold cyan]\n{content}")

        if self.write_file and self.file_path:
            p = Path(self.file_path).expanduser()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            console.print(f"[dim][OK] Salvo em {p}[/dim]")

        if self.html_report and self.html_path:
            self._write_html(content, label)

    def _write_html(self, content: str, label: str) -> None:
        """Gera relatorio HTML basico."""
        body = (
            "<!DOCTYPE html><html><head>"
            "<meta charset='utf-8'>"
            "<title>MYC - Relatorio {}</title>"
            "<style>"
            "body{{font-family:system-ui,sans-serif;max-width:900px;margin:40px auto;padding:20px}}"
            "pre{{white-space:pre-wrap;background:#f5f5f5;padding:20px;border-radius:8px}}"
            "h2{{color:#333}}"
            ".ts{{color:#999;font-size:0.9em}}"
            "</style>"
            "</head><body>"
            "<h2>MYC - {}</h2>"
            "<div class='ts'>{}</div>"
            "<pre>{}</pre>"
            "</body></html>"
        )
        p = Path(self.html_path).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            body.format(
                label, label,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"),
            ),
            encoding="utf-8",
        )


def record_routine_history(
    routine_name: str,
    duration_seconds: float,
    status: str = "completed",
    config_used: str = "",
    middlewares_used: list = None,
    output_path: str = "",
) -> None:
    """Registra execucao no historico de rotinas."""
    if ROUTINE_HISTORY_FILE.exists():
        try:
            entries = json.loads(ROUTINE_HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            entries = []
    else:
        entries = []

    entries.insert(0, {
        "routine": routine_name,
        "duration_seconds": round(duration_seconds, 2),
        "status": status,
        "config": config_used,
        "middlewares": middlewares_used or [],
        "output_path": output_path,
        "timestamp": datetime.now().isoformat(),
    })

    # Mantem no maximo 500 entradas
    ROUTINE_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    ROUTINE_HISTORY_FILE.write_text(
        json.dumps(entries[:500], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ── Wizard ─────────────────────────────────────────────────────

def create_config_wizard() -> None:
    """Wizard interativo para criar configuracao customizada."""
    import questionary

    console.print("\n[bold cyan]Criar Configuracao Customizada[/bold cyan]")
    console.print("[dim]Defina onde sera a saida, middlewares, e variaveis.[/dim]\n")

    # ID
    config_id = questionary.text(
        "ID da configuracao (sem espacos, ex: estudo_rapido, trabalho_dev):",
        validate=lambda x: (len(x) > 0 and " " not in x) or "Sem espacos",
    ).ask()
    if not config_id:
        return

    name = questionary.text(
        "Nome display:",
        default=config_id.replace("_", " ").title(),
    ).ask() or config_id

    description = questionary.text("Descricao (opcional):").ask() or ""

    # Agent profile
    from myc.agent import _load_agents
    agents = _load_agents()
    if agents:
        agent_choices = [questionary.Choice(n, value=n) for n in agents]
        agent_choices.insert(0, questionary.Choice("Nenhum / Perguntar depois", value=""))
        agent_profile = questionary.select(
            "Perfil de agente vinculado:",
            choices=agent_choices,
        ).ask() or ""
    else:
        agent_profile = ""

    # Output config
    console.print("\n[bold]Configuracao de Saida:[/bold]")
    console.print("[dim]Onde o resultado do agente deve ser salvo?[/dim]\n")

    out_console = questionary.confirm("Mostrar no console?", default=True).ask()
    out_file = questionary.confirm("Salvar em arquivo?", default=False).ask()
    out_file_path = ""
    if out_file:
        default_path = str(OUTPUT_DIR / f"{config_id}.txt")
        out_file_path = questionary.text(
            "Caminho do arquivo:",
            default=default_path,
        ).ask() or default_path

    out_html = questionary.confirm("Gerar relatorio HTML?", default=False).ask()
    out_html_path = ""
    if out_html:
        default_html = str(OUTPUT_DIR / f"{config_id}.html")
        out_html_path = questionary.text(
            "Caminho do HTML:",
            default=default_html,
        ).ask() or default_html

    output_section = {
        "console": out_console,
        "file": out_file,
        "file_path": out_file_path,
        "html_report": out_html,
        "html_path": out_html_path,
    }

    # Middlewares
    from myc.middleware_runner import list_all_middlewares
    all_mw = list_all_middlewares()
    if all_mw:
        console.print("\n[bold]Middlewares:[/bold]")
        console.print("[dim]Selecione os middlewares para esta config (ENTER = nenhum):[/dim]")
        mw_choices = [
            questionary.Choice(f"{m['id']} — {m.get('description', '')}", value=m["id"])
            for m in all_mw
        ]
        selected_mw = questionary.checkbox(
            "Middlewares:",
            choices=mw_choices,
        ).ask() or []
    else:
        selected_mw = []

    # Agent profile fallback for middleware
    agent_profile_data = {}
    if agent_profile and agent_profile in agents:
        agent_profile_data = agents[agent_profile]

    # Rotinas vinculadas
    from myc.config import load_config as load_myc_config
    myc_config = load_myc_config()
    commands = myc_config.get("commands", {})
    if commands:
        console.print("\n[bold]Rotinas vinculadas:[/bold]")
        console.print("[dim]Quais rotinas MYC usam esta config? (ENTER = nenhuma)[/dim]")
        routine_choices = []
        for grp, grp_data in commands.items():
            for sub in grp_data.get("subcommands", {}):
                routine_choices.append(
                    questionary.Choice(f"{grp} / {sub}", value=f"{grp}:{sub}")
                )
        if routine_choices:
            linked_routines = questionary.checkbox(
                "Rotinas:",
                choices=routine_choices,
            ).ask() or []
        else:
            linked_routines = []
    else:
        linked_routines = []

    # Variaveis customizadas
    variables: dict[str, str] = {}
    while questionary.confirm("Adicionar variavel customizada?", default=False).ask():
        var_name = questionary.text("Nome da variavel:").ask()
        if var_name:
            var_value = questionary.text(f"Valor para {var_name}:").ask() or ""
            variables[var_name.strip()] = var_value
        more = questionary.confirm("Outra variavel?", default=False).ask()
        if not more:
            break

    cfg = {
        "id": config_id,
        "name": name,
        "description": description,
        "output": output_section,
        "middlewares": selected_mw,
        "agent_profile": agent_profile,
        "linked_routines": linked_routines,
        "variables": variables,
        "created_at": datetime.now().isoformat(),
    }

    save_custom_config(cfg)
    ensure_dirs()

    console.print("\n[bold green]Configuracao customizada criada![/bold green]")
    console.print(f"  ID:          [cyan]{config_id}[/cyan]")
    console.print(f"  Saida:       console={out_console}, file={out_file}, html={out_html}")
    console.print(f"  Middlewares: {', '.join(selected_mw) if selected_mw else 'nenhum'}")
    if linked_routines:
        console.print(f"  Rotinas:     {', '.join(linked_routines)}")
    console.print(f"\n[dim]Use: myc custom run {config_id}[/dim]")
