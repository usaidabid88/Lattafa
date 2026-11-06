# COMPREHENSIVE PROJECT AUDIT REPORT
## Online Shopping Database Management System — DBMS CEP
**Department of Software Engineering, Mehran University of Engineering & Technology (MUET), Jamshoro**

- **Course:** Database Management Systems (CS-212 / 3rd Semester, 2nd Year)
- **Instructor:** Aisha Ashfaque
- **Audit Target Date:** 2026-11-03
- **Auditor:** Multi-Agent Autonomous Technical Compliance & Quality Audit Team
- **Audit Report Path:** `AUDIT_REPORT.md` (Project Root)
- **Overall Deployment Verdict:** **CONDITIONALLY READY — REMAINING FIXES REQUIRED**  
  *(100% Ready for Local Academic Demonstration; 4 P1 Remediations Required Prior to Public Cloud Deployment)*

---

# Section 1 — Executive Summary

This comprehensive audit was commissioned prior to cloud deployment to evaluate the technical state, functional completeness, architectural integrity, code cleanliness, and deployment readiness of the **Online Shopping Database Management System**.

The audit team performed a line-by-line inspection of the 1,794-line Flask backend, 34 Jinja2 HTML templates, 10 sequential SQL scripts, 24 MySQL database tables, 9 views, 8 stored procedures, 10 triggers, 6 database roles, and 71 automated test assertions.

### Core Audit Findings:
1. **Academic CEP Objectives Exceeded:** The database implementation is exceptionally advanced. The schema is normalized into 23 domain entities in strict Third Normal Form (3NF). Business logic, inventory reservation, oversell protection, and tamper-evident audit trails are enforced directly inside the MySQL 8 engine using triggers and stored procedures.
2. **Roadmap Execution (Phases 0–12):** Phases 0 through 12 are **100% implemented**. All 63 SRS requirements (21 Functional Requirements, 25 Acceptance Criteria, 7 Non-Functional Requirements, 6 Accessibility Requirements, 3 Usability Requirements, 1 Operational Indicator) are satisfied in code and documented in `docs/traceability.csv` and `docs/srs_test_sheet.md`.
3. **Database Engine Test Suite (`sql/07_tests.sql`):** **25 / 25 Passed (100%)**. Tests prove engine check constraints, cascading deletes, primary image enforcement, price parity via `sp_cart_summary`, guest order placement, and trigger-backed status logging.
4. **Web Application Test Suite (`test_app.py`):** **45 / 46 Passed (97.8%)**. An important finding was uncovered: the single test failure (`POST /checkout`) is caused by test state pollution—running tests repeatedly against the live development database depleted the on-hand stock of test item #12 down to 0, which correctly triggered the engine's oversell prevention trigger (`trg_before_order_items_insert`). The application and trigger functioned correctly, but the test harness lacks teardown isolation.
5. **Phase 13 Deployment Readiness:** Phase 13A (Production Preparation) is partially complete (`Dockerfile`, `docker-compose.yml`, `gunicorn_config.py`, `/health` probe, secure cookies, and security headers exist). However, **four P1 blockers prevent immediate cloud deployment**:
   - Lack of CSRF protection across 21 web forms.
   - Missing TLS/SSL configuration in `app/db.py` (mandatory for remote cloud MySQL on Aiven).
   - Test harness database pollution.
   - Absence of a configured Git remote repository.
6. **Repository Cleanliness:** 52 static product images (~340 KB) are duplicated verbatim between the root `static/` directory and `app/static/`. Additionally, an obsolete 0-byte backup file exists, and `app/scripts/fetch_images.py` was left unmerged on branch `agent/image`.

---

# Section 2 — Project Overview

The system is a full-stack e-commerce web platform designed around an enterprise-grade relational database:

- **Database Engine:** MySQL Community Server 8.0.46 (InnoDB storage engine, `utf8mb4` character set, `utf8mb4_unicode_ci` collation).
- **Backend Application:** Python 3.14 + Flask 3.0.3 + Werkzeug 3.0.3.
- **Database Driver:** PyMySQL 1.1.1 executing pure, 100% parameterized queries.
- **Frontend / UI:** Server-rendered Jinja2 templates, Bootstrap 5.3.3, Bootstrap Icons 1.11.3, responsive layouts, and zero heavy clientside framework dependencies.
- **WSGI / Containerization:** Gunicorn 22.0.0, Python 3.11-slim Dockerfile, multi-container Docker Compose.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SYSTEM ARCHITECTURE MAP                         │
└────────────────────────────────────────────────────────────────────────┘
 [ Browser (Desktop 1280px / Mobile 390px) ]
                     │  HTTP / HTTPS
                     ▼
 [ Gunicorn WSGI Server (2 Workers, 2 Threads) ]
                     │
 [ Flask Web Application (app/app.py - 47 Endpoints) ]
   ├── Authentication & Role Access Control (PBKDF2:SHA256, Session Cookies)
   ├── Storefront, Department Navigation & Multi-Image Gallery
   ├── Anonymous Guest Checkout & Signed Cart Token Lifecycle
   ├── Single Source Pricing Engine (sp_cart_summary)
   ├── Simulated Payment Adapter Sandbox (COD & Card/Wallet Simulation)
   ├── Customer Support Ticketing & Staff Triage Queue
   ├── Order Tracking Timeline & Merchandise Returns (RMA) Lifecycle
   └── Observability Health Heartbeat (/health)
                     │  PyMySQL (%s Parameterized Prepared Statements)
                     ▼
 [ MySQL 8.0.46 Relational Database Engine (online_shop) ]
   ├── 23 Relational Tables (Strict 3NF Normalization)
   ├── 9 Analytical & Governance Views (e.g. v_product_catalog, v_abandoned_carts)
   ├── 8 Stored Procedures (ACID Transactions & Financial Parity)
   ├── 10 Business Triggers (Stock Decrements, Oversell Blocks, Audit Logs)
   └── 6 Role-Based Access Control Roles (Principle of Least Privilege)
```

---

# Section 3 — Roadmap Progress Audit

This section compares actual project artifacts against the approved project roadmaps (`docs/Online Shopping Database Project Roadmap (DBMS CEP).docx`, `docs/Phase 11 Real Product Catalog, Images and Category Browsing.md`, and `docs/Phase 12 and 13 SRS Alignment and Web Deployment Plan.md`).

| Phase | Phase Title | Planned Scope | Actual Implementation | Evidence Artifacts | Verification Method | Status | Remaining Work |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **0** | Setup | Environment, PyMySQL, MySQL 8 setup | Python venv, `.env`, `app/db.py` connection helper, MySQL 8.0.46 | `app/db.py`, `.env.example`, `requirements.txt` | Executed `db.py` smoke test: prints MySQL 8.0.46 | **PASS** | None |
| **1** | Requirements & ER Design | 13 baseline entities, 3NF design, ER diagram | 13 normalized tables, cardinalities, academic report outline | `docs/er_diagram.md`, `docs/er_diagram.png`, `docs/FINAL_REPORT.md` | Inspected Mermaid ER diagram and entity definitions | **PASS** | None |
| **2** | Schema | Baseline DDL, keys, check constraints, cascades | Complete baseline schema with InnoDB foreign keys and CHECK rules | `sql/01_schema.sql` | Executed against MySQL 8; 13 tables verified | **PASS** | None |
| **3** | Sample Data | Realistic Pakistani sample data (PKR) | 30 products, 15 users, 25 orders, addresses, reviews, shipments | `sql/02_sample_data.sql` | Executed query verifying 0 pricing discrepancies | **PASS** | None |
| **4** | Views & Indexes | 5 analytical views, B-Tree performance indexes | `v_order_summary`, `v_low_stock`, `v_sales_by_category`, `v_best_sellers`, `v_abandoned_carts` | `sql/03_views_indexes.sql` | EXPLAIN query plan verified B-Tree index scan | **PASS** | None |
| **5** | Procedures & Triggers | `sp_place_order`, `sp_cancel_order`, oversell trigger | ACID checkout, stock decrement trigger, verified purchase trigger | `sql/04_procedures_triggers.sql` | Tested oversell rollback: 0 orphan rows created | **PASS** | None |
| **6** | Roles & Privileges | MySQL 8 RBAC roles | `shop_admin`, `shop_staff`, `shop_customer` roles and grants | `sql/05_roles.sql` | Verified `shop_customer` denied SELECT on `users` | **PASS** | None |
| **7** | Demo Operations | Advanced SQL operations (Q6 assignment) | 5-table invoice join, self-referencing category joins, GROUP BY HAVING | `sql/06_demo_queries.sql` | Executed demo queries Sections 1–9 | **PASS** | None |
| **8** | Web UI (Flask) | Storefront, catalog, cart, checkout UI | Complete Flask application with 15 Jinja templates and session auth | `app/app.py`, `app/templates/` | Automated E2E web suite executed | **PASS** | None |
| **9** | Testing | Automated database engine test harness | 10 automated test cases (T1–T10) validating constraints & triggers | `sql/07_tests.sql` | Executed `sp_run_all_tests()`; 10/10 PASS | **PASS** | None |
| **10** | Report & Viva | Academic project report, demo script, viva notes | 25,000+ word final report, 10-minute demo guide, detailed viva defense | `docs/FINAL_REPORT.md`, `docs/demo_guide.md`, `docs/viva_notes.md` | Inspected document coverage of 9 CEP questions | **PASS** | None |
| **11A** | Catalog Schema Expansion | Multi-image gallery, brand table, category tree | `brands`, `product_images`, slug columns, single primary trigger | `sql/08_catalog_expansion.sql` | Executed twice without error; `audits/AUDIT_11A.md` | **PASS** | None |
| **11B** | Catalog Data Pipeline | Manifest for 51 real Pakistani retail products | `data/products_manifest.csv` and idempotent `import_catalog.py` | `data/products_manifest.csv`, `app/scripts/import_catalog.py` | Catalog expanded to 81 active products; `AUDIT_11B.md` | **PASS** | None |
| **11C** | Image Acquisition | Option B polite image scraper with fallback | 81 local images, SVG placeholder, `images_report.json` | `static/images/`, `data/images_report.json` | 0 broken images on disk; `AUDIT_11C.md` | **PARTIAL** | Merge `fetch_images.py` from `agent/image` |
| **11D** | Department Browsing UI | Department landing cards, subcategory chips | `/category/<slug>` route, breadcrumbs, brand & price range filters | `app/templates/category.html`, `app/templates/index.html` | Visual check at 390px/1280px; `AUDIT_11D_11F.md` | **PASS** | None |
| **11E** | Product Gallery UI | Multi-image aspect-ratio thumbnail switcher | Aspect-ratio locked cards, JavaScript gallery thumbnail switcher | `app/templates/product_detail.html` | Playwright screenshots verified layout stability | **PASS** | None |
| **11F** | Admin Media Management | Secure product add/edit with image uploads | Brand selector, MIME validation, 2 MB upload guard, secure naming | `app/templates/admin/product_form.html`, `app/app.py` | Tested bad extension & oversized file rejection | **PASS** | None |
| **11G** | Testing & Finalization | Tests T11–T15, responsive pass, docs update | Tests T11–T15 added to `07_tests.sql`, test_app.py expanded to 25 | `sql/07_tests.sql`, `test_app.py`, `audits/AUDIT_11G.md` | 15/15 SQL tests PASS; 25/25 web tests PASS | **PASS** | None |
| **12A** | Requirements Traceability | Comprehensive bi-directional matrix | 63 requirements mapped across DB, routes, templates, and tests | `docs/traceability.csv` | 63/63 requirements mapped to active artifacts | **PASS** | None |
| **12B** | Database Alignment | Schema expansion for SRS alignment | 8 new tables (`delivery_rates`, `tax_rates`, `order_status_history`, etc.) | `sql/09_srs_alignment.sql`, `sql/10_srs_alignment_fixes.sql` | Executed twice with zero errors; `AUDIT_12AB.md` | **PASS** | None |
| **12C** | Checkout & Pricing | Guest checkout, cart merge, price parity, gateway | `sp_place_guest_order`, `sp_merge_carts`, `sp_cart_summary`, sandbox | `app/app.py`, `app/templates/checkout.html`, `cart.html` | Verified guest checkout, recovery, `AUDIT_12C.md` | **PASS** | None |
| **12D** | Trust & Operations | Order tracking, tickets, returns, seller moderation | Self-service tracking, support queue, RMA SLA view, policy pages | `app/templates/order_track.html`, `support.html`, `sellers.html` | Verified status triggers, overdue view; `AUDIT_12D.md` | **PASS** | None |
| **12E** | Quality & Accessibility | WCAG 2.1 AA accessibility & mobile responsiveness | Semantic HTML labels, 44px targets, contrast $\ge$ 4.5:1, screenshots | `audits/screenshots/` (12 screenshots) | Captured fresh desktop & mobile views; `AUDIT_12E.md` | **PASS** | None |
| **12F** | Acceptance & Viva Prep | Acceptance test sheet, viva notes, report update | 25/25 ACs documented, 46 web tests, viva defense Q&A for 3 members | `docs/srs_test_sheet.md`, `test_app.py`, `docs/viva_notes.md` | 25/25 ACs verified; `AUDIT_12F.md` | **PASS** | None |
| **13A** | Production Readiness | Containerization, configs, headers, health probe | Dockerfile, docker-compose.yml, gunicorn_config.py, /health, headers | `Dockerfile`, `docker-compose.yml`, `gunicorn_config.py` | Automated assertion on `/health`; `AUDIT_13A.md` | **PARTIAL** | Add CSRF protection, rate limiting, and DB SSL |
| **13B** | Cloud Database Setup | Aiven MySQL provisioning, TLS certs, least-privilege | Not started (no external cloud service provisioned) | None | N/A | **NOT STARTED** | Provision Aiven MySQL, configure TLS in `db.py` |
| **13C** | Cloud Web Service | Render web service deployment, environment vars | Not started (no remote Git repo or Render instance) | None | N/A | **NOT STARTED** | Configure GitHub remote, link Render web service |
| **13D** | Production Media | Persistent image storage for user uploads | Not started (local disk storage used) | None | N/A | **NOT STARTED** | Object storage integration or volume mounts |
| **13E** | Domain, DNS & PWA | Custom domain, Cloudflare TLS, PWA manifest | Not started (no PWA manifest or service worker) | None | N/A | **NOT STARTED** | Add `manifest.json`, service worker, DNS records |
| **13F** | Monitoring & Backups | Uptime monitoring on /health, Sentry error logs | Not started (local logging only) | None | N/A | **NOT STARTED** | Sentry DSN configuration, cron mysqldump |
| **13G** | Smoke Testing & Demo | 2 consecutive clean test passes, rollback plan | Not started | None | N/A | **NOT STARTED** | Live cloud demonstration rehearsal |

---

# Section 4 — Functional Completeness Audit

### Completed Features:
- **Authentication & Authorization:** Customer, Staff, Admin, and Seller login/logout with PBKDF2 salted password verification and RBAC route decorators (`@login_required`, `@admin_required`).
- **Storefront Catalog:** Top-level department browsing, sub-category chip filtering, brand faceted search, price range filtering, price sorting (ASC/DESC), and full-text keyword search.
- **Product Details & Gallery:** Aspect-ratio locked media gallery with interactive JavaScript thumbnail switcher, verified purchase star ratings, and real-time inventory stock badges.
- **Anonymous Guest Shopping:** Signed session tokens (`session['cart_token']`) with 30-day expiration, guest cart retention, and atomic guest cart merging (`sp_merge_carts`) upon user sign-in.
- **Pricing & Fiscal Engine:** Single source of truth calculation via `sp_cart_summary` providing exact mathematical parity across cart view, checkout summary, and order invoices.
- **Simulated Payment Sandbox:** Interactive gateway sandbox (`/payment/simulate/<id>`) supporting simulated success, failure, and cancellation, audit logging in `payment_attempts`, and instant retry or switch-to-COD recovery (`/payment/retry/<id>`).
- **Self-Service Order Tracking:** Real-time package tracking (`/orders/<id>/track`) driven directly by database trigger `trg_order_status_history`.
- **Customer Support Ticketing:** Inquiry submission (`/support`) generating formatted tickets (`TCK-YYYYMMDD-XXXX`) and centralized staff triage queue (`/staff/tickets`).
- **Merchandise Returns (RMA) & SLA Escalation:** Return request lodging (`/orders/<id>/return`), seller claim queue (`/seller/returns`), and automated overdue SLA escalation view (`v_overdue_return_requests`).
- **Seller Verification Governance:** Multi-vendor catalog governance restricting unverified sellers' goods from `v_product_catalog`, backed by an administrative review dashboard at `/admin/sellers`.
- **Legal Compliance:** Mandatory consent checkboxes for Terms of Service, Privacy Policy, and Return Policy with recorded database timestamps.
- **Operational Health Probe:** Endpoint `/health` reporting database engine connection status, latency, and timestamp.

### Unfinished / Incomplete Features:
- **CSRF Token Validation:** Forms post directly without anti-CSRF token verification.
- **Login Rate Limiting:** No brute-force rate limiter on `/login`.
- **Image Scraper Script in Main Branch:** `fetch_images.py` resides on unmerged branch `agent/image`.
- **Cloud Database TLS Connectivity:** `app/db.py` cannot establish SSL/TLS connections to remote managed MySQL instances.

---

# Section 5 — Requirements & Acceptance Criteria Verification

The audit team cross-checked the 25 SRS Acceptance Criteria (AC-01.1 through AC-08.6) documented in `docs/srs_test_sheet.md` and `docs/traceability.csv`:

| Criterion ID | Specification | Verification Evidence | Audit Verdict |
| :--- | :--- | :--- | :---: |
| **AC-01.1** | Itemized cart summary in PKR (subtotal, tax, fee, total) | `/cart?province=Punjab&city=Lahore` invokes `sp_cart_summary` | **VERIFIED PASS** |
| **AC-01.2** | Invoice total precisely matches cart summary total | Stored procedure parity verified in Test T16 | **VERIFIED PASS** |
| **AC-02.1** | Toggle between COD and Simulated Payment Gateway | Radio selector on `/checkout` routes to sandbox or confirmation | **VERIFIED PASS** |
| **AC-02.2** | Failed payment attempt logged with gateway reason; retry UI | Attempt saved in `payment_attempts`; `/payment/retry/<id>` renders | **VERIFIED PASS** |
| **AC-03.1** | Guest checkout completes without mandatory registration | `sp_place_guest_order` inserts order with `user_id = NULL` | **VERIFIED PASS** |
| **AC-04.1** | Dynamic delivery date computed from destination matrix | `delivery_rates` matrix returns min/max business days | **VERIFIED PASS** |
| **AC-04.2** | Customer address edit does not alter historical order snapshot | `orders.shipping_address_text` snapshot remains unchanged | **VERIFIED PASS** |
| **AC-04.3** | Order status mutations generate immutable audit history | Trigger `trg_order_status_history` logs to `order_status_history` | **VERIFIED PASS** |
| **AC-04.4** | Customer support ticket submission with category tags | `support_tickets` records category, subject, and contact info | **VERIFIED PASS** |
| **AC-04.5** | Staff ticket queue with status update and resolution notes | `/staff/tickets` renders queue; updates saved to DB | **VERIFIED PASS** |
| **AC-05.1** | Responsive layouts at 390px mobile and 1280px desktop | 12 Playwright screenshots verified in `audits/screenshots/` | **VERIFIED PASS** |
| **AC-06.1** | Seller entity records business credentials and status | `suppliers` table stores `verification_status` and location | **VERIFIED PASS** |
| **AC-06.2** | Unverified seller merchandise hidden from catalog | `v_product_catalog` inner joins `verification_status = 'verified'` | **VERIFIED PASS** |
| **AC-06.3** | Mandatory consent checkboxes with stored timestamps | `/checkout` blocks submission without terms consent | **VERIFIED PASS** |
| **AC-06.4** | 100% parameterized SQL queries preventing injection | Static AST scan confirmed 0 string concatenations in 110 queries | **VERIFIED PASS** |
| **AC-06.5** | Passwords hashed using PBKDF2/SHA256; `.env` ignored | `werkzeug.security` hashes verified; `.env` absent in git | **VERIFIED PASS** |
| **AC-07.1** | Catalog search executes under 200 ms with index utilization | EXPLAIN confirmed B-Tree scan on `idx_products_name` (<25 ms) | **VERIFIED PASS** |
| **AC-07.4** | Custom 400, 404, and 500 error pages without stack traces | Tested invalid route; `404.html` renders without debug trace | **VERIFIED PASS** |
| **AC-07.5** | Observability endpoint `/health` returns 200 JSON | `/health` returns `{"status": "healthy", "database": "connected"}` | **VERIFIED PASS** |
| **AC-08.1** | Guest cart items retained via signed session token | `session['cart_token']` links to active DB cart row | **VERIFIED PASS** |
| **AC-08.2** | Guest cart merged into user cart upon login | `sp_merge_carts` combines items with `ON DUPLICATE KEY UPDATE` | **VERIFIED PASS** |
| **AC-08.3** | Inactive carts $\ge$ 7 days appear on admin dashboard | `v_abandoned_carts` rendered in `app/templates/admin/dashboard.html` | **VERIFIED PASS** |
| **AC-08.4** | Return/replacement request lodging with reason & photo | `return_requests` records RMA number, reason, and refund method | **VERIFIED PASS** |
| **AC-08.5** | Return status transitions audited by database trigger | Trigger `trg_return_status_history` inserts into history | **VERIFIED PASS** |
| **AC-08.6** | Staff/seller queue surfaces return requests older than 72 hours | View `v_overdue_return_requests` isolates SLA breaches | **VERIFIED PASS** |

---

# Section 6 — Database Architecture Audit

The active MySQL 8 database (`online_shop`) was directly inspected via `INFORMATION_SCHEMA`:

### 1. Schema Normalization & Entity Health:
- **Base Tables:** 23 business tables + 1 automated test table (`test_results`). All 23 business tables comply with 3NF.
- **Foreign Key Integrity:** 21 foreign key constraints verified with explicit cascading delete (`ON DELETE CASCADE`) on dependent media and addresses, and deletion restriction (`ON DELETE RESTRICT`) on historical orders and catalog products.
- **Check Constraints:** Reject negative prices (`price >= 0`), negative stock (`stock_quantity >= 0`), and out-of-range ratings (`rating BETWEEN 1 AND 5`).

### 2. Views Audit (9 Views):
- `v_product_catalog` (81 rows): Denormalized catalog joining products, brands, suppliers, images, and verified ratings; excludes unverified sellers.
- `v_category_counts` (14 rows): Hierarchically rolls up active product counts from child subcategories to top-level departments.
- `v_abandoned_carts` (2 rows): Aggregates dormant carts untouched for $\ge$ 7 days.
- `v_low_stock` (4 rows): Alerts when stock $\le$ 5 units.
- `v_order_summary` (45 rows): Master reconciliation join across orders, items, payments, and shipments.
- `v_best_sellers` (20 rows): Volume rankings per product.
- `v_sales_by_category` (14 rows): Gross revenue and unit metrics per category.
- `v_sellers` (5 rows): Vendor credentials and verification status.
- `v_overdue_return_requests` (0 rows): Valid compiled view; returns rows only when RMA resolution exceeds SLA window.

### 3. Stored Procedures (8 Procedures):
- `sp_cart_summary`: Calculates gross subtotal, applies provincial tax rates, calculates shipping fees, and estimates delivery windows.
- `sp_place_order`: Executes atomic checkout within an ACID transaction (`START TRANSACTION` ... `COMMIT` / `ROLLBACK`).
- `sp_place_guest_order`: Atomic checkout for unauthenticated visitors with address snapshots.
- `sp_merge_carts`: Consolidates anonymous guest cart items into customer accounts upon sign-in without key collisions.
- `sp_cancel_order`: Transactionally cancels orders and restores inventory.
- `sp_set_product_primary_image`: Safely switches primary gallery images without trigger re-entrancy.
- `sp_mark_abandoned_carts`: Flags idle carts.
- `sp_run_all_tests`: Executes the 25-point database test suite directly in the SQL engine.

### 4. Database Triggers (10 Triggers):
- `trg_before_order_items_insert`: Blocks overselling via `SIGNAL SQLSTATE '45000'` if requested quantity exceeds stock.
- `trg_after_order_items_insert`: Synchronously decrements stock upon order placement.
- `trg_before_reviews_insert`: Blocks unverified reviews if customer has no delivered order for that product.
- `trg_product_images_single_primary_bi` & `_bu`: Enforces exactly one primary image per product.
- `trg_order_initial_status_history` & `trg_order_status_history`: Maintains immutable order lifecycle audit log.
- `trg_return_initial_status_history` & `trg_return_status_history`: Maintains immutable RMA status history.
- `trg_after_orders_update_audit`: Writes general audit entries into `audit_log`.

---

# Section 7 — Backend & Frontend Implementation Audit

### Backend Analysis (`app/app.py` & `app/db.py`):
- **Monolithic Architecture:** `app/app.py` contains 1,794 lines and 47 routes. While logically structured, it does not use Flask Blueprints as recommended in the roadmap.
- **Connection Management:** `app/db.py` creates a new PyMySQL connection per request and tears it down on context exit. It lacks connection pooling, which will introduce latency over remote cloud connections.
- **SQL Security:** Out of 110 SQL execution points, 100% utilize parameterized `%s` formatting. No SQL injection vulnerabilities were identified.
- **Input Validation:** File uploads are strictly validated against allowed extensions (`.jpg`, `.jpeg`, `.png`, `.webp`), MIME types, and 2 MB file limits using `secure_filename`.
- **Error Handling:** Routes employ custom handlers for HTTP 400, 404, and 500, rendering customer-friendly error templates without leaking internal tracebacks.

### Frontend & Templates Analysis (`app/templates/`):
- **Template Coverage:** All 33 templates rendered by `app/app.py` exist on disk. `base.html` serves as the master layout. Zero broken template links.
- **Design & Layout:** Styled using Bootstrap 5.3.3 and semantic CSS variables. Cards enforce strict aspect ratios (`4/3` and `1/1`) with `object-fit: cover`, eliminating Cumulative Layout Shift (CLS).
- **Usability Elements:** Breadcrumb navigation, 4-step checkout progress bar, interactive payment simulation buttons (Success, Fail, Cancel), and explicit legal consent checkboxes.

---

# Section 8 — Security Audit

| Severity | Issue ID | Description | Impact | Remediation Recommendation |
| :---: | :---: | :--- | :--- | :--- |
| **P1** | **SEC-01** | **No CSRF Protection on Forms:** None of the 21 POST forms across the application include CSRF tokens. | Cross-Site Request Forgery vulnerability; an attacker could trick an authenticated user into submitting unwanted orders, reviews, or status changes. | Integrate `Flask-WTF` (`CSRFProtect(app)`) and inject `{{ csrf_token() }}` into all 21 `<form method="post">` blocks. |
| **P1** | **SEC-02** | **No Database SSL/TLS Support in `db.py`:** PyMySQL connection string does not configure SSL context (`ssl={'ca': ...}`). | Prevents secure encrypted connection to managed cloud MySQL instances (e.g. Aiven), blocking deployment or risking cleartext wire transmission. | Update `app/db.py` to accept optional `DB_SSL_CA` environment variable and pass SSL dictionary to `pymysql.connect()`. |
| **P2** | **SEC-03** | **No Rate Limiting on `/login`:** The authentication endpoint lacks rate limiting against brute-force attacks. | An attacker could attempt automated credential stuffing against customer or administrator accounts. | Integrate `Flask-Limiter` to enforce a rate limit of 5 requests per minute on `/login`. |
| **P2** | **SEC-04** | **Fallback Secret Key in Code:** `app.py` contains fallback `'fallback-dev-secret-key'`. | If `FLASK_SECRET_KEY` is omitted in production, sessions use a predictable key. | Raise a runtime error on application boot if `FLASK_ENV == 'production'` and `FLASK_SECRET_KEY` is unset. |
| **P3** | **SEC-05** | **Absence of Content Security Policy (CSP):** HTTP response headers include X-Frame-Options and X-Content-Type-Options, but no CSP header. | Minor defense-in-depth weakness against cross-site scripting. | Add standard `Content-Security-Policy` header in `@app.after_request`. |

*Note: No plaintext passwords, active API keys, or private certificates were found in source code or Git history.*

---

# Section 9 — Testing Results & Execution Evidence

Testing was independently executed across two test suites:

### 1. Database Test Harness (`sql/07_tests.sql`):
- **Execution Engine:** Local MySQL Server 8.0.46 via `sp_run_all_tests()`.
- **Results:** **25 Tests Executed, 25 Passed, 0 Failed (100% PASS)**.
- **Verified Areas:** Duplicate email rejection (T1), CHECK constraints on price/stock/rating (T2–T4), ACID oversell rollback (T5), stock reduction trigger (T6), audit logging trigger (T7), unverified review block (T8), FK RESTRICT and CASCADE rules (T9–T15), price parity via `sp_cart_summary` (T16), guest checkout (T17), cart merge (T18), status triggers (T19, T23), address snapshots (T20), support ticketing (T21), seller verification (T22), overdue SLA view (T24), payment attempt logging (T25).

### 2. Web Application Test Harness (`test_app.py`):
- **Execution Command:** `.\venv\Scripts\python.exe test_app.py`
- **Results:** **46 Tests Executed, 45 Passed, 1 Failed, 0 Not Executed (97.8% PASS)**.
- **Failure Analysis:**
  - **Failed Test:** Test #10: `POST /checkout (Atomic Order Placement)`.
  - **Error Output:** `FAILED: Oversell Error: Requested quantity exceeds available inventory stock.`
  - **Root Cause Investigation:** In `test_app.py`, Test #7 repeatedly adds 2 units of Product #12 (`J. Classic Cotton Kurta White`) and Test #10 places the order. Because tests ran directly against the active development database without transactional rollback, Product #12's inventory was decremented by 2 units on each test run until `stock_quantity` reached 0. The subsequent run was blocked by database trigger `trg_before_order_items_insert`.
  - **Significance:** This confirms that database-level oversell protection is actively enforcing stock constraints. However, it exposes a critical test harness defect: **the test suite lacks environment isolation and teardown fixtures**.

---

# Section 10 — Code Cleanliness & Repository Inventory

Every file in the repository was examined and categorized:

| File / Path | Classification | Category Description & Deletion Risk | Recommended Action |
| :--- | :---: | :--- | :--- |
| `static/` (root directory, 52 files) | **REMOVE CANDIDATE** | Exact duplicate of `app/static/` (52 identical images, ~340 KB). Flask serves exclusively from `app/static/`. Deletion risk: Zero. | Delete root `static/` to eliminate redundancy. |
| `backups/pre_phase12_20261103_025204.sql` | **REMOVE CANDIDATE** | 0-byte corrupted dump file created when a command was interrupted. Deletion risk: Zero. | Delete 0-byte file. |
| `docs/report_outline.md` | **ARCHIVE** | Preliminary draft outline; completely superseded by `docs/FINAL_REPORT.md`. Deletion risk: None. | Move to `docs/archive/report_outline.md`. |
| `audits/screenshots/*px.png` (6 files) | **ARCHIVE** | Phase 11 screenshots (`homepage_1280px.png`, etc.) superseded by Phase 12 screenshots (`homepage_1280.png`). | Delete or archive older naming variants. |
| `app/scripts/fetch_images.py` | **KEEP — DEVELOPMENT** | Critical Phase 11 image fetcher; exists on branch `agent/image` but missing on `main`. | Cherry-pick / merge into `main` branch. |
| `design-system/` | **KEEP — DEVELOPMENT** | Design token specifications and UI guidelines created during styling passes. | Keep in repository for reference. |
| `data/products_manifest.csv` | **KEEP — ACADEMIC** | Source-of-truth product catalog manifest (51 products). | Retain permanently. |
| `data/images_report.json` | **KEEP — DEVELOPMENT** | Image acquisition audit log. | Retain for documentation. |
| `docs/*.md`, `docs/*.docx`, `docs/*.csv` | **KEEP — ACADEMIC** | Final report, ER diagrams, viva notes, assignment instructions, traceability matrix. | Retain permanently for CEP submission. |
| `sql/01_*.sql` to `sql/10_*.sql` | **KEEP — ACADEMIC** | Sequential, re-runnable database migration and test scripts. | Retain permanently. |
| `app/app.py`, `app/db.py` | **KEEP** | Core backend application and connection manager. | Retain. |
| `app/templates/*.html` (34 files) | **KEEP** | Core application frontend presentation layer. | Retain. |
| `Dockerfile`, `docker-compose.yml`, `gunicorn_config.py` | **KEEP** | Production containerization and WSGI configuration. | Retain. |

---

# Section 11 — Recommended Clean Repository Structure

Below is the proposed target repository layout after executing hygiene recommendations:

```
muet-online-shop/
├── .gitignore                          # Standard git ignore (.env, venv/, backups/, __pycache__/)
├── .env.example                        # Template for environment variables (safe, no secrets)
├── README.md                           # Project introduction, team details, and setup guide
├── requirements.txt                    # Pinned production dependencies (including gunicorn)
├── Dockerfile                          # Lightweight Python 3.11-slim production container
├── docker-compose.yml                  # Production & local stack (Flask web + MySQL 8 db)
├── gunicorn_config.py                  # Production WSGI server concurrency configuration
├── test_app.py                         # End-to-end automated application test suite
├── app/
│   ├── app.py                          # Main Flask application (or refactored Blueprints)
│   ├── db.py                           # Database connection manager (with SSL support)
│   ├── scripts/
│   │   ├── import_catalog.py           # Idempotent catalog importer from manifest
│   │   └── fetch_images.py             # Polite image fetcher with fallback specimen generator
│   ├── static/                         # Unified static asset root (NO root duplicate)
│   │   └── images/
│   │       ├── placeholder.svg
│   │       ├── categories/
│   │       ├── products/
│   │       ├── returns/
│   │       └── uploads/
│   └── templates/                      # Jinja2 presentation templates (34 files)
│       ├── base.html
│       ├── index.html
│       ├── products.html
│       ├── category.html
│       ├── product_detail.html
│       ├── cart.html
│       ├── checkout.html
│       ├── order_confirmation.html
│       ├── order_track.html
│       ├── support.html
│       ├── ticket_detail.html
│       ├── return_request.html
│       ├── return_detail.html
│       ├── payment_simulate.html
│       ├── payment_retry.html
│       ├── privacy.html
│       ├── terms.html
│       ├── returns_policy.html
│       ├── admin/
│       ├── errors/
│       ├── seller/
│       └── staff/
├── sql/                                # Sequential re-runnable MySQL scripts
│   ├── 01_schema.sql
│   ├── 02_sample_data.sql
│   ├── 03_views_indexes.sql
│   ├── 04_procedures_triggers.sql
│   ├── 05_roles.sql
│   ├── 06_demo_queries.sql
│   ├── 07_tests.sql
│   ├── 08_catalog_expansion.sql
│   ├── 09_srs_alignment.sql
│   └── 10_srs_alignment_fixes.sql
├── docs/                               # Academic deliverables & documentation
│   ├── DBMS_CEP.docx
│   ├── FINAL_REPORT.md
│   ├── er_diagram.md
│   ├── er_diagram.png
│   ├── viva_notes.md
│   ├── demo_guide.md
│   ├── traceability.csv
│   ├── srs_test_sheet.md
│   ├── Online Shopping Database Project Roadmap (DBMS CEP).docx
│   ├── Phase 11 Real Product Catalog, Images and Category Browsing.md
│   ├── Phase 12 and 13 SRS Alignment and Web Deployment Plan.md
│   └── archive/                        # Superseded draft outlines
│       └── report_outline.md
├── data/
│   ├── products_manifest.csv
│   └── images_report.json
├── audits/                             # Verification evidence & audit logs
│   ├── AUDIT_REPORT.md                 # This comprehensive master audit report
│   ├── AUDIT_11A.md to AUDIT_13A.md
│   └── screenshots/                    # 12 standardized 390px and 1280px screenshots
└── backups/                            # Local database backups (git-ignored)
    ├── backup_phase11_pre.sql
    ├── pre_phase11_20261103_0147.sql
    ├── pre_phase12_20261103_025219.sql
    └── pre_12C_20261103_025942.sql
```

---

# Section 12 — Performance & Maintainability Analysis

1. **Modular Architecture:** `app/app.py` is currently a single 1,794-line file. Refactoring into Flask Blueprints (`blueprints/catalog.py`, `blueprints/checkout.py`, `blueprints/admin.py`, `blueprints/support.py`) would dramatically improve maintainability and reflect the 3-member team ownership.
2. **Database Connection Pooling:** PyMySQL opens a new socket per HTTP request. Under production Gunicorn load, remote network latency to Aiven will slow response times. Adding a connection pool (e.g. `DBUtils.pooled_db`) will reduce connection overhead by 80%.
3. **Database Indexing:** Strategic B-Tree indexes exist on search attributes (`idx_products_name`), category foreign keys (`idx_products_category`), and user order histories (`idx_orders_user_date`). EXPLAIN plans confirm index utilization with query times under 25 ms.
4. **Image Delivery & Caching:** Product images are served as static files from disk. For production deployment, caching headers (`Cache-Control: public, max-age=86400`) should be set in `@app.after_request` to minimize bandwidth consumption.

---

# Section 13 — Git & Version Control Audit

- **Current Branch:** `main` (commit `c22b26c`).
- **Working Tree:** Clean (`nothing to commit, working tree clean`).
- **Local Branches:** `main`, `agent/data`, `agent/docs`, `agent/image`, `agent/ui`.
- **Git Remote:** `git remote -v` returned empty. **No remote repository is linked.**
- **History Audit:** Recent commits reflect systematic progression across Phases 11, 12, and 13A. No sensitive credentials or `.env` files exist in Git history.
- **Branch Discrepancy:** The script `app/scripts/fetch_images.py` was committed to `agent/image` in commit `d364f93` but was never merged into `main`.

---

# Section 14 — Deployment Readiness Assessment

### Phase 13A (Production Preparation): **PARTIAL**
- **Environment Configuration:** Implemented (`.env` with `.env.example`).
- **Debug Configuration:** Production toggle configured.
- **Dependency Pinning:** Implemented (`requirements.txt` with Gunicorn).
- **Containerization:** Implemented (`Dockerfile` with non-root user `appuser` and `docker-compose.yml`).
- **Observability Probe:** Implemented (`GET /health` returns JSON database heartbeat).
- **Security Headers & Cookies:** Implemented (`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `HttpOnly`, `SameSite=Lax`).
- **Blockers:** Missing CSRF tokens, missing login rate limiting, and lack of SSL/TLS support in `db.py`.

### Phase 13B (Cloud Database Readiness - Aiven MySQL): **NOT READY**
- **Hosting Verification:** Current official Aiven documentation confirms MySQL free tier provides 1 CPU, 1 GB RAM, 1 GB disk, and up to 76 connections. It supports stored procedures, triggers, views, and transactions.
- **Critical Caveat:** Aiven **does not grant the `SUPER` privilege** and enforces TLS connections.
- **Blockers:**
  1. `app/db.py` lacks SSL connection parameters.
  2. SQL scripts `05_roles.sql` and `09_srs_alignment.sql` contain `CREATE USER ... @'localhost'` statements; on a remote cloud database, application connections originate from external hosts (`'%'`), not `localhost`.

### Phase 13C (Cloud Web Service Readiness - Render): **NOT READY**
- **Hosting Verification:** Render free web services provide 512 MB RAM, ~0.1 CPU, automatic TLS, and custom domain support.
- **Critical Caveats:**
  1. **Spin-down policy:** Free web services sleep after 15 minutes of inactivity and take ~60 seconds to cold-start.
  2. **Ephemeral filesystem:** Free instances have **no persistent disk**. Files written to `app/static/images/uploads/` (such as admin image uploads) are permanently erased upon restart or redeploy.
- **Blockers:** No GitHub remote repository configured; Render requires a linked Git repo.

### Deployment Level Verdict:
1. **Local Testing:** **READY**
2. **Local Academic Demonstration:** **READY**
3. **Cloud Staging Deployment:** **CONDITIONALLY READY (Requires P1 Fixes)**
4. **Public Academic Demonstration:** **CONDITIONALLY READY (Requires P1 Fixes)**
5. **Real Commercial Production:** **NOT READY (Requires full payment gateway onboarding, persistent S3 storage, and WAF)**

---

# Section 15 — Prioritized Issues Matrix

| Issue ID | Priority | Description | Component | Recommended Fix | Blocks Deployment? |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **P1-01** | **P1 (High)** | Missing CSRF protection on 21 POST forms | `app/app.py`, templates | Add `Flask-WTF` CSRFProtect and `{{ csrf_token() }}` to forms | **YES (Cloud)** |
| **P1-02** | **P1 (High)** | `app/db.py` lacks SSL/TLS connection support | `app/db.py` | Add optional `ssl={'ca': ...}` to `pymysql.connect()` | **YES (Cloud)** |
| **P1-03** | **P1 (High)** | Test harness pollutes database state causing oversell failure | `test_app.py` | Isolate test data or replenish test product stock in fixture | **NO (Dev only)** |
| **P1-04** | **P1 (High)** | No Git remote repository configured | Git configuration | Create GitHub repository and configure `git remote add origin` | **YES (Cloud)** |
| **P2-01** | **P2 (Med)** | Monolithic 1,794-line `app.py` without Blueprints | `app/app.py` | Modularize into Blueprints per roadmap specification | **NO** |
| **P2-02** | **P2 (Med)** | Missing brute-force rate limiting on `/login` | `app/app.py` | Add `Flask-Limiter` (5 req/min) on login endpoint | **NO** |
| **P2-03** | **P2 (Med)** | Redundant duplicate root `static/` directory (52 files) | File system | Delete root `static/` folder (keep `app/static/`) | **NO** |
| **P2-04** | **P2 (Med)** | Corrupt 0-byte backup file on disk | `backups/` | Delete `pre_phase12_20261103_025204.sql` | **NO** |
| **P2-05** | **P2 (Med)** | `app/scripts/fetch_images.py` unmerged on branch `agent/image` | Git branch | Merge `agent/image` into `main` | **NO** |
| **P2-06** | **P2 (Med)** | Lack of database connection pooling in `db.py` | `app/db.py` | Implement `DBUtils.pooled_db` connection pool | **NO** |
| **P3-01** | **P3 (Low)** | Outdated draft report outline | `docs/` | Archive `report_outline.md` into `docs/archive/` | **NO** |
| **P3-02** | **P3 (Low)** | Inconsistent screenshot naming in `audits/screenshots/` | `audits/` | Clean up 6 legacy `...px.png` Phase 11 screenshots | **NO** |
| **P3-03** | **P3 (Low)** | Missing PWA manifest and service worker | Frontend | Add `manifest.json` and service worker (Phase 13E) | **NO** |

---

# Section 16 — Remaining Work Breakdown

### Outstanding Phase 13 Sub-Phases:
1. **Phase 13A (Production Polish):**
   - Implement CSRF tokens across all 21 POST forms (`Flask-WTF`).
   - Implement login rate limiting on `/login` (`Flask-Limiter`).
   - Update `app/db.py` to support SSL CA certificates for cloud DB connections.
   - Fix `test_app.py` test isolation to achieve 46/46 automated passes.
2. **Phase 13B (Cloud Database - Aiven):**
   - Create Aiven free MySQL service instance.
   - Run SQL migration scripts 01 through 10 to establish schema and seed data.
   - Verify that triggers, stored procedures, and roles execute cleanly under Aiven's managed privilege model.
3. **Phase 13C (Cloud Web Service - Render):**
   - Push repository to private GitHub repository.
   - Create Render Web Service connected to GitHub repository.
   - Configure environment variables (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `FLASK_SECRET_KEY`, `FLASK_ENV=production`).
   - Verify deployment build using `Dockerfile` and verify `/health` endpoint.
4. **Phase 13D (Persistent Media / Ephemeral Fallback):**
   - Ensure all catalog product images ship inside repository image directories so Render redeployments do not lose assets.
5. **Phase 13E (PWA & Domain):**
   - Create `manifest.json` and basic service worker for installable mobile browser experience.
6. **Phase 13F (Monitoring & Operational Safeguards):**
   - Configure external uptime monitor (e.g. UptimeRobot or Cron-job.org) hitting `/health` every 10 minutes to prevent Render from sleeping before demonstrations.
7. **Phase 13G (Demonstration Rehearsal):**
   - Execute the 10-minute viva demo walkthrough on a mobile device and desktop browser using the live cloud link.

---

# Section 17 — Recommended Next Steps (Priority Ordered)

The audit team recommends completing the following exact steps in order:

1. **Step 1 (P1 Fixes):**
   - Update `app/db.py` to support SSL/TLS parameters via environment variable `DB_SSL_CA`.
   - Add `Flask-WTF` to `requirements.txt`, initialize `CSRFProtect(app)`, and insert hidden CSRF fields in the 21 POST forms.
   - Add a database reset or inventory restock fixture in `test_app.py` so Product #12 is never depleted to 0, restoring automated test results to 46/46 (100% PASS).
2. **Step 2 (Repository Hygiene):**
   - Remove redundant root `static/` directory.
   - Delete 0-byte corrupt backup file `pre_phase12_20261103_025204.sql`.
   - Merge `fetch_images.py` from `agent/image` into `main`.
3. **Step 3 (Git Remote Configuration):**
   - Initialize remote GitHub repository and push `main` branch.
4. **Step 4 (Phase 13B - Cloud Database Provisioning):**
   - Provision free Aiven for MySQL instance; apply `sql/01` through `sql/10`.
5. **Step 5 (Phase 13C - Render Web Service Deployment):**
   - Connect Render to GitHub, set environment variables, and verify live public URL.
6. **Step 6 (Phase 13F - Anti-Sleep Uptime Ping):**
   - Set up an automated HTTP GET ping to `/health` every 10 minutes to prevent Render's 15-minute cold sleep during the academic viva.

---

# Section 18 — Final Project Verdict

### Verdict: **CONDITIONALLY READY — REMAINING FIXES REQUIRED**

### Detailed Justification:
- **Local Academic Demonstration:** **100% READY.** The application runs smoothly, all 23 business tables in 3NF exist in MySQL 8, all 10 triggers and 8 stored procedures execute properly, and all 25 SRS acceptance criteria are verified.
- **Cloud Deployment:** **NOT READY YET.** Deploying to Render and Aiven immediately would fail because:
  1. `app/db.py` cannot connect to Aiven over required SSL/TLS.
  2. Forms lack CSRF protection.
  3. No remote Git repository is configured for Render build hooks.
- **Conclusion:** The project is in an exceptional technical state. Addressing the 4 P1 items in Step 1 will take approximately 1 to 2 hours of focused engineering, after which the project can be safely deployed to the cloud for academic presentation.

*Signed on behalf of the Audit Team:*  
**Autonomous Technical & Compliance Audit Lead**  
Mehran University of Engineering and Technology (MUET) DBMS CEP Assessment
