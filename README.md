# WorkforceIQ

Skills intelligence, career mobility and strategic workforce planning, built with
Streamlit and SQLite. The app runs on synthetic demo data.

## Workspaces

- **Employee**: My Skills, Career Exploration (skill match, skill gaps with
  learning options, saved career interests), Learning Catalog
- **Manager**: Staffing for open and paused job openings (internal mobility
  candidates, readiness, staffing route)
- **HR / Workforce Planning**: aggregate workforce gaps, planned headcount,
  and internal learning coverage

## Project structure

```text
WorkforceIQ/
├── app/
│   ├── app.py                 # entry point
│   ├── db.py                  # all SQLite queries
│   └── views/                 # one file per page
├── database/
│   ├── schema.sql
│   ├── seed_*.sql
│   └── rebuild_db.py          # builds workforceiq.db from the SQL files
├── SQL/                       # reference queries
└── requirements.txt
```

## Run

```bash
pip install -r requirements.txt
python database/rebuild_db.py      # creates database/workforceiq.db
streamlit run app/app.py
```

`rebuild_db.py` options: `--dry-run` (check only), `--keep-interests`
(keep saved career interests from an existing database). An existing database is
backed up before it is replaced.

The workspace and employee selectors in the sidebar are for development only and
can later be replaced with authentication.
