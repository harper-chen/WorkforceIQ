import streamlit as st

from db import get_employee_profile, get_employee_skills


LEVEL_LABELS = {
    1: "Foundational",
    2: "Basic",
    3: "Working",
    4: "Advanced",
    5: "Expert",
}


def render_skill_card(row):
    level = int(row["proficiency_level"])

    with st.container(border=True):
        left, right = st.columns([3.4, 1.6])

        with left:
            st.markdown(f"**{row['skill_name']}**")
            st.caption(row["skill_category"])

        with right:
            st.markdown(f"**{level}/5**")
            st.caption(LEVEL_LABELS[level])

        st.progress(level / 5)

        if row["last_updated"]:
            st.caption(f"Last updated: {row['last_updated']}")


def render_my_skills():
    st.header("My Skills")

    st.write(
        "Review the skills currently recorded in your WorkforceIQ profile "
        "and the proficiency level associated with each one."
    )

    # The selected employee is controlled by app.py
    # and shared across pages through Streamlit session state.
    employee_id = st.session_state["employee_id"]

    profile = get_employee_profile(employee_id)
    skills = get_employee_skills(employee_id)

    if profile.empty:
        st.error("Employee profile not found.")
        return

    p = profile.iloc[0]

    st.subheader(p["employee_name"])

    c1, c2, c3 = st.columns([1.3, 1.8, 0.9])

    c1.metric(
        "Current role",
        p["current_role"],
    )

    c2.metric(
        "Department",
        p["department_name"],
    )

    c3.metric(
        "Recorded skills",
        len(skills),
    )

    st.divider()

    if skills.empty:
        st.info("No skills are currently recorded for this employee.")
        return

    categories = sorted(
        skills["skill_category"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_categories = st.multiselect(
        "Filter by skill category",
        categories,
        default=categories,
    )

    filtered = skills[
        skills["skill_category"].isin(selected_categories)
    ].copy()

    search_term = st.text_input(
        "Search skills",
        placeholder="e.g. SQL, Power BI, Workday",
    ).strip()

    if search_term:
        filtered = filtered[
            filtered["skill_name"].str.contains(
                search_term,
                case=False,
                na=False,
            )
        ]

    st.caption(
        f"Showing {len(filtered)} of {len(skills)} recorded skills"
    )

    for category in selected_categories:
        category_rows = filtered[
            filtered["skill_category"] == category
        ]

        if category_rows.empty:
            continue

        st.subheader(category)

        cols = st.columns(2)

        for idx, (_, row) in enumerate(category_rows.iterrows()):
            with cols[idx % 2]:
                render_skill_card(row)