# INDEPENDENT PROJECT AUDIT VERIFICATION REPORT
## Online Shopping Database Management System — DBMS CEP
**Department of Software Engineering, Mehran University of Engineering & Technology (MUET), Jamshoro**

- **Project:** Online Shopping Database Management System (DBMS CEP)
- **Course:** Database Management Systems (CS-212 / 3rd Semester, 2nd Year)
- **Course Instructor:** Aisha Ashfaque
- **Review Target:** `AUDIT_REPORT.md` (Comprehensive Project Audit Report, dated 2026-11-03)
- **Reviewer:** Independent Autonomous Technical Quality, Architecture & Security Reviewer
- **Review Date:** 2026-11-03
- **Review Report Path:** `AUDIT_REVIEW.md` (Project Root)
- **Overall Independent Audit Verdict:** **DISPUTED IN PART — SIGNIFICANT UNNOTICED BLOCKERS IDENTIFIED**  
  *(Ready for Local CLI Demonstration with restock; NOT Ready for Docker Compose; NOT Ready for Cloud Staging or Public Deployment)*

---

# 1. Executive Summary & Review Assessment

This verification was conducted by an independent technical reviewer to critically challenge and audit the findings, classifications, test results, cleanup suggestions, and deployment recommendations presented in `AUDIT_REPORT.md`.

Rather than taking the previous audit's assertions at face value, the reviewer inspected the live MySQL 8 database (`online_shop`), examined the 1,807-line backend application (`app/app.py`), reviewed the 34 Jinja2 templates, analyzed the 10 sequential SQL migration files, evaluated the container orchestration configurations (`Dockerfile`, `docker-compose.yml`), inspected Git commit history across all branches, and cross-referenced requirements against the official assignment prompt (`docs/DBMS_CEP.docx`), the project roadmap (`docs/Online Shopping Database Project Roadmap (DBMS CEP).docx`), and the SRS Alignment plan (`docs/Phase 12 and 13 SRS Alignment and Web Deployment Plan.md`).

### Summary of Independent Review Findings:
1. **The Original Audit Correctly Identified Several Key Weaknesses:**
   - The original auditor accurately identified the absence of CSRF protection across the application's 21 web forms (**SEC-01**).
   - The original auditor correctly observed that `app/db.py` lacks TLS/SSL configuration parameters (**SEC-02**), which blocks encrypted cloud connectivity to providers such as Aiven.
   - The original auditor accurately diagnosed that the failure of Test #10 (`POST /checkout`) in `test_app.py` was caused by test state pollution: repeated test runs decremented Product #12's stock to 0, which properly triggered the engine's oversell protection trigger (`trg_before_order_items_insert`).
   - The absence of a Git remote repository was correctly flagged.

2. **The Original Audit Failed to Detect Two Showstopper Deployment Blockers:**
   - **Showstopper 1: Gunicorn WSGI Import Crash (`ModuleNotFoundError: No module named 'db'`)**: In `Dockerfile`, line 39 executes `gunicorn --config gunicorn_config.py app.app:app`. In `app/app.py`, line 23 executes `from db import get_connection`. When Gunicorn runs from the container root directory `/app`, `sys.path` contains `/app` but not `/app/app`. Attempting to load `app.app` immediately crashes with `ModuleNotFoundError: No module named 'db'`. Neither the Phase 13A author nor the original auditor ever actually ran Gunicorn or built the Docker container.
   - **Showstopper 2: Database Initialization Out-of-Order Dependency in Docker**: In `docker-compose.yml`, `./sql` is mounted to `/docker-entrypoint-initdb.d`. MySQL entrypoint scripts execute SQL files in strict alphabetical order. `07_tests.sql` executes before `08_catalog_expansion.sql`, `09_srs_alignment.sql`, and `10_srs_alignment_fixes.sql`. Because `07_tests.sql` contains `CALL sp_run_all_tests();` which queries Phase 11 and Phase 12 tables and stored procedures (e.g. `product_images`, `sp_cart_summary`, `sp_place_guest_order`), clean database initialization in Docker crashes on script 07.

3. **The Original Audit Issued an Unsafe and Erroneous Cleanup Recommendation:**
   - The original auditor categorized the root `static/` directory as a "Zero-Risk REMOVE CANDIDATE". This recommendation is **technically flawed and unsafe**. At runtime, `app/app.py` explicitly synchronizes admin uploads to `../static/images/products/uploads/` (lines 1246–1251, 1325–1330), saves return proof images exclusively to `../static/images/returns/` (line 1599), and `docker-compose.yml` mounts `./static/images/uploads:/app/static/images/uploads` (line 50). Deleting the root `static/` directory would break return proof submissions and break Docker volume mounting.

4. **The Original Audit Overlooked Traceability Fabrication:**
   - The original audit marked Phase 12A as **PASS** based on `docs/traceability.csv`. Independent inspection revealed that over 40 test function names cited in `traceability.csv` (e.g. `test_cart_summary_calculation`, `test_accessible_form_labels`, `test_wcag_color_contrast`) do not exist in `test_app.py`, and 5 template targets cited do not exist on disk.

5. **Discrepancy in Database Object Counts:**
   - The original report claimed the database has **6 roles** and **21 foreign keys**. Direct inspection of MySQL's `INFORMATION_SCHEMA` proves that the database contains **4 roles** (`shop_admin`, `shop_staff`, `shop_customer`, `shop_seller`) and **25 foreign keys**.

---

# 2. Findings Classification Matrix

Every significant technical assertion made in `AUDIT_REPORT.md` has been independently checked against the codebase, database engine, and runtime environment:

| ID | Original Audit Statement | Independent Review Finding | Classification |
| :--- | :--- | :--- | :---: |
| **ST-01** | **Academic CEP Objectives Exceeded (Section 1):** Schema normalized into 23 domain entities in strict 3NF. | Verified. 23 business tables exist in MySQL 8 (`test_results` is the 24th table). Foreign key structures, junction tables (`order_items`, `cart_items`), and functional dependencies adhere to 3NF. | **VERIFIED** |
| **ST-02** | **Foreign Key Constraint Count (Section 1 & 6):** 21 foreign key constraints verified in MySQL 8. | Disputed. Direct query of `INFORMATION_SCHEMA.KEY_COLUMN_USAGE` identified **25 foreign key constraints**, not 21. The original audit undercounted by 4 constraints. | **DISPUTED** |
| **ST-03** | **Database Role Count (Section 1 & 6):** 6 Role-Based Access Control Roles exist in MySQL 8. | Disputed. Query of `mysql.user` and inspection of `05_roles.sql` and `09_srs_alignment.sql` confirms **4 roles** (`shop_admin`, `shop_staff`, `shop_customer`, `shop_seller`) and 3 test user accounts. | **DISPUTED** |
| **ST-04** | **Analytical Views Audit (Section 6):** 9 analytical views compiled and functional. | Verified. All 9 views (`v_abandoned_carts`, `v_best_sellers`, `v_category_counts`, `v_low_stock`, `v_order_summary`, `v_overdue_return_requests`, `v_product_catalog`, `v_sales_by_category`, `v_sellers`) return valid rows with zero syntax errors. | **VERIFIED** |
| **ST-05** | **Stored Procedures Audit (Section 6):** 8 stored procedures compiled and functional. | Verified. All 8 procedures (`sp_cancel_order`, `sp_cart_summary`, `sp_mark_abandoned_carts`, `sp_merge_carts`, `sp_place_guest_order`, `sp_place_order`, `sp_run_all_tests`, `sp_set_product_primary_image`) exist in `INFORMATION_SCHEMA.ROUTINES`. | **VERIFIED** |
| **ST-06** | **Triggers Audit (Section 6):** 10 business triggers active in engine. | Verified. All 10 triggers exist on tables `orders`, `order_items`, `product_images`, `return_requests`, and `reviews`. | **VERIFIED** |
| **ST-07** | **Check Constraints Audit (Section 6):** Check constraints reject negative prices, negative stock, and invalid ratings. | Verified. 8 check constraints confirmed in `INFORMATION_SCHEMA.CHECK_CONSTRAINTS` enforcing prices $\ge 0$, quantities $> 0$, and ratings between 1 and 5. | **VERIFIED** |
| **ST-08** | **Database Test Suite (Section 1 & 9):** 25 / 25 Passed (100%) via `sp_run_all_tests()`. | Partially Verified. The `test_results` table in MySQL records 25 PASS results. However, `07_tests.sql` cannot run on a clean database due to out-of-order schema dependencies. | **PARTIALLY VERIFIED** |
| **ST-09** | **Web Application Test Suite (Section 1 & 9):** 45 / 46 Passed (97.8%); Test #10 failed due to Product #12 stock depleted to 0. | Verified. Product #12 was verified to have `stock_quantity = 0`. Test #7 attempts to purchase 2 units, triggering oversell signal. The test harness mutates the database without teardown. | **VERIFIED** |
| **ST-10** | **Traceability Matrix Completeness (Section 3 & 5):** 63/63 requirements mapped to active artifacts; Phase 12A PASS. | Disputed. While `docs/traceability.csv` contains 63 entries, over 40 referenced test function names do not exist in `test_app.py`, and 5 referenced template targets do not exist on disk. | **DISPUTED** |
| **ST-11** | **Acceptance Criteria Verification (Section 5):** 25/25 SRS Acceptance Criteria satisfied. | Partially Verified. Core behaviors exist in code. However, `srs_test_sheet.md` omitted AC-02.3, AC-03.2, AC-05.2–4, and AC-07.2–3, which earlier reports falsely claimed were cataloged. | **PARTIALLY VERIFIED** |
| **ST-12** | **SEC-01 CSRF Protection (Section 8):** Missing CSRF protection on 21 POST forms. | Verified. Scan confirmed 21 POST forms across templates with zero anti-CSRF tokens and no `Flask-WTF` integration. | **VERIFIED** |
| **ST-13** | **SEC-02 Database SSL/TLS (Section 8):** `app/db.py` lacks SSL/TLS connection parameters. | Verified. `pymysql.connect` in `app/db.py` does not include `ssl` dictionary, preventing encrypted connections to cloud providers. | **VERIFIED** |
| **ST-14** | **SEC-03 Rate Limiting (Section 8):** `/login` lacks brute-force rate limiting. | Verified. No request throttling decorator is attached to the authentication endpoint. | **VERIFIED** |
| **ST-15** | **SEC-04 Fallback Secret Key (Section 8):** Hardcoded fallback key in `app.py`. | Verified. Line 29 contains `'fallback-dev-secret-key'`. | **VERIFIED** |
| **ST-16** | **SEC-05 CSP Absence (Section 8):** Absence of Content Security Policy header. | Verified. `@app.after_request` configures X-Frame-Options and X-Content-Type-Options, but no CSP header. | **VERIFIED** |
| **ST-17** | **Repository Hygiene - Root `static/` (Section 10 & 15):** Root `static/` is redundant duplicate; Deletion risk: Zero. | Disputed. Unsafe. `app.py` lines 1246–1251, 1325–1330 write to `../static/`, line 1599 writes return proofs to `../static/`, and `docker-compose.yml` mounts `./static/images/uploads`. | **DISPUTED** |
| **ST-18** | **Repository Hygiene - Backup File (Section 10):** `pre_phase12_20261103_025204.sql` is 0-byte corrupt file. | Verified. File size is 0 bytes and unreferenced. Safe to delete. | **VERIFIED** |
| **ST-19** | **Branch Discrepancy - `fetch_images.py` (Section 10 & 13):** Merge `agent/image` into `main`. | Partially Verified. The file exists on `agent/image`, but recommending a git branch merge is dangerous because `agent/image` diverged before Phase 12. Only cherry-pick or file checkout is safe. | **PARTIALLY VERIFIED** |
| **ST-20** | **Phase 13A Production Readiness (Section 3 & 14):** Dockerfile and WSGI configuration are complete and ready. | Disputed. `Dockerfile` crashes on startup with `ModuleNotFoundError: No module named 'db'` when running Gunicorn. Container startup was never tested. | **DISPUTED** |
| **ST-21** | **Cloud Database Migration - `CREATE USER` (Section 14):** `05_roles.sql` and `09_srs_alignment.sql` contain `CREATE USER ... @'localhost'`. | Partially Verified. `05_roles.sql` does contain `CREATE USER ... @'localhost'`, but `09_srs_alignment.sql` does NOT. Furthermore, `05_roles.sql` contains `FLUSH PRIVILEGES;`, which fails on Aiven due to lack of `RELOAD`. | **PARTIALLY VERIFIED** |
| **ST-22** | **Aiven Storage Allocation (Section 14):** Free tier provides 1 GB disk. | Disputed. Current official Aiven documentation confirms the active free tier allocation for MySQL is **5 GB disk**, not 1 GB. | **DISPUTED** |
| **ST-23** | **Local Academic Demonstration Verdict (Section 1 & 18):** 100% Ready for local demonstration. | Partially Verified. The Flask CLI runs smoothly (`python app/app.py`), but `test_app.py` has an active test failure (Test #10) due to Product #12 being at 0 stock. Product 12 must be replenished first. | **PARTIALLY VERIFIED** |

---

# 3. Incorrect or Unsupported Completion Claims

### 3.1 Phase 12A Traceability Matrix Artifact Disconnect (`docs/traceability.csv`)
The original audit marked Phase 12A as **PASS**, stating:
> *"All 63 SRS requirements ... are satisfied in code and documented in `docs/traceability.csv` ... 63/63 requirements mapped to active artifacts."*

**The Reality:**  
An automated cross-reference script between `docs/traceability.csv`, `app/app.py`, `app/templates/`, and `test_app.py` revealed significant fictional mappings:
1. **Fictional Test Function Names:** `docs/traceability.csv` maps requirements to specific pytest-style functions in `test_app.py`, including:
   - `test_cart_summary_calculation` (FR-01)
   - `test_guest_checkout_flow` (FR-02)
   - `test_accessible_form_labels` (AR-01)
   - `test_keyboard_navigation_focus` (AR-02)
   - `test_wcag_color_contrast` (AR-03)
   - `test_touch_target_dimensions` (AR-04)
   - `test_aria_alert_regions` (AR-05)
   - `test_sql_injection_defense` (AC-06.4)
   - `test_core_route_latency_under_1500ms` (OI-07)
   
   **None of these functions exist in `test_app.py`.** The test file `test_app.py` is a monolithic 295-line script with inline numbered procedural assertions inside `run_tests()`. The granular unit tests claimed in the matrix were never written.
2. **Missing Template Targets:** `docs/traceability.csv` claims requirements are mapped to templates that do not exist in `app/templates/`:
   - `app/templates/admin/delivery_rates.html` (FR-08) — Missing. Delivery rates has no dedicated admin UI.
   - `app/templates/seller/profile.html` (FR-17, AC-06.1) — Missing. Sellers have no dedicated profile page.
   - `app/templates/staff/ticket_detail.html` (AC-04.5) — Missing. Ticket management occurs in `staff/tickets.html`.
   - `app/templates/addresses.html` (AC-04.2) — Missing. Address editing is handled on the checkout page.
   - `app/templates/admin/abandoned_carts.html` (AC-08.3) — Missing. Abandoned carts are embedded in `admin/dashboard.html`.

**Verdict:** Claim of complete, verified 12A traceability is **DISPUTED**. The matrix was authored with planned targets rather than verified implementations.

---

### 3.2 Database Roles Count Discrepancy
The original report repeatedly asserted:
> *"19: 6 database roles, and 71 automated test assertions."*  
> *"70: 6 Role-Based Access Control Roles (Principle of Least Privilege)"*

**The Reality:**  
Inspection of `sql/05_roles.sql` and `sql/09_srs_alignment.sql` and the active MySQL `mysql.user` table reveals **exactly 4 database roles**:
1. `shop_admin` (defined in `05_roles.sql` line 31)
2. `shop_staff` (defined in `05_roles.sql` line 39)
3. `shop_customer` (defined in `05_roles.sql` line 53)
4. `shop_seller` (defined in `09_srs_alignment.sql` line 945)

`05_roles.sql` creates 3 test accounts (`test_admin`, `test_staff`, `test_customer`), not roles. The claim of "6 roles" is **DISPUTED**; the original auditor conflated roles with accounts or miscounted.

---

### 3.3 Foreign Key Count Understatement
The original report asserted:
> *"Foreign Key Integrity: 21 foreign key constraints verified with explicit cascading delete..."*

**The Reality:**  
Direct execution of SQL query against `INFORMATION_SCHEMA.KEY_COLUMN_USAGE` reveals **25 foreign key constraints** across the schema:
1. `addresses.user_id` -> `users.user_id`
2. `cart_items.cart_id` -> `carts.cart_id`
3. `cart_items.product_id` -> `products.product_id`
4. `carts.user_id` -> `users.user_id`
5. `categories.parent_category_id` -> `categories.category_id`
6. `order_items.order_id` -> `orders.order_id`
7. `order_items.product_id` -> `products.product_id`
8. `order_status_history.order_id` -> `orders.order_id`
9. `orders.address_id` -> `addresses.address_id`
10. `orders.user_id` -> `users.user_id`
11. `payment_attempts.order_id` -> `orders.order_id`
12. `payments.order_id` -> `orders.order_id`
13. `product_images.product_id` -> `products.product_id`
14. `products.brand_id` -> `brands.brand_id`
15. `products.category_id` -> `categories.category_id`
16. `products.supplier_id` -> `suppliers.supplier_id`
17. `return_requests.order_id` -> `orders.order_id`
18. `return_requests.product_id` -> `products.product_id`
19. `return_requests.user_id` -> `users.user_id`
20. `return_status_history.return_id` -> `return_requests.return_id`
21. `reviews.product_id` -> `products.product_id`
22. `reviews.user_id` -> `users.user_id`
23. `shipments.order_id` -> `orders.order_id`
24. `support_tickets.order_id` -> `orders.order_id`
25. `support_tickets.user_id` -> `users.user_id`

The original audit undercounted foreign key constraints by 4.

---

# 4. Critical Missing Findings Overlooked by Original Audit

The original audit failed to detect several severe architectural and operational defects:

### 4.1 Missing Finding 1: Gunicorn Module Import Crash (P0 Blocker)
In `Dockerfile` line 39:
```dockerfile
CMD ["gunicorn", "--config", "gunicorn_config.py", "app.app:app"]
```
When Gunicorn runs in the container (working directory `/app`), it attempts to load module `app.app`. Inside `app/app.py`, line 23 executes:
```python
from db import get_connection
```
Because the current working directory is `/app`, Python's `sys.path` does not include `/app/app`. Attempting to import `db` immediately fails:
```
ModuleNotFoundError: No module named 'db'
```
**Impact:** The containerized application crashes instantly upon startup. Any deployment using Gunicorn as configured will fail completely.  
**Why it was missed:** The subagents and the original auditor tested only via `test_app.py` (which explicitly does `sys.path.insert(0, app_dir)`) or `python app/app.py` from inside `app/`. No one ever executed Gunicorn or built the Docker container.

---

### 4.2 Missing Finding 2: Out-of-Order Database Initialization Crash in Docker (P0 Blocker)
In `docker-compose.yml` line 19:
```yaml
volumes:
  - ./sql:/docker-entrypoint-initdb.d:ro
```
When an official MySQL Docker container initializes, it executes all `.sql` scripts in `/docker-entrypoint-initdb.d` in **alphabetical order**:
1. `01_schema.sql`
2. `02_sample_data.sql`
3. `03_views_indexes.sql`
4. `04_procedures_triggers.sql`
5. `05_roles.sql`
6. `06_demo_queries.sql`
7. `07_tests.sql`  <-- **CRASH OCCURS HERE**
8. `08_catalog_expansion.sql`
9. `09_srs_alignment.sql`
10. `10_srs_alignment_fixes.sql`

At step 7, `07_tests.sql` executes `CALL sp_run_all_tests();`. Inside `sp_run_all_tests()`, Test 11 queries table `product_images` (created in script 08), Test 16 calls `sp_cart_summary` (created in script 09), Test 17 calls `sp_place_guest_order` (script 09), Test 19 queries `order_status_history` (script 09), and Test 25 queries `payment_attempts` (script 09).  
**Impact:** At step 7, none of these tables or stored procedures exist. MySQL halts initialization with fatal table/procedure not found errors. Docker Compose startup fails completely.

---

### 4.3 Missing Finding 3: Aiven `FLUSH PRIVILEGES;` Execution Failure (P1 Blocker)
In `sql/05_roles.sql` line 83:
```sql
FLUSH PRIVILEGES;
```
On Aiven for MySQL (and almost all cloud-managed MySQL services including AWS RDS and Azure Database for MySQL), the administrative user (`avnadmin`) is **not granted the `RELOAD` global privilege**. Executing `FLUSH PRIVILEGES;` results in:
```
ERROR 1227 (42000): Access denied; you need (at least one of) the RELOAD privilege(s) for this operation
```
**Impact:** Running `sql/05_roles.sql` against an Aiven instance will fail at line 83 unless this statement is removed or guarded. The original audit noted `CREATE USER ... @'localhost'` but missed the `FLUSH PRIVILEGES` privilege barrier.

---

### 4.4 Missing Finding 4: Return Proof Photo Upload Storage Disconnect
In `app/app.py` line 1599:
```python
save_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'returns')
os.makedirs(save_dir, exist_ok=True)
full_save = os.path.join(save_dir, sec_name)
file.save(full_save)
proof_path = f"static/images/returns/{sec_name}"
```
Notice that `save_dir` resolves to `D:\university\semister 3\DBS\DBS project\static\images\returns` (the **root** static folder).  
However, Flask's static folder is `app/static`. When `return_detail.html` or `seller/returns.html` renders:
```html
<img src="/{{ claim.proof_image_path }}">
```
The browser requests `/static/images/returns/...`. Flask looks inside `app/static/images/returns/...` where the file does **not** exist! This produces an immediate **HTTP 404 image error** for any uploaded return proof image!

---

### 4.5 Missing Finding 5: Deprecated `FLASK_ENV` Configuration in Flask 3.0+
In `app/app.py` lines 34–35:
```python
if os.getenv('FLASK_ENV') == 'production' or os.getenv('SESSION_COOKIE_SECURE', '0') == '1':
    app.config['SESSION_COOKIE_SECURE'] = True
```
In Flask 3.0.3, the environment variable `FLASK_ENV` is completely deprecated and ignored by Flask. While the custom check reads `os.getenv('FLASK_ENV')`, relying on this legacy variable creates a false sense of security. If a deployer configures modern Flask flags (`FLASK_DEBUG=0`), `SESSION_COOKIE_SECURE` remains `False`, leaving session cookies unencrypted over HTTPS.

---

### 4.6 Missing Finding 6: Missing Session Rotation on Login (Session Fixation Risk)
In `app/app.py` lines 183–188, when a user successfully authenticates, existing session values are overwritten:
```python
session['user'] = user['full_name']
session['user_id'] = user['user_id']
session['role'] = user['role']
```
However, the session cookie is not regenerated. This leaves the application susceptible to session fixation attacks, where an attacker pre-sets a guest session token and then gains authenticated access once the victim logs in.

---

# 5. Incorrect & Unsafe Cleanup Recommendations

Section 10 of `AUDIT_REPORT.md` provided a repository inventory and cleanup candidates. Several of these recommendations are **incorrect, incomplete, or unsafe**:

### 5.1 Recommendation: Delete Root `static/` Directory (UNSAFE)
- **Original Audit Claim:**  
  `static/` (root, 52 files) | **REMOVE CANDIDATE** | Exact duplicate of `app/static/`. Deletion risk: Zero. Action: Delete root `static/`.
- **Independent Verification:**  
  This recommendation would cause catastrophic application breakage:
  1. In `app/app.py` lines 1246–1251 (admin product add) and lines 1325–1330 (admin product edit):
     ```python
     root_dest = os.path.join(os.path.dirname(__file__), '..', rel_path)
     app_dest = os.path.join(os.path.dirname(__file__), rel_path)
     ...
     shutil.copyfile(app_dest, root_dest)
     ```
     The application code actively expects `root_dest` to exist and writes files to root `static/` on every product image upload.
  2. In `app/app.py` line 1599 (customer return proof upload):
     The application saves customer proof photos directly into `../static/images/returns/`.
  3. In `docker-compose.yml` line 50:
     ```yaml
     volumes:
       - ./static/images/uploads:/app/static/images/uploads
     ```
     Docker Compose explicitly mounts the root `static/images/uploads` directory.
- **Corrected Action:**  
  **DO NOT DELETE root `static/` yet.** The dual-directory structure is a code architectural defect in `app/app.py` and `docker-compose.yml`. Before any files are removed, `app/app.py` must first be refactored to use a single unified `UPLOAD_FOLDER`, and `docker-compose.yml` volume mounts must be synchronized. Deleting `static/` beforehand will crash image uploads and Docker Compose.

---

### 5.2 Recommendation: "Merge `agent/image` into `main`" (UNSAFE)
- **Original Audit Claim:**  
  `app/scripts/fetch_images.py` | **KEEP — DEVELOPMENT** | Critical Phase 11 image fetcher; exists on branch `agent/image` but missing on `main`. Action: "Merge agent/image into main" (Section 15, P2-05).
- **Independent Verification:**  
  Inspecting the Git branch graph shows that `agent/image` branched off commit `08186aa` during Phase 11C. Meanwhile, `main` has advanced through Phase 11D–11G, Phase 12A–12F, and Phase 13A (over 65 file modifications).  
  Running `git merge agent/image` would trigger extensive three-way merge conflicts across templates, tests, and documentation, risking accidental regression or deletion of Phase 12 deliverables.
- **Corrected Action:**  
  Do **NOT** merge the branch. Bring the single script over using:
  ```bash
  git checkout agent/image -- app/scripts/fetch_images.py
  ```
  or cherry-pick commit `d364f93` specifically.

---

### 5.3 Recommendation: Archive `docs/report_outline.md` (PARTIALLY FLAWED)
- **Original Audit Claim:**  
  Move `docs/report_outline.md` to `docs/archive/report_outline.md`. Deletion risk: None.
- **Independent Verification:**  
  `README.md` line 44 explicitly references `docs/report_outline.md` in its visual repository tree (`└── report_outline.md`). Moving the file without simultaneously updating `README.md` will produce a broken link in the repository's primary entry documentation.
- **Corrected Action:**  
  If moved to `docs/archive/`, `README.md` and `PROGRESS.md` must be updated in the same commit to avoid documentation rot.

---

### 5.4 Recommendation: Delete 0-Byte Backup File (VERIFIED)
- **File:** `backups/pre_phase12_20261103_025204.sql` (0 bytes).
- **Independent Verification:** Confirmed 0 bytes, corrupted aborted dump, unreferenced anywhere. Safe to delete.

---

# 6. Disputed Test Results & Test Harness Analysis

### 6.1 The Test #10 Failure in `test_app.py`
In Section 9 of `AUDIT_REPORT.md`, the auditor reported:
```
Total Tests Executed: 46
Passed: 45
Failed: 1 (Test #10: POST /checkout)
Error: FAILED: Oversell Error: Requested quantity exceeds available inventory stock.
```

**Independent Verification:**
- Direct query of `products` table in MySQL confirms:
  ```sql
  SELECT product_id, name, stock_quantity FROM products WHERE product_id = 12;
  -- Result: (12, 'J. Classic Cotton Kurta White', 0)
  ```
- Product #12 indeed has `stock_quantity = 0`.
- In `test_app.py`:
  - Test #7 adds 2 units of Product #12 to the cart.
  - Test #10 attempts to place the order via `sp_place_order`.
  - Database trigger `trg_before_order_items_insert` fires:
    ```sql
    IF NEW.quantity > v_stock THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Oversell Error: Requested quantity exceeds available inventory stock.';
    END IF;
    ```
- **Auditor Verdict:** The trigger worked exactly as engineered. However, this exposes a severe design defect in the integration test suite: **`test_app.py` has side-effects on the persistent development database**.
  - In addition to Product #12 being at 0, Product #1 has been depleted from 10 to 8, Product #2 has been depleted from 25 to 19, and Product #3 has been depleted to 4.
  - Continued execution of `test_app.py` will soon deplete Product #3, causing Test #45 (Cart Merge) to fail as well.
  - **Verdict:** VERIFIED that the test failed due to test pollution; DISPUTED that the web suite was in a passing state when Phase 12F was closed.

---

### 6.2 The Omission in `docs/srs_test_sheet.md`
In `MORNING_REPORT.md` (lines 32–37), the author claimed:
- `AC-02.1, AC-02.2, AC-02.3: PASS (100%)`
- `AC-03.1, AC-03.2: PASS (100%)`
- `AC-05.1 to AC-05.4: PASS (100%)`
- `AC-07.1 to AC-07.5: PASS (100%)`

**Independent Verification:**
Inspection of `docs/srs_test_sheet.md` reveals that:
- Under Category AC-02: only AC-02.1 and AC-02.2 exist. AC-02.3 is omitted.
- Under Category AC-03: only AC-03.1 exists. AC-03.2 is omitted.
- Under Category AC-05: only AC-05.1 exists. AC-05.2, AC-05.3, and AC-05.4 are omitted.
- Under Category AC-07: AC-07.2 and AC-07.3 are omitted.
- The sheet lists exactly 25 items because it skipped numbers, whereas `MORNING_REPORT.md` claimed sequential ranges.
- **Verdict:** PARTIALLY VERIFIED. The 25 documented criteria passed, but the documentation falsely claimed coverage of unwritten sub-criteria.

---

# 7. Additional Technical & Architectural Risks

The independent reviewer identified several technical risks not adequately highlighted in the original audit:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      RISK SEVERITY RADAR                               │
├───────────────────────────────┬────────────────────────────────────────┤
│ RISK AREA                     │ SEVERITY LEVEL                         │
├───────────────────────────────┼────────────────────────────────────────┤
│ Gunicorn Import Path Failure  │ CRITICAL (P0 - Deployment Showstopper) │
│ Docker Entrypoint SQL Order   │ CRITICAL (P0 - Deployment Showstopper) │
│ Form CSRF Vulnerability       │ HIGH (P1 - Cloud Security Blocker)     │
│ Cloud MySQL TLS & RELOAD      │ HIGH (P1 - Cloud Database Blocker)     │
│ Test Harness DB Pollution     │ MEDIUM (P2 - Developer Reliability)    │
│ Root/App Static Inconsistency │ MEDIUM (P2 - Data Integrity)           │
│ Render Cold Starts (60s)      │ LOW-MED (P3 - Academic Presentation)   │
└───────────────────────────────┴────────────────────────────────────────┘
```

1. **Aiven Free Tier Sleeping Policy:** Aiven automatically powers off free services that experience no activity. If powered off prior to the viva examination, waking the service can take several minutes.
2. **Render Ephemeral Filesystem Data Loss:** On Render's free tier, any images uploaded by an administrator at `/admin/product/add` are stored on local ephemeral container disk. When Render redeploys or restarts after 15 minutes of sleep, all newly uploaded images disappear.
3. **Absence of Database Connection Pooling:** PyMySQL opens a new TCP connection on every HTTP request. Over remote network connections to Aiven (round-trip time 150–250 ms from Pakistan), this will add noticeable latency to every page load unless a connection pool (e.g. `DBUtils`) is introduced.
4. **Depleted Test Stock During Examiner Demo:** If an examiner runs `python test_app.py` before testing the live site, Product #12 will fail, and subsequent manual attempts to purchase Product #12 or Product #3 will fail with unhandled errors.

---

# 8. Deployment Blockers Matrix

Below is the definitive, independent matrix of blockers preventing cloud staging and production deployment:

| Blocker ID | Severity | Category | Description | Exact Remediation Required |
| :---: | :---: | :---: | :--- | :--- |
| **BLK-01** | **P0 (Critical)** | Container / WSGI | Gunicorn crashes on boot: `ModuleNotFoundError: No module named 'db'`. | Add `PYTHONPATH=/app/app` to `Dockerfile` ENV, or add `sys.path.insert(0, os.path.dirname(__file__))` at top of `app/app.py`. |
| **BLK-02** | **P0 (Critical)** | Database / Docker | `07_tests.sql` executes before `08`, `09`, `10` during `/docker-entrypoint-initdb.d` initialization, crashing MySQL setup. | Rename `07_tests.sql` to `11_tests.sql` so it executes after all schema migrations, or exclude tests from entrypoint. |
| **BLK-03** | **P1 (High)** | Security | All 21 web forms lack anti-CSRF tokens. | Install `Flask-WTF`, initialize `CSRFProtect(app)`, and insert `{{ csrf_token() }}` in all 21 `<form method="post">` blocks. |
| **BLK-04** | **P1 (High)** | Cloud DB | `app/db.py` cannot connect to managed cloud MySQL over mandatory SSL/TLS. | Update `pymysql.connect` in `app/db.py` to support `ssl={'ca': ...}` when `DB_SSL_CA` is set. |
| **BLK-05** | **P1 (High)** | Cloud DB | `sql/05_roles.sql` contains `FLUSH PRIVILEGES;`, which throws Error 1227 on Aiven (no `RELOAD` privilege). | Remove `FLUSH PRIVILEGES;` from `05_roles.sql` or wrap in conditional check. |
| **BLK-06** | **P1 (High)** | Version Control | No Git remote repository configured. | Create GitHub repository and execute `git remote add origin <url>` and `git push -u origin main`. |
| **BLK-07** | **P2 (Medium)** | Architecture | Dual static folder confusion: return proof photos saved to root `static/` instead of `app/static/`. | Unify upload paths in `app/app.py` (lines 1246, 1325, 1599) to point strictly to `app/static/images/` and update `docker-compose.yml`. |
| **BLK-08** | **P2 (Medium)** | Test Harness | `test_app.py` depletes live database stock (Product 12 stock = 0). | Add a test fixture in `test_app.py` to replenish stock of test products (1, 2, 3, 12) before and after test execution. |

---

# 9. Corrected Roadmap Status

Below is the verified status of all roadmap phases, comparing the original claims in `PROGRESS.md` / `AUDIT_REPORT.md` against independent verification:

| Phase | Description | Original Audit Status | Independent Review Status | Variance / Reason |
| :---: | :--- | :---: | :---: | :--- |
| **0** | Environment, Python & MySQL 8 Setup | **PASS** | **VERIFIED PASS** | Python 3.14 + MySQL 8.0.46 confirmed. |
| **1** | Requirements & ER Design | **PASS** | **VERIFIED PASS** | 13 baseline entities, 3NF design documented. |
| **2** | Baseline Schema (`01_schema.sql`) | **PASS** | **VERIFIED PASS** | Baseline DDL verified in MySQL. |
| **3** | Sample Data (`02_sample_data.sql`) | **PASS** | **VERIFIED PASS** | Realistic PKR data loaded. |
| **4** | Views & Indexes (`03_views_indexes.sql`) | **PASS** | **VERIFIED PASS** | 5 analytical views and B-Tree indexes verified. |
| **5** | Procedures & Triggers (`04_procedures_triggers.sql`) | **PASS** | **VERIFIED PASS** | `sp_place_order`, stock decrement, ACID rollback verified. |
| **6** | Roles & Privileges (`05_roles.sql`) | **PASS** | **PARTIALLY VERIFIED** | RBAC verified locally, but `FLUSH PRIVILEGES` breaks on cloud. |
| **7** | Demo Queries (`06_demo_queries.sql`) | **PASS** | **VERIFIED PASS** | Demonstration queries Sections 1–9 verified. |
| **8** | Web UI Storefront & Auth | **PASS** | **VERIFIED PASS** | Storefront, cart, checkout UI functional. |
| **9** | Testing (`07_tests.sql`) | **PASS** | **PARTIALLY VERIFIED** | 10/10 tests pass, but script depends on later phases. |
| **10** | Academic Report & Viva Defense | **PASS** | **VERIFIED PASS** | 25,000+ word final report and viva notes verified. |
| **11A** | Multi-Image & Brand Schema (`08_catalog_expansion.sql`) | **PASS** | **VERIFIED PASS** | Brands, product_images, single primary trigger verified. |
| **11B** | Catalog Data Pipeline (51 products) | **PASS** | **VERIFIED PASS** | Manifest and importer verified (81 active products). |
| **11C** | Image Acquisition & Fallback Specimen | **PARTIAL** | **PARTIAL** | Specimen images on disk; `fetch_images.py` unmerged on `agent/image`. |
| **11D** | Department Browsing UI | **PASS** | **VERIFIED PASS** | Category hierarchy, subcategory chips, filters verified. |
| **11E** | Product Gallery UI | **PASS** | **VERIFIED PASS** | Multi-image thumbnail switcher verified. |
| **11F** | Admin Media Management | **PASS** | **PARTIALLY VERIFIED** | Validations work, but dual-static save path defect exists. |
| **11G** | Phase 11 Finalization & Tests T11–T15 | **PASS** | **VERIFIED PASS** | Tests T11–T15 pass in database. |
| **12A** | Requirements Traceability Matrix | **PASS** | **DISPUTED** | Matrix maps to 40+ non-existent test functions and 5 non-existent templates. |
| **12B** | Schema Alignment (`09_srs_alignment.sql`) | **PASS** | **VERIFIED PASS** | 8 new tables, matrices, procedures, and triggers verified. |
| **12C** | Checkout, Pricing & Payment Adapter | **PASS** | **VERIFIED PASS** | Guest token, `sp_merge_carts`, `sp_cart_summary`, sandbox verified. |
| **12D** | Order Tracking, Support & Returns | **PASS** | **VERIFIED PASS** | Tracking timeline, tickets, return claims, overdue view verified. |
| **12E** | Quality & Accessibility | **PASS** | **VERIFIED PASS** | Semantic labels, 44px touch targets, 12 screenshots verified. |
| **12F** | Acceptance Verification & Viva Defense | **PASS** | **PARTIALLY VERIFIED** | 25 ACs documented; web test suite has 1 failing test (Test #10). |
| **13A** | Production Readiness (Configs & WSGI) | **PARTIAL** | **DISPUTED / BLOCKED** | Gunicorn cannot import `db`; Docker initialization order broken; no CSRF. |
| **13B** | Cloud Database Setup (Aiven) | **NOT STARTED** | **NOT STARTED** | Awaiting P1 prerequisites. |
| **13C** | Cloud Web Service (Render) | **NOT STARTED** | **NOT STARTED** | Awaiting P0/P1 prerequisites. |
| **13D** | Persistent Media Storage | **NOT STARTED** | **NOT STARTED** | Ephemeral storage risks identified. |
| **13E** | Domain & PWA Manifest | **NOT STARTED** | **NOT STARTED** | Not started. |
| **13F** | Monitoring & Backups | **NOT STARTED** | **NOT STARTED** | Local backups exist; cloud monitoring not started. |
| **13G** | Demonstration Rehearsal | **NOT STARTED** | **NOT STARTED** | Not started. |

---

# 10. Final Independent GO / NO-GO Recommendation

The independent technical review establishes four clear, non-conflated readiness levels:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   DEPLOYMENT READINESS SUMMARY                         │
├──────────────────────────────────────┬─────────────────────────────────┤
│ DEPLOYMENT LEVEL                     │ INDEPENDENT VERDICT             │
├──────────────────────────────────────┼─────────────────────────────────┤
│ 1. Local Demonstration (Flask CLI)   │ GO (Conditionally Ready)       │
│ 2. Local Container (Docker Compose)  │ NO-GO (Blocked by P0 Defect)    │
│ 3. Cloud Staging Deployment          │ NO-GO (Blocked by P0/P1)        │
│ 4. Public Academic Demonstration     │ NO-GO (Blocked by P0/P1)        │
│ 5. Real Commercial Production        │ NO-GO (Out of CEP Scope)        │
└──────────────────────────────────────┴─────────────────────────────────┘
```

### Detailed Justifications:

1. **Local Academic Demonstration (Flask CLI):** **GO (CONDITIONALLY READY)**
   - **Condition:** Must run `UPDATE products SET stock_quantity = 15 WHERE product_id = 12;` before demonstrating to the examiner, so that `test_app.py` passes 46/46 and live checkout works smoothly.
   - **Rationale:** When running via standard development server (`python app/app.py`), the application connects reliably to local MySQL 8, all 23 domain entities in 3NF are operational, all 10 triggers fire correctly, all 8 stored procedures calculate pricing without drift, and all storefront/admin templates render cleanly.

2. **Local Container Demonstration (Docker Compose):** **NO-GO**
   - **Rationale:** `docker compose up` will fail due to:
     1. Gunicorn failing to import `db` in `app/app.py` (BLK-01).
     2. MySQL entrypoint running `07_tests.sql` before `08` and `09`, causing container database initialization failure (BLK-02).

3. **Cloud Staging Deployment (Render + Aiven):** **NO-GO**
   - **Rationale:** Deploying to Render and Aiven today will immediately fail due to:
     - Gunicorn startup crash on Render (BLK-01).
     - Missing SSL/TLS support in `app/db.py` (BLK-04).
     - `FLUSH PRIVILEGES;` execution denial on Aiven (BLK-05).
     - Missing Git remote repository (BLK-06).

4. **Public Academic Demonstration:** **NO-GO**
   - **Rationale:** A public link cannot be shared until Cloud Staging is fully operational, hardened with CSRF protection (BLK-03), and verified over two consecutive clean test runs.

5. **Real Commercial Production:** **NO-GO**
   - **Rationale:** The payment gateway is purely simulated (by academic CEP design), email dispatch is unconfigured, and user uploads are stored on ephemeral local disk.

---

# 11. Exact Remaining Work Required Before Implementation Begins

In accordance with strict audit rules, no code or database changes have been applied during this verification. The following **exact engineering work packages** must be formally approved before implementation begins:

### Work Package 1: P0 & P1 Deployment Unblocking (Estimated Time: 1.5 Hours)
1. **Fix WSGI Import Path in `app/app.py`:**
   Insert `sys.path.insert(0, os.path.dirname(__file__))` at the top of `app/app.py` so that both `from db import get_connection` and Gunicorn invocation (`app.app:app`) resolve seamlessly regardless of execution working directory.
2. **Fix SQL Script Execution Order for Docker:**
   Rename `sql/07_tests.sql` to `sql/11_tests.sql` (or move out of `/docker-entrypoint-initdb.d`), ensuring all tables, procedures, views, and fixes from scripts `08`, `09`, and `10` exist before the test suite is called.
3. **Add Database TLS/SSL Support in `app/db.py`:**
   Update `pymysql.connect` in `app/db.py` to accept an optional `DB_SSL_CA` environment variable, passing `ssl={'ca': os.getenv('DB_SSL_CA')}` when present.
4. **Remove `FLUSH PRIVILEGES;` from `sql/05_roles.sql`:**
   Delete line 83 (`FLUSH PRIVILEGES;`) or wrap it so cloud database initialization does not fail under restricted privileges on Aiven.
5. **Integrate CSRF Protection:**
   Add `Flask-WTF` to `requirements.txt`, initialize `CSRFProtect(app)` in `app/app.py`, and add `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>` to all 21 `<form method="post">` blocks across `app/templates/`.

### Work Package 2: Test Suite Isolation & Restock (Estimated Time: 30 Minutes)
1. **Replenish Stock of Test Products:**
   Execute SQL statement to restore test products to baseline quantities:
   ```sql
   UPDATE products SET stock_quantity = 15 WHERE product_id = 12;
   UPDATE products SET stock_quantity = 10 WHERE product_id = 1;
   UPDATE products SET stock_quantity = 25 WHERE product_id = 2;
   UPDATE products SET stock_quantity = 10 WHERE product_id = 3;
   ```
2. **Add Teardown / Restock Fixture in `test_app.py`:**
   Add an automated pre-test replenishment helper in `test_app.py` so running the test suite repeatedly never depletes inventory to 0, ensuring perpetual 46/46 (100%) test passes.

### Work Package 3: Static Asset Path Alignment (Estimated Time: 45 Minutes)
1. **Unify Upload Paths in `app/app.py`:**
   - Modify lines 1246–1251 and lines 1325–1330 in `app/app.py` to save uploaded product images strictly into `app/static/images/products/uploads/`, eliminating `shutil.copyfile(app_dest, root_dest)`.
   - Modify line 1599 in `app/app.py` to save return proof photos to `app/static/images/returns/` instead of `../static/images/returns/`, eliminating the 404 image bug.
   - Update `docker-compose.yml` line 50 to mount `./app/static/images/uploads:/app/static/images/uploads`.
2. **Safely Import `fetch_images.py`:**
   Extract the image fetching script without merging the diverged branch:
   ```bash
   git checkout agent/image -- app/scripts/fetch_images.py
   ```
3. **Delete 0-Byte Corrupt Backup:**
   Remove `backups/pre_phase12_20261103_025204.sql`.

### Work Package 4: Documentation Alignment (Estimated Time: 30 Minutes)
1. **Correct `docs/traceability.csv`:**
   Update `Test_Target` entries to reflect actual test descriptions in `test_app.py` rather than non-existent function names, and update `Template_Target` entries to reflect actual template locations (e.g. `admin/dashboard.html` for abandoned carts).
2. **Synchronize `docs/srs_test_sheet.md`:**
   Cleanly note that 25 distinct core acceptance criteria are evaluated, removing references to skipped sub-criteria numbers.

---

*Report independently prepared and certified by:*  
**Lead Independent Technical Quality & Compliance Reviewer**  
Mehran University of Engineering and Technology (MUET) DBMS CEP Verification