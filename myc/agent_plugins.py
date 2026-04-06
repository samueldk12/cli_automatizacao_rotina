"""
Sistema de plugins para agentes.

Cada plugin e um arquivo Python em ~/.myc/agents/plugins/ que exporta:
  - NAME: str                    — nome do plugin
  - DESCRIPTION: str             — descricao curta
  - PRE_LAUNCH(agent_profile)    — hook antes de lancar o agente
  - POST_LAUNCH(agent_profile)   — hook apos o agente iniciar (opcional)
  - CONTEXT(agent_profile) -> str  — texto extra para injetar no CLAUDE.md
"""

import importlib.util
import shutil
import sys
from pathlib import Path
from typing import Any

from rich.console import Console

console = Console()

PLUGINS_DIR = Path.home() / ".myc" / "agents" / "plugins"

# Plugins built-in dentro do pacote
def _get_pkg_plugins_dir() -> Path:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / "plugins" / "bundles"
    return Path(__file__).parent.parent / "plugins" / "bundles"

MYC_PKG = _get_pkg_plugins_dir()


def _ensure_plugins_dir() -> None:
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)


def _load_plugin_file(filepath: Path) -> Any | None:
    """Carrega um modulo plugin a partir do arquivo .py."""
    spec = importlib.util.spec_from_file_location(filepath.stem, filepath)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def list_plugins() -> list:
    """Lista todos os plugins disponiveis com seus metadados."""
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
    """Executa o hook de todos os plugins listados no perfil do agente.

    Retorna texto extra de contexto gerado pelos plugins (para CLAUDE.md).
    """
    plugins_list = agent_profile.get("plugins", [])
    if not plugins_list:
        return ""

    _ensure_plugins_dir()
    context_parts = []

    for plugin_id in plugins_list:
        plugin_file = PLUGINS_DIR / f"{plugin_id}.py"

        if not plugin_file.exists() and (MYC_PKG / f"{plugin_id}.py").exists():
            shutil.copy2(str(MYC_PKG / f"{plugin_id}.py"), str(plugin_file))

        if not plugin_file.exists():
            console.print(f"[yellow]Plugin '{plugin_id}' nao encontrado, ignorando.[/yellow]")
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
                        console.print(f"[green]Plugin '{getattr(mod, 'NAME', plugin_id)}' ({hook}) executado.[/green]")
                except Exception as e:
                    console.print(f"[red]Plugin '{getattr(mod, 'NAME', plugin_id)}' ({hook}) falhou: {e}[/red]")

            ctx_fn = getattr(mod, "CONTEXT", None)
            if ctx_fn:
                try:
                    extra = ctx_fn(agent_profile)
                    if extra:
                        context_parts.append(f"### Plugin: {getattr(mod, 'NAME', plugin_id)}\n\n{extra}")
                except Exception as e:
                    console.print(f"[red]Plugin '{getattr(mod, 'NAME', plugin_id)}' CONTEXT falhou: {e}[/red]")

        except Exception as e:
            console.print(f"[red]Erro no plugin '{plugin_id}': {e}[/red]")

    return "\n\n".join(context_parts)


def install_plugin_from_url(url: str, name: str) -> str | None:
    """Baixa um plugin de uma URL e salva em plugins dir."""
    import urllib.request

    _ensure_plugins_dir()
    target = PLUGINS_DIR / f"{name}.py"

    # Nao sobrescreve sem aviso
    if target.exists():
        backup = target.with_suffix(".py.bak")
        backup.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")

    try:
        urllib.request.urlretrieve(url, str(target))
        console.print(f"[green]Plugin '{name}' instalado em {target}[/green]")
        return str(target)
    except Exception as e:
        console.print(f"[red]Falha ao baixar plugin: {e}[/red]")
        return None


def create_plugin_wizard() -> None:
    """Wizard para criar um arquivo de plugin basico."""
    import questionary

    console.print("\n[bold cyan]Criar Plugin de Agente[/bold cyan]")

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
