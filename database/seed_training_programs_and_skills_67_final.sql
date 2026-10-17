PRAGMA foreign_keys = ON;

INSERT INTO training_programs (training_name, estimated_weeks, training_description)
VALUES
('Excel for Business Analysis', 2, 'Build practical spreadsheet analysis skills for organizing data, using formulas, pivot tables, and basic business metrics.'),
('Advanced Excel & KPI Reporting', 3, 'Use advanced spreadsheet techniques to build KPI reporting workflows and interpret business performance.'),
('SQL Foundations for Analysis', 2, 'Learn foundational SQL querying for filtering, joining, aggregating, and summarizing relational data.'),
('Advanced SQL Analytics', 3, 'Apply advanced SQL techniques to complex analytical queries, transformations, and data preparation workflows.'),
('Python Foundations', 3, 'Build foundational Python programming skills using core syntax, data structures, functions, modules, and debugging.'),
('Python for Data Analysis', 4, 'Use Python to clean, explore, transform, and analyze structured datasets.'),
('Applied Statistics for Business', 4, 'Apply statistical reasoning, descriptive and inferential methods, and hypothesis testing to business problems.'),
('Regression & Model Interpretation', 4, 'Build and interpret regression models and evaluate model assumptions, limitations, and risks.'),
('Power BI Reporting & Dashboarding', 3, 'Create Power BI reports, visualizations, dashboards, and KPI monitoring views.'),
('Advanced BI Storytelling & Dashboard Design', 3, 'Design decision-oriented dashboards and communicate analytical insights through effective visual storytelling.'),
('Operations Analytics & Optimization', 5, 'Use quantitative reasoning, operations analysis, optimization models, and model validation to support operational decisions.'),
('Workforce Analytics Foundations', 3, 'Analyze workforce metrics, headcount, movement, retention, and workforce trends using structured data.'),
('Advanced People Analytics', 5, 'Apply statistical and regression methods to workforce questions while interpreting results responsibly and protecting employee data.'),
('Java Application Development', 5, 'Develop object-oriented Java applications using structured software development practices.'),
('JavaScript / TypeScript Application Development', 4, 'Build application functionality using JavaScript and TypeScript within modern software delivery workflows.'),
('API Development & Integration', 4, 'Design, implement, consume, and integrate APIs across applications and enterprise systems.'),
('Git & Collaborative Development', 2, 'Use Git for branching, merging, version control, and collaborative software development.'),
('Docker & Application Deployment', 3, 'Containerize applications and deploy application workloads using Docker and AWS.'),
('Software Testing Foundations', 3, 'Design and execute software tests, document defects, and build structured test cases.'),
('Test Automation Engineering', 4, 'Develop automated tests and integrate them into repeatable software testing workflows.'),
('Agile Software Delivery', 3, 'Apply Agile and Scrum practices using iterative planning, backlogs, Jira workflows, reviews, and retrospectives.'),
('Python Automation & Scripting', 3, 'Use Python to automate repetitive workflows, files, data transfers, and operational tasks.'),
('Python Backend & API Development', 4, 'Use Python to build backend logic and API-based services using structured development practices.'),
('Relational Database Design', 4, 'Design normalized relational schemas, relationships, keys, constraints, and database objects.'),
('Advanced Data Modeling & Architecture', 5, 'Design conceptual, logical, and physical data models and higher-level enterprise data architectures.'),
('PostgreSQL Administration', 4, 'Administer PostgreSQL environments including configuration, monitoring, users, routine maintenance, and troubleshooting.'),
('Database Performance & Reliability', 4, 'Improve database performance and reliability through tuning, monitoring, backup, and recovery practices.'),
('Database Security & Access Control', 3, 'Implement database permissions, authentication, secure access, and privacy-aware handling of data.'),
('Data Pipelines & ETL', 4, 'Build and maintain data pipelines that extract, transform, validate, and load data across systems.'),
('Data Governance & Quality', 4, 'Establish data quality, ownership, stewardship, standards, governance, and appropriate-use practices.'),
('AWS Data Services', 3, 'Use AWS services for databases, storage, processing, and data workloads.'),
('Requirements Analysis & Documentation', 4, 'Elicit, analyze, prioritize, and document stakeholder and system requirements.'),
('Systems Analysis & Evaluation', 4, 'Analyze system components, dependencies, business needs, and solution alternatives.'),
('Enterprise Systems Integration', 4, 'Integrate enterprise applications, services, data flows, and configurable business systems.'),
('Technical Troubleshooting & Service Management', 3, 'Diagnose technical problems and manage service workflows using structured troubleshooting and ServiceNow practices.'),
('AWS Application Deployment', 3, 'Deploy and operate application workloads using AWS and container-based deployment practices.'),
('AWS Security & IAM', 3, 'Configure AWS identities, permissions, access controls, and cloud security practices.'),
('Jira & Confluence for Delivery Teams', 2, 'Use Jira and Confluence to manage work, documentation, delivery workflows, and team collaboration.'),
('Security Fundamentals & Risk Assessment', 4, 'Apply core information-security principles and evaluate threats, vulnerabilities, controls, and organizational risk.'),
('Identity & Access Management', 3, 'Design and administer authentication, authorization, account lifecycle, and access-control practices.'),
('Security Monitoring & Incident Response', 4, 'Monitor security events and respond to potential incidents through investigation, containment, and recovery.'),
('Vulnerability Management', 3, 'Identify, assess, prioritize, remediate, and track security vulnerabilities.'),
('Data Privacy & Secure Handling', 2, 'Apply privacy, confidentiality, retention, access, and secure-handling practices to sensitive organizational data.'),
('HR Operations & Employee Data', 3, 'Manage core HR operations, employee lifecycle processes, workforce records, and compliant employee data practices.'),
('Workday Core HCM & Reporting', 4, 'Use Workday Core HCM and reporting capabilities for employee, job, organization, and HR reporting processes.'),
('Workday Recruiting & ATS', 3, 'Manage requisitions, candidates, recruiting workflows, and applicant tracking using Workday Recruiting and ATS practices.'),
('Workday Configuration for HRIS', 5, 'Configure and administer Workday business processes, permissions, fields, workflows, and HRIS operations.'),
('Talent Sourcing & Resume Screening', 3, 'Use structured sourcing and resume-screening methods to identify candidates against documented job criteria.'),
('Structured Interviewing & Candidate Assessment', 3, 'Design and conduct structured interviews and evaluate candidates using standardized assessment criteria.'),
('Recruiting Analytics', 3, 'Analyze recruiting funnel, sourcing, conversion, timing, and hiring metrics.'),
('Employment Compliance for HR', 2, 'Apply employment policies, legal requirements, and compliant HR practices to common HR scenarios.'),
('Learning Needs & Instructional Design', 4, 'Identify learning needs and design structured learning objectives, content, activities, and assessments.'),
('Facilitation & Digital Learning Design', 3, 'Deliver facilitated learning and create effective digital learning materials for employee development.'),
('Training Evaluation & LMS Administration', 3, 'Evaluate learning effectiveness and administer course, enrollment, completion, and learning records in an LMS.'),
('Business Process Mapping & Improvement', 3, 'Map business workflows, identify inefficiencies, and design practical process improvements.'),
('Project Planning & Delivery Control', 4, 'Plan schedules, milestones, dependencies, and monitor project delivery using structured project controls.'),
('Project Risk & Stakeholder Management', 4, 'Manage project risks, issues, stakeholders, expectations, and negotiation needs.'),
('Product Discovery & Customer Analysis', 4, 'Investigate user problems, customer needs, market conditions, and product opportunities.'),
('Product Roadmapping & Prioritization', 4, 'Prioritize product initiatives and build roadmaps supported by KPIs and business rationale.'),
('User Stories & Acceptance Criteria', 2, 'Translate product or business needs into actionable user stories, requirements, and verifiable acceptance criteria.'),
('Business Case & Negotiation', 3, 'Develop evidence-based business cases and apply structured negotiation approaches to competing priorities.');

-- Excel for Business Analysis
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Excel for Business Analysis'), (SELECT skill_id FROM skills WHERE skill_name = 'Microsoft Excel'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Excel for Business Analysis'), (SELECT skill_id FROM skills WHERE skill_name = 'KPI Analysis & Monitoring'), 2);

-- Advanced Excel & KPI Reporting
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Excel & KPI Reporting'), (SELECT skill_id FROM skills WHERE skill_name = 'Microsoft Excel'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Excel & KPI Reporting'), (SELECT skill_id FROM skills WHERE skill_name = 'KPI Analysis & Monitoring'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Excel & KPI Reporting'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Interpretation & Insight Generation'), 3);

-- SQL Foundations for Analysis
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'SQL Foundations for Analysis'), (SELECT skill_id FROM skills WHERE skill_name = 'SQL Querying & Analysis'), 2);

-- Advanced SQL Analytics
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced SQL Analytics'), (SELECT skill_id FROM skills WHERE skill_name = 'SQL Querying & Analysis'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced SQL Analytics'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Cleaning & Preparation'), 3);

-- Python Foundations
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Python Foundations'), (SELECT skill_id FROM skills WHERE skill_name = 'Python Fundamentals'), 3);

-- Python for Data Analysis
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Python for Data Analysis'), (SELECT skill_id FROM skills WHERE skill_name = 'Python Fundamentals'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Python for Data Analysis'), (SELECT skill_id FROM skills WHERE skill_name = 'Python for Data Analysis'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Python for Data Analysis'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Cleaning & Preparation'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Python for Data Analysis'), (SELECT skill_id FROM skills WHERE skill_name = 'Exploratory Data Analysis'), 3);

-- Applied Statistics for Business
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Applied Statistics for Business'), (SELECT skill_id FROM skills WHERE skill_name = 'Statistical Analysis'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Applied Statistics for Business'), (SELECT skill_id FROM skills WHERE skill_name = 'Hypothesis Testing'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Applied Statistics for Business'), (SELECT skill_id FROM skills WHERE skill_name = 'Quantitative Reasoning'), 3);

-- Regression & Model Interpretation
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Regression & Model Interpretation'), (SELECT skill_id FROM skills WHERE skill_name = 'Regression Analysis'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Regression & Model Interpretation'), (SELECT skill_id FROM skills WHERE skill_name = 'Statistical Analysis'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Regression & Model Interpretation'), (SELECT skill_id FROM skills WHERE skill_name = 'Model Validation & Risk Assessment'), 3);

-- Power BI Reporting & Dashboarding
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Power BI Reporting & Dashboarding'), (SELECT skill_id FROM skills WHERE skill_name = 'Power BI'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Power BI Reporting & Dashboarding'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Visualization'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Power BI Reporting & Dashboarding'), (SELECT skill_id FROM skills WHERE skill_name = 'Dashboard Design'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Power BI Reporting & Dashboarding'), (SELECT skill_id FROM skills WHERE skill_name = 'KPI Analysis & Monitoring'), 3);

-- Advanced BI Storytelling & Dashboard Design
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced BI Storytelling & Dashboard Design'), (SELECT skill_id FROM skills WHERE skill_name = 'Power BI'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced BI Storytelling & Dashboard Design'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Visualization'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced BI Storytelling & Dashboard Design'), (SELECT skill_id FROM skills WHERE skill_name = 'Dashboard Design'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced BI Storytelling & Dashboard Design'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Interpretation & Insight Generation'), 4);

-- Operations Analytics & Optimization
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Operations Analytics & Optimization'), (SELECT skill_id FROM skills WHERE skill_name = 'Operations Analysis'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Operations Analytics & Optimization'), (SELECT skill_id FROM skills WHERE skill_name = 'Optimization Modeling'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Operations Analytics & Optimization'), (SELECT skill_id FROM skills WHERE skill_name = 'Quantitative Reasoning'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Operations Analytics & Optimization'), (SELECT skill_id FROM skills WHERE skill_name = 'Model Validation & Risk Assessment'), 3);

-- Workforce Analytics Foundations
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Workforce Analytics Foundations'), (SELECT skill_id FROM skills WHERE skill_name = 'Workforce Analytics'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Workforce Analytics Foundations'), (SELECT skill_id FROM skills WHERE skill_name = 'SQL Querying & Analysis'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Workforce Analytics Foundations'), (SELECT skill_id FROM skills WHERE skill_name = 'KPI Analysis & Monitoring'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Workforce Analytics Foundations'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Privacy & Secure Handling'), 3);

-- Advanced People Analytics
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced People Analytics'), (SELECT skill_id FROM skills WHERE skill_name = 'Workforce Analytics'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced People Analytics'), (SELECT skill_id FROM skills WHERE skill_name = 'Regression Analysis'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced People Analytics'), (SELECT skill_id FROM skills WHERE skill_name = 'Statistical Analysis'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced People Analytics'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Interpretation & Insight Generation'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced People Analytics'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Privacy & Secure Handling'), 4);

-- Java Application Development
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Java Application Development'), (SELECT skill_id FROM skills WHERE skill_name = 'Java'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Java Application Development'), (SELECT skill_id FROM skills WHERE skill_name = 'Object-Oriented Programming'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Java Application Development'), (SELECT skill_id FROM skills WHERE skill_name = 'Software Development Lifecycle'), 3);

-- JavaScript / TypeScript Application Development
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'JavaScript / TypeScript Application Development'), (SELECT skill_id FROM skills WHERE skill_name = 'JavaScript / TypeScript'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'JavaScript / TypeScript Application Development'), (SELECT skill_id FROM skills WHERE skill_name = 'Software Development Lifecycle'), 3);

-- API Development & Integration
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'API Development & Integration'), (SELECT skill_id FROM skills WHERE skill_name = 'API Development & Integration'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'API Development & Integration'), (SELECT skill_id FROM skills WHERE skill_name = 'Systems Integration'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'API Development & Integration'), (SELECT skill_id FROM skills WHERE skill_name = 'Requirements Elicitation & Analysis'), 3);

-- Git & Collaborative Development
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Git & Collaborative Development'), (SELECT skill_id FROM skills WHERE skill_name = 'Git / Version Control'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Git & Collaborative Development'), (SELECT skill_id FROM skills WHERE skill_name = 'Agile / Scrum Practices'), 2);

-- Docker & Application Deployment
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Docker & Application Deployment'), (SELECT skill_id FROM skills WHERE skill_name = 'Docker'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Docker & Application Deployment'), (SELECT skill_id FROM skills WHERE skill_name = 'AWS Application Deployment'), 3);

-- Software Testing Foundations
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Software Testing Foundations'), (SELECT skill_id FROM skills WHERE skill_name = 'Software Testing'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Software Testing Foundations'), (SELECT skill_id FROM skills WHERE skill_name = 'Test Case Design'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Software Testing Foundations'), (SELECT skill_id FROM skills WHERE skill_name = 'Defect Tracking & Management'), 3);

-- Test Automation Engineering
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Test Automation Engineering'), (SELECT skill_id FROM skills WHERE skill_name = 'Test Automation'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Test Automation Engineering'), (SELECT skill_id FROM skills WHERE skill_name = 'Software Testing'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Test Automation Engineering'), (SELECT skill_id FROM skills WHERE skill_name = 'Git / Version Control'), 3);

-- Agile Software Delivery
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Agile Software Delivery'), (SELECT skill_id FROM skills WHERE skill_name = 'Agile / Scrum Practices'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Agile Software Delivery'), (SELECT skill_id FROM skills WHERE skill_name = 'Jira'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Agile Software Delivery'), (SELECT skill_id FROM skills WHERE skill_name = 'Software Development Lifecycle'), 3);

-- Python Automation & Scripting
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Python Automation & Scripting'), (SELECT skill_id FROM skills WHERE skill_name = 'Python Fundamentals'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Python Automation & Scripting'), (SELECT skill_id FROM skills WHERE skill_name = 'Python for Automation & Scripting'), 3);

-- Python Backend & API Development
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Python Backend & API Development'), (SELECT skill_id FROM skills WHERE skill_name = 'Python for Backend & API Development'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Python Backend & API Development'), (SELECT skill_id FROM skills WHERE skill_name = 'API Development & Integration'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Python Backend & API Development'), (SELECT skill_id FROM skills WHERE skill_name = 'Git / Version Control'), 2);

-- Relational Database Design
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Relational Database Design'), (SELECT skill_id FROM skills WHERE skill_name = 'Relational Database Design'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Relational Database Design'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Modeling'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Relational Database Design'), (SELECT skill_id FROM skills WHERE skill_name = 'SQL Database Development'), 3);

-- Advanced Data Modeling & Architecture
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Modeling & Architecture'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Modeling'), 5),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Modeling & Architecture'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Architecture'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Modeling & Architecture'), (SELECT skill_id FROM skills WHERE skill_name = 'Relational Database Design'), 4);

-- PostgreSQL Administration
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'PostgreSQL Administration'), (SELECT skill_id FROM skills WHERE skill_name = 'PostgreSQL Administration'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'PostgreSQL Administration'), (SELECT skill_id FROM skills WHERE skill_name = 'Database Administration'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'PostgreSQL Administration'), (SELECT skill_id FROM skills WHERE skill_name = 'Technical Troubleshooting'), 3);

-- Database Performance & Reliability
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Database Performance & Reliability'), (SELECT skill_id FROM skills WHERE skill_name = 'Database Performance Tuning'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Database Performance & Reliability'), (SELECT skill_id FROM skills WHERE skill_name = 'Database Backup & Recovery'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Database Performance & Reliability'), (SELECT skill_id FROM skills WHERE skill_name = 'Database Administration'), 4);

-- Database Security & Access Control
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Database Security & Access Control'), (SELECT skill_id FROM skills WHERE skill_name = 'Database Security & Access Control'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Database Security & Access Control'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Privacy & Secure Handling'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Database Security & Access Control'), (SELECT skill_id FROM skills WHERE skill_name = 'Identity & Access Management'), 2);

-- Data Pipelines & ETL
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Data Pipelines & ETL'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Pipeline & ETL Development'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Data Pipelines & ETL'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Quality Management'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Data Pipelines & ETL'), (SELECT skill_id FROM skills WHERE skill_name = 'Systems Integration'), 3);

-- Data Governance & Quality
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Data Governance & Quality'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Governance'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Data Governance & Quality'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Quality Management'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Data Governance & Quality'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Privacy & Secure Handling'), 3);

-- AWS Data Services
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'AWS Data Services'), (SELECT skill_id FROM skills WHERE skill_name = 'AWS Data Services'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'AWS Data Services'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Pipeline & ETL Development'), 2),
((SELECT training_id FROM training_programs WHERE training_name = 'AWS Data Services'), (SELECT skill_id FROM skills WHERE skill_name = 'Database Administration'), 2);

-- Requirements Analysis & Documentation
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Requirements Analysis & Documentation'), (SELECT skill_id FROM skills WHERE skill_name = 'Requirements Elicitation & Analysis'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Requirements Analysis & Documentation'), (SELECT skill_id FROM skills WHERE skill_name = 'Requirements Documentation'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Requirements Analysis & Documentation'), (SELECT skill_id FROM skills WHERE skill_name = 'Stakeholder Management'), 3);

-- Systems Analysis & Evaluation
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Systems Analysis & Evaluation'), (SELECT skill_id FROM skills WHERE skill_name = 'Systems Analysis'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Systems Analysis & Evaluation'), (SELECT skill_id FROM skills WHERE skill_name = 'Systems Evaluation'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Systems Analysis & Evaluation'), (SELECT skill_id FROM skills WHERE skill_name = 'Business Process Mapping'), 3);

-- Enterprise Systems Integration
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Enterprise Systems Integration'), (SELECT skill_id FROM skills WHERE skill_name = 'Systems Integration'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Enterprise Systems Integration'), (SELECT skill_id FROM skills WHERE skill_name = 'Business Systems Configuration'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Enterprise Systems Integration'), (SELECT skill_id FROM skills WHERE skill_name = 'API Development & Integration'), 2);

-- Technical Troubleshooting & Service Management
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Technical Troubleshooting & Service Management'), (SELECT skill_id FROM skills WHERE skill_name = 'Technical Troubleshooting'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Technical Troubleshooting & Service Management'), (SELECT skill_id FROM skills WHERE skill_name = 'ServiceNow IT Service Management'), 3);

-- AWS Application Deployment
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'AWS Application Deployment'), (SELECT skill_id FROM skills WHERE skill_name = 'AWS Application Deployment'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'AWS Application Deployment'), (SELECT skill_id FROM skills WHERE skill_name = 'Docker'), 3);

-- AWS Security & IAM
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'AWS Security & IAM'), (SELECT skill_id FROM skills WHERE skill_name = 'AWS Security & IAM'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'AWS Security & IAM'), (SELECT skill_id FROM skills WHERE skill_name = 'Identity & Access Management'), 4);

-- Jira & Confluence for Delivery Teams
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Jira & Confluence for Delivery Teams'), (SELECT skill_id FROM skills WHERE skill_name = 'Jira'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Jira & Confluence for Delivery Teams'), (SELECT skill_id FROM skills WHERE skill_name = 'Confluence'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Jira & Confluence for Delivery Teams'), (SELECT skill_id FROM skills WHERE skill_name = 'Agile / Scrum Practices'), 2);

-- Security Fundamentals & Risk Assessment
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Security Fundamentals & Risk Assessment'), (SELECT skill_id FROM skills WHERE skill_name = 'Information Security Fundamentals'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Security Fundamentals & Risk Assessment'), (SELECT skill_id FROM skills WHERE skill_name = 'Security Risk Assessment'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Security Fundamentals & Risk Assessment'), (SELECT skill_id FROM skills WHERE skill_name = 'Security Controls Evaluation'), 3);

-- Identity & Access Management
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Identity & Access Management'), (SELECT skill_id FROM skills WHERE skill_name = 'Identity & Access Management'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Identity & Access Management'), (SELECT skill_id FROM skills WHERE skill_name = 'AWS Security & IAM'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Identity & Access Management'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Privacy & Secure Handling'), 3);

-- Security Monitoring & Incident Response
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Security Monitoring & Incident Response'), (SELECT skill_id FROM skills WHERE skill_name = 'Security Monitoring'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Security Monitoring & Incident Response'), (SELECT skill_id FROM skills WHERE skill_name = 'Security Incident Response'), 4);

-- Vulnerability Management
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Vulnerability Management'), (SELECT skill_id FROM skills WHERE skill_name = 'Vulnerability Management'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Vulnerability Management'), (SELECT skill_id FROM skills WHERE skill_name = 'Security Controls Evaluation'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Vulnerability Management'), (SELECT skill_id FROM skills WHERE skill_name = 'Technical Troubleshooting'), 3);

-- Data Privacy & Secure Handling
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Data Privacy & Secure Handling'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Privacy & Secure Handling'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Data Privacy & Secure Handling'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Governance'), 3);

-- HR Operations & Employee Data
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'HR Operations & Employee Data'), (SELECT skill_id FROM skills WHERE skill_name = 'HR Operations'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'HR Operations & Employee Data'), (SELECT skill_id FROM skills WHERE skill_name = 'Employee Data Management'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'HR Operations & Employee Data'), (SELECT skill_id FROM skills WHERE skill_name = 'Employment Compliance'), 3);

-- Workday Core HCM & Reporting
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Workday Core HCM & Reporting'), (SELECT skill_id FROM skills WHERE skill_name = 'Workday Core HCM'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Workday Core HCM & Reporting'), (SELECT skill_id FROM skills WHERE skill_name = 'Workday Reporting & Analytics'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Workday Core HCM & Reporting'), (SELECT skill_id FROM skills WHERE skill_name = 'Employee Data Management'), 3);

-- Workday Recruiting & ATS
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Workday Recruiting & ATS'), (SELECT skill_id FROM skills WHERE skill_name = 'Workday Recruiting'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Workday Recruiting & ATS'), (SELECT skill_id FROM skills WHERE skill_name = 'Applicant Tracking Systems (ATS)'), 4);

-- Workday Configuration for HRIS
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Workday Configuration for HRIS'), (SELECT skill_id FROM skills WHERE skill_name = 'Workday Configuration & Administration'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Workday Configuration for HRIS'), (SELECT skill_id FROM skills WHERE skill_name = 'HRIS Administration'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Workday Configuration for HRIS'), (SELECT skill_id FROM skills WHERE skill_name = 'Business Systems Configuration'), 4);

-- Talent Sourcing & Resume Screening
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Talent Sourcing & Resume Screening'), (SELECT skill_id FROM skills WHERE skill_name = 'Talent Sourcing'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Talent Sourcing & Resume Screening'), (SELECT skill_id FROM skills WHERE skill_name = 'Resume Screening'), 4);

-- Structured Interviewing & Candidate Assessment
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Structured Interviewing & Candidate Assessment'), (SELECT skill_id FROM skills WHERE skill_name = 'Structured Interviewing'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Structured Interviewing & Candidate Assessment'), (SELECT skill_id FROM skills WHERE skill_name = 'Candidate Assessment'), 4);

-- Recruiting Analytics
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Recruiting Analytics'), (SELECT skill_id FROM skills WHERE skill_name = 'Recruiting Analytics'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Recruiting Analytics'), (SELECT skill_id FROM skills WHERE skill_name = 'Microsoft Excel'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Recruiting Analytics'), (SELECT skill_id FROM skills WHERE skill_name = 'KPI Analysis & Monitoring'), 3);

-- Employment Compliance for HR
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Employment Compliance for HR'), (SELECT skill_id FROM skills WHERE skill_name = 'Employment Compliance'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Employment Compliance for HR'), (SELECT skill_id FROM skills WHERE skill_name = 'HR Operations'), 3);

-- Learning Needs & Instructional Design
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Learning Needs & Instructional Design'), (SELECT skill_id FROM skills WHERE skill_name = 'Training Needs Analysis'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Learning Needs & Instructional Design'), (SELECT skill_id FROM skills WHERE skill_name = 'Instructional Design'), 4);

-- Facilitation & Digital Learning Design
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Facilitation & Digital Learning Design'), (SELECT skill_id FROM skills WHERE skill_name = 'Training Facilitation'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Facilitation & Digital Learning Design'), (SELECT skill_id FROM skills WHERE skill_name = 'Digital Learning Content Development'), 3);

-- Training Evaluation & LMS Administration
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Training Evaluation & LMS Administration'), (SELECT skill_id FROM skills WHERE skill_name = 'Training Evaluation'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Training Evaluation & LMS Administration'), (SELECT skill_id FROM skills WHERE skill_name = 'Learning Management Systems (LMS)'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Training Evaluation & LMS Administration'), (SELECT skill_id FROM skills WHERE skill_name = 'KPI Analysis & Monitoring'), 3);

-- Business Process Mapping & Improvement
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Business Process Mapping & Improvement'), (SELECT skill_id FROM skills WHERE skill_name = 'Business Process Mapping'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Business Process Mapping & Improvement'), (SELECT skill_id FROM skills WHERE skill_name = 'Business Process Improvement'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Business Process Mapping & Improvement'), (SELECT skill_id FROM skills WHERE skill_name = 'Stakeholder Management'), 3);

-- Project Planning & Delivery Control
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Project Planning & Delivery Control'), (SELECT skill_id FROM skills WHERE skill_name = 'Project Planning & Scheduling'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Project Planning & Delivery Control'), (SELECT skill_id FROM skills WHERE skill_name = 'Project Status & Delivery Monitoring'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Project Planning & Delivery Control'), (SELECT skill_id FROM skills WHERE skill_name = 'Jira'), 3);

-- Project Risk & Stakeholder Management
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Project Risk & Stakeholder Management'), (SELECT skill_id FROM skills WHERE skill_name = 'Project Risk & Issue Management'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Project Risk & Stakeholder Management'), (SELECT skill_id FROM skills WHERE skill_name = 'Stakeholder Management'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Project Risk & Stakeholder Management'), (SELECT skill_id FROM skills WHERE skill_name = 'Negotiation'), 3);

-- Product Discovery & Customer Analysis
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Product Discovery & Customer Analysis'), (SELECT skill_id FROM skills WHERE skill_name = 'Product Discovery'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Product Discovery & Customer Analysis'), (SELECT skill_id FROM skills WHERE skill_name = 'Market & Customer Analysis'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Product Discovery & Customer Analysis'), (SELECT skill_id FROM skills WHERE skill_name = 'Stakeholder Management'), 3);

-- Product Roadmapping & Prioritization
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Product Roadmapping & Prioritization'), (SELECT skill_id FROM skills WHERE skill_name = 'Product Prioritization & Roadmapping'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Product Roadmapping & Prioritization'), (SELECT skill_id FROM skills WHERE skill_name = 'Business Case Development'), 3),
((SELECT training_id FROM training_programs WHERE training_name = 'Product Roadmapping & Prioritization'), (SELECT skill_id FROM skills WHERE skill_name = 'KPI Analysis & Monitoring'), 3);

-- User Stories & Acceptance Criteria
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'User Stories & Acceptance Criteria'), (SELECT skill_id FROM skills WHERE skill_name = 'User Story & Acceptance Criteria Design'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'User Stories & Acceptance Criteria'), (SELECT skill_id FROM skills WHERE skill_name = 'Requirements Documentation'), 3);

-- Business Case & Negotiation
INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
((SELECT training_id FROM training_programs WHERE training_name = 'Business Case & Negotiation'), (SELECT skill_id FROM skills WHERE skill_name = 'Business Case Development'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Business Case & Negotiation'), (SELECT skill_id FROM skills WHERE skill_name = 'Negotiation'), 4),
((SELECT training_id FROM training_programs WHERE training_name = 'Business Case & Negotiation'), (SELECT skill_id FROM skills WHERE skill_name = 'Data Interpretation & Insight Generation'), 3);


-- =========================================================
-- Advanced coverage courses added after level coverage audit
-- =========================================================

-- 62. Advanced Data Architecture
INSERT INTO training_programs (
    training_name,
    estimated_weeks,
    training_description
)
VALUES (
    'Advanced Data Architecture',
    5,
    'Design advanced enterprise data architectures, integration patterns, data domains, governance structures, and scalable data platforms.'
);

INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Architecture'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Data Architecture'),
    5
),
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Architecture'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Data Governance'),
    4
);

-- 63. Advanced Relational Database Engineering
INSERT INTO training_programs (
    training_name,
    estimated_weeks,
    training_description
)
VALUES (
    'Advanced Relational Database Engineering',
    5,
    'Design advanced relational database structures and implement complex database objects, constraints, indexing strategies, and SQL-based database logic.'
);

INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Relational Database Engineering'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Relational Database Design'),
    5
),
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Relational Database Engineering'),
    (SELECT skill_id FROM skills WHERE skill_name = 'SQL Database Development'),
    4
),
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Relational Database Engineering'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Data Modeling'),
    4
);

-- 64. Advanced Data Preparation with Python
INSERT INTO training_programs (
    training_name,
    estimated_weeks,
    training_description
)
VALUES (
    'Advanced Data Preparation with Python',
    4,
    'Use advanced Python data workflows to clean, transform, validate, restructure, and prepare complex datasets for analytical use.'
);

INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Preparation with Python'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Python for Data Analysis'),
    4
),
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Preparation with Python'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Data Cleaning & Preparation'),
    4
),
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Data Preparation with Python'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Exploratory Data Analysis'),
    3
);

-- 65. Advanced QA Design & Defect Management
INSERT INTO training_programs (
    training_name,
    estimated_weeks,
    training_description
)
VALUES (
    'Advanced QA Design & Defect Management',
    4,
    'Design advanced software test strategies and manage complex defect lifecycles, prioritization, reproducibility, and resolution workflows.'
);

INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced QA Design & Defect Management'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Test Case Design'),
    4
),
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced QA Design & Defect Management'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Defect Tracking & Management'),
    4
),
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced QA Design & Defect Management'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Software Testing'),
    4
);

-- 66. Advanced Jira for Technical Delivery
INSERT INTO training_programs (
    training_name,
    estimated_weeks,
    training_description
)
VALUES (
    'Advanced Jira for Technical Delivery',
    2,
    'Use advanced Jira workflows, boards, issue structures, dependencies, reporting, and delivery tracking for complex technical projects.'
);

INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Jira for Technical Delivery'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Jira'),
    4
),
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Jira for Technical Delivery'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Project Status & Delivery Monitoring'),
    4
);

-- 67. Advanced Operations Research Modeling
INSERT INTO training_programs (
    training_name,
    estimated_weeks,
    training_description
)
VALUES (
    'Advanced Operations Research Modeling',
    6,
    'Build, evaluate, validate, and apply advanced quantitative and optimization models for complex operational and resource-allocation decisions.'
);

INSERT INTO training_skills (training_id, skill_id, course_skill_level)
VALUES
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Operations Research Modeling'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Operations Analysis'),
    5
),
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Operations Research Modeling'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Optimization Modeling'),
    5
),
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Operations Research Modeling'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Model Validation & Risk Assessment'),
    4
),
(
    (SELECT training_id FROM training_programs WHERE training_name = 'Advanced Operations Research Modeling'),
    (SELECT skill_id FROM skills WHERE skill_name = 'Quantitative Reasoning'),
    4
);

-- Final validation
SELECT COUNT(*) AS total_training_programs
FROM training_programs;

SELECT COUNT(*) AS total_training_skill_mappings
FROM training_skills;
