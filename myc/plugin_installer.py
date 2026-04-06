"""
Instala plugins built-in no diretorio do usuario (~/.myc/agents/plugins/).

Plugins built-in ficam em <repo>/plugins/specialists/ e <repo>/plugins/companies/
e sao copiados para ~/.myc/agents/plugins/ ou ~/.myc/agents/companies/
quando instalados via `myc agent bundle-install` ou `myc agent add-plugin`.
"""

import shutil
import sys
from pathlib import Path

from rich.console import Console

console = Console()

PLUGINS_DIR = Path.home() / ".myc" / "agents" / "plugins"
COMPANIES_DIR = Path.home() / ".myc" / "agents" / "companies"
MIDDLEWARES_DIR = Path.home() / ".myc" / "agents" / "middlewares"


def _get_builtin_dir(subfolder: str = "specialists") -> Path:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / "plugins" / subfolder
    return Path(__file__).parent.parent / "plugins" / subfolder


SPECIALISTS_DIR = _get_builtin_dir("specialists")
BUILTIN_DIR = SPECIALISTS_DIR  # alias para compatibilidade

COMPANIES_BUILTIN = _get_builtin_dir("companies")
MIDDLEWARES_BUILTIN = _get_builtin_dir("middlewares")

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

    # Tenta builtin em specialists
    builtin = SPECIALISTS_DIR / f"{plugin_id}.py"
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


def install_company_plugin(plugin_id: str) -> bool:
    """Instala um plugin de empresa built-in no diretorio do usuario."""
    COMPANIES_DIR.mkdir(parents=True, exist_ok=True)
    target = COMPANIES_DIR / f"{plugin_id}.py"

    if target.exists():
        console.print(f"  [dim]  {plugin_id}: ja instalado[/dim]")
        return False

    builtin = COMPANIES_BUILTIN / f"{plugin_id}.py"
    if builtin.exists():
        shutil.copy2(str(builtin), str(target))
        meta = get_company_meta(plugin_id)
        name = meta.get("name", plugin_id) if meta else plugin_id
        console.print(f"  [green]  + {name} (empresa)[/green]")
        return True

    console.print(f"  [yellow]  ? {plugin_id}: plugin de empresa nao encontrado[/yellow]")
    return False


def get_company_meta(company_id: str) -> dict | None:
    """Verifica se um plugin de empresa esta instalado e retorna metadados."""
    f = COMPANIES_DIR / f"{company_id}.py"
    if not f.exists():
        return None
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(company_id, f)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return {
            "name": getattr(mod, "NAME", company_id),
            "description": getattr(mod, "DESCRIPTION", ""),
            "specialists": getattr(mod, "SPECIALISTS", []),
            "file": str(f),
        }
    except Exception as e:
        return {"name": company_id, "description": f"Erro ao carregar: {e}", "file": str(f)}


def install_middleware_plugin(plugin_id: str) -> bool:
    """Instala um plugin de middleware built-in no diretorio do usuario."""
    MIDDLEWARES_DIR.mkdir(parents=True, exist_ok=True)
    target = MIDDLEWARES_DIR / f"{plugin_id}.py"

    if target.exists():
        console.print(f"  [dim]  {plugin_id}: ja instalado[/dim]")
        return False

    builtin = MIDDLEWARES_BUILTIN / f"{plugin_id}.py"
    if builtin.exists():
        shutil.copy2(str(builtin), str(target))
        meta = get_middleware_meta(plugin_id)
        name = meta.get("name", plugin_id) if meta else plugin_id
        console.print(f"  [green]  + {name} (middleware)[/green]")
        return True

    console.print(f"  [yellow]  ? {plugin_id}: plugin de middleware nao encontrado[/yellow]")
    return False


def get_middleware_meta(middleware_id: str) -> dict | None:
    """Verifica se um middleware esta instalado e retorna metadados."""
    f = MIDDLEWARES_DIR / f"{middleware_id}.py"
    if not f.exists():
        return None
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(middleware_id, f)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return {
            "name": getattr(mod, "NAME", middleware_id),
            "description": getattr(mod, "DESCRIPTION", ""),
            "middleware_type": getattr(mod, "MIDDLEWARE_TYPE", "unknown"),
            "runs_when": getattr(mod, "RUNS_WHEN", "manual"),
            "file": str(f),
        }
    except Exception as e:
        return {"name": middleware_id, "description": f"Erro ao carregar: {e}", "file": str(f)}


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


def uninstall_company_plugin(plugin_id: str) -> bool:
    """Remove um plugin de empresa do diretorio do usuario."""
    target = COMPANIES_DIR / f"{plugin_id}.py"
    if not target.exists():
        console.print(f"[yellow]Empresa '{plugin_id}' nao instalada.[/yellow]")
        return False
    target.unlink()
    console.print(f"[green]Empresa '{plugin_id}' removida.[/green]")
    return True


def uninstall_middleware_plugin(plugin_id: str) -> bool:
    """Remove um plugin de middleware do diretorio do usuario."""
    target = MIDDLEWARES_DIR / f"{plugin_id}.py"
    if not target.exists():
        console.print(f"[yellow]Middleware '{plugin_id}' nao instalado.[/yellow]")
        return False
    target.unlink()
    console.print(f"[green]Middleware '{plugin_id}' removido.[/green]")
    return True
