PRAGMA foreign_keys = ON;

-- WorkforceIQ job openings + future demand seed
-- Compatible with the final 100-employee synthetic workforce.
-- future_demand.required_headcount = total required headcount at that future point,
-- not incremental hires.

-- Rebuild only these two synthetic planning tables.
DELETE FROM job_openings;
DELETE FROM future_demand;

-- =========================================================
-- JOB OPENINGS
-- =========================================================
INSERT INTO job_openings (role_id, hiring_manager_id, headcount, status, open_date)
VALUES
((SELECT role_id FROM roles WHERE role_name = 'HRIS Analyst'), 1, 1, 'open', '2026-09-02'),
((SELECT role_id FROM roles WHERE role_name = 'People Analytics Analyst'), 2, 1, 'open', '2026-09-08'),
((SELECT role_id FROM roles WHERE role_name = 'Talent Acquisition Specialist'), 3, 1, 'paused', '2026-08-12'),
((SELECT role_id FROM roles WHERE role_name = 'Systems Analyst'), 6, 1, 'open', '2026-09-10'),
((SELECT role_id FROM roles WHERE role_name = 'Database Administrator'), 5, 1, 'open', '2026-08-28'),
((SELECT role_id FROM roles WHERE role_name = 'Information Security Analyst'), 7, 1, 'open', '2026-09-05'),
((SELECT role_id FROM roles WHERE role_name = 'Software Engineer'), 10, 3, 'open', '2026-08-25'),
((SELECT role_id FROM roles WHERE role_name = 'Software QA Analyst'), 9, 1, 'open', '2026-09-12'),
((SELECT role_id FROM roles WHERE role_name = 'Technical Project Manager'), 9, 1, 'open', '2026-09-01'),
((SELECT role_id FROM roles WHERE role_name = 'Product Manager'), 8, 1, 'open', '2026-09-06'),
((SELECT role_id FROM roles WHERE role_name = 'BI Analyst'), 12, 1, 'open', '2026-08-30'),
((SELECT role_id FROM roles WHERE role_name = 'Operations Research Analyst'), 11, 1, 'open', '2026-09-09');

-- =========================================================
-- FUTURE DEMAND
-- =========================================================
INSERT INTO future_demand (role_id, planning_period, required_headcount, created_at)
VALUES
((SELECT role_id FROM roles WHERE role_name = 'HR Analyst'), '2027-Q4', 4, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Talent Acquisition Specialist'), '2027-Q4', 4, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'HRIS Analyst'), '2027-Q4', 5, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'People Analytics Analyst'), '2027-Q4', 4, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Learning & Development Specialist'), '2027-Q4', 3, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Systems Analyst'), '2027-Q4', 9, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Database Administrator'), '2027-Q4', 5, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Database Architect'), '2027-Q4', 3, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Information Security Analyst'), '2027-Q4', 8, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Software Engineer'), '2027-Q4', 20, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Software QA Analyst'), '2027-Q4', 8, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Technical Project Manager'), '2027-Q4', 6, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Product Manager'), '2027-Q4', 7, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Business Analyst'), '2027-Q4', 10, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'BI Analyst'), '2027-Q4', 9, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Operations Research Analyst'), '2027-Q4', 8, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'HR Analyst'), '2028-Q4', 4, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Talent Acquisition Specialist'), '2028-Q4', 5, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'HRIS Analyst'), '2028-Q4', 6, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'People Analytics Analyst'), '2028-Q4', 5, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Learning & Development Specialist'), '2028-Q4', 4, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Systems Analyst'), '2028-Q4', 10, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Database Administrator'), '2028-Q4', 6, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Database Architect'), '2028-Q4', 3, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Information Security Analyst'), '2028-Q4', 9, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Software Engineer'), '2028-Q4', 23, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Software QA Analyst'), '2028-Q4', 9, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Technical Project Manager'), '2028-Q4', 7, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Product Manager'), '2028-Q4', 8, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Business Analyst'), '2028-Q4', 11, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'BI Analyst'), '2028-Q4', 10, '2026-09-24'),
((SELECT role_id FROM roles WHERE role_name = 'Operations Research Analyst'), '2028-Q4', 9, '2026-09-24');

-- =========================================================
-- VALIDATION
-- =========================================================

SELECT COUNT(*) AS total_job_openings FROM job_openings;

SELECT COUNT(*) AS total_future_demand_rows FROM future_demand;

-- Open requisitions with manager names
SELECT
    jo.opening_id,
    r.role_name,
    e.employee_name AS hiring_manager,
    jo.headcount,
    jo.status,
    jo.open_date
FROM job_openings jo
JOIN roles r ON jo.role_id = r.role_id
JOIN employees e ON jo.hiring_manager_id = e.employee_id
ORDER BY jo.status, r.role_name;

-- Current vs future required headcount by role
WITH current_headcount AS (
    SELECT
        current_role_id AS role_id,
        COUNT(*) AS current_headcount
    FROM employees
    GROUP BY current_role_id
)
SELECT
    r.role_name,
    COALESCE(ch.current_headcount, 0) AS current_headcount,
    fd.planning_period,
    fd.required_headcount,
    fd.required_headcount - COALESCE(ch.current_headcount, 0) AS gross_future_gap
FROM future_demand fd
JOIN roles r ON fd.role_id = r.role_id
LEFT JOIN current_headcount ch ON ch.role_id = fd.role_id
ORDER BY fd.planning_period, r.role_name;

-- Total company headcount requirement by planning period
SELECT
    planning_period,
    SUM(required_headcount) AS total_required_headcount
FROM future_demand
GROUP BY planning_period
ORDER BY planning_period;

PRAGMA foreign_key_check;