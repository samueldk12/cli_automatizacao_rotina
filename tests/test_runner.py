"""Unit tests for myc.runner module."""

from unittest.mock import MagicMock, patch

from myc.runner import (
    run_command,
    find_browser,
    list_day_commands,
    DAYS_PT,
    DAYS_DISPLAY,
)


class TestRunCommand:
    def test_run_existing_browser_command(self, loaded_config):
        result = run_command("estudar", "visao")
        assert result is True

    def test_run_nonexistent_group(self, loaded_config):
        result = run_command("inexistente", "foo")
        assert result is False

    def test_run_nonexistent_subcommand(self, loaded_config):
        result = run_command("estudar", "inexistente")
        assert result is False

    def test_run_with_matching_day(self, loaded_config):
        result = run_command("estudar", "visao", day="segunda")
        assert result is True

    def test_run_with_non_matching_day(self, loaded_config):
        result = run_command("estudar", "visao", day="terca")
        assert result is False

    def test_run_command_with_no_days(self, loaded_config):
        """Commands with empty days list run any day."""
        result = run_command("trabalhar", "tralingo", day="segunda")
        assert result is True

    def test_run_browser_action_opens_url(self, loaded_config):
        with patch("myc.runner.open_url_on_monitor") as mock_open:
            run_command("estudar", "visao")
            mock_open.assert_called_once()
            assert "https://example.com/visao" == mock_open.call_args[1]["url"]

    def test_run_mixed_actions(self, loaded_config):
        """Command with both browser and app actions."""
        with (
            patch("myc.runner.open_url_on_monitor") as mock_browser,
            patch("myc.runner.open_app") as mock_app,
        ):
            run_command("trabalhar", "tralingo")
            mock_browser.assert_called_once()
            mock_app.assert_called_once()

    def test_run_app_action(self, loaded_config):
        with (
            patch("myc.runner.open_url_on_monitor"),
            patch("myc.runner.open_app") as mock_app,
        ):
            run_command("trabalhar", "tralingo")
            call_args = mock_app.call_args[0]
            assert call_args[0] == "C:/Program Files/app.exe"
            assert call_args[1] == ["--arg1"]


class TestFindBrowser:
    def test_fallback_returns_browser_string(self):
        with patch("myc.runner.Path") as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = False
            mock_path.return_value = mock_path_instance
            result = find_browser("unknown_browser")
            assert result == "unknown_browser"

    def test_custom_path_used_when_valid(self):
        with patch("myc.runner.load_config") as mock_cfg:
            mock_cfg.return_value = {"settings": {"chrome_path": "C:/custom/chrome.exe"}}
            with patch("myc.runner.Path") as mock_path:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True
                mock_path.return_value = mock_path_instance
                result = find_browser("chrome")
                assert result == "C:/custom/chrome.exe"


class TestListDayCommands:
    def test_returns_commands_for_day(self, loaded_config):
        results = list_day_commands("segunda", loaded_config)
        groups = [r[0] for r in results]
        subs = [r[1] for r in results]
        assert "estudar" in groups
        assert "visao" in subs

    def test_returns_empty_for_day_without_commands(self, loaded_config):
        """Saturday has no commands explicitly scheduled."""
        results = list_day_commands("sabado", loaded_config)
        # Commands with empty days list are returned for every day,
        # so only those with explicitly set days should be excluded.
        subs = {r[1] for r in results}
        # visao (segunda) and pytest (terca) should NOT appear
        assert "visao" not in subs
        assert "pytest" not in subs

    def test_returns_commands_with_empty_days(self, loaded_config):
        """Commands with empty days list appear for every day."""
        results = list_day_commands("quarta", loaded_config)
        subs = [r[1] for r in results]
        assert "tralingo" in subs


class TestDaysConstants:
    def test_days_pt_has_seven_elements(self):
        assert len(DAYS_PT) == 7

    def test_days_display_has_all_days(self):
        assert len(DAYS_DISPLAY) == 7
        for day_pt in DAYS_PT:
            assert day_pt in DAYS_DISPLAY
