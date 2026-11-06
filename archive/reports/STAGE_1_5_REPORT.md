# STAGE 1.5 REPORT: FINAL TECHNICAL CORRECTIONS

**Project:** Online Shopping Database Management System (DBMS CEP)  
**Institution:** Mehran University of Engineering and Technology, Jamshoro  
**Department:** Department of Computer Systems Engineering  
**Phase:** Final Stabilization  
**Stage:** 1.5 of 4 (Technical Corrections & Reconciliation)  
**Execution Date:** 2026-11-04  
**Overall Status:** **COMPLETE (100% Verified)**  
**Gate Recommendation:** **GO FOR STAGE 2 (REPOSITORY CLEANUP)**  

---

## 1. Executive Summary

Stage 1.5 was initiated to resolve three critical technical concerns identified following the initial Stage 1 remediation:
1. **Database Object Count Inconsistency:** An apparent discrepancy between reports identifying 24 tables / 8 routines vs. clean initialization identifying 23 tables / 7 routines.
2. **Insecure Flask Secret Key Fallback:** A predictable default secret key fallback (`'fallback-dev-secret-key'`) that could compromise session security and CSRF integrity if deployed to production.
3. **Database Credential Exposure:** An embedded database root password observed in test commands and legacy utility scripts.

All three concerns have been comprehensively investigated, resolved, and verified.
* The database object discrepancy is completely explained: clean deployment initialization yields **23 Base Tables, 9 Views, 7 Stored Procedures, 0 Functions, and 10 Triggers** (49 production objects). The 24th table (`test_results`) and 8th procedure (`sp_run_all_tests`) are dedicated test runner fixtures created by `sql/11_tests.sql`.
* Flask secret key management now enforces strict, environment-specific policies: production refuses application startup if `FLASK_SECRET_KEY` is missing, short (< 16 chars), or set to an insecure placeholder.
* All hardcoded credentials have been eradicated from application code, test scripts, and documentation, transitioning to interactive CLI prompts (`mysql -u <user> -p <db>`). The affected `root` database account has been formally flagged for user credential rotation.
* Across all test suites, **49 of 49 Flask integration tests**, **7 of 7 Secret Key unit tests**, **6 of 6 TLS/SSL tests**, and **25 of 25 MySQL engine tests** passed with zero defects. The development database (`online_shop`) remains 100% pristine and untouched.

---

## 2. Work Package A — Database Object Reconciliation

### 2.1 The Problem & Investigation
The previous audit noted that one report recorded 24 tables, 9 views, 8 routines, and 10 triggers, while clean initialization reported 23 tables, 9 views, 7 routines, and 10 triggers.

To determine the ground truth, `information_schema` was queried across:
1. The development database (`online_shop`).
2. The isolated test database (`online_shop_test`).
3. The clean initialization scripts in `sql/init/` (01 through 08).
4. A fresh disposable database initialized from scratch (`online_shop_disposable_stage15`).

### 2.2 Named Object Comparison Table

| Object Name | Object Type | Exists in `sql/init/`? | Exists in `online_shop`? | Exists in `online_shop_test`? | Required by SRS? | Required by Web App? | Impact of Absence |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **addresses** | BASE TABLE | YES (01) | YES | YES | YES | YES | Critical |
| **audit_log** | BASE TABLE | YES (01) | YES | YES | YES | NO (Trigger-only) | Critical |
| **brands** | BASE TABLE | YES (06) | YES | YES | YES | YES | Critical |
| **cart_items** | BASE TABLE | YES (01) | YES | YES | YES | YES | Critical |
| **carts** | BASE TABLE | YES (01) | YES | YES | YES | YES | Critical |
| **categories** | BASE TABLE | YES (01) | YES | YES | YES | YES | Critical |
| **delivery_rates** | BASE TABLE | YES (07) | YES | YES | YES | YES | Critical |
| **order_items** | BASE TABLE | YES (01) | YES | YES | YES | YES | Critical |
| **order_status_history** | BASE TABLE | YES (07) | YES | YES | YES | YES | Critical |
| **orders** | BASE TABLE | YES (01) | YES | YES | YES | YES | Critical |
| **payment_attempts** | BASE TABLE | YES (07) | YES | YES | YES | YES | Critical |
| **payment_methods** | BASE TABLE | YES (07) | YES | YES | YES | YES | Critical |
| **payments** | BASE TABLE | YES (01) | YES | YES | YES | YES | Critical |
| **product_images** | BASE TABLE | YES (06) | YES | YES | YES | YES | Critical |
| **products** | BASE TABLE | YES (01) | YES | YES | YES | YES | Critical |
| **return_requests** | BASE TABLE | YES (07) | YES | YES | YES | YES | Critical |
| **return_status_history** | BASE TABLE | YES (07) | YES | YES | YES | YES | Critical |
| **reviews** | BASE TABLE | YES (01) | YES | YES | YES | YES | Critical |
| **shipments** | BASE TABLE | YES (01) | YES | YES | YES | YES | Critical |
| **suppliers** | BASE TABLE | YES (01) | YES | YES | YES | YES | Critical |
| **support_tickets** | BASE TABLE | YES (07) | YES | YES | YES | YES | Critical |
| **tax_rates** | BASE TABLE | YES (07) | YES | YES | YES | YES | Critical |
| **users** | BASE TABLE | YES (01) | YES | YES | YES | YES | Critical |
| **test_results** | BASE TABLE | **NO (11_tests.sql)** | YES | YES | **NO** | **NO** | **Zero application impact (Test harness fixture)** |
| **v_abandoned_carts** | VIEW | YES (07) | YES | YES | YES | YES | Critical |
| **v_best_sellers** | VIEW | YES (03) | YES | YES | YES | YES | Critical |
| **v_category_counts** | VIEW | YES (06) | YES | YES | YES | YES | Critical |
| **v_low_stock** | VIEW | YES (03) | YES | YES | YES | YES | Critical |
| **v_order_summary** | VIEW | YES (03) | YES | YES | YES | YES | Critical |
| **v_overdue_return_requests** | VIEW | YES (07) | YES | YES | YES | YES | Critical |
| **v_product_catalog** | VIEW | YES (06) | YES | YES | YES | YES | Critical |
| **v_sales_by_category** | VIEW | YES (03) | YES | YES | YES | YES | Critical |
| **v_sellers** | VIEW | YES (07) | YES | YES | YES | YES | Critical |
| **sp_cancel_order** | PROCEDURE | YES (04) | YES | YES | YES | YES | Critical |
| **sp_cart_summary** | PROCEDURE | YES (07) | YES | YES | YES | YES | Critical |
| **sp_mark_abandoned_carts**| PROCEDURE | YES (07) | YES | YES | YES | YES | Critical |
| **sp_merge_carts** | PROCEDURE | YES (07) | YES | YES | YES | YES | Critical |
| **sp_place_guest_order** | PROCEDURE | YES (07) | YES | YES | YES | YES | Critical |
| **sp_place_order** | PROCEDURE | YES (04) | YES | YES | YES | YES | Critical |
| **sp_set_product_primary_image**| PROCEDURE | YES (06) | YES | YES | YES | YES | Critical |
| **sp_run_all_tests** | PROCEDURE | **NO (11_tests.sql)** | YES | YES | **NO** | **NO** | **Zero application impact (Test runner procedure)** |
| *(Stored Functions)* | FUNCTION | None (0) | None (0)| None (0) | NO | NO | None |
| **trg_after_orders_update_audit** | TRIGGER | YES (04) | YES | YES | YES | N/A (Engine) | Critical |
| **trg_after_order_items_insert** | TRIGGER | YES (04) | YES | YES | YES | N/A (Engine) | Critical |
| **trg_before_order_items_insert**| TRIGGER | YES (04) | YES | YES | YES | N/A (Engine) | Critical |
| **trg_before_reviews_insert** | TRIGGER | YES (04) | YES | YES | YES | N/A (Engine) | Critical |
| **trg_order_initial_status_history**| TRIGGER | YES (07) | YES | YES | YES | N/A (Engine) | Critical |
| **trg_order_status_history** | TRIGGER | YES (07) | YES | YES | YES | N/A (Engine) | Critical |
| **trg_product_images_single_primary_bi**| TRIGGER | YES (06) | YES | YES | YES | N/A (Engine) | Critical |
| **trg_product_images_single_primary_bu**| TRIGGER | YES (06) | YES | YES | YES | N/A (Engine) | Critical |
| **trg_return_initial_status_history**| TRIGGER | YES (07) | YES | YES | YES | N/A (Engine) | Critical |
| **trg_return_status_history**| TRIGGER | YES (07) | YES | YES | YES | N/A (Engine) | Critical |

### 2.3 Reconciliation Conclusion: Outcome A (Reporting Discrepancy)
The discrepancy is 100% accounted for by the intentional separation between production schema scripts and test execution harnesses:
* **Production Deployment Schema (`sql/init/` 01–08):**
  * **23 Base Tables** (100% of SRS domain tables)
  * **9 Views**
  * **7 Stored Procedures** (100% of production procedures)
  * **0 Stored Functions**
  * **10 Database Triggers**
  * *Total Production Objects: 49*
* **Test Database Schema (`online_shop_test` after running `sql/11_tests.sql`):**
  * **24 Base Tables** (23 production tables + 1 `test_results` fixture table)
  * **9 Views**
  * **8 Stored Procedures** (7 production procedures + 1 `sp_run_all_tests` test runner procedure)
  * **0 Stored Functions**
  * **10 Database Triggers**
  * *Total Objects in Test Environment: 51*

No required production objects are missing. Clean initialization reproducibility was verified by creating disposable database `online_shop_disposable_stage15`, verifying all 49 clean objects, executing the 25 MySQL test assertions, and verifying the addition of the 2 test objects.

---

## 3. Work Package B — Flask Secret Key Security

### 3.1 Problem Identified
The initial remediation left a default fallback `'fallback-dev-secret-key'` in `app/app.py`. A predictable key in production exposes user session cookies to tampering and compromises CSRF tokens.

### 3.2 Implementation & Hardening
1. **Explicit Environment Resolution:** Implemented `resolve_app_environment()` checking `APP_ENV` first, falling back to `FLASK_ENV`, `PRODUCTION=1`, and `TESTING=1`.
2. **Environment-Specific Policies:**
   * **Development (`APP_ENV=development`):** Loads `FLASK_SECRET_KEY` from `.env`. If unset or empty, dynamically generates an ephemeral, cryptographically secure 64-char hex key (`secrets.token_hex(32)`).
   * **Testing (`APP_ENV=testing`):** Employs an isolated testing secret key, ensuring tests never reuse production secrets.
   * **Production (`APP_ENV=production`):** Mandatory `FLASK_SECRET_KEY` requirement. Startup is strictly refused with a clear `RuntimeError` under any of the following conditions:
     - The variable is unset or empty.
     - The key is shorter than 16 characters.
     - The key matches known insecure placeholders (`default_dev_key`, `fallback-dev-secret-key`, `change_this_to_a_random_string`, `your_secret_key_here`, `muet-dbs-production-secret-2026`).
3. **Deployment Configuration Alignment:**
   * `docker-compose.yml`: Removed the default `${FLASK_SECRET_KEY:-muet-dbs-production-secret-2026}` fallback; mapped directly to `${FLASK_SECRET_KEY}` with `APP_ENV: production`.
   * `Dockerfile`: Added `APP_ENV=production` to base environment variables.
   * `.env.example`: Documented `APP_ENV=development` and command for generating 32-byte production keys (`python -c "import secrets; print(secrets.token_hex(32))"`).

### 3.3 Verification
Authored and executed `test_secret_key.py` (7/7 tests passed):
* Development custom key: PASS
* Development ephemeral auto-generation: PASS
* Testing isolated key: PASS
* Production valid key initialization: PASS
* Production missing key startup refusal (`RuntimeError`): PASS
* Production short key refusal (`RuntimeError`): PASS
* Production placeholder rejection (`RuntimeError`): PASS

---

## 4. Work Package C — Credential Exposure

### 4.1 Findings & Locations
An automated scan of all workspace files identified genuine database root credentials and embedded passwords in four distinct locations:

1. **`app/scripts/import_catalog.py` (Line 27):**
   * *Finding:* `DB_PASS = os.getenv('DB_PASS', '[REDACTED DATABASE CREDENTIAL]')`
   * *Status:* Remediated. Replaced with `DB_PASS = os.getenv('DB_PASSWORD') or os.getenv('DB_PASS', '')`.
2. **`docs/demo_guide.md` (Line 71):**
   * *Finding:* `mysql.exe -u root -p[REDACTED DATABASE CREDENTIAL] online_shop`
   * *Status:* Remediated. Replaced with interactive prompt: `mysql -u root -p online_shop`.
3. **`docs/demo_guide.md` (Line 102):**
   * *Finding:* `mysql.exe -u test_customer -p[REDACTED DATABASE CREDENTIAL] online_shop`
   * *Status:* Remediated. Replaced with interactive prompt: `mysql -u test_customer -p online_shop`.
4. **`STAGE_1_TEST_RESULTS.md` (Line 166):**
   * *Finding:* `mysql.exe -u root -p[REDACTED DATABASE CREDENTIAL] online_shop_test < sql\11_tests.sql`
   * *Status:* Remediated. Sanitized to: `mysql -u root -p online_shop_test < sql/11_tests.sql`.

### 4.2 Git History Audit
The root database credential was found in historical Git commits:
* Commit `9ac07d4` (`app/scripts/import_catalog.py`)
* Commit `950a35d` (`docs/demo_guide.md`)

*Note:* In accordance with strict audit instructions, Git history was not rewritten.

### 4.3 Operational Recommendation: Mandatory User Credential Rotation
Because the MySQL `root` account password appeared in Git history and local logs, **immediate user credential rotation is required**.
* **Action for User / Operator:** Execute on local MySQL:
  ```sql
  ALTER USER 'root'@'localhost' IDENTIFIED BY 'YOUR_NEW_SECURE_PASSWORD';
  FLUSH PRIVILEGES;
  ```
* **Configuration:** Update the new password in your uncommitted, private local `.env` file:
  ```ini
  DB_PASSWORD=YOUR_NEW_SECURE_PASSWORD
  ```

---

## 5. Summary of Files Modified & Created

### 5.1 Modified Files
1. `app/app.py`: Implemented `resolve_app_environment()` and `configure_secret_key()` with production startup refusal.
2. `app/db.py`: Added `APP_ENV == 'production'` check to `get_ssl_config()`.
3. `app/scripts/import_catalog.py`: Removed hardcoded database password fallback.
4. `sql/11_tests.sql`: Refactored Test 11 (`T11`) to ensure self-contained primary image test execution.
5. `docker-compose.yml`: Removed default secret key fallback; added `APP_ENV: production`.
6. `Dockerfile`: Added `APP_ENV=production`.
7. `.env.example`: Documented `APP_ENV` and key generation instructions.
8. `docs/demo_guide.md`: Sanitized MySQL CLI commands to use interactive password prompting.
9. `STAGE_1_TEST_RESULTS.md`: Sanitized MySQL command logs.

### 5.2 Created Files
1. `test_secret_key.py`: Automated unit test suite verifying secret key security policies.
2. `STAGE_1_5_REPORT.md`: This comprehensive technical corrections report.
3. `STAGE_1_5_TEST_RESULTS.md`: Detailed test output evidence.
4. `STAGE_1_5_CHANGELOG.md`: Detailed itemized file changelog.

---

## 6. Regression Testing Summary

| Test Suite | Total Tests | Passed | Failed | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Flask Integration Suite (`test_app.py`)** | 49 | 49 | 0 | **PASS** |
| **Secret Key Security Suite (`test_secret_key.py`)** | 7 | 7 | 0 | **PASS** |
| **Database Engine Suite (`sql/11_tests.sql`)** | 25 | 25 | 0 | **PASS** |
| **Database TLS/SSL Suite (`test_ssl_db.py`)** | 6 | 6 | 0 | **PASS** |
| **Clean Init Object Reconciliation** | 49 objects | 49 | 0 | **PASS** |
| **Post-Test Object Reconciliation** | 51 objects | 51 | 0 | **PASS** |
| **TOTAL** | **187 assertions/checks** | **187** | **0** | **100% PASS** |

### Core Functionality Verification
* **Customer Registration & Login:** Verified (`test_app.py` lines 145–147).
* **Catalog Browsing & Search:** Verified (`test_app.py` lines 140–144).
* **Shopping Cart & Single-Source Pricing:** Verified (`test_app.py` lines 148–150, 169–170).
* **Guest & Authenticated Checkout:** Verified (`test_app.py` lines 151, 171).
* **Payment Simulation & Fallback to COD:** Verified (`test_app.py` lines 172–174).
* **Order Status Tracking:** Verified (`test_app.py` line 175).
* **Customer Returns & Seller Queue:** Verified (`test_app.py` lines 180–182).
* **Seller Verification Governance:** Verified (`test_app.py` lines 178–179).
* **Administrative Operations & Reports:** Verified (`test_app.py` lines 153–158, 183).

---

## 7. Remaining Limitations & Operational Tasks

1. **MySQL Root Credential Rotation:**
   * The genuine local database root password appeared in historical Git commits (`9ac07d4`, `950a35d`).
   * As Git history was intentionally preserved without rewriting, the operator must rotate the root password on their local MySQL instance and update `.env`.
2. **Catalog Image Downloads:**
   * Automated scrapers for Pakistani fashion brand images encounter anti-bot challenges (403); high-fidelity local specimens in `static/images/` remain in active use, ensuring zero 404 broken images exist in the storefront.

---

## 8. Final Stage 1.5 Verdict

**Status:** **`COMPLETE` (100% Verified)**  
**Gate Recommendation:** **`GO FOR STAGE 2 (REPOSITORY CLEANUP)`**  

All technical blockers, object count inconsistencies, security fallbacks, and credential exposures have been fully resolved. The project is completely stable, secure, test-isolated, and ready for Stage 2 repository cleanup upon user authorization.
