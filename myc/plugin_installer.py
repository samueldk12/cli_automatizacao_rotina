"""
Instala plugins built-in no diretorio do usuario (~/.myc/agents/plugins/).

Plugins built-in ficam em <repo>/plugins/ e sao copiados para ~/.myc/agents/plugins/
quando instalados via `myc agent bundle-install` ou `myc agent add-plugin`.
"""

import shutil
from pathlib import Path

from rich.console import Console

console = Console()

PLUGINS_DIR = Path.home() / ".myc" / "agents" / "plugins"
# Diretorio dos plugins built-in (dentro do pacote myc)
MYC_DIR = Path(__file__).parent
BUILTIN_DIR = MYC_DIR.parent / "plugins"

# Mapa de plugin_id -> gerador de conteudo
# Cada plugin e gerado dinamicamente para nao depender de arquivos extras

_plugin_generators = {}


def register_plugin(id_: str, generator) -> None:
    """Registra um plugin com sua função geradora de conteudo."""
    _plugin_generators[id_] = generator


def get_plugin_meta(plugin_id: str) -> dict | None:
    """Verifica se plugin ja esta instalado e retorna metadados."""
    f = PLUGINS_DIR / f"{plugin_id}.py"
    if not f.exists():
        return None
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(plugin_id, f)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return {
            "name": getattr(mod, "NAME", plugin_id),
            "description": getattr(mod, "DESCRIPTION", ""),
            "file": str(f),
            "hooks": [h for h in ("PRE_LAUNCH", "POST_LAUNCH", "CONTEXT") if hasattr(mod, h)],
        }
    except Exception as e:
        return {"name": plugin_id, "description": f"Erro ao carregar: {e}", "file": str(f)}


def install_plugin(plugin_id: str) -> bool:
    """Instala um plugin built-in no diretorio do usuario."""
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    target = PLUGINS_DIR / f"{plugin_id}.py"

    # Ja instalado?
    if target.exists():
        console.print(f"  [dim]  {plugin_id}: ja instalado[/dim]")
        return False

    # Tenta builtin
    builtin = BUILTIN_DIR / f"{plugin_id}.py"
    if builtin.exists():
        shutil.copy2(str(builtin), str(target))
        meta = get_plugin_meta(plugin_id)
        name = meta["name"] if meta else plugin_id
        console.print(f"  [green]  + {name}[/green]")
        return True

    # Tenta gerador
    if plugin_id in _plugin_generators:
        content = _plugin_generators[plugin_id](plugin_id)
        target.write_text(content, encoding="utf-8")
        console.print(f"  [green]  + {plugin_id} (gerado)[/green]")
        return True

    console.print(f"  [yellow]  ? {plugin_id}: plugin nao encontrado[/yellow]")
    return False


def install_plugin_from_file(filepath: str) -> bool:
    """Instala um plugin a partir de um arquivo .py local."""
    src = Path(filepath)
    if not src.exists() or not src.name.endswith(".py"):
        console.print(f"[red]Arquivo invalido: {filepath}[/red]")
        return False

    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    target = PLUGINS_DIR / src.name
    shutil.copy2(str(src), str(target))
    console.print(f"[green]Plugin {src.name} instalado.[/green]")
    return True


def uninstall_plugin(plugin_id: str) -> bool:
    """Remove um plugin do diretorio do usuario."""
    target = PLUGINS_DIR / f"{plugin_id}.py"
    if not target.exists():
        console.print(f"[yellow]Plugin '{plugin_id}' nao instalado.[/yellow]")
        return False
    target.unlink()
    console.print(f"[green]Plugin '{plugin_id}' removido.[/green]")
    return True
