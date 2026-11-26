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
from i18n import department, level_label, readiness_text, route_text, t, tn
from views.skill_display import level_bar_html, skill_badges_html
from i18n_data import localized
from db import (
    get_manager_openings,
    get_visible_internal_candidates,
    get_opening_detail,
    get_target_role_skill_details,
)

# In Chinese (?lang=zh), role / skill / course names come back translated.
get_manager_openings = localized(get_manager_openings)
get_visible_internal_candidates = localized(get_visible_internal_candidates)
get_opening_detail = localized(get_opening_detail)
get_target_role_skill_details = localized(get_target_role_skill_details)


DEPARTMENT_COLORS = {
    "Human Resources": "#F8D7DA",
    "Information Technology": "#D6E4FF",
    "Product & Engineering": "#D9F2E6",
    "Business Operations": "#FCE8C3",
}


def render_candidate_skill_detail(candidate_id: int, role_id: int):
    skill_details = get_target_role_skill_details(candidate_id, role_id)

    if skill_details.empty:
        st.info(
            t("no_role_requirements")
        )
        return

    sort_choice = st.radio(
        t("sort_skills_by"),
        options=list(SKILL_SORT_OPTIONS),
        format_func=lambda value: t(SKILL_SORT_LABELS[value]),
        horizontal=True,
        key=f"skill_sort_{candidate_id}_{role_id}",
    )

    st.caption(
        t(SKILL_SORT_OPTIONS[sort_choice])
        + " "
        + t("mgr_bar_caption").strip()
    )

    skills = [_skill_view(skill) for _, skill in skill_details.iterrows()]

    if sort_choice == "Gap size":
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
                    skill_badges_html(
                        item["importance"],
                        item["status"] == "not_recorded",
                    ),
                    unsafe_allow_html=True,
                )

            st.markdown(
                t(
                    "needs_level",
                    current=item["current_text"],
                    level=required_level,
                    label=level_label(required_level),
                )
            )
            st.markdown(
                level_bar_html(item["current_level"], required_level),
                unsafe_allow_html=True,
            )


# Stored values stay in English (widget state); text comes from i18n.
SKILL_SORT_OPTIONS = {
    "Importance": "sort_importance_caption",
    "Gap size": "sort_gap_caption",
}

SKILL_SORT_LABELS = {
    "Importance": "sort_importance",
    "Gap size": "sort_gap",
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
        current_text = t("not_recorded")
        status = "not_recorded"
        gap = 0
    else:
        current_level = int(proficiency)
        current_text = f"L{current_level} {level_label(current_level)}"
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


def render_candidate_card(candidate, role_id: int):
    coverage = get_candidate_profile_coverage(candidate)
    evidence = get_candidate_evidence_quality(candidate)
    readiness = get_candidate_internal_readiness(candidate)

    with st.container(border=True):
        st.markdown(f"### {candidate['employee_name']}")
        st.caption(
            f"{candidate['current_role']} • "
            f"{department(candidate['current_department'])}"
        )

        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

        metric_col1.metric(
            t("skill_match"),
            f"{candidate['match_percent']:.1f}%",
        )

        metric_col2.metric(
            t("profile_coverage"),
            f"{coverage * 100:.0f}%",
        )

        metric_col3.metric(
            t("skills_to_develop"),
            int(candidate["skills_to_develop"]),
        )

        metric_col4.metric(
            t("not_recorded"),
            int(candidate["not_recorded_skills"]),
        )

        not_recorded_skills = int(candidate["not_recorded_skills"])
        no_record_text = tn("no_record", not_recorded_skills)

        if evidence["code"] == "limited":
            st.warning(
                t("not_enough_data", no_record=no_record_text)
            )
        elif not_recorded_skills:
            st.caption(
                tn(
                    "no_record_note",
                    not_recorded_skills,
                    no_record=no_record_text,
                )
            )

        readiness_label, readiness_explanation = readiness_text(readiness)

        st.markdown(
            t("internal_readiness_line", label=readiness_label)
        )
        st.caption(readiness_explanation)

        st.caption(
            t("interest_shared_on", date=candidate["interest_shared_date"])
        )

        with st.expander(
            t("view_match_detail"),
            expanded=False,
        ):
            render_candidate_skill_detail(
                int(candidate["employee_id"]),
                role_id,
            )


def render_opening_decision_support(candidates):
    route = get_opening_staffing_route(candidates)

    route_label, route_readiness, route_explanation = route_text(route)

    st.markdown("### " + t("decision_support"))

    col1, col2 = st.columns(2)

    with col1:
        st.caption(t("staffing_route"))
        st.markdown(f"### {route_label}")

    with col2:
        st.caption(t("internal_readiness"))
        if route_readiness:
            st.markdown(f"### {route_readiness}")
        else:
            st.markdown("### —")

    st.info(route_explanation)

    st.caption(
        t("decision_caption")
    )

    with st.expander(t("how_decided")):
        st.markdown(
            t(
                "how_decided_body",
                coverage=f"{MIN_PROFILE_COVERAGE * 100:.0f}",
                ready=f"{READY_NOW_MATCH_THRESHOLD:.0f}",
                train=f"{TRAIN_FIRST_MATCH_THRESHOLD:.0f}",
            )
        )


def render_opening_staffing(manager_id: int, opening_id: int):
    opening_df = get_opening_detail(
        manager_id,
        opening_id,
    )

    if opening_df.empty:
        st.error(
            t("opening_unavailable")
        )
        return

    opening = opening_df.iloc[0]
    department_name = opening["department_name"]
    department_label = department(department_name)
    department_color = DEPARTMENT_COLORS.get(
        department_name,
        "#E5E7EB",
    )

    header_col, badge_col = st.columns([4, 2])

    with header_col:
        st.subheader(opening["role_name"])
        st.caption(
            t(
                "opening_meta",
                level=int(opening["level"]),
                date=opening["open_date"],
                headcount=int(opening["headcount"]),
            )
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
                    {department_label}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if opening["role_description"]:
        st.write(opening["role_description"])

    if opening["status"] == "paused":
        st.warning(
            t("req_paused")
        )
        return

    st.divider()

    candidates = get_visible_internal_candidates(
        manager_id,
        opening_id,
    )

    render_opening_decision_support(candidates)

    st.divider()

    st.markdown("### " + t("visible_interest"))

    st.caption(
        t("visible_interest_caption")
    )

    if candidates.empty:
        st.info(
            t("no_visible_interest")
        )
        return

    st.caption(
        tn("visible_count", len(candidates))
    )

    for _, candidate in candidates.iterrows():
        render_candidate_card(
            candidate,
            int(opening["role_id"]),
        )


def render_manager_staffing():
    st.header(t("manager_title"))

    st.write(
        t("manager_intro")
    )

    st.info(
        t("manager_info")
    )

    manager_id = st.session_state["manager_id"]
    openings = get_manager_openings(manager_id)

    if openings.empty:
        st.info(
            t("no_requisitions")
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
        t("open_reqs"),
        open_count,
    )
    count_col2.metric(
        t("paused_reqs"),
        paused_count,
    )

    st.divider()

    opening_options = {}

    for row in openings.itertuples():
        status_label = (
            t("status_open")
            if row.status == "open"
            else t("status_paused")
        )

        label = (
            f"{row.role_name} — "
            f"{status_label}"
        )

        opening_options[label] = row.opening_id

    selected_opening_label = st.selectbox(
        t("select_req"),
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
