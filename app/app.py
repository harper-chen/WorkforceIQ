import streamlit as st

from db import (
    get_employee_list,
    get_manager_list,
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


st.title(
    "WorkforceIQ"
)

st.caption(
    "Skills Intelligence, Career Mobility & "
    "Strategic Workforce Planning"
)


# =========================================================
# Workspace
# =========================================================

workspace = st.sidebar.radio(
    "Workspace",
    [
        "Employee",
        "Manager",
        "HR / Workforce Planning",
    ],
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

    # Keep the last selected employee across workspace changes.
    if (
        "employee_id" not in st.session_state
        or st.session_state["employee_id"] not in employee_ids
    ):
        st.session_state[
            "employee_id"
        ] = employee_options[
            employee_labels[0]
        ]

    current_employee_label = next(
        label
        for label, employee_id
        in employee_options.items()
        if employee_id
        == st.session_state["employee_id"]
    )

    selected_employee_label = (
        st.sidebar.selectbox(
            "Preview as employee",
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

    page = st.sidebar.radio(
        "Employee",
        [
            "My Skills",
            "Career Exploration",
            "Learning Catalog",
        ],
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
            "No hiring managers are currently "
            "linked to job openings."
        )

    else:
        manager_options = {
            (
                f"{row.manager_name} — "
                f"{row.current_role}"
            ): row.manager_id
            for row in managers.itertuples()
        }

        manager_labels = list(
            manager_options.keys()
        )

        manager_ids = set(
            manager_options.values()
        )

        # Keep the last selected manager across workspace changes.
        if (
            "manager_id" not in st.session_state
            or st.session_state["manager_id"] not in manager_ids
        ):
            st.session_state[
                "manager_id"
            ] = manager_options[
                manager_labels[0]
            ]

        current_manager_label = next(
            label
            for label, manager_id
            in manager_options.items()
            if manager_id
            == st.session_state["manager_id"]
        )

        selected_manager_label = (
            st.sidebar.selectbox(
                "Preview as manager",
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
