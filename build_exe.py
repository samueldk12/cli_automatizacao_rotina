"""
Build script — gera executavel via PyInstaller.

Uso:
    python build_exe.py

Requer PyInstaller:
    pip install pyinstaller
"""

import platform
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

BINARY = "myc.exe" if platform.system() == "Windows" else "myc"


def ensure_pyinstaller() -> None:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            stdout=sys.stdout,
        )


def build() -> None:
    ensure_pyinstaller()
    spec = HERE / "myc.spec"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec),
    ]

    print("Executando PyInstaller...")
    subprocess.check_call(cmd)

    exe = HERE / "dist" / BINARY
    if exe.exists():
        size = exe.stat().st_size / 1024 / 1024
        print(f"\n[OK] Exe gerado: {exe}")
        print(f"     Tamanho: {size:.1f} MB")
    else:
        print("\n[ERRO] Falha ao gerar o executavel.")
        sys.exit(1)


if __name__ == "__main__":
    build()
