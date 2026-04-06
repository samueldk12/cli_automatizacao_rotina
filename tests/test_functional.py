"""Functional tests — end-to-end flows simulating real user interactions."""

import json
from pathlib import Path
from contextlib import ExitStack
from unittest.mock import MagicMock, patch


# ─── Full Command Lifecycle ──────────────────────────────────

class TestCommandLifecycle:
    """User adds a command → lists it → runs it → edits it → deletes it."""

    def test_add_list_run_delete_command(self, config_path, capsys):
        """Full lifecycle: create a command, verify it exists, run it, delete it."""
        from myc.config import load_config, save_config

        # 1. ADD: Simulate user adding a command
        config = {
            "version": "1.0", "settings": {}, "commands": {}
        }
        config["commands"]["estudar"] = {
            "description": "Estudar",
            "subcommands": {
                "matematica": {
                    "description": "Aula de matematica",
                    "days": ["segunda", "quarta"],
                    "actions": [
                        {"type": "browser", "url": "https://math.example.com", "monitor": 0, "new_window": True, "browser": "chrome"},
                    ],
                },
            },
        }
        save_config(config)

        # 2. LIST: Verify command appears in saved config
        loaded = load_config()
        assert "estudar" in loaded["commands"]
        assert "matematica" in loaded["commands"]["estudar"]["subcommands"]

        # 3. RUN: Execute the command
        from myc.runner import run_command
        with patch("myc.runner.open_url_on_monitor") as mock_open:
            result = run_command("estudar", "matematica", day="segunda")
        assert result is True
        mock_open.assert_called_once()
        called_kwargs = mock_open.call_args[1]
        assert "math.example.com" in called_kwargs["url"]

        # 4. DELETE: Remove the subcommand
        loaded = load_config()
        del loaded["commands"]["estudar"]["subcommands"]["matematica"]
        save_config(loaded)

        reloaded = load_config()
        assert "matematica" not in reloaded["commands"]["estudar"]["subcommands"]

    def test_command_with_multiple_actions(self, config_path):
        """A command that opens multiple URLs and an app."""
        from myc.config import save_config

        config = {
            "version": "1.0", "settings": {},
            "commands": {
                "manha": {
                    "subcommands": {
                        "rotina": {
                            "days": [],
                            "actions": [
                                {"type": "browser", "url": "https://news.example.com", "monitor": 0, "new_window": True, "browser": "chrome"},
                                {"type": "browser", "url": "https://mail.example.com", "monitor": 1, "new_window": True, "browser": "edge"},
                                {"type": "app", "path": "C:/Slack/slack.exe", "args": []},
                            ],
                        },
                    },
                },
            },
        }
        save_config(config)

        with (
            patch("myc.runner.open_url_on_monitor") as mock_browser,
            patch("myc.runner.open_app") as mock_app,
        ):
            from myc.runner import run_command
            result = run_command("manha", "rotina")

        assert result is True
        assert mock_browser.call_count == 2
        mock_app.assert_called_once_with("C:/Slack/slack.exe", [])


# ─── Agent Full Lifecycle ────────────────────────────────────

class TestAgentLifecycle:
    """Create agent → launch → check history → delete."""

    def test_create_launch_history_delete(self, config_path):
        """Full agent lifecycle."""
        from myc.agent import _load_agents, _save_agents, _load_history, launch_agent

        # 1. CREATE agent
        agents = {
            "dev": {
                "name": "dev", "platform": "openclaude",
                "env": {"CLAUDE_CODE_USE_OPENAI": "1", "OPENAI_MODEL": "test-model"},
                "cwd": str(config_path), "initial_context": "You are a dev",
                "custom_command": None, "plugins": [], "linked_routines": [],
            }
        }
        _save_agents(agents)
        assert "dev" in _load_agents()

        # 2. LAUNCH agent
        mock_proc = MagicMock()
        mock_proc.wait.return_value = 0

        with ExitStack() as stack:
            stack.enter_context(patch("myc.agent._write_claude_md", return_value=True))
            stack.enter_context(patch("myc.agent._build_launch_cmd", return_value=(["mock_cmd"], False)))
            stack.enter_context(patch("myc.agent._find_binary", return_value="mock_cmd"))
            stack.enter_context(patch("myc.agent_plugins.execute_plugins", return_value=""))
            stack.enter_context(patch("subprocess.Popen", return_value=mock_proc))
            rc = launch_agent("dev")

        assert rc == 0

        # 3. CHECK HISTORY
        history = _load_history()
        assert len(history) == 1
        assert history[0]["agent"] == "dev"
        assert history[0]["status"] == "ok"

        # 4. DELETE agent
        del agents["dev"]
        _save_agents(agents)
        assert "dev" not in _load_agents()

    def test_agent_with_plugins_and_context(self, config_path):
        """Agent with plugins should include plugin context in CLAUDE.md."""
        from myc.agent import _save_agents, launch_agent
        from myc.agent_plugins import PLUGINS_DIR

        (PLUGINS_DIR / "context_plugin.py").write_text('''
NAME = "Context Plugin"
DESCRIPTION = "Adds context"
def CONTEXT(profile):
    return f"Extra context for {profile.get('name', 'agent')}"
''', encoding="utf-8")

        agents = {
            "ctx_agent": {
                "name": "ctx_agent", "platform": "openclaude", "env": {},
                "cwd": str(config_path), "initial_context": "Base context",
                "custom_command": None, "plugins": ["context_plugin"],
                "linked_routines": [],
            }
        }
        _save_agents(agents)

        mock_proc = MagicMock()
        mock_proc.wait.return_value = 0

        md_file = config_path / "CLAUDE.md"

        # Don't patch _write_claude_md so the file is actually written
        with ExitStack() as stack:
            stack.enter_context(patch("myc.agent._build_launch_cmd", return_value=(["mock_cmd"], False)))
            stack.enter_context(patch("myc.agent._find_binary", return_value="mock_cmd"))
            stack.enter_context(patch("myc.agent_plugins.execute_plugins", return_value=""))
            stack.enter_context(patch("subprocess.Popen", return_value=mock_proc))
            launch_agent("ctx_agent")

        assert md_file.exists()
        content = md_file.read_text()
        assert "ctx_agent" in content or "Base context" in content


# ─── Plugin Install/Lifecycle ────────────────────────────────

class TestPluginLifecycle:
    """Install plugin → execute → uninstall."""

    def test_plugin_full_lifecycle(self, config_path):
        """Create, run hooks, and remove a plugin."""
        from myc.plugin_installer import (
            install_plugin_from_file, uninstall_plugin, get_plugin_meta,
            PLUGINS_DIR,
        )

        # 1. CREATE plugin from file
        src = config_path / "lifecycle_plugin.py"
        src.write_text('''
NAME = "Lifecycle Plugin"
DESCRIPTION = "Tests full lifecycle"
def PRE_LAUNCH(profile):
    print("pre-launch called")
def CONTEXT(profile):
    return "lifecycle context"
def POST_LAUNCH(profile):
    pass
''', encoding="utf-8")

        result = install_plugin_from_file(str(src))
        assert result is True

        # 2. VERIFY installed
        meta = get_plugin_meta("lifecycle_plugin")
        assert meta is not None
        assert meta["name"] == "Lifecycle Plugin"

        # 3. EXECUTE hooks
        from myc.agent_plugins import execute_plugins
        profile = {"name": "test", "plugins": ["lifecycle_plugin"]}
        context = execute_plugins(profile, "PRE_LAUNCH")
        assert "lifecycle context" in context

        # 4. UNINSTALL
        with patch("myc.plugin_installer.console"):
            result = uninstall_plugin("lifecycle_plugin")
        assert result is True
        assert not (PLUGINS_DIR / "lifecycle_plugin.py").exists()


# ─── Company Workflow ────────────────────────────────────────

class TestCompanyWorkflow:
    """Create company → launch specialist → verify context."""

    def test_full_company_workflow(self, config_path):
        """Create company with specialists, launch one, verify output."""
        from myc.agent_plugins import PLUGINS_DIR, COMPANIES_DIR
        from myc.agent_plugins import execute_company_profile, _resolve_specialist_context

        # Install specialists
        (PLUGINS_DIR / "frontend_dev.py").write_text('''
NAME = "Frontend Developer"
DESCRIPTION = "Builds UI components"
def CONTEXT(profile):
    return "Expert in React, CSS, accessibility"
''', encoding="utf-8")

        (PLUGINS_DIR / "backend_dev.py").write_text('''
NAME = "Backend Developer"
DESCRIPTION = "builds APIs"
def CONTEXT(profile):
    return "Expert in Python, databases, APIs"
''', encoding="utf-8")

        # Create company
        (COMPANIES_DIR / "dev_house.py").write_text('''
NAME = "Dev House"
DESCRIPTION = "Full stack development company"
SPECIALISTS = [
    {
        "id": "tech_lead",
        "name": "Tech Lead",
        "role": "Architect and lead all development",
        "specialists": ["frontend_dev", "backend_dev"],
    },
    {
        "id": "qa_engineer",
        "name": "QA Engineer",
        "role": "Test everything",
        "specialists": [],
    }
]
def COMPANY_CONTEXT():
    return "Working at Dev House. Code quality is #1."
''', encoding="utf-8")

        # List companies
        from myc.agent_plugins import list_companies
        companies = list_companies()
        ids = [c["id"] for c in companies]
        assert "dev_house" in ids

        # Execute general company context
        general_ctx = execute_company_profile("dev_house")
        assert "Dev House" in general_ctx
        assert "Tech Lead" in general_ctx

        # Execute specific specialist
        specialist_ctx = execute_company_profile("dev_house", specialist_id="tech_lead")
        assert "Tech Lead" in specialist_ctx
        assert "Dev House" in specialist_ctx

        # Resolve specialist contexts are included
        frontend_ctx = _resolve_specialist_context("frontend_dev")
        assert "React" in frontend_ctx

    def test_company_invalid_specialist_fails_gracefully(self, config_path):
        """Requesting a nonexistent specialist should return empty string."""
        from myc.agent_plugins import COMPANIES_DIR, execute_company_profile

        (COMPANIES_DIR / "simple_company.py").write_text('''
NAME = "Simple"
DESCRIPTION = "Simple company"
SPECIALISTS = [{"id": "only_one", "name": "Only One", "role": "Does everything", "specialists": []}]
''', encoding="utf-8")

        result = execute_company_profile("simple_company", specialist_id="nonexistent")
        assert result == ""


# ─── Department Workflow ─────────────────────────────────────

class TestDepartmentWorkflow:
    """Create department → list → get context → launch."""

    def test_department_full_workflow(self, config_path):
        """Complete department lifecycle."""
        from myc.department import DEPARTMENTS_DIR, list_departments, get_department_context, launch_department

        # Create department
        (DEPARTMENTS_DIR / "marketing_dept.py").write_text('''
NAME = "Marketing Department"
DESCRIPTION = "Handles all marketing activities"
ROLE = "You are the marketing team. Create campaigns, analyze metrics, and grow the brand."
SPECIALISTS = ["social_media", "content_writer"]
MIDDLEWARES = []
PARENT_COMPANY = None

def DEPARTMENT_CONTEXT():
    return "Marketing dept active"
''', encoding="utf-8")

        # List departments
        depts = list_departments()
        ids = [d["id"] for d in depts]
        assert "marketing_dept" in ids

        # Get context
        ctx = get_department_context("marketing_dept")
        assert ctx is not None
        assert "Marketing Department" in ctx
        assert "marketing team" in ctx
        assert "Marketing dept active" in ctx or "marketing_dept active" in ctx

        # Launch department
        with patch("myc.department.console") as mock_console:
            result = launch_department("marketing_dept", "Create Q4 campaign")
        assert result == 0

    def test_department_bound_to_company(self, config_path):
        """Department should be filterable by parent company."""
        from myc.department import DEPARTMENTS_DIR, list_departments

        (DEPARTMENTS_DIR / "hr_dept.py").write_text('''
NAME = "HR"
DESCRIPTION = "Human Resources"
PARENT_COMPANY = "big_corp"
SPECIALISTS = []
MIDDLEWARES = []

def DEPARTMENT_CONTEXT():
    return "HR context"
''', encoding="utf-8")

        # Filter by company
        filtered = list_departments(company_id="big_corp")
        assert any(d["id"] == "hr_dept" for d in filtered)

        # Filter by other company - should not include it
        other = list_departments(company_id="other_corp")
        assert not any(d["id"] == "hr_dept" for d in other)


# ─── Bundle Installation Workflow ────────────────────────────

class TestBundleWorkflow:
    """Install bundle → verify plugins → list bundles."""

    def test_bundle_install_lists_available(self, config_path):
        """Should be able to list all bundles."""
        from myc.plugin_manager import list_bundles, BUNDLES

        with patch("myc.plugin_manager.console") as mock_console:
            with patch("myc.plugin_installer.get_plugin_meta", return_value=None):
                list_bundles()
            assert mock_console.print.called

    def test_install_unknown_bundle_warns(self, config_path):
        from myc.plugin_manager import install_bundles
        with patch("myc.plugin_manager.console") as mock_console:
            install_bundles(names=["bogus_bundle_xyz"])
            calls = [str(c) for c in mock_console.print.call_args_list]
            assert any("bogus_bundle_xyz" in c for c in calls), f"Expected warning about bogus bundle in: {calls}"


# ─── Cross-Module: Config → Agent → Plugin Flow ──────────────

class TestEndToEndMyWorkflow:
    """Simulating a complete 'myc' user workflow."""

    def test_full_user_session(self, config_path):
        """
        1. User saves config with commands
        2. User creates an agent
        3. Agent is launched with MYC routine context
        4. History is recorded
        """
        from myc.config import save_config, load_config
        from myc.agent import _save_agents, _load_history, launch_agent

        # Step 1: Save config
        config = {
            "version": "1.0", "settings": {},
            "commands": {
                "estudar": {
                    "subcommands": {
                        "python": {
                            "description": "Python course",
                            "days": [],
                            "actions": [
                                {"type": "browser", "url": "https://python-course.com", "monitor": 0, "new_window": True, "browser": "chrome"},
                            ],
                        },
                    },
                },
            },
        }
        save_config(config)

        # Step 2: Create agent
        agents = {
            "default": {
                "name": "default", "platform": "openclaude", "env": {},
                "cwd": str(config_path), "initial_context": "You are MYC assistant",
                "custom_command": None, "plugins": [], "linked_routines": ["estudar:python"],
            },
        }
        _save_agents(agents)

        # Step 3: Launch with MYC context
        mock_proc = MagicMock()
        mock_proc.wait.return_value = 0

        with ExitStack() as stack:
            stack.enter_context(patch("myc.agent._write_claude_md", return_value=True))
            stack.enter_context(patch("myc.agent._build_launch_cmd", return_value=(["mock_cmd"], False)))
            stack.enter_context(patch("myc.agent._find_binary", return_value="mock_cmd"))
            stack.enter_context(patch("myc.agent_plugins.execute_plugins", return_value=""))
            stack.enter_context(patch("subprocess.Popen", return_value=mock_proc))
            rc = launch_agent("default", group="estudar", subcommand="python")

        assert rc == 0

        # Step 4: Verify history
        history = _load_history()
        assert len(history) >= 1
        assert history[0]["agent"] == "default"

    def test_multi_command_multi_day(self, config_path):
        """Verify multiple commands across different days work correctly."""
        from myc.config import save_config, load_config
        from myc.runner import run_command, list_day_commands

        config = {
            "version": "1.0", "settings": {},
            "commands": {
                "estudar": {
                    "subcommands": {
                        "ingles": {"days": ["segunda", "quarta", "sexta"], "actions": []},
                        "design": {"days": ["terca", "quinta"], "actions": []},
                        "projeto": {"days": [], "actions": []},  # every day
                    },
                },
            },
        }
        save_config(config)

        # Monday commands
        monday = list_day_commands("segunda", load_config())
        monday_subs = {s[1] for s in monday}
        assert "projeto" in monday_subs
        assert "design" not in monday_subs

        # Run commands
        assert run_command("estudar", "ingles", day="segunda") is True

        # Tuesday commands
        tuesday = list_day_commands("terca", load_config())
        tuesday_subs = {s[1] for s in tuesday}
        assert "projeto" in tuesday_subs
        assert "english" not in tuesday_subs


# ─── Monitor Detection ───────────────────────────────────────

class TestMonitorFunctional:
    def test_monitor_info_accessible(self, config_path):
        """Monitor dataclasses should be usable and contain expected fields."""
        from myc.monitor import get_monitors, Monitor
        monitors = get_monitors()
        for m in monitors:
            assert hasattr(m, "index")
            assert hasattr(m, "width")
            assert hasattr(m, "height")
            assert hasattr(m, "x")
            assert hasattr(m, "y")
            assert hasattr(m, "is_primary")
            assert isinstance(m.index, int)
            assert isinstance(m.width, int)
            assert isinstance(m.height, int)
