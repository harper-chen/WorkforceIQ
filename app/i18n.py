"""
English / Traditional Chinese (Taiwan) interface text.

English is always the default. Chinese is shown only when the URL has
?lang=zh (for example https://workforceiq-demo.streamlit.app/?lang=zh).
The choice is never stored anywhere else, so a link without ?lang=zh
always opens in English.

Interface text, rule labels, department names and skill categories are
translated here. Role, skill and course names and course descriptions are
translated in i18n_data.py; people's names and tool names (SQL, Power BI,
Jira ...) stay in English.
"""

import streamlit as st

LANGS = ("en", "zh")


# =========================================================
# Language selection
# =========================================================

def get_lang() -> str:
    try:
        value = st.query_params.get("lang", "en")
    except Exception:
        return "en"
    return "zh" if value == "zh" else "en"


def is_zh() -> bool:
    return get_lang() == "zh"


def render_language_switch():
    """Sidebar switch that keeps ?lang=zh in the URL in step with the UI."""
    lang = get_lang()
    choice = st.sidebar.radio(
        "Language / 語言",
        list(LANGS),
        index=LANGS.index(lang),
        format_func=lambda code: "English" if code == "en" else "繁體中文",
        horizontal=True,
        label_visibility="collapsed",
    )
    if choice != lang:
        if choice == "zh":
            st.query_params["lang"] = "zh"
        else:
            try:
                del st.query_params["lang"]
            except KeyError:
                pass
        st.rerun()


# =========================================================
# Lookup
# =========================================================

def t(key: str, **kwargs) -> str:
    """Interface text in the current language, with {placeholders} filled."""
    table = TEXT[get_lang()]
    text = table.get(key)
    if text is None:
        text = TEXT["en"][key]
    return text.format(**kwargs) if kwargs else text


def tn(key: str, count: int, **kwargs) -> str:
    """
    Text that depends on a count. English uses key_one / key_other;
    Chinese has no plural, so key_other is enough there.
    """
    lang = get_lang()
    suffix = "_one" if count == 1 else "_other"
    table = TEXT[lang]
    text = table.get(key + suffix) or table.get(key + "_other")
    if text is None:
        text = TEXT["en"][key + suffix]
    return text.format(count=count, **kwargs)


def level_label(level: int) -> str:
    return t(f"level_{int(level)}")


def department(name) -> str:
    if not is_zh():
        return name
    return DEPARTMENTS_ZH.get(name, name)


def skill_category(name) -> str:
    if not is_zh():
        return name
    return SKILL_CATEGORIES_ZH.get(name, name)


def readiness_text(result: dict) -> tuple[str, str]:
    """(label, explanation) for a readiness.get_candidate_internal_readiness result."""
    if not is_zh():
        return result["label"], result["explanation"]
    code = result["code"]
    variant = result.get("variant")
    label = t(f"ready_{code}")
    if variant == "unrecorded_could_change":
        explanation = t(
            "ready_expl_unrecorded_could_change",
            match=result["match_percent"],
            best=result["best_case_match_percent"],
        )
    else:
        explanation = t(f"ready_expl_{code}")
        if variant == "might_be_ready_now":
            explanation += t("ready_expl_might_be_ready_now")
    return label, explanation


def route_text(route: dict) -> tuple[str, str | None, str]:
    """(route label, readiness label or None, explanation) for a staffing route."""
    if not is_zh():
        return route["route_label"], route["readiness_label"], route["explanation"]
    readiness = route["readiness_label"]
    readiness_zh = None
    if readiness == "Ready Now":
        readiness_zh = t("ready_ready_now")
    elif readiness == "Train First":
        readiness_zh = t("ready_train_first")
    return (
        t(f"route_{route['route_code']}"),
        readiness_zh,
        t(f"route_expl_{route.get('variant') or route['route_code']}"),
    )


# =========================================================
# Demo data that is translated
# =========================================================

DEPARTMENTS_ZH = {
    "Business Operations": "營運管理部",
    "Human Resources": "人力資源部",
    "Information Technology": "資訊部",
    "Product & Engineering": "產品研發部",
}

SKILL_CATEGORIES_ZH = {
    "Data & Analytics": "資料分析",
    "Software & Development": "軟體開發",
    "Data & Database Engineering": "資料與資料庫工程",
    "Systems & Cloud": "系統與雲端",
    "Security": "資訊安全",
    "HR & People Development": "人資與人才發展",
    "Product & Business Operations": "產品與營運",
}


# =========================================================
# Interface text
# =========================================================

TEXT = {
    "en": {
        # ---- app shell ----
        "app_caption": "Skills Intelligence, Career Mobility & Strategic Workforce Planning",
        "synthetic_notice": (
            "**Synthetic demo data.** Every employee, role, skill, and number "
            "in this prototype is fictional and was generated for demonstration. "
            "Nothing here describes a real person or organization."
        ),
        "workspace": "Workspace",
        "ws_employee": "Employee",
        "ws_manager": "Manager",
        "ws_hr": "HR / Workforce Planning",
        "suggested_demo": "Suggested demo",
        "suggested_demo_body": (
            "Employee: River Hsu → Career Exploration → Systems Analyst<br>"
            "Manager: Riley Chang → Systems Analyst opening"
        ),
        "preview_as_employee": "Preview as employee",
        "employee_pages": "Employee",
        "page_my_skills": "My Skills",
        "page_career": "Career Exploration",
        "page_learning": "Learning Catalog",
        "no_managers": "No hiring managers are currently linked to job openings.",
        "manager_option_one": "{name} — {count} open requisition",
        "manager_option_other": "{name} — {count} open requisitions",
        "preview_as_manager": "Preview as manager",
        "demo_controls": "Demo controls",
        "demo_controls_body": (
            "You are working on your own private copy of the demo data, "
            "so changes you make are not shared with other visitors and "
            "are temporary. Reset restores the seeded career interests "
            "and visibility settings in your copy only."
        ),
        "reset_demo": "Reset demo data",
        "demo_restored": "Demo data restored.",
        "employee_not_found": "Employee profile not found.",

        # ---- shared skill text ----
        "level_1": "Foundational",
        "level_2": "Basic",
        "level_3": "Working",
        "level_4": "Advanced",
        "level_5": "Expert",
        "not_recorded": "Not recorded",
        "importance_badge": "Importance {level}/5",
        "needs_level": "{current} → needs **L{level} {label}**",
        "skill_match": "Skill Match",
        "role_level": "Role Level {level}",
        "formal_path": "★ Formal career path",
        "no_role_requirements": "No skill requirements are currently defined for this role.",

        # ---- my skills ----
        "my_skills_intro": (
            "Review the skills currently recorded in your WorkforceIQ profile "
            "and the proficiency level associated with each one."
        ),
        "current_role": "Current role",
        "department": "Department",
        "recorded_skills": "Recorded skills",
        "no_skills": "No skills are currently recorded for this employee.",
        "filter_category": "Filter by skill category",
        "search_skills": "Search skills",
        "search_skills_ph": "e.g. SQL, Power BI, Workday",
        "showing_skills": "Showing {shown} of {total} recorded skills",
        "last_updated": "Last updated: {date}",

        # ---- career exploration: lists ----
        "career_intro": (
            "Explore career opportunities across the organization based on "
            "your currently recorded skills."
        ),
        "career_view": "Career View",
        "view_recommended": "Recommended Careers",
        "view_all": "Explore All Careers",
        "view_saved": "Saved Careers",
        "recommended_caption": "Company-recognized career paths, ordered by your current skill match.",
        "what_is_formal": "What is a Formal Career Path?",
        "what_is_formal_body": (
            "Formal career paths are company-defined, recognized "
            "internal career moves. They are guidance, not restrictions. "
            "You can still explore any other role in the organization."
        ),
        "no_formal_paths": "No formal career paths are currently defined for this role.",
        "all_caption": (
            "Explore any role in the organization. "
            "Skill match is provided as guidance, not as a restriction."
        ),
        "current_role_excluded": (
            "Current role: {role}. "
            "Your current role is excluded from career exploration."
        ),
        "search_role": "Search by role name",
        "search_role_ph": "e.g. Analyst, Product, Security",
        "select_all_depts": "Select All Departments",
        "clear_depts": "Clear Departments",
        "role_level_heading": "Role Level",
        "select_all_levels": "Select All Levels",
        "clear_levels": "Clear Levels",
        "sort_by": "Sort by",
        "sort_match": "Skill Match",
        "sort_department": "Department",
        "sort_level": "Role Level",
        "showing_careers": "Showing {shown} career options out of {total} available roles.",
        "no_roles_match": "No roles match the selected filters.",
        "skills_met": "Skills met",
        "to_develop": "To develop",
        "view_details": "View details",
        "saved_caption": (
            "Career interests you have chosen to save. Saved careers are "
            "private by default. You can choose to share a saved interest "
            "with relevant opening managers."
        ),
        "no_saved": (
            "You have not saved any careers yet. "
            "Open a role and select Save Career to add it here."
        ),
        "saved_count_one": "{count} saved career.",
        "saved_count_other": "{count} saved careers.",
        "not_available": "Not available",
        "level_saved": "Role Level {level} • Saved {date}",
        "visibility": "Visibility",
        "unsave": "Unsave",

        # ---- career exploration: save + visibility ----
        "save_career": "Save Career",
        "unsave_career": "Unsave Career",
        "career_removed": "Career removed from your saved interests.",
        "career_not_saved": "This career was no longer saved.",
        "saved_note": (
            "Saved to your career interests. "
            "Removing it also removes its sharing visibility."
        ),
        "saved_privately": "Career saved privately.",
        "save_failed": "This career could not be saved.",
        "vis_private": "Private",
        "vis_opening_managers": "Visible to opening managers",
        "vis_updated": "Visibility updated.",
        "vis_failed": "This saved career could not be updated.",
        "vis_private_note": "Only you can see this career interest.",
        "vis_managers_note": (
            "Managers responsible for openings for this exact "
            "role can see this career interest."
        ),

        # ---- career exploration: detail page ----
        "back_to": "← Back to {view}",
        "meets_requirement": "Meets requirement",
        "gaps_recorded": "Gaps (recorded)",
        "unrecorded_note_one": (
            "Skill Match counts the {count} 'Not recorded' skill as 0, "
            "so it may understate your fit."
        ),
        "unrecorded_note_other": (
            "Skill Match counts the {count} 'Not recorded' skills as 0, "
            "so it may understate your fit."
        ),
        "course_summary_one": (
            "Recommended courses: {ready} ready now, {locked} need a prerequisite "
            "first • {covered} of {count} skill gap have a recommended course."
        ),
        "course_summary_other": (
            "Recommended courses: {ready} ready now, {locked} need a prerequisite "
            "first • {covered} of {count} skill gaps have a recommended course."
        ),
        "skills_learning": "Skills & learning options",
        "skills_learning_caption": (
            "Bar = your current level, dark marker = required level. "
            "Courses are listed under the skill they help with."
        ),
        "all_met": "Your recorded skills currently meet every requirement for this role.",
        "group_gaps": "Recorded gaps",
        "group_gaps_caption": "Skills in your profile that are below the required level.",
        "group_unrecorded": "Not recorded yet",
        "group_unrecorded_caption": (
            "These skills are not in your WorkforceIQ profile yet. If you "
            "already have them, they may only need to be added; the courses "
            "below are optional paths if you do not."
        ),
        "met_expander": "Skills that already meet the requirement ({count})",
        "group_heading": "#### {title} ({count})",
        "met_line": "✓ **{skill}** — L{current} {label} (needs L{required})",
        "learning_options": "Learning options",
        "more_options_one": "+{count} more option in the Learning Catalog.",
        "more_options_other": "+{count} more options in the Learning Catalog.",
        "in_catalog_line": "ℹ️ In catalog — **{course}** · {weeks} wks · reaches L{level}",
        "not_top_reco": (
            "Not among your top recommendations. "
            "Check the Learning Catalog for prerequisites."
        ),
        "no_course_teaches": "No internal course currently teaches this skill.",
        "no_course_raises": "No internal course would raise this skill above your current level.",
        "learning_max": "Internal learning reaches at most L{best} for this skill; the role needs L{required}.",
        "tag_in_progress": "▶ In progress",
        "tag_ready": "✓ Ready now",
        "tag_locked": "🔒 Prerequisite needed",
        "fit_meets": "meets required level",
        "fit_partial": "partial: L{level} of L{required} needed",
        "option_line": "{tag} — **{course}** · {weeks} wks · reaches L{level} · {fit}",
        "also_develops": "This course also develops: {skills}",
        "list_sep": ", ",
        "skill_with_level": "{skill} (L{level})",
        "prereq_not_recorded": "not recorded",
        "prereq_before": "Before enrolling: **{skill}** {current} → L{minimum}.",
        "prereq_available": "available now",
        "prereq_needs_own": "needs its own prerequisite",
        "prereq_prepare": " Prepare with **{course}** ({weeks} wks, {availability}).",
        "prereq_none": " No internal course provides this prerequisite.",
        "prereq_confirm": (
            "Confirm before enrolling: **{skill}** is not recorded; "
            "this course expects L{minimum}."
        ),
        "gap_small": "Small gap",
        "gap_priority": "Priority gap",
        "gap_significant": "Significant gap",

        # ---- learning catalog ----
        "learning_intro": (
            "Browse the company's internal learning programs, "
            "the skills they develop, expected outcome levels, "
            "estimated duration, and formal prerequisites."
        ),
        "no_programs": "No internal learning programs are currently available.",
        "search_courses": "Search courses",
        "search_courses_ph": "Search by course name, skill, or description",
        "filter_skill": "Filter by skill",
        "all_skills": "All skills",
        "no_courses_match": "No courses match the current search and filter.",
        "courses_shown_one": "{count} course shown.",
        "courses_shown_other": "{count} courses shown.",
        "weeks_one": "{count} week",
        "weeks_other": "{count} weeks",
        "duration_unspecified": "Duration not specified",
        "not_specified": "Not specified",
        "skills_prefix": "Skills: ",
        "estimated_duration": "Estimated duration",
        "no_description": "No course description is available.",
        "skills_developed": "**Skills developed**",
        "col_skill": "Skill",
        "col_outcome_level": "Outcome Level",
        "prerequisites": "**Prerequisites**",
        "no_prereqs": "No formal prerequisites.",
        "col_prereq_skill": "Prerequisite Skill",
        "col_min_level": "Minimum Level",

        # ---- manager ----
        "manager_title": "Manager Staffing",
        "manager_intro": (
            "Review your current requisitions and identify employees who have "
            "explicitly shared interest in the exact role."
        ),
        "manager_info": (
            "WorkforceIQ supports staffing decisions; "
            "it does not automatically select, promote, or transfer employees."
        ),
        "no_requisitions": "No open or paused requisitions are currently assigned to this manager.",
        "open_reqs": "Open requisitions",
        "paused_reqs": "Paused requisitions",
        "status_open": "Open",
        "status_paused": "Paused",
        "select_req": "Select requisition",
        "opening_unavailable": "This opening is not available for the selected manager.",
        "opening_meta": "Role Level {level} • Opened {date} • Headcount {headcount}",
        "req_paused": (
            "This requisition is currently paused. "
            "Internal candidate search is disabled "
            "until the opening is active again."
        ),
        "visible_interest": "Visible Internal Interest",
        "visible_interest_caption": (
            "Only employees who explicitly make this career interest visible "
            "to relevant opening managers are shown here. "
            "Private interests are not visible to managers."
        ),
        "no_visible_interest": (
            "No employees have currently shared this exact career interest "
            "with the relevant opening manager."
        ),
        "visible_count_one": "{count} visible internal candidate, ordered by current skill match.",
        "visible_count_other": "{count} visible internal candidates, ordered by current skill match.",
        "profile_coverage": "Profile Coverage",
        "skills_to_develop": "Skills to develop",
        "no_record_one": "1 skill has no record",
        "no_record_other": "{count} skills have no record",
        "not_enough_data": (
            "Not enough data: {no_record}. A low Skill Match "
            "here does not mean the employee lacks these skills."
        ),
        "no_record_note_one": "{no_record}. Skill Match counts it as 0, but it is not treated as a gap.",
        "no_record_note_other": "{no_record}. Skill Match counts them as 0, but they are not treated as a gap.",
        "internal_readiness_line": "**Internal readiness: {label}**",
        "interest_shared_on": "Shared interest in this role on {date}.",
        "view_match_detail": "View Skill Match Detail",
        "sort_skills_by": "Sort skills by",
        "sort_importance": "Importance",
        "sort_gap": "Gap size",
        "sort_importance_caption": "Most important to the role first (darker blue = more important).",
        "sort_gap_caption": (
            "Largest gap first, then skills that meet the requirement, "
            "then skills with no record."
        ),
        "mgr_bar_caption": (
            " Bar = recorded level, dark marker = required level. "
            "'Not recorded' does not mean the employee has no ability in that skill."
        ),
        "decision_support": "Staffing Decision Support",
        "staffing_route": "Staffing Route",
        "internal_readiness": "Internal Readiness",
        "decision_caption": (
            "Staffing route: where to look first, inside or outside the company. "
            "Internal readiness: how ready the best internal candidate is. "
            "These are simple rules anyone can check, not a prediction model, "
            "and the manager makes the decision."
        ),
        "how_decided": "How this is decided",
        "how_decided_body": """
**1. Is there enough data?**
If fewer than {coverage}% of the role's skills are
recorded for an employee, the app does not judge them. Skills with no
record count as 0 in Skill Match, so if they alone could decide whether
someone qualifies, the app does not judge either.

**2. How ready is each employee?**
- **Ready Now:** Skill Match of {ready}% or more,
  and at most one skill is 2+ levels short (never one of the most
  important skills, importance 4–5).
- **Train First:** Skill Match of {train}% or
  more, and at most one of the most important skills is 2+ levels short.
- Otherwise: the gap is larger.

**3. Where to look first?**
- **Internal Mobility:** someone is Ready Now or Train First.
- **More Evidence Needed:** no one qualifies yet, but someone could not be
  judged. Record more skills before hiring from outside.
- **External Hire:** everyone was judged and no one qualifies, or no
  employee shared interest in this role.
""",

        # ---- HR ----
        "hr_title": "HR / Workforce Planning",
        "hr_intro": (
            "Plan future headcount, identify workforce gaps, "
            "and surface capability needs that current internal "
            "learning cannot fully support."
        ),
        "hr_info": (
            "This workspace focuses on aggregate workforce-planning "
            "needs rather than individual employee staffing decisions."
        ),
        "no_demand": "No future workforce-demand data is available.",
        "planning_period": "Planning Period",
        "no_demand_period": "No workforce-demand data is available for the selected planning period.",
        "demand_heading": "1. Workforce Demand & Gaps",
        "demand_caption": (
            "Planned HC is the future target headcount for each role. "
            "Edit it to test a different workforce scenario. "
            "Workforce Gap is recalculated from Planned HC minus Current HC."
        ),
        "reset_baseline": "Reset planned headcount to baseline",
        "show_no_gap": "Show roles with no gap",
        "no_positive_gaps": "No positive workforce gaps are currently identified under this scenario.",
        "col_role": "Role",
        "col_current_hc": "Current HC",
        "col_planned_hc": "Planned HC ✎",
        "col_planned_hc_help": "Editable future target headcount.",
        "col_workforce_gap": "Workforce Gap",
        "capability_heading": "2. Unaddressed Capability Gaps",
        "capability_caption": (
            "The skill requirements of every existing role are evaluated "
            "here, independent of the headcount scenario above. A skill "
            "appears only when the current internal learning catalog "
            "cannot reach the required proficiency level."
        ),
        "coverage_ok": (
            "Current internal learning coverage is sufficient "
            "for the skill requirements of all existing roles."
        ),
        "coverage_warning": (
            "These role capability needs are not fully supported "
            "by the current internal learning catalog."
        ),
        "col_affected_roles": "Affected Roles",
        "col_required_level": "Required Level",
        "col_available_training": "Available Internal Training",
        "no_internal_training": "No internal training available",
        "capability_note": (
            "Available Internal Training shows the strongest course "
            "outcome currently available for each skill. Multiple "
            "courses are shown when they reach the same highest "
            "outcome level. This section identifies planning risks "
            "rather than prescribing a single solution."
        ),
    },

    # =====================================================
    # 繁體中文（台灣）
    # =====================================================
    "zh": {
        # ---- app shell ----
        "app_caption": "技能盤點、內部職涯發展與策略性人力規劃",
        "synthetic_notice": (
            "**本系統使用模擬資料。** 所有員工、職位、技能與數字皆為示範用的虛構資料，"
            "不涉及任何真實的人或組織。"
        ),
        "workspace": "工作區",
        "ws_employee": "員工",
        "ws_manager": "用人主管",
        "ws_hr": "HR／人力規劃",
        "suggested_demo": "建議的操作路徑",
        "suggested_demo_body": (
            "員工：River Hsu → 職涯探索 → 系統分析師<br>"
            "用人主管：Riley Chang → 系統分析師職缺"
        ),
        "preview_as_employee": "切換員工身分",
        "employee_pages": "員工功能",
        "page_my_skills": "我的技能",
        "page_career": "職涯探索",
        "page_learning": "學習目錄",
        "no_managers": "目前沒有任何用人主管負責開放中的職缺。",
        "manager_option_other": "{name} — {count} 個開放職缺",
        "preview_as_manager": "切換主管身分",
        "demo_controls": "示範資料設定",
        "demo_controls_body": (
            "你操作的是專屬於你的示範資料副本，所做的變更不會影響其他訪客，"
            "也只會暫時保留。按下重設後，只會將你這份副本的職涯意向與公開設定還原成預設值。"
        ),
        "reset_demo": "重設示範資料",
        "demo_restored": "示範資料已還原。",
        "employee_not_found": "找不到這位員工的資料。",

        # ---- shared skill text ----
        "level_1": "入門",
        "level_2": "基礎",
        "level_3": "可獨立作業",
        "level_4": "進階",
        "level_5": "專家",
        "not_recorded": "未記錄",
        "importance_badge": "重要性 {level}/5",
        "needs_level": "{current} → 需要 **L{level} {label}**",
        "skill_match": "技能符合度",
        "role_level": "職級 {level}",
        "formal_path": "★ 正式職涯路徑",
        "no_role_requirements": "這個職位目前尚未設定技能要求。",

        # ---- my skills ----
        "my_skills_intro": "查看你在 WorkforceIQ 檔案中已記錄的技能，以及每項技能的熟練程度。",
        "current_role": "目前職位",
        "department": "部門",
        "recorded_skills": "已記錄技能",
        "no_skills": "這位員工目前沒有任何技能紀錄。",
        "filter_category": "依技能類別篩選",
        "search_skills": "搜尋技能",
        "search_skills_ph": "例如：SQL、Power BI、資料分析",
        "showing_skills": "顯示 {shown} 項技能（共 {total} 項）",
        "last_updated": "最後更新：{date}",

        # ---- career exploration: lists ----
        "career_intro": "根據你目前已記錄的技能，探索公司內部各部門的職涯機會。",
        "career_view": "檢視方式",
        "view_recommended": "推薦職位",
        "view_all": "瀏覽所有職位",
        "view_saved": "已收藏職位",
        "recommended_caption": "公司認可的職涯發展路徑，依你目前的技能符合度排序。",
        "what_is_formal": "什麼是正式職涯路徑？",
        "what_is_formal_body": (
            "正式職涯路徑是公司明確定義、認可的內部職涯發展方向。"
            "它是參考，不是限制，你仍然可以探索公司內的任何職位。"
        ),
        "no_formal_paths": "你目前的職位尚未設定正式職涯路徑。",
        "all_caption": "探索公司內的任何職位。技能符合度僅供參考，不會限制你的選擇。",
        "current_role_excluded": "你目前的職位是 {role}，因此不會出現在職涯探索中。",
        "search_role": "依職位名稱搜尋",
        "search_role_ph": "例如：分析師、產品、Security",
        "select_all_depts": "全選部門",
        "clear_depts": "清除部門",
        "role_level_heading": "職級",
        "select_all_levels": "全選職級",
        "clear_levels": "清除職級",
        "sort_by": "排序方式",
        "sort_match": "技能符合度",
        "sort_department": "部門",
        "sort_level": "職級",
        "showing_careers": "顯示 {shown} 個職位（共 {total} 個）。",
        "no_roles_match": "沒有符合篩選條件的職位。",
        "skills_met": "已達標技能",
        "to_develop": "待加強",
        "view_details": "查看詳情",
        "saved_caption": (
            "你收藏的職涯意向預設不公開。"
            "你可以自行決定是否讓該職缺的用人主管看到。"
        ),
        "no_saved": "你還沒有收藏任何職位。打開職位詳情並按下「收藏職位」，就會出現在這裡。",
        "saved_count_other": "已收藏 {count} 個職位。",
        "not_available": "無資料",
        "level_saved": "職級 {level} • 收藏於 {date}",
        "visibility": "公開設定",
        "unsave": "取消收藏",

        # ---- career exploration: save + visibility ----
        "save_career": "收藏職位",
        "unsave_career": "取消收藏",
        "career_removed": "已從你的職涯意向中移除。",
        "career_not_saved": "這個職位原本就不在收藏中。",
        "saved_note": "已加入你的職涯意向。取消收藏時，公開設定也會一併移除。",
        "saved_privately": "已收藏，預設為不公開。",
        "save_failed": "無法收藏這個職位。",
        "vis_private": "不公開",
        "vis_opening_managers": "開放給該職缺主管查看",
        "vis_updated": "公開設定已更新。",
        "vis_failed": "無法更新這個職位的設定。",
        "vis_private_note": "只有你自己看得到這個職涯意向。",
        "vis_managers_note": "負責這個職位職缺的用人主管可以看到你的意向。",

        # ---- career exploration: detail page ----
        "back_to": "← 回到{view}",
        "meets_requirement": "已達標",
        "gaps_recorded": "已記錄的落差",
        "unrecorded_note_other": (
            "有 {count} 項技能「未記錄」，在技能符合度中以 0 計算，"
            "所以分數可能低估了你的適配程度。"
        ),
        "course_summary_other": (
            "推薦課程：{ready} 門可直接報名，{locked} 門需先完成先修條件 • "
            "{count} 項技能落差中，有 {covered} 項有推薦課程。"
        ),
        "skills_learning": "技能與學習資源",
        "skills_learning_caption": "長條代表你目前的等級，深色標記代表職位要求的等級。課程會列在它能幫助提升的技能下方。",
        "all_met": "你已記錄的技能目前符合這個職位的所有要求。",
        "group_gaps": "已記錄的技能落差",
        "group_gaps_caption": "你檔案中已有紀錄、但尚未達到職位要求等級的技能。",
        "group_unrecorded": "尚未記錄的技能",
        "group_unrecorded_caption": (
            "這些技能還沒有出現在你的 WorkforceIQ 檔案中。如果你其實已經具備，"
            "可能只需要補上紀錄；如果還沒有，下方課程可以作為學習方向參考。"
        ),
        "met_expander": "已達到要求的技能（{count}）",
        "group_heading": "#### {title}（{count}）",
        "met_line": "✓ **{skill}** — L{current} {label}（要求 L{required}）",
        "learning_options": "學習資源",
        "more_options_other": "學習目錄中還有 {count} 個選項。",
        "in_catalog_line": "ℹ️ 目錄中的課程 — **{course}** · {weeks} 週 · 可達 L{level}",
        "not_top_reco": "這門課不在你的優先推薦中，請到學習目錄查看先修條件。",
        "no_course_teaches": "目前沒有內部課程教授這項技能。",
        "no_course_raises": "目前沒有內部課程能讓這項技能超過你現在的等級。",
        "learning_max": "內部課程最高只能將這項技能提升到 L{best}，但職位要求 L{required}。",
        "tag_in_progress": "▶ 進行中",
        "tag_ready": "✓ 可直接報名",
        "tag_locked": "🔒 需先完成先修條件",
        "fit_meets": "達到要求等級",
        "fit_partial": "部分補足（要求 L{required}）",
        "option_line": "{tag} — **{course}** · {weeks} 週 · 可達 L{level} · {fit}",
        "also_develops": "這門課也能培養：{skills}",
        "list_sep": "、",
        "skill_with_level": "{skill}（L{level}）",
        "prereq_not_recorded": "未記錄",
        "prereq_before": "報名前需具備：**{skill}** {current} → L{minimum}。",
        "prereq_available": "可直接報名",
        "prereq_needs_own": "本身也有先修條件",
        "prereq_prepare": "可先修 **{course}**（{weeks} 週，{availability}）。",
        "prereq_none": "目前沒有內部課程能補足這項先修條件。",
        "prereq_confirm": "報名前請先確認：**{skill}** 尚未記錄，這門課預期你已達 L{minimum}。",
        "gap_small": "小幅落差",
        "gap_priority": "優先補強",
        "gap_significant": "明顯落差",

        # ---- learning catalog ----
        "learning_intro": "瀏覽公司的內部培訓課程，查看每門課能培養的技能、預期達到的等級、所需時間與先修條件。",
        "no_programs": "目前沒有可用的內部培訓課程。",
        "search_courses": "搜尋課程",
        "search_courses_ph": "可用中文或英文搜尋課程名稱、技能或說明",
        "filter_skill": "依技能篩選",
        "all_skills": "所有技能",
        "no_courses_match": "沒有符合搜尋與篩選條件的課程。",
        "courses_shown_other": "共 {count} 門課程。",
        "weeks_other": "{count} 週",
        "duration_unspecified": "未標示時長",
        "not_specified": "未標示",
        "skills_prefix": "培養技能：",
        "estimated_duration": "預估時長",
        "no_description": "這門課目前沒有說明。",
        "skills_developed": "**可培養的技能**",
        "col_skill": "技能",
        "col_outcome_level": "結業等級",
        "prerequisites": "**先修條件**",
        "no_prereqs": "沒有正式的先修條件。",
        "col_prereq_skill": "先修技能",
        "col_min_level": "最低等級",

        # ---- manager ----
        "manager_title": "用人主管：職缺人選評估",
        "manager_intro": "查看你目前負責的職缺，以及主動對該職位表達意願的內部員工。",
        "manager_info": "WorkforceIQ 只提供人選評估的參考，不會自動挑選、晉升或調動任何員工。",
        "no_requisitions": "目前沒有分配給這位主管的開放中或暫停中職缺。",
        "open_reqs": "開放中職缺",
        "paused_reqs": "暫停中職缺",
        "status_open": "開放中",
        "status_paused": "暫停中",
        "select_req": "選擇職缺",
        "opening_unavailable": "這位主管無法查看這個職缺。",
        "opening_meta": "職級 {level} • 開缺日期 {date} • 需求人數 {headcount}",
        "req_paused": "這個職缺目前暫停中，在重新開放之前無法搜尋內部人選。",
        "visible_interest": "已公開意向的內部員工",
        "visible_interest_caption": (
            "這裡只會顯示主動將職涯意向開放給該職缺主管查看的員工，"
            "設為不公開的意向主管看不到。"
        ),
        "no_visible_interest": "目前沒有員工將這個職位的意向開放給你查看。",
        "visible_count_other": "共 {count} 位內部人選，依目前技能符合度排序。",
        "profile_coverage": "技能紀錄完整度",
        "skills_to_develop": "待加強技能",
        "no_record_other": "有 {count} 項技能沒有紀錄",
        "not_enough_data": "資料不足：{no_record}。這裡技能符合度偏低，不代表這位員工缺乏這些技能。",
        "no_record_note_other": "{no_record}。這些技能在技能符合度中以 0 計算，但不會被當成技能落差。",
        "internal_readiness_line": "**內部人選準備度：{label}**",
        "interest_shared_on": "於 {date} 公開對這個職位的意向。",
        "view_match_detail": "查看技能符合度明細",
        "sort_skills_by": "技能排序方式",
        "sort_importance": "重要性",
        "sort_gap": "落差大小",
        "sort_importance_caption": "對職位最重要的技能排在前面（藍色越深代表越重要）。",
        "sort_gap_caption": "落差最大的排在前面，接著是已達標的技能，最後是沒有紀錄的技能。",
        "mgr_bar_caption": "長條代表已記錄的等級，深色標記代表要求等級。「未記錄」不代表員工不具備這項能力。",
        "decision_support": "人選決策參考",
        "staffing_route": "建議招募方向",
        "internal_readiness": "內部人選準備度",
        "decision_caption": (
            "建議招募方向：優先從公司內部還是外部找人。"
            "內部人選準備度：最適合的內部人選目前準備得如何。"
            "這些都是任何人都能檢查的簡單規則，不是預測模型，最後由主管做決定。"
        ),
        "how_decided": "判斷規則說明",
        "how_decided_body": """
**1. 資料夠不夠？**
如果一位員工在這個職位要求的技能中，有紀錄的不到 {coverage}%，系統就不會評估他。
沒有紀錄的技能在技能符合度中以 0 計算，所以如果光是這些缺漏就可能改變結果，系統也不會評估。

**2. 每位員工準備得如何？**
- **可立即到任：** 技能符合度達 {ready}% 以上，且最多只有一項技能差 2 級以上（而且不能是重要性 4–5 的關鍵技能）。
- **先培訓再調任：** 技能符合度達 {train}% 以上，且關鍵技能中最多只有一項差 2 級以上。
- 其他情況：落差較大。

**3. 應該優先往哪裡找人？**
- **內部調動：** 有人屬於「可立即到任」或「先培訓再調任」。
- **需補充技能紀錄：** 目前沒有人符合，但有人因資料不足而無法評估。建議先補齊技能紀錄，再考慮對外招募。
- **外部招募：** 所有人都評估過且沒有人符合，或沒有員工對這個職位公開意向。
""",

        # ---- readiness + route ----
        "ready_ready_now": "可立即到任",
        "ready_train_first": "先培訓再調任",
        "ready_larger_gap": "落差較大",
        "ready_not_assessed": "暫不評估",
        "ready_expl_ready_now": "已接近職位需求：最多只有一項技能差 2 級以上，而且不是最關鍵的技能。",
        "ready_expl_train_first": "整體適配度不錯，但調任前有些技能需要先培訓。",
        "ready_expl_larger_gap": "已記錄的技能與職位需求仍有不小的差距。",
        "ready_expl_not_assessed": "暫不評估：這個職位的技能中，有紀錄的太少。",
        "ready_expl_unrecorded_could_change": (
            "暫不評估：沒有紀錄的技能可能會改變結果。目前技能符合度為 {match:.1f}%，"
            "補齊紀錄後最高可能達到 {best:.1f}%。"
        ),
        "ready_expl_might_be_ready_now": "補齊缺漏的技能紀錄後，這位員工有可能達到「可立即到任」。",
        "route_internal_mobility": "內部調動",
        "route_more_evidence_needed": "需補充技能紀錄",
        "route_external_hire": "外部招募",
        "route_expl_no_interest": "目前還沒有員工向你公開對這個職位的意向。",
        "route_expl_ready_now": "至少有一位公開意向的員工已經可以立即到任。",
        "route_expl_train_first": "至少有一位公開意向的員工在完成部分培訓後可以調任。",
        "route_expl_more_evidence_needed": (
            "在對外招募之前，建議先為公開意向的員工補齊技能紀錄，"
            "目前缺少的資料可能會改變評估結果。"
        ),
        "route_expl_none_close": "公開意向的員工都已評估過，但目前還沒有人足夠接近這個職位的需求。",

        # ---- HR ----
        "hr_title": "HR／人力規劃",
        "hr_intro": "規劃未來的人力需求、找出人力缺口，並標出現有內部培訓無法完全支援的能力需求。",
        "hr_info": "這個工作區著重在整體的人力規劃需求，而不是個別員工的人事決定。",
        "no_demand": "目前沒有未來人力需求資料。",
        "planning_period": "規劃期間",
        "no_demand_period": "所選規劃期間沒有人力需求資料。",
        "demand_heading": "1. 人力需求與缺口",
        "demand_caption": (
            "「規劃人數」是各職位未來的目標人數，可以直接修改來模擬不同情境。"
            "「人力缺口」會以規劃人數減去現有人數重新計算。"
        ),
        "reset_baseline": "將規劃人數還原為基準值",
        "show_no_gap": "顯示沒有缺口的職位",
        "no_positive_gaps": "在目前的情境下，沒有任何職位出現人力缺口。",
        "col_role": "職位",
        "col_current_hc": "現有人數",
        "col_planned_hc": "規劃人數 ✎",
        "col_planned_hc_help": "可編輯的未來目標人數。",
        "col_workforce_gap": "人力缺口",
        "capability_heading": "2. 內部培訓無法補足的能力缺口",
        "capability_caption": (
            "這裡會檢查所有現有職位的技能要求，與上方的人數情境無關。"
            "只有當目前的內部課程無法培養到職位要求的等級時，該技能才會出現在這裡。"
        ),
        "coverage_ok": "目前的內部培訓足以支援所有現有職位的技能要求。",
        "coverage_warning": "以下職位的能力需求，目前的內部培訓課程無法完全支援。",
        "col_affected_roles": "受影響職位",
        "col_required_level": "要求等級",
        "col_available_training": "現有內部培訓",
        "no_internal_training": "目前沒有相關內部培訓",
        "capability_note": (
            "「現有內部培訓」列出每項技能目前能達到最高等級的課程；"
            "若有多門課程達到相同的最高等級，會一併列出。"
            "這個區塊的目的是找出規劃上的風險，而不是提供單一解法。"
        ),
    },
}
