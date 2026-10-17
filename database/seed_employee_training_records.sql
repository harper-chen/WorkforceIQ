PRAGMA foreign_keys = ON;

-- WorkforceIQ employee training record seed
-- 36 synthetic enrollments: completed + in_progress.
-- Business rule: completed means the employee passed the final assessment.
-- This seed records pass/fail explicitly through passed = 1 for completed rows.
-- assessment_score remains NULL because this synthetic dataset does not claim
-- a specific numeric assessment score.
-- For completed courses, employee skill proficiency is raised to at least
-- training_skills.course_skill_level; lower-level courses never reduce a skill.
-- No explicit BEGIN/COMMIT is used to avoid nested-transaction issues in SQLiteStudio.

-- Rebuild only employee training history.
DELETE FROM employee_training_records;

INSERT INTO employee_training_records (
    employee_id,
    training_id,
    status,
    enrollment_date,
    completion_date,
    assessment_score,
    passed
)
VALUES
(13, (SELECT training_id FROM training_programs WHERE training_name = 'SQL Foundations for Analysis'), 'completed', '2026-02-03', '2026-02-18', NULL, 1),
(14, (SELECT training_id FROM training_programs WHERE training_name = 'Workforce Analytics Foundations'), 'completed', '2026-03-01', '2026-03-24', NULL, 1),
(15, (SELECT training_id FROM training_programs WHERE training_name = 'Workday Core HCM & Reporting'), 'completed', '2026-01-12', '2026-02-10', NULL, 1),
(18, (SELECT training_id FROM training_programs WHERE training_name = 'HR Operations & Employee Data'), 'completed', '2026-02-05', '2026-02-28', NULL, 1),
(20, (SELECT training_id FROM training_programs WHERE training_name = 'Advanced People Analytics'), 'in_progress', '2026-09-01', NULL, NULL, NULL),
(22, (SELECT training_id FROM training_programs WHERE training_name = 'Regression & Model Interpretation'), 'completed', '2026-04-07', '2026-05-05', NULL, 1),
(27, (SELECT training_id FROM training_programs WHERE training_name = 'AWS Security & IAM'), 'in_progress', '2026-09-08', NULL, NULL, NULL),
(28, (SELECT training_id FROM training_programs WHERE training_name = 'Project Planning & Delivery Control'), 'completed', '2026-03-10', '2026-04-08', NULL, 1),
(29, (SELECT training_id FROM training_programs WHERE training_name = 'Security Fundamentals & Risk Assessment'), 'completed', '2026-05-01', '2026-05-28', NULL, 1),
(31, (SELECT training_id FROM training_programs WHERE training_name = 'Identity & Access Management'), 'completed', '2026-04-03', '2026-04-24', NULL, 1),
(32, (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Jira for Technical Delivery'), 'in_progress', '2026-09-05', NULL, NULL, NULL),
(33, (SELECT training_id FROM training_programs WHERE training_name = 'Product Discovery & Customer Analysis'), 'completed', '2026-02-14', '2026-03-12', NULL, 1),
(35, (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Relational Database Engineering'), 'in_progress', '2026-09-02', NULL, NULL, NULL),
(38, (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Architecture'), 'completed', '2026-03-01', '2026-04-05', NULL, 1),
(41, (SELECT training_id FROM training_programs WHERE training_name = 'API Development & Integration'), 'completed', '2026-01-20', '2026-02-18', NULL, 1),
(47, (SELECT training_id FROM training_programs WHERE training_name = 'Agile Software Delivery'), 'completed', '2026-05-06', '2026-05-27', NULL, 1),
(50, (SELECT training_id FROM training_programs WHERE training_name = 'Product Roadmapping & Prioritization'), 'in_progress', '2026-09-03', NULL, NULL, NULL),
(51, (SELECT training_id FROM training_programs WHERE training_name = 'Project Risk & Stakeholder Management'), 'completed', '2026-02-09', '2026-03-08', NULL, 1),
(52, (SELECT training_id FROM training_programs WHERE training_name = 'Business Case & Negotiation'), 'completed', '2026-04-01', '2026-04-25', NULL, 1),
(53, (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Jira for Technical Delivery'), 'completed', '2026-06-02', '2026-06-16', NULL, 1),
(55, (SELECT training_id FROM training_programs WHERE training_name = 'Project Planning & Delivery Control'), 'in_progress', '2026-09-10', NULL, NULL, NULL),
(62, (SELECT training_id FROM training_programs WHERE training_name = 'Java Application Development'), 'completed', '2026-02-11', '2026-03-20', NULL, 1),
(63, (SELECT training_id FROM training_programs WHERE training_name = 'Git & Collaborative Development'), 'completed', '2026-05-04', '2026-05-18', NULL, 1),
(66, (SELECT training_id FROM training_programs WHERE training_name = 'Software Testing Foundations'), 'completed', '2026-03-02', '2026-03-23', NULL, 1),
(68, (SELECT training_id FROM training_programs WHERE training_name = 'Test Automation Engineering'), 'in_progress', '2026-09-07', NULL, NULL, NULL),
(72, (SELECT training_id FROM training_programs WHERE training_name = 'Docker & Application Deployment'), 'in_progress', '2026-09-06', NULL, NULL, NULL),
(78, (SELECT training_id FROM training_programs WHERE training_name = 'Business Process Mapping & Improvement'), 'completed', '2026-01-15', '2026-02-05', NULL, 1),
(79, (SELECT training_id FROM training_programs WHERE training_name = 'Requirements Analysis & Documentation'), 'completed', '2026-04-04', '2026-05-02', NULL, 1),
(82, (SELECT training_id FROM training_programs WHERE training_name = 'Power BI Reporting & Dashboarding'), 'completed', '2026-03-03', '2026-03-24', NULL, 1),
(83, (SELECT training_id FROM training_programs WHERE training_name = 'Advanced SQL Analytics'), 'in_progress', '2026-09-09', NULL, NULL, NULL),
(85, (SELECT training_id FROM training_programs WHERE training_name = 'Advanced BI Storytelling & Dashboard Design'), 'completed', '2026-05-01', '2026-05-29', NULL, 1),
(87, (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Preparation with Python'), 'in_progress', '2026-09-04', NULL, NULL, NULL),
(91, (SELECT training_id FROM training_programs WHERE training_name = 'Operations Analytics & Optimization'), 'completed', '2026-02-02', '2026-03-10', NULL, 1),
(94, (SELECT training_id FROM training_programs WHERE training_name = 'Advanced People Analytics'), 'in_progress', '2026-09-11', NULL, NULL, NULL),
(97, (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Operations Research Modeling'), 'in_progress', '2026-09-12', NULL, NULL, NULL),
(99, (SELECT training_id FROM training_programs WHERE training_name = 'Python for Data Analysis'), 'completed', '2026-04-06', '2026-05-01', NULL, 1);

-- =========================================================
-- APPLY COMPLETED TRAINING TO EMPLOYEE SKILLS
-- =========================================================
-- Insert missing skills and raise existing proficiency when the course certifies
-- a higher level. MAX() prevents any course from lowering an existing skill.

INSERT INTO employee_skills (employee_id, skill_id, proficiency_level, last_updated)
SELECT
    etr.employee_id,
    ts.skill_id,
    ts.course_skill_level,
    etr.completion_date
FROM employee_training_records etr
JOIN training_skills ts
    ON ts.training_id = etr.training_id
WHERE etr.status = 'completed'
  AND etr.passed = 1
ON CONFLICT(employee_id, skill_id)
DO UPDATE SET
    proficiency_level = MAX(employee_skills.proficiency_level, excluded.proficiency_level),
    last_updated = CASE
        WHEN excluded.proficiency_level > employee_skills.proficiency_level
        THEN excluded.last_updated
        ELSE employee_skills.last_updated
    END;

-- =========================================================
-- VALIDATION
-- =========================================================

SELECT COUNT(*) AS total_training_records FROM employee_training_records;

SELECT
    status,
    COUNT(*) AS record_count
FROM employee_training_records
GROUP BY status
ORDER BY status;

SELECT
    e.employee_id,
    e.employee_name,
    tp.training_name,
    etr.status,
    etr.enrollment_date,
    etr.completion_date
FROM employee_training_records etr
JOIN employees e ON e.employee_id = etr.employee_id
JOIN training_programs tp ON tp.training_id = etr.training_id
ORDER BY e.employee_id, tp.training_name;

-- Check completed-course skill outcomes
SELECT
    e.employee_name,
    tp.training_name,
    s.skill_name,
    ts.course_skill_level,
    es.proficiency_level AS employee_level_after_completion
FROM employee_training_records etr
JOIN employees e ON e.employee_id = etr.employee_id
JOIN training_programs tp ON tp.training_id = etr.training_id
JOIN training_skills ts ON ts.training_id = etr.training_id
JOIN skills s ON s.skill_id = ts.skill_id
JOIN employee_skills es
  ON es.employee_id = etr.employee_id
 AND es.skill_id = ts.skill_id
WHERE etr.status = 'completed'
  AND etr.passed = 1
ORDER BY e.employee_id, tp.training_name, s.skill_name;

PRAGMA foreign_key_check;
