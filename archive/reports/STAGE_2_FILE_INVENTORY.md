# STAGE 2 FILE INVENTORY — Complete Repository Classification

**Project:** Online Shopping Database Management System (DBMS CEP)  
**Institution:** Mehran University of Engineering and Technology, Jamshoro  
**Phase:** Final Stabilization  
**Stage:** 2 of 4 (Repository Cleanup & Code Organization)  
**Execution Date:** 2026-11-04  
**Audit Baseline:** 529 total files inventoried across workspace (excluding `.git` and `venv`)  

---

## 1. Classification Taxonomy

| Classification | Meaning | Total Count |
| :--- | :--- | :---: |
| **KEEP** | Essential for live application runtime operation | 89 files |
| **KEEP — ACADEMIC** | Required for assignment evaluation, viva defense, or university grading | 24 files |
| **KEEP — DEVELOPMENT**| Essential for codebase maintenance, data pipelines, and local development | 12 files |
| **KEEP — TESTING** | Automated test suites, fixtures, and verification harnesses | 6 files |
| **KEEP — DEPLOYMENT** | Docker orchestration, WSGI configuration, and production initialization | 12 files |
| **ARCHIVE** | Historical milestone scripts and superseded phase reports | 15 files |
| **REMOVE CANDIDATE** | Verified obsolete, corrupt, or redundant files safe for removal | 1 file (0-byte backup) |
| **EXEMPT / TOOLING** | Agent skill definitions (`.agent/`) ignored by Git | 277 files |
| **PERSISTED STATIC** | Identical mirrored static assets for container volume mount parity | 52 files |

---

## 2. Comprehensive Inventory by Directory

### 2.1 Root Application & Configuration Files

| Relative Path | Classification | File Type | Purpose & Description | Runtime Ref | Test Ref | Docker Ref |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| `.env.example` | KEEP — DEPLOYMENT | Config | Template for environment variables (DB, Secret Key, SSL) | Yes | Yes | Yes |
| `.gitignore` | KEEP — DEPLOYMENT | Git | Version control exclusions (.env, venv, pycache, backups) | No | No | Yes |
| `Dockerfile` | KEEP — DEPLOYMENT | Docker | Debian Python 3.11-slim production container image definition | No | No | Yes |
| `docker-compose.yml` | KEEP — DEPLOYMENT | Docker | Stack orchestration for MySQL 8 and Flask web service | No | No | Yes |
| `gunicorn_config.py` | KEEP — DEPLOYMENT | Python | Production WSGI worker, timeout, and logging configuration | Yes | No | Yes |
| `requirements.txt` | KEEP — DEPLOYMENT | Config | Pinned Python production dependencies (Flask, PyMySQL, etc.)| Yes | Yes | Yes |
| `README.md` | KEEP — ACADEMIC | Markdown | Project overview, architecture, and examiner startup guide | No | No | No |
| `PROGRESS.md` | KEEP — ACADEMIC | Markdown | Project phase completion checklist (Phases 0–13A, Stages 1–3)| No | No | No |
| `TASKS.md` | KEEP — ACADEMIC | Markdown | Task board and milestone execution records | No | No | No |
| `DECISIONS.md` | KEEP — ACADEMIC | Markdown | Architecture decision records (ADRs) | No | No | No |
| `KNOWN_ISSUES.md` | KEEP — ACADEMIC | Markdown | Documented platform constraints (anti-bot scraping challenges)| No | No | No |
| `MORNING_REPORT.md` | ARCHIVE | Markdown | Historical autonomous overnight run report (Phases 12–13A) | No | No | No |
| `test_app.py` | KEEP — TESTING | Python | 49-test unified Flask E2E integration test suite | No | Yes | No |
| `test_secret_key.py` | KEEP — TESTING | Python | 7-test automated unit suite for secret key security policies | No | Yes | No |
| `test_ssl_db.py` | KEEP — TESTING | Python | 6-test automated unit suite for database TLS/SSL loader | No | Yes | No |

---

### 2.2 Core Application Source (`app/`)

| Relative Path | Classification | File Type | Purpose & Description | Runtime Ref | Test Ref | Docker Ref |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| `app/__init__.py` | KEEP | Python | Package marker enabling root WSGI resolution (`app.app:app`) | Yes | Yes | Yes |
| `app/app.py` | KEEP | Python | Main Flask backend application (routes, auth, cart, views) | Yes | Yes | Yes |
| `app/db.py` | KEEP | Python | Centralized database connection manager with TLS/SSL loader | Yes | Yes | Yes |
| `app/scripts/import_catalog.py`| KEEP — DEVELOPMENT| Python | Idempotent catalog importer for verified products | No | No | No |
| `app/scripts/fetch_images.py` | KEEP — DEVELOPMENT| Python | Phase 11C polite image acquisition pipeline (recovered) | No | No | No |
| `app/templates/*.html` (34 files)| KEEP | Jinja2 | Complete storefront, administrative, seller, and staff UI | Yes | Yes | Yes |
| `app/static/images/...` (52 files)| KEEP | Assets | Category specimens, product thumbnails, gallery photos | Yes | Yes | Yes |

---

### 2.3 SQL & Database Files (`sql/`)

| Relative Path | Classification | File Type | Purpose & Description | Runtime Ref | Test Ref | Docker Ref |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| `sql/init/01_schema.sql` | KEEP — DEPLOYMENT | SQL | DDL: 13 core domain tables, constraints, foreign keys | No | Yes | Yes |
| `sql/init/02_sample_data.sql` | KEEP — DEPLOYMENT | SQL | DML: Base seed data (products, categories, users, orders) | No | Yes | Yes |
| `sql/init/03_views_indexes.sql`| KEEP — DEPLOYMENT | SQL | Views and performance B-Tree indexes | No | Yes | Yes |
| `sql/init/04_procedures_triggers.sql`| KEEP — DEPLOYMENT| SQL | Transactional procedures (`sp_place_order`) and triggers | No | Yes | Yes |
| `sql/init/05_roles.sql` | KEEP — DEPLOYMENT | SQL | RBAC roles (`shop_admin`, `shop_staff`, `shop_customer`) | No | Yes | Yes |
| `sql/init/06_catalog_expansion.sql`| KEEP — DEPLOYMENT| SQL | Brands table, multi-image gallery, primary image trigger | No | Yes | Yes |
| `sql/init/07_srs_alignment.sql`| KEEP — DEPLOYMENT | SQL | Fiscal rates, returns lifecycle, support ticketing, SLA view | No | Yes | Yes |
| `sql/init/08_srs_alignment_fixes.sql`| KEEP — DEPLOYMENT| SQL | Enum expansion for simulated payment method | No | Yes | Yes |
| `sql/11_tests.sql` | KEEP — TESTING | SQL | Standalone 25-assertion database engine test harness | No | Yes | No |
| `sql/06_demo_queries.sql` | KEEP — ACADEMIC | SQL | Viva defense demonstration queries (Sections 1–9) | No | No | No |
| `sql/01_schema.sql` | ARCHIVE | SQL | Historical schema baseline (Phases 1–2) | No | No | No |
| `sql/02_sample_data.sql` | ARCHIVE | SQL | Historical sample data baseline (Phase 3) | No | No | No |
| `sql/03_views_indexes.sql`| ARCHIVE | SQL | Historical views and indexes baseline (Phase 4) | No | No | No |
| `sql/04_procedures_triggers.sql`| ARCHIVE | SQL | Historical procedures and triggers baseline (Phase 5) | No | No | No |
| `sql/05_roles.sql` | ARCHIVE | SQL | Historical roles baseline (Phase 6) | No | No | No |
| `sql/07_tests.sql` | ARCHIVE | SQL | Pre-Stage 1 database test suite (superseded by 11_tests.sql)| No | No | No |
| `sql/08_catalog_expansion.sql`| ARCHIVE | SQL | Historical Phase 11A catalog expansion script | No | No | No |
| `sql/09_srs_alignment.sql`| ARCHIVE | SQL | Historical Phase 12B schema alignment script | No | No | No |
| `sql/10_srs_alignment_fixes.sql`| ARCHIVE | SQL | Historical Phase 12C fix script | No | No | No |

---

### 2.4 Academic Documentation (`docs/`)

| Relative Path | Classification | File Type | Purpose & Description |
| :--- | :--- | :---: | :--- |
| `docs/FINAL_REPORT.md` | KEEP — ACADEMIC | Markdown | Comprehensive final submission report answering 9 CEP questions |
| `docs/demo_guide.md` | KEEP — ACADEMIC | Markdown | 10-minute live demonstration script for examiners |
| `docs/viva_notes.md` | KEEP — ACADEMIC | Markdown | Viva defense preparation questions and answers for all 3 members |
| `docs/traceability.csv` | KEEP — ACADEMIC | CSV | 63-requirement SRS Traceability Matrix (21 FR, 25 AC, 7 NFR, etc.) |
| `docs/srs_test_sheet.md` | KEEP — ACADEMIC | Markdown | 25 acceptance criteria verification test sheet (100% PASS) |
| `docs/er_diagram.md` | KEEP — ACADEMIC | Markdown | Entity-Relationship diagram specification (Mermaid format, 3NF) |
| `docs/er_diagram.png` | KEEP — ACADEMIC | Image | Rendered visual diagram of database schema (23 tables) |
| `docs/report_outline.md` | KEEP — ACADEMIC | Markdown | Original CEP report outline and project requirements specification |

---

### 2.5 Audit Reports & Evidence (`audits/` and Root)

| Relative Path | Classification | File Type | Purpose & Description |
| :--- | :--- | :---: | :--- |
| `AUDIT_REPORT.md` | KEEP — ACADEMIC | Markdown | Comprehensive initial independent project audit report |
| `AUDIT_REVIEW.md` | KEEP — ACADEMIC | Markdown | Independent review and challenge of AUDIT_REPORT.md |
| `STAGE_1_REPORT.md` | KEEP — DEVELOPMENT | Markdown | Stage 1 Critical Remediation implementation report |
| `STAGE_1_TEST_RESULTS.md` | KEEP — DEVELOPMENT | Markdown | Stage 1 initial test outputs (sanitized) |
| `STAGE_1_CHANGELOG.md` | KEEP — DEVELOPMENT | Markdown | Stage 1 itemized file modification log |
| `STAGE_1_5_REPORT.md` | KEEP — DEVELOPMENT | Markdown | Stage 1.5 Object reconciliation & secret hardening report |
| `STAGE_1_5_TEST_RESULTS.md`| KEEP — DEVELOPMENT| Markdown | Stage 1.5 detailed verification logs |
| `STAGE_1_5_CHANGELOG.md` | KEEP — DEVELOPMENT | Markdown | Stage 1.5 itemized file modification log |
| `audits/AUDIT_11*.md` (5 files)| KEEP — ACADEMIC | Markdown | Phase 11 milestone audit reports (11A, 11B, 11C, 11D_11F, 11G) |
| `audits/AUDIT_12*.md` (5 files)| KEEP — ACADEMIC | Markdown | Phase 12 milestone audit reports (12AB, 12C, 12D, 12E, 12F) |
| `audits/screenshots/*` (18 files)| KEEP — ACADEMIC | Images | High-resolution mobile (390px) & desktop (1280px) interface proofs |
| `audits/evidence/scan_secrets.py`| KEEP — TESTING | Python | Automated workspace secret scanning script |

---

### 2.6 Data & Specimen Assets (`data/`)

| Relative Path | Classification | File Type | Purpose & Description |
| :--- | :--- | :---: | :--- |
| `data/products_manifest.csv`| KEEP — DEVELOPMENT | CSV | Canonical dataset of 51 verified Pakistani retail catalog products |
| `data/images_report.json` | KEEP — DEVELOPMENT | JSON | Image acquisition audit log documenting anti-bot challenge falls |

---

### 2.7 Backups (`backups/`)

| Relative Path | Classification | File Type | Size | Status / Action |
| :--- | :--- | :---: | :---: | :--- |
| `backups/pre_stage1_recovery_point.sql` | KEEP — DEVELOPMENT | SQL | 205 KB | **KEEP** (Critical non-empty pre-remediation backup) |
| `backups/pre_12C_20261103_025942.sql` | ARCHIVE | SQL | 172 KB | **KEEP** (Pre-Phase 12C schema backup) |
| `backups/pre_phase12_20261103_025219.sql`| ARCHIVE | SQL | 127 KB | **KEEP** (Pre-Phase 12 schema backup) |
| `backups/pre_phase11_20261103_0147.sql` | ARCHIVE | SQL | 88 KB | **KEEP** (Pre-Phase 11 catalog expansion backup) |
| `backups/backup_phase11_pre.sql` | ARCHIVE | SQL | 74 KB | **KEEP** (Initial Phase 11 baseline backup) |
| `backups/pre_phase12_20261103_025204.sql`| REMOVE CANDIDATE | SQL | **0 bytes**| **REMOVED** (Zero-byte corrupt file; superseded by 025219) |

---

### 2.8 Static Asset Mirror (`static/`)

| Directory | Classification | Files | Purpose & Action |
| :--- | :--- | :---: | :--- |
| `static/images/` | PERSISTED STATIC | 52 files | Byte-for-byte SHA256 identical duplicate of `app/static/images/`. Retained to maintain parity between host filesystem volume mounts (`docker-compose.yml`) and internal Flask static serving. |

---

## 3. Inventory Summary

* **Total Files Inventoried:** 529
* **Total Files Retained:** 528
* **Total Files Safely Removed:** 1 (0-byte corrupt backup `backups/pre_phase12_20261103_025204.sql`)
* **Total Python Files:** 8 (100% active, syntax verified)
* **Total Jinja Templates:** 34 (100% valid, 0 compilation errors)
* **Total Production SQL Scripts:** 8 (`sql/init/01_*.sql` to `08_*.sql`)
* **Total Test Harnesses:** 4 (`test_app.py`, `test_secret_key.py`, `test_ssl_db.py`, `sql/11_tests.sql`)
