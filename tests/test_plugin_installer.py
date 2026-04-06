"""Unit tests for myc.plugin_installer module."""

from pathlib import Path
from unittest.mock import patch

from myc.plugin_installer import (
    get_plugin_meta,
    install_plugin,
    install_company_plugin,
    install_middleware_plugin,
    get_company_meta,
    get_middleware_meta,
    uninstall_plugin,
    uninstall_company_plugin,
    uninstall_middleware_plugin,
    install_plugin_from_file,
)


class TestGetPluginMeta:
    def test_not_installed(self, config_path):
        result = get_plugin_meta("nonexistent")
        assert result is None

    def test_installed_returns_meta(self, config_path, sample_plugin_content):
        from myc.plugin_installer import PLUGINS_DIR
        f = PLUGINS_DIR / "meta_test.py"
        f.write_text(sample_plugin_content, encoding="utf-8")
        meta = get_plugin_meta("meta_test")
        assert meta is not None
        assert meta["name"] == "Test Specialist"
        assert "PRE_LAUNCH" in meta["hooks"]
        assert "CONTEXT" in meta["hooks"]
        assert "POST_LAUNCH" in meta["hooks"]


class TestInstallPlugin:
    def test_install_from_generators(self, config_path):
        """Without builtin files, install should return False for unknown plugin."""
        result = install_plugin("nonexistent_plugin_xyz")
        assert result is False


class TestInstallCompanyPlugin:
    def test_not_found(self, config_path):
        result = install_company_plugin("nonexistent_company")
        assert result is False

    def test_already_installed(self, config_path):
        from myc.plugin_installer import COMPANIES_DIR
        f = COMPANIES_DIR / "already_installed.py"
        f.write_text("NAME = 'x'\nDESCRIPTION = 'y'", encoding="utf-8")
        result = install_company_plugin("already_installed")
        assert result is False


class TestInstallMiddlewarePlugin:
    def test_not_found(self, config_path):
        result = install_middleware_plugin("nonexistent_mw")
        assert result is False


class TestGetCompanyMeta:
    def test_not_installed(self, config_path):
        result = get_company_meta("missing")
        assert result is None

    def test_returns_meta(self, config_path, sample_company_content):
        from myc.plugin_installer import COMPANIES_DIR
        f = COMPANIES_DIR / "meta_company.py"
        f.write_text(sample_company_content, encoding="utf-8")
        meta = get_company_meta("meta_company")
        assert meta is not None
        assert meta["name"] == "Test Company"


class TestGetMiddlewareMeta:
    def test_not_installed(self, config_path):
        result = get_middleware_meta("missing_mw")
        assert result is None

    def test_returns_meta(self, config_path):
        from myc.plugin_installer import MIDDLEWARES_DIR
        f = MIDDLEWARES_DIR / "test_mw.py"
        f.write_text(
            'NAME = "Test MW"\nDESCRIPTION = "Test middleware"\nMIDDLEWARE_TYPE = "pre"\nRUNS_WHEN = "manual"',
            encoding="utf-8",
        )
        meta = get_middleware_meta("test_mw")
        assert meta is not None
        assert meta["name"] == "Test MW"
        assert meta["middleware_type"] == "pre"
        assert meta["runs_when"] == "manual"


class TestUninstallPlugin:
    def test_not_installed(self, config_path):
        with patch("myc.plugin_installer.console"):
            result = uninstall_plugin("never_existed")
        assert result is False

    def test_uninstall_existing(self, config_path):
        from myc.plugin_installer import PLUGINS_DIR
        f = PLUGINS_DIR / "to_remove.py"
        f.write_text("NAME = 'remove me'", encoding="utf-8")
        with patch("myc.plugin_installer.console"):
            result = uninstall_plugin("to_remove")
        assert result is True
        assert not f.exists()


class TestUninstallCompanyPlugin:
    def test_not_installed(self, config_path):
        with patch("myc.plugin_installer.console"):
            result = uninstall_company_plugin("no_company")
        assert result is False

    def test_uninstall_existing(self, config_path):
        from myc.plugin_installer import COMPANIES_DIR
        f = COMPANIES_DIR / "to_remove_comp.py"
        f.write_text("NAME = 'remove'", encoding="utf-8")
        with patch("myc.plugin_installer.console"):
            result = uninstall_company_plugin("to_remove_comp")
        assert result is True
        assert not f.exists()


class TestUninstallMiddlewarePlugin:
    def test_not_installed(self, config_path):
        with patch("myc.plugin_installer.console"):
            result = uninstall_middleware_plugin("no_mw")
        assert result is False

    def test_uninstall_existing(self, config_path):
        from myc.plugin_installer import MIDDLEWARES_DIR
        f = MIDDLEWARES_DIR / "to_remove_mw.py"
        f.write_text("NAME = 'rm'", encoding="utf-8")
        with patch("myc.plugin_installer.console"):
            result = uninstall_middleware_plugin("to_remove_mw")
        assert result is True
        assert not f.exists()


class TestInstallPluginFromFile:
    def test_invalid_path(self, config_path):
        result = install_plugin_from_file("/nonexistent/file.py")
        assert result is False

    def test_valid_file(self, config_path):
        src = config_path / "source_plugin.py"
        src.write_text("NAME = 'from file'", encoding="utf-8")
        with patch("myc.plugin_installer.console"):
            result = install_plugin_from_file(str(src))
        assert result is True
        from myc.plugin_installer import PLUGINS_DIR
        assert (PLUGINS_DIR / "source_plugin.py").exists()

    def test_non_py_extension(self, config_path):
        src = config_path / "source_plugin.txt"
        src.write_text("hello", encoding="utf-8")
        with patch("myc.plugin_installer.console"):
            result = install_plugin_from_file(str(src))
        assert result is False
