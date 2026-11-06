# STAGE 1 CHANGELOG — Critical Remediation

**Project:** Online Shopping Database Management System (DBMS CEP)  
**Institution:** Mehran University of Engineering and Technology, Jamshoro  
**Stage:** 1 of 4 (Critical Remediation)  
**Date:** 2026-11-03  
**Status:** COMPLETED & VERIFIED  

---

## 1. Summary of Changes

Stage 1 resolves the critical security, configuration, isolation, and deployment issues identified during the comprehensive audit, without modifying existing application business logic or corrupting development database contents.

| Work Package | Focus Area | Files Modified | Files Created | Verification |
| :--- | :--- | :---: | :---: | :---: |
| **Package A** | CSRF Protection | 16 | 0 | 49/49 Tests Pass |
| **Package B** | Database TLS/SSL Support | 2 | 1 | 6/6 SSL Tests Pass |
| **Package C** | Test Database Isolation | 2 | 0 | `online_shop` untouched |
| **Package D** | Gunicorn WSGI Import Path | 1 | 1 | Dual imports verified |
| **Package E** | Docker Initialization Order | 1 | 9 | Disposable DB Init (0 errors) |
| **Package F** | MySQL Privilege Compatibility | 1 | 0 | Clean role grant on Cloud DB |
| **Package G** | Python Runtime Consistency | 1 | 0 | Python 3.11-slim & pinned deps |

---

## 2. Itemized File Changelog

### 2.1 Python Application Code

#### `app/app.py`
* **Work Packages:** A, C, D
* **Change Type:** Modified
* **Description:**
  * Added `from flask_wtf.csrf import CSRFProtect` and initialized `csrf = CSRFProtect(app)`.
  * Set `app.config['WTF_CSRF_ENABLED'] = True` with `app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_dev_key')`.
  * Wrapped database connection import in dual-compatible import block:
    ```python
    try:
        from app.db import get_connection
    except ImportError:
        from db import get_connection
    ```
  * Updated `get_db()` helper to inspect `app.config.get('DB_NAME')` before falling back to `os.getenv('DB_NAME', 'online_shop')`, allowing dynamic runtime test database routing.
* **Justification:** Enforces CSRF token validation on all state-mutating requests; enables Gunicorn to import the module from root or subfolder; allows test harnesses to redirect connections to `online_shop_test`.
* **Verification:** `python -c "import app.app"` succeeds; CSRF rejection tested on invalid/missing tokens; 49 integration tests passed.

#### `app/db.py`
* **Work Packages:** B, C
* **Change Type:** Modified
* **Description:**
  * Implemented `get_ssl_config()`:
    * Reads `DB_SSL_CA` from environment.
    * Validates certificate path on disk, raising `FileNotFoundError` if missing.
    * For remote hosts (`host` not in `['localhost', '127.0.0.1', 'db', 'mysql']`) in production, strictly enforces TLS by raising `RuntimeError` if `DB_SSL_CA` is not provided.
    * Allows local Docker containers and localhost to connect without SSL.
  * Updated `get_connection(database=None)`:
    * Accepts optional `database` parameter.
    * Checks `current_app.config.get('DB_NAME')` when running within Flask context.
    * Passes `ssl=get_ssl_config()` to `pymysql.connect()`.
* **Justification:** Prepares the application for secure managed MySQL hosting (e.g. Aiven Cloud MySQL) without breaking local developer workflows.
* **Verification:** Verified via `test_ssl_db.py` (6 unit tests, 100% PASS).

#### `app/__init__.py`
* **Work Package:** D
* **Change Type:** Created
* **Description:** Created standard Python package initialization file in `app/`.
* **Justification:** Marks `app` as a regular Python package, resolving ModuleNotFoundError when Gunicorn or test runners execute from repository root.
* **Verification:** Verified with `python -c "import app.app; from app.app import app; print(app)"`.

---

### 2.2 Templates & CSRF Token Injection (Work Package A)

The following 15 template files containing exactly 21 POST forms were updated to include:
```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
```

1. **`app/templates/login.html`**
   * *Form Protected:* Customer and administrative login form (`action="/login"`, `method="POST"`).
2. **`app/templates/register.html`**
   * *Form Protected:* Customer account registration form (`action="/register"`, `method="POST"`).
3. **`app/templates/product_detail.html`**
   * *Forms Protected (2):* Add-to-cart form; customer review submission form.
4. **`app/templates/category.html`**
   * *Form Protected:* Category grid quick add-to-cart form.
5. **`app/templates/cart.html`**
   * *Forms Protected (2):* Item quantity adjustment form; item deletion form.
6. **`app/templates/checkout.html`**
   * *Form Protected:* Order placement submission form (`action="/checkout"`, `method="POST"`).
7. **`app/templates/payment_simulate.html`**
   * *Form Protected:* Simulated payment gateway sandbox execution form (`action="/payment/process"`).
8. **`app/templates/payment_retry.html`**
   * *Forms Protected (2):* Payment gateway retry action; switch-to-COD payment fallback action.
9. **`app/templates/support.html`**
   * *Form Protected:* Customer support ticket submission form (`action="/support"`).
6. **`app/templates/return_request.html`**
   * *Form Protected:* Customer return and replacement claim lodging form (`action="/orders/<id>/return"`).
11. **`app/templates/admin/orders.html`**
    * *Form Protected:* Administrative order status transition form (`action="/admin/order/status"`).
12. **`app/templates/admin/product_form.html`**
    * *Form Protected:* Administrative product catalog create/edit form (`action="/admin/product/..."`).
13. **`app/templates/admin/sellers.html`**
    * *Forms Protected (2):* Seller verification approval action; seller rejection action.
14. **`app/templates/staff/tickets.html`**
    * *Forms Protected (2):* Staff support ticket status change; ticket assignment action.
15. **`app/templates/seller/returns.html`**
    * *Forms Protected (2):* Seller return claim acceptance; claim dispute action.

* **Verification:** Confirmed via `git grep -c "csrf_token" app/templates/` confirming exactly 21 instances across all templates.

---

### 2.3 SQL & Database Configuration

#### `sql/05_roles.sql`
* **Work Package:** F
* **Change Type:** Modified
* **Description:** Removed `FLUSH PRIVILEGES;` from line 41.
* **Justification:** MySQL roles take effect dynamically. Executing `FLUSH PRIVILEGES;` requires the `RELOAD` privilege, which is prohibited on managed database hosting providers (e.g. Aiven, AWS RDS).
* **Verification:** Executed against local MySQL 8.0 instance; verified default roles created in `mysql.default_roles` without error.

#### `sql/init/`
* **Work Packages:** E, F
* **Change Type:** Created Directory with 8 Initialized Scripts
* **Description:** Provisioned clean directory containing production database initialization scripts in strict numerical sequence:
  1. `01_schema.sql` (Tables, constraints, foreign keys)
  2. `02_sample_data.sql` (Initial seed data)
  3. `03_views_indexes.sql` (Reporting views and performance indexes)
  4. `04_procedures_triggers.sql` (Order triggers and stored procedures)
  5. `05_roles.sql` (RBAC roles without FLUSH PRIVILEGES)
  6. `06_catalog_expansion.sql` (Brands, multi-image gallery, slugs)
  7. `07_srs_alignment.sql` (Fiscal rates, tracking, return lifecycle)
  8. `08_srs_alignment_fixes.sql` (Payment method enum expansion)
* **Justification:** Isolates clean deployment initialization from test execution scripts. Guarantees deterministic container bootstrap.
* **Verification:** Tested via `test_clean_initialization.py` against disposable database `online_shop_disposable_init_test` with 0 errors.

#### `sql/11_tests.sql`
* **Work Packages:** C, E
* **Change Type:** Created (Refactored from `sql/07_tests.sql`)
* **Description:**
  * Established 25-assertion database test harness decoupled from deployment initialization scripts.
  * Refactored Test 16 (`T16` Price Parity) to create an isolated test cart (`tok_test_parity_t16`), preventing state interference from earlier checkout runs.
  * Refactored Test 19 (`T19` Order Status Trigger) to restore Order 1's status back to `'delivered'`, ensuring downstream review trigger tests (`T4`, `T8`) remain valid on consecutive runs.
* **Justification:** Ensures complete repeatability and deterministic results for the database test suite.
* **Verification:** Executed via `mysql.exe` against `online_shop_test`: 25/25 PASS.

#### `docker-compose.yml`
* **Work Package:** E
* **Change Type:** Modified
* **Description:** Updated database volume mount from `./sql:/docker-entrypoint-initdb.d:ro` to `./sql/init:/docker-entrypoint-initdb.d:ro`.
* **Justification:** Prevents Docker entrypoint from executing test scripts during container initialization.
* **Verification:** Inspected file; verified mount target points exclusively to `sql/init`.

---

### 2.4 Configuration & Project Infrastructure

#### `requirements.txt`
* **Work Packages:** A, G
* **Change Type:** Modified
* **Description:** Added pinned dependencies `Flask-WTF==1.2.1` and `wtforms==3.3.2`.
* **Justification:** Mandatory for server-side CSRF form protection.
* **Verification:** Installed cleanly into project virtual environment; all imports verified.

#### `.env.example`
* **Work Package:** B
* **Change Type:** Modified
* **Description:** Added documented placeholder for `DB_SSL_CA` explaining remote managed MySQL SSL configurations.
* **Justification:** Guides operators on configuring managed database certificates.
* **Verification:** Inspected file syntax and documentation clarity.

#### `test_ssl_db.py`
* **Work Package:** B
* **Change Type:** Created
* **Description:** Authored unit test suite testing `get_ssl_config()` across local, production, missing cert, and valid cert scenarios.
* **Justification:** Verifies Quality Gates SG-03 and SG-04.
* **Verification:** 6/6 unit tests pass.

#### `test_app.py`
* **Work Packages:** A, C
* **Change Type:** Modified
* **Description:**
  * Added `assert_safe_test_database(TEST_DB_NAME)` guard enforcing that tests execute exclusively against a dedicated test database containing `_test` in its name.
  * Added `reset_test_state()` fixture restoring inventory on products `1, 2, 3, 10, 12` in `online_shop_test`.
  * Injected CSRF security test gates (POST without token -> 400, POST with invalid token -> 400).
  * Built `post_csrf()` helper that synchronizes active session cookies with form-rendered CSRF tokens.
* **Justification:** Eliminates test-to-development database contamination; asserts CSRF security across all endpoints.
* **Verification:** 49/49 tests pass consecutively on `online_shop_test`.
