import streamlit as st

from readiness import (
    MIN_PROFILE_COVERAGE,
    READY_NOW_MATCH_THRESHOLD,
    TRAIN_FIRST_MATCH_THRESHOLD,
    get_candidate_evidence_quality,
    get_candidate_internal_readiness,
    get_candidate_profile_coverage,
    get_opening_staffing_route,
)
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


def render_candidate_skill_detail(candidate_id: int, role_id: int):
    skill_details = get_target_role_skill_details(candidate_id, role_id)

    if skill_details.empty:
        st.info(
            "No skill requirements are currently defined for this role."
        )
        return

    sort_choice = st.radio(
        "Sort skills by",
        options=list(SKILL_SORT_OPTIONS),
        horizontal=True,
        key=f"skill_sort_{candidate_id}_{role_id}",
    )

    st.caption(
        f"{SKILL_SORT_OPTIONS[sort_choice]} "
        "Bar = recorded level, dark marker = required level. "
        "'Not recorded' does not mean the employee has no ability in that skill."
    )

    skills = [_skill_view(skill) for _, skill in skill_details.iterrows()]

    if sort_choice == "Status":
        skills.sort(
            key=lambda item: (
                STATUS_ORDER.index(item["status"]),
                -item["gap"],
                -item["importance"],
                item["skill_name"],
            )
        )
    else:
        skills.sort(
            key=lambda item: (-item["importance"], item["skill_name"])
        )

    for item in skills:
        required_level = item["required_level"]

        with st.container(border=True):
            title_col, badge_col = st.columns([3, 2])

            with title_col:
                st.markdown(f"**{item['skill_name']}**")

            with badge_col:
                st.markdown(
                    '<div style="text-align:right;">'
                    + _status_badge_html(item["status"])
                    + "&nbsp;"
                    + _importance_badge_html(item["importance"])
                    + "</div>",
                    unsafe_allow_html=True,
                )

            st.markdown(
                f"{item['current_text']} → needs "
                f"**L{required_level} {LEVEL_LABELS[required_level]}**"
            )
            st.markdown(
                _level_bar_html(item["current_level"], required_level),
                unsafe_allow_html=True,
            )


SKILL_SORT_OPTIONS = {
    "Importance": (
        "Most important to the role first (darker blue = more important)."
    ),
    "Status": (
        "Gaps first (largest gap first), then requirements met, "
        "then not recorded."
    ),
}

STATUS_ORDER = [
    "gap",
    "meets",
    "not_recorded",
]


def _skill_view(skill) -> dict:
    required_level = int(skill["required_level"])
    importance = int(skill["importance_level"])
    proficiency = skill["proficiency_level"]

    if proficiency is None or proficiency != proficiency:
        current_level = None
        current_text = "Not recorded"
        status = "not_recorded"
        gap = 0
    else:
        current_level = int(proficiency)
        current_text = f"L{current_level} {LEVEL_LABELS[current_level]}"
        gap = required_level - current_level
        status = "meets" if gap <= 0 else "gap"

    return {
        "skill_name": skill["skill_name"],
        "required_level": required_level,
        "importance": importance,
        "current_level": current_level,
        "current_text": current_text,
        "status": status,
        "gap": max(gap, 0),
    }


# Status: how the recorded level compares with the requirement.
# Orange = gap (the bar shows how large), green = met, gray = no evidence.
STATUS_BADGES = {
    "gap": ("Gap", "#FFEDD5", "#9A3412"),
    "meets": ("Meets requirement", "#DCFCE7", "#166534"),
    "not_recorded": ("Not recorded", "#F3F4F6", "#4B5563"),
}

# Importance: one blue scale with a clearly different shade per level,
# darker = more important to the role.
# Kept separate from the status colors so the two are not confused.
IMPORTANCE_BADGES = {
    5: ("#172554", "#FFFFFF"),
    4: ("#1D4ED8", "#FFFFFF"),
    3: ("#60A5FA", "#0B1F4D"),
    2: ("#BFDBFE", "#1E3A8A"),
    1: ("#F1F5F9", "#475569"),
}


def _badge_html(text: str, background: str, color: str) -> str:
    return (
        f'<span style="display:inline-block;padding:2px 10px;'
        f"border-radius:999px;font-size:0.8rem;font-weight:600;"
        f'background:{background};color:{color};white-space:nowrap;">'
        f"{text}</span>"
    )


def _status_badge_html(status: str) -> str:
    label, background, color = STATUS_BADGES[status]
    return _badge_html(label, background, color)


def _importance_badge_html(importance: int) -> str:
    background, color = IMPORTANCE_BADGES.get(
        importance, IMPORTANCE_BADGES[1]
    )
    return _badge_html(f"Importance {importance}/5", background, color)


def _level_bar_html(current_level, required_level: int) -> str:
    """
    Same bar as the employee view: filled = current level,
    dark marker = required level. A skill that is not recorded
    shows an empty bar.
    """
    current_pct = (current_level or 0) * 20
    required_pct = required_level * 20
    return (
        '<div style="position:relative;height:10px;background:#E5E7EB;'
        'border-radius:999px;margin:8px 0 6px 0;">'
        f'<div style="width:{current_pct}%;height:100%;background:#6B8EAD;'
        'border-radius:999px;"></div>'
        f'<div style="position:absolute;left:calc({required_pct}% - 2px);'
        "top:-3px;width:4px;height:16px;background:#374151;"
        'border-radius:2px;"></div></div>'
    )


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

        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

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

        metric_col4.metric(
            "Not recorded",
            int(candidate["not_recorded_skills"]),
        )

        not_recorded_skills = int(candidate["not_recorded_skills"])
        no_record_text = (
            "1 skill has no record"
            if not_recorded_skills == 1
            else f"{not_recorded_skills} skills have no record"
        )

        if evidence["code"] == "limited":
            st.warning(
                f"Not enough data: {no_record_text}. A low Skill Match "
                "here does not mean the employee lacks these skills."
            )
        elif not_recorded_skills:
            st.caption(
                f"{no_record_text}. Skill Match counts "
                f"{'it' if not_recorded_skills == 1 else 'them'} as 0, "
                f"but {'it is' if not_recorded_skills == 1 else 'they are'} "
                "not treated as a gap."
            )

        st.markdown(
            f"**Internal readiness: {readiness['label']}**"
        )
        st.caption(readiness["explanation"])

        st.caption(
            "Shared interest in this role "
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
        "Staffing route: where to look first, inside or outside the company. "
        "Internal readiness: how ready the best internal candidate is. "
        "These are simple rules anyone can check, not a prediction model, "
        "and the manager makes the decision."
    )

    with st.expander("How this is decided"):
        st.markdown(
            f"""
**1. Is there enough data?**
If fewer than {MIN_PROFILE_COVERAGE * 100:.0f}% of the role's skills are
recorded for an employee, the app does not judge them. Skills with no
record count as 0 in Skill Match, so if they alone could decide whether
someone qualifies, the app does not judge either.

**2. How ready is each employee?**
- **Ready Now:** Skill Match of {READY_NOW_MATCH_THRESHOLD:.0f}% or more,
  and at most one skill is 2+ levels short (never one of the most
  important skills, importance 4–5).
- **Train First:** Skill Match of {TRAIN_FIRST_MATCH_THRESHOLD:.0f}% or
  more, and at most one of the most important skills is 2+ levels short.
- Otherwise: the gap is larger.

**3. Where to look first?**
- **Internal Mobility:** someone is Ready Now or Train First.
- **More Evidence Needed:** no one qualifies yet, but someone could not be
  judged. Record more skills before hiring from outside.
- **External Hire:** everyone was judged and no one qualifies, or no
  employee shared interest in this role.
"""
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
