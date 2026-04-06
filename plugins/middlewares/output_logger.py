"""
Output Logger — Salva logs de saida do agente em arquivo.

No ROUTINE_START, abre arquivo de log.
No PROMPT_MODIFY, registra o prompt enviado.
No OUTPUT_MODIFY, adiciona log da saida.
No ROUTINE_END, fecha o arquivo.

Caminho padrao: ~/.myc/logs/{routine_name}.log
Configuravel: variavel "log_path" na config customizada.
"""

from datetime import datetime
from pathlib import Path

NAME = "Output Logger"
DESCRIPTION = "Registra prompts, saidas e erros de uma rotina em arquivo de log"
MIDDLEWARE_TYPE = "routine"
RUNS_WHEN = "both"

# Estado do modulo para compartilhamento entre hooks
_log_file: str | None = None
_config_variables: dict = {}


def _resolve_log_path(routine_name: str) -> Path:
    """Determina caminho do log."""
    custom_path = _config_variables.get("log_path")
    if custom_path:
        return Path(custom_path).expanduser()
    return Path.home() / ".myc" / "logs" / f"{routine_name}.log"


def ROUTINE_START(routine_name: str, context: dict) -> None:
    """Abre arquivo de log."""
    global _log_file, _config_variables
    _config_variables = context.get("variables", {}) or {}

    log_path = _resolve_log_path(routine_name)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    fh = open(log_path, "a", encoding="utf-8")
    fh.write(f"\n{'='*60}\n")
    fh.write(f"ROTINA: {routine_name}\n")
    fh.write(f"INICIO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    fh.write(f"{'='*60}\n")
    fh.flush()

    _log_file = str(log_path)
    print(f"[OUTPUT LOGGER] Log iniciado em {log_path}")


def PROMPT_MODIFY(prompt: str, profile: dict) -> str:
    """Registra o prompt enviado no log."""
    global _log_file
    if _log_file:
        try:
            with open(_log_file, "a", encoding="utf-8") as fh:
                fh.write(f"\n--- PROMPT ENVIADO ({datetime.now().strftime('%H:%M:%S')}) ---\n")
                # Registra apenas os primeiros 500 chars do prompt
                preview = prompt[:500]
                if len(prompt) > 500:
                    preview += f"\n...(+{len(prompt) - 500} chars)"
                fh.write(preview + "\n")
        except Exception:
            pass
    return prompt


def OUTPUT_MODIFY(output: str, profile: dict) -> str:
    """Registra saida do agente no log."""
    global _log_file
    if _log_file:
        try:
            with open(_log_file, "a", encoding="utf-8") as fh:
                fh.write(f"\n--- SAIDA ({datetime.now().strftime('%H:%M:%S')}) ---\n")
                fh.write(output)
                fh.write("\n")
        except Exception:
            pass
    return output


def ROUTINE_END(routine_name: str, context: dict) -> None:
    """Fecha arquivo de log."""
    global _log_file
    if not _log_file:
        return

    try:
        with open(_log_file, "a", encoding="utf-8") as fh:
            duration = context.get("duration_seconds", 0)
            status = context.get("status", "completed")
            fh.write(f"\n{'='*60}\n")
            fh.write(f"FIM: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            fh.write(f"DURACAO: {duration:.1f}s\n")
            fh.write(f"STATUS: {status}\n")
            fh.write(f"{'='*60}\n")
    except Exception:
        pass

    _log_file = None


def ERROR(context: dict) -> None:
    """Registra erro no log."""
    global _log_file
    if not _log_file:
        return

    try:
        with open(_log_file, "a", encoding="utf-8") as fh:
            fh.write(f"\n[ERRO] {context.get('error_type', 'Exception')}: {context.get('error', 'unknown')}\n")
    except Exception:
        pass
