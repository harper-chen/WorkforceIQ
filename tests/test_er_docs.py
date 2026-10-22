"""
The ER documentation is generated from schema.sql; these tests keep it from going stale.
"""

import importlib.util
import unittest

import support

spec = importlib.util.spec_from_file_location("generate_er_diagram", support.DATABASE_DIR / "generate_er_diagram.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

TINY_SCHEMA = """
-- a comment that must be ignored
CREATE TABLE parents (
    parent_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE children (
    child_id INTEGER NOT NULL,
    parent_id INTEGER NOT NULL,
    boss_id INTEGER,
    score INTEGER NOT NULL,
    kind TEXT NOT NULL DEFAULT 'a',

    PRIMARY KEY (child_id, parent_id),
    FOREIGN KEY (parent_id)
        REFERENCES parents(parent_id),
    FOREIGN KEY (boss_id)
        REFERENCES parents(parent_id),
    CHECK (score BETWEEN 1 AND 5),
    CHECK (kind IN ('a', 'b'))
);
"""


class TestParser(unittest.TestCase):
    def setUp(self):
        self.tables = gen.parse_schema(TINY_SCHEMA)

    def test_finds_tables_in_file_order(self):
        self.assertEqual(list(self.tables), ["parents", "children"])

    def test_inline_and_composite_primary_keys(self):
        self.assertEqual(self.tables["parents"]["primary_key"], ["parent_id"])
        self.assertEqual(self.tables["children"]["primary_key"], ["child_id", "parent_id"])

    def test_foreign_keys(self):
        fks = self.tables["children"]["foreign_keys"]
        self.assertEqual([fk["column"] for fk in fks], ["parent_id", "boss_id"])
        self.assertEqual({fk["ref_table"] for fk in fks}, {"parents"})

    def test_column_details(self):
        columns = {c["name"]: c for c in self.tables["children"]["columns"]}
        self.assertTrue(columns["parent_id"]["not_null"])
        self.assertFalse(columns["boss_id"]["not_null"])
        self.assertEqual(columns["kind"]["default"], "'a'")
        self.assertEqual(columns["score"]["note"], "1 to 5")
        self.assertEqual(columns["kind"]["note"], "one of: a, b")
        self.assertTrue({c["name"]: c for c in self.tables["parents"]["columns"]}["name"]["unique"])

    def test_nullable_foreign_key_uses_a_zero_or_one_parent_end(self):
        lines = gen._relationship_lines(self.tables, ["children"])
        self.assertIn('    parents ||--o{ children : "parent_id"', lines)
        self.assertIn('    parents |o--o{ children : "boss_id"', lines)

    def test_dbml_output(self):
        dbml = gen.render_dbml(self.tables)
        self.assertIn("Ref: children.parent_id > parents.parent_id", dbml)
        self.assertIn("(child_id, parent_id) [pk]", dbml)
        self.assertIn("kind text [not null, default: 'a', note: 'one of: a, b']", dbml)

    def test_empty_input_is_an_error(self):
        with self.assertRaises(ValueError):
            gen.parse_schema("-- nothing here")


class TestRealSchemaDocumentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = gen.generate()
        cls.tables = cls.result["tables"]

    def test_all_fourteen_tables_are_parsed(self):
        self.assertEqual(len(self.tables), 14)

    def test_every_table_has_a_primary_key(self):
        for name, table in self.tables.items():
            self.assertTrue(table["primary_key"], name)

    def test_committed_diagram_files_match_the_schema(self):
        self.assertEqual(gen.MERMAID_PATH.read_text(encoding="utf-8"), self.result["mermaid_markdown"])
        self.assertEqual(gen.DBML_PATH.read_text(encoding="utf-8"), self.result["dbml"])

    def test_every_table_appears_in_both_outputs(self):
        for name in self.tables:
            self.assertIn(f"    {name} {{", self.result["mermaid_markdown"], name)
            self.assertIn(f"Table {name} {{", self.result["dbml"], name)

    def test_every_foreign_key_is_drawn(self):
        total = sum(len(t["foreign_keys"]) for t in self.tables.values())
        self.assertEqual(total, 20)
        self.assertEqual(self.result["dbml"].count("\nRef: "), total)
        overview_lines = [line for line in self.result["overview"].splitlines() if "--o{" in line]
        self.assertEqual(len(overview_lines), total)

    def test_groups_cover_every_table_exactly_once(self):
        grouped = [name for _, _, owned in gen.GROUPS for name in owned]
        self.assertEqual(sorted(grouped), sorted(self.tables))

    def test_readmes_embed_the_current_overview_diagram(self):
        for name in ("README.md", "README.zh-TW.md"):
            text = (support.ROOT / name).read_text(encoding="utf-8")
            self.assertTrue(
                self.result["overview"] in text,
                f"{name} has an out-of-date or missing ER overview; copy the output of "
                "`python database/generate_er_diagram.py --overview` into its mermaid block",
            )


if __name__ == "__main__":
    unittest.main()
