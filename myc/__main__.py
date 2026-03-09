import sys

# Força UTF-8 no stdout/stderr antes de qualquer import de rich/questionary.
# Necessário no Windows (cmd/PowerShell legado) que usa cp1252 por padrão.
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from myc.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
