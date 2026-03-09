import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Set

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

_NO_WINDOW = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


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

    return browser


def _get_chrome_handles() -> Set[int]:
    """Retorna o conjunto de handles de janelas Chrome visíveis no momento."""
    try:
        result = subprocess.run(
            [
                "powershell", "-NoProfile", "-NonInteractive", "-Command",
                "Get-Process chrome -ErrorAction SilentlyContinue"
                " | Where-Object { $_.MainWindowHandle -ne 0 }"
                " | ForEach-Object { $_.MainWindowHandle.ToInt64() }",
            ],
            capture_output=True,
            text=True,
            creationflags=_NO_WINDOW,
        )
        handles: Set[int] = set()
        for line in result.stdout.strip().splitlines():
            try:
                handles.add(int(line.strip()))
            except ValueError:
                pass
        return handles
    except Exception:
        return set()


def _reposition_new_window(before_handles: Set[int], monitor: Monitor) -> None:
    """
    Aguarda uma *nova* janela Chrome surgir (não presente em before_handles)
    e a move para o monitor especificado via Win32 API.
    Bloqueante — retorna quando a janela foi movida ou após timeout (~8 s).
    """
    if before_handles:
        before_ps = "@(" + ", ".join(str(h) for h in before_handles) + ")"
    else:
        before_ps = "@()"

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
    [DllImport("user32.dll")]
    public static extern bool RedrawWindow(IntPtr hWnd, IntPtr lprcUpdate, IntPtr hrgnUpdate, uint flags);
}}
"@

$before = {before_ps}
$newHwnd = [IntPtr]::Zero

# Poll ate 8 s (80 x 100 ms)
for ($i = 0; $i -lt 80; $i++) {{
    Start-Sleep -Milliseconds 100
    $procs = Get-Process chrome -ErrorAction SilentlyContinue | Where-Object {{ $_.MainWindowHandle -ne 0 }}
    foreach ($p in $procs) {{
        $h = $p.MainWindowHandle.ToInt64()
        if ($before -notcontains $h) {{
            $newHwnd = $p.MainWindowHandle
            break
        }}
    }}
    if ($newHwnd -ne [IntPtr]::Zero) {{ break }}
}}

if ($newHwnd -ne [IntPtr]::Zero) {{
    Start-Sleep -Milliseconds 400
    # 1) Minimiza para forcar o Chrome a sair do estado atual
    [WinAPI]::ShowWindow($newHwnd, 6)
    Start-Sleep -Milliseconds 150
    # 2) Move para o monitor correto enquanto minimizado
    [WinAPI]::MoveWindow($newHwnd, {monitor.x}, {monitor.y}, {monitor.width}, {monitor.height}, $true)
    Start-Sleep -Milliseconds 150
    # 3) Restaura e maximiza — força a GPU a repintar no novo monitor
    [WinAPI]::ShowWindow($newHwnd, 9)
    Start-Sleep -Milliseconds 100
    [WinAPI]::ShowWindow($newHwnd, 3)
    [WinAPI]::SetForegroundWindow($newHwnd)
    # 4) Forca repaint completo (RDW_INVALIDATE | RDW_UPDATENOW | RDW_ALLCHILDREN = 0x0181)
    [WinAPI]::RedrawWindow($newHwnd, [IntPtr]::Zero, [IntPtr]::Zero, 0x0181)
}}
"""
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            creationflags=_NO_WINDOW,
        )
    except Exception:
        pass


def open_url_on_monitor(
    url: str,
    monitor_index: int = 0,
    new_window: bool = True,
    browser: str = "chrome",
) -> None:
    """Abre uma URL em um monitor específico e garante que a janela esteja no lugar certo."""
    exe = find_browser(browser)
    monitor = get_monitor(monitor_index)

    # Captura handles existentes ANTES de abrir o Chrome
    before_handles = _get_chrome_handles()

    cmd = [exe]
    if new_window:
        cmd.append("--new-window")
    # Hint de posição (funciona quando Chrome ainda não está rodando)
    cmd += [
        f"--window-position={monitor.x},{monitor.y}",
        f"--window-size={monitor.width},{monitor.height}",
    ]
    cmd.append(url)
    subprocess.Popen(cmd)

    # Detecta e reposiciona APENAS a janela recém-criada
    _reposition_new_window(before_handles, monitor)


def open_app(path: str, args: List[str] = None) -> None:
    """Abre um aplicativo."""
    cmd = [path] + (args or [])
    subprocess.Popen(cmd, shell=True)


def run_command(group: str, subcommand: str, day: Optional[str] = None) -> bool:
    """
    Executa um comando registrado.

    Args:
        group:      Nome do grupo (ex: "estudar")
        subcommand: Nome do subcomando (ex: "visao")
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
