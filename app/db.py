from pathlib import Path
from contextlib import contextmanager
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import uuid

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# The seeded baseline. It is built from schema + seed files, then only ever COPIED:
# in the running app nobody writes to it, so it always holds the clean demo data.
DB_PATH = PROJECT_ROOT / "database" / "workforceiq.db"
REBUILD_SCRIPT = PROJECT_ROOT / "database" / "rebuild_db.py"

# Each visitor session works on its own private copy of the baseline, so one visitor's
# saved career interests or visibility changes never show up for anyone else.
SESSION_DB_DIR = Path(tempfile.gettempdir()) / "workforceiq_sessions"
SESSION_DB_KEY = "_workforceiq_session_db"
SESSION_DB_MAX_AGE_SECONDS = 24 * 60 * 60
SESSION_DB_MAX_FILES = 200

# One Streamlit server process serves every session, so a process-wide lock is enough
# to keep "build the baseline" and "copy the baseline" from overlapping.
_db_lock = threading.RLock()


def _run_database_rebuild(*extra_args: str) -> None:
    """Run the reproducible database rebuild and surface useful errors."""
    command = [
        sys.executable,
        str(REBUILD_SCRIPT),
        *extra_args,
    ]

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 or not DB_PATH.exists():
        details = (result.stderr or result.stdout).strip()
        raise RuntimeError(
            "WorkforceIQ could not create the demo database."
            + (f"\n\n{details}" if details else "")
        )


def ensure_database() -> None:
    """Create the seeded baseline database automatically when it is missing."""
    with _db_lock:
        if DB_PATH.exists():
            return

        _run_database_rebuild("--no-backup")


def _session_state():
    """
    Return Streamlit's per-visitor session_state, or None when the code runs
    outside a Streamlit session (unit tests, command-line scripts).
    """
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        try:
            context = get_script_run_ctx(suppress_warning=True)
        except TypeError:  # older Streamlit without the keyword
            context = get_script_run_ctx()

        if context is None:
            return None

        import streamlit as st

        return st.session_state
    except Exception:
        return None


def _purge_stale_session_databases(now=None) -> None:
    """Best-effort cleanup: drop session copies older than a day, then cap the total."""
    now = time.time() if now is None else now

    try:
        files = sorted(
            SESSION_DB_DIR.glob("session_*.db"),
            key=lambda path: path.stat().st_mtime,
        )
    except OSError:
        return

    keep = []
    for path in files:
        try:
            if now - path.stat().st_mtime > SESSION_DB_MAX_AGE_SECONDS:
                path.unlink()
            else:
                keep.append(path)
        except OSError:
            continue

    # The newest copies belong to the visitors who are most likely still here.
    for path in keep[: max(len(keep) - SESSION_DB_MAX_FILES, 0)]:
        try:
            path.unlink()
        except OSError:
            continue


def active_db_path() -> Path:
    """
    Database file for the current caller.

    Inside a Streamlit session this is that visitor's private copy (created on first use).
    Outside a session it is the shared baseline file, which keeps scripts and tests simple.
    """
    state = _session_state()

    if state is None:
        return DB_PATH

    with _db_lock:
        ensure_database()

        existing = state.get(SESSION_DB_KEY)
        if existing and Path(existing).exists():
            # Touch it so an active visitor's copy is not mistaken for a stale one.
            try:
                Path(existing).touch()
            except OSError:
                pass
            return Path(existing)

        _purge_stale_session_databases()
        SESSION_DB_DIR.mkdir(parents=True, exist_ok=True)

        new_path = SESSION_DB_DIR / f"session_{uuid.uuid4().hex}.db"
        shutil.copyfile(DB_PATH, new_path)
        state[SESSION_DB_KEY] = str(new_path)

        return new_path


def reset_demo_database() -> None:
    """
    Restore the seeded demo data.

    In a Streamlit session this affects only the current visitor's private copy.
    Outside a session it rebuilds the shared baseline from the schema and seed files.
    """
    with _db_lock:
        path = active_db_path()

        if path == DB_PATH:
            _run_database_rebuild("--no-backup")
        else:
            shutil.copyfile(DB_PATH, path)


@contextmanager
def get_connection():
    """
    Open a SQLite connection with foreign-key enforcement enabled.

    Successful writes are committed, exceptions are rolled back,
    and the connection is always closed after use.
    """
    ensure_database()

    conn = sqlite3.connect(active_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        with conn:
            yield conn
    finally:
        conn.close()


def is_career_saved(employee_id: int, role_id: int) -> bool:
    """Return True if the employee has already saved the target role."""
    query = """
    SELECT 1
    FROM employee_career_interests
    WHERE employee_id = ?
      AND target_role_id = ?
    LIMIT 1;
    """

    with get_connection() as conn:
        row = conn.execute(
            query,
            (employee_id, role_id),
        ).fetchone()

    return row is not None


def save_career_interest(employee_id: int, role_id: int) -> bool:
    """
    Save a target role as a private career interest.

    Returns True when a new record is created.
    Returns False when the career was already saved.
    """
    query = """
    INSERT OR IGNORE INTO employee_career_interests (
        employee_id,
        target_role_id,
        created_at,
        visibility_level
    )
    VALUES (?, ?, DATE('now'), 'private');
    """

    with get_connection() as conn:
        cursor = conn.execute(
            query,
            (employee_id, role_id),
        )
        created = cursor.rowcount == 1

    return created



def delete_career_interest(
    employee_id: int,
    role_id: int,
) -> bool:
    """
    Remove one saved career interest for an employee.

    Returns True when an existing saved career is deleted.
    Returns False when no matching saved career exists.
    """
    query = """
    DELETE FROM employee_career_interests
    WHERE employee_id = ?
      AND target_role_id = ?;
    """

    with get_connection() as conn:
        cursor = conn.execute(
            query,
            (
                employee_id,
                role_id,
            ),
        )
        deleted = cursor.rowcount == 1

    return deleted


def update_career_visibility(
    employee_id: int,
    role_id: int,
    visibility_level: str,
) -> bool:
    """
    Update the sharing visibility for one saved career interest.

    Allowed values:
        private
        opening_managers

    Returns True when an existing career-interest row is updated.
    Returns False when no matching saved career exists.
    """

    allowed_visibility_levels = {
        "private",
        "opening_managers",
    }

    if visibility_level not in allowed_visibility_levels:
        raise ValueError(
            "Invalid visibility_level. "
            "Expected one of: private, opening_managers."
        )

    query = """
    UPDATE employee_career_interests
    SET visibility_level = ?
    WHERE employee_id = ?
      AND target_role_id = ?;
    """

    with get_connection() as conn:
        cursor = conn.execute(
            query,
            (
                visibility_level,
                employee_id,
                role_id,
            ),
        )
        updated = cursor.rowcount == 1

    return updated

def get_employee_list():
    query = '''
    SELECT
        e.employee_id,
        e.employee_name,
        r.role_name AS current_role
    FROM employees e
    JOIN roles r
      ON r.role_id = e.current_role_id
    ORDER BY e.employee_name;
    '''
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_employee_profile(employee_id: int):
    query = '''
    SELECT
        e.employee_id,
        e.employee_name,
        r.role_name AS current_role,
        d.department_name,
        e.tenure_years,
        e.hire_date
    FROM employees e
    JOIN roles r
      ON r.role_id = e.current_role_id
    JOIN departments d
      ON d.department_id = r.department_id
    WHERE e.employee_id = ?;
    '''
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=[employee_id])


def get_employee_skills(employee_id: int):
    query = '''
    SELECT
        s.skill_id,
        s.skill_name,
        s.skill_category,
        es.proficiency_level,
        es.last_updated
    FROM employee_skills es
    JOIN skills s
      ON s.skill_id = es.skill_id
    WHERE es.employee_id = ?
    ORDER BY
        s.skill_category,
        es.proficiency_level DESC,
        s.skill_name;
    '''
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=[employee_id])


def get_all_roles(employee_id: int):
    query = '''
    SELECT
        r.role_id,
        r.role_name,
        r.level,
        d.department_name,
        r.role_description
    FROM roles r
    JOIN departments d
      ON d.department_id = r.department_id
    WHERE r.role_id <> (
        SELECT current_role_id
        FROM employees
        WHERE employee_id = ?
    )
    ORDER BY d.department_name, r.level, r.role_name;
    '''
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=[employee_id])


def get_recommended_careers(employee_id: int):
    query = '''
    WITH employee_info AS (
        SELECT
            employee_id,
            current_role_id
        FROM employees
        WHERE employee_id = ?
    ),

    role_skill_match AS (
        SELECT
            r.role_id,
            r.role_name,
            r.level,
            r.role_description,
            d.department_name,
            rs.skill_id,
            rs.required_level,
            rs.importance_level,
            es.proficiency_level AS employee_level,
            MIN(
                1.0 * COALESCE(es.proficiency_level, 0)
                / rs.required_level,
                1.0
            ) AS per_skill_match,
            MAX(
                rs.required_level
                - COALESCE(es.proficiency_level, 0),
                0
            ) AS gap
        FROM employee_info ei
        JOIN roles r
          ON r.role_id <> ei.current_role_id
        JOIN departments d
          ON d.department_id = r.department_id
        JOIN role_skills rs
          ON rs.role_id = r.role_id
        LEFT JOIN employee_skills es
          ON es.employee_id = ei.employee_id
         AND es.skill_id = rs.skill_id
    ),

    role_scores AS (
        SELECT
            role_id,
            role_name,
            level,
            role_description,
            department_name,
            ROUND(
                100.0
                * SUM(importance_level * per_skill_match)
                / SUM(importance_level),
                1
            ) AS match_percent,
            SUM(
                CASE
                    WHEN employee_level IS NULL THEN 1
                    ELSE 0
                END
            ) AS not_recorded_skills,
            SUM(
                CASE
                    WHEN gap = 0 THEN 1
                    ELSE 0
                END
            ) AS skills_met,
            SUM(
                CASE
                    WHEN gap > 0 THEN 1
                    ELSE 0
                END
            ) AS skills_to_develop
        FROM role_skill_match
        GROUP BY
            role_id,
            role_name,
            level,
            role_description,
            department_name
    )

    SELECT
        rs.*,
        CASE
            WHEN cp.career_path_id IS NOT NULL THEN 1
            ELSE 0
        END AS formal_career_path
    FROM role_scores rs
    LEFT JOIN employee_info ei
      ON 1 = 1
    LEFT JOIN career_paths cp
      ON cp.source_role_id = ei.current_role_id
     AND cp.target_role_id = rs.role_id
    ORDER BY
        formal_career_path DESC,
        match_percent DESC,
        rs.role_name;
    '''

    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=[employee_id])
def get_target_role_skill_details(employee_id, role_id):

    query = """
    SELECT
        s.skill_id,
        s.skill_name,
        s.skill_category,

        rs.required_level,
        rs.importance_level,

        es.proficiency_level,

        CASE
            WHEN es.proficiency_level IS NULL
                THEN NULL
            ELSE rs.required_level - es.proficiency_level
        END AS gap

    FROM role_skills rs

    JOIN skills s
        ON rs.skill_id = s.skill_id

    LEFT JOIN employee_skills es
        ON es.skill_id = rs.skill_id
        AND es.employee_id = ?

    WHERE rs.role_id = ?

    ORDER BY
        rs.importance_level DESC,
        s.skill_name ASC
    """

    with get_connection() as conn:

        return pd.read_sql_query(
            query,
            conn,
            params=(
                employee_id,
                role_id,
            ),
        )
def get_role_detail(role_id):

    query = """
    SELECT
        r.role_id,
        r.role_name,
        r.level,
        r.role_description,
        d.department_name

    FROM roles r

    JOIN departments d
        ON r.department_id = d.department_id

    WHERE r.role_id = ?
    """

    with get_connection() as conn:

        return pd.read_sql_query(
            query,
            conn,
            params=(role_id,),
        )
def get_recommended_learning(employee_id, role_id):

    # =====================================================
    # 1. Load all training programs and their outcome skills
    # =====================================================

    course_skills_query = """
    SELECT
        tp.training_id,
        tp.training_name,
        tp.estimated_weeks,
        tp.training_description,

        ts.skill_id,
        s.skill_name,
        ts.course_skill_level

    FROM training_programs tp

    JOIN training_skills ts
        ON tp.training_id = ts.training_id

    JOIN skills s
        ON ts.skill_id = s.skill_id
    """

    # =====================================================
    # 2. Load target-role skill requirements
    # =====================================================

    role_skills_query = """
    SELECT
        rs.skill_id,
        s.skill_name,
        rs.required_level,
        rs.importance_level,

        COALESCE(
            es.proficiency_level,
            0
        ) AS current_level,

        CASE
            WHEN es.proficiency_level IS NULL
                THEN 1
            ELSE 0
        END AS not_recorded

    FROM role_skills rs

    JOIN skills s
        ON rs.skill_id = s.skill_id

    LEFT JOIN employee_skills es
        ON es.skill_id = rs.skill_id
        AND es.employee_id = ?

    WHERE rs.role_id = ?
    """

    # =====================================================
    # 3. Load course prerequisites
    # =====================================================

    prerequisites_query = """
    SELECT
        tpr.training_id,
        tpr.skill_id,
        s.skill_name AS prerequisite_skill,
        tpr.minimum_level,

        COALESCE(
            es.proficiency_level,
            0
        ) AS current_level,

        CASE
            WHEN es.proficiency_level IS NULL
                THEN 1
            ELSE 0
        END AS not_recorded

    FROM training_prerequisites tpr

    JOIN skills s
        ON tpr.skill_id = s.skill_id

    LEFT JOIN employee_skills es
        ON es.skill_id = tpr.skill_id
        AND es.employee_id = ?

    """

    # =====================================================
    # 4. Load employee training records
    # =====================================================

    training_records_query = """
    SELECT
        training_id,
        status,
        passed

    FROM employee_training_records

    WHERE employee_id = ?
    """

    with get_connection() as conn:

        course_skills = pd.read_sql_query(
            course_skills_query,
            conn,
        )

        role_skills = pd.read_sql_query(
            role_skills_query,
            conn,
            params=(
                employee_id,
                role_id,
            ),
        )

        prerequisites = pd.read_sql_query(
            prerequisites_query,
            conn,
            params=(
                employee_id,
            ),
        )

        training_records = pd.read_sql_query(
            training_records_query,
            conn,
            params=(
                employee_id,
            ),
        )

    # =====================================================
    # 5. Employee training status
    # =====================================================

    completed_training_ids = set(
        training_records.loc[
            (
                training_records["status"]
                == "completed"
            )
            & (
                training_records["passed"]
                == 1
            ),
            "training_id",
        ].tolist()
    )

    in_progress_training_ids = set(
        training_records.loc[
            training_records["status"]
            == "in_progress",
            "training_id",
        ].tolist()
    )

    # =====================================================
    # 6. Build target-role lookup
    # =====================================================

    role_skill_lookup = {}

    for _, row in role_skills.iterrows():

        role_skill_lookup[
            int(row["skill_id"])
        ] = {
            "skill_name": row["skill_name"],
            "required_level": int(
                row["required_level"]
            ),
            "importance_level": int(
                row["importance_level"]
            ),
            "current_level": int(
                row["current_level"]
            ),
            "not_recorded": int(
                row["not_recorded"]
            ),
        }

    target_skill_ids = set(
        role_skill_lookup.keys()
    )

    # =====================================================
    # 7. Helper:
    #    check whether a course's prerequisites are satisfied
    # =====================================================

    def get_course_prerequisite_status(training_id):

        course_prereqs = prerequisites[
            prerequisites[
                "training_id"
            ] == training_id
        ].copy()

        if course_prereqs.empty:

            return (
                True,
                course_prereqs,
            )

        course_prereqs[
            "prerequisite_met"
        ] = (
            course_prereqs[
                "current_level"
            ]
            >=
            course_prereqs[
                "minimum_level"
            ]
        )

        unmet = course_prereqs[
            ~course_prereqs[
                "prerequisite_met"
            ]
        ].copy()

        return (
            unmet.empty,
            unmet,
        )

    # =====================================================
    # 8. Evaluate each course against target role
    # =====================================================

    course_results = []

    for training_id, group in (
        course_skills.groupby(
            "training_id"
        )
    ):

        training_id = int(
            training_id
        )

        # Do not recommend courses already completed.
        if (
            training_id
            in completed_training_ids
        ):
            continue

        first = group.iloc[0]

        total_outcome_skills = len(
            group
        )

        target_outcomes = group[
            group["skill_id"].isin(
                target_skill_ids
            )
        ]

        target_outcome_count = len(
            target_outcomes
        )

        course_role_alignment = (
            target_outcome_count
            / total_outcome_skills
            if total_outcome_skills > 0
            else 0
        )

        gaps_improved = 0
        gaps_fully_closed = 0

        improvement_details = []

        # -------------------------------------------------
        # Evaluate course outcomes that belong to target role
        # -------------------------------------------------

        for _, outcome in (
            target_outcomes.iterrows()
        ):

            skill_id = int(
                outcome["skill_id"]
            )

            course_level = int(
                outcome[
                    "course_skill_level"
                ]
            )

            role_skill = (
                role_skill_lookup[
                    skill_id
                ]
            )

            current_level = (
                role_skill[
                    "current_level"
                ]
            )

            required_level = (
                role_skill[
                    "required_level"
                ]
            )

            not_recorded = (
                role_skill[
                    "not_recorded"
                ]
            )

            # Only count a benefit if:
            # 1. employee currently has a target-role gap
            # 2. course would improve demonstrated proficiency
            has_gap = (
                current_level
                < required_level
            )

            improves_skill = (
                course_level
                > current_level
            )

            if (
                has_gap
                and improves_skill
            ):

                gaps_improved += 1

                if (
                    course_level
                    >= required_level
                ):

                    gaps_fully_closed += 1

                improvement_details.append(
                    {
                        "skill_id": skill_id,
                        "skill_name": (
                            role_skill[
                                "skill_name"
                            ]
                        ),
                        "current_level": (
                            current_level
                        ),
                        "not_recorded": (
                            not_recorded
                        ),
                        "course_level": (
                            course_level
                        ),
                        "required_level": (
                            required_level
                        ),
                    }
                )

        # -------------------------------------------------
        # Direct relevance rule
        # -------------------------------------------------

        directly_relevant = (
            (
                course_role_alignment
                >= 0.50
                and gaps_improved >= 1
            )
            or
            gaps_improved >= 2
        )

        if not directly_relevant:
            continue

        # -------------------------------------------------
        # Prerequisite status
        # -------------------------------------------------

        (
            prerequisites_met,
            unmet_prerequisites,
        ) = get_course_prerequisite_status(
            training_id
        )

        if prerequisites_met:

            recommendation_status = (
                "Ready now"
            )

        else:

            recommendation_status = (
                "Prerequisite required"
            )

        course_results.append(
            {
                "training_id": (
                    training_id
                ),
                "training_name": (
                    first[
                        "training_name"
                    ]
                ),
                "estimated_weeks": int(
                    first[
                        "estimated_weeks"
                    ]
                ),
                "training_description": (
                    first[
                        "training_description"
                    ]
                ),
                "course_role_alignment": (
                    course_role_alignment
                ),
                "gaps_improved": (
                    gaps_improved
                ),
                "gaps_fully_closed": (
                    gaps_fully_closed
                ),
                "recommendation_status": (
                    recommendation_status
                ),
                "is_in_progress": (
                    training_id
                    in in_progress_training_ids
                ),
                "improvement_details": (
                    improvement_details
                ),
                "unmet_prerequisites": (
                    unmet_prerequisites
                ),
            }
        )

    # =====================================================
    # 9. Separate Ready / Locked
    # =====================================================

    ready_courses = [
        course
        for course in course_results
        if (
            course[
                "recommendation_status"
            ]
            == "Ready now"
        )
    ]

    locked_courses = [
        course
        for course in course_results
        if (
            course[
                "recommendation_status"
            ]
            == "Prerequisite required"
        )
    ]

    # =====================================================
    # 10. Ready-now ranking
    #
    #     1. more gaps improved
    #     2. more gaps fully closed
    #     3. higher role alignment
    #     4. shorter duration
    # =====================================================

    ready_courses.sort(
        key=lambda course: (
            -course[
                "gaps_improved"
            ],
            -course[
                "gaps_fully_closed"
            ],
            -course[
                "course_role_alignment"
            ],
            course[
                "estimated_weeks"
            ],
        )
    )

    # =====================================================
    # 11. Locked-course ranking
    #
    #     1. more gaps improved
    #     2. higher role alignment
    #     3. fewer unmet prerequisites
    #     4. shorter duration
    # =====================================================

    locked_courses.sort(
        key=lambda course: (
            -course[
                "gaps_improved"
            ],
            -course[
                "course_role_alignment"
            ],
            len(
                course[
                    "unmet_prerequisites"
                ]
            ),
            course[
                "estimated_weeks"
            ],
        )
    )

    # =====================================================
    # 12. Find courses that can satisfy each missing
    #     prerequisite
    # =====================================================

    for locked_course in (
        locked_courses
    ):

        prerequisite_options = []

        unmet = locked_course[
            "unmet_prerequisites"
        ]

        for _, prereq in (
            unmet.iterrows()
        ):

            prerequisite_skill_id = int(
                prereq["skill_id"]
            )

            minimum_level = int(
                prereq[
                    "minimum_level"
                ]
            )

            current_level = int(
                prereq[
                    "current_level"
                ]
            )

            options = course_skills[
                (
                    course_skills[
                        "skill_id"
                    ]
                    == prerequisite_skill_id
                )
                &
                (
                    course_skills[
                        "course_skill_level"
                    ]
                    >= minimum_level
                )
            ].copy()

            option_results = []

            for option_training_id, option_group in (
                options.groupby(
                    "training_id"
                )
            ):

                option_training_id = int(
                    option_training_id
                )

                # Do not recommend the locked target course
                # as its own prerequisite solution.
                if (
                    option_training_id
                    == locked_course[
                        "training_id"
                    ]
                ):
                    continue

                # If already completed, the resulting employee
                # skill should already have been applied.
                if (
                    option_training_id
                    in completed_training_ids
                ):
                    continue

                option_first = (
                    option_group.iloc[0]
                )

                outcome_level = int(
                    option_group[
                        "course_skill_level"
                    ].max()
                )

                (
                    option_available,
                    option_unmet,
                ) = (
                    get_course_prerequisite_status(
                        option_training_id
                    )
                )

                # Does this prerequisite course also help
                # the chosen target role?
                option_target_outcomes = (
                    course_skills[
                        (
                            course_skills[
                                "training_id"
                            ]
                            == option_training_id
                        )
                        &
                        (
                            course_skills[
                                "skill_id"
                            ].isin(
                                target_skill_ids
                            )
                        )
                    ]
                )

                additional_target_gaps = 0

                for _, option_outcome in (
                    option_target_outcomes.iterrows()
                ):

                    option_skill_id = int(
                        option_outcome[
                            "skill_id"
                        ]
                    )

                    option_course_level = int(
                        option_outcome[
                            "course_skill_level"
                        ]
                    )

                    role_skill = (
                        role_skill_lookup[
                            option_skill_id
                        ]
                    )

                    if (
                        role_skill[
                            "current_level"
                        ]
                        <
                        role_skill[
                            "required_level"
                        ]
                        and
                        option_course_level
                        >
                        role_skill[
                            "current_level"
                        ]
                    ):

                        additional_target_gaps += 1

                option_results.append(
                    {
                        "training_id": (
                            option_training_id
                        ),
                        "training_name": (
                            option_first[
                                "training_name"
                            ]
                        ),
                        "estimated_weeks": int(
                            option_first[
                                "estimated_weeks"
                            ]
                        ),
                        "course_skill_level": (
                            outcome_level
                        ),
                        "available_now": (
                            option_available
                        ),
                        "unmet_prerequisite_count": (
                            len(
                                option_unmet
                            )
                        ),
                        "additional_target_gaps": (
                            additional_target_gaps
                        ),
                    }
                )

            # -------------------------------------------------
            # Rank prerequisite-course options
            #
            # 1. available now first
            # 2. smallest sufficient level increase
            # 3. shorter duration
            # 4. helps more target-role gaps
            # -------------------------------------------------

            option_results.sort(
                key=lambda option: (
                    not option[
                        "available_now"
                    ],
                    option[
                        "course_skill_level"
                    ]
                    - minimum_level,
                    option[
                        "estimated_weeks"
                    ],
                    -option[
                        "additional_target_gaps"
                    ],
                )
            )

            prerequisite_options.append(
                {
                    "skill_id": (
                        prerequisite_skill_id
                    ),
                    "skill_name": (
                        prereq[
                            "prerequisite_skill"
                        ]
                    ),
                    "current_level": (
                        current_level
                    ),
                    "not_recorded": int(
                        prereq[
                            "not_recorded"
                        ]
                    ),
                    "minimum_level": (
                        minimum_level
                    ),
                    "course_options": (
                        option_results
                    ),
                }
            )

        locked_course[
            "prerequisite_options"
        ] = prerequisite_options

    # =====================================================
    # 13. Career Detail display limits
    # =====================================================

    return {
        "ready": (
            ready_courses[:3]
        ),
        "locked": (
            locked_courses[:2]
        ),
    }

def get_saved_careers(employee_id: int):
    """
    Return all career interests saved by an employee.

    Career interests are role-specific and include the
    employee-controlled visibility level.
    """
    query = """
    SELECT
        eci.target_role_id AS role_id,
        r.role_name,
        r.level,
        d.department_name,
        r.role_description,
        eci.created_at,
        eci.visibility_level

    FROM employee_career_interests eci

    JOIN roles r
        ON r.role_id = eci.target_role_id

    JOIN departments d
        ON d.department_id = r.department_id

    WHERE eci.employee_id = ?

    ORDER BY
        eci.created_at DESC,
        r.role_name ASC;
    """

    with get_connection() as conn:
        return pd.read_sql_query(
            query,
            conn,
            params=(employee_id,),
        )

# =========================================================
# Manager Staffing
# =========================================================

def get_manager_list():
    """
    Return employees who currently own at least one job opening.

    This list is used only for the synthetic demo's
    "Preview as manager" control.
    """
    query = """
    SELECT
        e.employee_id AS manager_id,
        e.employee_name AS manager_name,
        r.role_name AS current_role,
        SUM(
            CASE
                WHEN jo.status = 'open' THEN 1
                ELSE 0
            END
        ) AS open_requisition_count

    FROM job_openings jo

    JOIN employees e
        ON e.employee_id = jo.hiring_manager_id

    JOIN roles r
        ON r.role_id = e.current_role_id

    WHERE jo.status IN ('open', 'paused')

    GROUP BY
        e.employee_id,
        e.employee_name,
        r.role_name

    ORDER BY
        e.employee_name ASC;
    """

    with get_connection() as conn:
        return pd.read_sql_query(
            query,
            conn,
        )


def get_manager_openings(manager_id: int):
    """
    Return openings owned by one hiring manager.

    Open and paused requisitions are included so the manager
    can see the current state of their staffing workload.
    """
    query = """
    SELECT
        jo.opening_id,
        jo.role_id,
        r.role_name,
        r.level,
        d.department_name,
        jo.headcount,
        jo.status,
        jo.open_date

    FROM job_openings jo

    JOIN roles r
        ON r.role_id = jo.role_id

    JOIN departments d
        ON d.department_id = r.department_id

    WHERE jo.hiring_manager_id = ?
      AND jo.status IN ('open', 'paused')

    ORDER BY
        CASE jo.status
            WHEN 'open' THEN 1
            WHEN 'paused' THEN 2
            ELSE 3
        END,
        jo.open_date DESC,
        r.role_name ASC;
    """

    with get_connection() as conn:
        return pd.read_sql_query(
            query,
            conn,
            params=(manager_id,),
        )


def get_visible_internal_candidates(
    manager_id: int,
    opening_id: int,
):
    """
    Return employees who explicitly shared interest in the
    exact role attached to a manager-owned OPEN requisition.

    Privacy rule:
    - employee_career_interests.visibility_level must be
      'opening_managers'
    - target_role_id must exactly match job_openings.role_id
    - the opening must belong to the requesting manager
    - the opening must currently be open
    - the hiring manager is excluded from their own candidate list

    Skill-match logic follows the employee-side frozen formula:
        per-skill match = min(employee_level / required_level, 1)
        overall match = weighted average using importance_level

    Missing employee skill records receive 0 demonstrated match
    credit for calculation and remain countable as "not recorded".
    They are not classified as significant or priority gaps because
    missing evidence is not evidence of a demonstrated deficiency.
    """
    query = """
    WITH opening_info AS (
        SELECT
            jo.opening_id,
            jo.role_id,
            jo.hiring_manager_id

        FROM job_openings jo

        WHERE jo.opening_id = ?
          AND jo.hiring_manager_id = ?
          AND jo.status = 'open'
    ),

    visible_candidates AS (
        SELECT
            eci.employee_id,
            eci.target_role_id,
            eci.created_at AS interest_shared_date

        FROM employee_career_interests eci

        JOIN opening_info oi
            ON oi.role_id = eci.target_role_id

        WHERE eci.visibility_level = 'opening_managers'
          AND eci.employee_id <> oi.hiring_manager_id
    ),

    candidate_skill_match AS (
        SELECT
            vc.employee_id,
            vc.interest_shared_date,

            e.employee_name,
            cr.role_name AS current_role,
            cd.department_name AS current_department,

            rs.skill_id,
            rs.required_level,
            rs.importance_level,
            es.proficiency_level AS employee_level,

            MIN(
                1.0 * COALESCE(
                    es.proficiency_level,
                    0
                ) / rs.required_level,
                1.0
            ) AS per_skill_match,

            MAX(
                rs.required_level
                - COALESCE(
                    es.proficiency_level,
                    0
                ),
                0
            ) AS gap

        FROM visible_candidates vc

        JOIN employees e
            ON e.employee_id = vc.employee_id

        JOIN roles cr
            ON cr.role_id = e.current_role_id

        JOIN departments cd
            ON cd.department_id = cr.department_id

        JOIN role_skills rs
            ON rs.role_id = vc.target_role_id

        LEFT JOIN employee_skills es
            ON es.employee_id = vc.employee_id
           AND es.skill_id = rs.skill_id
    )

    SELECT
        employee_id,
        employee_name,
        current_role,
        current_department,
        interest_shared_date,

        ROUND(
            100.0
            * SUM(
                importance_level
                * per_skill_match
            )
            / SUM(importance_level),
            1
        ) AS match_percent,

        SUM(
            CASE
                WHEN gap = 0 THEN 1
                ELSE 0
            END
        ) AS skills_met,

        SUM(
            CASE
                WHEN gap > 0 THEN 1
                ELSE 0
            END
        ) AS skills_to_develop,

        SUM(
            CASE
                WHEN employee_level IS NULL THEN 1
                ELSE 0
            END
        ) AS not_recorded_skills,

        SUM(
            CASE
                WHEN employee_level IS NOT NULL
                 AND gap >= 2 THEN 1
                ELSE 0
            END
        ) AS significant_gaps,

        SUM(
            CASE
                WHEN employee_level IS NOT NULL
                 AND gap >= 2
                 AND importance_level >= 4
                    THEN 1
                ELSE 0
            END
        ) AS priority_gaps

    FROM candidate_skill_match

    GROUP BY
        employee_id,
        employee_name,
        current_role,
        current_department,
        interest_shared_date

    ORDER BY
        match_percent DESC,
        priority_gaps ASC,
        significant_gaps ASC,
        employee_name ASC;
    """

    with get_connection() as conn:
        return pd.read_sql_query(
            query,
            conn,
            params=(
                opening_id,
                manager_id,
            ),
        )


def get_opening_detail(
    manager_id: int,
    opening_id: int,
):
    """
    Return one manager-owned opening with role metadata.
    """
    query = """
    SELECT
        jo.opening_id,
        jo.role_id,
        r.role_name,
        r.level,
        r.role_description,
        d.department_name,
        jo.headcount,
        jo.status,
        jo.open_date

    FROM job_openings jo

    JOIN roles r
        ON r.role_id = jo.role_id

    JOIN departments d
        ON d.department_id = r.department_id

    WHERE jo.opening_id = ?
      AND jo.hiring_manager_id = ?;
    """

    with get_connection() as conn:
        return pd.read_sql_query(
            query,
            conn,
            params=(
                opening_id,
                manager_id,
            ),
        )


# =========================================================
# HR / Workforce Planning
# =========================================================

def get_planning_periods():
    """
    Return available workforce-planning periods from future_demand.
    """
    query = """
    SELECT DISTINCT
        planning_period
    FROM future_demand
    ORDER BY planning_period;
    """

    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_workforce_demand(planning_period: str):
    """
    Return baseline workforce demand by role for one planning period.

    future_demand.required_headcount is treated as total required
    headcount at the future point, not incremental hires.
    """
    query = """
    WITH current_headcount AS (
        SELECT
            current_role_id AS role_id,
            COUNT(*) AS current_headcount
        FROM employees
        GROUP BY current_role_id
    )

    SELECT
        fd.role_id,
        r.role_name,
        r.level,
        d.department_name,
        COALESCE(
            ch.current_headcount,
            0
        ) AS current_headcount,
        fd.required_headcount
            AS baseline_required_headcount

    FROM future_demand fd

    JOIN roles r
        ON r.role_id = fd.role_id

    JOIN departments d
        ON d.department_id = r.department_id

    LEFT JOIN current_headcount ch
        ON ch.role_id = fd.role_id

    WHERE fd.planning_period = ?

    ORDER BY
        d.department_name,
        r.role_name;
    """

    with get_connection() as conn:
        return pd.read_sql_query(
            query,
            conn,
            params=(planning_period,),
        )


# =========================================================
# HR / Workforce Planning
# =========================================================
#
# WorkforceIQ's HR workspace is intentionally aggregate-only.
# Individual career-interest candidate queries were removed because
# the current MVP does not expose employee-level career interests to HR.
#
# =========================================================


def get_internal_training_outcomes():
    """
    Return the internal learning catalog at training-skill outcome level.
    """
    query = """
    SELECT
        tp.training_id,
        tp.training_name,
        tp.estimated_weeks,
        tp.training_description,
        ts.skill_id,
        s.skill_name,
        ts.course_skill_level

    FROM training_programs tp

    JOIN training_skills ts
        ON ts.training_id = tp.training_id

    JOIN skills s
        ON s.skill_id = ts.skill_id

    ORDER BY
        tp.training_name,
        s.skill_name;
    """

    with get_connection() as conn:
        return pd.read_sql_query(
            query,
            conn,
        )


def get_all_role_skill_requirements():
    """
    Return role-skill requirements for every existing role,
    independent of any planning period or headcount scenario.
    """
    query = """
    SELECT
        r.role_id,
        r.role_name,
        d.department_name,
        rs.skill_id,
        s.skill_name,
        s.skill_category,
        rs.required_level,
        rs.importance_level
    FROM roles r
    JOIN departments d
        ON d.department_id = r.department_id
    JOIN role_skills rs
        ON rs.role_id = r.role_id
    JOIN skills s
        ON s.skill_id = rs.skill_id
    ORDER BY
        r.role_name,
        rs.importance_level DESC,
        s.skill_name;
    """

    with get_connection() as conn:
        return pd.read_sql_query(
            query,
            conn,
        )


def get_training_prerequisites_catalog():
    """
    Return all formal prerequisites for the internal learning catalog.
    One row represents one course-prerequisite skill requirement.
    """
    query = """
    SELECT
        tp.training_id,
        tp.training_name,
        tpr.skill_id AS prerequisite_skill_id,
        s.skill_name AS prerequisite_skill,
        tpr.minimum_level

    FROM training_prerequisites tpr

    JOIN training_programs tp
        ON tp.training_id = tpr.training_id

    JOIN skills s
        ON s.skill_id = tpr.skill_id

    ORDER BY
        tp.training_name,
        s.skill_name;
    """

    with get_connection() as conn:
        return pd.read_sql_query(
            query,
            conn,
        )
