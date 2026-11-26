import streamlit as st

from i18n import render_language_switch, t, tn
from db import (
    get_employee_list,
    get_manager_list,
    reset_demo_database,
)

from views.my_skills import (
    render_my_skills,
)

from views.career_exploration import (
    render_career_exploration,
)

from views.learning_catalog import (
    render_learning_catalog,
)

from views.manager_staffing import (
    render_manager_staffing,
)

from views.hr_workforce_planning import (
    render_hr_workforce_planning,
)


st.set_page_config(
    page_title="WorkforceIQ",
    page_icon="🧭",
    layout="wide",
)


# English by default; ?lang=zh in the URL switches to Traditional Chinese.
render_language_switch()

st.title(
    "WorkforceIQ"
)

st.caption(
    t("app_caption")
)

st.info(
    t("synthetic_notice"),
    icon="🧪",
)


DEMO_EMPLOYEE_NAME = "River Hsu"
DEMO_MANAGER_NAME = "Riley Chang"


# =========================================================
# Workspace
# =========================================================

st.sidebar.markdown(
    f"""
<div style="
    font-size: 1.15rem;
    font-weight: 700;
    margin-bottom: 0.35rem;
">
    {t("workspace")}
</div>
""",
    unsafe_allow_html=True,
)

WORKSPACE_LABELS = {
    "Employee": "ws_employee",
    "Manager": "ws_manager",
    "HR / Workforce Planning": "ws_hr",
}

workspace = st.sidebar.radio(
    t("workspace"),
    list(WORKSPACE_LABELS),
    format_func=lambda value: t(WORKSPACE_LABELS[value]),
    label_visibility="collapsed",
    key="workspace",
)

st.sidebar.markdown(
    f"""
<div style="
    margin-top: 1rem;
    margin-bottom: 0.25rem;
    font-size: 0.82rem;
    font-weight: 600;
    color: #8B95A7;
">
    {t("suggested_demo")}
</div>

<div style="
    font-size: 0.80rem;
    line-height: 1.55;
    color: #9AA3B2;
">
    {t("suggested_demo_body")}
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# Employee Workspace
# =========================================================

if workspace == "Employee":

    employees = (
        get_employee_list()
    )

    employee_options = {
        (
            f"{row.employee_name} — "
            f"{row.current_role}"
        ): row.employee_id
        for row in employees.itertuples()
    }

    employee_labels = list(
        employee_options.keys()
    )

    employee_ids = set(
        employee_options.values()
    )

    demo_employee_id = next(
        (
            int(row.employee_id)
            for row in employees.itertuples()
            if row.employee_name == DEMO_EMPLOYEE_NAME
        ),
        employee_options[employee_labels[0]],
    )

    # Default first-time visitors to the suggested demo employee,
    # while preserving any later manual selection.
    if (
        "employee_id" not in st.session_state
        or st.session_state["employee_id"] not in employee_ids
    ):
        st.session_state["employee_id"] = demo_employee_id

    current_employee_label = next(
        label
        for label, employee_id
        in employee_options.items()
        if employee_id
        == st.session_state["employee_id"]
    )

    selected_employee_label = (
        st.sidebar.selectbox(
            t("preview_as_employee"),
            options=employee_labels,
            index=employee_labels.index(
                current_employee_label
            ),
        )
    )

    selected_employee_id = (
        employee_options[
            selected_employee_label
        ]
    )

    st.session_state[
        "employee_id"
    ] = selected_employee_id

    if "employee_page" not in st.session_state:
        st.session_state["employee_page"] = "My Skills"

    EMPLOYEE_PAGE_LABELS = {
        "My Skills": "page_my_skills",
        "Career Exploration": "page_career",
        "Learning Catalog": "page_learning",
    }

    page = st.sidebar.radio(
        t("employee_pages"),
        list(EMPLOYEE_PAGE_LABELS),
        format_func=lambda value: t(EMPLOYEE_PAGE_LABELS[value]),
        key="employee_page",
    )

    if page == "My Skills":
        render_my_skills()

    elif page == "Career Exploration":
        render_career_exploration()

    elif page == "Learning Catalog":
        render_learning_catalog()


# =========================================================
# Manager Workspace
# =========================================================

elif workspace == "Manager":

    managers = (
        get_manager_list()
    )

    if managers.empty:
        st.warning(
            t("no_managers")
        )

    else:
        manager_options = {}

        for row in managers.itertuples():
            open_count = int(row.open_requisition_count)

            label = tn(
                "manager_option",
                open_count,
                name=row.manager_name,
            )
            manager_options[label] = row.manager_id

        manager_labels = list(
            manager_options.keys()
        )

        manager_ids = set(
            manager_options.values()
        )

        demo_manager_id = next(
            (
                int(row.manager_id)
                for row in managers.itertuples()
                if row.manager_name == DEMO_MANAGER_NAME
            ),
            manager_options[manager_labels[0]],
        )

        # Default first-time visitors to the suggested demo manager,
        # while preserving any later manual selection.
        if (
            "manager_id" not in st.session_state
            or st.session_state["manager_id"] not in manager_ids
        ):
            st.session_state["manager_id"] = demo_manager_id

        current_manager_label = next(
            label
            for label, manager_id
            in manager_options.items()
            if manager_id
            == st.session_state["manager_id"]
        )

        selected_manager_label = (
            st.sidebar.selectbox(
                t("preview_as_manager"),
                options=manager_labels,
                index=manager_labels.index(
                    current_manager_label
                ),
            )
        )

        selected_manager_id = (
            manager_options[
                selected_manager_label
            ]
        )

        st.session_state[
            "manager_id"
        ] = selected_manager_id

        render_manager_staffing()


# =========================================================
# HR / Workforce Planning Workspace
# =========================================================

elif workspace == "HR / Workforce Planning":

    render_hr_workforce_planning()

# =========================================================
# Demo Controls
# =========================================================

def _reset_demo():
    """Restore this visitor's seeded demo data and clear DB-backed UI state."""
    reset_demo_database()

    for key in list(st.session_state.keys()):
        if (
            key.startswith("career_saved_state_")
            or key.startswith("career_visibility_db_")
            or key.startswith("career_visibility_select_")
        ):
            st.session_state.pop(key, None)

    st.session_state["demo_reset_notice"] = True


with st.sidebar.expander(t("demo_controls")):
    st.caption(
        t("demo_controls_body")
    )
    st.button(
        t("reset_demo"),
        on_click=_reset_demo,
        use_container_width=True,
    )

if st.session_state.pop("demo_reset_notice", False):
    st.sidebar.success(t("demo_restored"))

