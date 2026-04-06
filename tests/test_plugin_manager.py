"""Unit tests for myc.plugin_manager module."""

from unittest.mock import MagicMock, patch

from myc.plugin_manager import BUNDLES, COMPANY_BUNDLES


class TestBundles:
    def test_bundles_is_dict(self):
        assert isinstance(BUNDLES, dict)
        assert len(BUNDLES) > 0

    def test_bundle_structure(self):
        for bid, bdata in BUNDLES.items():
            assert "name" in bdata, f"Bundle {bid} missing 'name'"
            assert "description" in bdata, f"Bundle {bid} missing 'description'"
            assert "plugins" in bdata, f"Bundle {bid} missing 'plugins'"
            assert isinstance(bdata["plugins"], list)

    def test_nonempty_bundles(self):
        for bid, bdata in BUNDLES.items():
            assert len(bdata["plugins"]) > 0, f"Bundle {bid} has no plugins"


class TestCompanyBundles:
    def test_company_bundles_is_dict(self):
        assert isinstance(COMPANY_BUNDLES, dict)
        assert len(COMPANY_BUNDLES) > 0

    def test_company_bundle_structure(self):
        for bid, bdata in COMPANY_BUNDLES.items():
            assert "name" in bdata
            assert "description" in bdata
            assert "specialists" in bdata
            assert "company_context" in bdata
            assert isinstance(bdata["specialists"], list)


class TestInstallBundles:
    def test_install_all_with_no_plugins(self, config_path):
        """Should not crash even if no plugins exist."""
        from myc.plugin_manager import install_bundles
        with patch("myc.plugin_installer.install_plugin", return_value=False):
            install_bundles(all_=True)

    def test_install_by_name(self, config_path):
        from myc.plugin_manager import install_bundles
        with patch("myc.plugin_installer.install_plugin", return_value=False):
            install_bundles(names=["marketing"])

    def test_install_unknown_bundle(self, config_path):
        from myc.plugin_manager import install_bundles
        with patch("myc.plugin_manager.console") as mock_console:
            install_bundles(names=["nonexistent_bundle_xyz"])
            mock_console.print.assert_called()

    def test_install_no_args_shows_table(self, config_path):
        from myc.plugin_manager import install_bundles
        install_bundles()  # Should print table and return


class TestInstallCompanyBundle:
    def test_install_unknown(self, config_path):
        from myc.plugin_manager import install_company_bundle
        with patch("myc.plugin_manager.console") as mock_console:
            install_company_bundle("nonexistent_company")
            # Should print error about unknown bundle
            assert mock_console.print.called

    def test_install_lists_available(self, config_path):
        """Testing that install_company_bundle at least handles empty company lists."""
        from myc.plugin_manager import install_company_bundle
        # Pick first available bundle - may or may not have plugins installed
        # Just ensure it doesn't crash on known bundles
        first_key = next(iter(COMPANY_BUNDLES))
        with patch("myc.plugin_installer.install_plugin", return_value=False):
            with patch("myc.plugin_manager.console"):
                install_company_bundle(first_key)


class TestListBundles:
    def test_list_bundles_no_crash(self, config_path):
        from myc.plugin_manager import list_bundles
        with patch("myc.plugin_manager.console"):
            with patch("myc.plugin_installer.get_plugin_meta", return_value=None):
                list_bundles()

    def test_list_company_bundles_no_crash(self, config_path):
        from myc.plugin_manager import list_company_bundles
        with patch("myc.plugin_manager.console"):
            list_company_bundles()
