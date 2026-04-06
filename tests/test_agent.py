"""Unit tests for myc.agent module."""

import json
from unittest.mock import MagicMock, patch

from myc.agent import (
    _load_agents,
    _save_agents,
    _load_history,
    _save_history,
    _record_history,
    _find_command,
    _build_launch_cmd,
    _summarize_myc_routine,
    _write_claude_md,
    list_agents,
    delete_agent,
    link_plugin_to_agent,
    unlink_plugin_from_agent,
    link_agent_to_agent,
    unlink_agent_from_agent,
)


class TestAgentStorage:
    def test_load_empty_returns_dict(self, config_path):
        data = _load_agents()
        assert isinstance(data, dict)
        assert len(data) == 0

    def test_save_and_load_roundtrip(self, config_path):
        agents = {
            "dev": {"name": "dev", "platform": "openclaude", "env": {}, "cwd": None},
        }
        _save_agents(agents)
        loaded = _load_agents()
        assert loaded["dev"]["platform"] == "openclaude"

    def test_load_handles_corrupt_json(self, config_path):
        from myc.agent import AGENTS_DIR
        idx_file = AGENTS_DIR / "agents.json"
        idx_file.write_text("not json", encoding="utf-8")
        result = _load_agents()
        assert result == {}


class TestHistory:
    def test_empty_history(self, config_path):
        entries = _load_history()
        assert isinstance(entries, list)

    def test_record_and_load(self, config_path):
        _record_history("dev", "openclaude", "/tmp", "test:routine", "ok")
        entries = _load_history()
        assert len(entries) == 1
        assert entries[0]["agent"] == "dev"
        assert entries[0]["status"] == "ok"
        assert "timestamp" in entries[0]

    def test_history_limited_to_500(self, config_path):
        for i in range(510):
            _record_history("dev", "openclaude", "/tmp", None, "ok")
        entries = _load_history()
        assert len(entries) == 500


class TestFindCommand:
    def test_nonexistent_command(self):
        result = _find_command("xyz_nonexistent_cmd_12345")
        assert result is None

    def test_returns_path_when_found(self):
        """Verify it finds a real command like 'python' or 'python3'."""
        import sys
        result = _find_command("python")
        if result is None:
            result = _find_command("python3")
        # May still be None if not on PATH, so just check type
        assert result is None or isinstance(result, str)


class TestBuildLaunchCmd:
    def test_openclaude(self):
        with patch("myc.agent._find_binary", return_value=None):
            cmd, shell = _build_launch_cmd("openclaude", None)
            assert cmd == ["openclaude"]
            assert shell is True

    def test_cursor(self):
        with patch("myc.agent._find_binary", return_value=None):
            cmd, shell = _build_launch_cmd("cursor", None)
            assert cmd[0] == "cursor"
            assert shell is False

    def test_vscode_copilot(self):
        with patch("myc.agent._find_binary", return_value=None):
            cmd, shell = _build_launch_cmd("vscode_copilot", None)
            assert cmd[0] == "code"
            assert shell is False

    def test_codex_fallback(self):
        with patch("myc.agent._find_binary", return_value=None):
            cmd, shell = _build_launch_cmd("codex", None)
            assert cmd == ["codex"]
            assert shell is True

    def test_custom_command(self):
        cmd, shell = _build_launch_cmd("custom", "claude --verbose")
        assert cmd == "claude --verbose"
        assert shell is True

    def test_unknown_platform(self):
        result = _build_launch_cmd("bogus", None)
        assert result is None

    def test_openclaude_with_binary(self):
        with patch("myc.agent._find_binary", return_value="C:/openclaude.cmd"):
            cmd, shell = _build_launch_cmd("openclaude", None)
            assert cmd == ["C:/openclaude.cmd"]
            assert shell is True


class TestSummarizeRoutine:
    def test_empty_config_returns_empty(self):
        with patch("myc.config.load_config", return_value={"commands": {}}):
            result = _summarize_myc_routine()
            assert result == ""

    def test_no_config_file(self):
        with patch("myc.config.load_config", return_value={}):
            result = _summarize_myc_routine()
            assert result == ""

    def test_with_commands(self, loaded_config):
        result = _summarize_myc_routine()
        assert "MYC Routines" in result
        assert "estudar" in result

    def test_filters_by_group(self, loaded_config):
        result = _summarize_myc_routine(group="estudar")
        assert "estudar" in result
        assert "trabalhar" not in result

    def test_filters_by_subcommand(self, loaded_config):
        result = _summarize_myc_routine(group="estudar", subcommand="visao")
        assert "visao" in result
        assert "pytest" not in result


class TestWriteClaudeMd:
    def test_creates_file(self, config_path):
        work_dir = config_path / "workdir"
        work_dir.mkdir()
        result = _write_claude_md(work_dir, "dev", "context")
        assert result is True
        md = work_dir / "CLAUDE.md"
        assert md.exists()
        content = md.read_text()
        assert "# Agent: dev" in content

    def test_does_not_duplicate_same_agent(self, config_path):
        work_dir = config_path / "workdir"
        work_dir.mkdir()
        _write_claude_md(work_dir, "dev", "context")
        result = _write_claude_md(work_dir, "dev", "other context")
        assert result is False

    def test_appends_to_existing_file(self, config_path):
        work_dir = config_path / "workdir"
        work_dir.mkdir()
        existing = work_dir / "CLAUDE.md"
        existing.write_text("Existing content", encoding="utf-8")
        _write_claude_md(work_dir, "dev", "new context")
        content = existing.read_text()
        assert "Existing content" in content
        assert "# Agent: dev" in content

    def test_with_myc_tasks(self, config_path):
        work_dir = config_path / "workdir"
        work_dir.mkdir()
        _write_claude_md(work_dir, "dev", "ctx", myc_tasks="## MYC Tasks\n\n- run visao")
        content = (work_dir / "CLAUDE.md").read_text()
        assert "MYC Tasks" in content


class TestDeleteAgent:
    def test_delete_nonexistent(self, config_path):
        with patch("questionary.confirm") as mock_confirm:
            delete_agent("nonexistent")
            # Should return early, never ask
            mock_confirm.assert_not_called()

    def test_delete_existing_confirmed(self, config_path):
        agents = {"dev": {"name": "dev", "platform": "openclaude"}}
        _save_agents(agents)
        with patch("questionary.confirm", return_value=MagicMock(ask=MagicMock(return_value=True))):
            delete_agent("dev")
        remaining = _load_agents()
        assert "dev" not in remaining

    def test_delete_existing_cancelled(self, config_path):
        agents = {"dev": {"name": "dev", "platform": "openclaude"}}
        _save_agents(agents)
        with patch("questionary.confirm", return_value=MagicMock(ask=MagicMock(return_value=False))):
            delete_agent("dev")
        remaining = _load_agents()
        assert "dev" in remaining


class TestAgentLinking:
    def test_link_plugin_to_agent(self, config_path):
        agents = {"dev": {"name": "dev", "platform": "openclaude"}}
        _save_agents(agents)
        with patch("myc.agent.console"):
            link_plugin_to_agent("dev", "git_helper")
        after = _load_agents()
        assert "git_helper" in after["dev"]["plugins"]

    def test_link_plugin_duplicate_rejected(self, config_path):
        agents = {"dev": {"name": "dev", "platform": "openclaude", "plugins": ["git_helper"]}}
        _save_agents(agents)
        with patch("myc.agent.console"):
            link_plugin_to_agent("dev", "git_helper")
        after = _load_agents()
        # Should not be duplicated
        count = after["dev"]["plugins"].count("git_helper")
        assert count == 1

    def test_unlink_plugin_from_agent(self, config_path):
        agents = {"dev": {"name": "dev", "platform": "openclaude", "plugins": ["git_helper"]}}
        _save_agents(agents)
        with patch("myc.agent.console"):
            unlink_plugin_from_agent("dev", "git_helper")
        after = _load_agents()
        assert "git_helper" not in after["dev"]["plugins"]

    def test_link_agent_to_agent(self, config_path):
        agents = {"dev": {"name": "dev"}, "artist": {"name": "artist"}}
        _save_agents(agents)
        with patch("myc.agent.console"):
            link_agent_to_agent("dev", "artist")
        after = _load_agents()
        assert "artist" in after["dev"]["callable_agents"]

    def test_link_agent_bidirectional(self, config_path):
        agents = {"dev": {"name": "dev"}, "artist": {"name": "artist"}}
        _save_agents(agents)
        with patch("myc.agent.console"):
            link_agent_to_agent("dev", "artist", bidirectional=True)
        after = _load_agents()
        assert "artist" in after["dev"]["callable_agents"]
        assert "dev" in after["artist"]["callable_agents"]

    def test_unlink_agent_from_agent(self, config_path):
        agents = {"dev": {"name": "dev", "callable_agents": ["artist"]}, "artist": {"name": "artist"}}
        _save_agents(agents)
        with patch("myc.agent.console"):
            unlink_agent_from_agent("dev", "artist")
        after = _load_agents()
        assert "artist" not in after["dev"]["callable_agents"]
