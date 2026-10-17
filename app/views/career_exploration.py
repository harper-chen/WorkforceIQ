"""
Career Exploration (employee workspace) -- master-detail layout.

List views (Recommended / Explore All / Saved) show compact cards only.
"View details" opens ONE full-width detail page for the selected role, so:
  * there is no expander-inside-expander problem,
  * the heavy learning recommendation runs only for the selected role,
  * each skill gap shows its learning options directly underneath it.
"""

import inspect
import json
import time
from html import escape

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from db import (
    get_employee_profile,
    get_recommended_careers,
    get_target_role_skill_details,
    get_recommended_learning,
    get_internal_training_outcomes,
    is_career_saved,
    save_career_interest,
    delete_career_interest,
    get_saved_careers,
    update_career_visibility,
)


# =========================================================
# Constants
# =========================================================

DEPARTMENT_COLORS = {
    "Human Resources": "#F8D7DA",
    "Information Technology": "#D6E4FF",
    "Product & Engineering": "#D9F2E6",
    "Business Operations": "#FCE8C3",
}

LEVEL_LABELS = {
    1: "Foundational",
    2: "Basic",
    3: "Working",
    4: "Advanced",
    5: "Expert",
}

VISIBILITY_LABELS = {
    "private": "Private",
    "opening_managers": "Visible to opening managers",
}

VISIBILITY_OPTIONS = ["private", "opening_managers"]

CAREER_VIEWS = [
    "Recommended Careers",
    "Explore All Careers",
    "Saved Careers",
]

# Session-state keys
DETAIL_ROLE_KEY = "career_detail_role_id"
DETAIL_EMPLOYEE_KEY = "career_detail_employee_id"
FLASH_KEY = "_career_flash"
CARD_ANCHOR_KEY = "_career_card_anchor"      # which card opened the detail
SCROLL_RESTORE_KEY = "_career_scroll_restore"  # scroll back to that card once
SCROLL_TOP_KEY = "_career_scroll_top"          # scroll detail page to top once

# Widget keys of the list views. Streamlit deletes the state of widgets that
# are not rendered in a run, so while the detail page is open we re-assign
# these keys to keep filters / search / selected view when the user comes back.
LIST_WIDGET_KEYS = [
    "career_view",
    "career_search",
    "career_sort",
    "selected_departments",
    "selected_levels",
]

MAX_OPTIONS_PER_SKILL = 3


def _button_stretch_kwargs():
    """width='stretch' on new Streamlit, use_container_width on older ones."""
    try:
        if "width" in inspect.signature(st.button).parameters:
            return {"width": "stretch"}
    except (TypeError, ValueError):
        pass
    return {"use_container_width": True}


STRETCH = _button_stretch_kwargs()


# =========================================================
# Small helpers
# =========================================================

def pluralize(count: int, singular: str, plural: str | None = None) -> str:
    if plural is None:
        plural = f"{singular}s"
    return singular if count == 1 else plural


def _flash(message: str):
    """Show a toast on the NEXT run (survives st.rerun())."""
    st.session_state[FLASH_KEY] = message


def _show_flash():
    message = st.session_state.pop(FLASH_KEY, None)
    if message:
        st.toast(message)


def _keep_list_widget_state():
    for key in LIST_WIDGET_KEYS:
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]


def _department_badge_html(department) -> str:
    color = DEPARTMENT_COLORS.get(department, "#E5E7EB")
    return (
        f'<span style="display:inline-block;background-color:{color};'
        "color:#1F2937;padding:4px 10px;border-radius:999px;"
        'font-size:0.8rem;font-weight:600;white-space:nowrap;">'
        f"{escape(str(department))}</span>"
    )


def _level_bar_html(current_level, required_level: int) -> str:
    """One bar: filled = current level, dark marker = required level."""
    current_pct = (current_level or 0) * 20
    required_pct = required_level * 20
    return (
        '<div style="position:relative;height:10px;background:#E5E7EB;'
        'border-radius:999px;margin:8px 0 6px 0;">'
        f'<div style="width:{current_pct}%;height:100%;background:#6B8EAD;'
        'border-radius:999px;"></div>'
        f'<div style="position:absolute;left:calc({required_pct}% - 2px);'
        "top:-3px;width:4px;height:16px;background:#374151;"
        'border-radius:2px;"></div></div>'
    )


# =========================================================
# Navigation (list <-> detail)
# =========================================================

def _open_detail(role_id: int, employee_id: int, button_key: str, position: int):
    """on_click callback of a card's 'View details' button."""
    st.session_state[DETAIL_ROLE_KEY] = int(role_id)
    st.session_state[DETAIL_EMPLOYEE_KEY] = int(employee_id)
    st.session_state[CARD_ANCHOR_KEY] = {"key": button_key, "position": position}
    st.session_state[SCROLL_TOP_KEY] = True


def _close_detail():
    st.session_state.pop(DETAIL_ROLE_KEY, None)
    st.session_state.pop(DETAIL_EMPLOYEE_KEY, None)
    st.session_state.pop(CARD_ANCHOR_KEY, None)


def _back_to_list():
    """on_click callback of the Back button: close detail, remember the card."""
    anchor = st.session_state.get(CARD_ANCHOR_KEY)
    _close_detail()
    if anchor:
        st.session_state[SCROLL_RESTORE_KEY] = anchor


# =========================================================
# Scroll helpers (small JS snippets)
# =========================================================

def _run_js(js: str):
    """
    Run a JS snippet against the Streamlit page. components.html renders in
    an iframe, so we reach the real page through window.parent. The nonce
    makes the HTML different every time, otherwise Streamlit would reuse the
    old iframe and the script would not run again.
    """
    try:
        components.html(
            f"<!-- {time.time_ns()} --><script>(function(){{{js}}})();</script>",
            height=0,
        )
    except Exception:
        pass  # scrolling is a nicety, never break the page for it


def _scroll_to_card(anchor: dict):
    key = json.dumps(anchor["key"])
    position = int(anchor["position"])
    _run_js(
        f"""
        var doc = window.parent.document;
        var key = {key};
        var position = {position};
        var tries = 0;
        function findCard() {{
            // Streamlit >= 1.39 puts the widget key on a CSS class.
            var el = doc.querySelector(".st-key-" + key);
            if (el) return el;
            // Older versions: the position-th 'View details' button.
            var buttons = Array.prototype.filter.call(
                doc.querySelectorAll("button"),
                function (b) {{ return (b.innerText || "").trim() === "View details"; }}
            );
            return buttons[position] || null;
        }}
        function go() {{
            var el = findCard();
            if (el) {{
                el.scrollIntoView({{block: "center"}});
                // once more after late layout changes
                setTimeout(function () {{ el.scrollIntoView({{block: "center"}}); }}, 250);
                return;
            }}
            if (tries++ < 30) setTimeout(go, 100);
        }}
        go();
        """
    )


def _scroll_to_top():
    _run_js(
        """
        var doc = window.parent.document;
        function top() {
            var c = doc.querySelector('[data-testid="stMain"]')
                 || doc.querySelector('section.main')
                 || doc.querySelector('.main');
            if (c) c.scrollTo(0, 0);
            window.parent.scrollTo(0, 0);
        }
        top();
        setTimeout(top, 150);
        """
    )


# =========================================================
# Save / Unsave + Visibility
# =========================================================

def clear_career_interest_session_state(employee_id: int, role_id: int):
    """Drop cached UI state for one saved career (e.g. after unsave)."""
    for key in (
        f"career_saved_state_{employee_id}_{role_id}",
        f"career_visibility_db_{employee_id}_{role_id}",
        f"career_visibility_select_{employee_id}_{role_id}",
    ):
        st.session_state.pop(key, None)


@st.fragment
def render_save_career_control(employee_id: int, role_id: int):
    saved_key = f"career_saved_state_{employee_id}_{role_id}"

    if saved_key not in st.session_state:
        st.session_state[saved_key] = is_career_saved(employee_id, role_id)

    if st.session_state[saved_key]:
        if st.button(
            "Unsave Career",
            key=f"unsave_career_button_{employee_id}_{role_id}",
            **STRETCH,
        ):
            deleted = delete_career_interest(employee_id, role_id)
            clear_career_interest_session_state(employee_id, role_id)
            _flash(
                "Career removed from your saved interests."
                if deleted
                else "This career was no longer saved."
            )
            # Full rerun: Saved Careers and visibility must reflect the DB.
            st.rerun()
        st.caption(
            "Saved to your career interests. "
            "Removing it also removes its sharing visibility."
        )
        return

    if st.button(
        "Save Career",
        key=f"save_career_button_{employee_id}_{role_id}",
        **STRETCH,
    ):
        save_career_interest(employee_id, role_id)
        # Re-read from the DB so a stale session can never show a wrong state.
        st.session_state[saved_key] = is_career_saved(employee_id, role_id)
        if st.session_state[saved_key]:
            _flash("Career saved privately.")
            st.rerun()
        else:
            st.error("This career could not be saved.")


@st.fragment
def render_career_visibility_control(
    employee_id: int,
    role_id: int,
    current_visibility: str,
):
    widget_key = f"career_visibility_select_{employee_id}_{role_id}"
    stored_key = f"career_visibility_db_{employee_id}_{role_id}"

    # Normalise legacy values (e.g. the removed "hr_only").
    if stored_key not in st.session_state:
        st.session_state[stored_key] = (
            current_visibility
            if current_visibility in VISIBILITY_OPTIONS
            else "private"
        )
    if st.session_state[stored_key] not in VISIBILITY_OPTIONS:
        st.session_state[stored_key] = "private"
    if (
        widget_key in st.session_state
        and st.session_state[widget_key] not in VISIBILITY_OPTIONS
    ):
        st.session_state.pop(widget_key, None)

    stored = st.session_state[stored_key]

    selected = st.selectbox(
        "Visibility",
        options=VISIBILITY_OPTIONS,
        index=VISIBILITY_OPTIONS.index(stored),
        format_func=lambda value: VISIBILITY_LABELS[value],
        key=widget_key,
        label_visibility="collapsed",
    )

    # A change reruns only this fragment; persist immediately.
    if selected != stored:
        if update_career_visibility(employee_id, role_id, selected):
            st.session_state[stored_key] = selected
            st.success("Visibility updated.")
        else:
            st.error("This saved career could not be updated.")

    if selected == "private":
        st.caption("Only you can see this career interest.")
    else:
        st.caption(
            "Managers responsible for openings for this exact "
            "role can see this career interest."
        )


# =========================================================
# Skill state + learning lookups (used by the detail page)
# =========================================================

def _skill_state(skill_row) -> dict:
    """
    status: 'met' | 'gap' | 'not_recorded'
    'Not recorded' is evidence that is missing, not a zero skill level.
    """
    required = int(skill_row["required_level"])
    importance = int(skill_row["importance_level"])
    proficiency = skill_row["proficiency_level"]

    if proficiency is None or pd.isna(proficiency):
        return {
            "status": "not_recorded",
            "current": None,
            "required": required,
            "importance": importance,
            "gap": required,
            "label": "Not recorded",
        }

    current = int(proficiency)
    gap = required - current

    if gap <= 0:
        label, status = "Meets requirement", "met"
    elif gap == 1:
        label, status = "Small gap", "gap"
    elif importance >= 4:
        label, status = "Priority gap", "gap"
    else:
        label, status = "Significant gap", "gap"

    return {
        "status": status,
        "current": current,
        "required": required,
        "importance": importance,
        "gap": gap,
        "label": label,
    }


def _load_learning(employee_id: int, role_id: int) -> dict:
    """
    Use the uncapped recommendation list when db.py supports it
    (max_ready / max_locked); otherwise fall back to the default call.
    """
    try:
        params = inspect.signature(get_recommended_learning).parameters
    except (TypeError, ValueError):
        params = {}

    if "max_ready" in params and "max_locked" in params:
        return get_recommended_learning(
            employee_id,
            role_id,
            max_ready=None,
            max_locked=None,
        )
    return get_recommended_learning(employee_id, role_id)


def _build_skill_learning_index(learning: dict) -> dict:
    """skill_id -> recommended course options (in-progress/ready first)."""
    index: dict[int, list] = {}

    for status_code in ("ready", "locked"):
        for course in learning[status_code]:
            skill_names = [
                detail["skill_name"]
                for detail in course["improvement_details"]
            ]
            for detail in course["improvement_details"]:
                index.setdefault(int(detail["skill_id"]), []).append(
                    {
                        "course": course,
                        "status_code": status_code,
                        "course_level": int(detail["course_level"]),
                        "also_builds": [
                            name
                            for name in skill_names
                            if name != detail["skill_name"]
                        ],
                    }
                )

    def sort_key(option):
        course = option["course"]
        if course.get("is_in_progress"):
            rank = 0
        elif option["status_code"] == "ready":
            rank = 1
        else:
            rank = 2
        return (
            rank,
            -option["course_level"],
            int(course["estimated_weeks"]),
            course["training_name"],
        )

    for skill_id in index:
        index[skill_id].sort(key=sort_key)

    return index


def _catalog_lookup(catalog: pd.DataFrame, skill_id: int, current_level):
    """
    Whole-catalog view of one skill, independent of the recommendation caps.
    Returns (highest course level for the skill or None, up to 3 useful rows).
    """
    if catalog is None or catalog.empty:
        return None, []

    rows = catalog[catalog["skill_id"] == skill_id]
    if rows.empty:
        return None, []

    best_level = int(rows["course_skill_level"].max())
    useful = (
        rows[rows["course_skill_level"] > (current_level or 0)]
        .sort_values(
            ["course_skill_level", "estimated_weeks", "training_name"],
            ascending=[False, True, True],
        )
        .head(MAX_OPTIONS_PER_SKILL)
    )
    return best_level, useful.to_dict("records")


# =========================================================
# Detail page rendering
# =========================================================

def _render_prerequisites(course: dict):
    for prerequisite in course.get("prerequisite_options", []):
        current_text = (
            "not recorded"
            if prerequisite["not_recorded"] == 1
            else f"L{prerequisite['current_level']}"
        )
        text = (
            f"Before enrolling: **{prerequisite['skill_name']}** "
            f"{current_text} → L{prerequisite['minimum_level']}."
        )
        options = prerequisite.get("course_options", [])
        if options:
            best = options[0]
            availability = (
                "available now"
                if best["available_now"]
                else "needs its own prerequisite"
            )
            text += (
                f" Prepare with **{best['training_name']}** "
                f"({best['estimated_weeks']} wks, {availability})."
            )
        else:
            text += " No internal course provides this prerequisite."
        st.caption(text)


def _render_recommended_option(option: dict, required_level: int):
    course = option["course"]

    if course.get("is_in_progress"):
        tag = "▶ In progress"
    elif option["status_code"] == "ready":
        tag = "✓ Ready now"
    else:
        tag = "🔒 Prerequisite needed"

    level = option["course_level"]
    fit = (
        "meets required level"
        if level >= required_level
        else f"partial: L{level} of L{required_level} needed"
    )

    st.markdown(
        f"{tag} — **{course['training_name']}** · "
        f"{int(course['estimated_weeks'])} wks · reaches L{level} · {fit}"
    )

    if option["also_builds"]:
        st.caption(
            "This course also develops: "
            + ", ".join(option["also_builds"])
        )

    if option["status_code"] == "locked":
        _render_prerequisites(course)


def _render_skill_card(skill_row, state: dict, learning_index: dict, catalog):
    skill_id = int(skill_row["skill_id"])
    required = state["required"]

    with st.container(border=True):
        title_col, importance_col = st.columns([4, 1])
        with title_col:
            st.markdown(f"**{skill_row['skill_name']}**")
            st.caption(skill_row["skill_category"])
        with importance_col:
            st.caption(f"Importance {state['importance']}/5")

        current_text = (
            "Not recorded"
            if state["current"] is None
            else f"L{state['current']} {LEVEL_LABELS[state['current']]}"
        )
        st.markdown(
            f"{current_text} → needs **L{required} {LEVEL_LABELS[required]}**"
        )
        st.markdown(
            _level_bar_html(state["current"], required),
            unsafe_allow_html=True,
        )

        # ---- learning options for this skill -------------------------
        options = learning_index.get(skill_id, [])
        best_level, catalog_rows = _catalog_lookup(
            catalog,
            skill_id,
            state["current"],
        )

        st.caption("Learning options")

        if options:
            for option in options[:MAX_OPTIONS_PER_SKILL]:
                _render_recommended_option(option, required)
            hidden = len(options) - MAX_OPTIONS_PER_SKILL
            if hidden > 0:
                st.caption(
                    f"+{hidden} more {pluralize(hidden, 'option')} "
                    "in the Learning Catalog."
                )
        elif catalog_rows:
            # Courses exist but were not in the top recommendations.
            for row in catalog_rows:
                st.markdown(
                    f"ℹ️ In catalog — **{row['training_name']}** · "
                    f"{int(row['estimated_weeks'])} wks · "
                    f"reaches L{int(row['course_skill_level'])}"
                )
            st.caption(
                "Not among your top recommendations. "
                "Check the Learning Catalog for prerequisites."
            )
        elif best_level is None:
            st.caption("No internal course currently teaches this skill.")
        else:
            st.caption(
                "No internal course would raise this skill "
                "above your current level."
            )

        if best_level is not None and best_level < required:
            st.caption(
                f"Internal learning reaches at most L{best_level} "
                f"for this skill; the role needs L{required}."
            )


def _render_skill_group(
    title: str,
    caption: str,
    items: list,
    learning_index: dict,
    catalog,
):
    if not items:
        return

    st.markdown(f"#### {title} ({len(items)})")
    st.caption(caption)

    for skill_row, state in items:
        _render_skill_card(skill_row, state, learning_index, catalog)


def render_career_detail_page(role_id: int, matches: pd.DataFrame, employee_id: int):
    row = matches[matches["role_id"].astype(int) == role_id].iloc[0]

    origin = st.session_state.get("career_view", "careers")
    st.button(
        f"← Back to {origin}",
        key="career_detail_back",
        on_click=_back_to_list,
    )

    # ---- header --------------------------------------------------
    title_col, side_col = st.columns([3, 1.4])

    with title_col:
        st.markdown(f"## {row['role_name']}")
        level_text = f"Role Level {int(row['level'])}"
        if int(row["formal_career_path"]) == 1:
            level_text += " • ★ Formal career path"
        st.caption(level_text)

    with side_col:
        st.markdown(
            '<div style="text-align:right;padding-bottom:8px;">'
            f"{_department_badge_html(row['department_name'])}</div>",
            unsafe_allow_html=True,
        )
        render_save_career_control(employee_id, role_id)

    if row["role_description"]:
        st.write(row["role_description"])

    # ---- data (only for this role) -------------------------------
    skill_details = get_target_role_skill_details(employee_id, role_id)

    if skill_details.empty:
        st.info("No skill requirements are currently defined for this role.")
        return

    learning = _load_learning(employee_id, role_id)
    learning_index = _build_skill_learning_index(learning)
    catalog = get_internal_training_outcomes()

    met, recorded_gaps, not_recorded = [], [], []

    for _, skill_row in skill_details.iterrows():
        state = _skill_state(skill_row)
        item = (skill_row, state)
        if state["status"] == "met":
            met.append(item)
        elif state["status"] == "gap":
            recorded_gaps.append(item)
        else:
            not_recorded.append(item)

    recorded_gaps.sort(
        key=lambda item: (
            -item[1]["importance"],
            -item[1]["gap"],
            item[0]["skill_name"],
        )
    )
    not_recorded.sort(
        key=lambda item: (
            -item[1]["importance"],
            -item[1]["required"],
            item[0]["skill_name"],
        )
    )

    # ---- summary -------------------------------------------------
    st.divider()

    metric_cols = st.columns(4)
    metric_cols[0].metric("Skill Match", f"{row['match_percent']:.1f}%")
    metric_cols[1].metric("Meets requirement", len(met))
    metric_cols[2].metric("Gaps (recorded)", len(recorded_gaps))
    metric_cols[3].metric("Not recorded", len(not_recorded))

    if not_recorded:
        st.caption(
            f"Skill Match counts the {len(not_recorded)} 'Not recorded' "
            f"{pluralize(len(not_recorded), 'skill')} as 0, so it may "
            "understate your fit."
        )

    gap_items = recorded_gaps + not_recorded
    if gap_items:
        covered = sum(
            1
            for skill_row, state in gap_items
            if learning_index.get(int(skill_row["skill_id"]))
        )
        st.caption(
            f"Recommended courses: {len(learning['ready'])} ready now, "
            f"{len(learning['locked'])} need a prerequisite first • "
            f"{covered} of {len(gap_items)} skill "
            f"{pluralize(len(gap_items), 'gap')} have a recommended course."
        )

    # ---- skills with their learning options ----------------------
    st.divider()
    st.markdown("### Skills & learning options")
    st.caption(
        "Bar = your current level, dark marker = required level. "
        "Courses are listed under the skill they help with."
    )

    if not gap_items:
        st.success(
            "Your recorded skills currently meet every requirement "
            "for this role."
        )

    _render_skill_group(
        "Recorded gaps",
        "Skills in your profile that are below the required level.",
        recorded_gaps,
        learning_index,
        catalog,
    )

    _render_skill_group(
        "Not recorded yet",
        "These skills are not in your WorkforceIQ profile yet. If you "
        "already have them, they may only need to be added; the courses "
        "below are optional paths if you do not.",
        not_recorded,
        learning_index,
        catalog,
    )

    if met:
        with st.expander(f"Skills that already meet the requirement ({len(met)})"):
            for skill_row, state in met:
                st.markdown(
                    f"✓ **{skill_row['skill_name']}** — "
                    f"L{state['current']} {LEVEL_LABELS[state['current']]} "
                    f"(needs L{state['required']})"
                )


# =========================================================
# List views (compact cards)
# =========================================================

def render_career_card(row, source: str, position: int):
    role_id = int(row["role_id"])
    employee_id = st.session_state["employee_id"]
    button_key = f"open_role_{source}_{role_id}"

    with st.container(border=True):
        title_col, match_col, met_col, develop_col, action_col = st.columns(
            [3.4, 1.2, 1, 1, 1.3]
        )

        with title_col:
            st.markdown(f"#### {row['role_name']}")
            badges = _department_badge_html(row["department_name"])
            if int(row["formal_career_path"]) == 1:
                badges += " &nbsp;<strong>★ Formal career path</strong>"
            st.markdown(badges, unsafe_allow_html=True)
            st.caption(f"Role Level {int(row['level'])}")

        match_col.metric("Skill Match", f"{row['match_percent']:.1f}%")
        met_col.metric("Skills met", int(row["skills_met"]))
        develop_col.metric("To develop", int(row["skills_to_develop"]))

        with action_col:
            st.button(
                "View details",
                key=button_key,
                on_click=_open_detail,
                args=(role_id, employee_id, button_key, position),
                **STRETCH,
            )


def render_recommended_careers(matches: pd.DataFrame):
    st.subheader("Recommended Careers")
    st.caption(
        "Company-recognized career paths, ordered by your "
        "current skill match."
    )

    with st.expander("What is a Formal Career Path?"):
        st.write(
            "Formal career paths are company-defined, recognized "
            "internal career moves. They are guidance, not restrictions. "
            "You can still explore any other role in the organization."
        )

    recommended = matches[matches["formal_career_path"] == 1].sort_values(
        "match_percent",
        ascending=False,
    )

    if recommended.empty:
        st.info("No formal career paths are currently defined for this role.")
        return

    for position, (_, row) in enumerate(recommended.iterrows()):
        render_career_card(row, source="recommended", position=position)


def render_all_careers(matches: pd.DataFrame, current_role: str):
    st.subheader("Explore All Careers")
    st.caption(
        "Explore any role in the organization. "
        "Skill match is provided as guidance, not as a restriction."
    )
    st.info(
        f"Current role: {current_role}. "
        "Your current role is excluded from career exploration."
    )

    filtered = matches.copy()

    search_term = st.text_input(
        "Search by role name",
        placeholder="e.g. Analyst, Product, Security",
        key="career_search",
    ).strip()

    if search_term:
        filtered = filtered[
            filtered["role_name"].str.contains(
                search_term,
                case=False,
                na=False,
                regex=False,
            )
        ]

    department_options = sorted(
        matches["department_name"].dropna().unique().tolist()
    )
    level_options = sorted(
        matches["level"].dropna().astype(int).unique().tolist()
    )

    # First visit: everything selected. Later: drop values that no longer exist.
    if "selected_departments" not in st.session_state:
        st.session_state["selected_departments"] = department_options
    else:
        st.session_state["selected_departments"] = [
            value
            for value in st.session_state["selected_departments"]
            if value in department_options
        ]

    if "selected_levels" not in st.session_state:
        st.session_state["selected_levels"] = level_options
    else:
        st.session_state["selected_levels"] = [
            value
            for value in st.session_state["selected_levels"]
            if value in level_options
        ]

    st.markdown("**Department**")
    dept_all_col, dept_clear_col = st.columns(2)
    with dept_all_col:
        if st.button("Select All Departments", key="select_all_departments"):
            st.session_state["selected_departments"] = department_options
    with dept_clear_col:
        if st.button("Clear Departments", key="clear_departments"):
            st.session_state["selected_departments"] = []

    selected_departments = st.multiselect(
        "Department",
        options=department_options,
        key="selected_departments",
        label_visibility="collapsed",
    )

    st.markdown("**Role Level**")
    level_all_col, level_clear_col = st.columns(2)
    with level_all_col:
        if st.button("Select All Levels", key="select_all_levels"):
            st.session_state["selected_levels"] = level_options
    with level_clear_col:
        if st.button("Clear Levels", key="clear_levels"):
            st.session_state["selected_levels"] = []

    selected_levels = st.multiselect(
        "Role Level",
        options=level_options,
        key="selected_levels",
        label_visibility="collapsed",
    )

    filtered = filtered[filtered["department_name"].isin(selected_departments)]
    filtered = filtered[filtered["level"].astype(int).isin(selected_levels)]

    sort_by = st.selectbox(
        "Sort by",
        ["Skill Match", "Department", "Role Level"],
        key="career_sort",
    )

    if sort_by == "Skill Match":
        filtered = filtered.sort_values("match_percent", ascending=False)
    elif sort_by == "Department":
        filtered = filtered.sort_values(
            ["department_name", "level", "match_percent"],
            ascending=[True, True, False],
        )
    else:
        filtered = filtered.sort_values(
            ["level", "match_percent"],
            ascending=[True, False],
        )

    st.caption(
        f"Showing {len(filtered)} career options "
        f"out of {len(matches)} available roles."
    )

    if filtered.empty:
        st.info("No roles match the selected filters.")
        return

    for position, (_, row) in enumerate(filtered.iterrows()):
        render_career_card(row, source="all", position=position)


def render_saved_careers():
    employee_id = st.session_state["employee_id"]
    saved_careers = get_saved_careers(employee_id)

    st.subheader("Saved Careers")
    st.caption(
        "Career interests you have chosen to save. Saved careers are "
        "private by default. You can choose to share a saved interest "
        "with relevant opening managers."
    )

    if saved_careers.empty:
        st.info(
            "You have not saved any careers yet. "
            "Open a role and select Save Career to add it here."
        )
        return

    count = len(saved_careers)
    st.caption(f"{count} saved career{'' if count == 1 else 's'}.")

    for position, (_, row) in enumerate(saved_careers.iterrows()):
        role_id = int(row["role_id"])
        button_key = f"open_role_saved_{role_id}"

        with st.container(border=True):
            info_col, visibility_col, action_col = st.columns([3, 2.4, 1.3])

            with info_col:
                st.markdown(f"#### {row['role_name']}")
                st.markdown(
                    _department_badge_html(row["department_name"]),
                    unsafe_allow_html=True,
                )
                saved_date = row["created_at"] or "Not available"
                st.caption(
                    f"Role Level {int(row['level'])} • Saved {saved_date}"
                )

            with visibility_col:
                st.caption("Visibility")
                render_career_visibility_control(
                    employee_id,
                    role_id,
                    row["visibility_level"],
                )

            with action_col:
                st.button(
                    "View details",
                    key=button_key,
                    on_click=_open_detail,
                    args=(role_id, employee_id, button_key, position),
                    **STRETCH,
                )
                if st.button(
                    "Unsave",
                    key=f"unsave_saved_career_{employee_id}_{role_id}",
                    **STRETCH,
                ):
                    deleted = delete_career_interest(employee_id, role_id)
                    clear_career_interest_session_state(employee_id, role_id)
                    _flash(
                        "Career removed from your saved interests."
                        if deleted
                        else "This career was no longer saved."
                    )
                    st.rerun()


# =========================================================
# Main view
# =========================================================

def render_career_exploration():
    _keep_list_widget_state()
    _show_flash()

    employee_id = st.session_state["employee_id"]

    profile = get_employee_profile(employee_id)
    if profile.empty:
        st.error("Employee profile not found.")
        return

    matches = get_recommended_careers(employee_id)

    # Drop a stale detail selection (employee switched / role not available).
    detail_role_id = st.session_state.get(DETAIL_ROLE_KEY)
    if detail_role_id is not None:
        still_valid = (
            st.session_state.get(DETAIL_EMPLOYEE_KEY) == employee_id
            and int(detail_role_id)
            in set(matches["role_id"].astype(int).tolist())
        )
        if not still_valid:
            _close_detail()
            detail_role_id = None

    if detail_role_id is not None:
        render_career_detail_page(int(detail_role_id), matches, employee_id)
        if st.session_state.pop(SCROLL_TOP_KEY, False):
            _scroll_to_top()
        return

    st.session_state.pop(SCROLL_TOP_KEY, None)

    current_role = profile.iloc[0]["current_role"]

    st.header("Career Exploration")
    st.write(
        "Explore career opportunities across the organization based on "
        "your currently recorded skills."
    )

    career_view = st.radio(
        "Career View",
        CAREER_VIEWS,
        horizontal=True,
        key="career_view",
        label_visibility="collapsed",
    )

    st.divider()

    if career_view == "Recommended Careers":
        render_recommended_careers(matches)
    elif career_view == "Explore All Careers":
        render_all_careers(matches, current_role)
    else:
        render_saved_careers()

    # Came back from a detail page: jump to the card that was opened.
    restore = st.session_state.pop(SCROLL_RESTORE_KEY, None)
    if restore:
        _scroll_to_card(restore)
