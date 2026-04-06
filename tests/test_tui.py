"""Unit tests for myc.tui module."""

from unittest.mock import MagicMock, patch, PropertyMock


class TestActionSummary:
    def test_browser_action(self):
        from myc.tui import _action_summary
        actions = [{"type": "browser", "monitor": 0}]
        result = _action_summary(actions)
        assert "Monitor 1" in result

    def test_app_action(self):
        from myc.tui import _action_summary
        actions = [{"type": "app", "path": "/usr/bin/app"}]
        result = _action_summary(actions)
        assert "/usr/bin/app" in result

    def test_mixed_actions(self):
        from myc.tui import _action_summary
        actions = [
            {"type": "browser", "monitor": 1},
            {"type": "app", "path": "/usr/bin/editor"},
        ]
        result = _action_summary(actions)
        assert "Monitor 2" in result
        assert "/usr/bin/editor" in result

    def test_empty_actions(self):
        from myc.tui import _action_summary
        assert _action_summary([]) == "\u2014"

    def test_url_type(self):
        from myc.tui import _action_summary
        actions = [{"type": "url", "monitor": 0}]
        result = _action_summary(actions)
        assert "Monitor 1" in result


class TestNavigateGroupSubcommands:
    def test_navigate_empty_group(self):
        from myc.tui import _navigate_group_subcommands
        with patch("myc.tui.console") as mock_console:
            _navigate_group_subcommands("empty", {"subcommands": {}})
            mock_console.print.assert_called_once()

    def test_select_and_run_subcommand(self, loaded_config):
        from myc.tui import _navigate_group_subcommands
        grp_data = loaded_config["commands"]["estudar"]
        # Mock questionary.select to return a callable that has .ask() returning the value
        mock_select_instance = MagicMock()
        mock_select_instance.ask.return_value = "visao"
        with patch("myc.tui.questionary.select", return_value=mock_select_instance):
            with patch("myc.tui.run_command") as mock_run:
                _navigate_group_subcommands("estudar", grp_data)
                mock_run.assert_called_once_with("estudar", "visao")

    def test_back_choice_exits(self, loaded_config):
        from myc.tui import _navigate_group_subcommands
        grp_data = loaded_config["commands"]["estudar"]
        mock_select_instance = MagicMock()
        mock_select_instance.ask.return_value = "_back"
        with patch("myc.tui.questionary.select", return_value=mock_select_instance):
            with patch("myc.tui.run_command") as mock_run:
                _navigate_group_subcommands("estudar", grp_data)
                mock_run.assert_not_called()


class TestTuiNavigation:
    def test_navigate_by_group_selects_group(self, loaded_config):
        from myc.tui import navigate_by_group
        cmds = loaded_config["commands"]
        mock_select_instance = MagicMock()
        mock_select_instance.ask.return_value = "estudar"
        with patch("myc.tui.questionary.select", return_value=mock_select_instance):
            with patch("myc.tui._navigate_group_subcommands") as mock_nav:
                navigate_by_group(cmds)
                mock_nav.assert_called_once_with("estudar", cmds["estudar"])

    def test_navigate_tui_empty_config(self, config_path):
        from myc.tui import navigate_tui
        with patch("myc.tui.console") as mock_console:
            navigate_tui()
            mock_console.print.assert_called_once()

    def test_navigate_tui_group_filter(self, loaded_config):
        from myc.tui import navigate_tui
        cmds = loaded_config["commands"]
        with patch("myc.tui._navigate_group_subcommands") as mock_nav:
            navigate_tui(group_filter="estudar")
            mock_nav.assert_called_once_with("estudar", cmds["estudar"])

    def test_navigate_tui_group_filter_invalid(self, loaded_config):
        from myc.tui import navigate_tui
        with patch("myc.tui.console") as mock_console:
            navigate_tui(group_filter="invalid_group")
            assert mock_console.print.call_count >= 1
