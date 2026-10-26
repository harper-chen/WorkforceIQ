PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

INSERT INTO employee_skills (
    employee_id,
    skill_id,
    proficiency_level,
    last_updated
)
VALUES (
    79,
    (SELECT skill_id FROM skills WHERE skill_name = 'Technical Troubleshooting'),
    1,
    '2026-10-02'
)
ON CONFLICT(employee_id, skill_id)
DO UPDATE SET
    proficiency_level = excluded.proficiency_level,
    last_updated = excluded.last_updated;

UPDATE training_skills
SET course_skill_level = 3
WHERE skill_id = (
    SELECT skill_id FROM skills WHERE skill_name = 'Systems Analysis'
)
AND course_skill_level > 3;

UPDATE training_skills
SET course_skill_level = 2
WHERE skill_id = (
    SELECT skill_id FROM skills WHERE skill_name = 'Technical Troubleshooting'
)
AND course_skill_level > 2;

COMMIT;

SELECT
    s.skill_name,
    es.proficiency_level AS current_level,
    rs.required_level,
    rs.importance_level,
    rs.required_level - es.proficiency_level AS gap
FROM employees e
JOIN employee_skills es
    ON es.employee_id = e.employee_id
JOIN skills s
    ON s.skill_id = es.skill_id
JOIN roles tr
    ON tr.role_name = 'Systems Analyst'
JOIN role_skills rs
    ON rs.role_id = tr.role_id
   AND rs.skill_id = es.skill_id
WHERE e.employee_id = 79
  AND es.proficiency_level < rs.required_level
ORDER BY rs.importance_level DESC, s.skill_name;

WITH max_training_level AS (
    SELECT
        ts.skill_id,
        MAX(ts.course_skill_level) AS max_internal_training_level
    FROM training_skills ts
    GROUP BY ts.skill_id
)
SELECT
    r.role_name,
    s.skill_name,
    rs.required_level,
    mtl.max_internal_training_level,
    CASE
        WHEN mtl.max_internal_training_level IS NULL
            THEN 'NOT_ADEQUATELY_COVERED'
        WHEN mtl.max_internal_training_level >= rs.required_level
            THEN 'ADEQUATELY_COVERED'
        ELSE 'NOT_ADEQUATELY_COVERED'
    END AS role_requirement_coverage
FROM role_skills rs
JOIN roles r
    ON r.role_id = rs.role_id
JOIN skills s
    ON s.skill_id = rs.skill_id
LEFT JOIN max_training_level mtl
    ON mtl.skill_id = rs.skill_id
WHERE s.skill_name IN (
    'Systems Evaluation',
    'Systems Analysis',
    'Technical Troubleshooting'
)
ORDER BY s.skill_name, rs.required_level, r.role_name;

WITH max_training_level AS (
    SELECT
        ts.skill_id,
        MAX(ts.course_skill_level) AS max_internal_training_level
    FROM training_skills ts
    GROUP BY ts.skill_id
)
SELECT
    s.skill_name,
    COUNT(DISTINCT rs.role_id) AS affected_roles,
    MIN(rs.required_level) AS min_required_level,
    MAX(rs.required_level) AS max_required_level,
    mtl.max_internal_training_level,
    SUM(
        CASE
            WHEN mtl.max_internal_training_level >= rs.required_level THEN 1
            ELSE 0
        END
    ) AS covered_role_requirements,
    SUM(
        CASE
            WHEN mtl.max_internal_training_level < rs.required_level THEN 1
            ELSE 0
        END
    ) AS uncovered_role_requirements
FROM role_skills rs
JOIN skills s
    ON s.skill_id = rs.skill_id
LEFT JOIN max_training_level mtl
    ON mtl.skill_id = rs.skill_id
WHERE s.skill_name = 'Systems Analysis'
GROUP BY s.skill_id, s.skill_name, mtl.max_internal_training_level;

WITH candidate_skill_match AS (
    SELECT
        rs.skill_id,
        rs.required_level,
        rs.importance_level,
        es.proficiency_level AS employee_level,
        MIN(
            1.0 * COALESCE(es.proficiency_level, 0) / rs.required_level,
            1.0
        ) AS per_skill_match,
        MAX(
            rs.required_level - COALESCE(es.proficiency_level, 0),
            0
        ) AS gap
    FROM roles r
    JOIN role_skills rs
        ON rs.role_id = r.role_id
    LEFT JOIN employee_skills es
        ON es.employee_id = 79
       AND es.skill_id = rs.skill_id
    WHERE r.role_name = 'Systems Analyst'
)
SELECT
    ROUND(
        100.0 * SUM(importance_level * per_skill_match)
        / SUM(importance_level),
        1
    ) AS match_percent,
    ROUND(
        100.0 * SUM(CASE WHEN employee_level IS NOT NULL THEN 1 ELSE 0 END)
        / COUNT(*),
        0
    ) AS profile_coverage_percent,
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
             AND importance_level >= 4 THEN 1
            ELSE 0
        END
    ) AS priority_gaps
FROM candidate_skill_match;

PRAGMA foreign_key_check;
