"""
Sistema de Departamentos/Equipes.

Departamentos sao conjuntos de specialists que podem:
  1. Existir isoladamente: `myc agent department marketing "faça campanha"`
  2. Estar dentro de uma empresa: vinculados a um company plugin
  3. Ter middlewares proprios (pre/post prompt modifiers)

Cada departamento e um arquivo .py em ~/.myc/agents/departments/ que exporta:
  - NAME: str                    — nome do departamento
  - DESCRIPTION: str             — descricao curta
  - SPECIALISTS: list[str]       — IDs de specialists neste departamento
  - MIDDLEWARES: list[str]       — IDs de middlewares aplicados a este depto
  - PARENT_COMPANY: str | None   — ID da empresa pai (None = independente)
  - ROLE: str                    — papel/descricao detalhada (prompt base)
  - DEPARTMENT_CONTEXT() -> str  — contexto extra (opcional)

Um departamento funciona como um mini-agente multi-papel:
  - O prompt do usuario e enviado para cada specialist (com contexto do depto)
  - Middlewares pre sao aplicados antes de cada specialist
  - Middlewares pos sao aplicados na resposta de cada specialist
  - As respostas sao consolidadas
"""

import importlib.util
import json
import shutil
from pathlib import Path
from typing import Any

from rich.console import Console

console = Console()

DEPARTMENTS_DIR = Path.home() / ".myc" / "agents" / "departments"
PLUGINS_DIR = Path.home() / ".myc" / "agents" / "plugins"
MIDDLEWARES_DIR = Path.home() / ".myc" / "agents" / "middlewares"


def _get_pkg_dir(subfolder: str) -> Path:
    """Retorna o diretorio built-in de um subfolder de plugins."""
    import sys
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / "plugins" / subfolder
    return Path(__file__).parent.parent / "plugins" / subfolder


MYC_DEPARTMENTS = _get_pkg_dir("departments")
MYC_MIDDLEWARES = _get_pkg_dir("middlewares")


def _ensure_dir() -> None:
    DEPARTMENTS_DIR.mkdir(parents=True, exist_ok=True)


def _load_module(filepath: Path) -> Any | None:
    spec = importlib.util.spec_from_file_location(filepath.stem, filepath)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _auto_install(dept_id: str) -> Path | None:
    """Tenta instalar o departamento do builtin se nao existir."""
    _ensure_dir()
    target = DEPARTMENTS_DIR / f"{dept_id}.py"
    if target.exists():
        return target

    builtin = MYC_DEPARTMENTS / f"{dept_id}.py"
    if builtin.exists():
        shutil.copy2(str(builtin), str(target))
        return target
    return None


def list_departments(company_id: str | None = None) -> list:
    """Lista todos os departamentos disponiveis.

    Se company_id for fornecido, filtra apenas os departamentos daquela empresa.
    """
    _ensure_dir()
    depts = []

    # Instala builtins faltantes
    for f in MYC_DEPARTMENTS.glob("*.py"):
        if f.stem.startswith("_"):
            continue
        _auto_install(f.stem)

    for f in DEPARTMENTS_DIR.glob("*.py"):
        if f.stem.startswith("_"):
            continue
        try:
            mod = _load_module(f)
            if not mod or not hasattr(mod, "NAME"):
                continue

            parent = getattr(mod, "PARENT_COMPANY", None)
            if company_id and parent != company_id:
                continue

            depts.append({
                "id": f.stem,
                "name": getattr(mod, "NAME", f.stem),
                "description": getattr(mod, "DESCRIPTION", ""),
                "specialists": getattr(mod, "SPECIALISTS", []),
                "middlewares": getattr(mod, "MIDDLEWARES", []),
                "parent_company": parent,
                "file": str(f),
            })
        except Exception as e:
            depts.append({
                "id": f.stem,
                "name": f"[ERRO] {f.name}",
                "description": str(e),
                "parent_company": None,
                "specialists": [],
                "middlewares": [],
            })

    return depts


def get_department_context(dept_id: str) -> str | None:
    """Retorna o contexto completo de um departamento com middlewares aplicados."""
    dept_file = DEPARTMENTS_DIR / f"{dept_id}.py"
    if not dept_file.exists():
        dept_file = _auto_install(dept_id)
    if not dept_file:
        return None

    try:
        mod = _load_module(dept_file)
        if not mod:
            return None

        parts = []

        # Contexto do departamento
        role = getattr(mod, "ROLE", "")
        name = getattr(mod, "NAME", dept_id)
        if role:
            parts.append(f"# Departamento: {name}\n\n{role}")

        # Contexto extra
        ctx_fn = getattr(mod, "DEPARTMENT_CONTEXT", None)
        if ctx_fn:
            parts.append(ctx_fn())

        # Specialists disponiveis
        specialists = getattr(mod, "SPECIALISTS", [])
        if specialists:
            parts.append(f"\n## Especialistas disponiveis: {', '.join(specialists)}")

        # Middlewares pre aplicados
        middlewares = getattr(mod, "MIDDLEWARES", [])
        if middlewares:
            pre_mw = _get_middleware_config([m for m in middlewares if m in ("prompt_enhancer", "security_checker_pre")])
            if pre_mw:
                parts.append(f"\n## Regras adicionais (middlewares):\n{pre_mw}")

        return "\n\n".join(parts)

    except Exception as e:
        console.print(f"[red]Erro ao carregar departamento {dept_id}: {e}[/red]")
        return None


def _get_middleware_config(middleware_ids: list[str]) -> str | None:
    """Carrega config de middlewares de um departamento."""
    parts = []
    for mw_id in middleware_ids:
        mw_file = MIDDLEWARES_DIR / f"{mw_id}.py"
        if not mw_file.exists():
            mw_file = MYC_MIDDLEWARES / f"{mw_id}.py"
            if mw_file.exists():
                shutil.copy2(str(mw_file), str(MIDDLEWARES_DIR / f"{mw_id}.py"))

        if mw_file.exists():
            try:
                mod = _load_module(mw_file)
                if mod:
                    name = getattr(mod, "NAME", mw_id)
                    desc = getattr(mod, "DESCRIPTION", "")
                    parts.append(f"- **{name}**: {desc}")
            except Exception:
                pass

    return "\n".join(parts) if parts else None


def create_department_wizard() -> None:
    """Wizard para criar departamento/quipe."""
    import questionary

    console.print("\n[bold cyan]Criar Departamento/quipe[/bold cyan]")

    dept_id = questionary.text(
        "ID do departamento (ex: marketing, dev_frontend):",
        validate=lambda x: (len(x) > 0 and " " not in x) or "Sem espacos",
    ).ask()
    if not dept_id:
        return

    name = questionary.text("Nome:", default=dept_id.replace("_", " ").title()).ask() or dept_id
    description = questionary.text("Descricao:").ask() or ""
    role = questionary.text(
        "Papel do departamento (prompt base, o que esse depto faz):",
        default="",
    ).ask() or ""

    # Empresa pai
    parent_company = questionary.text(
        "ID da empresa pai (deixe vazio = independente):",
        default="",
    ).ask() or None

    # Specialists
    from myc.agent_plugins import list_plugins
    available = listPlugins()
    specialists = []
    if available:
        console.print("\nSelecione os specialists deste departamento:")
        choices = [
            questionary.Choice(f"{s['name']} ({s['id']})", value=s["id"])
            for s in available
        ]
        specialists = questionary.checkbox(
            "Especialistas:",
            choices=choices,
        ).ask() or []

    # Middlewares
    pre_mw_ids = []
    console.print("\nSelecione middlewares pre-prompt (modificam entrada):")
    pre_choices = [
        questionary.Choice("Prompt Enhancer - melhora estrutura do prompt", value="prompt_enhancer"),
        questionary.Choice("Security Check - adiciona checklist seguranca", value="security_checker_pre"),
    ]
    pre_mw_ids = questionary.checkbox(
        "Middlewares PRE:",
        choices=pre_choices,
    ).ask() or []

    # Monta SPECIALISTS + MIDDLEWARES
    all_mw = list(set(pre_mw_ids))  # middlewares separados dos specialists

    template = f'''"""
Departamento: {name}
Descricao: {description}
Especialistas: {len(specialists)}
'''
    if parent_company:
        template += f"Empresa pai: {parent_company}\n"
    template += f'''"""

NAME = "{name}"
DESCRIPTION = "{description}"
ROLE = """{role}"""
SPECIALISTS = {json.dumps(specialists, indent=4, ensure_ascii=False)}
MIDDLEWARES = {json.dumps(all_mw, indent=4, ensure_ascii=False)}
PARENT_COMPANY = {json.dumps(parent_company)}

def DEPARTMENT_CONTEXT():
    return "{description}"
'''

    _ensure_dir()
    target = DEPARTMENTS_DIR / f"{dept_id}.py"
    target.write_text(template, encoding="utf-8")
    console.print(f"[green]Departamento criado em {target}[/green]")


def launch_department(dept_id: str, query: str) -> int:
    """Lanca um departamento com uma query.

    Coleta contexto de todos os specialists, aplica middlewares,
    e gera o prompt com o contexto do departamento.
    """
    from myc.agent import launch_agent

    context = get_department_context(dept_id)
    if not context:
        console.print(f"[red]Departamento '{dept_id}' nao encontrado.[/red]")
        return 1

    # Aplica middleware pre na query
    dept_file = DEPARTMENTS_DIR / f"{dept_id}.py"
    if dept_file.exists():
        try:
            mod = _load_module(dept_file)
            if mod:
                middlewares = getattr(mod, "MIDDLEWARES", [])
                for mw_id in middlewares:
                    mw_file = MIDDLEWARES_DIR / f"{mw_id}.py"
                    if mw_file.exists():
                        try:
                            mw_mod = _load_module(mw_file)
                            if mw_mod:
                                fn = getattr(mw_mod, "PROMPT_MODIFY", None)
                                if fn:
                                    query = fn(query, {})
                        except Exception:
                            pass
        except Exception:
            pass

    # Monta o prompt final
    final_prompt = f"{context}\n\n---\n\n## Tarefa\n\n{query}"

    console.print(f"\n[bold]Departamento: {dept_id}[/bold]")
    console.print(f"[dim]Query ({len(query)} chars)[/dim]")

    # Abre um editor temporario ou imprime
    console.print(final_prompt)
    return 0
