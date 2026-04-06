"""
Routine Timer — Conta tempo de execucao de rotinas.

No ROUTINE_START, registra o instante inicial.
No ROUTINE_END, calcula duracao e salva no historico.

Uso: adicione "routine_timer" na lista de middlewares da sua config.
"""

import time
from pathlib import Path

NAME = "Routine Timer"
DESCRIPTION = "Conta quanto tempo voce ficou fazendo uma rotina e salva no historico"
MIDDLEWARE_TYPE = "routine"
RUNS_WHEN = "both"

_START_KEY = "_routine_timer_start"


def ROUTINE_START(routine_name: str, context: dict) -> None:
    """Registra o instante de inicio."""
    context[_START_KEY] = time.time()
    print(f"\n[ROTINA TIMER] Iniciando '{routine_name}'...")


def ROUTINE_END(routine_name: str, context: dict) -> None:
    """Calcula duracao e salva no historico."""
    start = context.pop(_START_KEY, None)
    if start is None:
        return

    duration = time.time() - start
    mins = int(duration // 60)
    secs = int(duration % 60)
    print(f"\n[ROTINA TIMER] '{routine_name}' finalizada em {mins}m {secs}s")

    # Salva no historico de rotinas
    from myc.custom_config import record_routine_history

    record_routine_history(
        routine_name=routine_name,
        duration_seconds=duration,
        status=context.get("status", "completed"),
        config_used=context.get("config_used", ""),
        middlewares_used=context.get("middlewares_used", []),
        output_path=context.get("output_path", ""),
    )
