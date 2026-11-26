"""
English / Traditional Chinese interface text.

Checks that both languages define the same text, that their {placeholders}
agree, that English stays the default, and that every readiness result and
staffing route has Chinese wording.
"""

import string
import unittest
from unittest import mock

import pandas as pd

import support  # noqa: F401  (sets up the import path)
import i18n
from readiness import get_candidate_internal_readiness, get_opening_staffing_route

from test_readiness import candidate


def placeholders(text):
    return {
        name
        for _, name, _, _ in string.Formatter().parse(text)
        if name
    }


def use_lang(lang):
    params = {"lang": lang} if lang else {}
    return mock.patch.object(i18n.st, "query_params", params)


class TextTableTests(unittest.TestCase):
    def test_every_chinese_key_exists_in_english(self):
        # ready_* / route_* are Chinese-only: English wording for those
        # comes straight from readiness.py.
        extra = {
            key
            for key in set(i18n.TEXT["zh"]) - set(i18n.TEXT["en"])
            if not key.startswith(("ready_", "route_"))
        }
        self.assertEqual(extra, set())

    def test_every_english_key_has_chinese(self):
        # Chinese has no plural, so key_one may fall back to key_other.
        missing = {
            key
            for key in i18n.TEXT["en"]
            if key not in i18n.TEXT["zh"]
            and not (
                key.endswith("_one")
                and key[: -len("_one")] + "_other" in i18n.TEXT["zh"]
            )
        }
        self.assertEqual(missing, set())

    def test_chinese_only_uses_placeholders_the_code_passes(self):
        # Chinese may leave a value out (e.g. a repeated number), but must
        # never ask for one the English call does not provide.
        for key, english in i18n.TEXT["en"].items():
            chinese = i18n.TEXT["zh"].get(key)
            if chinese is None:
                continue
            with self.subTest(key=key):
                self.assertLessEqual(placeholders(chinese), placeholders(english))


class LanguageSelectionTests(unittest.TestCase):
    def test_english_is_the_default(self):
        with use_lang(None):
            self.assertEqual(i18n.get_lang(), "en")
            self.assertEqual(i18n.t("skill_match"), "Skill Match")

    def test_only_lang_zh_switches_to_chinese(self):
        for value in ("zh-TW", "ZH", "fr", ""):
            with use_lang(value):
                self.assertEqual(i18n.get_lang(), "en")
        with use_lang("zh"):
            self.assertEqual(i18n.t("skill_match"), "技能符合度")

    def test_plural_text(self):
        with use_lang(None):
            self.assertEqual(i18n.tn("courses_shown", 1), "1 course shown.")
            self.assertEqual(i18n.tn("courses_shown", 3), "3 courses shown.")
        with use_lang("zh"):
            self.assertEqual(i18n.tn("courses_shown", 1), "共 1 門課程。")

    def test_demo_data_translation_only_in_chinese(self):
        with use_lang(None):
            self.assertEqual(i18n.department("Human Resources"), "Human Resources")
        with use_lang("zh"):
            self.assertEqual(i18n.department("Human Resources"), "人力資源部")
            self.assertEqual(i18n.skill_category("Security"), "資訊安全")


READINESS_CASES = {
    "ready_now": candidate(match=90.0),
    "train_first": candidate(match=70.0),
    "larger_gap": candidate(match=40.0),
    "not_assessed_limited": candidate(met=2, to_develop=1, not_recorded=7),
    "not_assessed_unrecorded": candidate(
        match=55.0, met=7, to_develop=2, not_recorded=1, best_case=75.0
    ),
    "train_first_might_be_ready": candidate(
        match=70.0, met=7, to_develop=2, not_recorded=1, best_case=90.0
    ),
}


class ReadinessWordingTests(unittest.TestCase):
    def test_english_wording_is_unchanged(self):
        with use_lang(None):
            for name, cand in READINESS_CASES.items():
                result = get_candidate_internal_readiness(cand)
                with self.subTest(case=name):
                    self.assertEqual(
                        i18n.readiness_text(result),
                        (result["label"], result["explanation"]),
                    )

    def test_every_result_has_chinese_wording(self):
        with use_lang("zh"):
            for name, cand in READINESS_CASES.items():
                result = get_candidate_internal_readiness(cand)
                label, explanation = i18n.readiness_text(result)
                with self.subTest(case=name, code=result["code"]):
                    self.assertNotEqual(label, result["label"])
                    self.assertNotEqual(explanation, result["explanation"])

    def test_unrecorded_numbers_appear_in_chinese(self):
        result = get_candidate_internal_readiness(
            READINESS_CASES["not_assessed_unrecorded"]
        )
        with use_lang("zh"):
            _, explanation = i18n.readiness_text(result)
        self.assertIn("55.0%", explanation)
        self.assertIn("75.0%", explanation)

    def test_every_route_has_chinese_wording(self):
        groups = {
            "no_interest": [],
            "ready_now": [READINESS_CASES["ready_now"]],
            "train_first": [READINESS_CASES["train_first"]],
            "more_evidence_needed": [READINESS_CASES["not_assessed_limited"]],
            "none_close": [READINESS_CASES["larger_gap"]],
        }
        for variant, rows in groups.items():
            route = get_opening_staffing_route(pd.DataFrame(rows))
            with self.subTest(variant=variant):
                self.assertEqual(route["variant"], variant)
                with use_lang("zh"):
                    label, readiness, explanation = i18n.route_text(route)
                self.assertNotEqual(label, route["route_label"])
                self.assertNotEqual(explanation, route["explanation"])
                if route["readiness_label"]:
                    self.assertNotEqual(readiness, route["readiness_label"])


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------
# Demo data (roles, skills, courses)
# ---------------------------------------------------------------------------

import contextlib  # noqa: E402
import importlib.util  # noqa: E402
import io  # noqa: E402
import sqlite3  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

import i18n_data  # noqa: E402
from views.learning_catalog import row_matches_search  # noqa: E402


class DemoDataTranslationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "rebuild_db", support.DATABASE_DIR / "rebuild_db.py"
        )
        rebuild = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rebuild)
        cls._tmp = tempfile.TemporaryDirectory()
        path = Path(cls._tmp.name) / "seeded.db"
        with contextlib.redirect_stdout(io.StringIO()):
            rebuild.build(path)
        connection = sqlite3.connect(path)
        try:
            cls.roles = {r[0] for r in connection.execute("SELECT role_name FROM roles")}
            cls.skills = {r[0] for r in connection.execute("SELECT skill_name FROM skills")}
            cls.courses = {
                r[0] for r in connection.execute("SELECT training_name FROM training_programs")
            }
        finally:
            connection.close()

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_every_seeded_name_has_chinese(self):
        self.assertEqual(self.roles - set(i18n_data.ROLES_ZH), set())
        self.assertEqual(self.skills - set(i18n_data.SKILLS_ZH), set())
        self.assertEqual(self.courses - set(i18n_data.COURSES_ZH), set())
        self.assertEqual(self.courses - set(i18n_data.COURSE_DESCRIPTIONS_ZH), set())

    def test_chinese_names_are_unique(self):
        # Grouping and selection by name must not merge two different items.
        for table in (i18n_data.ROLES_ZH, i18n_data.SKILLS_ZH, i18n_data.COURSES_ZH):
            self.assertEqual(len(set(table.values())), len(table))

    def test_short_role_name_for_narrow_places(self):
        with use_lang(None):
            self.assertEqual(i18n_data.short_role_name("Systems Analyst"), "Systems Analyst")
        with use_lang("zh"):
            self.assertEqual(i18n_data.short_role_name("Systems Analyst"), "系統分析師")

    def test_english_results_are_untouched(self):
        frame = pd.DataFrame({"role_name": ["Systems Analyst"], "skill_name": ["Negotiation"]})
        with use_lang(None):
            self.assertIs(i18n_data.localize(frame), frame)

    def test_chinese_results_keep_english_for_search(self):
        frame = pd.DataFrame(
            {
                "role_name": ["Systems Analyst"],
                "skill_name": ["Stakeholder Management"],
                "training_name": ["Python Foundations"],
                "training_description": ["English text"],
            }
        )
        with use_lang("zh"):
            result = i18n_data.localize(frame)
        row = result.iloc[0]
        self.assertEqual(row["role_name"], "系統分析師（Systems Analyst）")
        self.assertEqual(row["skill_name"], "利害關係人管理")
        self.assertEqual(row["skill_name_en"], "Stakeholder Management")
        self.assertEqual(row["training_name"], "Python 基礎")
        self.assertTrue(row["training_description"].startswith("學習 Python"))
        self.assertEqual(row["training_description_en"], "English text")

    def test_nested_learning_results_are_translated(self):
        learning = {
            "ready": [
                {
                    "training_name": "Python Foundations",
                    "estimated_weeks": 3,
                    "improvement_details": [{"skill_name": "Python Fundamentals"}],
                }
            ],
            "locked": [],
        }
        with use_lang("zh"):
            result = i18n_data.localize(learning)
        course = result["ready"][0]
        self.assertEqual(course["training_name"], "Python 基礎")
        self.assertEqual(course["estimated_weeks"], 3)
        self.assertEqual(course["improvement_details"][0]["skill_name"], "Python 基礎")

    def test_learning_search_matches_chinese_and_english(self):
        frame = pd.DataFrame(
            {
                "training_name": ["Advanced SQL Analytics"],
                "skill_name": ["SQL Querying & Analysis"],
                "training_description": ["Apply advanced SQL techniques."],
            }
        )
        with use_lang("zh"):
            row = i18n_data.localize(frame).iloc[0]
        self.assertTrue(row_matches_search(row, "進階"))
        self.assertTrue(row_matches_search(row, "SQL 查詢"))
        self.assertTrue(row_matches_search(row, "advanced sql"))
        self.assertFalse(row_matches_search(row, "資安"))
