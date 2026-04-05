"""
Build script — gera myc.exe via PyInstaller.

Uso:
    python build_exe.py

Requer PyInstaller:
    pip install pyinstaller
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


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

    exe = HERE / "dist" / "myc.exe"
    if exe.exists():
        print(f"\n[OK] Exe gerado: {exe}")
        print(f"     Tamanho: {exe.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print("\n[ERRO] Falha ao gerar o executavel.")
        sys.exit(1)


if __name__ == "__main__":
    build()
