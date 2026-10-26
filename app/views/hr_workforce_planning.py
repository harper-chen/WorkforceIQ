import pandas as pd
import streamlit as st

from planning import (
    build_unaddressed_capability_gaps,
    build_workforce_plan,
)
from db import (
    get_planning_periods,
    get_workforce_demand,
    get_internal_training_outcomes,
    get_all_role_skill_requirements,
)


# =========================================================
# Session State
# =========================================================

def planned_headcount_state_key(planning_period: str) -> str:
    return (
        "hr_planned_headcount_"
        + planning_period.replace("-", "_")
    )


def editor_version_state_key(planning_period: str) -> str:
    return (
        "hr_workforce_editor_version_"
        + planning_period.replace("-", "_")
    )


def initialize_planned_headcount_state(
    planning_period: str,
    demand: pd.DataFrame,
) -> str:
    """
    Planned HC starts from the baseline future-demand value
    stored in the database.

    Baseline is intentionally hidden from the main UI.
    It is used only as:
    1. the default Planned HC
    2. the value restored by Reset to baseline
    """
    state_key = planned_headcount_state_key(
        planning_period
    )

    if state_key not in st.session_state:
        st.session_state[state_key] = {
            int(row["role_id"]):
                int(
                    row[
                        "baseline_required_headcount"
                    ]
                )
            for _, row in demand.iterrows()
        }

    version_key = editor_version_state_key(
        planning_period
    )

    if version_key not in st.session_state:
        st.session_state[version_key] = 0

    return state_key


def reset_planned_headcount_to_baseline(
    state_key: str,
    demand: pd.DataFrame,
):
    st.session_state[state_key] = {
        int(row["role_id"]):
            int(
                row[
                    "baseline_required_headcount"
                ]
            )
        for _, row in demand.iterrows()
    }


# =========================================================
# Main Page
# =========================================================

def render_hr_workforce_planning():
    st.header(
        "HR / Workforce Planning"
    )

    st.write(
        "Plan future headcount, identify workforce gaps, "
        "and surface capability needs that current internal "
        "learning cannot fully support."
    )

    st.info(
        "This workspace focuses on aggregate workforce-planning "
        "needs rather than individual employee staffing decisions."
    )

    periods = get_planning_periods()

    if periods.empty:
        st.warning(
            "No future workforce-demand data is available."
        )
        return

    selected_period = st.selectbox(
        "Planning Period",
        periods[
            "planning_period"
        ].tolist(),
    )

    demand = get_workforce_demand(
        selected_period
    )

    if demand.empty:
        st.warning(
            "No workforce-demand data is available "
            "for the selected planning period."
        )
        return

    role_skill_requirements = (
        get_all_role_skill_requirements()
    )

    training_outcomes = (
        get_internal_training_outcomes()
    )

    state_key = (
        initialize_planned_headcount_state(
            selected_period,
            demand,
        )
    )

    # =====================================================
    # 1. Workforce Demand & Gaps
    # =====================================================

    st.subheader(
        "1. Workforce Demand & Gaps"
    )

    st.caption(
        "Planned HC is the future target headcount for each role. "
        "Edit it to test a different workforce scenario. "
        "Workforce Gap is recalculated from Planned HC minus Current HC."
    )

    control_col1, control_col2 = st.columns(
        [1.4, 2.6]
    )

    with control_col1:
        if st.button(
            "Reset planned headcount to baseline",
            key=(
                "reset_"
                + state_key
            ),
        ):
            reset_planned_headcount_to_baseline(
                state_key,
                demand,
            )

            version_key = editor_version_state_key(
                selected_period
            )

            st.session_state[
                version_key
            ] += 1

            st.rerun()

    with control_col2:
        show_no_gap_roles = st.checkbox(
            "Show roles with no gap",
            value=False,
            key=(
                "show_no_gap_"
                + selected_period
            ),
        )

    workforce_plan = build_workforce_plan(
        demand,
        st.session_state[
            state_key
        ],
    )

    gap_only = workforce_plan[
        workforce_plan[
            "Workforce Gap"
        ] > 0
    ].copy()

    table_source = (
        workforce_plan.copy()
        if show_no_gap_roles
        else gap_only.copy()
    )

    if table_source.empty:
        st.success(
            "No positive workforce gaps are currently "
            "identified under this scenario."
        )
    else:
        editor_input = table_source[
            [
                "role_id",
                "Role",
                "Current HC",
                "Planned HC",
                "Workforce Gap",
            ]
        ].copy()

        # Build the editor key from:
        # 1. the selected planning period,
        # 2. whether all roles or only gap roles are shown,
        # 3. a reset version, and
        # 4. the exact set of visible role IDs.
        #
        # This prevents Streamlit from reusing row-position edits
        # after a role disappears from the gap-only table, and it
        # ensures Reset to baseline starts from a fresh editor state.
        version_key = editor_version_state_key(
            selected_period
        )

        visible_role_signature = "-".join(
            str(int(role_id))
            for role_id in editor_input[
                "role_id"
            ].tolist()
        )

        editor_scope = (
            "all"
            if show_no_gap_roles
            else "gap"
        )

        editor_key = (
            f"workforce_editor_{selected_period}_"
            f"{editor_scope}_"
            f"v{st.session_state[version_key]}_"
            f"{visible_role_signature}"
        )

        edited_table = st.data_editor(
            editor_input,
            hide_index=True,
            use_container_width=True,
            disabled=[
                "role_id",
                "Role",
                "Current HC",
                "Workforce Gap",
            ],
            column_config={
                "role_id": None,
                "Role":
                    st.column_config.TextColumn(
                        "Role",
                        width="large",
                    ),
                "Current HC":
                    st.column_config.NumberColumn(
                        "Current HC",
                        width="small",
                        format="%d",
                    ),
                "Planned HC":
                    st.column_config.NumberColumn(
                        "Planned HC ✎",
                        min_value=0,
                        step=1,
                        format="%d",
                        width="small",
                        help=(
                            "Editable future target headcount."
                        ),
                    ),
                "Workforce Gap":
                    st.column_config.NumberColumn(
                        "Workforce Gap",
                        width="small",
                        format="%d",
                    ),
            },
            key=editor_key,
        )

        planned_headcount_changed = False

        for _, row in edited_table.iterrows():
            role_id = int(
                row["role_id"]
            )

            new_planned_headcount = int(
                row["Planned HC"]
            )

            if (
                st.session_state[
                    state_key
                ][role_id]
                != new_planned_headcount
            ):
                st.session_state[
                    state_key
                ][role_id] = (
                    new_planned_headcount
                )

                planned_headcount_changed = True

        # st.data_editor returns the edited Planned HC immediately,
        # but the disabled Workforce Gap column was calculated from
        # the previous render. Rerun only when a value actually
        # changes so the derived gap is refreshed right away.
        if planned_headcount_changed:
            st.rerun()

    # =====================================================
    # 2. Unaddressed Capability Gaps
    # =====================================================

    st.divider()

    st.subheader(
        "2. Unaddressed Capability Gaps"
    )

    st.caption(
        "The skill requirements of every existing role are evaluated "
        "here, independent of the headcount scenario above. A skill "
        "appears only when the current internal learning catalog "
        "cannot reach the required proficiency level."
    )

    unaddressed = (
        build_unaddressed_capability_gaps(
            role_skill_requirements,
            training_outcomes,
        )
    )

    if unaddressed.empty:
        st.success(
            "Current internal learning coverage is sufficient "
            "for the skill requirements of all existing roles."
        )
    else:
        st.warning(
            "These role capability needs are not fully supported "
            "by the current internal learning catalog."
        )

        display_table = unaddressed.copy()

        display_table["Available Internal Training"] = (
            display_table["Available Internal Training"]
            .str.replace("\n", "<br>", regex=False)
        )

        st.markdown(
            display_table.to_html(
                index=False,
                escape=False,
            ),
            unsafe_allow_html=True,
        )

        st.caption(
            "Available Internal Training shows the strongest course "
            "outcome currently available for each skill. Multiple "
            "courses are shown when they reach the same highest "
            "outcome level. This section identifies planning risks "
            "rather than prescribing a single solution."
        )
