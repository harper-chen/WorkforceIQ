PRAGMA foreign_keys = ON;


-- =========================================================
-- 1. departments
-- =========================================================

CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL UNIQUE,
    department_description TEXT
);


-- =========================================================
-- 2. roles
-- =========================================================

CREATE TABLE roles (
    role_id INTEGER PRIMARY KEY,
    role_name TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    level INTEGER NOT NULL,
    role_description TEXT,

    FOREIGN KEY (department_id)
        REFERENCES departments(department_id),

    UNIQUE (role_name, department_id),

    CHECK (level > 0)
);


-- =========================================================
-- 3. skills
-- =========================================================

CREATE TABLE skills (
    skill_id INTEGER PRIMARY KEY,
    skill_name TEXT NOT NULL UNIQUE,
    skill_category TEXT NOT NULL,
    skill_description TEXT
);


-- =========================================================
-- 4. employees
-- =========================================================

CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    employee_name TEXT NOT NULL,
    current_role_id INTEGER NOT NULL,
    manager_id INTEGER,
    tenure_years REAL NOT NULL,
    hire_date TEXT,

    FOREIGN KEY (current_role_id)
        REFERENCES roles(role_id),

    FOREIGN KEY (manager_id)
        REFERENCES employees(employee_id),

    CHECK (tenure_years >= 0)
);


-- =========================================================
-- 5. employee_skills
-- =========================================================

CREATE TABLE employee_skills (
    employee_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    proficiency_level INTEGER NOT NULL,
    last_updated TEXT NOT NULL,

    PRIMARY KEY (employee_id, skill_id),

    FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id),

    FOREIGN KEY (skill_id)
        REFERENCES skills(skill_id),

    CHECK (proficiency_level BETWEEN 1 AND 5)
);


-- =========================================================
-- 6. role_skills
-- =========================================================

CREATE TABLE role_skills (
    role_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    required_level INTEGER NOT NULL,
    importance_level INTEGER NOT NULL,

    PRIMARY KEY (role_id, skill_id),

    FOREIGN KEY (role_id)
        REFERENCES roles(role_id),

    FOREIGN KEY (skill_id)
        REFERENCES skills(skill_id),

    CHECK (required_level BETWEEN 1 AND 5),

    CHECK (importance_level BETWEEN 1 AND 5)
);


-- =========================================================
-- 7. employee_career_interests
-- =========================================================

CREATE TABLE employee_career_interests (
    employee_id INTEGER NOT NULL,
    target_role_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    visibility_level TEXT NOT NULL DEFAULT 'private',

    PRIMARY KEY (employee_id, target_role_id),

    FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id),

    FOREIGN KEY (target_role_id)
        REFERENCES roles(role_id),

    CHECK (
        visibility_level IN (
            'private',
            'opening_managers'
        )
    )
);


-- =========================================================
-- 8. career_paths
-- =========================================================

CREATE TABLE career_paths (
    career_path_id INTEGER PRIMARY KEY,
    source_role_id INTEGER NOT NULL,
    target_role_id INTEGER NOT NULL,
    path_description TEXT,

    FOREIGN KEY (source_role_id)
        REFERENCES roles(role_id),

    FOREIGN KEY (target_role_id)
        REFERENCES roles(role_id),

    UNIQUE (source_role_id, target_role_id),

    CHECK (source_role_id <> target_role_id)
);


-- =========================================================
-- 9. job_openings
-- =========================================================

CREATE TABLE job_openings (
    opening_id INTEGER PRIMARY KEY,
    role_id INTEGER NOT NULL,
    hiring_manager_id INTEGER NOT NULL,
    headcount INTEGER NOT NULL,
    status TEXT NOT NULL,
    open_date TEXT NOT NULL,

    FOREIGN KEY (role_id)
        REFERENCES roles(role_id),

    FOREIGN KEY (hiring_manager_id)
        REFERENCES employees(employee_id),

    CHECK (headcount > 0),

    CHECK (
        status IN (
            'open',
            'paused',
            'filled',
            'closed'
        )
    )
);


-- =========================================================
-- 10. training_programs
-- =========================================================

CREATE TABLE training_programs (
    training_id INTEGER PRIMARY KEY,
    training_name TEXT NOT NULL,
    estimated_weeks INTEGER NOT NULL,
    training_description TEXT,

    CHECK (estimated_weeks > 0)
);


-- =========================================================
-- 11. training_skills
-- =========================================================

CREATE TABLE training_skills (
    training_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    course_skill_level INTEGER NOT NULL,

    PRIMARY KEY (training_id, skill_id),

    FOREIGN KEY (training_id)
        REFERENCES training_programs(training_id),

    FOREIGN KEY (skill_id)
        REFERENCES skills(skill_id),

    CHECK (course_skill_level BETWEEN 1 AND 5)
);


-- =========================================================
-- 12. training_prerequisites
-- =========================================================

CREATE TABLE training_prerequisites (
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


-- =========================================================
-- 13. employee_training_records
-- =========================================================

CREATE TABLE employee_training_records (
    employee_id INTEGER NOT NULL,
    training_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    enrollment_date TEXT NOT NULL,
    completion_date TEXT,
    assessment_score REAL,
    passed INTEGER,

    PRIMARY KEY (employee_id, training_id),

    FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id),

    FOREIGN KEY (training_id)
        REFERENCES training_programs(training_id),

    CHECK (
        status IN (
            'enrolled',
            'in_progress',
            'completed',
            'withdrawn'
        )
    ),

    CHECK (
        passed IN (0, 1)
        OR passed IS NULL
    ),

    CHECK (
        assessment_score IS NULL
        OR assessment_score BETWEEN 0 AND 100
    ),

    CHECK (
        (
            status = 'completed'
            AND completion_date IS NOT NULL
            AND passed IS NOT NULL
            AND passed = 1
        )
        OR
        (
            status IN (
                'enrolled',
                'in_progress',
                'withdrawn'
            )
            AND completion_date IS NULL
            AND passed IS NULL
        )
    )
);


-- =========================================================
-- 14. future_demand
-- =========================================================

CREATE TABLE future_demand (
    demand_id INTEGER PRIMARY KEY,
    role_id INTEGER NOT NULL,
    planning_period TEXT NOT NULL,
    required_headcount INTEGER NOT NULL,
    created_at TEXT NOT NULL,

    FOREIGN KEY (role_id)
        REFERENCES roles(role_id),

    UNIQUE (role_id, planning_period),

    CHECK (required_headcount >= 0)
);