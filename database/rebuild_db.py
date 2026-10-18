#!/usr/bin/env python3
"""
Rebuild database/workforceiq.db from schema.sql + seed scripts.

Put this file in the `database/` folder (next to schema.sql) and run:

    python rebuild_db.py --dry-run          # build + check in a temp file, change nothing
    python rebuild_db.py                    # back up the old DB, then replace it
    python rebuild_db.py --keep-interests   # same, but carry over saved career interests
                                            # (and their visibility) from the old DB

Stop the Streamlit app first so the .db file is not in use.
"""

import argparse
import os
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "workforceiq.db"

# Order matters: later files depend on rows created by earlier ones.
SQL_FILES = [
    "schema.sql",
    "seed_skills.sql",
    "seed_roles_and_role_skills.sql",
    "seed_employees_and_employee_skills_final.sql",
    "seed_career_paths_revised_17.sql",
    "seed_training_programs_and_skills_67_final.sql",
    "add_training_prerequisites_and_seed.sql",
    "seed_job_openings_and_future_demand.sql",
    "seed_employee_career_interests.sql",
    "seed_employee_training_records.sql",
    "seed_hr_learning_coverage_demo.sql",
]

VALID_VISIBILITY = {"private", "opening_managers"}

TABLES = [
    "departments",
    "roles",
    "skills",
    "employees",
    "employee_skills",
    "role_skills",
    "employee_career_interests",
    "career_paths",
    "job_openings",
    "training_programs",
    "training_skills",
    "training_prerequisites",
    "employee_training_records",
    "future_demand",
]


def build(target: Path):
    """Create a fresh database at `target` from the SQL files."""
    missing = [name for name in SQL_FILES if not (DB_DIR / name).exists()]
    if missing:
        sys.exit("Missing SQL files: " + ", ".join(missing))

    if target.exists():
        target.unlink()

    conn = sqlite3.connect(target)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        for name in SQL_FILES:
            script = (DB_DIR / name).read_text(encoding="utf-8")
            try:
                conn.executescript(script)
            except sqlite3.Error as error:
                sys.exit(f"FAILED while running {name}: {error}")
            print(f"  ran {name}")
        conn.commit()
    finally:
        conn.close()


def carry_over_interests(old_db: Path, new_db: Path):
    """Replace seeded career interests with the ones saved in the old DB."""
    old = sqlite3.connect(old_db)
    try:
        rows = old.execute(
            """
            SELECT employee_id, target_role_id, created_at, visibility_level
            FROM employee_career_interests
            """
        ).fetchall()
    except sqlite3.Error as error:
        print(f"  could not read old career interests ({error}); keeping seeds")
        return
    finally:
        old.close()

    new = sqlite3.connect(new_db)
    new.execute("PRAGMA foreign_keys = ON")
    kept = skipped = 0
    try:
        new.execute("DELETE FROM employee_career_interests")
        for employee_id, role_id, created_at, visibility in rows:
            if visibility not in VALID_VISIBILITY:
                visibility = "private"  # e.g. the removed 'hr_only'
            try:
                new.execute(
                    """
                    INSERT INTO employee_career_interests
                        (employee_id, target_role_id, created_at, visibility_level)
                    VALUES (?, ?, ?, ?)
                    """,
                    (employee_id, role_id, created_at, visibility),
                )
                kept += 1
            except sqlite3.Error:
                skipped += 1
        new.commit()
    finally:
        new.close()
    print(f"  career interests carried over: {kept} (skipped {skipped})")


def verify(db_path: Path) -> bool:
    """Print a report and return True when every check passes."""
    conn = sqlite3.connect(db_path)
    ok = True

    def check(label, passed, detail=""):
        nonlocal ok
        ok = ok and passed
        print(f"  [{'OK' if passed else 'FAIL'}] {label} {detail}".rstrip())

    check("integrity_check", conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok")

    violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    check(
        "foreign_key_check",
        not violations,
        f"({len(violations)} violations)" if violations else "",
    )

    columns = [
        row[1]
        for row in conn.execute(
            "PRAGMA table_info(employee_training_records)"
        )
    ]

    check(
        "employee_training_records has passed / assessment_score",
        {"passed", "assessment_score"} <= set(columns),
    )

    table_sql_row = conn.execute(
        """
        SELECT sql
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'employee_training_records'
        """
    ).fetchone()

    table_sql = (
        table_sql_row[0]
        if table_sql_row and table_sql_row[0]
        else ""
    )

    check(
        "completed-training CHECK requires passed IS NOT NULL",
        "passed IS NOT NULL" in table_sql,
    )

    not_passed = conn.execute(
        """
        SELECT COUNT(*)
        FROM employee_training_records
        WHERE status = 'completed'
          AND passed IS NOT 1
        """
    ).fetchone()[0]

    check(
        "every completed training has passed = 1",
        not_passed == 0,
        f"({not_passed} not)" if not_passed else "",
    )

    bad_visibility = conn.execute(
        """
        SELECT COUNT(*)
        FROM employee_career_interests
        WHERE visibility_level NOT IN (
            'private',
            'opening_managers'
        )
        """
    ).fetchone()[0]

    check(
        "career interest visibility values valid",
        bad_visibility == 0,
    )

    own_role = conn.execute(
        """
        SELECT COUNT(*)
        FROM employee_career_interests eci
        JOIN employees e
          ON e.employee_id = eci.employee_id
        WHERE e.current_role_id = eci.target_role_id
        """
    ).fetchone()[0]

    check(
        "no career interest points at the employee's own role",
        own_role == 0,
    )

    no_skills = conn.execute(
        """
        SELECT COUNT(*)
        FROM roles
        WHERE role_id NOT IN (
            SELECT role_id
            FROM role_skills
        )
        """
    ).fetchone()[0]

    check(
        "every role has required skills",
        no_skills == 0,
    )

    print(
        "  row counts: "
        + ", ".join(
            f"{table}="
            f"{conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]}"
            for table in TABLES
        )
    )

    conn.close()
    return ok


def main():
    parser = argparse.ArgumentParser(description="Rebuild workforceiq.db from SQL files.")
    parser.add_argument("--dry-run", action="store_true", help="build and check in a temp file only")
    parser.add_argument("--keep-interests", action="store_true",
                        help="carry saved career interests over from the existing DB")
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="replace the database without creating a backup (used by the public demo reset)",
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        new_db = Path(tmp) / "workforceiq_new.db"

        print("1/3 Building a fresh database ...")
        build(new_db)

        if args.keep_interests and DB_PATH.exists():
            print("2/3 Carrying over career interests ...")
            carry_over_interests(DB_PATH, new_db)
        else:
            print("2/3 Using seeded career interests")

        print("3/3 Verifying ...")
        if not verify(new_db):
            sys.exit("\nVerification failed. The existing database was NOT changed.")

        if args.dry_run:
            print("\nDry run finished. Nothing was changed.")
            return

        if DB_PATH.exists() and not args.no_backup:
            backup = DB_PATH.with_name(
                f"workforceiq_backup_{datetime.now():%Y%m%d_%H%M%S}.db"
            )
            shutil.copy2(DB_PATH, backup)
            print(f"\nBacked up old database -> {backup.name}")

        # Copy to a unique file in the database directory, then atomically
        # replace the live path. This avoids exposing a partially copied
        # SQLite file to another demo session during a reset.
        fd, staging_name = tempfile.mkstemp(
            prefix=".workforceiq_rebuild_",
            suffix=".db",
            dir=DB_DIR,
        )
        os.close(fd)
        staging = Path(staging_name)
        try:
            shutil.copy2(new_db, staging)
            staging.replace(DB_PATH)
        finally:
            staging.unlink(missing_ok=True)

        print(f"Replaced {DB_PATH}")


if __name__ == "__main__":
    main()
