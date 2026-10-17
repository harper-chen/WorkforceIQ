-- WorkforceIQ: Target Role Match
-- Change employee_id and target role name below for testing in SQLiteStudio.

WITH params AS (
    SELECT
        13 AS employee_id,
        (SELECT role_id FROM roles WHERE role_name = 'BI Analyst') AS target_role_id
),
skill_match AS (
    SELECT
        p.employee_id,
        p.target_role_id,
        s.skill_id,
        s.skill_name,
        s.skill_category,
        es.proficiency_level AS employee_level,
        rs.required_level,
        rs.importance_level,
        MAX(rs.required_level - COALESCE(es.proficiency_level, 0), 0) AS gap,
        MIN(1.0 * COALESCE(es.proficiency_level, 0) / rs.required_level, 1.0) AS per_skill_match
    FROM params p
    JOIN role_skills rs ON rs.role_id = p.target_role_id
    JOIN skills s ON s.skill_id = rs.skill_id
    LEFT JOIN employee_skills es
      ON es.employee_id = p.employee_id
     AND es.skill_id = rs.skill_id
),
overall AS (
    SELECT
        employee_id,
        target_role_id,
        SUM(importance_level * per_skill_match) / SUM(importance_level) AS overall_match
    FROM skill_match
    GROUP BY employee_id, target_role_id
)
SELECT
    e.employee_id,
    e.employee_name,
    current_role.role_name AS current_role,
    target_role.role_name AS target_role,
    ROUND(o.overall_match * 100, 1) AS overall_match_percent,
    sm.skill_name,
    sm.skill_category,
    sm.employee_level,
    sm.required_level,
    sm.importance_level,
    sm.gap,
    ROUND(sm.per_skill_match * 100, 1) AS per_skill_match_percent,
    CASE
        WHEN sm.employee_level IS NULL THEN 'Not recorded'
        WHEN sm.gap = 0 THEN 'Meets'
        WHEN sm.gap >= 2 AND sm.importance_level >= 4 THEN 'Priority gap'
        ELSE 'Develop'
    END AS skill_status
FROM skill_match sm
JOIN overall o
  ON o.employee_id = sm.employee_id
 AND o.target_role_id = sm.target_role_id
JOIN employees e ON e.employee_id = sm.employee_id
JOIN roles current_role ON current_role.role_id = e.current_role_id
JOIN roles target_role ON target_role.role_id = sm.target_role_id
ORDER BY sm.importance_level DESC, sm.gap DESC, sm.skill_name;
