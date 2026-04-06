"""Unit tests for myc.agent_plugins module."""

from pathlib import Path
from unittest.mock import patch

from myc.agent_plugins import (
    list_plugins,
    execute_plugins,
    list_companies,
    execute_company_profile,
    _resolve_specialist_context,
)


class TestSpecialistPlugins:
    def test_list_empty(self, config_path):
        plugins = list_plugins()
        assert isinstance(plugins, list)

    def test_list_with_plugin(self, config_path, sample_plugin_content):
        from myc.agent_plugins import PLUGINS_DIR
        plugin_file = PLUGINS_DIR / "test_spec.py"
        plugin_file.write_text(sample_plugin_content, encoding="utf-8")
        plugins = list_plugins()
        ids = [p["id"] for p in plugins]
        assert "test_spec" in ids

    def test_list_plugin_with_error(self, config_path):
        from myc.agent_plugins import PLUGINS_DIR
        bad_file = PLUGINS_DIR / "bad_plugin.py"
        bad_file.write_text("NAME = 'bad'\nraise RuntimeError('broken')", encoding="utf-8")
        plugins = list_plugins()
        ids = [p["id"] for p in plugins]
        assert "bad_plugin" in ids

    def test_execute_plugins_empty_profile(self, config_path):
        result = execute_plugins({"name": "dev", "plugins": []})
        assert result == ""

    def test_execute_plugins_runs_pre_launch(self, config_path, sample_plugin_content):
        from myc.agent_plugins import PLUGINS_DIR
        plugin_file = PLUGINS_DIR / "test_hook.py"
        plugin_file.write_text(sample_plugin_content, encoding="utf-8")
        profile = {"name": "dev", "plugins": ["test_hook"]}
        execute_plugins(profile, "PRE_LAUNCH")
        # Plugin should have been loaded without error

    def test_execute_plugins_returns_context(self, config_path, sample_plugin_content):
        from myc.agent_plugins import PLUGINS_DIR
        plugin_file = PLUGINS_DIR / "test_ctx.py"
        plugin_file.write_text(sample_plugin_content, encoding="utf-8")
        profile = {"name": "dev", "plugins": ["test_ctx"]}
        result = execute_plugins(profile, "PRE_LAUNCH")
        assert "Test Specialist" in result or "dev" in result

    def test_execute_plugins_missing_plugin(self, config_path):
        profile = {"name": "dev", "plugins": ["nonexistent_plugin"]}
        with patch("myc.agent_plugins.console") as mock_console:
            result = execute_plugins(profile, "PRE_LAUNCH")
        # Should handle missing plugin gracefully
        assert isinstance(result, str)


class TestCompanyPlugins:
    def test_list_empty(self, config_path):
        companies = list_companies()
        assert isinstance(companies, list)

    def test_list_with_company(self, config_path, sample_company_content):
        from myc.agent_plugins import COMPANIES_DIR
        company_file = COMPANIES_DIR / "test_company.py"
        company_file.write_text(sample_company_content, encoding="utf-8")
        companies = list_companies()
        ids = [c["id"] for c in companies]
        assert "test_company" in ids

    def test_execute_company_general_context(self, config_path, sample_company_content):
        from myc.agent_plugins import COMPANIES_DIR
        company_file = COMPANIES_DIR / "test_ctx_company.py"
        sample_with_ctx = sample_company_content.replace("Test Company", "Ctx Company")
        company_file.write_text(sample_with_ctx, encoding="utf-8")
        result = execute_company_profile("test_ctx_company")
        assert "Ctx Company" in result

    def test_execute_company_specialist(self, config_path, sample_company_content):
        from myc.agent_plugins import COMPANIES_DIR
        company_file = COMPANIES_DIR / "ctx_comp2.py"
        company_file.write_text(sample_company_content, encoding="utf-8")
        result = execute_company_profile("ctx_comp2", specialist_id="tech_lead")
        assert "Tech Lead" in result or "Lead developer" in result

    def test_execute_company_invalid_specialist(self, config_path, sample_company_content):
        from myc.agent_plugins import COMPANIES_DIR
        company_file = COMPANIES_DIR / "ctx_comp3.py"
        company_file.write_text(sample_company_content, encoding="utf-8")
        result = execute_company_profile("ctx_comp3", specialist_id="nonexistent")
        assert result == ""

    def test_execute_company_not_found(self, config_path):
        result = execute_company_profile("does_not_exist")
        assert result == ""

    def test_resolve_specialist_context_empty(self, config_path):
        result = _resolve_specialist_context("nonexistent")
        assert result == ""


class TestResolveSpecialistContext:
    def test_returns_context_from_plugin(self, config_path, sample_plugin_content):
        from myc.agent_plugins import PLUGINS_DIR
        plugin_file = PLUGINS_DIR / "resolve_test.py"
        plugin_file.write_text(sample_plugin_content, encoding="utf-8")
        result = _resolve_specialist_context("resolve_test")
        assert "Test Specialist" in result or "Test context" in result
