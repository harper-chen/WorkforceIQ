"""
Traditional Chinese (Taiwan) names for the demo data: roles, skills, courses.

Only used when the interface is in Chinese (?lang=zh). The database itself
always stays in English.

Naming choices:
* Roles are shown in both languages, e.g. 系統分析師（Systems Analyst),
  because Taiwanese tech companies use both forms.
* Product and tool names stay as they are: SQL, Power BI, Jira, Docker,
  Workday, AWS, Python ...
"""

import functools

import pandas as pd

from i18n import is_zh


ROLES_ZH = {
    "BI Analyst": "商業智慧分析師",
    "Business Analyst": "商業分析師",
    "Database Administrator": "資料庫管理師",
    "Database Architect": "資料庫架構師",
    "HR Analyst": "人資分析師",
    "HRIS Analyst": "人資系統分析師",
    "Information Security Analyst": "資訊安全分析師",
    "Learning & Development Specialist": "學習發展專員",
    "Operations Research Analyst": "作業研究分析師",
    "People Analytics Analyst": "人才數據分析師",
    "Product Manager": "產品經理",
    "Software Engineer": "軟體工程師",
    "Software QA Analyst": "軟體測試分析師",
    "Systems Analyst": "系統分析師",
    "Talent Acquisition Specialist": "人才招募專員",
    "Technical Project Manager": "技術專案經理",
}

SKILLS_ZH = {
    "API Development & Integration": "API 開發與整合",
    "AWS Application Deployment": "AWS 應用程式部署",
    "AWS Data Services": "AWS 資料服務",
    "AWS Security & IAM": "AWS 安全與 IAM",
    "Agile / Scrum Practices": "Agile／Scrum 實務",
    "Applicant Tracking Systems (ATS)": "應徵者追蹤系統（ATS）",
    "Business Case Development": "商業提案撰寫",
    "Business Process Improvement": "業務流程改善",
    "Business Process Mapping": "業務流程繪製",
    "Business Systems Configuration": "企業系統設定",
    "Candidate Assessment": "候選人評估",
    "Confluence": "Confluence",
    "Dashboard Design": "儀表板設計",
    "Data Architecture": "資料架構",
    "Data Cleaning & Preparation": "資料清理與準備",
    "Data Governance": "資料治理",
    "Data Interpretation & Insight Generation": "資料解讀與洞察",
    "Data Modeling": "資料建模",
    "Data Pipeline & ETL Development": "資料管線與 ETL 開發",
    "Data Privacy & Secure Handling": "資料隱私與安全處理",
    "Data Quality Management": "資料品質管理",
    "Data Visualization": "資料視覺化",
    "Database Administration": "資料庫管理",
    "Database Backup & Recovery": "資料庫備份與復原",
    "Database Performance Tuning": "資料庫效能調校",
    "Database Security & Access Control": "資料庫安全與存取控制",
    "Defect Tracking & Management": "缺陷追蹤與管理",
    "Digital Learning Content Development": "數位學習內容開發",
    "Docker": "Docker",
    "Employee Data Management": "員工資料管理",
    "Employment Compliance": "勞動法規遵循",
    "Exploratory Data Analysis": "探索性資料分析",
    "Git / Version Control": "Git／版本控制",
    "HR Operations": "人資作業",
    "HRIS Administration": "人資系統管理",
    "Hypothesis Testing": "假設檢定",
    "Identity & Access Management": "身分與存取管理",
    "Information Security Fundamentals": "資訊安全基礎",
    "Instructional Design": "教學設計",
    "Java": "Java",
    "JavaScript / TypeScript": "JavaScript／TypeScript",
    "Jira": "Jira",
    "KPI Analysis & Monitoring": "KPI 分析與監控",
    "Learning Management Systems (LMS)": "學習管理系統（LMS）",
    "Market & Customer Analysis": "市場與客戶分析",
    "Microsoft Excel": "Microsoft Excel",
    "Model Validation & Risk Assessment": "模型驗證與風險評估",
    "Negotiation": "談判協商",
    "Object-Oriented Programming": "物件導向程式設計",
    "Operations Analysis": "營運分析",
    "Optimization Modeling": "最佳化建模",
    "PostgreSQL Administration": "PostgreSQL 管理",
    "Power BI": "Power BI",
    "Product Discovery": "產品探索",
    "Product Prioritization & Roadmapping": "產品優先排序與路線圖規劃",
    "Project Planning & Scheduling": "專案規劃與排程",
    "Project Risk & Issue Management": "專案風險與議題管理",
    "Project Status & Delivery Monitoring": "專案進度與交付追蹤",
    "Python Fundamentals": "Python 基礎",
    "Python for Automation & Scripting": "Python 自動化與腳本",
    "Python for Backend & API Development": "Python 後端與 API 開發",
    "Python for Data Analysis": "Python 資料分析",
    "Quantitative Reasoning": "量化推理",
    "Recruiting Analytics": "招募數據分析",
    "Regression Analysis": "迴歸分析",
    "Relational Database Design": "關聯式資料庫設計",
    "Requirements Documentation": "需求文件撰寫",
    "Requirements Elicitation & Analysis": "需求訪談與分析",
    "Resume Screening": "履歷篩選",
    "SQL Database Development": "SQL 資料庫開發",
    "SQL Querying & Analysis": "SQL 查詢與分析",
    "Security Controls Evaluation": "資安控制措施評估",
    "Security Incident Response": "資安事件應變",
    "Security Monitoring": "資安監控",
    "Security Risk Assessment": "資安風險評估",
    "ServiceNow IT Service Management": "ServiceNow IT 服務管理",
    "Software Development Lifecycle": "軟體開發生命週期",
    "Software Testing": "軟體測試",
    "Stakeholder Management": "利害關係人管理",
    "Statistical Analysis": "統計分析",
    "Structured Interviewing": "結構化面試",
    "Systems Analysis": "系統分析",
    "Systems Evaluation": "系統評估",
    "Systems Integration": "系統整合",
    "Talent Sourcing": "人才搜尋",
    "Technical Troubleshooting": "技術問題排除",
    "Test Automation": "測試自動化",
    "Test Case Design": "測試案例設計",
    "Training Evaluation": "培訓成效評估",
    "Training Facilitation": "培訓引導",
    "Training Needs Analysis": "培訓需求分析",
    "User Story & Acceptance Criteria Design": "使用者故事與驗收條件設計",
    "Vulnerability Management": "弱點管理",
    "Workday Configuration & Administration": "Workday 設定與管理",
    "Workday Core HCM": "Workday Core HCM",
    "Workday Recruiting": "Workday Recruiting",
    "Workday Reporting & Analytics": "Workday 報表與分析",
    "Workforce Analytics": "人力數據分析",
}

COURSES_ZH = {
    "API Development & Integration": "API 開發與整合",
    "AWS Application Deployment": "AWS 應用程式部署",
    "AWS Data Services": "AWS 資料服務",
    "AWS Security & IAM": "AWS 安全與 IAM",
    "Advanced BI Storytelling & Dashboard Design": "進階 BI 資料敘事與儀表板設計",
    "Advanced Data Architecture": "進階資料架構",
    "Advanced Data Modeling & Architecture": "進階資料建模與架構",
    "Advanced Data Preparation with Python": "Python 進階資料準備",
    "Advanced Excel & KPI Reporting": "進階 Excel 與 KPI 報表",
    "Advanced Jira for Technical Delivery": "Jira 進階技術交付管理",
    "Advanced Operations Research Modeling": "進階作業研究建模",
    "Advanced People Analytics": "進階人才數據分析",
    "Advanced QA Design & Defect Management": "進階測試設計與缺陷管理",
    "Advanced Relational Database Engineering": "進階關聯式資料庫工程",
    "Advanced SQL Analytics": "進階 SQL 分析",
    "Agile Software Delivery": "敏捷軟體交付",
    "Applied Statistics for Business": "商業應用統計",
    "Business Case & Negotiation": "商業提案與談判",
    "Business Process Mapping & Improvement": "業務流程繪製與改善",
    "Data Governance & Quality": "資料治理與品質",
    "Data Pipelines & ETL": "資料管線與 ETL",
    "Data Privacy & Secure Handling": "資料隱私與安全處理",
    "Database Performance & Reliability": "資料庫效能與可靠性",
    "Database Security & Access Control": "資料庫安全與存取控制",
    "Docker & Application Deployment": "Docker 與應用程式部署",
    "Employment Compliance for HR": "人資勞動法規遵循",
    "Enterprise Systems Integration": "企業系統整合",
    "Excel for Business Analysis": "商業分析 Excel 實務",
    "Facilitation & Digital Learning Design": "課程引導與數位學習設計",
    "Git & Collaborative Development": "Git 與協作開發",
    "HR Operations & Employee Data": "人資作業與員工資料",
    "Identity & Access Management": "身分與存取管理",
    "Java Application Development": "Java 應用程式開發",
    "JavaScript / TypeScript Application Development": "JavaScript／TypeScript 應用程式開發",
    "Jira & Confluence for Delivery Teams": "交付團隊的 Jira 與 Confluence",
    "Learning Needs & Instructional Design": "學習需求分析與教學設計",
    "Operations Analytics & Optimization": "營運分析與最佳化",
    "PostgreSQL Administration": "PostgreSQL 管理",
    "Power BI Reporting & Dashboarding": "Power BI 報表與儀表板",
    "Product Discovery & Customer Analysis": "產品探索與客戶分析",
    "Product Roadmapping & Prioritization": "產品路線圖與優先排序",
    "Project Planning & Delivery Control": "專案規劃與交付控管",
    "Project Risk & Stakeholder Management": "專案風險與利害關係人管理",
    "Python Automation & Scripting": "Python 自動化與腳本",
    "Python Backend & API Development": "Python 後端與 API 開發",
    "Python Foundations": "Python 基礎",
    "Python for Data Analysis": "Python 資料分析",
    "Recruiting Analytics": "招募數據分析",
    "Regression & Model Interpretation": "迴歸分析與模型解讀",
    "Relational Database Design": "關聯式資料庫設計",
    "Requirements Analysis & Documentation": "需求分析與文件撰寫",
    "SQL Foundations for Analysis": "資料分析 SQL 基礎",
    "Security Fundamentals & Risk Assessment": "資安基礎與風險評估",
    "Security Monitoring & Incident Response": "資安監控與事件應變",
    "Software Testing Foundations": "軟體測試基礎",
    "Structured Interviewing & Candidate Assessment": "結構化面試與候選人評估",
    "Systems Analysis & Evaluation": "系統分析與評估",
    "Talent Sourcing & Resume Screening": "人才搜尋與履歷篩選",
    "Technical Troubleshooting & Service Management": "技術問題排除與服務管理",
    "Test Automation Engineering": "測試自動化工程",
    "Training Evaluation & LMS Administration": "培訓成效評估與 LMS 管理",
    "User Stories & Acceptance Criteria": "使用者故事與驗收條件",
    "Vulnerability Management": "弱點管理",
    "Workday Configuration for HRIS": "Workday 人資系統設定",
    "Workday Core HCM & Reporting": "Workday Core HCM 與報表",
    "Workday Recruiting & ATS": "Workday Recruiting 與 ATS",
    "Workforce Analytics Foundations": "人力數據分析基礎",
}

COURSE_DESCRIPTIONS_ZH = {
    "API Development & Integration": "設計、實作與串接 API，整合各應用程式與企業系統。",
    "AWS Application Deployment": "運用 AWS 與容器化部署實務，部署並維運應用程式。",
    "AWS Data Services": "運用 AWS 服務處理資料庫、儲存、運算與各類資料工作。",
    "AWS Security & IAM": "設定 AWS 的身分、權限與存取控制，並落實雲端安全實務。",
    "Advanced BI Storytelling & Dashboard Design": "設計以決策為導向的儀表板，透過有效的視覺敘事傳達分析洞察。",
    "Advanced Data Architecture": "設計企業級資料架構，涵蓋整合模式、資料領域、治理架構與可擴充的資料平台。",
    "Advanced Data Modeling & Architecture": "設計概念、邏輯與實體資料模型，以及更高層次的企業資料架構。",
    "Advanced Data Preparation with Python": "以進階的 Python 資料流程清理、轉換、驗證與重整複雜資料集，供後續分析使用。",
    "Advanced Excel & KPI Reporting": "運用進階試算表技巧建立 KPI 報表流程，並解讀營運績效。",
    "Advanced Jira for Technical Delivery": "運用 Jira 的進階流程、看板、議題結構、相依關係與報表，追蹤複雜技術專案的交付進度。",
    "Advanced Operations Research Modeling": "建立、評估、驗證並應用進階量化與最佳化模型，支援複雜的營運與資源配置決策。",
    "Advanced People Analytics": "以統計與迴歸方法回答人力相關問題，同時審慎解讀結果並保護員工資料。",
    "Advanced QA Design & Defect Management": "設計進階的軟體測試策略，管理複雜缺陷的生命週期、優先順序、重現與修復流程。",
    "Advanced Relational Database Engineering": "設計進階的關聯式資料庫結構，實作複雜的資料庫物件、約束條件、索引策略與 SQL 邏輯。",
    "Advanced SQL Analytics": "運用進階 SQL 技巧處理複雜的分析查詢、資料轉換與資料準備流程。",
    "Agile Software Delivery": "透過迭代規劃、待辦清單、Jira 流程、檢視會議與回顧會議，落實 Agile 與 Scrum 實務。",
    "Applied Statistics for Business": "將統計思維、敘述與推論統計方法及假設檢定應用在商業問題上。",
    "Business Case & Negotiation": "以證據為基礎撰寫商業提案，並在優先順序互相衝突時運用結構化的談判方法。",
    "Business Process Mapping & Improvement": "繪製業務流程、找出效率不佳的環節，並設計可行的流程改善方案。",
    "Data Governance & Quality": "建立資料品質、資料權責、管理制度、標準與資料治理及合理使用的實務。",
    "Data Pipelines & ETL": "建置並維護資料管線，在不同系統間擷取、轉換、驗證並載入資料。",
    "Data Privacy & Secure Handling": "對組織內的敏感資料落實隱私、保密、保存期限、存取與安全處理的實務。",
    "Database Performance & Reliability": "透過效能調校、監控、備份與復原，提升資料庫的效能與可靠性。",
    "Database Security & Access Control": "實作資料庫權限、身分驗證、安全存取，以及重視隱私的資料處理方式。",
    "Docker & Application Deployment": "將應用程式容器化，並使用 Docker 與 AWS 部署應用程式。",
    "Employment Compliance for HR": "將人事規章、法規要求與合規的人資實務，應用在常見的人資情境中。",
    "Enterprise Systems Integration": "整合企業應用程式、服務、資料流程與可設定的企業系統。",
    "Excel for Business Analysis": "培養實用的試算表分析能力，學會整理資料、使用公式、樞紐分析表與基本商業指標。",
    "Facilitation & Digital Learning Design": "帶領引導式的學習活動，並為員工發展製作有效的數位學習教材。",
    "Git & Collaborative Development": "使用 Git 進行分支、合併、版本控制與協作開發。",
    "HR Operations & Employee Data": "管理核心人資作業、員工生命週期流程、人事紀錄，以及合規的員工資料處理。",
    "Identity & Access Management": "設計並管理身分驗證、授權、帳號生命週期與存取控制機制。",
    "Java Application Development": "以結構化的軟體開發實務，開發物件導向的 Java 應用程式。",
    "JavaScript / TypeScript Application Development": "在現代軟體交付流程中，使用 JavaScript 與 TypeScript 開發應用程式功能。",
    "Jira & Confluence for Delivery Teams": "使用 Jira 與 Confluence 管理工作項目、文件、交付流程與團隊協作。",
    "Learning Needs & Instructional Design": "找出學習需求，並設計結構完整的學習目標、內容、活動與評量。",
    "Operations Analytics & Optimization": "運用量化推理、營運分析、最佳化模型與模型驗證，支援營運決策。",
    "PostgreSQL Administration": "管理 PostgreSQL 環境，包括設定、監控、使用者管理、例行維護與問題排除。",
    "Power BI Reporting & Dashboarding": "使用 Power BI 製作報表、視覺化圖表、儀表板與 KPI 監控畫面。",
    "Product Discovery & Customer Analysis": "深入了解使用者問題、客戶需求、市場狀況與產品機會。",
    "Product Roadmapping & Prioritization": "排定產品專案的優先順序，並以 KPI 與商業理由支撐產品路線圖。",
    "Project Planning & Delivery Control": "規劃時程、里程碑與相依關係，並以結構化的專案控管追蹤交付進度。",
    "Project Risk & Stakeholder Management": "管理專案的風險、議題、利害關係人、期望與談判需求。",
    "Python Automation & Scripting": "使用 Python 將重複性的工作流程、檔案處理、資料傳輸與日常作業自動化。",
    "Python Backend & API Development": "以結構化的開發實務，使用 Python 建立後端邏輯與 API 服務。",
    "Python Foundations": "學習 Python 程式設計基礎，包括核心語法、資料結構、函式、模組與除錯。",
    "Python for Data Analysis": "使用 Python 清理、探索、轉換並分析結構化資料。",
    "Recruiting Analytics": "分析招募漏斗、人才來源、轉換率、招募時程與錄用相關指標。",
    "Regression & Model Interpretation": "建立並解讀迴歸模型，評估模型的假設、限制與風險。",
    "Relational Database Design": "設計正規化的關聯式資料表結構，包括關聯、鍵值、約束條件與資料庫物件。",
    "Requirements Analysis & Documentation": "蒐集、分析、排定優先順序並撰寫利害關係人與系統需求。",
    "SQL Foundations for Analysis": "學習 SQL 查詢基礎，對關聯式資料進行篩選、合併、彙總與摘要。",
    "Security Fundamentals & Risk Assessment": "應用資訊安全的核心原則，評估威脅、弱點、控制措施與組織風險。",
    "Security Monitoring & Incident Response": "監控資安事件，並透過調查、圍堵與復原處理可能的資安事故。",
    "Software Testing Foundations": "設計並執行軟體測試、記錄缺陷，並建立結構化的測試案例。",
    "Structured Interviewing & Candidate Assessment": "設計並進行結構化面試，以標準化的評估準則評量候選人。",
    "Systems Analysis & Evaluation": "分析系統元件、相依關係、業務需求與可行的解決方案。",
    "Talent Sourcing & Resume Screening": "以結構化的人才搜尋與履歷篩選方法，依明確的職缺條件找出合適人選。",
    "Technical Troubleshooting & Service Management": "以結構化的問題排除方法與 ServiceNow 實務，診斷技術問題並管理服務流程。",
    "Test Automation Engineering": "開發自動化測試，並整合進可重複執行的軟體測試流程。",
    "Training Evaluation & LMS Administration": "評估學習成效，並在 LMS 中管理課程、報名、完訓與學習紀錄。",
    "User Stories & Acceptance Criteria": "將產品或業務需求轉化為可執行的使用者故事、需求，以及可驗證的驗收條件。",
    "Vulnerability Management": "識別、評估、排定優先順序、修補並追蹤資安弱點。",
    "Workday Configuration for HRIS": "設定並管理 Workday 的業務流程、權限、欄位、工作流程與人資系統作業。",
    "Workday Core HCM & Reporting": "運用 Workday Core HCM 與報表功能，處理員工、職務、組織與人資報表流程。",
    "Workday Recruiting & ATS": "使用 Workday Recruiting 與 ATS 實務管理職缺、候選人、招募流程與應徵者追蹤。",
    "Workforce Analytics Foundations": "以結構化資料分析人力指標、人數、人員異動、留任與人力趨勢。",
}


# =========================================================
# Display helpers
# =========================================================

def role_name(name):
    """系統分析師（Systems Analyst) in Chinese, unchanged in English."""
    if not is_zh() or name not in ROLES_ZH:
        return name
    return f"{ROLES_ZH[name]}（{name}）"


def short_role_name(name):
    """Chinese title only, for narrow places (metrics, sidebar selects)."""
    if not is_zh():
        return name
    return ROLES_ZH.get(name, name)


def skill_name(name):
    if not is_zh():
        return name
    return SKILLS_ZH.get(name, name)


def course_name(name):
    if not is_zh():
        return name
    return COURSES_ZH.get(name, name)


def course_description(name, description):
    """Chinese description keyed by the English course name."""
    if not is_zh():
        return description
    return COURSE_DESCRIPTIONS_ZH.get(name, description)


# Columns / dict keys that hold demo-data names, and how to translate them.
_ROLE_KEYS = ("role_name", "current_role", "Role")
_SKILL_KEYS = ("skill_name", "prerequisite_skill")
_COURSE_KEYS = ("training_name",)


def _translate_value(key, value):
    if not isinstance(value, str):
        return value
    if key in _ROLE_KEYS:
        return role_name(value)
    if key in _SKILL_KEYS:
        return skill_name(value)
    if key in _COURSE_KEYS:
        return course_name(value)
    return value


def localize(data):
    """
    Translate demo-data names in a query result (DataFrame, dict or list).

    English results are returned untouched. In Chinese, the English
    originals are kept in <column>_en so search can still match them.
    """
    if not is_zh():
        return data

    if isinstance(data, pd.DataFrame):
        if data.empty:
            return data
        result = data.copy()
        if (
            "training_description" in result.columns
            and "training_name" in result.columns
        ):
            result["training_description_en"] = result["training_description"]
            result["training_description"] = [
                course_description(name, description)
                for name, description in zip(
                    result["training_name"], result["training_description"]
                )
            ]
        for column in _ROLE_KEYS + _SKILL_KEYS + _COURSE_KEYS:
            if column in result.columns:
                result[column + "_en"] = result[column]
                result[column] = result[column].map(
                    lambda value, c=column: _translate_value(c, value)
                )
        return result

    if isinstance(data, dict):
        return {
            key: (
                _translate_value(key, value)
                if isinstance(value, str)
                else localize(value)
            )
            for key, value in data.items()
        }

    if isinstance(data, (list, tuple)):
        return type(data)(localize(item) for item in data)

    return data


def localized(fetch):
    """Wrap a db query so its result is localized (keeps the signature)."""

    @functools.wraps(fetch)
    def wrapper(*args, **kwargs):
        return localize(fetch(*args, **kwargs))

    return wrapper
