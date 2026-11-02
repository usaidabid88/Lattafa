# Online Shopping System – DBMS CEP
**Mehran University of Engineering and Technology**
Department of Software Engineering | Semester 3 | Instructor: Aisha Ashfaque

## Project overview
A relational Online Shopping System built with MySQL 8 and Flask.
Solves the problem of small/medium sellers managing products, orders and customers in spreadsheets.

## Team
| Role | Module |
|------|--------|
| Member A | Users and Access |
| Member B | Catalog and Inventory |
| Member C | Orders and Payments |

## Quick start
```bash
# 1. Copy environment file and fill in your credentials
cp .env.example .env

# 2. Create virtual environment and install dependencies
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# 3. Test the database connection
python app/db.py

# 4. Create the database schema
mysql -u root -p < sql/01_schema.sql

# 5. Load sample data
mysql -u root -p online_shop < sql/02_sample_data.sql

# 6. Run the web app
python app/app.py
```

## Folder structure
```
DBS project/
├── PROGRESS.md
├── README.md
├── .env              ← real credentials (never commit)
├── .env.example      ← safe placeholder
├── requirements.txt
├── sql/
│   ├── 01_schema.sql
│   ├── 02_sample_data.sql
│   ├── 03_views_indexes.sql
│   ├── 04_procedures_triggers.sql
│   ├── 05_roles.sql
│   ├── 06_demo_queries.sql
│   └── 07_tests.sql
├── app/
│   ├── app.py
│   ├── db.py
│   ├── templates/
│   └── static/
└── docs/
    ├── er_diagram.png
    ├── viva_notes.md
    └── report_outline.md
```
