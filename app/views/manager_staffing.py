import streamlit as st

from db import (
    get_manager_openings,
    get_visible_internal_candidates,
    get_opening_detail,
    get_target_role_skill_details,
)


DEPARTMENT_COLORS = {
    "Human Resources": "#F8D7DA",
    "Information Technology": "#D6E4FF",
    "Product & Engineering": "#D9F2E6",
    "Business Operations": "#FCE8C3",
}


LEVEL_LABELS = {
    1: "Foundational",
    2: "Basic",
    3: "Working",
    4: "Advanced",
    5: "Expert",
}


MIN_PROFILE_COVERAGE = 0.70
READY_NOW_MATCH_THRESHOLD = 80.0
TRAIN_FIRST_MATCH_THRESHOLD = 60.0


def get_candidate_profile_coverage(candidate):
    total_required_skills = (
        int(candidate["skills_met"])
        + int(candidate["skills_to_develop"])
    )

    if total_required_skills <= 0:
        return 0.0

    recorded_required_skills = (
        total_required_skills
        - int(candidate["not_recorded_skills"])
    )

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
    priority_gaps = int(candidate["priority_gaps"])
    significant_gaps = int(candidate["significant_gaps"])

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
                "recorded skill evidence to assess internal readiness reliably."
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


def render_candidate_skill_detail(candidate_id: int, role_id: int):
    skill_details = get_target_role_skill_details(candidate_id, role_id)

    if skill_details.empty:
        st.info(
            "No skill requirements are currently defined for this role."
        )
        return

    st.caption(
        "Current proficiency is based only on skills recorded in WorkforceIQ. "
        "'Not recorded' does not mean the employee has no ability in that skill."
    )

    for _, skill in skill_details.iterrows():
        required_level = int(skill["required_level"])
        importance = int(skill["importance_level"])
        proficiency = skill["proficiency_level"]

        if proficiency is None or proficiency != proficiency:
            current_text = "Not recorded"
            gap_label = "Not recorded"
        else:
            current_level = int(proficiency)
            current_text = (
                f"Level {current_level} — {LEVEL_LABELS[current_level]}"
            )
            gap = required_level - current_level

            if gap <= 0:
                gap_label = "Meets requirement"
            elif gap == 1:
                gap_label = "Small gap"
            elif importance >= 4:
                gap_label = "Priority gap"
            else:
                gap_label = "Significant gap"

        with st.container(border=True):
            left_col, right_col = st.columns([3, 2])

            with left_col:
                st.markdown(f"**{skill['skill_name']}**")
                st.caption(skill["skill_category"])

            with right_col:
                st.caption(f"Importance {importance}/5")

            current_col, required_col = st.columns(2)

            with current_col:
                st.caption("Current")
                st.write(current_text)

            with required_col:
                st.caption("Required")
                st.write(
                    f"Level {required_level} — "
                    f"{LEVEL_LABELS[required_level]}"
                )

            st.caption(gap_label)


def render_candidate_card(candidate, role_id: int):
    coverage = get_candidate_profile_coverage(candidate)
    evidence = get_candidate_evidence_quality(candidate)
    readiness = get_candidate_internal_readiness(candidate)

    with st.container(border=True):
        st.markdown(f"### {candidate['employee_name']}")
        st.caption(
            f"{candidate['current_role']} • "
            f"{candidate['current_department']}"
        )

        metric_col1, metric_col2, metric_col3 = st.columns(3)

        metric_col1.metric(
            "Skill Match",
            f"{candidate['match_percent']:.1f}%",
        )

        metric_col2.metric(
            "Profile Coverage",
            f"{coverage * 100:.0f}%",
        )

        metric_col3.metric(
            "Skills to develop",
            int(candidate["skills_to_develop"]),
        )

        if evidence["code"] == "limited":
            not_recorded_skills = int(
                candidate["not_recorded_skills"]
            )

            skill_noun = (
                "skill"
                if not_recorded_skills == 1
                else "skills"
            )

            verb = (
                "is"
                if not_recorded_skills == 1
                else "are"
            )

            st.warning(
                "Evidence quality: Limited. "
                f"{not_recorded_skills} required "
                f"{skill_noun} {verb} not recorded. "
                "The match score should not be interpreted "
                "as evidence that the employee lacks those skills."
            )
        else:
            st.caption("Evidence quality: Sufficient")

        st.markdown(
            f"**Internal readiness: {readiness['label']}**"
        )
        st.caption(readiness["explanation"])

        st.caption(
            "Explicitly shared interest in this exact role "
            f"on {candidate['interest_shared_date']}."
        )

        with st.expander(
            "View Skill Match Detail",
            expanded=False,
        ):
            render_candidate_skill_detail(
                int(candidate["employee_id"]),
                role_id,
            )


def render_opening_decision_support(candidates):
    route = get_opening_staffing_route(candidates)

    st.markdown("### Staffing Decision Support")

    col1, col2 = st.columns(2)

    with col1:
        st.caption("Staffing Route")
        st.markdown(f"### {route['route_label']}")

    with col2:
        st.caption("Internal Readiness")
        if route["readiness_label"]:
            st.markdown(f"### {route['readiness_label']}")
        else:
            st.markdown("### —")

    st.info(route["explanation"])

    st.caption(
        "The staffing route answers where the talent should primarily come from. "
        "Internal readiness separately describes whether an internal candidate "
        "appears ready now or should train first."
    )

    st.caption(
        "This is a transparent MVP heuristic based on recorded skills, "
        "profile coverage, and employee-controlled visibility. "
        "It is not a predictive hiring model and does not make "
        "an employment decision."
    )

    with st.expander(
        "How this decision support is determined"
    ):
        st.write("**Step 1 — Evidence quality**")
        st.write(
            f"Profile evidence is treated as limited when fewer than "
            f"{MIN_PROFILE_COVERAGE * 100:.0f}% of required skills "
            "have recorded proficiency."
        )

        st.write("**Step 2 — Internal readiness**")
        st.write(
            f"Ready Now: at least "
            f"{READY_NOW_MATCH_THRESHOLD:.0f}% skill match, "
            "no priority gaps, and at most one significant gap."
        )
        st.write(
            f"Train First: at least "
            f"{TRAIN_FIRST_MATCH_THRESHOLD:.0f}% skill match "
            "and at most one priority gap."
        )

        st.write("**Step 3 — Staffing route**")
        st.write(
            "Internal Mobility is recommended when at least one visible "
            "internal candidate is Ready Now or Train First."
        )
        st.write(
            "More Evidence Needed is shown when no visible candidate is "
            "Ready Now or Train First and at least one candidate still has "
            "insufficient recorded skill evidence for a reliable assessment."
        )
        st.write(
            "External Hire is recommended only when no visible candidate is "
            "Ready Now or Train First and all visible candidates have "
            "sufficient evidence, or when no internal interest is visible."
        )


def render_opening_staffing(manager_id: int, opening_id: int):
    opening_df = get_opening_detail(
        manager_id,
        opening_id,
    )

    if opening_df.empty:
        st.error(
            "This opening is not available for the selected manager."
        )
        return

    opening = opening_df.iloc[0]
    department = opening["department_name"]
    department_color = DEPARTMENT_COLORS.get(
        department,
        "#E5E7EB",
    )

    header_col, badge_col = st.columns([4, 2])

    with header_col:
        st.subheader(opening["role_name"])
        st.caption(
            f"Role Level {int(opening['level'])} "
            f"• Opened {opening['open_date']} "
            f"• Headcount {int(opening['headcount'])}"
        )

    with badge_col:
        st.markdown(
            f"""
            <div style="
                text-align: right;
                padding-top: 4px;
            ">
                <span style="
                    display: inline-block;
                    background-color: {department_color};
                    padding: 5px 10px;
                    border-radius: 999px;
                    font-size: 0.8rem;
                    font-weight: 600;
                    white-space: nowrap;
                ">
                    {department}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if opening["role_description"]:
        st.write(opening["role_description"])

    if opening["status"] == "paused":
        st.warning(
            "This requisition is currently paused. "
            "Internal candidate search is disabled "
            "until the opening is active again."
        )
        return

    st.divider()

    candidates = get_visible_internal_candidates(
        manager_id,
        opening_id,
    )

    render_opening_decision_support(candidates)

    st.divider()

    st.markdown("### Visible Internal Interest")

    st.caption(
        "Only employees who explicitly make this career interest visible "
        "to relevant opening managers are shown here. "
        "Private interests are not visible to managers."
    )

    if candidates.empty:
        st.info(
            "No employees have currently shared this exact career interest "
            "with the relevant opening manager."
        )
        return

    st.caption(
        f"{len(candidates)} visible internal candidate"
        f"{'' if len(candidates) == 1 else 's'}, "
        "ordered by current skill match."
    )

    for _, candidate in candidates.iterrows():
        render_candidate_card(
            candidate,
            int(opening["role_id"]),
        )


def render_manager_staffing():
    st.header("Manager Staffing")

    st.write(
        "Review your current requisitions and identify employees who have "
        "explicitly shared interest in the exact role."
    )

    st.info(
        "WorkforceIQ supports staffing decisions; "
        "it does not automatically select, promote, or transfer employees."
    )

    manager_id = st.session_state["manager_id"]
    openings = get_manager_openings(manager_id)

    if openings.empty:
        st.info(
            "No open or paused requisitions are currently assigned "
            "to this manager."
        )
        return

    open_count = int(
        (openings["status"] == "open").sum()
    )
    paused_count = int(
        (openings["status"] == "paused").sum()
    )

    count_col1, count_col2 = st.columns(2)

    count_col1.metric(
        "Open requisitions",
        open_count,
    )
    count_col2.metric(
        "Paused requisitions",
        paused_count,
    )

    st.divider()

    opening_options = {}

    for row in openings.itertuples():
        status_label = (
            "Open"
            if row.status == "open"
            else "Paused"
        )

        label = (
            f"{row.role_name} — "
            f"{status_label}"
        )

        opening_options[label] = row.opening_id

    selected_opening_label = st.selectbox(
        "Select requisition",
        options=list(opening_options.keys()),
    )

    selected_opening_id = opening_options[
        selected_opening_label
    ]

    st.divider()

    render_opening_staffing(
        manager_id,
        selected_opening_id,
    )
