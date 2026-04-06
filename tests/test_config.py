"""Unit tests for myc.config module."""

import json
from myc.config import load_config, save_config, DEFAULT_CONFIG


class TestDefaultConfig:
    def test_default_config_has_required_keys(self):
        assert "version" in DEFAULT_CONFIG
        assert "settings" in DEFAULT_CONFIG
        assert "commands" in DEFAULT_CONFIG


class TestLoadConfig:
    def test_load_creates_default_when_missing(self, config_path):
        config = load_config()
        assert "version" in config
        assert "commands" in config
        assert "settings" in config

    def test_load_returns_saved_data(self, loaded_config):
        config = load_config()
        assert config["commands"] == loaded_config["commands"]

    def test_load_handles_corrupt_json(self, config_path):
        from myc.config import CONFIG_FILE
        CONFIG_FILE.write_text("not json{{{", encoding="utf-8")
        result = load_config()
        assert "commands" in result
        assert isinstance(result["commands"], dict)


class TestSaveConfig:
    def test_save_and_load_roundtrip(self, config_path):
        new_config = {"version": "2.0", "settings": {}, "commands": {"foo": {"subcommands": {}}}}
        save_config(new_config)
        loaded = load_config()
        assert loaded["version"] == "2.0"
        assert "foo" in loaded["commands"]

    def test_save_creates_directory(self, config_path):
        from myc.config import CONFIG_DIR
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        cfg = {"version": "1.0", "settings": {}, "commands": {}}
        save_config(cfg)
        from myc.config import CONFIG_FILE
        assert CONFIG_FILE.exists()
        data = json.loads(CONFIG_FILE.read_text())
        assert data["version"] == "1.0"

    def test_save_nested_values(self, loaded_config):
        loaded_config["commands"]["new_group"] = {"subcommands": {"a": {"days": [], "actions": []}}}
        save_config(loaded_config)
        reread = load_config()
        assert "new_group" in reread["commands"]
        assert "a" in reread["commands"]["new_group"]["subcommands"]

    def test_save_preserves_utf8(self, config_path):
        cfg = {
            "version": "1.0",
            "settings": {},
            "commands": {
                "grupo": {"description": "Teste com acentos \xe7\xe3\xe0", "subcommands": {}}
            },
        }
        save_config(cfg)
        reread = load_config()
        assert "\xe7\xe3\xe0" in reread["commands"]["grupo"]["description"]
