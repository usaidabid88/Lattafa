# TASKS.md - Phase 11 Task Board

| Task ID | Description | Owner | Dependencies | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TASK-11A-AUDIT** | Audit 11A database schema, views, triggers, and idempotence | AUDITOR | None | DONE (AUDIT_11A.md PASS) |
| **TASK-11B-MANIFEST** | Create `data/products_manifest.csv` for 51 catalog checklist items | DATA | TASK-11A-AUDIT | DONE |
| **TASK-11B-IMPORT** | Create `app/scripts/import_catalog.py` (idempotent catalog loader) | DATA | TASK-11B-MANIFEST | DONE (AUDIT_11B.md PASS) |
| **TASK-11C-PLACEHOLDER**| Create `static/images/placeholder.svg` branded fallback | IMAGE | None | DONE |
| **TASK-11C-FETCHER** | Create `app/scripts/fetch_images.py` (Option B polite fetcher) | IMAGE | TASK-11B-MANIFEST | DONE |
| **TASK-11C-FETCH-EXEC** | Run image fetcher, download & optimize images (<300KB, max 1000px) | IMAGE | TASK-11C-FETCHER | DONE (images_report.json generated) |
| **TASK-11D-CATALOG-UI** | Homepage 5 category cards, category browsing, chips, filters & sorting | UI | TASK-11A-AUDIT | DONE |
| **TASK-11E-GALLERY-UI** | Aspect-ratio product cards & detail page image gallery | UI | TASK-11D-CATALOG-UI | DONE |
| **TASK-11F-ADMIN-MGMT** | Admin product form with brand/category dropdowns & image uploads | UI | TASK-11E-GALLERY-UI | DONE (AUDIT_11D_11F.md PASS) |
| **TASK-11G-SQL-TESTS** | Add Phase 11 tests to `sql/07_tests.sql` and `test_app.py` | AUDITOR | TASK-11B-IMPORT | DONE (15/15 SQL, 25/25 Web PASS) |
| **TASK-11G-DEMO-SQL** | Add Phase 11 demo queries in `sql/06_demo_queries.sql` | DOCS | TASK-11B-IMPORT | DONE (Section 9 validated) |
| **TASK-11G-DOCS** | Update ER diagram, FINAL_REPORT.md, and viva_notes.md | DOCS | TASK-11F-ADMIN-MGMT | DONE |
| **TASK-11G-E2E-AUDIT** | End-to-end verification and responsive screenshots (390px, 1280px) | AUDITOR | TASK-11F-ADMIN-MGMT | DONE (AUDIT_11G.md PASS) |
| **TASK-FINAL-REPORT** | LEAD compiles `MORNING_REPORT.md` | LEAD | ALL | IN_PROGRESS |
