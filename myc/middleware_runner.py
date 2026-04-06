"""
Middleware Runner — executa middlewares em cadeia para rotinas MYC.

Hooks suportados:
  - PROMPT_MODIFY:  modifica o prompt antes de enviar ao agente
  - OUTPUT_MODIFY:  modifica a saida depois da execucao
  - ROUTINE_START:  chamado ao iniciar uma rotina
  - ROUTINE_END:    chamado ao finalizar uma rotina
  - ERROR:          chamado quando ocorre erro

Convenções de funcao em middlewares:
  - Padrão:      PROMPT_MODIFY(text, profile) / OUTPUT_MODIFY(text, profile)
  - Alternativo: process_prompt(agent_profile, original_prompt) /
                 process_output(agent_profile, original_output)
"""

import importlib.util
import shutil
import time
from pathlib import Path
from typing import Any

from rich.console import Console

console = Console()

MW_DIR_USER = Path.home() / ".myc" / "agents" / "middlewares"
MW_DIR_BUILTIN = Path(__file__).parent.parent / "plugins" / "middlewares"


def list_all_middlewares() -> list[dict]:
    """Lista todos os middlewares (user + builtin) com metadados."""
    # Auto-instala builtins
    MW_DIR_USER.mkdir(parents=True, exist_ok=True)
    for f in MW_DIR_BUILTIN.glob("*.py"):
        if f.stem.startswith("_"):
            continue
        target = MW_DIR_USER / f.name
        if not target.exists():
            shutil.copy2(str(f), str(target))

    result = []
    for f in MW_DIR_USER.glob("*.py"):
        if f.stem.startswith("_"):
            continue
        try:
            mod = _load_module(f)
            if mod:
                result.append({
                    "id": f.stem,
                    "name": getattr(mod, "NAME", f.stem),
                    "description": getattr(mod, "DESCRIPTION", ""),
                    "type": getattr(mod, "MIDDLEWARE_TYPE", "?"),
                    "file": str(f),
                })
        except Exception as e:
            result.append({
                "id": f.stem,
                "name": f"[ERRO] {f.name}",
                "description": str(e),
                "type": "?",
                "file": str(f),
            })
    return result


def _load_module(filepath: Path) -> Any | None:
    """Carrega modulo Python de um arquivo."""
    spec = importlib.util.spec_from_file_location(filepath.stem, filepath)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _find_middleware_file(mw_id: str) -> Path | None:
    """Busca arquivo do middleware no user dir, fallback builtin."""
    mw_dir = Path(__file__).parent.parent / "plugins" / "middlewares"
    user_file = MW_DIR_USER / f"{mw_id}.py"
    if user_file.exists():
        return user_file
    builtin = mw_dir / f"{mw_id}.py"
    if builtin.exists():
        if not user_file.exists():
            MW_DIR_USER.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(builtin), str(user_file))
        return user_file
    return None


class MiddlewareRunner:
    """Executa middlewares em cadeia para uma rotina."""

    def __init__(self, config_id: str, agent_profile: dict | None = None):
        """
        Args:
            config_id: ID da configuracao customizada
            agent_profile: Perfil do agente (dict) para contexto dos middlewares
        """
        from myc.custom_config import get_custom_config

        self.config_id = config_id
        self.agent_profile = agent_profile or {}
        cfg = get_custom_config(config_id)
        self.middleware_ids = cfg.get("middlewares", []) if cfg else []
        self.variables = cfg.get("variables", {}) if cfg else {}
        self._loaded: dict[str, Any] = {}
        self._start_time: float = 0
        self._routine_name: str = ""

    def load_all(self) -> None:
        """Carrega todos os middlewares da config."""
        for mw_id in self.middleware_ids:
            self.load_middleware(mw_id)

    def load_middleware(self, mw_id: str) -> Any | None:
        """Carrega um middleware pelo ID."""
        if mw_id in self._loaded:
            return self._loaded[mw_id]

        filepath = _find_middleware_file(mw_id)
        if not filepath:
            console.print(f"[yellow]Middleware '{mw_id}' nao encontrado, ignorando.[/yellow]")
            return None

        mod = _load_module(filepath)
        if mod:
            self._loaded[mw_id] = mod
        return mod

    def modify_prompt(self, prompt: str) -> str:
        """Aplica PROMPT_MODIFY de todos os middlewares em cadeia."""
        result = prompt
        for mw_id in self.middleware_ids:
            mod = self.load_middleware(mw_id)
            if not mod:
                continue

            modified = None
            # Tenta PROMPT_MODIFY(padrao)
            if hasattr(mod, "PROMPT_MODIFY"):
                fn = getattr(mod, "PROMPT_MODIFY")
                modified = fn(result, self.agent_profile)
            # Tenta process_prompt(alternativo)
            elif hasattr(mod, "process_prompt"):
                fn = getattr(mod, "process_prompt")
                modified = fn(self.agent_profile, result)

            if modified is not None:
                result = modified
                console.print(f"[dim][MW] {mw_id}: prompt modificado[/dim]")

        return result

    def modify_output(self, output: str) -> str:
        """Aplica OUTPUT_MODIFY de todos os middlewares em cadeia."""
        result = output
        for mw_id in self.middleware_ids:
            mod = self.load_middleware(mw_id)
            if not mod:
                continue

            modified = None
            # Tenta OUTPUT_MODIFY(padrao)
            if hasattr(mod, "OUTPUT_MODIFY"):
                fn = getattr(mod, "OUTPUT_MODIFY")
                modified = fn(result, self.agent_profile)
            # Tenta process_output(alternativo)
            elif hasattr(mod, "process_output"):
                fn = getattr(mod, "process_output")
                modified = fn(self.agent_profile, result)

            if modified is not None:
                result = modified
                console.print(f"[dim][MW] {mw_id}: output modificado[/dim]")

        return result

    def notify_start(self, routine_name: str, context: dict | None = None) -> None:
        """Avisa os middlewares que a rotina comecou."""
        self._start_time = time.time()
        self._routine_name = routine_name

        for mw_id in self.middleware_ids:
            mod = self.load_middleware(mw_id)
            if not mod:
                continue
            if hasattr(mod, "ROUTINE_START"):
                try:
                    getattr(mod, "ROUTINE_START")(
                        routine_name,
                        {**self.agent_profile, **(context or {})},
                    )
                except Exception as e:
                    console.print(f"[yellow][MW] {mw_id} ROUTINE_START falhou: {e}[/yellow]")

    def notify_end(self, status: str = "completed", context: dict | None = None) -> float:
        """
        Avisa os middlewares que a rotina terminou.
        Retorna duracao em segundos.
        """
        duration = time.time() - self._start_time if self._start_time else 0

        end_context = {
            **(self.agent_profile),
            "duration_seconds": duration,
            "status": status,
            "routine_name": self._routine_name,
            **(context or {}),
        }

        for mw_id in self.middleware_ids:
            mod = self.load_middleware(mw_id)
            if not mod:
                continue
            if hasattr(mod, "ROUTINE_END"):
                try:
                    getattr(mod, "ROUTINE_END")(
                        self._routine_name,
                        end_context,
                    )
                except Exception as e:
                    console.print(f"[yellow][MW] {mw_id} ROUTINE_END falhou: {e}[/yellow]")

        return duration

    def handle_error(self, error: Exception, context: dict | None = None) -> None:
        """Avisa os middlewares sobre um erro."""
        err_context = {
            **(self.agent_profile),
            "error": str(error),
            "error_type": type(error).__name__,
            "routine_name": self._routine_name,
            **(context or {}),
        }

        for mw_id in self.middleware_ids:
            mod = self.load_middleware(mw_id)
            if not mod:
                continue
            if hasattr(mod, "ERROR"):
                try:
                    getattr(mod, "ERROR")(err_context)
                except Exception as e2:
                    console.print(f"[yellow][MW] {mw_id} ERROR falhou: {e2}[/yellow]")
