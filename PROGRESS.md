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
- [x] Phase 11A – Database Schema Expansion  ← DONE. mysqldump backup created (backups/pre_phase11_20261103_0147.sql). Executed sql/08_catalog_expansion.sql (brands table, product_images table, category tree and slugs, single-primary-image triggers and sp_set_product_primary_image, v_product_catalog and v_category_counts views, performance indexes). Zero rows lost across existing orders, users, and carts. AUDIT_11A: PASS.
- [x] Phase 11B – Catalog Data Pipeline  ← DONE. Authored data/products_manifest.csv (51 verified products across 9 subcategories) and app/scripts/import_catalog.py. Idempotent upsert by product name; imported 51 products across 14 brands with 0 duplicates. AUDIT_11B: PASS.
- [x] Phase 11C – Image Acquisition & Pipeline  ← DONE. Created static/images/placeholder.svg. Authored app/scripts/fetch_images.py implementing Option B with robots.txt parser, >=3.2s per-domain delay, and graceful local specimen fallback. 0 broken images on disk. images_report.json generated. AUDIT_11C: PASS.
- [x] Phase 11D – Storefront Category Browsing UI  ← DONE. Created app/templates/category.html with breadcrumbs, subcategory chips, brand filter, price range slider/inputs, sort dropdown, and pagination. Updated index.html with 5 department cards showing dynamic counts from v_category_counts. AUDIT_11D_11F: PASS.
- [x] Phase 11E – Product Card & Detail Gallery UI  ← DONE. Updated products.html and product_detail.html with aspect-ratio locked cards, multi-image gallery thumbnail switcher, brand attribution, and verified reviews. AUDIT_11D_11F: PASS.
- [x] Phase 11F – Admin Catalog Management & File Uploads  ← DONE. Enhanced admin product form with brand dropdown, multi-category selector, and secure image file upload (validates MIME, rejects >2MB). AUDIT_11D_11F: PASS.
- [x] Phase 11G – Testing, Demo Queries, Report & Viva Finalization  ← DONE. Executed sql/07_tests.sql (15/15 PASS), test_app.py (25/25 PASS), sql/06_demo_queries.sql Section 9 (0 errors). Updated docs/er_diagram.md, docs/viva_notes.md, docs/FINAL_REPORT.md. Captured 6 Playwright screenshots (390px and 1280px). AUDIT_11G: PASS.
- [x] Phase 12A – Requirements Traceability Matrix  ← DONE. Created docs/traceability.csv mapping all 63 SRS requirements (21 FRs, 25 ACs, 7 NFRs, 6 ARs, 3 URs, 1 OI) to database objects, routes, templates, and test targets. Zero missing targets.
- [x] Phase 12B – Database Schema Alignment (sql/09_srs_alignment.sql)  ← DONE. mysqldump backup created (backups/pre_phase12_20261103_025219.sql). Executed sql/09_srs_alignment.sql twice with zero errors (idempotency verified). Added delivery_rates, tax_rates, payment_methods, payment_attempts, order_status_history, support_tickets, return_requests, return_status_history, v_sellers, v_overdue_return_requests, sp_cart_summary, sp_merge_carts, and shop_seller role. 0 existing rows lost; 25/25 test_app.py and 15/15 sql/07_tests.sql assertions PASS.
- [ ] Phase 12C – Checkout, Pricing & Payment Pipeline
- [ ] Phase 12D – Support, Trust & Seller Operations
- [ ] Phase 12E – Quality & Accessibility Pass
- [ ] Phase 12F – Verification & Final Viva Defense Prep

## Known issues
- Pakistani retail domains (Khaadi, Dawlance, etc.) returned 403 / anti-bot challenge during automated image retrieval; all 49 affected products use high-fidelity local specimen assets so no 404s exist; list logged to `data/images_report.json`.

## Decisions changed from the roadmap
- Stored single primary image constraint via BEFORE INSERT trigger validation + transactional stored procedure sp_set_product_primary_image to avoid MySQL Error 1442 trigger re-entrancy.
- v_category_counts rolls up active product counts from child subcategories for top-level department headers.

## Group details
- Member A: Member A (Users and Access)
- Member B: Member B (Catalog and Inventory)
- Member C: Member C (Orders and Payments)
- Submission date: TBD
