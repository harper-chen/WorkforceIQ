"""
Workforce-gap and capability-coverage calculations (no Streamlit, no database).

    Workforce Gap = max(Planned Headcount - Current Headcount, 0)

Across all existing roles, a required skill is "unaddressed" when the highest outcome
level offered by any internal training course is below the level the role requires.
This check does not depend on planned headcount.
Kept separate from the Streamlit view so the arithmetic can be unit-tested.
"""

import pandas as pd


def build_workforce_plan(
    demand: pd.DataFrame,
    planned_headcount: dict,
) -> pd.DataFrame:
    plan = demand[
        [
            "role_id",
            "role_name",
            "current_headcount",
        ]
    ].copy()

    plan["Planned HC"] = (
        plan["role_id"]
        .map(planned_headcount)
        .astype(int)
    )

    plan["Workforce Gap"] = (
        plan["Planned HC"]
        - plan["current_headcount"]
    ).clip(lower=0)

    plan = plan.rename(
        columns={
            "role_name": "Role",
            "current_headcount": "Current HC",
        }
    )

    return plan[
        [
            "role_id",
            "Role",
            "Current HC",
            "Planned HC",
            "Workforce Gap",
        ]
    ]


def build_unaddressed_capability_gaps(
    role_skill_requirements: pd.DataFrame,
    training_outcomes: pd.DataFrame,
) -> pd.DataFrame:
    """
    Check the skill requirements of every existing role and show
    the ones the current internal learning catalog cannot fully
    reach.

    For each skill, Available Internal Training shows the
    course or courses with the highest available outcome level.
    """
    if role_skill_requirements.empty:
        return pd.DataFrame()

    requirements = role_skill_requirements.rename(
        columns={"role_name": "Role"}
    )

    # Highest internal-learning outcome currently available
    # for each skill.
    if training_outcomes.empty:
        max_level_by_skill = {}
    else:
        max_level_by_skill = (
            training_outcomes
            .groupby("skill_id")[
                "course_skill_level"
            ]
            .max()
            .to_dict()
        )

    requirements[
        "max_internal_training_level"
    ] = (
        requirements["skill_id"]
        .map(max_level_by_skill)
    )

    requirements[
        "coverage_gap"
    ] = (
        requirements["required_level"]
        - requirements[
            "max_internal_training_level"
        ].fillna(0)
    )

    unaddressed = requirements[
        requirements[
            "coverage_gap"
        ] > 0
    ].copy()

    if unaddressed.empty:
        return pd.DataFrame()

    rows = []

    for skill_id, group in unaddressed.groupby(
        "skill_id"
    ):
        skill_name = group[
            "skill_name"
        ].iloc[0]

        affected_roles = sorted(
            group["Role"].unique()
        )

        required_levels = sorted(
            {
                int(level)
                for level in group[
                    "required_level"
                ].tolist()
            }
        )

        min_required = min(
            required_levels
        )
        max_required = max(
            required_levels
        )

        if min_required == max_required:
            required_level_text = (
                f"L{min_required}"
            )
        else:
            required_level_text = (
                f"L{min_required}–L{max_required}"
            )

        skill_courses = training_outcomes[
            training_outcomes[
                "skill_id"
            ] == skill_id
        ].copy()

        if skill_courses.empty:
            available_training = (
                "No internal training available"
            )
        else:
            highest_level = int(
                skill_courses[
                    "course_skill_level"
                ].max()
            )

            strongest_courses = (
                skill_courses[
                    skill_courses[
                        "course_skill_level"
                    ] == highest_level
                ][
                    "training_name"
                ]
                .drop_duplicates()
                .sort_values()
                .tolist()
            )

            available_training = (
                "  \n".join(
                    f"{course} (L{highest_level})"
                    for course in strongest_courses
                )
            )

        rows.append(
            {
                "Skill":
                    skill_name,
                "Affected Roles":
                    ", ".join(
                        affected_roles
                    ),
                "Required Level":
                    required_level_text,
                "Available Internal Training":
                    available_training,
            }
        )

    result = pd.DataFrame(rows)

    return result.sort_values(
        [
            "Affected Roles",
            "Skill",
        ]
    ).reset_index(
        drop=True
    )
