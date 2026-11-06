# STAGE 1 TEST RESULTS — Online Shopping Database Management System

**Project:** Online Shopping Database Management System (DBMS CEP)  
**Institution:** Mehran University of Engineering and Technology, Jamshoro  
**Phase:** Final Stabilization  
**Stage:** 1 — Critical Remediation  
**Date of Execution:** 2026-11-03  
**Target Environment:** Isolated Test Database (`online_shop_test`) on MySQL 8.0.46  

---

## 1. Executive Test Summary

| Test Suite | File / Scope | Total Assertions | Passed | Failed | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Flask Integration & E2E** | `test_app.py` | 49 | 49 | 0 | **100% PASS** |
| **Database Engine & Triggers** | `sql/11_tests.sql` | 25 | 25 | 0 | **100% PASS** |
| **TLS/SSL Configuration** | `test_ssl_db.py` | 6 | 6 | 0 | **100% PASS** |
| **Clean Docker Init Reproduction** | Disposable DB Scratch | 49 objects | 49 | 0 | **100% PASS** |
| **Repeatability Verification** | Consecutive `test_app.py` | 49 | 49 | 0 | **100% PASS** |
| **Development DB Preservation** | `online_shop` verification | 2 probes | 2 | 0 | **100% PASS** |

**Overall Stage 1 Verification Status:** **100% PASS (Zero Failures)**

---

## 2. Flask Application Integration Test Suite (`test_app.py`)

### 2.1 Execution Command
```powershell
.\venv\Scripts\python.exe test_app.py
```

### 2.2 Standard Output Log
```text
========================================================
      UNIFIED E2E VERIFICATION SUITE (ISOLATED TEST DB)
      Active Test Database: online_shop_test
========================================================
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

========================================================
  TOTAL RESULTS: 49 PASSED, 0 FAILED
  Target Database: online_shop_test
========================================================
```

### 2.3 Detailed Assertion Breakdown by Domain

#### A. Security & Test Isolation Gates (SG-01, SG-02, SG-05)
1. **Test Database Isolation Guard:** Verified `assert_safe_test_database()` rejects target database if it matches development DB or lacks `_test` suffix. (`online_shop_test` verified).
2. **CSRF Enforcement (Missing Token):** Submitting a POST request without `csrf_token` returns HTTP `400 Bad Request`.
3. **CSRF Enforcement (Invalid Token):** Submitting a POST request with forged/expired `csrf_token` returns HTTP `400 Bad Request`.

#### B. Storefront, Catalog & Multi-Media Browsing (Phases 8, 11D, 11E, 11F)
4. `GET /`: Homepage renders status 200 with category navigation.
5. `GET /products`: Full catalog pagination renders status 200.
6. `GET /products?q=Samsung`: Keyword search returns filtered product subset.
7. `GET /product/1`: Product detail page renders title, price, stock, brand.
8. `GET /category/laptops-computers`: Subcategory filter renders products.
9. `GET /category/women-unstitched`: Subcategory filter renders products.
10. `GET /category/laptops-computers?sort=price_asc`: Sort ordering applied to catalog.
11. `GET /category/laptops-computers?brand=Dell`: Brand filter applied to catalog.
12. `GET /product/1` Gallery: Multi-image thumbnail switcher renders active images.
13. Admin Upload Format Check: Rejects `.exe` and non-image file uploads.
14. Admin Upload Size Check: Enforces 2MB maximum payload constraint.

#### C. Authentication & Customer RBAC (Phases 8, 12C)
15. `GET /login`: Renders login form with CSRF token.
16. `POST /login`: Authenticates valid customer credentials and establishes session.
17. Customer denied `/admin`: Access to administrative endpoints triggers HTTP 302 redirect.
18. `POST /login`: Authenticates administrative credentials and grants admin session.
19. Cart Merge on Login: Guest session cart items automatically transfer to user cart upon login via `sp_merge_carts`.

#### D. Cart, Single-Source Pricing & Checkout Flow (Phases 8, 12C)
20. `POST /cart/add` (Auth User): Adds item to customer cart with stock validation.
21. `GET /cart` (Auth User): Renders cart summary with dynamic calculations.
22. `GET /checkout` (Auth User): Renders checkout view with address options.
23. `POST /checkout` (Atomic Order Placement): Places authenticated order via `sp_place_order`.
24. `GET /my-orders`: Lists customer order history.
25. `POST /cart/add` (Guest): Permits anonymous addition of items to session cart.
26. `GET /cart` (Guest): Calculates fiscal totals via stored procedure `sp_cart_summary`.
27. `POST /checkout` (Guest Order Placement): Executes atomic guest checkout via `sp_place_guest_order`.

#### E. Simulated Payment Gateway Sandbox & Error Recovery (Phase 12C)
28. `POST /checkout` (Simulated Payment): Routes transaction to gateway sandbox.
29. `POST /payment/process` (Failure Outcome): Logs payment attempt failure and redirects to payment recovery.
30. `POST /payment/switch-cod`: Switches payment method to Cash-on-Delivery and confirms order without repurchasing.

#### F. Support Ticketing, Trust, & Seller Governance (Phase 12D)
31. `GET /orders/<id>/track`: Displays live timeline backed by `order_status_history` trigger.
32. `POST /support`: Submits customer support ticket with auto-generated reference code.
33. `GET /staff/tickets`: Renders triage queue for customer support staff.
34. `GET /admin/sellers`: Renders seller verification governance dashboard.
35. `POST /admin/sellers/<id>/verify`: Toggles seller verification status (`v_sellers` view).
36. `POST /orders/<id>/return`: Lodges customer return claim with reason code.
37. `GET /seller/returns`: Surfaces return claims queue to authorized sellers.
38. `GET /admin/returns/overdue`: Renders `v_overdue_return_requests` SLA escalation view.

#### G. Administrative Operations & Compliance (Phases 8, 12D, 13A)
39. `GET /admin`: Dashboard renders summary metrics and `v_abandoned_carts` table.
40. `GET /admin/products`: Product management view renders with CRUD actions.
41. `GET /admin/orders`: Order management view renders active orders.
42. `GET /admin/reports`: Reports view displays view aggregations.
43. `POST /admin/order/status`: Updates order status and verifies transition.
44. `GET /health`: Production liveness probe returns HTTP 200 with JSON payload (`{"status": "healthy"}`).
45. `GET /privacy`: Renders privacy policy.
46. `GET /terms`: Renders terms of service.
47. `GET /returns-policy`: Renders return and replacement policy.
48. Custom 404 Error Page: Renders branded 404 without leaking server internals or stack traces.

---

## 3. Database Engine & Trigger Test Suite (`sql/11_tests.sql`)

### 3.1 Execution Command
```cmd
mysql -u root -p online_shop_test < sql/11_tests.sql
# (Database root password supplied interactively via secure prompt)
```

### 3.2 Standard Output Table
```text
test_id | test_name                               | expected_result                                                         | actual_result                                                                                        | status
--------+-----------------------------------------+-------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------+-------
T1      | Duplicate Email Rejection               | Rejection with Error 1062 (Duplicate entry)                             | Caught Error 1062: Duplicate entry for key users.email                                               | PASS
T2      | Negative Price Rejection                | Engine CHECK constraint chk_products_price violated                     | Caught Error 3819: Check constraint chk_products_price violated                                      | PASS
T3      | Negative Stock Rejection                | Engine CHECK constraint chk_products_stock violated                     | Caught Error 3819: Check constraint chk_products_stock violated                                      | PASS
T4      | Invalid Review Rating Rejection         | Engine CHECK constraint chk_reviews_rating violated                     | Caught Error 3819: Check constraint chk_reviews_rating violated                                      | PASS
T5      | Oversell Prevention & ACID Rollback     | Transaction aborted, 0 orders added, stock unchanged                    | Rollback confirmed. Result: FAILED: Oversell Error: Requested quantity exceeds available inventory stock., Stock remained: 3 | PASS
T6      | Automatic Stock Reduction Trigger       | Stock quantity decremented by exactly 2 via AFTER INSERT trigger         | Stock changed from 10 to 8 (Decremented by 2)                                                        | PASS
T7      | Automated Audit Trail Trigger           | Row created automatically in audit_log by trg_after_orders_update_audit | Audit record verified in audit_log for order #9999                                                   | PASS
T8      | Unverified Review Trigger Block         | Engine trigger trg_before_reviews_insert raises 45000 custom error       | Caught SQLSTATE 45000: Review Error (Unverified purchase)                                            | PASS
T9      | Referential Integrity (RESTRICT Delete) | Engine blocks deletion with Error 1451 (foreign key RESTRICT)           | Caught Error 1451: Cannot delete or update a parent row: foreign key constraint fails (RESTRICT)    | PASS
T10     | Cascading Delete (ON DELETE CASCADE)    | Dependent addresses deleted automatically via ON DELETE CASCADE         | Child address rows cleaned up cleanly (0 orphan records remaining)                                   | PASS
T11     | Single Primary Image Enforcement        | Trigger trg_product_images_single_primary_bi raises SQLSTATE 45000       | Caught SQLSTATE 45000: Product already has an active primary image                                  | PASS
T12     | Gallery Cascade Deletion                | Linked product_images rows deleted automatically via ON DELETE CASCADE  | 0 orphan image records remaining                                                                     | PASS
T13     | Historic Order Preservation             | Foreign key RESTRICT blocks deletion with Error 1451                    | Caught Error 1451: Cannot delete or update a parent row: foreign key constraint fails                | PASS
T14     | Category Roll-Up Consistency            | Perfect match: 81 active products                                       | Verified consistent count: 81 products in view roll-up                                               | PASS
T15     | Brand Referential Integrity             | Rejection with Error 1452 (foreign key violation)                       | Caught Error 1452: Foreign key constraint fk_products_brand fails                                    | PASS
T16     | Price Parity (sp_cart_summary)          | Total exactly equals subtotal + tax + delivery fee (Rs 150 fee)         | Computed Total: PKR 420148.95 = 399999.00 + 19999.95 + 150.00                                       | PASS
T17     | Guest Checkout Placement (AC-03.1)      | Order created successfully with user_id IS NULL and address snapshot   | Guest Order #10060 created with user_id NULL                                                         | PASS
T18     | Guest Cart Merge on Login (AC-08.2)     | Items combined into customer cart and guest cart converted              | Items successfully merged into user #2 active cart                                                  | PASS
T19     | Order Status Audit Trigger (AC-04.3)    | Row created in order_status_history with old_status and new_status       | Status transition record verified in order_status_history                                            | PASS
T20     | Address Snapshot Immutability (AC-04.2) | Order shipping_address_snapshot remains completely unaltered             | Historical order address preserved intact despite address edit                                       | PASS
T21     | Customer Support Ticketing (AC-04.4)    | Record saved in support_tickets with status open                         | Support ticket TCK-TEST-SQL-21 created successfully                                                  | PASS
T22     | Seller Verification Governance (AC-06.2)| Rejected seller products excluded from storefront catalog view          | Verified isolation: Catalog items dropped from 19 to 0                                               | PASS
T23     | Return Status Audit Trigger (AC-08.5)   | Row created in return_status_history by trg_return_status_history       | Return status transition to approved verified in audit table                                         | PASS
T24     | Overdue Return SLA Escalation (AC-08.6) | View accurately surfaces unattended claims with days_elapsed            | Overdue claim detected by v_overdue_return_requests view                                              | PASS
T25     | Payment Attempt Audit Logging (AC-02.2) | Record saved with transaction_ref, amount, status, and failure_reason    | Failed payment attempt audit record verified in database                                             | PASS
```

---

## 4. Database TLS/SSL Test Suite (`test_ssl_db.py`)

### 4.1 Execution Command
```powershell
.\venv\Scripts\python.exe test_ssl_db.py
```

### 4.2 Standard Output Log
```text
test_database_connection_to_test_db (__main__.TestDatabaseSSLConfiguration.test_database_connection_to_test_db)
SG-03: Live database connection connects successfully to online_shop_test. ... ok
test_local_connection_no_ssl_default (__main__.TestDatabaseSSLConfiguration.test_local_connection_no_ssl_default)
SG-03: Local connections on localhost do not require SSL configuration. ... ok
test_missing_ca_certificate_raises_file_not_found (__main__.TestDatabaseSSLConfiguration.test_missing_ca_certificate_raises_file_not_found)
SG-04: A non-existent DB_SSL_CA path raises a descriptive FileNotFoundError. ... ok
test_production_local_host_allowed_without_ssl (__main__.TestDatabaseSSLConfiguration.test_production_local_host_allowed_without_ssl)
SG-03: In production, local containers (host='db' or 'localhost') do not require external SSL. ... ok
test_production_remote_host_without_ssl_raises_error (__main__.TestDatabaseSSLConfiguration.test_production_remote_host_without_ssl_raises_error)
SG-04: In production, connecting to a remote host without SSL raises RuntimeError. ... ok
test_valid_ca_certificate_loads_ssl_dict (__main__.TestDatabaseSSLConfiguration.test_valid_ca_certificate_loads_ssl_dict)
SG-04: Providing a valid CA certificate path configures PyMySQL ssl dictionary. ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.013s

OK
```

---

## 5. Clean Database Initialization Verification

### 5.1 Verification Script Execution
To verify that the clean `sql/init/` directory (scripts 01–08) executes without error from a completely empty state, a disposable test database `online_shop_disposable_init_test` was provisioned and initialized from scratch.

### 5.2 Verification Log
```text
[CLEAN INIT TEST] Creating disposable database: online_shop_disposable_init_test
[CLEAN INIT TEST] Executing scripts in sequential order:
  -> Executing: sql\init\01_schema.sql ... OK
  -> Executing: sql\init\02_sample_data.sql ... OK
  -> Executing: sql\init\03_views_indexes.sql ... OK
  -> Executing: sql\init\04_procedures_triggers.sql ... OK
  -> Executing: sql\init\05_roles.sql ... OK
  -> Executing: sql\init\06_catalog_expansion.sql ... OK
  -> Executing: sql\init\07_srs_alignment.sql ... OK
  -> Executing: sql\init\08_srs_alignment_fixes.sql ... OK

[CLEAN INIT VERIFICATION]
  Tables Created:     23
  Views Created:       9
  Routines Created:    7
  Triggers Created:   10
  Default Roles:      shop_admin, shop_staff, shop_customer
  Execution Errors:    0

[CLEAN INIT TEARDOWN] Dropped disposable database online_shop_disposable_init_test.
RESULT: 100% REPRODUCIBLE CLEAN INITIALIZATION.
```

---

## 6. Repeatability & Test Database Self-Healing Proof

### 6.1 Consecutive Execution Verification
To prove that `test_app.py` is fully idempotent and self-healing, it was executed consecutively without any intervening manual intervention:

* **Execution 1:** 49 Passed, 0 Failed (Elapsed: 4.8s)
* **Execution 2:** 49 Passed, 0 Failed (Elapsed: 4.7s)

### 6.2 Key State Isolation Mechanisms
1. **Dynamic Fixture State:** `reset_test_state()` in `test_app.py` restores inventory levels for products `1, 2, 3, 10, 12` in `online_shop_test` prior to each test run.
2. **Deterministic Cart IDs:** SQL tests `T16`, `T17`, and `T18` allocate independent guest carts with temporary session tokens and explicitly delete test artifacts on completion.
3. **Status Restoration:** Trigger verification test `T19` updates Order 1 to `'shipped'` and restores it to `'delivered'`, ensuring downstream review tests (`T4`, `T8`) do not encounter invalid status state.

---

## 7. Development Database (`online_shop`) Preservation Proof

Direct query against the primary development database `online_shop` proves zero corruption or modification occurred during the testing sessions:

```sql
SELECT product_id, name, stock_quantity FROM online_shop.products WHERE product_id = 12;
SELECT order_id, status FROM online_shop.orders WHERE order_id = 1;
```

**Query Output:**
```text
product_id  name                            stock_quantity
12          J. Classic Cotton Kurta White   0

order_id    status
1           pending
```

* **Stock Verification:** `product_id = 12` retains its initial inventory count of `0` (untouched by test checkout replenishment).
* **Order Status Verification:** `order_id = 1` retains its initial state `'pending'` (untouched by test review triggers).
* **Conclusion:** Complete physical and logical isolation confirmed between development and testing environments.
