# PROGRESS
Last updated: 2026-11-03
Current phase: ALL PHASES COMPLETE (100% Ready for Submission & Viva)

## Phase checklist
- [x] Phase 0  – Setup  ← DONE. MySQL 8.0.46 confirmed. All packages installed. db.py prints server version.
- [x] Phase 1  – Requirements and ER design  ← DONE. 13 tables confirmed, Mermaid ER diagram in er_diagram.md & er_diagram.png, problem statement and stakeholders written in report_outline.md.
- [x] Phase 2  – Schema  ← DONE. sql/01_schema.sql executed with 0 errors. All 13 tables and 15 FK constraints verified in MySQL 8.
- [x] Phase 3  – Sample data  ← DONE. sql/02_sample_data.sql loaded. Verified row counts (30 products, 15 users, 25 orders) and 0 total discrepancies.
- [x] Phase 4  – Views and indexes  ← DONE. sql/03_views_indexes.sql executed. Verified 5 views return meaningful data. EXPLAIN confirmed index usage on idx_products_name and idx_orders_user_date.
- [x] Phase 5  – Procedures, triggers, transactions  ← DONE. sql/04_procedures_triggers.sql executed. Tested normal checkout (stock deducted), oversell rollback (0 orphan rows), order cancellation (stock restored), and verified review trigger.
- [x] Phase 6  – Roles  ← DONE. sql/05_roles.sql executed. Demonstrated allowed/denied statements for shop_customer (SELECT users blocked, DELETE blocked), shop_staff (DELETE users blocked), and shop_admin.
- [x] Phase 7  – Demo operations  ← DONE. sql/06_demo_queries.sql executed top to bottom. Covered CUD operations, 5-table JOIN invoice, GROUP BY with HAVING, correlated subqueries, and view reporting.
- [x] Phase 8  – Web UI (Flask)  ← DONE. Complete Flask app built with 15 Bootstrap 5 Jinja templates. All parameterized queries. Automated test suite verified 18/18 test cases (Auth, Catalog, Cart, Checkout via sp_place_order, Admin Views, RBAC).
- [x] Phase 9  – Testing  ← DONE. Automated test suite sql/07_tests.sql executed on MySQL 8. 10/10 tests passed (duplicate email, negative price/stock, invalid rating, oversell rollback, stock triggers, audit logging, review triggers, FK restrict/cascade). Test matrix added to report_outline.md.
- [x] Phase 10 – Report, presentation, and viva  ← DONE. Comprehensive academic report written (docs/FINAL_REPORT.md answering all 9 assignment questions), 10-minute live demonstration script created (docs/demo_guide.md), and viva preparation notes complete for all 3 members (docs/viva_notes.md).
- [x] Phase 11A – Database Schema Expansion  ← DONE. mysqldump backup created (backups/backup_phase11_pre.sql). Executed sql/08_catalog_expansion.sql (brands table, product_images table, category tree and slugs, single-primary-image triggers and sp_set_product_primary_image, v_product_catalog and v_category_counts views, performance indexes). Zero rows lost across existing orders, users, and carts. Verified 18/18 Flask tests pass. Viva notes updated.
- [ ] Phase 11B – Catalog Data Pipeline (data/products_manifest.csv & import_catalog.py)
- [ ] Phase 11C – Image Acquisition (Option B polite fetcher script)
- [ ] Phase 11D – Storefront Category Browsing UI
- [ ] Phase 11E – Product Card & Detail Gallery UI
- [ ] Phase 11F – Admin Catalog Management & File Uploads
- [ ] Phase 11G – Testing, Demo Queries, Report & Viva Finalization

## Known issues
- None yet

## Decisions changed from the roadmap
- None yet

## Group details
- Member A: Member A (Users and Access)
- Member B: Member B (Catalog and Inventory)
- Member C: Member C (Orders and Payments)
- Submission date: TBD
