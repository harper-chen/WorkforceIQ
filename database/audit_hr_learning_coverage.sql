
PRAGMA foreign_keys = ON;

-- =========================================================
-- WorkforceIQ HR / Workforce Planning
-- Learning-coverage audit (READ ONLY)
-- =========================================================

WITH max_training_level AS (
    SELECT
        ts.skill_id,
        MAX(ts.course_skill_level) AS max_internal_training_level
    FROM training_skills ts
    GROUP BY ts.skill_id
),
future_roles AS (
    SELECT DISTINCT role_id
    FROM future_demand
)
SELECT
    r.role_name,
    s.skill_name,
    rs.required_level,
    rs.importance_level,
    mtl.max_internal_training_level,
    CASE
        WHEN mtl.max_internal_training_level IS NULL
            THEN 'NO_INTERNAL_TRAINING'
        WHEN mtl.max_internal_training_level >= rs.required_level
            THEN 'ADEQUATELY_COVERED'
        ELSE 'BELOW_REQUIRED_LEVEL'
    END AS coverage_status
FROM role_skills rs
JOIN future_roles fr
    ON fr.role_id = rs.role_id
JOIN roles r
    ON r.role_id = rs.role_id
JOIN skills s
    ON s.skill_id = rs.skill_id
LEFT JOIN max_training_level mtl
    ON mtl.skill_id = rs.skill_id
ORDER BY
    coverage_status,
    s.skill_name,
    rs.required_level,
    r.role_name;

WITH max_training_level AS (
    SELECT
        ts.skill_id,
        MAX(ts.course_skill_level) AS max_internal_training_level
    FROM training_skills ts
    GROUP BY ts.skill_id
),
future_role_skills AS (
    SELECT DISTINCT
        rs.role_id,
        rs.skill_id,
        rs.required_level
    FROM role_skills rs
    JOIN future_demand fd
        ON fd.role_id = rs.role_id
)
SELECT
    s.skill_name,
    COUNT(*) AS future_role_requirements,
    MIN(frs.required_level) AS min_required_level,
    MAX(frs.required_level) AS max_required_level,
    mtl.max_internal_training_level,
    SUM(
        CASE
            WHEN COALESCE(mtl.max_internal_training_level, 0)
                 >= frs.required_level
                THEN 1
            ELSE 0
        END
    ) AS adequately_covered_role_pairs,
    SUM(
        CASE
            WHEN COALESCE(mtl.max_internal_training_level, 0)
                 < frs.required_level
                THEN 1
            ELSE 0
        END
    ) AS not_adequately_covered_role_pairs
FROM future_role_skills frs
JOIN skills s
    ON s.skill_id = frs.skill_id
LEFT JOIN max_training_level mtl
    ON mtl.skill_id = frs.skill_id
GROUP BY
    frs.skill_id,
    s.skill_name,
    mtl.max_internal_training_level
HAVING
    adequately_covered_role_pairs > 0
    AND not_adequately_covered_role_pairs > 0
ORDER BY
    not_adequately_covered_role_pairs DESC,
    adequately_covered_role_pairs DESC,
    s.skill_name;

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
            THEN 'No course available'
        ELSE 'Existing course below required level'
    END AS reason
FROM role_skills rs
JOIN roles r
    ON r.role_id = rs.role_id
JOIN skills s
    ON s.skill_id = rs.skill_id
JOIN future_demand fd
    ON fd.role_id = rs.role_id
LEFT JOIN max_training_level mtl
    ON mtl.skill_id = rs.skill_id
WHERE
    COALESCE(mtl.max_internal_training_level, 0) < rs.required_level
GROUP BY
    r.role_id,
    r.role_name,
    rs.skill_id,
    s.skill_name,
    rs.required_level,
    mtl.max_internal_training_level
ORDER BY
    reason,
    r.role_name,
    s.skill_name;

-- =========================================================
-- Scope note
-- =========================================================
-- The current WorkforceIQ HR workspace is aggregate-only.
-- Employee-level career-interest and internal-mobility candidate
-- audits are intentionally excluded from this file.
