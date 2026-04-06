"""Shared fixtures for all MYC tests."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def isolate_myc_dirs(tmp_path):
    """Redirect all ~/.myc paths to tmp_path so tests don't touch real files."""
    agents_dir = tmp_path / ".myc" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    (agents_dir / "plugins").mkdir(exist_ok=True)
    (agents_dir / "companies").mkdir(exist_ok=True)
    (agents_dir / "departments").mkdir(exist_ok=True)
    (agents_dir / "middlewares").mkdir(exist_ok=True)

    config_dir = tmp_path / ".myc"
    config_dir.mkdir(parents=True, exist_ok=True)

    default_config = {
        "version": "1.0",
        "settings": {"chrome_path": "", "default_browser": "chrome"},
        "commands": {},
    }
    config_file = config_dir / "config.json"
    config_file.write_text(json.dumps(default_config), encoding="utf-8")

    with (
        patch("myc.config.CONFIG_DIR", config_dir),
        patch("myc.config.CONFIG_FILE", config_file),
        patch("myc.agent.AGENTS_DIR", agents_dir),
        patch("myc.agent.HISTORY_FILE", agents_dir / "history.json"),
        patch("myc.agent_plugins.PLUGINS_DIR", agents_dir / "plugins"),
        patch("myc.agent_plugins.COMPANIES_DIR", agents_dir / "companies"),
        patch("myc.plugin_manager.PLUGINS_DIR", agents_dir / "plugins"),
        patch("myc.plugin_manager.COMPANIES_DIR", agents_dir / "companies"),
        patch("myc.plugin_manager.PLUGIN_REGISTRY", agents_dir / "plugin_registry.json"),
        patch("myc.plugin_installer.PLUGINS_DIR", agents_dir / "plugins"),
        patch("myc.plugin_installer.COMPANIES_DIR", agents_dir / "companies"),
        patch("myc.plugin_installer.MIDDLEWARES_DIR", agents_dir / "middlewares"),
        patch("myc.department.DEPARTMENTS_DIR", agents_dir / "departments"),
        patch("myc.config.BIN_DIR", config_dir / "bin"),
    ):
        yield tmp_path


@pytest.fixture
def config_path(isolate_myc_dirs):
    return isolate_myc_dirs


@pytest.fixture
def sample_config():
    """A config dict with some commands pre-filled."""
    return {
        "version": "1.0",
        "settings": {"chrome_path": "", "default_browser": "chrome"},
        "commands": {
            "estudar": {
                "description": "Estudar",
                "subcommands": {
                    "visao": {
                        "description": "Visao Computacional",
                        "days": ["segunda"],
                        "actions": [
                            {"type": "browser", "url": "https://example.com/visao", "monitor": 0, "new_window": True, "browser": "chrome"}
                        ],
                    },
                    "pytest": {
                        "description": "Pytest",
                        "days": ["terca"],
                        "actions": [
                            {"type": "browser", "url": "https://example.com/pytest", "monitor": 1, "new_window": True, "browser": "chrome"},
                        ],
                    },
                },
            },
            "trabalhar": {
                "description": "Trabalhar",
                "subcommands": {
                    "tralingo": {
                        "description": "Tralingo",
                        "days": [],
                        "actions": [
                            {"type": "browser", "url": "https://tralingo.com", "monitor": 0, "new_window": False, "browser": "edge"},
                            {"type": "app", "path": "C:/Program Files/app.exe", "args": ["--arg1"]},
                        ],
                    },
                },
            },
        },
    }


@pytest.fixture
def loaded_config(sample_config):
    """Save sample config and return it."""
    from myc.config import save_config
    save_config(sample_config)
    return sample_config


@pytest.fixture
def sample_agent_profile():
    """A sample agent profile dict."""
    return {
        "name": "dev",
        "platform": "openclaude",
        "env": {"OPENAI_API_KEY": "test-key"},
        "cwd": None,
        "initial_context": "You are a dev assistant",
        "custom_command": None,
        "plugins": [],
        "linked_routines": ["estudar:visao"],
        "role": "dev",
        "plugin_filter": [],
        "callable_agents": [],
        "created_at": "2025-01-01T00:00:00",
    }


@pytest.fixture
def sample_plugin_content():
    """Minimal plugin file content."""
    return '''
NAME = "Test Specialist"
DESCRIPTION = "A test specialist plugin"

def PRE_LAUNCH(profile):
    profile.setdefault("test_hook", "pre_launch_called")

def CONTEXT(profile):
    return f"Test context for {profile.get('name', 'unknown')}"

def POST_LAUNCH(profile):
    pass
'''


@pytest.fixture
def sample_company_content():
    """Minimal company file content."""
    return '''
NAME = "Test Company"
DESCRIPTION = "A test company"

SPECIALISTS = [
    {
        "id": "tech_lead",
        "name": "Tech Lead",
        "role": "Lead developer and architect",
        "specialists": [],
    }
]

def COMPANY_CONTEXT():
    return "You work at Test Company"
'''


@pytest.fixture
def sample_department_content():
    """Minimal department file content."""
    return '''
NAME = "Test Department"
DESCRIPTION = "A test department"
ROLE = "You are the test department"
SPECIALISTS = ["test_spec"]
MIDDLEWARES = []
PARENT_COMPANY = None

def DEPARTMENT_CONTEXT():
    return "Test dept context"
'''
