PRAGMA foreign_keys = ON;

-- WorkforceIQ revised career path seed data
-- 17 company-recognized core/formal mobility paths.
-- These paths are guidance, not a whitelist; employees may still explore roles outside them.

BEGIN TRANSACTION;

DELETE FROM career_paths;

INSERT INTO career_paths (source_role_id, target_role_id, path_description)
VALUES
((SELECT role_id FROM roles WHERE role_name = 'HR Analyst'), (SELECT role_id FROM roles WHERE role_name = 'HRIS Analyst'), 'Progression from core HR operations and employee data work into HR systems administration, configuration, and reporting.'),
((SELECT role_id FROM roles WHERE role_name = 'HR Analyst'), (SELECT role_id FROM roles WHERE role_name = 'People Analytics Analyst'), 'Progression from HR reporting and employee data work into advanced workforce analytics and quantitative analysis.'),
((SELECT role_id FROM roles WHERE role_name = 'Talent Acquisition Specialist'), (SELECT role_id FROM roles WHERE role_name = 'HR Analyst'), 'Lateral move from recruiting operations into broader HR operations, employee data, reporting, and compliance work.'),
((SELECT role_id FROM roles WHERE role_name = 'Learning & Development Specialist'), (SELECT role_id FROM roles WHERE role_name = 'HR Analyst'), 'Lateral move from learning and development operations into broader HR operations, workforce reporting, and employee data work.'),
((SELECT role_id FROM roles WHERE role_name = 'HRIS Analyst'), (SELECT role_id FROM roles WHERE role_name = 'People Analytics Analyst'), 'Lateral move from HR systems, employee data, and reporting into workforce analytics and data interpretation.'),
((SELECT role_id FROM roles WHERE role_name = 'Systems Analyst'), (SELECT role_id FROM roles WHERE role_name = 'Technical Project Manager'), 'Progression from requirements, systems analysis, and integration work into technical project planning and delivery leadership.'),
((SELECT role_id FROM roles WHERE role_name = 'Systems Analyst'), (SELECT role_id FROM roles WHERE role_name = 'Product Manager'), 'Progression from systems and requirements analysis into product discovery, prioritization, stakeholder management, and roadmapping.'),
((SELECT role_id FROM roles WHERE role_name = 'Systems Analyst'), (SELECT role_id FROM roles WHERE role_name = 'Database Administrator'), 'Lateral move from systems analysis into specialized database administration through deeper SQL, PostgreSQL, reliability, and security skills.'),
((SELECT role_id FROM roles WHERE role_name = 'Systems Analyst'), (SELECT role_id FROM roles WHERE role_name = 'Information Security Analyst'), 'Lateral move from broad systems analysis into a security specialization focused on risk, access control, monitoring, and incident response.'),
((SELECT role_id FROM roles WHERE role_name = 'Database Administrator'), (SELECT role_id FROM roles WHERE role_name = 'Database Architect'), 'Progression from database operations into advanced relational design, data modeling, data architecture, and governance.'),
((SELECT role_id FROM roles WHERE role_name = 'Software QA Analyst'), (SELECT role_id FROM roles WHERE role_name = 'Software Engineer'), 'Progression from software testing and automation into application development through stronger programming and software engineering skills.'),
((SELECT role_id FROM roles WHERE role_name = 'Software Engineer'), (SELECT role_id FROM roles WHERE role_name = 'Technical Project Manager'), 'Progression from software delivery into technical project leadership while retaining technical depth.'),
((SELECT role_id FROM roles WHERE role_name = 'Software Engineer'), (SELECT role_id FROM roles WHERE role_name = 'Product Manager'), 'Progression from software development into product discovery, prioritization, stakeholder management, and roadmap ownership.'),
((SELECT role_id FROM roles WHERE role_name = 'Business Analyst'), (SELECT role_id FROM roles WHERE role_name = 'BI Analyst'), 'Progression from business process and requirements analysis into SQL, dashboards, data analysis, and business intelligence.'),
((SELECT role_id FROM roles WHERE role_name = 'Business Analyst'), (SELECT role_id FROM roles WHERE role_name = 'Systems Analyst'), 'Progression from business process and requirements work into broader systems analysis, evaluation, integration, and technical solution design.'),
((SELECT role_id FROM roles WHERE role_name = 'BI Analyst'), (SELECT role_id FROM roles WHERE role_name = 'Operations Research Analyst'), 'Lateral move from business intelligence into deeper quantitative analysis, statistical modeling, optimization, and model validation.'),
((SELECT role_id FROM roles WHERE role_name = 'BI Analyst'), (SELECT role_id FROM roles WHERE role_name = 'People Analytics Analyst'), 'Lateral move from general business intelligence into workforce analytics using SQL, dashboards, statistics, and employee data.');

COMMIT;

SELECT COUNT(*) AS total_career_paths FROM career_paths;

SELECT
    cp.career_path_id,
    sr.role_name AS source_role,
    sr.level AS source_level,
    tr.role_name AS target_role,
    tr.level AS target_level,
    CASE
        WHEN tr.level > sr.level THEN 'Upward move'
        WHEN tr.level = sr.level THEN 'Lateral move'
        ELSE 'Downward move'
    END AS mobility_type,
    cp.path_description
FROM career_paths cp
JOIN roles sr ON cp.source_role_id = sr.role_id
JOIN roles tr ON cp.target_role_id = tr.role_id
ORDER BY sr.role_name, tr.role_name;

SELECT
    CASE
        WHEN tr.level > sr.level THEN 'Upward move'
        WHEN tr.level = sr.level THEN 'Lateral move'
        ELSE 'Downward move'
    END AS mobility_type,
    COUNT(*) AS path_count
FROM career_paths cp
JOIN roles sr ON cp.source_role_id = sr.role_id
JOIN roles tr ON cp.target_role_id = tr.role_id
GROUP BY mobility_type
ORDER BY mobility_type;