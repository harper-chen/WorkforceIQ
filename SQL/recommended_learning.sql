-- WorkforceIQ: Recommended Learning v3 (FINAL)
-- Adds course-to-role alignment and prerequisite-unlocking relationships.
-- Change only employee_id and target role name in params when testing.

WITH params AS (
    SELECT
        78 AS employee_id,
        (SELECT role_id FROM roles WHERE role_name = 'BI Analyst') AS target_role_id
),

target_skills AS (
    SELECT
        rs.skill_id,
        s.skill_name,
        s.skill_category,
        rs.required_level,
        rs.importance_level,
        es.proficiency_level AS employee_level_recorded,
        COALESCE(es.proficiency_level, 0) AS employee_level_numeric
    FROM params p
    JOIN role_skills rs ON rs.role_id = p.target_role_id
    JOIN skills s ON s.skill_id = rs.skill_id
    LEFT JOIN employee_skills es
      ON es.employee_id = p.employee_id
     AND es.skill_id = rs.skill_id
),

target_gaps AS (
    SELECT *, required_level - employee_level_numeric AS gap
    FROM target_skills
    WHERE employee_level_numeric < required_level
),

course_alignment AS (
    SELECT
        tp.training_id,
        tp.training_name,
        tp.training_category,
        tp.estimated_weeks,
        COUNT(DISTINCT ts.skill_id) AS total_course_skills,
        COUNT(DISTINCT CASE WHEN trs.skill_id IS NOT NULL THEN ts.skill_id END) AS target_role_skill_overlap,
        1.0 * COUNT(DISTINCT CASE WHEN trs.skill_id IS NOT NULL THEN ts.skill_id END)
            / COUNT(DISTINCT ts.skill_id) AS course_role_alignment
    FROM training_programs tp
    JOIN training_skills ts ON ts.training_id = tp.training_id
    LEFT JOIN target_skills trs ON trs.skill_id = ts.skill_id
    GROUP BY tp.training_id, tp.training_name, tp.training_category, tp.estimated_weeks
),

direct_skill_impact AS (
    SELECT
        ca.training_id,
        ca.training_name,
        ca.training_category,
        ca.estimated_weeks,
        ca.total_course_skills,
        ca.target_role_skill_overlap,
        ca.course_role_alignment,
        g.skill_id,
        g.skill_name,
        g.employee_level_recorded,
        g.employee_level_numeric,
        g.required_level,
        g.importance_level,
        g.gap,
        ts.course_skill_level,
        CASE WHEN ts.course_skill_level >= g.required_level THEN 1 ELSE 0 END AS fully_closes_gap,
        1.0 * (MIN(ts.course_skill_level, g.required_level) - g.employee_level_numeric) / g.gap AS gap_closure_fraction
    FROM course_alignment ca
    JOIN training_skills ts ON ts.training_id = ca.training_id
    JOIN target_gaps g ON g.skill_id = ts.skill_id
    WHERE ts.course_skill_level > g.employee_level_numeric
),

direct_course_impact AS (
    SELECT
        training_id,
        training_name,
        training_category,
        estimated_weeks,
        total_course_skills,
        target_role_skill_overlap,
        course_role_alignment,
        COUNT(*) AS relevant_gap_skills,
        SUM(fully_closes_gap) AS gaps_fully_closed,
        SUM(importance_level * gap_closure_fraction) AS weighted_gap_improvement,
        MAX(importance_level) AS highest_gap_importance,
        GROUP_CONCAT(
            skill_name || ' (' ||
            CASE WHEN employee_level_recorded IS NULL THEN 'Not recorded'
                 ELSE CAST(employee_level_recorded AS TEXT) END ||
            ' -> ' || CAST(course_skill_level AS TEXT) ||
            ', target ' || CAST(required_level AS TEXT) || ')',
            '; '
        ) AS skills_helped
    FROM direct_skill_impact
    GROUP BY training_id, training_name, training_category, estimated_weeks,
             total_course_skills, target_role_skill_overlap, course_role_alignment
),

direct_prereq_check AS (
    SELECT
        dci.training_id,
        COUNT(tpr.skill_id) AS prerequisite_count,
        SUM(CASE WHEN COALESCE(es.proficiency_level, 0) < tpr.minimum_level THEN 1 ELSE 0 END) AS unmet_prerequisite_count
    FROM direct_course_impact dci
    LEFT JOIN training_prerequisites tpr ON tpr.training_id = dci.training_id
    CROSS JOIN params p
    LEFT JOIN employee_skills es
      ON es.employee_id = p.employee_id
     AND es.skill_id = tpr.skill_id
    GROUP BY dci.training_id
),

direct_recommendations AS (
    SELECT dci.*, dpc.prerequisite_count, dpc.unmet_prerequisite_count
    FROM direct_course_impact dci
    JOIN direct_prereq_check dpc ON dpc.training_id = dci.training_id
    WHERE
        (dci.course_role_alignment >= 0.50 AND dci.relevant_gap_skills >= 1)
        OR dci.relevant_gap_skills >= 2
),

unmet_direct_prereqs AS (
    SELECT
        dr.training_id AS locked_course_id,
        dr.training_name AS locked_course_name,
        tpr.skill_id AS prerequisite_skill_id,
        s.skill_name AS prerequisite_skill_name,
        tpr.minimum_level,
        es.proficiency_level AS current_level_recorded,
        COALESCE(es.proficiency_level, 0) AS current_level_numeric
    FROM direct_recommendations dr
    JOIN training_prerequisites tpr ON tpr.training_id = dr.training_id
    JOIN skills s ON s.skill_id = tpr.skill_id
    CROSS JOIN params p
    LEFT JOIN employee_skills es
      ON es.employee_id = p.employee_id
     AND es.skill_id = tpr.skill_id
    WHERE COALESCE(es.proficiency_level, 0) < tpr.minimum_level
),

unlocking_courses_raw AS (
    SELECT DISTINCT
        prereq_course.training_id,
        prereq_course.training_name,
        prereq_course.training_category,
        prereq_course.estimated_weeks,
        udp.locked_course_id,
        udp.locked_course_name,
        udp.prerequisite_skill_id,
        udp.prerequisite_skill_name,
        udp.minimum_level,
        pts.course_skill_level,
        ca.total_course_skills,
        ca.target_role_skill_overlap,
        ca.course_role_alignment
    FROM unmet_direct_prereqs udp
    JOIN training_skills pts
      ON pts.skill_id = udp.prerequisite_skill_id
     AND pts.course_skill_level >= udp.minimum_level
    JOIN training_programs prereq_course
      ON prereq_course.training_id = pts.training_id
    JOIN course_alignment ca
      ON ca.training_id = prereq_course.training_id
    WHERE prereq_course.training_id <> udp.locked_course_id
),

unlocking_course_prereq_check AS (
    SELECT
        u.training_id,
        SUM(CASE WHEN COALESCE(es.proficiency_level, 0) < tpr.minimum_level THEN 1 ELSE 0 END) AS unmet_prerequisite_count
    FROM (SELECT DISTINCT training_id FROM unlocking_courses_raw) u
    LEFT JOIN training_prerequisites tpr ON tpr.training_id = u.training_id
    CROSS JOIN params p
    LEFT JOIN employee_skills es
      ON es.employee_id = p.employee_id
     AND es.skill_id = tpr.skill_id
    GROUP BY u.training_id
),

unlocking_courses AS (
    SELECT
        ucr.training_id,
        ucr.training_name,
        ucr.training_category,
        ucr.estimated_weeks,
        ucr.total_course_skills,
        ucr.target_role_skill_overlap,
        ucr.course_role_alignment,
        COUNT(DISTINCT ucr.locked_course_id) AS courses_unlocked,
        GROUP_CONCAT(DISTINCT ucr.locked_course_name || ' via ' || ucr.prerequisite_skill_name || ' Level ' || ucr.minimum_level) AS unlocks,
        ucpc.unmet_prerequisite_count
    FROM unlocking_courses_raw ucr
    JOIN unlocking_course_prereq_check ucpc ON ucpc.training_id = ucr.training_id
    GROUP BY ucr.training_id, ucr.training_name, ucr.training_category, ucr.estimated_weeks,
             ucr.total_course_skills, ucr.target_role_skill_overlap, ucr.course_role_alignment,
             ucpc.unmet_prerequisite_count
),

direct_output AS (
    SELECT
        dr.training_id,
        dr.training_name,
        dr.training_category,
        dr.estimated_weeks,
        CASE WHEN dr.unmet_prerequisite_count = 0 THEN 'Start here' ELSE 'Next step' END AS learning_stage,
        ROUND(dr.course_role_alignment * 100, 1) AS course_role_alignment_percent,
        dr.relevant_gap_skills,
        dr.gaps_fully_closed,
        ROUND(dr.weighted_gap_improvement, 2) AS weighted_gap_improvement,
        dr.skills_helped,
        COALESCE((
            SELECT GROUP_CONCAT(
                s.skill_name || ' requires Level ' || tpr.minimum_level ||
                ' (current ' || COALESCE(CAST(es.proficiency_level AS TEXT), 'Not recorded') || ')',
                '; '
            )
            FROM training_prerequisites tpr
            JOIN skills s ON s.skill_id = tpr.skill_id
            CROSS JOIN params p
            LEFT JOIN employee_skills es
              ON es.employee_id = p.employee_id
             AND es.skill_id = tpr.skill_id
            WHERE tpr.training_id = dr.training_id
              AND COALESCE(es.proficiency_level, 0) < tpr.minimum_level
        ), '') AS unmet_prerequisites,
        '' AS unlocks_courses
    FROM direct_recommendations dr
),

unlocking_output AS (
    SELECT
        uc.training_id,
        uc.training_name,
        uc.training_category,
        uc.estimated_weeks,
        'Prerequisite pathway' AS learning_stage,
        ROUND(uc.course_role_alignment * 100, 1) AS course_role_alignment_percent,
        0 AS relevant_gap_skills,
        0 AS gaps_fully_closed,
        0.0 AS weighted_gap_improvement,
        '' AS skills_helped,
        CASE WHEN uc.unmet_prerequisite_count = 0 THEN ''
             ELSE 'This prerequisite course also has unmet prerequisites' END AS unmet_prerequisites,
        uc.unlocks AS unlocks_courses
    FROM unlocking_courses uc
    WHERE uc.training_id NOT IN (SELECT training_id FROM direct_recommendations)
)

SELECT *
FROM (
    SELECT * FROM direct_output
    UNION ALL
    SELECT * FROM unlocking_output
)
ORDER BY
    CASE learning_stage
        WHEN 'Start here' THEN 1
        WHEN 'Prerequisite pathway' THEN 2
        WHEN 'Next step' THEN 3
        ELSE 4
    END,
    course_role_alignment_percent DESC,
    gaps_fully_closed DESC,
    weighted_gap_improvement DESC,
    relevant_gap_skills DESC,
    estimated_weeks ASC,
    training_name;
