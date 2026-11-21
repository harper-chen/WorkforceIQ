"""
Course prerequisites: a recorded level below the minimum locks a course,
but a prerequisite with no record only asks the employee to confirm it.
"""

import sqlite3

import support
from db import get_recommended_learning

DAN = 5      # Python not recorded
CAROL = 4    # Python recorded at level 1
SYSTEMS_ANALYST = 2

TRAINING_SQL = """
INSERT INTO training_programs (training_id, training_name, estimated_weeks, training_description) VALUES
    (1, 'Applied Modeling', 6, 'Builds Modeling and Communication'),
    (2, 'Python Basics',    3, 'Builds Python to level 2');

INSERT INTO training_skills (training_id, skill_id, course_skill_level) VALUES
    (1, 4, 5),
    (1, 3, 3),
    (2, 2, 2);

-- Applied Modeling expects Python level 2 or higher.
INSERT INTO training_prerequisites (training_id, skill_id, minimum_level) VALUES
    (1, 2, 2);
"""


class TestCoursePrerequisites(support.FixtureDatabaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        connection = sqlite3.connect(cls.fixture_path)
        try:
            connection.executescript(TRAINING_SQL)
            connection.commit()
        finally:
            connection.close()

    @staticmethod
    def course(courses, name):
        return next(course for course in courses if course["training_name"] == name)

    def test_not_recorded_prerequisite_does_not_lock_the_course(self):
        learning = get_recommended_learning(DAN, SYSTEMS_ANALYST)
        ready_names = [course["training_name"] for course in learning["ready"]]
        locked_names = [course["training_name"] for course in learning["locked"]]

        self.assertIn("Applied Modeling", ready_names)
        self.assertNotIn("Applied Modeling", locked_names)

    def test_not_recorded_prerequisite_is_flagged_to_confirm(self):
        learning = get_recommended_learning(DAN, SYSTEMS_ANALYST)
        course = self.course(learning["ready"], "Applied Modeling")

        self.assertEqual(
            course["unconfirmed_prerequisites"],
            [{"skill_id": 2, "skill_name": "Python", "minimum_level": 2}],
        )

    def test_recorded_level_below_minimum_still_locks_the_course(self):
        learning = get_recommended_learning(CAROL, SYSTEMS_ANALYST)
        locked = self.course(learning["locked"], "Applied Modeling")

        self.assertEqual(locked["unconfirmed_prerequisites"], [])
        option = locked["prerequisite_options"][0]
        self.assertEqual((option["skill_name"], option["current_level"]), ("Python", 1))
        self.assertEqual(option["course_options"][0]["training_name"], "Python Basics")
        self.assertTrue(option["course_options"][0]["available_now"])
