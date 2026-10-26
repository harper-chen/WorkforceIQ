"""
Workforce gap and unaddressed capability gaps, on small hand-made tables.
"""

import unittest

import pandas as pd

import support  # noqa: F401  (sets up the import path)
from planning import build_unaddressed_capability_gaps, build_workforce_plan


def demand(*rows):
    return pd.DataFrame(rows, columns=["role_id", "role_name", "current_headcount"])


class TestWorkforceGap(unittest.TestCase):
    def test_gap_is_planned_minus_current(self):
        plan = build_workforce_plan(demand((1, "Analyst", 4), (2, "Engineer", 1)), {1: 6, 2: 5})
        self.assertEqual(plan["Workforce Gap"].tolist(), [2, 4])

    def test_gap_never_goes_negative(self):
        plan = build_workforce_plan(demand((1, "Analyst", 9)), {1: 6})
        self.assertEqual(plan["Workforce Gap"].tolist(), [0])

    def test_equal_headcount_is_no_gap(self):
        plan = build_workforce_plan(demand((1, "Analyst", 6)), {1: 6})
        self.assertEqual(plan["Workforce Gap"].tolist(), [0])

    def test_output_columns_and_labels(self):
        plan = build_workforce_plan(demand((1, "Analyst", 4)), {1: 6})
        self.assertEqual(
            list(plan.columns), ["role_id", "Role", "Current HC", "Planned HC", "Workforce Gap"]
        )
        self.assertEqual(plan.loc[0, "Role"], "Analyst")
        self.assertEqual(plan.loc[0, "Current HC"], 4)
        self.assertEqual(plan.loc[0, "Planned HC"], 6)

    def test_input_table_is_not_modified(self):
        table = demand((1, "Analyst", 4))
        build_workforce_plan(table, {1: 6})
        self.assertEqual(list(table.columns), ["role_id", "role_name", "current_headcount"])


def requirements(*rows):
    return pd.DataFrame(
        rows,
        columns=["role_id", "role_name", "skill_id", "skill_name", "required_level"],
    )


def trainings(*rows):
    return pd.DataFrame(
        rows, columns=["training_id", "training_name", "skill_id", "course_skill_level"]
    )


class TestUnaddressedCapabilityGaps(unittest.TestCase):
    def test_skill_is_flagged_only_when_best_course_is_below_requirement(self):
        result = build_unaddressed_capability_gaps(
            requirements(
                (2, "Systems Analyst", 10, "Data Modeling", 4),
                (2, "Systems Analyst", 11, "SQL", 3),
            ),
            trainings(
                (1, "SQL Fundamentals", 11, 4),
                (2, "Modeling Basics", 10, 2),
            ),
        )
        self.assertEqual(result["Skill"].tolist(), ["Data Modeling"])
        row = result.iloc[0]
        self.assertEqual(row["Affected Roles"], "Systems Analyst")
        self.assertEqual(row["Required Level"], "L4")
        self.assertEqual(row["Available Internal Training"], "Modeling Basics (L2)")

    def test_meeting_the_requirement_exactly_is_covered(self):
        result = build_unaddressed_capability_gaps(
            requirements((2, "Systems Analyst", 11, "SQL", 3)),
            trainings((1, "SQL Fundamentals", 11, 3)),
        )
        self.assertTrue(result.empty)

    def test_every_role_is_checked_regardless_of_workforce_gap(self):
        result = build_unaddressed_capability_gaps(
            requirements(
                (1, "Analyst", 12, "Negotiation", 3),
                (2, "Systems Analyst", 10, "Data Modeling", 4),
            ),
            trainings(),
        )
        self.assertEqual(sorted(result["Skill"]), ["Data Modeling", "Negotiation"])

    def test_no_requirements_returns_an_empty_table(self):
        result = build_unaddressed_capability_gaps(
            requirements(),
            trainings(),
        )
        self.assertTrue(result.empty)

    def test_skill_with_no_internal_training_says_so(self):
        result = build_unaddressed_capability_gaps(
            requirements((2, "Systems Analyst", 10, "Data Modeling", 4)),
            trainings((1, "SQL Fundamentals", 11, 4)),
        )
        self.assertEqual(result.iloc[0]["Available Internal Training"], "No internal training available")

    def test_required_level_is_shown_as_a_range_across_roles(self):
        result = build_unaddressed_capability_gaps(
            requirements(
                (2, "Systems Analyst", 10, "Data Modeling", 3),
                (3, "Data Engineer", 10, "Data Modeling", 5),
            ),
            trainings((1, "Modeling Basics", 10, 2)),
        )
        row = result.iloc[0]
        self.assertEqual(row["Required Level"], "L3–L5")
        self.assertEqual(row["Affected Roles"], "Data Engineer, Systems Analyst")

    def test_tied_best_courses_are_all_listed_alphabetically(self):
        result = build_unaddressed_capability_gaps(
            requirements((2, "Systems Analyst", 10, "Data Modeling", 5)),
            trainings(
                (1, "Zebra Modeling", 10, 3),
                (2, "Alpha Modeling", 10, 3),
                (3, "Intro Modeling", 10, 1),
            ),
        )
        self.assertEqual(
            result.iloc[0]["Available Internal Training"],
            "Alpha Modeling (L3)  \nZebra Modeling (L3)",
        )

    def test_empty_training_catalog_flags_every_required_skill(self):
        result = build_unaddressed_capability_gaps(
            requirements(
                (2, "Systems Analyst", 10, "Data Modeling", 4),
                (2, "Systems Analyst", 11, "SQL", 3),
            ),
            trainings(),
        )
        self.assertEqual(sorted(result["Skill"]), ["Data Modeling", "SQL"])


if __name__ == "__main__":
    unittest.main()
