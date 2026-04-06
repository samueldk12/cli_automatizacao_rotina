"""Integration tests — verify that MYC modules work together."""

import json
from pathlib import Path
from contextlib import ExitStack
from unittest.mock import MagicMock, patch

import pytest


# ─── Config + Runner Integration ──────────────────────────────

class TestConfigRunnerIntegration:
    """Test that config drives runner correctly."""

    def test_full_command_lifecycle(self, config_path):
        """Save config → run command → verify action called."""
        from myc.config import save_config
        from myc.runner import run_command

        config = {
            "version": "1.0",
            "settings": {},
            "commands": {
                "work": {
                    "subcommands": {
                        "email": {
                            "days": [],
                            "actions": [
                                {"type": "browser", "url": "https://mail.example.com", "monitor": 0, "new_window": True, "browser": "chrome"},
                            ],
                        },
                    },
                },
            },
        }
        save_config(config)

        with patch("myc.runner.open_url_on_monitor") as mock_open:
            result = run_command("work", "email")

        assert result is True
        mock_open.assert_called_once_with(
            url="https://mail.example.com",
            monitor_index=0,
            new_window=True,
            browser="chrome",
        )

    def test_config_edit_reflected_in_runner(self, config_path):
        """Changes in config should immediately affect runner behavior."""
        from myc.config import load_config, save_config
        from myc.runner import run_command

        save_config({
            "version": "1.0", "settings": {}, "commands": {
                "test": {"subcommands": {"a": {"days": ["segunda"], "actions": []}}}
            },
        })

        # Should fail on wrong day
        assert run_command("test", "a", day="sexta") is False
        # Should succeed on correct day
        assert run_command("test", "a", day="segunda") is True

        # Now change the days
        config = load_config()
        config["commands"]["test"]["subcommands"]["a"]["days"] = ["sexta"]
        save_config(config)

        assert run_command("test", "a", day="segunda") is False
        assert run_command("test", "a", day="sexta") is True


# ─── Config + TUI Integration ────────────────────────────────

class TestConfigTuiIntegration:
    """Test that TUI reads and displays config data."""

    def test_tui_displays_saved_commands(self, config_path):
        """Commands saved via config should appear in TUI components."""
        from myc.config import save_config
        from myc.tui import show_commands_table

        config = {
            "version": "1.0", "settings": {},
            "commands": {
                "grp1": {"subcommands": {"cmd1": {"description": "desc1", "days": [], "actions": []}}},
            },
        }
        save_config(config)

        with patch("myc.tui.console") as mock_console:
            show_commands_table(config["commands"])
            assert mock_console.print.called


# ─── Agent + Config Integration ──────────────────────────────

class TestAgentConfigIntegration:
    """Test that agent module integrates with config for MYC routines."""

    def test_launch_records_history(self, config_path):
        """Launching an agent with subprocess should record history."""
        from myc.agent import _save_agents, _load_history, launch_agent

        agents = {"test_agent": {
            "name": "test_agent", "platform": "openclaude", "env": {},
            "cwd": str(config_path), "initial_context": "ctx", "custom_command": None,
        }}
        _save_agents(agents)

        mock_proc = MagicMock()
        mock_proc.wait.return_value = 0

        with ExitStack() as stack:
            stack.enter_context(patch("myc.agent._write_claude_md", return_value=True))
            stack.enter_context(patch("myc.agent._build_launch_cmd", return_value=(["mock_cmd"], False)))
            stack.enter_context(patch("myc.agent._find_binary", return_value="mock_cmd"))
            stack.enter_context(patch("myc.agent_plugins.execute_plugins", return_value=""))
            stack.enter_context(patch("subprocess.Popen", return_value=mock_proc))
            launch_agent("test_agent")

        history = _load_history()
        assert len(history) >= 1
        assert history[0]["agent"] == "test_agent"

    def test_summarize_routine_injected_in_claude_md(self, config_path):
        """MYC routines should be included in CLAUDE.md."""
        from myc.config import save_config
        from myc.agent import _write_claude_md

        save_config({
            "version": "1.0", "settings": {},
            "commands": {
                "study": {"subcommands": {"math": {"description": "math study", "days": [], "actions": []}}},
            },
        })

        work_dir = config_path / "workdir"
        work_dir.mkdir()
        _write_claude_md(work_dir, "student", "initial ctx", myc_tasks="## MYC Tasks\n\n- study math")

        content = (work_dir / "CLAUDE.md").read_text()
        assert "MYC Tasks" in content


# ─── Plugin + Agent Integration ──────────────────────────────

class TestPluginAgentIntegration:
    """Test plugins execute hooks when agent launches."""

    def test_plugin_hook_called_during_agent_launch(self, config_path):
        """When agent launches, plugins should run their PRE_LAUNCH hooks."""
        from myc.agent import _save_agents, launch_agent
        from myc.agent_plugins import PLUGINS_DIR

        # Create plugin
        plugin_file = PLUGINS_DIR / "hook_test.py"
        plugin_file.write_text('''
NAME = "Hook Test"
DESCRIPTION = "Tests plugin hooks"
def PRE_LAUNCH(profile):
    profile.setdefault("hook_called", True)
    return True
def CONTEXT(profile):
    return "Plugin context active"
''', encoding="utf-8")

        agents = {"agent_with_plugin": {
            "name": "agent_with_plugin", "platform": "openclaude", "env": {},
            "cwd": str(config_path), "initial_context": "Agent initial context here",
            "custom_command": None,
            "plugins": ["hook_test"],
        }}
        _save_agents(agents)

        mock_proc = MagicMock()
        mock_proc.wait.return_value = 0

        md_path = config_path / "CLAUDE.md"

        # Don't mock _write_claude_md so the file actually gets written
        with ExitStack() as stack:
            stack.enter_context(patch("myc.agent._build_launch_cmd", return_value=(["mock_cmd"], False)))
            stack.enter_context(patch("myc.agent._find_binary", return_value="mock_cmd"))
            stack.enter_context(patch("myc.agent_plugins.execute_plugins", return_value="Plugin context active"))
            stack.enter_context(patch("subprocess.Popen", return_value=mock_proc))
            launch_agent("agent_with_plugin")

        # Verify CLAUDE.md was created
        assert md_path.exists()
        content = md_path.read_text()
        assert "Agent initial context here" in content


# ─── Company + Specialist Integration ────────────────────────

class TestCompanySpecialistIntegration:
    """Test company plugins reference specialist plugins."""

    def test_company_resolves_specialist_context(self, config_path):
        """A company should be able to resolve context from its specialists."""
        from myc.agent_plugins import PLUGINS_DIR, COMPANIES_DIR, execute_company_profile

        # Create a specialist
        (PLUGINS_DIR / "company_spec.py").write_text('''
NAME = "Company Spec"
DESCRIPTION = "Specialist for company"
def CONTEXT(profile):
    return "Specialist context"
''', encoding="utf-8")

        # Create a company referencing the specialist
        (COMPANIES_DIR / "integration_company.py").write_text('''
NAME = "Integration Company"
DESCRIPTION = "Tests company-specialist integration"
SPECIALISTS = [
    {
        "id": "team_lead",
        "name": "Team Lead",
        "role": "Lead the team",
        "specialists": ["company_spec"],
    }
]
def COMPANY_CONTEXT():
    return "Company context"
''', encoding="utf-8")

        ctx = execute_company_profile("integration_company", specialist_id="team_lead")
        assert "Team Lead" in ctx
        assert "Integration Company" in ctx

    def test_company_list_specialists(self, config_path):
        """Company general context should list available specialists."""
        from myc.agent_plugins import COMPANIES_DIR, execute_company_profile

        (COMPANIES_DIR / "list_company.py").write_text('''
NAME = "List Company"
DESCRIPTION = "Lists specialists"
SPECIALISTS = [
    {"id": "s1", "name": "Spec One", "role": "Role 1", "specialists": []},
    {"id": "s2", "name": "Spec Two", "role": "Role 2", "specialists": []},
]
''', encoding="utf-8")

        ctx = execute_company_profile("list_company")
        assert "List Company" in ctx
        assert "Spec One" in ctx
        assert "Spec Two" in ctx


# ─── Department + Middleware Integration ─────────────────────

class TestDepartmentMiddlewareIntegration:
    """Test departments apply middlewares to queries."""

    def test_department_with_middlewares(self, config_path):
        """Department should load middlewares and include them in context."""
        from myc.department import DEPARTMENTS_DIR, MIDDLEWARES_DIR, get_department_context

        # Ensure dirs exist
        MIDDLEWARES_DIR.mkdir(parents=True, exist_ok=True)
        (MIDDLEWARES_DIR / "dept_mw.py").write_text('''
NAME = "Dept MW"
DESCRIPTION = "Department middleware"
MIDDLEWARE_TYPE = "pre"
RUNS_WHEN = "auto"
''', encoding="utf-8")

        (DEPARTMENTS_DIR / "mw_dept.py").write_text('''
NAME = "MW Dept"
DESCRIPTION = "Dept with middleware"
ROLE = "You handle everything"
SPECIALISTS = []
MIDDLEWARES = []
PARENT_COMPANY = None

def DEPARTMENT_CONTEXT():
    return "MW dept context"
''', encoding="utf-8")

        # Verify department loads without error
        ctx = get_department_context("mw_dept")
        assert ctx is not None
        assert "MW Dept" in ctx


# ─── Config Wrapper Generation Integration ───────────────────

class TestWrapperGenerationIntegration:
    """Test that wrapper scripts are generated correctly."""

    def test_generate_wrapper_creates_files(self, config_path):
        """Calling the wrapper generator should create .bat and .ps1 files."""
        from myc.config import BIN_DIR
        from myc.cli import _generate_wrapper

        BIN_DIR.mkdir(parents=True, exist_ok=True)

        with patch("sys.executable", "python"):
            _generate_wrapper("test_group")

        assert (BIN_DIR / "test_group.bat").exists()
        assert (BIN_DIR / "test_group.ps1").exists()

        # Check .bat content
        bat = (BIN_DIR / "test_group.bat").read_text()
        assert "test_group" in bat
        assert "python" in bat
        assert "myc" in bat

        # Check .ps1 content
        ps1 = (BIN_DIR / "test_group.ps1").read_text()
        assert "test_group" in ps1
        assert "python" in ps1

    def test_wrapper_content_executes_tui_and_run(self, config_path):
        """Wrapper should support both TUI (no args) and run (with args) modes."""
        from myc.cli import _generate_wrapper
        # Must patch where the module looks for BIN_DIR
        test_bin = config_path / ".myc" / "bin"

        with patch("myc.cli.BIN_DIR", test_bin):
            with patch("sys.executable", "python"):
                _generate_wrapper("my_group")

        bat_path = test_bin / "my_group.bat"
        assert bat_path.exists(), f"Expected wrapper at {bat_path}"
        bat = bat_path.read_text()
        # Check TUI mode (no args)
        assert "myc tui --group my_group" in bat
        # Check run mode (with args)
        assert "myc run my_group" in bat
