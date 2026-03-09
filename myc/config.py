import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".myc"
CONFIG_FILE = CONFIG_DIR / "config.json"
BIN_DIR = CONFIG_DIR / "bin"

DEFAULT_CONFIG: dict[str, Any] = {
    "version": "1.0",
    "settings": {
        "chrome_path": "",
        "default_browser": "chrome",
    },
    "commands": {},
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {**DEFAULT_CONFIG, "commands": {}, "settings": {**DEFAULT_CONFIG["settings"]}}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {**DEFAULT_CONFIG, "commands": {}, "settings": {**DEFAULT_CONFIG["settings"]}}


def save_config(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
