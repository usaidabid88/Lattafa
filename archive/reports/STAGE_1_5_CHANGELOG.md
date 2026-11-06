# STAGE 1.5 CHANGELOG — Final Technical Corrections

**Project:** Online Shopping Database Management System (DBMS CEP)  
**Institution:** Mehran University of Engineering and Technology, Jamshoro  
**Phase:** Final Stabilization  
**Stage:** 1.5 of 4 (Technical Corrections & Reconciliation)  
**Date:** 2026-11-04  
**Status:** COMPLETED & VERIFIED  

---

## 1. Summary of Changes

Stage 1.5 resolves the three outstanding technical findings identified during the Stage 1 review:
1. Reconciled database object count discrepancies between clean initialization and post-test schemas.
2. Eliminated insecure Flask secret key fallbacks and implemented strict environment-aware secret key enforcement with startup refusal in production.
3. Completely eradicated hardcoded credentials from codebase files, application scripts, and demonstration guides, establishing interactive credential prompting.

---

## 2. Itemized File Changelog

### 2.1 Core Application Code

#### `app/app.py`
* **Work Package:** B (Flask Secret Key Security)
* **Change Type:** Modified
* **Description:**
  * Implemented `resolve_app_environment()` prioritizing `APP_ENV` over deprecated `FLASK_ENV`.
  * Implemented `configure_secret_key(app_instance)`:
    * In **Development**: Loads `FLASK_SECRET_KEY` from `.env`; if absent or unset, generates an ephemeral, cryptographically secure 64-char hex key via `secrets.token_hex(32)`.
    * In **Testing**: Applies an isolated testing secret key, preventing cross-environment credential contamination.
    * In **Production**: Strictly requires `FLASK_SECRET_KEY` to be passed via the deployment environment. Enforces minimum length (>= 16 characters) and validates against known insecure placeholders (`default_dev_key`, `fallback-dev-secret-key`, `change_this_to_a_random_string`, `your_secret_key_here`, `muet-dbs-production-secret-2026`). Raises `RuntimeError` on violation, refusing startup.
  * Updated production session cookie security check to evaluate `resolve_app_environment() == 'production'`.
* **Justification:** Eliminates predictability vulnerabilities in session cookies and CSRF token generation; prevents deployment with placeholder secrets.
* **Verification:** Verified via `test_secret_key.py` (7/7 tests passed) and `test_app.py` (49/49 tests passed).

#### `app/db.py`
* **Work Package:** B (Flask Secret Key Security)
* **Change Type:** Modified
* **Description:** Updated line 28 to check `os.getenv('APP_ENV') == 'production'` alongside `FLASK_ENV` and `PRODUCTION` flags.
* **Justification:** Unifies environment resolution across database and web application layers.
* **Verification:** Verified via `test_ssl_db.py` (6/6 tests passed).

#### `app/scripts/import_catalog.py`
* **Work Package:** C (Credential Exposure)
* **Change Type:** Modified
* **Description:** Line 27: Replaced hardcoded default root password fallback `DB_PASS = os.getenv('DB_PASS', '090078601')` with `DB_PASS = os.getenv('DB_PASSWORD') or os.getenv('DB_PASS', '')`.
* **Justification:** Prevents hardcoded database credentials from residing in utility scripts.
* **Verification:** Verified via `credential_scanner.py`; script runs cleanly with `.env` credentials.

---

### 2.2 Database & SQL Scripts

#### `sql/11_tests.sql`
* **Work Package:** A (Database Object Reconciliation)
* **Change Type:** Modified
* **Description:** Refactored Test 11 (`T11` Duplicate Primary Image Rejection) to check if product 1 already has a primary image; if not, inserts an initial primary image before asserting that a second primary image is rejected with `SQLSTATE 45000`. Ensures initial primary image is cleaned up on completion.
* **Justification:** Makes `sql/11_tests.sql` 100% self-contained and reproducible even on a pristine database that has not yet run catalog image seeding scripts.
* **Verification:** Verified by executing against clean disposable database `online_shop_disposable_stage15`: 25/25 PASS.

---

### 2.3 Configuration & Documentation

#### `docker-compose.yml`
* **Work Package:** B (Flask Secret Key Security)
* **Change Type:** Modified
* **Description:**
  * Removed insecure default fallback `muet-dbs-production-secret-2026` from `FLASK_SECRET_KEY: ${FLASK_SECRET_KEY}`.
  * Added `APP_ENV: production`.
* **Justification:** Ensures Docker production deployment cannot boot with an insecure fallback key.
* **Verification:** Inspected file syntax; verified container environment variable mapping.

#### `Dockerfile`
* **Work Package:** B (Flask Secret Key Security)
* **Change Type:** Modified
* **Description:** Added `APP_ENV=production` to the base `ENV` directive.
* **Justification:** Explicitly sets the production environment variable inside the container.
* **Verification:** Inspected file syntax.

#### `.env.example`
* **Work Package:** B (Flask Secret Key Security)
* **Change Type:** Modified
* **Description:** Added documentation for `APP_ENV=development` and clear instructions on generating a secure 32-byte cryptographic hex key for production.
* **Justification:** Informs developers and operators of secure configuration requirements.
* **Verification:** Inspected file documentation.

#### `docs/demo_guide.md`
* **Work Package:** C (Credential Exposure)
* **Change Type:** Modified
* **Description:**
  * Line 71: Replaced hardcoded MySQL root CLI connection command with interactive password prompt: `mysql -u root -p online_shop`.
  * Line 102: Replaced embedded test customer password command with interactive prompt: `mysql -u test_customer -p online_shop`.
* **Justification:** Eliminates exposure of credentials in live viva demonstration instructions.
* **Verification:** Confirmed via repository credential scanner.

#### `STAGE_1_TEST_RESULTS.md`
* **Work Package:** C (Credential Exposure)
* **Change Type:** Modified
* **Description:** Line 166: Replaced embedded root password command with sanitized interactive prompt command: `mysql -u root -p online_shop_test < sql/11_tests.sql`.
* **Justification:** Sanitizes testing documentation.
* **Verification:** Confirmed via repository credential scanner.

#### `test_secret_key.py`
* **Work Package:** B (Flask Secret Key Security)
* **Change Type:** Created
* **Description:** Authored comprehensive automated test suite (7 unit tests) covering local dev custom key, local dev ephemeral generation, testing environment isolation, production valid key, production missing key refusal, production short key refusal, and production placeholder rejection.
* **Justification:** Automated verification of Quality Gate SG-01 security compliance.
* **Verification:** 7/7 tests passed.
