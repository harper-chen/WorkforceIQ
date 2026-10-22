#!/usr/bin/env python3
"""
Generate the data-model documentation straight from database/schema.sql.

Outputs
-------
docs/er-diagram.md   Mermaid ER diagrams (GitHub renders them natively)
docs/schema.dbml     DBML, paste into https://dbdiagram.io to get a polished image

Usage
-----
    python database/generate_er_diagram.py            # (re)write both files
    python database/generate_er_diagram.py --check    # exit 1 when the files are out of date
    python database/generate_er_diagram.py --overview # print the overview diagram for the README

The schema is the single source of truth, so the diagrams cannot drift from the real tables.
The automated tests run the --check logic, so a schema change without regenerating fails CI.
"""

import argparse
import re
import sys
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DB_DIR.parent
SCHEMA_PATH = DB_DIR / "schema.sql"
MERMAID_PATH = PROJECT_ROOT / "docs" / "er-diagram.md"
DBML_PATH = PROJECT_ROOT / "docs" / "schema.dbml"

# Detail diagrams: (title, description, tables owned by the diagram)
GROUPS = [
    (
        "Organization and skills",
        "Who works where, which skills exist, what each role requires, and what each employee has recorded.",
        ["departments", "roles", "skills", "employees", "employee_skills", "role_skills"],
    ),
    (
        "Career interests and staffing",
        "Employee-controlled career interests, possible career paths, and manager-owned job openings.",
        ["employee_career_interests", "career_paths", "job_openings"],
    ),
    (
        "Learning and workforce planning",
        "The internal training catalog, who has completed what, and planned future headcount by role.",
        [
            "training_programs",
            "training_skills",
            "training_prerequisites",
            "employee_training_records",
            "future_demand",
        ],
    ),
]


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _strip_comments(sql):
    return re.sub(r"--[^\n]*", "", sql)


def _split_top_level(body):
    """Split a CREATE TABLE body on commas that are not inside parentheses."""
    parts, depth, current = [], 0, []
    for char in body:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _columns_in(text):
    return [name.strip() for name in text.split(",") if name.strip()]


def parse_schema(sql):
    """
    Return {table_name: table} in file order.

    table = {
        "columns": [{"name", "type", "not_null", "unique", "default", "note"}],
        "primary_key": [column, ...],
        "foreign_keys": [{"column", "ref_table", "ref_column"}],
    }
    """
    sql = _strip_comments(sql)
    tables = {}

    for match in re.finditer(
        r"CREATE\s+TABLE\s+(\w+)\s*\((.*?)\)\s*;", sql, flags=re.S | re.I
    ):
        name, body = match.group(1), match.group(2)
        table = {"columns": [], "primary_key": [], "foreign_keys": []}
        notes = {}

        for item in _split_top_level(body):
            flat = re.sub(r"\s+", " ", item).strip()
            upper = flat.upper()

            if upper.startswith("FOREIGN KEY"):
                fk = re.match(
                    r"FOREIGN KEY \((\w+)\) REFERENCES (\w+) ?\((\w+)\)", flat, flags=re.I
                )
                table["foreign_keys"].append(
                    {"column": fk.group(1), "ref_table": fk.group(2), "ref_column": fk.group(3)}
                )
            elif upper.startswith("PRIMARY KEY"):
                pk = re.match(r"PRIMARY KEY \((.+)\)", flat, flags=re.I)
                table["primary_key"] = _columns_in(pk.group(1))
            elif upper.startswith("UNIQUE"):
                continue
            elif upper.startswith("CHECK"):
                between = re.match(r"CHECK \( ?(\w+) BETWEEN (\d+) AND (\d+) ?\)", flat, flags=re.I)
                value_list = re.match(r"CHECK \( ?(\w+) IN \(([^)]*)\) ?\)", flat, flags=re.I)
                if between:
                    notes[between.group(1)] = f"{between.group(2)} to {between.group(3)}"
                elif value_list:
                    values = ", ".join(v.strip().strip("'") for v in value_list.group(2).split(","))
                    notes[value_list.group(1)] = f"one of: {values}"
            else:
                tokens = flat.split(" ")
                column = {
                    "name": tokens[0],
                    "type": tokens[1].upper(),
                    "not_null": "NOT NULL" in upper,
                    "unique": bool(re.search(r"\bUNIQUE\b", upper)),
                    "default": None,
                    "note": None,
                }
                default = re.search(r"DEFAULT ('[^']*'|[\w.]+)", flat, flags=re.I)
                if default:
                    column["default"] = default.group(1)
                if "PRIMARY KEY" in upper:
                    table["primary_key"] = [column["name"]]
                table["columns"].append(column)

        for column in table["columns"]:
            column["note"] = notes.get(column["name"])
        tables[name] = table

    if not tables:
        raise ValueError("No CREATE TABLE statements found.")
    return tables


# ---------------------------------------------------------------------------
# Mermaid
# ---------------------------------------------------------------------------

def _relationship_lines(tables, child_names):
    """Mermaid relationship lines for every foreign key held by `child_names`."""
    lines = []
    for child in child_names:
        columns = {c["name"]: c for c in tables[child]["columns"]}
        for fk in tables[child]["foreign_keys"]:
            nullable = not columns[fk["column"]]["not_null"] and fk["column"] not in tables[child]["primary_key"]
            left = "|o" if nullable else "||"
            lines.append(f'    {fk["ref_table"]} {left}--o{{ {child} : "{fk["column"]}"')
    return lines


def _entity_block(name, table, key_columns_only=False):
    fk_columns = {fk["column"] for fk in table["foreign_keys"]}
    lines = [f"    {name} {{"]
    for column in table["columns"]:
        is_pk = column["name"] in table["primary_key"]
        if key_columns_only and not is_pk:
            continue
        keys = []
        if is_pk:
            keys.append("PK")
        if column["name"] in fk_columns:
            keys.append("FK")
        suffix = f" {', '.join(keys)}" if keys else ""
        lines.append(f"        {column['type']} {column['name']}{suffix}")
    lines.append("    }")
    return lines


def mermaid_overview(tables):
    """All tables and relationships, no columns: a one-glance map."""
    lines = ["erDiagram"]
    lines += _relationship_lines(tables, list(tables))
    return "\n".join(lines)


def mermaid_group(tables, owned):
    lines = ["erDiagram"]
    lines += _relationship_lines(tables, owned)

    context = []
    for name in owned:
        for fk in tables[name]["foreign_keys"]:
            if fk["ref_table"] not in owned and fk["ref_table"] not in context:
                context.append(fk["ref_table"])

    for name in owned:
        lines += _entity_block(name, tables[name])
    for name in context:
        lines += _entity_block(name, tables[name], key_columns_only=True)
    return "\n".join(lines)


def render_mermaid_markdown(tables):
    parts = [
        "# Data model",
        "",
        "<!-- Generated by database/generate_er_diagram.py from database/schema.sql. Do not edit by hand. -->",
        "",
        f"WorkforceIQ stores its data in {len(tables)} SQLite tables. "
        "The diagrams below are generated from `database/schema.sql`, "
        "so they always match the real schema.",
        "",
        "In each diagram, `PK` marks a primary key and `FK` a foreign key. "
        "A line reads \"one parent row has zero or more child rows\". "
        "The label on the line is the foreign-key column; a nullable foreign key "
        "(for example `employees.manager_id`) uses a \"zero or one\" parent end.",
        "",
        "For a polished, shareable image, paste [`docs/schema.dbml`](schema.dbml) into "
        "[dbdiagram.io](https://dbdiagram.io).",
        "",
        "## Overview",
        "",
        "All tables and how they relate.",
        "",
        "```mermaid",
        mermaid_overview(tables),
        "```",
    ]

    for title, description, owned in GROUPS:
        parts += ["", f"## {title}", "", description, "", "```mermaid", mermaid_group(tables, owned), "```"]

    parts += [
        "",
        "## Rules enforced by the database",
        "",
        "Beyond keys, the schema enforces these rules with `CHECK` constraints:",
        "",
        "- Skill proficiency, required level, importance and course level are integers from 1 to 5.",
        "- Career-interest visibility is `private` or `opening_managers`.",
        "- A job opening is `open`, `paused`, `filled` or `closed`, and its headcount is positive.",
        "- A career path cannot point a role at itself.",
        "- A completed training record needs a completion date and `passed = 1`; "
        "enrolled, in-progress and withdrawn records must have neither.",
        "- Future required headcount cannot be negative; each role has at most one row per planning period.",
        "",
    ]
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# DBML
# ---------------------------------------------------------------------------

def render_dbml(tables):
    lines = [
        "// Generated by database/generate_er_diagram.py from database/schema.sql. Do not edit by hand.",
        "// Paste this file into https://dbdiagram.io (Import > DBML) to get a polished diagram.",
        "",
    ]
    references = []

    for name, table in tables.items():
        lines.append(f"Table {name} {{")
        single_pk = table["primary_key"] if len(table["primary_key"]) == 1 else []
        for column in table["columns"]:
            settings = []
            if column["name"] in single_pk:
                settings.append("pk")
            if column["not_null"] and column["name"] not in single_pk:
                settings.append("not null")
            if column["unique"]:
                settings.append("unique")
            if column["default"] is not None:
                settings.append(f"default: {column['default']}")
            if column["note"]:
                settings.append(f"note: '{column['note']}'")
            suffix = f" [{', '.join(settings)}]" if settings else ""
            lines.append(f"  {column['name']} {column['type'].lower()}{suffix}")
        if len(table["primary_key"]) > 1:
            lines += ["", "  indexes {", f"    ({', '.join(table['primary_key'])}) [pk]", "  }"]
        lines += ["}", ""]
        for fk in table["foreign_keys"]:
            references.append(f"Ref: {name}.{fk['column']} > {fk['ref_table']}.{fk['ref_column']}")

    lines += references
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def generate(schema_path=SCHEMA_PATH):
    tables = parse_schema(Path(schema_path).read_text(encoding="utf-8"))
    return {
        "tables": tables,
        "mermaid_markdown": render_mermaid_markdown(tables),
        "dbml": render_dbml(tables),
        "overview": mermaid_overview(tables),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate ER diagrams from schema.sql.")
    parser.add_argument("--check", action="store_true", help="fail when the generated files are out of date")
    parser.add_argument("--overview", action="store_true", help="print the overview diagram and exit")
    args = parser.parse_args()

    result = generate()

    if args.overview:
        print(result["overview"])
        return

    targets = {MERMAID_PATH: result["mermaid_markdown"], DBML_PATH: result["dbml"]}

    if args.check:
        stale = [
            str(path.relative_to(PROJECT_ROOT))
            for path, text in targets.items()
            if not path.exists() or path.read_text(encoding="utf-8") != text
        ]
        if stale:
            sys.exit("Out of date: " + ", ".join(stale) + "\nRun: python database/generate_er_diagram.py")
        print("ER documentation is up to date.")
        return

    for path, text in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
