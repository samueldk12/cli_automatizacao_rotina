import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

from myc.config import load_config
from myc.monitor import Monitor, get_monitor

DAYS_PT = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]

DAYS_DISPLAY = {
    "segunda": "Segunda-feira",
    "terca": "Terça-feira",
    "quarta": "Quarta-feira",
    "quinta": "Quinta-feira",
    "sexta": "Sexta-feira",
    "sabado": "Sábado",
    "domingo": "Domingo",
}


def find_browser(browser: str = "chrome") -> str:
    """Localiza o executável do navegador."""
    config = load_config()
    custom = config.get("settings", {}).get("chrome_path", "")
    if custom and Path(custom).exists():
        return custom

    if browser in ("chrome", "google-chrome"):
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            str(Path.home() / "AppData/Local/Google/Chrome/Application/chrome.exe"),
        ]
        for c in candidates:
            if Path(c).exists():
                return c

    if browser in ("edge", "msedge"):
        edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        if Path(edge).exists():
            return edge

    if browser == "firefox":
        ff = r"C:\Program Files\Mozilla Firefox\firefox.exe"
        if Path(ff).exists():
            return ff

    # Fallback: espera que esteja no PATH
    return browser


def _try_reposition_window(monitor: Monitor, delay: float = 2.0) -> None:
    """
    Tenta mover a janela do Chrome mais recente para o monitor correto via PowerShell.
    Necessário quando Chrome já está aberto (ignora --window-position no processo existente).
    """
    ps_script = f"""
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinAPI {{
    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
}}
"@
Start-Sleep -Milliseconds {int(delay * 1000)}
$chrome = Get-Process chrome -ErrorAction SilentlyContinue | Sort-Object StartTime -Descending | Select-Object -First 1
if ($chrome -and $chrome.MainWindowHandle -ne 0) {{
    [WinAPI]::MoveWindow($chrome.MainWindowHandle, {monitor.x}, {monitor.y}, {monitor.width}, {monitor.height}, $true)
    [WinAPI]::ShowWindow($chrome.MainWindowHandle, 3)
}}
"""
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
    except Exception:
        pass


def open_url_on_monitor(
    url: str,
    monitor_index: int = 0,
    new_window: bool = True,
    browser: str = "chrome",
) -> None:
    """Abre uma URL em um monitor específico."""
    exe = find_browser(browser)
    monitor = get_monitor(monitor_index)

    cmd = [exe]
    if new_window:
        cmd.append("--new-window")

    # --window-position funciona quando Chrome não está aberto ainda.
    # Quando já está aberto, usamos PowerShell para reposicionar.
    cmd += [
        f"--window-position={monitor.x},{monitor.y}",
        f"--window-size={monitor.width},{monitor.height}",
    ]
    cmd.append(url)

    subprocess.Popen(cmd)

    # Aguarda janela abrir e tenta reposicionar via API Windows
    _try_reposition_window(monitor, delay=2.0)

    # Delay entre janelas para evitar conflito de foco
    time.sleep(0.8)


def open_app(path: str, args: List[str] = None) -> None:
    """Abre um aplicativo."""
    cmd = [path] + (args or [])
    subprocess.Popen(cmd, shell=True)


def run_command(group: str, subcommand: str, day: Optional[str] = None) -> bool:
    """
    Executa um comando registrado.

    Args:
        group:      Nome do grupo (ex: "estudar")
        subcommand: Nome do subcomando (ex: "visao-computacional")
        day:        Dia da semana opcional (ex: "segunda")

    Returns:
        True se executado com sucesso, False se não encontrado.
    """
    config = load_config()
    group_data = config.get("commands", {}).get(group)
    if not group_data:
        return False

    sub_data = group_data.get("subcommands", {}).get(subcommand)
    if not sub_data:
        return False

    # Valida filtro de dia
    allowed_days: List[str] = sub_data.get("days", [])
    if day and allowed_days and day not in allowed_days:
        days_str = ", ".join(DAYS_DISPLAY.get(d, d) for d in allowed_days)
        print(f"Comando '{subcommand}' não disponível para '{DAYS_DISPLAY.get(day, day)}'.")
        print(f"Dias configurados: {days_str}")
        return False

    actions = sub_data.get("actions", [])
    if not actions:
        print(f"Comando '{group} {subcommand}' não possui ações configuradas.")
        return True

    for action in actions:
        atype = action.get("type", "browser")
        if atype in ("browser", "url"):
            open_url_on_monitor(
                url=action.get("url", ""),
                monitor_index=action.get("monitor", 0),
                new_window=action.get("new_window", True),
                browser=action.get("browser", "chrome"),
            )
        elif atype == "app":
            open_app(action.get("path", ""), action.get("args", []))

    return True


def list_day_commands(day: str, config: dict) -> List[tuple]:
    """Retorna todos os comandos disponíveis para um dia."""
    results = []
    for group_name, group_data in config.get("commands", {}).items():
        for sub_name, sub_data in group_data.get("subcommands", {}).items():
            days = sub_data.get("days", [])
            if not days or day in days:
                results.append((group_name, sub_name, sub_data))
    return results
