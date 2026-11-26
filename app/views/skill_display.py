"""
Small display pieces shared by the employee and manager skill cards,
so both views show a skill the same way.
"""

# Importance: one blue scale with a clearly different shade per level,
# darker = more important to the role.
IMPORTANCE_BADGES = {
    5: ("#172554", "#FFFFFF"),
    4: ("#1D4ED8", "#FFFFFF"),
    3: ("#60A5FA", "#0B1F4D"),
    2: ("#BFDBFE", "#1E3A8A"),
    1: ("#F1F5F9", "#475569"),
}

from i18n import t

# Gray: missing evidence, not a gap.
NOT_RECORDED_BADGE_COLORS = ("#F3F4F6", "#4B5563")


def badge_html(text: str, background: str, color: str) -> str:
    return (
        f'<span style="display:inline-block;padding:2px 10px;'
        f"border-radius:999px;font-size:0.8rem;font-weight:600;"
        f'background:{background};color:{color};white-space:nowrap;">'
        f"{text}</span>"
    )


def importance_badge_html(importance: int) -> str:
    background, color = IMPORTANCE_BADGES.get(
        importance, IMPORTANCE_BADGES[1]
    )
    return badge_html(t("importance_badge", level=importance), background, color)


def skill_badges_html(importance: int, not_recorded: bool) -> str:
    """Right-aligned badges: 'Not recorded' (if so), then importance."""
    badges = []
    if not_recorded:
        badges.append(badge_html(t("not_recorded"), *NOT_RECORDED_BADGE_COLORS))
    badges.append(importance_badge_html(importance))
    return (
        '<div style="text-align:right;">'
        + "&nbsp;".join(badges)
        + "</div>"
    )


def level_bar_html(current_level, required_level: int) -> str:
    """
    Filled bar = current level, dark marker = required level.
    A skill that is not recorded shows an empty bar.
    """
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
