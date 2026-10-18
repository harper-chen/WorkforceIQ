PRAGMA foreign_keys = ON;

-- =========================================================
-- WorkforceIQ employee career interest seed
-- =========================================================
-- Career interests are role-specific.
-- Each saved career is private by default.
--
-- visibility_level:
--   private           = visible only to the employee
--   opening_managers  = visible to the employee and
--                       managers responsible for openings
--                       for the exact target role
--
-- No explicit BEGIN / COMMIT is used to avoid
-- nested-transaction errors in SQLiteStudio.
-- =========================================================


-- =========================================================
-- RESET
-- =========================================================

DELETE FROM employee_career_interests;


-- =========================================================
-- EMPLOYEE CAREER INTERESTS
-- =========================================================

INSERT INTO employee_career_interests (
    employee_id,
    target_role_id,
    created_at,
    visibility_level
)
VALUES

(4,
 (SELECT role_id FROM roles WHERE role_name = 'HR Analyst'),
 '2026-04-06',
 'private'),

(6,
 (SELECT role_id FROM roles WHERE role_name = 'Product Manager'),
 '2026-08-27',
 'private'),

(12,
 (SELECT role_id FROM roles WHERE role_name = 'Operations Research Analyst'),
 '2026-07-03',
 'private'),

(12,
 (SELECT role_id FROM roles WHERE role_name = 'People Analytics Analyst'),
 '2026-05-01',
 'private'),

(14,
 (SELECT role_id FROM roles WHERE role_name = 'People Analytics Analyst'),
 '2026-07-27',
 'private'),

(15,
 (SELECT role_id FROM roles WHERE role_name = 'People Analytics Analyst'),
 '2026-04-05',
 'private'),

(18,
 (SELECT role_id FROM roles WHERE role_name = 'HR Analyst'),
 '2026-04-26',
 'private'),

(20,
 (SELECT role_id FROM roles WHERE role_name = 'People Analytics Analyst'),
 '2026-07-09',
 'private'),

(22,
 (SELECT role_id FROM roles WHERE role_name = 'People Analytics Analyst'),
 '2026-07-04',
 'private'),

(27,
 (SELECT role_id FROM roles WHERE role_name = 'Information Security Analyst'),
 '2026-07-02',
 'private'),

(28,
 (SELECT role_id FROM roles WHERE role_name = 'Technical Project Manager'),
 '2026-07-10',
 'private'),

(28,
 (SELECT role_id FROM roles WHERE role_name = 'Product Manager'),
 '2026-03-29',
 'private'),

(29,
 (SELECT role_id FROM roles WHERE role_name = 'Information Security Analyst'),
 '2026-07-14',
 'private'),

(31,
 (SELECT role_id FROM roles WHERE role_name = 'Information Security Analyst'),
 '2026-08-19',
 'private'),

(32,
 (SELECT role_id FROM roles WHERE role_name = 'Technical Project Manager'),
 '2026-08-25',
 'private'),

(33,
 (SELECT role_id FROM roles WHERE role_name = 'Product Manager'),
 '2026-04-29',
 'private'),

(33,
 (SELECT role_id FROM roles WHERE role_name = 'Technical Project Manager'),
 '2026-07-23',
 'private'),

(35,
 (SELECT role_id FROM roles WHERE role_name = 'Database Architect'),
 '2026-08-15',
 'private'),

(38,
 (SELECT role_id FROM roles WHERE role_name = 'Database Architect'),
 '2026-08-23',
 'private'),

(47,
 (SELECT role_id FROM roles WHERE role_name = 'Technical Project Manager'),
 '2026-07-06',
 'private'),

(50,
 (SELECT role_id FROM roles WHERE role_name = 'Product Manager'),
 '2026-04-27',
 'private'),

(51,
 (SELECT role_id FROM roles WHERE role_name = 'Product Manager'),
 '2026-07-23',
 'private'),

(51,
 (SELECT role_id FROM roles WHERE role_name = 'Technical Project Manager'),
 '2026-05-05',
 'private'),

(52,
 (SELECT role_id FROM roles WHERE role_name = 'Product Manager'),
 '2026-07-19',
 'private'),

(52,
 (SELECT role_id FROM roles WHERE role_name = 'Technical Project Manager'),
 '2026-05-17',
 'private'),

(53,
 (SELECT role_id FROM roles WHERE role_name = 'Product Manager'),
 '2026-06-20',
 'private'),

(55,
 (SELECT role_id FROM roles WHERE role_name = 'Technical Project Manager'),
 '2026-08-05',
 'private'),

(55,
 (SELECT role_id FROM roles WHERE role_name = 'Product Manager'),
 '2026-04-08',
 'private'),

(62,
 (SELECT role_id FROM roles WHERE role_name = 'Software Engineer'),
 '2026-08-04',
 'private'),

(63,
 (SELECT role_id FROM roles WHERE role_name = 'Software Engineer'),
 '2026-07-11',
 'private'),

(66,
 (SELECT role_id FROM roles WHERE role_name = 'Software Engineer'),
 '2026-05-07',
 'private'),

(68,
 (SELECT role_id FROM roles WHERE role_name = 'Software Engineer'),
 '2026-05-18',
 'private'),

(78,
 (SELECT role_id FROM roles WHERE role_name = 'Systems Analyst'),
 '2026-05-15',
 'private'),

(78,
 (SELECT role_id FROM roles WHERE role_name = 'BI Analyst'),
 '2026-05-27',
 'private'),

(79,
 (SELECT role_id FROM roles WHERE role_name = 'Systems Analyst'),
 '2026-05-31',
 'opening_managers'),

(79,
 (SELECT role_id FROM roles WHERE role_name = 'BI Analyst'),
 '2026-04-18',
 'private'),

(82,
 (SELECT role_id FROM roles WHERE role_name = 'BI Analyst'),
 '2026-04-25',
 'private'),

(83,
 (SELECT role_id FROM roles WHERE role_name = 'BI Analyst'),
 '2026-06-27',
 'private'),

(85,
 (SELECT role_id FROM roles WHERE role_name = 'BI Analyst'),
 '2026-08-23',
 'private'),

(87,
 (SELECT role_id FROM roles WHERE role_name = 'BI Analyst'),
 '2026-08-30',
 'private'),

(94,
 (SELECT role_id FROM roles WHERE role_name = 'People Analytics Analyst'),
 '2026-04-22',
 'private');


-- =========================================================
-- VALIDATION
-- =========================================================

-- Total number of saved career interests
SELECT
    COUNT(*) AS total_career_interests
FROM employee_career_interests;


-- Distribution by visibility level
SELECT
    visibility_level,
    COUNT(*) AS career_interest_count
FROM employee_career_interests
GROUP BY visibility_level
ORDER BY career_interest_count DESC;


-- Number of interested employees by target role
SELECT
    r.role_name AS target_role,
    COUNT(*) AS interested_employees
FROM employee_career_interests eci
JOIN roles r
    ON eci.target_role_id = r.role_id
GROUP BY
    r.role_id,
    r.role_name
ORDER BY
    interested_employees DESC,
    r.role_name;


-- Detailed career interest records
SELECT
    e.employee_id,
    e.employee_name,
    cr.role_name AS current_role,
    tr.role_name AS target_role,
    cr.level AS current_level,
    tr.level AS target_level,

    CASE
        WHEN tr.level > cr.level THEN 'Upward move'
        WHEN tr.level = cr.level THEN 'Lateral move'
        ELSE 'Downward move'
    END AS mobility_type,

    eci.visibility_level

FROM employee_career_interests eci

JOIN employees e
    ON eci.employee_id = e.employee_id

JOIN roles cr
    ON e.current_role_id = cr.role_id

JOIN roles tr
    ON eci.target_role_id = tr.role_id

ORDER BY
    e.employee_id,
    tr.role_name;


-- Check foreign-key integrity
PRAGMA foreign_key_check;