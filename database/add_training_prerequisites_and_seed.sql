PRAGMA foreign_keys = ON;

-- WorkforceIQ migration: add training prerequisites
-- No row in training_prerequisites means the course has no formal prerequisite.

CREATE TABLE IF NOT EXISTS training_prerequisites (
    training_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    minimum_level INTEGER NOT NULL,

    PRIMARY KEY (training_id, skill_id),

    FOREIGN KEY (training_id)
        REFERENCES training_programs(training_id),

    FOREIGN KEY (skill_id)
        REFERENCES skills(skill_id),

    CHECK (minimum_level BETWEEN 1 AND 5)
);

-- Rebuild prerequisite seed only.
DELETE FROM training_prerequisites;

INSERT INTO training_prerequisites (training_id, skill_id, minimum_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Excel & KPI Reporting'), (SELECT skill_id FROM skills WHERE skill_name = 'Microsoft Excel'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced SQL Analytics'), (SELECT skill_id FROM skills WHERE skill_name = 'SQL Querying & Analysis'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Python for Data Analysis'), (SELECT skill_id FROM skills WHERE skill_name = 'Python Fundamentals'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Regression & Model Interpretation'), (SELECT skill_id FROM skills WHERE skill_name = 'Statistical Analysis'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced BI Storytelling & Dashboard Design'), (SELECT skill_id FROM skills WHERE skill_name = 'Power BI'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Operations Analytics & Optimization'), (SELECT skill_id FROM skills WHERE skill_name = 'Quantitative Reasoning'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced People Analytics'), (SELECT skill_id FROM skills WHERE skill_name = 'Workforce Analytics'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced People Analytics'), (SELECT skill_id FROM skills WHERE skill_name = 'Statistical Analysis'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced People Analytics'), (SELECT skill_id FROM skills WHERE skill_name = 'SQL Querying & Analysis'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'API Development & Integration'), (SELECT skill_id FROM skills WHERE skill_name = 'Requirements Elicitation & Analysis'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Docker & Application Deployment'), (SELECT skill_id FROM skills WHERE skill_name = 'Git / Version Control'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Test Automation Engineering'), (SELECT skill_id FROM skills WHERE skill_name = 'Software Testing'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Test Automation Engineering'), (SELECT skill_id FROM skills WHERE skill_name = 'Git / Version Control'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Python Automation & Scripting'), (SELECT skill_id FROM skills WHERE skill_name = 'Python Fundamentals'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Python Backend & API Development'), (SELECT skill_id FROM skills WHERE skill_name = 'Python Fundamentals'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Modeling & Architecture'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Modeling'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Modeling & Architecture'), (SELECT skill_id FROM skills WHERE skill_name = 'Relational Database Design'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Database Performance & Reliability'), (SELECT skill_id FROM skills WHERE skill_name = 'Database Administration'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Database Security & Access Control'), (SELECT skill_id FROM skills WHERE skill_name = 'Database Administration'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Data Pipelines & ETL'), (SELECT skill_id FROM skills WHERE skill_name = 'SQL Querying & Analysis'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'AWS Data Services'), (SELECT skill_id FROM skills WHERE skill_name = 'Database Administration'), 1),
((SELECT training_id FROM training_programs WHERE training_name = 'Systems Analysis & Evaluation'), (SELECT skill_id FROM skills WHERE skill_name = 'Requirements Elicitation & Analysis'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Enterprise Systems Integration'), (SELECT skill_id FROM skills WHERE skill_name = 'Systems Analysis'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'AWS Application Deployment'), (SELECT skill_id FROM skills WHERE skill_name = 'Docker'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'AWS Security & IAM'), (SELECT skill_id FROM skills WHERE skill_name = 'Information Security Fundamentals'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Identity & Access Management'), (SELECT skill_id FROM skills WHERE skill_name = 'Information Security Fundamentals'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Security Monitoring & Incident Response'), (SELECT skill_id FROM skills WHERE skill_name = 'Information Security Fundamentals'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Vulnerability Management'), (SELECT skill_id FROM skills WHERE skill_name = 'Information Security Fundamentals'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Workday Core HCM & Reporting'), (SELECT skill_id FROM skills WHERE skill_name = 'HR Operations'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Workday Recruiting & ATS'), (SELECT skill_id FROM skills WHERE skill_name = 'Talent Sourcing'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Workday Configuration for HRIS'), (SELECT skill_id FROM skills WHERE skill_name = 'Workday Core HCM'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Workday Configuration for HRIS'), (SELECT skill_id FROM skills WHERE skill_name = 'HRIS Administration'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Recruiting Analytics'), (SELECT skill_id FROM skills WHERE skill_name = 'Microsoft Excel'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Facilitation & Digital Learning Design'), (SELECT skill_id FROM skills WHERE skill_name = 'Instructional Design'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Training Evaluation & LMS Administration'), (SELECT skill_id FROM skills WHERE skill_name = 'Training Needs Analysis'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Project Risk & Stakeholder Management'), (SELECT skill_id FROM skills WHERE skill_name = 'Project Planning & Scheduling'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Product Roadmapping & Prioritization'), (SELECT skill_id FROM skills WHERE skill_name = 'Product Discovery'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Architecture'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Architecture'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Architecture'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Modeling'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Relational Database Engineering'), (SELECT skill_id FROM skills WHERE skill_name = 'Relational Database Design'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Relational Database Engineering'), (SELECT skill_id FROM skills WHERE skill_name = 'SQL Database Development'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Preparation with Python'), (SELECT skill_id FROM skills WHERE skill_name = 'Python for Data Analysis'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Preparation with Python'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Cleaning & Preparation'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced QA Design & Defect Management'), (SELECT skill_id FROM skills WHERE skill_name = 'Software Testing'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced QA Design & Defect Management'), (SELECT skill_id FROM skills WHERE skill_name = 'Test Case Design'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Jira for Technical Delivery'), (SELECT skill_id FROM skills WHERE skill_name = 'Jira'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Operations Research Modeling'), (SELECT skill_id FROM skills WHERE skill_name = 'Operations Analysis'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Operations Research Modeling'), (SELECT skill_id FROM skills WHERE skill_name = 'Optimization Modeling'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Operations Research Modeling'), (SELECT skill_id FROM skills WHERE skill_name = 'Quantitative Reasoning'), 3);

-- Validation
SELECT COUNT(*) AS total_training_prerequisites
FROM training_prerequisites;

SELECT
    tp.training_name,
    s.skill_name AS prerequisite_skill,
    tpr.minimum_level
FROM training_prerequisites tpr
JOIN training_programs tp ON tp.training_id = tpr.training_id
JOIN skills s ON s.skill_id = tpr.skill_id
ORDER BY tp.training_name, s.skill_name;

PRAGMA foreign_key_check;
