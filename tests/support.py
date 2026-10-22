"""
Shared test helpers.

Importing this module puts `app/` on the import path (the app imports its own modules
as `from db import ...`) and provides a tiny hand-built database whose numbers can be
checked with a calculator.
"""

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
DATABASE_DIR = ROOT / "database"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import db  # noqa: E402  (needs the path set above)


# ---------------------------------------------------------------------------
# A small world with exact, hand-checkable answers
#
# Target role "Systems Analyst" (id 2) requires four skills:
#
#   skill           required  importance
#   SQL                 4         5
#   Python              3         4
#   Communication       3         2
#   Modeling            5         1        (importance total = 12)
#
# Opening 1 (role 2) belongs to hiring manager Maya and is open.
# Opening 2 (role 2) belongs to Erin and is paused.
# Opening 3 (role 4) belongs to Maya and is open.
# ---------------------------------------------------------------------------

FIXTURE_SQL = """
INSERT INTO departments VALUES (1, 'Engineering', 'Fixture department');

INSERT INTO roles (role_id, role_name, department_id, level, role_description) VALUES
    (1, 'Analyst',         1, 2, 'Current role of the fixture employees'),
    (2, 'Systems Analyst', 1, 3, 'Target role for most tests'),
    (3, 'Manager',         1, 4, 'Role of the hiring managers'),
    (4, 'Data Engineer',   1, 3, 'A different role, used to test exact-role matching');

INSERT INTO skills VALUES
    (1, 'SQL',           'Technical',  NULL),
    (2, 'Python',        'Technical',  NULL),
    (3, 'Communication', 'Behavioral', NULL),
    (4, 'Modeling',      'Technical',  NULL);

INSERT INTO role_skills (role_id, skill_id, required_level, importance_level) VALUES
    (2, 1, 4, 5),
    (2, 2, 3, 4),
    (2, 3, 3, 2),
    (2, 4, 5, 1),
    (4, 1, 3, 3);

INSERT INTO employees (employee_id, employee_name, current_role_id, manager_id, tenure_years, hire_date) VALUES
    (1, 'Maya Manager', 3, NULL, 8, '2018-01-01'),
    (2, 'Alice',        1, 1,    3, '2023-01-01'),
    (3, 'Bob',          1, 1,    3, '2023-01-01'),
    (4, 'Carol',        1, 1,    3, '2023-01-01'),
    (5, 'Dan',          1, 1,    3, '2023-01-01'),
    (6, 'Erin Manager', 3, NULL, 6, '2020-01-01'),
    (7, 'Priv',         1, 1,    2, '2024-01-01'),
    (8, 'Frank',        1, 1,    2, '2024-01-01'),
    (9, 'Gina',         1, 1,    4, '2022-01-01');

-- Alice meets every requirement; Bob has one priority gap (SQL, 2 levels short);
-- Carol is far below on everything; Dan has recorded only SQL;
-- Gina beats the requirement on SQL and Python but is far short on Modeling.
INSERT INTO employee_skills (employee_id, skill_id, proficiency_level, last_updated) VALUES
    (2, 1, 4, '2026-01-01'), (2, 2, 3, '2026-01-01'), (2, 3, 3, '2026-01-01'), (2, 4, 5, '2026-01-01'),
    (3, 1, 2, '2026-01-01'), (3, 2, 3, '2026-01-01'), (3, 3, 3, '2026-01-01'), (3, 4, 5, '2026-01-01'),
    (4, 1, 1, '2026-01-01'), (4, 2, 1, '2026-01-01'), (4, 3, 1, '2026-01-01'), (4, 4, 1, '2026-01-01'),
    (5, 1, 4, '2026-01-01'),
    (9, 1, 5, '2026-01-01'), (9, 2, 5, '2026-01-01'), (9, 3, 3, '2026-01-01'), (9, 4, 1, '2026-01-01');

INSERT INTO employee_career_interests (employee_id, target_role_id, created_at, visibility_level) VALUES
    (2, 2, '2026-02-01', 'opening_managers'),
    (3, 2, '2026-02-01', 'opening_managers'),
    (4, 2, '2026-02-01', 'opening_managers'),
    (5, 2, '2026-02-01', 'opening_managers'),
    (7, 2, '2026-02-01', 'private'),
    (8, 4, '2026-02-01', 'opening_managers'),
    (1, 2, '2026-02-01', 'opening_managers'),
    (9, 2, '2026-02-01', 'opening_managers');

INSERT INTO job_openings (opening_id, role_id, hiring_manager_id, headcount, status, open_date) VALUES
    (1, 2, 1, 1, 'open',   '2026-03-01'),
    (2, 2, 6, 1, 'paused', '2026-03-01'),
    (3, 4, 1, 1, 'open',   '2026-03-01');

INSERT INTO future_demand (demand_id, role_id, planning_period, required_headcount, created_at) VALUES
    (1, 1, '2027-Q4', 8, '2026-01-01'),
    (2, 2, '2027-Q4', 3, '2026-01-01'),
    (3, 4, '2027-Q4', 2, '2026-01-01'),
    (4, 2, '2028-Q4', 5, '2026-01-01');
"""


def build_fixture_database(path):
    """Create `path` from the real schema.sql plus the fixture rows above."""
    connection = sqlite3.connect(path)
    try:
        connection.executescript((DATABASE_DIR / "schema.sql").read_text(encoding="utf-8"))
        connection.executescript(FIXTURE_SQL)
        connection.commit()
    finally:
        connection.close()


class FixtureDatabaseTestCase(unittest.TestCase):
    """Runs every test of the subclass against the fixture database."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.fixture_path = Path(cls._tmp.name) / "fixture.db"
        build_fixture_database(cls.fixture_path)
        cls._patch = mock.patch.object(db, "DB_PATH", cls.fixture_path)
        cls._patch.start()

    @classmethod
    def tearDownClass(cls):
        cls._patch.stop()
        cls._tmp.cleanup()
