"""Unit tests for myc.monitor module."""

from unittest.mock import patch

from myc.monitor import Monitor, get_monitors, get_monitor


class TestMonitor:
    def test_str_representation(self):
        m = Monitor(index=0, x=0, y=0, width=1920, height=1080, is_primary=True)
        s = str(m)
        assert "1920" in s
        assert "1080" in s
        assert "prim\xe1rio" in s

    def test_str_secondary(self):
        m = Monitor(index=1, x=1920, y=0, width=1920, height=1080, is_primary=False)
        s = str(m)
        assert "prim\xe1rio" not in s


class TestGetMonitors:
    def test_returns_at_least_one_monitor(self):
        monitors = get_monitors()
        assert len(monitors) >= 1
        assert isinstance(monitors[0], Monitor)

    def test_fallback_when_import_fails(self):
        import sys
        with patch.dict("sys.modules", {"screeninfo": None}):
            monitors = get_monitors()
            assert len(monitors) == 1
            assert monitors[0].width == 1920
            assert monitors[0].height == 1080

    def test_first_monitor_is_primary_when_no_screeninfo(self):
        with patch.dict("sys.modules", {"screeninfo": None}):
            monitors = get_monitors()
            assert monitors[0].is_primary is True


class TestGetMonitor:
    def test_get_by_index(self):
        m = get_monitor(0)
        assert isinstance(m, Monitor)
        assert m.index == 0

    def test_get_out_of_range_returns_first(self):
        m = get_monitor(999)
        assert m.index == 0

    def test_get_negative_index_returns_first(self):
        m = get_monitor(-1)
        assert m.index == 0
