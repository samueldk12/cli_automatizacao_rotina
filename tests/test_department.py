"""Unit tests for myc.department module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from myc.department import (
    list_departments,
    get_department_context,
    launch_department,
)


class TestListDepartments:
    def test_empty_returns_list(self, config_path):
        depts = list_departments()
        assert isinstance(depts, list)

    def test_with_department(self, config_path, sample_department_content):
        from myc.department import DEPARTMENTS_DIR
        dept_file = DEPARTMENTS_DIR / "test_dept.py"
        dept_file.write_text(sample_department_content, encoding="utf-8")
        depts = list_departments()
        ids = [d["id"] for d in depts]
        assert "test_dept" in ids

    def test_filter_by_company(self, config_path):
        from myc.department import DEPARTMENTS_DIR
        # Company-bound department
        dept1 = DEPARTMENTS_DIR / "dept_a.py"
        dept1.write_text(
            'NAME = "Dept A"\nPARENT_COMPANY = "company_a"\nDESCRIPTION = "A dept"\nSPECIALISTS = []\nMIDDLEWARES = []',
            encoding="utf-8",
        )
        # Independent department
        dept2 = DEPARTMENTS_DIR / "dept_b.py"
        dept2.write_text(
            'NAME = "Dept B"\nPARENT_COMPANY = None\nDESCRIPTION = "B dept"\nSPECIALISTS = []\nMIDDLEWARES = []',
            encoding="utf-8",
        )
        filtered = list_departments(company_id="company_a")
        ids = [d["id"] for d in filtered]
        assert "dept_a" in ids
        assert "dept_b" not in ids

    def test_handles_corrupt_file(self, config_path):
        from myc.department import DEPARTMENTS_DIR
        bad = DEPARTMENTS_DIR / "bad_dept.py"
        bad.write_text("raise RuntimeError('broken')", encoding="utf-8")
        depts = list_departments()
        ids = [d["id"] for d in depts]
        assert "bad_dept" in ids
        # Should have error in description
        bad_dept = next(d for d in depts if d["id"] == "bad_dept")
        assert "ERRO" in bad_dept["name"] or "broken" in bad_dept["description"]


class TestGetDepartmentContext:
    def test_missing_department(self, config_path):
        result = get_department_context("nonexistent")
        assert result is None

    def test_basic_context(self, config_path, sample_department_content):
        from myc.department import DEPARTMENTS_DIR
        dept_file = DEPARTMENTS_DIR / "ctx_dept.py"
        dept_file.write_text(sample_department_content, encoding="utf-8")
        result = get_department_context("ctx_dept")
        assert "Test Department" in result

    def test_includes_specialists(self, config_path):
        from myc.department import DEPARTMENTS_DIR
        content = '''
NAME = "SpecDept"
DESCRIPTION = "Dept with specialists"
ROLE = "You handle X"
SPECIALISTS = ["spec_a", "spec_b"]
MIDDLEWARES = []
PARENT_COMPANY = None

def DEPARTMENT_CONTEXT():
    return "Extra dept info"
'''
        dept_file = DEPARTMENTS_DIR / "spec_dept.py"
        dept_file.write_text(content, encoding="utf-8")
        result = get_department_context("spec_dept")
        assert "spec_a" in result
        assert "spec_b" in result


class TestLaunchDepartment:
    def test_missing_department(self, config_path):
        result = launch_department("nonexistent", "test query")
        assert result == 1

    def test_valid_department(self, config_path, sample_department_content):
        from myc.department import DEPARTMENTS_DIR
        dept_file = DEPARTMENTS_DIR / "launch_dept.py"
        dept_file.write_text(sample_department_content, encoding="utf-8")
        with patch("myc.department.console") as mock_console:
            result = launch_department("launch_dept", "do something")
        assert result == 0
