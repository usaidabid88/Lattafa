# Master Repository Restructuring & Reorganization Report
**Project:** LUXE FRAGRANCE / Online Shopping System (MUET DBMS CEP)  
**Author:** Senior Software Architect & Repository Maintenance Specialist  
**Date:** November 8, 2026  
**Status:** Successfully Reorganized and Verified (100% Quality Gates Satisfied)  

---

## 1. Executive Summary

This report documents the comprehensive structural reorganization and cleanup of the **LUXE FRAGRANCE** perfume e-commerce repository. 

Over multiple phases of active feature development, domain transformation, and asset pipeline enhancements, the repository accumulated scattered markdown documents in the root directory, temporary test logs, prototyping cache files, unstructured SQL scripts, and mixed test files.

To prepare the codebase for **academic submission at Mehran University of Engineering and Technology (MUET)**, open-source presentation on GitHub, and long-term cloud deployment readiness, a systematic restructuring was executed following established Python, Flask, testing, documentation, and database conventions.

### Core Achievements
1. **Separation of Concerns**: Application code (`app/`), database scripts (`database/`), test suites (`tests/`), documentation (`docs/`), utility scripts (`scripts/`), and active data (`data/`) now reside in dedicated, single-responsibility directories.
2. **Root Cleanliness**: Root directory clutter was reduced from 36 files to strictly essential project-level entrypoints and configurations (`run.py`, `run_test_suite.py`, `README.md`, `requirements.txt`, `.gitignore`, `.env.example`, `Dockerfile`, `docker-compose.yml`, `gunicorn_config.py`).
3. **Zero Functionality Regression**: All 69 automated tests across 4 test suites pass with 100% success rate. Flask route dispatching, database connectivity, and the `/health` endpoint were verified live.
4. **100% Backward Compatibility**: Backward-compatible execution wrappers were placed in `app/scripts/`, and root-level test runners maintain seamless compatibility for existing development workflows.
5. **Security & History Preservation**: No secrets were exposed; `.gitignore` was updated with industry-standard patterns; historical materials and backups were safely archived in `archive/` and `backups/`.

---

## 2. Before and After Structure

### Original Organization (Pre-Restructuring)
```text
PROJECT_ROOT/
├── .agent/
├── .work/
├── __pycache__/
├── app/
│   ├── app.py
│   ├── db.py
│   ├── __init__.py
│   ├── data/
│   │   └── PERFUME_IMAGE_MANIFEST.json
│   ├── scripts/
│   │   ├── check_endpoints.py
│   │   ├── generate_perfume_assets.py
│   │   ├── generate_perfume_catalog.py
│   │   ├── generate_sql_migration.py
│   │   └── import_catalog.py
│   ├── static/
│   └── templates/
├── archive/
├── audits/                      <-- Redundant separate audit folder
│   ├── evidence/
│   ├── screenshots/
│   └── AUDIT_11A.md ... AUDIT_13A.md (11 files)
├── backups/
├── data/
│   ├── BATCH_ASSIGNMENTS.json
│   ├── images_report.json
│   ├── PERFUME_IMAGE_MANIFEST.json
│   └── products_manifest.csv
├── design-system/
├── docs/                        <-- Flat, unorganized documentation
│   └── [12 scattered files]
├── scratch/                     <-- Prototype test renders
├── sql/                         <-- Flat and fragmented SQL scripts
│   ├── init/
│   ├── init_perfume/
│   └── [12 root SQL files]
├── static/
│   └── Img/                     <-- Redundant unextracted zip file
├── venv/
├── [6 .log files: .cleanup-flask.*, .flask-live.*, .flask-preview.*]
├── [16 scattered root .md files]
├── PERFUME_CATALOG_DATA.csv     <-- Active catalog CSV at root
├── test_app.py                  <-- Tests in root
├── test_perfume_suite.py        <-- Tests in root
├── test_secret_key.py           <-- Tests in root
├── test_ssl_db.py               <-- Tests in root
├── run_test_suite.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── gunicorn_config.py
└── README.md
```

### Final Organization (Post-Restructuring)
```text
PROJECT_ROOT/
├── app/                        # Application package
│   ├── app.py                  # Core Flask application & view routing
│   ├── db.py                   # Centralized PyMySQL & TLS helper
│   ├── __init__.py             # Application factory package marker
│   ├── data/                   # Runtime data (manifests)
│   ├── scripts/                # Backward-compatibility shims
│   ├── static/                 # Static assets (mirrored with root static/)
│   └── templates/              # Jinja2 HTML templates
│
├── database/                   # Structured relational database assets
│   ├── schema/                 # DDL: 01_schema.sql, 03_views, 04_procedures, 05_roles
│   ├── seeds/                  # Seed datasets: 02_sample, 08_catalog, 12_perfume
│   ├── migrations/             # Schema migrations: 09_srs_alignment, 10_fixes
│   ├── queries/                # Demonstrations & queries: 06_demo, 07_tests, 11_tests
│   ├── init_perfume/           # Sequential automated container bootstrap (01 to 09)
│   ├── init_legacy/            # Preserved pre-perfume baseline initialization
│   └── README.md               # Detailed database documentation
│
├── tests/                      # Automated test harness
│   ├── unit/                   # Unit suites: test_secret_key.py, test_ssl_db.py
│   ├── integration/            # Integration suites: test_app.py, test_perfume_suite.py
│   ├── conftest.py             # Pytest fixtures and environment setup
│   ├── run_test_suite.py       # Direct test package runner
│   └── __init__.py
│
├── docs/                       # Structured documentation hierarchy
│   ├── architecture/           # DECISIONS.md, FINAL_PROJECT_STRUCTURE.md
│   ├── database/               # PERFUME_DATABASE_DESIGN.md, er_diagram.md/.png
│   ├── development/            # demo_guide.md
│   ├── deployment/             # FINAL_DEPLOYMENT_READINESS.md
│   ├── audits/                 # AUDIT_REPORT.md, AUDIT_REVIEW.md, AUDIT_11A-13A, evidence/
│   ├── reports/                # Academic reports, test results, SRS traceability
│   └── project/                # PERFUME_CATALOG.md, PROGRESS.md, TASKS.md, changelog
│
├── scripts/                    # Standalone utility & maintenance scripts
│   ├── database/               # generate_sql_migration.py, import_catalog.py
│   ├── development/            # check_endpoints.py
│   └── maintenance/            # generate_perfume_assets.py, generate_perfume_catalog.py
│
├── data/                       # Active dataset files
│   ├── PERFUME_CATALOG_DATA.csv# Curated 100-perfume catalog
│   ├── PERFUME_IMAGE_MANIFEST.json
│   ├── BATCH_ASSIGNMENTS.json
│   ├── images_report.json
│   └── products_manifest.csv
│
├── static/                     # Storefront static assets (CSS, JS, images, contact sheet)
├── design-system/              # Design specifications and theme guidelines
├── archive/                    # Preserved historical materials and legacy assets
├── backups/                    # Point-in-time database snapshots and recovery points
├── .env                        # Local secrets (git-ignored)
├── .env.example                # Sanitized environment template
├── .gitignore                  # Standard exclusion rules
├── docker-compose.yml          # Container orchestration (updated to database/init_perfume)
├── Dockerfile                  # Production container definition
├── gunicorn_config.py          # Production WSGI server configuration
├── requirements.txt            # Dependency manifest
├── run.py                      # Primary application entrypoint
├── run_test_suite.py           # Master automated test harness entrypoint
└── README.md                   # Comprehensive authoritative project documentation
```

---

## 3. File Movement Register

| Original Path | New Path | Category | Reason / Responsibility |
|---|---|---|---|
| `PERFUME_CATALOG_DATA.csv` | `data/PERFUME_CATALOG_DATA.csv` | Active Data | Consolidates catalog datasets within `data/`. |
| `sql/01_schema.sql` | `database/schema/01_schema.sql` | Database | Baseline table definitions and constraints. |
| `sql/03_views_indexes.sql` | `database/schema/03_views_indexes.sql` | Database | Reporting views and performance indexes. |
| `sql/04_procedures_triggers.sql` | `database/schema/04_procedures_triggers.sql` | Database | Stored procedures and transactional audit triggers. |
| `sql/05_roles.sql` | `database/schema/05_roles.sql` | Database | RBAC user privileges and database roles. |
| `sql/02_sample_data.sql` | `database/seeds/02_sample_data.sql` | Database | Baseline seed accounts and inventory. |
| `sql/08_catalog_expansion.sql` | `database/seeds/08_catalog_expansion.sql` | Database | Extended catalog baseline seeds. |
| `sql/12_perfume_transformation.sql` | `database/seeds/12_perfume_transformation.sql` | Database | 100 genuine perfume products & olfactory notes. |
| `sql/09_srs_alignment.sql` | `database/migrations/09_srs_alignment.sql` | Database | Schema evolution (tracking, returns, support). |
| `sql/10_srs_alignment_fixes.sql` | `database/migrations/10_srs_alignment_fixes.sql` | Database | Procedure parameter fixes and SLA views. |
| `sql/06_demo_queries.sql` | `database/queries/06_demo_queries.sql` | Database | Analytical and KPI demonstration queries. |
| `sql/07_tests.sql` | `database/queries/07_tests.sql` | Database | Schema integrity and constraint tests. |
| `sql/11_tests.sql` | `database/queries/11_tests.sql` | Database | SRS compliance and audit verification queries. |
| `sql/init/` | `database/init_legacy/` | Database | Preserved pre-perfume initialization scripts. |
| `sql/init_perfume/` | `database/init_perfume/` | Database | Docker container sequential initialization scripts. |
| `test_secret_key.py` | `tests/unit/test_secret_key.py` | Testing | Unit tests verifying Flask secret key security gates. |
| `test_ssl_db.py` | `tests/unit/test_ssl_db.py` | Testing | Unit tests verifying PyMySQL TLS/SSL enforcement. |
| `test_app.py` | `tests/integration/test_app.py` | Testing | Unified E2E regression suite (49 test cases). |
| `test_perfume_suite.py` | `tests/integration/test_perfume_suite.py` | Testing | Perfume domain and olfactory pyramid suite (7 tests). |
| `AUDIT_REPORT.md` | `docs/audits/AUDIT_REPORT.md` | Documentation | Comprehensive repository and code quality audit. |
| `AUDIT_REVIEW.md` | `docs/audits/AUDIT_REVIEW.md` | Documentation | Quality review and remediation register. |
| `audits/AUDIT_*.md` (11 files) | `docs/audits/` | Documentation | Phase-specific audit records (Phases 11A–13A). |
| `audits/evidence/` | `docs/audits/evidence/` | Documentation | Diagnostic scripts and audit logs. |
| `audits/screenshots/` | `docs/audits/screenshots/` | Documentation | Visual audit verification captures. |
| `DECISIONS.md` | `docs/architecture/DECISIONS.md` | Documentation | Architectural Decision Records (ADRs). |
| `FINAL_PROJECT_STRUCTURE.md` | `docs/architecture/FINAL_PROJECT_STRUCTURE.md` | Documentation | Structural architectural blueprints. |
| `PERFUME_DATABASE_DESIGN.md` | `docs/database/PERFUME_DATABASE_DESIGN.md` | Documentation | Schema design specifications for perfume domain. |
| `docs/er_diagram.md` & `.png` | `docs/database/` | Documentation | Visual entity relationship diagrams. |
| `FINAL_DEPLOYMENT_READINESS.md` | `docs/deployment/FINAL_DEPLOYMENT_READINESS.md` | Documentation | Production hosting and operational audit. |
| `docs/demo_guide.md` | `docs/development/demo_guide.md` | Documentation | Examiner demonstration guide and walkthrough. |
| `docs/FINAL_REPORT.md` | `docs/reports/FINAL_REPORT.md` | Documentation | Comprehensive CEP final report. |
| `MORNING_REPORT.md` | `docs/reports/MORNING_REPORT.md` | Documentation | Daily milestone progress summaries. |
| `PERFUME_TRANSFORMATION_FINAL_REPORT.md` | `docs/reports/PERFUME_TRANSFORMATION_FINAL_REPORT.md` | Documentation | Transformation delivery milestone report. |
| `PERFUME_TRANSFORMATION_TEST_RESULTS.md` | `docs/reports/PERFUME_TRANSFORMATION_TEST_RESULTS.md` | Documentation | Automated test execution matrix. |
| `docs/Phase 11 ... .md` | `docs/reports/` | Documentation | Historical phase delivery document. |
| `docs/Phase 12 and 13 ... .md` | `docs/reports/` | Documentation | Historical SRS alignment report. |
| `docs/report_outline.md` | `docs/reports/report_outline.md` | Documentation | Academic report planning outline. |
| `docs/srs_test_sheet.md` | `docs/reports/srs_test_sheet.md` | Documentation | Requirements traceability verification sheet. |
| `docs/traceability.csv` | `docs/reports/traceability.csv` | Documentation | Requirement to test matrix mapping. |
| `KNOWN_ISSUES.md` | `docs/project/KNOWN_ISSUES.md` | Documentation | Tracked project defect register. |
| `STOREFRONT_KNOWN_ISSUES.md` | `docs/project/STOREFRONT_KNOWN_ISSUES.md` | Documentation | UI/UX known considerations and workarounds. |
| `PERFUME_CATALOG.md` | `docs/project/PERFUME_CATALOG.md` | Documentation | 100-fragrance catalog specifications. |
| `PERFUME_TRANSFORMATION_CHANGELOG.md` | `docs/project/PERFUME_TRANSFORMATION_CHANGELOG.md` | Documentation | Detailed chronological changelog. |
| `PERFUME_TRANSFORMATION_PLAN.md` | `docs/project/PERFUME_TRANSFORMATION_PLAN.md` | Documentation | Domain transformation implementation plan. |
| `PROGRESS.md` | `docs/project/PROGRESS.md` | Documentation | Work package progress tracking log. |
| `TASKS.md` | `docs/project/TASKS.md` | Documentation | Task breakdown and backlog management. |
| `docs/DBMS_CEP.docx` | `docs/project/DBMS_CEP.docx` | Documentation | Academic assignment specification. |
| `docs/Online Shopping ... .docx` | `docs/project/` | Documentation | Original CEP roadmap document. |
| `docs/viva_notes.md` | `docs/project/viva_notes.md` | Documentation | Examiner defense preparation notes. |

---

## 4. Removed Files & Verification

The following files were identified as temporary development artifacts or generated logs and safely removed:

| File / Directory | Nature | Justification for Removal |
|---|---|---|
| `.cleanup-flask.err.log` | Ephemeral Log | Standard error from background cleanup Flask process. |
| `.cleanup-flask.out.log` | Ephemeral Log | Standard output from background cleanup Flask process. |
| `.flask-live.err.log` | Ephemeral Log | Standard error from background live Flask server run. |
| `.flask-live.out.log` | Ephemeral Log | Standard output from background live Flask server run. |
| `.flask-preview.err.log` | Ephemeral Log | Standard error from background preview server run. |
| `.flask-preview.out.log` | Ephemeral Log | Standard output from background preview server run. |
| `scratch/` | Temporary Directory | Prototyping renders generated during silhouette testing; active 100-perfume assets are permanently stored in `static/images/products/`. |
| `__pycache__/` and `*.pyc` | Bytecode Cache | Auto-generated Python bytecode files safely removed; recreated on execution. |

---

## 5. Archived Files

| File / Item | Archive Destination | Justification for Archival |
|---|---|---|
| `static/Img/Refine perfume storefront UI, restore images, verify navigation.zip` | `archive/legacy-marketplace-assets/` | Historical asset bundle provided during earlier storefront enhancement; all required assets were already extracted and integrated into `static/images/`. Archiving frees `static/` from unextracted archives while preserving history. |
| `sql/init/` | `database/init_legacy/` | Original electronics store initialization scripts kept for regression reference and historical auditability. |

---

## 6. Configuration & Path Changes

1. **`docker-compose.yml`**:
   - Updated database volume mount:
     - Old: `./sql/init_perfume:/docker-entrypoint-initdb.d:ro`
     - New: `./database/init_perfume:/docker-entrypoint-initdb.d:ro`
2. **`data/PERFUME_CATALOG_DATA.csv` Resolution**:
   - `scripts/maintenance/generate_perfume_assets.py`: Configured to prioritize `data/PERFUME_CATALOG_DATA.csv` with root fallback.
   - `scripts/maintenance/generate_perfume_catalog.py`: Updated to write output to `data/PERFUME_CATALOG_DATA.csv` and `docs/project/PERFUME_CATALOG.md`.
   - `scripts/database/generate_sql_migration.py`: Updated to read `data/PERFUME_CATALOG_DATA.csv` and write to `database/seeds/12_perfume_transformation.sql`.
3. **Test Suite Module Discovery**:
   - `run_test_suite.py`: Updated imports to discover tests from `tests.integration` and `tests.unit`.
   - `tests/run_test_suite.py`: Created as an equivalent package runner within `tests/`.
   - `tests/conftest.py`: Added standard pytest fixtures and session-wide testing isolation configuration.
   - Individual test modules (`test_app.py`, `test_perfume_suite.py`, `test_secret_key.py`, `test_ssl_db.py`): Path calculations adjusted to dynamically resolve project root (`os.path.join(os.path.dirname(__file__), '..', '..')`).
4. **Primary Entrypoint**:
   - `run.py`: Created at the repository root as the canonical development entry point, executing Flask with environment configuration loaded from `.env`.
5. **`.gitignore` Expansion**:
   - Added standard ignore patterns for `scratch/`, `*.log`, `.*.log`, coverage artifacts, build artifacts, and IDE temporary files.

---

## 7. Testing Results

All 69 automated test cases across 4 test suites were executed post-restructuring using `python run_test_suite.py`:

```text
========================================================
  EXECUTING COMPREHENSIVE PROJECT TEST HARNESS
  Target Database: online_shop_perfume_test
========================================================

--- SUITE 1: Unified Core E2E Regression Suite (test_app.py) ---
  [PASS] Test Database Isolation (SG-05) 
  [PASS] CSRF Gate: POST without token rejected (SG-01/02) 
  [PASS] CSRF Gate: POST with invalid token rejected (SG-02) 
  [PASS] GET / (Homepage) 
  [PASS] GET /products 
  [PASS] GET /products?q=Samsung 
  [PASS] GET /product/1 
  [PASS] GET /login 
  [PASS] POST /login (Customer Auth) 
  [PASS] POST /cart/add (Auth User) 
  [PASS] GET /cart (Auth User) 
  [PASS] GET /checkout (Auth User) 
  [PASS] POST /checkout (Atomic Order Placement) 
  [PASS] GET /my-orders 
  [PASS] RBAC: Customer denied /admin (302 Redirect) 
  [PASS] POST /login (Admin Auth) 
  [PASS] GET /admin 
  [PASS] GET /admin/products 
  [PASS] GET /admin/orders 
  [PASS] GET /admin/reports (Views Integration) 
  [PASS] POST /admin/order/status 
  [PASS] GET /category/laptops-computers (11D) 
  [PASS] GET /category/women-unstitched (11D) 
  [PASS] GET /category/laptops-computers?sort=price_asc (11D) 
  [PASS] GET /category/laptops-computers?brand=Dell (11D) 
  [PASS] GET /product/1 Gallery (11E) 
  [PASS] Admin Upload Format Check (11F) 
  [PASS] Admin Upload Size Check (11F) 
  [PASS] GET /health probe returns 200 JSON 
  [PASS] GET /privacy renders successfully 
  [PASS] GET /terms renders successfully 
  [PASS] GET /returns-policy renders successfully 
  [PASS] POST /cart/add (Guest) allows adding without auth 
  [PASS] GET /cart (Guest) calculates pricing via sp_cart_summary 
  [PASS] POST /checkout (Guest Order Placement) completes via sp_place_guest_order 
  [PASS] POST /checkout (Simulated Payment) routes to payment gateway sandbox 
  [PASS] POST /payment/process (Fail outcome) logs attempt and routes to payment recovery 
  [PASS] POST /payment/switch-cod switches method to COD and confirms order 
  [PASS] GET /orders/<id>/track displays live trigger audit timeline 
  [PASS] POST /support submits customer support ticket 
  [PASS] GET /staff/tickets renders staff ticket queue 
  [PASS] GET /admin/sellers renders seller verification dashboard 
  [PASS] POST /admin/sellers/<id>/verify toggles seller verification status 
  [PASS] POST /orders/<id>/return lodges customer return claim 
  [PASS] GET /seller/returns displays seller return claims queue 
  [PASS] GET /admin/returns/overdue displays v_overdue_return_requests SLA view 
  [PASS] GET /admin dashboard renders v_abandoned_carts table 
  [PASS] Custom 404 error page renders without leaking stack trace 
  [PASS] Cart Merge on Login (Guest cart items transferred to user cart) 
  TOTAL RESULTS: 49 PASSED, 0 FAILED

--- SUITE 2: Perfume Domain Transformation Suite (test_perfume_suite.py) ---
  test_01_database_count: Verify exactly 100 perfumes in product_perfume_details ... ok
  test_02_all_17_mandatory_fragrances_present: Verify 17 mandatory fragrances ... ok
  test_03_homepage_sections: Verify homepage renders all luxury sections ... ok
  test_04_collections_hubs: Verify collections directory & landing pages ... ok
  test_05_gender_and_curation_routes: Verify gender hubs (/men, /women, /unisex) ... ok
  test_06_faceted_filtering: Verify faceted filters and sorting ... ok
  test_07_product_detail_olfactory_pyramid: Verify olfactory pyramid notes ... ok
  TOTAL RESULTS: 7 PASSED, 0 FAILED

--- SUITE 3: Secret Key Security Suite (test_secret_key.py) ---
  test_local_dev_empty_key_generates_ephemeral ... ok
  test_local_dev_with_custom_key ... ok
  test_production_missing_secret_key_raises_error ... ok
  test_production_placeholder_secret_key_raises_error ... ok
  test_production_short_secret_key_raises_error ... ok
  test_production_valid_secret_key_succeeds ... ok
  test_testing_environment_isolated_key ... ok
  TOTAL RESULTS: 7 PASSED, 0 FAILED

--- SUITE 4: SSL & Database Connectivity Suite (test_ssl_db.py) ---
  test_database_connection_to_test_db ... ok
  test_local_connection_no_ssl_default ... ok
  test_missing_ca_certificate_raises_file_not_found ... ok
  test_production_local_host_allowed_without_ssl ... ok
  test_production_remote_host_without_ssl_raises_error ... ok
  test_valid_ca_certificate_loads_ssl_dict ... ok
  TOTAL RESULTS: 6 PASSED, 0 FAILED

========================================================
  ALL TEST SUITES SUMMARY: 69 TESTS EXECUTED
  Core E2E Regression:      PASSED (49/49)
  Perfume Transformation:  PASSED (7/7)
  Secret Key Security:     PASSED (7/7)
  SSL Database Config:     PASSED (6/6)
  OVERALL HARNESS VERDICT: ALL TESTS PASSED (100%)
========================================================
```

---

## 8. Regression Verification

| Area | Verification Method | Status | Notes |
|---|---|---|---|
| **Flask Route Dispatching** | Live test client request to `/` and `/health` | Verified (200 OK) | Homepage rendered 102.6 KB HTML payload; health probe returned status JSON. |
| **Olfactory Pyramids** | Test suite `test_perfume_suite.py` | Verified (Pass) | Verified top/heart/base note rendering on product detail pages. |
| **Catalog Count** | Database query against `v_perfume_catalog` | Verified (100/100) | 100 genuine perfumes confirmed in database. |
| **Transactional Checkout** | Test suite `test_app.py` | Verified (Pass) | Atomic checkout verified for both authenticated shoppers and guest sessions. |
| **Security Gates** | Test suites `test_secret_key.py`, `test_ssl_db.py` | Verified (Pass) | CSRF rejection, production secret key enforcement, and TLS verification confirmed. |
| **Template URL Resolution** | `scripts/development/check_endpoints.py` | Verified (Pass) | 100% of all `url_for` references across all Jinja2 templates resolve to active view endpoints. |

---

## 9. Remaining Issues & Technical Notes

- **Zero Blocking Issues**: The reorganization is complete, fully tested, and verified.
- **Development vs. Production Database**: Local developers should ensure both `online_shop_perfume_dev` and `online_shop_perfume_test` exist in MySQL before executing the test harness. Instructions are clearly documented in `database/README.md` and `README.md`.
- **Legacy Sample Data in Test Database**: The test database intentionally preserves the pre-transformation sample data records (products 1–80) because regression test cases in `tests/integration/test_app.py` specifically validate legacy search queries (`/products?q=Samsung`, `/category/laptops-computers`, `/product/1`). This was deliberately maintained to guarantee 100% backward compatibility.

---

## 10. Final Assessment

**Classification: Successfully Reorganized and Verified**

The repository has been restructured into an industry-standard, professional architecture. All application source code, database scripts, tests, datasets, and documentation are cleanly partitioned into single-responsibility hierarchies. All 69 tests pass, zero regressions were introduced, and the codebase is primed for university presentation, peer review, and containerized deployment.
