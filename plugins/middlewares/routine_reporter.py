"""
Routine Reporter — Gera relatorio ao final de uma rotina.

Exibe no console um resumo com:
  - Nome da rotina
  - Tempo inicial e final
  - Duracao total
  - Middlewares utilizados
  - Status
  - Caminho de saida (output)
"""

from datetime import datetime

NAME = "Routine Reporter"
DESCRIPTION = "Gera relatorio resumido de uma rotina ao final (tempo, middlewares, status)"
MIDDLEWARE_TYPE = "routine"
RUNS_WHEN = "end"

_start_time_str = ""
_routines: list = []


def ROUTINE_START(routine_name: str, context: dict) -> None:
    """Registra inicio da rotina."""
    global _start_time_str
    _start_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ROUTINE_END(routine_name: str, context: dict) -> None:
    """Imprime relatorio no console."""
    global _start_time_str
    if not _start_time_str:
        _start_time_str = "N/A"

    end_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    duration = context.get("duration_seconds", 0)
    status = context.get("status", "completed")
    config = context.get("config_used", "N/A")
    middlewares = context.get("middlewares_used", [])
    output_path = context.get("output_path", "console")

    mins = int(duration // 60)
    secs = int(duration % 60)

    status_icon = "OK" if status == "completed" else "ERRO"

    print(f"\n{'='*50}")
    print(f"  RELATORIO DA ROTINA")
    print(f"{'='*50}")
    print(f"  Rotina:    {routine_name}")
    print(f"  Config:    {config}")
    print(f"  Inicio:    {_start_time_str}")
    print(f"  Fim:       {end_time_str}")
    print(f"  Duracao:   {mins}m {secs}s ({duration:.1f}s)")
    print(f"  Status:    {status} [{status_icon}]")
    print(f"  Middlewares: {', '.join(middlewares) if middlewares else 'nenhum'}")
    print(f"  Saida:     {output_path}")
    print(f"{'='*50}\n")

    _start_time_str = ""
