"""
Internal readiness and staffing route: the rules in the README table, tested at the boundaries.
"""

import unittest

import pandas as pd

import support  # noqa: F401  (sets up the import path)
from readiness import (
    MIN_PROFILE_COVERAGE,
    READY_NOW_MATCH_THRESHOLD,
    TRAIN_FIRST_MATCH_THRESHOLD,
    get_candidate_evidence_quality,
    get_candidate_internal_readiness,
    get_candidate_profile_coverage,
    get_opening_staffing_route,
)


def candidate(
    match=90.0,
    priority=0,
    significant=0,
    met=8,
    to_develop=2,
    not_recorded=0,
):
    """A candidate row with 10 required skills unless told otherwise."""
    return {
        "match_percent": match,
        "priority_gaps": priority,
        "significant_gaps": significant,
        "skills_met": met,
        "skills_to_develop": to_develop,
        "not_recorded_skills": not_recorded,
    }


def readiness_code(**kwargs):
    return get_candidate_internal_readiness(candidate(**kwargs))["code"]


class TestThresholdsMatchTheReadme(unittest.TestCase):
    def test_documented_defaults(self):
        self.assertEqual(MIN_PROFILE_COVERAGE, 0.70)
        self.assertEqual(READY_NOW_MATCH_THRESHOLD, 80.0)
        self.assertEqual(TRAIN_FIRST_MATCH_THRESHOLD, 60.0)


class TestProfileCoverage(unittest.TestCase):
    def test_share_of_required_skills_with_a_record(self):
        self.assertAlmostEqual(
            get_candidate_profile_coverage(candidate(met=5, to_develop=5, not_recorded=2)), 0.8
        )

    def test_full_and_empty_profiles(self):
        self.assertEqual(get_candidate_profile_coverage(candidate(not_recorded=0)), 1.0)
        self.assertEqual(
            get_candidate_profile_coverage(candidate(met=0, to_develop=10, not_recorded=10)), 0.0
        )

    def test_role_without_required_skills_has_zero_coverage(self):
        self.assertEqual(
            get_candidate_profile_coverage(candidate(met=0, to_develop=0, not_recorded=0)), 0.0
        )


class TestEvidenceQuality(unittest.TestCase):
    def test_exactly_70_percent_is_sufficient(self):
        # 10 required skills, 3 not recorded: 7 / 10 = 70%
        result = get_candidate_evidence_quality(candidate(not_recorded=3))
        self.assertEqual(result["code"], "sufficient")

    def test_below_70_percent_is_limited(self):
        result = get_candidate_evidence_quality(candidate(not_recorded=4))
        self.assertEqual(result["code"], "limited")


class TestInternalReadiness(unittest.TestCase):
    def test_ready_now_at_the_boundary(self):
        self.assertEqual(readiness_code(match=80.0, priority=0, significant=1), "ready_now")

    def test_just_below_80_is_train_first(self):
        self.assertEqual(readiness_code(match=79.9, priority=0, significant=0), "train_first")

    def test_two_significant_gaps_block_ready_now(self):
        self.assertEqual(readiness_code(match=95.0, priority=0, significant=2), "train_first")

    def test_any_priority_gap_blocks_ready_now(self):
        self.assertEqual(readiness_code(match=95.0, priority=1, significant=1), "train_first")

    def test_train_first_boundary_at_60(self):
        self.assertEqual(readiness_code(match=60.0, priority=0), "train_first")
        self.assertEqual(readiness_code(match=59.9, priority=0), "larger_gap")

    def test_train_first_allows_at_most_one_priority_gap(self):
        self.assertEqual(readiness_code(match=70.0, priority=1), "train_first")
        self.assertEqual(readiness_code(match=70.0, priority=2), "larger_gap")

    def test_train_first_has_no_cap_on_significant_gaps(self):
        self.assertEqual(readiness_code(match=70.0, priority=0, significant=6), "train_first")

    def test_high_score_with_too_many_priority_gaps_is_still_larger_gap(self):
        # The README calls this case out explicitly.
        self.assertEqual(readiness_code(match=85.0, priority=2), "larger_gap")

    def test_limited_evidence_is_not_assessed_even_with_a_perfect_score(self):
        self.assertEqual(readiness_code(match=100.0, not_recorded=4), "not_assessed")

    def test_every_result_explains_itself(self):
        for kwargs in (
            dict(),
            dict(match=70.0),
            dict(match=10.0),
            dict(not_recorded=9),
        ):
            result = get_candidate_internal_readiness(candidate(**kwargs))
            self.assertTrue(result["label"])
            self.assertTrue(result["explanation"])


class TestStaffingRoute(unittest.TestCase):
    @staticmethod
    def route(*candidates):
        return get_opening_staffing_route(pd.DataFrame(list(candidates)))

    def test_no_visible_interest_means_external_hire(self):
        result = get_opening_staffing_route(pd.DataFrame())
        self.assertEqual(result["route_code"], "external_hire")

    def test_ready_now_means_internal_mobility(self):
        result = self.route(candidate(match=90.0))
        self.assertEqual(result["route_code"], "internal_mobility")
        self.assertEqual(result["readiness_label"], "Ready Now")

    def test_train_first_means_internal_mobility(self):
        result = self.route(candidate(match=70.0))
        self.assertEqual(result["route_code"], "internal_mobility")
        self.assertEqual(result["readiness_label"], "Train First")

    def test_ready_now_outranks_train_first(self):
        result = self.route(candidate(match=70.0), candidate(match=90.0))
        self.assertEqual(result["readiness_label"], "Ready Now")

    def test_only_unassessable_candidates_need_more_evidence(self):
        result = self.route(candidate(not_recorded=8), candidate(not_recorded=9))
        self.assertEqual(result["route_code"], "more_evidence_needed")

    def test_a_train_first_candidate_beats_missing_evidence_elsewhere(self):
        result = self.route(candidate(not_recorded=8), candidate(match=70.0))
        self.assertEqual(result["route_code"], "internal_mobility")

    def test_missing_evidence_is_not_treated_as_a_poor_fit(self):
        result = self.route(candidate(match=20.0), candidate(not_recorded=8))
        self.assertEqual(result["route_code"], "more_evidence_needed")

    def test_external_hire_only_when_everyone_is_assessed_and_none_qualify(self):
        result = self.route(candidate(match=20.0), candidate(match=40.0, priority=3))
        self.assertEqual(result["route_code"], "external_hire")


if __name__ == "__main__":
    unittest.main()
