"""
The SQL-side rules (Skill Match, gaps, manager visibility, headcount) against a small
database whose answers are worked out by hand in tests/support.py.

Target role "Systems Analyst" requires SQL 4 (importance 5), Python 3 (4),
Communication 3 (2) and Modeling 5 (1); the importance total is 12.
"""

import math
import unittest

import support
from readiness import get_candidate_internal_readiness, get_opening_staffing_route
import db

ALICE, BOB, CAROL, DAN, FRANK, GINA = 2, 3, 4, 5, 8, 9
MAYA, ERIN = 1, 6
SYSTEMS_ANALYST, DATA_ENGINEER = 2, 4


class TestTargetRoleSkillDetails(support.FixtureDatabaseTestCase):
    def details(self, employee_id, role_id=SYSTEMS_ANALYST):
        table = db.get_target_role_skill_details(employee_id, role_id)
        return table.set_index("skill_name")

    def test_lists_every_required_skill_most_important_first(self):
        table = db.get_target_role_skill_details(ALICE, SYSTEMS_ANALYST)
        self.assertEqual(table["skill_name"].tolist(), ["SQL", "Python", "Communication", "Modeling"])

    def test_gap_is_required_minus_current(self):
        self.assertEqual(self.details(BOB).loc["SQL", "gap"], 2)
        self.assertEqual(self.details(ALICE).loc["SQL", "gap"], 0)

    def test_exceeding_a_requirement_shows_a_negative_gap(self):
        # Gina's SQL is 5 against a requirement of 4.
        self.assertEqual(self.details(GINA).loc["SQL", "gap"], -1)

    def test_missing_record_is_null_not_zero(self):
        # Dan has recorded only SQL.
        details = self.details(DAN)
        self.assertTrue(math.isnan(details.loc["Python", "proficiency_level"]))
        self.assertTrue(math.isnan(details.loc["Python", "gap"]))
        self.assertEqual(details.loc["SQL", "gap"], 0)


class TestVisibleInternalCandidates(support.FixtureDatabaseTestCase):
    def candidates(self, manager_id=MAYA, opening_id=1):
        return db.get_visible_internal_candidates(manager_id, opening_id)

    def by_name(self, **kwargs):
        table = self.candidates(**kwargs)
        return table.set_index("employee_name")

    # ---- who is visible -------------------------------------------------

    def test_only_employees_who_opted_in_for_the_exact_role_are_visible(self):
        self.assertEqual(
            sorted(self.candidates()["employee_name"]),
            ["Alice", "Bob", "Carol", "Dan", "Gina"],
        )

    def test_private_interest_is_never_visible(self):
        self.assertNotIn("Priv", self.candidates()["employee_name"].tolist())

    def test_interest_in_a_different_role_is_not_visible(self):
        # Frank opted in for Data Engineer, not Systems Analyst.
        self.assertNotIn("Frank", self.candidates()["employee_name"].tolist())

    def test_exact_role_match_for_the_other_opening(self):
        self.assertEqual(
            self.candidates(manager_id=MAYA, opening_id=3)["employee_name"].tolist(),
            ["Frank"],
        )

    def test_hiring_manager_is_excluded_from_their_own_list(self):
        self.assertNotIn("Maya Manager", self.candidates()["employee_name"].tolist())

    def test_paused_opening_shows_no_candidates(self):
        self.assertTrue(self.candidates(manager_id=ERIN, opening_id=2).empty)

    def test_another_managers_opening_shows_no_candidates(self):
        self.assertTrue(self.candidates(manager_id=ERIN, opening_id=1).empty)

    def test_unknown_opening_shows_no_candidates(self):
        self.assertTrue(self.candidates(opening_id=999).empty)

    # ---- the numbers ----------------------------------------------------

    def test_fully_qualified_candidate(self):
        alice = self.by_name().loc["Alice"]
        self.assertAlmostEqual(alice["match_percent"], 100.0, delta=0.05)
        self.assertEqual(
            (alice["skills_met"], alice["skills_to_develop"], alice["not_recorded_skills"]), (4, 0, 0)
        )
        self.assertEqual((alice["significant_gaps"], alice["priority_gaps"]), (0, 0))

    def test_one_priority_gap(self):
        # (5 x 2/4 + 4 + 2 + 1) / 12 = 79.17%
        bob = self.by_name().loc["Bob"]
        self.assertAlmostEqual(bob["match_percent"], 79.2, delta=0.05)
        self.assertEqual((bob["skills_met"], bob["skills_to_develop"]), (3, 1))
        self.assertEqual((bob["significant_gaps"], bob["priority_gaps"]), (1, 1))

    def test_large_gaps_everywhere(self):
        # (5 x 1/4 + 4 x 1/3 + 2 x 1/3 + 1 x 1/5) / 12 = 28.75%
        carol = self.by_name().loc["Carol"]
        self.assertAlmostEqual(carol["match_percent"], 28.75, delta=0.06)
        self.assertEqual((carol["skills_met"], carol["skills_to_develop"]), (0, 4))
        # All four gaps are 2+ levels; only SQL (5) and Python (4) have importance >= 4.
        self.assertEqual((carol["significant_gaps"], carol["priority_gaps"]), (4, 2))

    def test_missing_records_score_zero_but_are_not_counted_as_gaps(self):
        # Dan: only SQL recorded -> 5 / 12 = 41.67%
        dan = self.by_name().loc["Dan"]
        self.assertAlmostEqual(dan["match_percent"], 41.7, delta=0.05)
        self.assertEqual(dan["not_recorded_skills"], 3)
        self.assertEqual((dan["significant_gaps"], dan["priority_gaps"]), (0, 0))

    def test_overperformance_in_one_skill_does_not_offset_a_gap_in_another(self):
        # Gina: SQL 5 vs 4 and Python 5 vs 3 are capped at 100% each, Modeling is 1 of 5.
        # (5 + 4 + 2 + 1 x 1/5) / 12 = 93.3%. Without the cap she would score above 100%.
        gina = self.by_name().loc["Gina"]
        self.assertAlmostEqual(gina["match_percent"], 93.3, delta=0.05)
        self.assertLessEqual(gina["match_percent"], 100.0)
        # The Modeling shortfall is 4 levels but the skill has importance 1: significant, not priority.
        self.assertEqual((gina["significant_gaps"], gina["priority_gaps"]), (1, 0))

    def test_candidates_are_ordered_by_skill_match(self):
        self.assertEqual(
            self.candidates()["employee_name"].tolist(),
            ["Alice", "Gina", "Bob", "Dan", "Carol"],
        )

    def test_priority_gaps_are_a_subset_of_significant_gaps(self):
        table = self.candidates()
        self.assertTrue((table["priority_gaps"] <= table["significant_gaps"]).all())

    # ---- from SQL row to decision --------------------------------------

    def test_readiness_labels_for_the_fixture_candidates(self):
        table = self.by_name()
        labels = {
            name: get_candidate_internal_readiness(row)["code"] for name, row in table.iterrows()
        }
        self.assertEqual(
            labels,
            {
                "Alice": "ready_now",
                "Gina": "ready_now",
                "Bob": "train_first",
                "Carol": "larger_gap",
                "Dan": "not_assessed",
            },
        )

    def test_staffing_route_for_the_fixture_opening(self):
        route = get_opening_staffing_route(self.candidates())
        self.assertEqual((route["route_code"], route["readiness_label"]), ("internal_mobility", "Ready Now"))

    def test_candidate_with_no_recorded_skills_is_not_assessed(self):
        frank = self.candidates(manager_id=MAYA, opening_id=3).iloc[0]
        self.assertEqual(get_candidate_internal_readiness(frank)["code"], "not_assessed")


class TestRecommendedCareers(support.FixtureDatabaseTestCase):
    """The employee-facing Skill Match must use the same rules as the manager-facing one."""

    def match(self, employee_id, role_name):
        table = db.get_recommended_careers(employee_id).set_index("role_name")
        return table.loc[role_name]

    def test_overperformance_is_capped_per_skill(self):
        # Gina: (5 + 4 + 2 + 1 x 1/5) / 12 = 93.3%, the same as in the manager view.
        self.assertAlmostEqual(self.match(GINA, "Systems Analyst")["match_percent"], 93.3, delta=0.05)

    def test_a_role_fully_covered_scores_exactly_one_hundred(self):
        # Data Engineer needs only SQL 3; Gina has SQL 5.
        self.assertAlmostEqual(self.match(GINA, "Data Engineer")["match_percent"], 100.0, delta=0.05)

    def test_missing_records_are_counted_but_score_zero(self):
        dan = self.match(DAN, "Systems Analyst")
        self.assertAlmostEqual(dan["match_percent"], 41.7, delta=0.05)
        self.assertEqual(dan["not_recorded_skills"], 3)


class TestWorkforceDemand(support.FixtureDatabaseTestCase):
    def test_planning_periods_are_sorted_and_distinct(self):
        self.assertEqual(db.get_planning_periods()["planning_period"].tolist(), ["2027-Q4", "2028-Q4"])

    def test_current_headcount_counts_employees_in_each_role(self):
        table = db.get_workforce_demand("2027-Q4").set_index("role_name")
        self.assertEqual(table.loc["Analyst", "current_headcount"], 7)

    def test_roles_without_employees_have_zero_current_headcount(self):
        table = db.get_workforce_demand("2027-Q4").set_index("role_name")
        self.assertEqual(table.loc["Systems Analyst", "current_headcount"], 0)
        self.assertEqual(table.loc["Data Engineer", "current_headcount"], 0)

    def test_baseline_is_the_required_headcount_of_that_period(self):
        table = db.get_workforce_demand("2027-Q4").set_index("role_name")
        self.assertEqual(table.loc["Analyst", "baseline_required_headcount"], 8)
        later = db.get_workforce_demand("2028-Q4").set_index("role_name")
        self.assertEqual(later.loc["Systems Analyst", "baseline_required_headcount"], 5)

    def test_only_roles_in_the_selected_period_are_returned(self):
        self.assertEqual(db.get_workforce_demand("2028-Q4")["role_name"].tolist(), ["Systems Analyst"])

    def test_requirements_cover_every_role_regardless_of_period(self):
        # Data Engineer is not part of the 2028-Q4 demand, but it is still checked.
        table = db.get_all_role_skill_requirements()
        self.assertEqual(set(table["role_name"]), {"Systems Analyst", "Data Engineer"})
        self.assertEqual(len(table[table["role_name"] == "Systems Analyst"]), 4)


if __name__ == "__main__":
    unittest.main()
