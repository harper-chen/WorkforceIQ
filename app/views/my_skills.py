import pandas as pd
import streamlit as st

from i18n_data import localized
from db import get_employee_profile, get_employee_skills
from i18n import department, level_label, skill_category, t

# In Chinese (?lang=zh), role / skill / course names come back translated.
get_employee_profile = localized(get_employee_profile)
get_employee_skills = localized(get_employee_skills)


def render_skill_card(row):
    level = int(row["proficiency_level"])

    with st.container(border=True):
        left, right = st.columns([3.4, 1.6])

        with left:
            st.markdown(f"**{row['skill_name']}**")
            st.caption(skill_category(row["skill_category"]))

        with right:
            st.markdown(f"**{level}/5**")
            st.caption(level_label(level))

        st.progress(level / 5)

        if row["last_updated"]:
            st.caption(t("last_updated", date=row["last_updated"]))


def render_my_skills():
    st.header(t("page_my_skills"))

    st.write(
        t("my_skills_intro")
    )

    # The selected employee is controlled by app.py
    # and shared across pages through Streamlit session state.
    employee_id = st.session_state["employee_id"]

    profile = get_employee_profile(employee_id)
    skills = get_employee_skills(employee_id)

    if profile.empty:
        st.error(t("employee_not_found"))
        return

    p = profile.iloc[0]

    st.subheader(p["employee_name"])

    c1, c2, c3 = st.columns([1.3, 1.8, 0.9])

    c1.metric(
        t("current_role"),
        p["current_role"],
    )

    c2.metric(
        t("department"),
        department(p["department_name"]),
    )

    c3.metric(
        t("recorded_skills"),
        len(skills),
    )

    st.divider()

    if skills.empty:
        st.info(t("no_skills"))
        return

    categories = sorted(
        skills["skill_category"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_categories = st.multiselect(
        t("filter_category"),
        categories,
        default=categories,
        format_func=skill_category,
    )

    filtered = skills[
        skills["skill_category"].isin(selected_categories)
    ].copy()

    search_term = st.text_input(
        t("search_skills"),
        placeholder=t("search_skills_ph"),
    ).strip()

    if search_term:
        # In Chinese, also match the English skill name.
        search_columns = [
            column
            for column in ("skill_name", "skill_name_en")
            if column in filtered.columns
        ]
        matches = pd.Series(False, index=filtered.index)
        for column in search_columns:
            matches |= filtered[column].str.contains(
                search_term,
                case=False,
                na=False,
                regex=False,
            )
        filtered = filtered[matches]

    st.caption(
        t("showing_skills", shown=len(filtered), total=len(skills))
    )

    for category in selected_categories:
        category_rows = filtered[
            filtered["skill_category"] == category
        ]

        if category_rows.empty:
            continue

        st.subheader(skill_category(category))

        cols = st.columns(2)

        for idx, (_, row) in enumerate(category_rows.iterrows()):
            with cols[idx % 2]:
                render_skill_card(row)