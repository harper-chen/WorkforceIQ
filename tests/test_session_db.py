"""
Each visitor session gets a private copy of the seeded database.

Streamlit's session_state is replaced by plain dictionaries: one dictionary is one visitor.
"""

import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import support
import db

ALICE, SYSTEMS_ANALYST, DATA_ENGINEER = 2, 2, 4


class FakeSessions:
    """Stands in for db._session_state(): call .use(name) to 'become' that visitor."""

    def __init__(self):
        self.sessions = {}
        self.current = None

    def use(self, name):
        self.current = None if name is None else self.sessions.setdefault(name, {})

    def __call__(self):
        return self.current


class TestPerVisitorDatabase(support.FixtureDatabaseTestCase):
    def setUp(self):
        self.sessions = FakeSessions()
        self.session_dir = tempfile.TemporaryDirectory()
        patches = [
            mock.patch.object(db, "_session_state", self.sessions),
            mock.patch.object(db, "SESSION_DB_DIR", Path(self.session_dir.name)),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        self.addCleanup(self.session_dir.cleanup)

    def visible_names(self):
        table = db.get_visible_internal_candidates(1, 1)
        return set(table["employee_name"])

    # ---- identity of the file -------------------------------------------

    def test_outside_a_session_the_shared_baseline_is_used(self):
        self.sessions.use(None)
        self.assertEqual(db.active_db_path(), self.fixture_path)

    def test_each_visitor_gets_a_different_private_file(self):
        self.sessions.use("a")
        path_a = db.active_db_path()
        self.sessions.use("b")
        path_b = db.active_db_path()

        self.assertNotEqual(path_a, path_b)
        self.assertNotEqual(path_a, self.fixture_path)
        self.assertEqual(path_a.parent, Path(self.session_dir.name))

    def test_the_same_visitor_keeps_the_same_file(self):
        self.sessions.use("a")
        first = db.active_db_path()
        self.assertEqual(db.active_db_path(), first)

    def test_a_new_copy_starts_with_the_seeded_data(self):
        self.sessions.use("a")
        self.assertEqual(self.visible_names(), {"Alice", "Bob", "Carol", "Dan", "Gina"})

    def test_a_deleted_copy_is_recreated(self):
        self.sessions.use("a")
        original = db.active_db_path()
        db.update_career_visibility(ALICE, SYSTEMS_ANALYST, "private")
        original.unlink()

        self.assertTrue(db.active_db_path().exists())
        self.assertIn("Alice", self.visible_names())  # back to the seeded state

    # ---- isolation of changes -------------------------------------------

    def test_a_saved_career_interest_is_only_visible_to_its_own_visitor(self):
        self.sessions.use("a")
        self.assertTrue(db.save_career_interest(ALICE, DATA_ENGINEER))
        self.assertTrue(db.is_career_saved(ALICE, DATA_ENGINEER))

        self.sessions.use("b")
        self.assertFalse(db.is_career_saved(ALICE, DATA_ENGINEER))

    def test_a_visibility_change_does_not_leak_to_other_visitors(self):
        self.sessions.use("a")
        db.update_career_visibility(ALICE, SYSTEMS_ANALYST, "private")
        self.assertNotIn("Alice", self.visible_names())

        self.sessions.use("b")
        self.assertIn("Alice", self.visible_names())

    def test_the_shared_baseline_is_never_modified(self):
        self.sessions.use("a")
        db.update_career_visibility(ALICE, SYSTEMS_ANALYST, "private")
        db.save_career_interest(ALICE, DATA_ENGINEER)

        self.sessions.use(None)
        self.assertIn("Alice", self.visible_names())
        self.assertFalse(db.is_career_saved(ALICE, DATA_ENGINEER))

    # ---- reset ------------------------------------------------------------

    def test_reset_restores_only_the_callers_copy(self):
        self.sessions.use("a")
        db.update_career_visibility(ALICE, SYSTEMS_ANALYST, "private")
        self.sessions.use("b")
        db.update_career_visibility(ALICE, SYSTEMS_ANALYST, "private")

        self.sessions.use("a")
        db.reset_demo_database()

        self.assertIn("Alice", self.visible_names())
        self.sessions.use("b")
        self.assertNotIn("Alice", self.visible_names())

    def test_reset_keeps_the_same_file_for_the_visitor(self):
        self.sessions.use("a")
        before = db.active_db_path()
        db.reset_demo_database()
        self.assertEqual(db.active_db_path(), before)

    # ---- cleanup -----------------------------------------------------------

    def make_old_file(self, name, age_seconds):
        path = Path(self.session_dir.name) / name
        path.write_bytes(b"x")
        stamp = time.time() - age_seconds
        os.utime(path, (stamp, stamp))
        return path

    def test_copies_untouched_for_more_than_a_day_are_removed(self):
        old = self.make_old_file("session_old.db", db.SESSION_DB_MAX_AGE_SECONDS + 60)
        fresh = self.make_old_file("session_fresh.db", 60)

        self.sessions.use("newcomer")
        db.active_db_path()

        self.assertFalse(old.exists())
        self.assertTrue(fresh.exists())

    def test_total_number_of_copies_is_capped_keeping_the_newest(self):
        files = [self.make_old_file(f"session_{i}.db", 1000 - i * 10) for i in range(6)]

        with mock.patch.object(db, "SESSION_DB_MAX_FILES", 3):
            self.sessions.use("newcomer")
            db.active_db_path()

        survivors = {path.name for path in Path(self.session_dir.name).glob("session_*.db")}
        self.assertEqual(len(survivors), 4)  # 3 kept + the newcomer's
        self.assertIn(files[-1].name, survivors)
        self.assertNotIn(files[0].name, survivors)

    def test_files_that_are_not_session_copies_are_left_alone(self):
        other = self.make_old_file("notes.txt", db.SESSION_DB_MAX_AGE_SECONDS + 60)
        self.sessions.use("newcomer")
        db.active_db_path()
        self.assertTrue(other.exists())


if __name__ == "__main__":
    unittest.main()
