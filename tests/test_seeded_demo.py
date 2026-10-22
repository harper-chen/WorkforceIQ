"""
The real seed files: the database must rebuild cleanly, and the README walkthrough
(River Hsu -> Systems Analyst -> Riley Chang) must still tell the story it claims to.
"""

import contextlib
import importlib.util
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import support
import db
from readiness import get_candidate_internal_readiness, get_opening_staffing_route

spec = importlib.util.spec_from_file_location("rebuild_db", support.DATABASE_DIR / "rebuild_db.py")
rebuild = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rebuild)


class TestSeededDemo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls._tmp.name) / "seeded.db"

        cls.log = io.StringIO()
        with contextlib.redirect_stdout(cls.log):
            rebuild.build(cls.path)
            cls.checks_passed = rebuild.verify(cls.path)

        cls._patch = mock.patch.object(db, "DB_PATH", cls.path)
        cls._patch.start()

    @classmethod
    def tearDownClass(cls):
        cls._patch.stop()
        cls._tmp.cleanup()

    def test_rebuild_integrity_checks_pass(self):
        self.assertTrue(self.checks_passed, self.log.getvalue())

    def test_every_table_has_data(self):
        connection = sqlite3.connect(self.path)
        try:
            for table in rebuild.TABLES:
                count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                self.assertGreater(count, 0, table)
        finally:
            connection.close()

    def lookup(self, sql, *params):
        connection = sqlite3.connect(self.path)
        try:
            return connection.execute(sql, params).fetchone()
        finally:
            connection.close()

    def test_readme_walkthrough_cast_exists(self):
        river = self.lookup(
            "SELECT r.role_name FROM employees e JOIN roles r ON r.role_id = e.current_role_id "
            "WHERE e.employee_name = 'River Hsu'"
        )
        riley = self.lookup(
            "SELECT e.employee_id, jo.opening_id, r.role_name, jo.status FROM employees e "
            "JOIN job_openings jo ON jo.hiring_manager_id = e.employee_id "
            "JOIN roles r ON r.role_id = jo.role_id WHERE e.employee_name = 'Riley Chang'"
        )
        self.assertEqual(river[0], "Business Analyst")
        self.assertEqual(riley[2:], ("Systems Analyst", "open"))

    def test_readme_walkthrough_decision(self):
        manager_id, opening_id = self.lookup(
            "SELECT e.employee_id, jo.opening_id FROM employees e "
            "JOIN job_openings jo ON jo.hiring_manager_id = e.employee_id "
            "WHERE e.employee_name = 'Riley Chang'"
        )
        candidates = db.get_visible_internal_candidates(manager_id, opening_id)
        names = candidates["employee_name"].tolist()

        self.assertIn("River Hsu", names)
        self.assertNotIn("Micah Liu", names)  # saved the same role but kept it private

        river = candidates[candidates["employee_name"] == "River Hsu"].iloc[0]
        self.assertEqual(get_candidate_internal_readiness(river)["label"], "Train First")

        route = get_opening_staffing_route(candidates)
        self.assertEqual(route["route_label"], "Internal Mobility")
        self.assertEqual(route["readiness_label"], "Train First")


if __name__ == "__main__":
    unittest.main()
