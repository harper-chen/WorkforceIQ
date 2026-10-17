import re

import pandas as pd
import streamlit as st

from db import (
    get_internal_training_outcomes,
    get_training_prerequisites_catalog,
)


# =========================================================
# Search Helpers
# =========================================================

def tokenize(text):
    if text is None or pd.isna(text):
        return []

    return re.findall(
        r"[a-z0-9+#./-]+",
        str(text).lower(),
    )


def row_matches_search(
    row,
    search_term,
):
    """
    Search course name, skill name, and description.

    Short searches such as "HR" must match a complete token,
    preventing false positives such as "through".
    """
    search_term = (
        search_term
        .strip()
        .lower()
    )

    if not search_term:
        return True

    searchable_text = " ".join(
        [
            str(
                row.get(
                    "training_name",
                    "",
                )
            ),
            str(
                row.get(
                    "skill_name",
                    "",
                )
            ),
            str(
                row.get(
                    "training_description",
                    "",
                )
            ),
        ]
    ).lower()

    search_tokens = tokenize(
        search_term
    )

    text_tokens = set(
        tokenize(
            searchable_text
        )
    )

    if not search_tokens:
        return False

    if (
        len(
            search_tokens
        ) == 1
        and len(
            search_tokens[0]
        ) <= 3
    ):
        return (
            search_tokens[0]
            in text_tokens
        )

    normalized_phrase = " ".join(
        search_tokens
    )

    normalized_text = " ".join(
        tokenize(
            searchable_text
        )
    )

    if (
        normalized_phrase
        in normalized_text
    ):
        return True

    return all(
        token in text_tokens
        for token in search_tokens
    )


# =========================================================
# Display Helpers
# =========================================================

def format_course_skills(
    course_rows,
):
    skills = (
        course_rows[
            [
                "skill_name",
                "course_skill_level",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            [
                "course_skill_level",
                "skill_name",
            ],
            ascending=[
                False,
                True,
            ],
        )
    )

    return [
        (
            f"{row.skill_name} "
            f"(L{int(row.course_skill_level)})"
        )
        for row in skills.itertuples()
    ]


def render_course_detail(
    course_rows,
    prerequisites,
):
    training_id = int(
        course_rows[
            "training_id"
        ].iloc[0]
    )

    description = course_rows[
        "training_description"
    ].iloc[0]

    estimated_weeks = course_rows[
        "estimated_weeks"
    ].iloc[0]

    meta_col1, meta_col2 = st.columns(
        [1, 3]
    )

    with meta_col1:
        st.metric(
            "Estimated duration",
            (
                "Not specified"
                if pd.isna(
                    estimated_weeks
                )
                else (
                    f"{int(estimated_weeks)} weeks"
                )
            ),
        )

    with meta_col2:
        if (
            description is not None
            and not pd.isna(
                description
            )
            and str(
                description
            ).strip()
        ):
            st.write(
                str(
                    description
                ).strip()
            )
        else:
            st.caption(
                "No course description is available."
            )

    st.markdown(
        "**Skills developed**"
    )

    skills_table = (
        course_rows[
            [
                "skill_name",
                "course_skill_level",
            ]
        ]
        .drop_duplicates()
        .rename(
            columns={
                "skill_name":
                    "Skill",
                "course_skill_level":
                    "Outcome Level",
            }
        )
        .sort_values(
            [
                "Outcome Level",
                "Skill",
            ],
            ascending=[
                False,
                True,
            ],
        )
    )

    skills_table[
        "Outcome Level"
    ] = (
        skills_table[
            "Outcome Level"
        ]
        .astype(int)
        .map(
            lambda level:
                f"L{level}"
        )
    )

    st.dataframe(
        skills_table,
        hide_index=True,
        use_container_width=True,
    )

    st.markdown(
        "**Prerequisites**"
    )

    course_prereqs = (
        prerequisites[
            prerequisites[
                "training_id"
            ] == training_id
        ]
        .copy()
    )

    if course_prereqs.empty:
        st.caption(
            "No formal prerequisites."
        )
    else:
        prereq_table = (
            course_prereqs[
                [
                    "prerequisite_skill",
                    "minimum_level",
                ]
            ]
            .rename(
                columns={
                    "prerequisite_skill":
                        "Prerequisite Skill",
                    "minimum_level":
                        "Minimum Level",
                }
            )
            .sort_values(
                "Prerequisite Skill"
            )
        )

        prereq_table[
            "Minimum Level"
        ] = (
            prereq_table[
                "Minimum Level"
            ]
            .astype(int)
            .map(
                lambda level:
                    f"L{level}"
            )
        )

        st.dataframe(
            prereq_table,
            hide_index=True,
            use_container_width=True,
        )


# =========================================================
# Main Page
# =========================================================

def render_learning_catalog():
    st.header(
        "Learning Catalog"
    )

    st.write(
        "Browse the company's internal learning programs, "
        "the skills they develop, expected outcome levels, "
        "estimated duration, and formal prerequisites."
    )

    catalog = (
        get_internal_training_outcomes()
    )

    prerequisites = (
        get_training_prerequisites_catalog()
    )

    if catalog.empty:
        st.info(
            "No internal learning programs are currently available."
        )
        return

    # -----------------------------------------------------
    # Search and Filter
    # -----------------------------------------------------

    search_col, skill_col = st.columns(
        [2, 1]
    )

    with search_col:
        search_term = st.text_input(
            "Search courses",
            placeholder=(
                "Search by course name, skill, or description"
            ),
        ).strip()

    skill_options = sorted(
        catalog[
            "skill_name"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    with skill_col:
        selected_skill = st.selectbox(
            "Filter by skill",
            [
                "All skills"
            ]
            + skill_options,
        )

    filtered = (
        catalog.copy()
    )

    if search_term:
        matching_training_ids = set(
            filtered.loc[
                filtered.apply(
                    lambda row:
                        row_matches_search(
                            row,
                            search_term,
                        ),
                    axis=1,
                ),
                "training_id",
            ].tolist()
        )

        filtered = filtered[
            filtered[
                "training_id"
            ].isin(
                matching_training_ids
            )
        ]

    if (
        selected_skill
        != "All skills"
    ):
        matching_training_ids = set(
            filtered.loc[
                filtered[
                    "skill_name"
                ] == selected_skill,
                "training_id",
            ].tolist()
        )

        filtered = filtered[
            filtered[
                "training_id"
            ].isin(
                matching_training_ids
            )
        ]

    if filtered.empty:
        st.info(
            "No courses match the current search and filter."
        )
        return

    course_ids = (
        filtered[
            "training_id"
        ]
        .drop_duplicates()
        .tolist()
    )

    course_count = len(course_ids)

    st.caption(
        f"{course_count} "
        f"{'course' if course_count == 1 else 'courses'} shown."
    )

    # -----------------------------------------------------
    # Compact expandable catalog
    # -----------------------------------------------------

    for training_id in course_ids:
        course_rows = catalog[
            catalog[
                "training_id"
            ] == training_id
        ].copy()

        if course_rows.empty:
            continue

        course_name = (
            course_rows[
                "training_name"
            ].iloc[0]
        )

        estimated_weeks = (
            course_rows[
                "estimated_weeks"
            ].iloc[0]
        )

        skill_labels = (
            format_course_skills(
                course_rows
            )
        )

        duration_text = (
            "Duration not specified"
            if pd.isna(
                estimated_weeks
            )
            else (
                f"{int(estimated_weeks)} weeks"
            )
        )

        # Keep the collapsed row compact:
        # course title + duration only.
        expander_label = (
            f"{course_name}  ·  "
            f"{duration_text}"
        )

        with st.expander(
            expander_label,
            expanded=False,
        ):
            # Skills are shown as chips-like short lines
            # instead of forcing all skills into the row.
            if skill_labels:
                st.caption(
                    "Skills: "
                    + " · ".join(
                        skill_labels
                    )
                )

            render_course_detail(
                course_rows,
                prerequisites,
            )
