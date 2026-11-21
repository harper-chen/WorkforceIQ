"""
Internal-readiness and staffing-route rules (no Streamlit, no database).

These are the heuristics described in the README. They live in their own module so
they can be unit-tested directly; the Manager view only imports and displays them.
Thresholds are prototype-level defaults, not validated against real mobility outcomes.
"""

MIN_PROFILE_COVERAGE = 0.70
READY_NOW_MATCH_THRESHOLD = 80.0
TRAIN_FIRST_MATCH_THRESHOLD = 60.0


def get_candidate_profile_coverage(candidate):
    # Every required skill is exactly one of: met, to develop (a recorded
    # gap), or not recorded.
    recorded_required_skills = (
        int(candidate["skills_met"])
        + int(candidate["skills_to_develop"])
    )
    total_required_skills = (
        recorded_required_skills
        + int(candidate["not_recorded_skills"])
    )

    if total_required_skills <= 0:
        return 0.0

    return recorded_required_skills / total_required_skills


def get_candidate_evidence_quality(candidate):
    coverage = get_candidate_profile_coverage(candidate)

    if coverage < MIN_PROFILE_COVERAGE:
        return {
            "code": "limited",
            "label": "Limited",
            "explanation": (
                "Too many required skills are not recorded "
                "to support a reliable readiness assessment."
            ),
        }

    return {
        "code": "sufficient",
        "label": "Sufficient",
        "explanation": (
            "Enough required skills are recorded to support "
            "a preliminary readiness assessment."
        ),
    }


def get_best_case_match_percent(candidate):
    """
    Skill Match if every not-recorded skill met its requirement.

    Falls back to the recorded Skill Match when the value is not
    available or there are no missing records.
    """
    match_percent = float(candidate["match_percent"])

    if int(candidate["not_recorded_skills"]) == 0:
        return match_percent

    best_case = candidate.get("match_percent_if_unrecorded_met")

    if best_case is None or best_case != best_case:  # None or NaN
        return match_percent

    return max(float(best_case), match_percent)


def get_candidate_internal_readiness(candidate):
    evidence = get_candidate_evidence_quality(candidate)

    if evidence["code"] == "limited":
        return {
            "code": "not_assessed",
            "label": "Not assessed",
            "explanation": (
                "Internal readiness is not classified because "
                "profile evidence is currently limited."
            ),
        }

    match_percent = float(candidate["match_percent"])
    best_case_match = get_best_case_match_percent(candidate)
    priority_gaps = int(candidate["priority_gaps"])
    significant_gaps = int(candidate["significant_gaps"])

    recorded_result = _classify_recorded_profile(
        match_percent,
        priority_gaps,
        significant_gaps,
    )
    best_case_result = _classify_recorded_profile(
        best_case_match,
        priority_gaps,
        significant_gaps,
    )

    if recorded_result["code"] == best_case_result["code"]:
        return recorded_result

    # Missing records score 0 in Skill Match, so they can only pull a
    # result down. If they are what keeps the employee out of Train
    # First, the missing evidence would be deciding the result (and could
    # push the opening toward an external hire), so it is not classified.
    if recorded_result["code"] == "larger_gap":
        return {
            "code": "not_assessed",
            "label": "Not assessed",
            "explanation": (
                "Internal readiness is not classified because the "
                "skills that are not recorded could change the result: "
                f"Skill Match is {match_percent:.1f}% with them counted as 0 "
                f"and up to {best_case_match:.1f}% if they meet requirements."
            ),
        }

    # Train First on recorded skills alone, Ready Now in the best case:
    # keep the cautious result and say what would change it.
    return {
        **recorded_result,
        "explanation": (
            recorded_result["explanation"]
            + " Recording the missing skills could show the employee "
            "is Ready Now."
        ),
    }


def _classify_recorded_profile(match_percent, priority_gaps, significant_gaps):
    if (
        match_percent >= READY_NOW_MATCH_THRESHOLD
        and priority_gaps == 0
        and significant_gaps <= 1
    ):
        return {
            "code": "ready_now",
            "label": "Ready Now",
            "explanation": (
                "Recorded skills are closely aligned with the role, "
                "with no priority gap and at most one significant gap."
            ),
        }

    if (
        match_percent >= TRAIN_FIRST_MATCH_THRESHOLD
        and priority_gaps <= 1
    ):
        return {
            "code": "train_first",
            "label": "Train First",
            "explanation": (
                "The employee shows meaningful alignment, "
                "but targeted development is recommended before transfer."
            ),
        }

    return {
        "code": "larger_gap",
        "label": "Larger development gap",
        "explanation": (
            "The recorded skill profile currently shows a larger "
            "development need relative to the role."
        ),
    }


def get_opening_staffing_route(candidates):
    if candidates.empty:
        return {
            "route_code": "external_hire",
            "route_label": "External Hire",
            "readiness_label": None,
            "explanation": (
                "No employee has currently shared interest in this exact role "
                "with the relevant opening manager."
            ),
        }

    readiness_codes = [
        get_candidate_internal_readiness(candidate)["code"]
        for _, candidate in candidates.iterrows()
    ]

    if "ready_now" in readiness_codes:
        return {
            "route_code": "internal_mobility",
            "route_label": "Internal Mobility",
            "readiness_label": "Ready Now",
            "explanation": (
                "At least one visible internal candidate appears ready "
                "for further transfer consideration based on recorded skills."
            ),
        }

    if "train_first" in readiness_codes:
        return {
            "route_code": "internal_mobility",
            "route_label": "Internal Mobility",
            "readiness_label": "Train First",
            "explanation": (
                "At least one visible internal candidate appears suitable "
                "for a train-then-transfer pathway."
            ),
        }

    if "not_assessed" in readiness_codes:
        return {
            "route_code": "more_evidence_needed",
            "route_label": "More Evidence Needed",
            "readiness_label": None,
            "explanation": (
                "Some visible internal candidates do not have enough "
                "recorded skill evidence to assess internal readiness reliably, "
                "or their missing records could change the result."
            ),
        }

    return {
        "route_code": "external_hire",
        "route_label": "External Hire",
        "readiness_label": None,
        "explanation": (
            "Visible internal candidates have sufficient evidence, "
            "but none currently meet the Ready Now or Train First criteria."
        ),
    }
