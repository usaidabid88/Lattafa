# STOREFRONT REFINEMENT TEST RESULTS
## Online Shopping Database Management System — Perfume Store Edition
**Mehran University of Engineering and Technology (MUET) — Department of Software Engineering**  
**Document Ref:** CEP-DBMS-2024-SRT-01  
**Execution Environment:** Windows Server / Python 3.11.9 Virtual Environment (`.\venv`)  
**Target Test Database:** `online_shop_perfume_test`  
**Target Dev Database:** `online_shop_perfume_dev`  
**Execution Timestamp:** 2026-11-06 20:08:15 PKT  

---

## 1. COMPREHENSIVE TEST SUITE EXECUTION SUMMARY

```
========================================================
      CONSOLIDATED VERIFICATION RESULTS
========================================================
  [1] Unified E2E Test Suite (run_test_suite.py)      : 49 / 49 PASSED (100%)
  [2] Perfume Domain Test Suite (test_perfume_suite.py):  7 /  7 PASSED (100%)
  [3] Guest Order Tracking Suite (test_guest_tracking) :  4 /  4 PASSED (100%)
  [4] Multi-Province Location Parity (test_location_rates): 6 /  6 PASSED (100%)
========================================================
  TOTAL VERIFICATION RUNS: 66 PASSED, 0 FAILED
  VERDICT: COMPLETE PASS
========================================================
```

---

## 2. UNIFIED E2E TEST SUITE BREAKDOWN (`run_test_suite.py`)

Execution command: `.\venv\Scripts\python.exe run_test_suite.py`  
Output verification:

| # | Test Scenario | Requirement / AC Reference | Status |
|---|---|---|---|
| 1 | Test Database Isolation | SG-05 | **PASS** |
| 2 | CSRF Gate: POST without token rejected | SG-01 / SG-02 | **PASS** |
| 3 | CSRF Gate: POST with invalid token rejected | SG-02 | **PASS** |
| 4 | GET / (Homepage) with platform preservation tag | Core Platform | **PASS** |
| 5 | GET /products (Catalog Route) | FR-01 | **PASS** |
| 6 | GET /products?q=Samsung (Search compatibility) | FR-01, AC-01.1 | **PASS** |
| 7 | GET /product/1 (Detail Route & Gallery) | FR-01 | **PASS** |
| 8 | GET /login | FR-02 | **PASS** |
| 9 | POST /login (Customer Auth Verification) | FR-02, AC-02.1 | **PASS** |
| 10 | POST /cart/add (Auth User) | FR-03 | **PASS** |
| 11 | GET /cart (Auth User) | FR-03 | **PASS** |
| 12 | GET /checkout (Auth User) | FR-04 | **PASS** |
| 13 | POST /checkout (Atomic Order Placement via `sp_place_order`) | FR-04, AC-04.1 | **PASS** |
| 14 | GET /my-orders (Order History Listing) | FR-05 | **PASS** |
| 15 | RBAC: Customer denied /admin (302 Redirect) | SG-03 | **PASS** |
| 16 | POST /login (Admin Auth Verification) | FR-02 | **PASS** |
| 17 | GET /admin (Admin Dashboard) | FR-06 | **PASS** |
| 18 | GET /admin/products (Catalog Management) | FR-06 | **PASS** |
| 19 | GET /admin/orders (Order Processing) | FR-06 | **PASS** |
| 20 | GET /admin/reports (Reporting Views Integration) | FR-07 | **PASS** |
| 21 | POST /admin/order/status (Trigger Audit Verification) | FR-08, AC-04.3 | **PASS** |
| 22 | GET /category/laptops-computers (Legacy Routing) | 11D | **PASS** |
| 23 | GET /category/women-unstitched (Legacy Routing) | 11D | **PASS** |
| 24 | GET /category/laptops-computers?sort=price_asc | 11D | **PASS** |
| 25 | GET /category/laptops-computers?brand=Dell | 11D | **PASS** |
| 26 | GET /product/1 Gallery Verification | 11E | **PASS** |
| 27 | Admin Upload Format Check (MIME whitelist) | 11F | **PASS** |
| 28 | Admin Upload Size Check (Max payload clamp) | 11F | **PASS** |
| 29 | GET /health probe returns 200 JSON | NFR-02 | **PASS** |
| 30 | GET /privacy renders successfully | Statutory | **PASS** |
| 31 | GET /terms renders successfully | Statutory | **PASS** |
| 32 | GET /returns-policy renders successfully | Statutory | **PASS** |
| 33 | POST /cart/add (Guest) allows adding without auth | FR-02, AC-08.1 | **PASS** |
| 34 | GET /cart (Guest) calculates pricing via `sp_cart_summary` | NFR-06, AC-01.1 | **PASS** |
| 35 | POST /checkout (Guest Order via `sp_place_guest_order`) | FR-02, AC-03.1 | **PASS** |
| 36 | POST /checkout (Simulated Payment) routes to sandbox | FR-06, AC-02.1 | **PASS** |
| 37 | POST /payment/process (Fail outcome) logs attempt | FR-10, FR-11 | **PASS** |
| 38 | POST /payment/switch-cod switches method to COD | FR-11 | **PASS** |
| 39 | GET /orders/<id>/track displays live trigger audit | FR-12, AC-04.3 | **PASS** |
| 40 | POST /support submits customer support ticket | FR-14, AC-04.4 | **PASS** |
| 41 | GET /staff/tickets renders staff ticket queue | FR-14, AC-04.5 | **PASS** |
| 42 | GET /admin/sellers renders seller verification dashboard | FR-15 | **PASS** |
| 43 | POST /admin/sellers/<id>/verify toggles status | FR-15 | **PASS** |
| 44 | POST /orders/<id>/return lodges customer return claim | FR-16 | **PASS** |
| 45 | GET /seller/returns displays seller return claims queue | FR-16 | **PASS** |
| 46 | GET /admin/returns/overdue displays SLA view | FR-17 | **PASS** |
| 47 | GET /admin dashboard renders `v_abandoned_carts` table | FR-18 | **PASS** |
| 48 | Custom 404 error page renders without leaking trace | NFR-04 | **PASS** |
| 49 | Cart Merge on Login (`sp_merge_carts`) | FR-03, AC-08.2 | **PASS** |

---

## 3. PERFUME DOMAIN TEST SUITE BREAKDOWN (`test_perfume_suite.py`)

Execution command: `.\venv\Scripts\python.exe test_perfume_suite.py`  
Output verification:

```
.......
----------------------------------------------------------------------
Ran 7 tests in 0.496s

OK
```

| Method Name | Test Purpose | Assertions Verified | Status |
|---|---|---|---|
| `test_01_perfume_database_schema` | Verifies `product_perfume_details` table and 100 genuine perfume records | `COUNT(*) == 100`, schema columns present | **PASS** |
| `test_02_perfume_database_views` | Verifies `v_perfume_catalog`, `v_perfume_collections`, and `v_category_counts` | View existence, column projections, and nonzero data | **PASS** |
| `test_03_homepage_sections` | Verifies luxury homepage architecture (Hero, Collections, Best Sellers, Categories) | Status 200, "Featured Fragrance Houses", "Shop by Fragrance Category" | **PASS** |
| `test_04_perfume_catalog_browsing` | Verifies gender filters (Men, Women, Unisex) and collection routes | Status 200 on all gender routes; correct filtered sets | **PASS** |
| `test_05_perfume_detail_page` | Verifies flacon specifications, fragrance notes (top/heart/base), and concentration | Bottle size, EDP concentration, longevity badges | **PASS** |
| `test_06_collection_pages` | Verifies signature house pages (Khamrah, Asad, Yara, Badee Al Oud) | Status 200, correct slugs, member count match | **PASS** |
| `test_07_cart_checkout_parity` | Verifies end-to-end add-to-bag, `sp_cart_summary` calculations, and guest checkout | Exact currency totals match stored procedure outputs | **PASS** |

---

## 4. TARGETED GUEST ORDER TRACKING VERIFICATION

Script: `scratch/test_guest_tracking.py`  
Output verification:

```
[PASS] GET /track-order renders lookup form
[PASS] Invalid numeric ID rejected gracefully
[PASS] Non-existent ID handled with friendly flash message
[PASS] GET /orders/10045/track displays audit timeline for Order #10045

ALL GUEST TRACKING TESTS PASSED!
```

Key edge cases validated:
1. **Uninitialized `order` Object:** Verified that visiting `/track-order` without an `order_id` renders the lookup card without throwing `jinja2.exceptions.UndefinedError`.
2. **String / Alphanumeric IDs:** Verified that inputs such as `"abc"` or `"#1024"` flash `"Please enter a valid numeric Order ID."` and do not produce database conversion exceptions.
3. **Non-Existent Numeric ID:** Tested order reference `999999`. Handled via flash warning `"No matching order was found for the details provided."` and redirect to lookup form.
4. **Live Trigger History Rendering:** Queried existing order #10045. Verified that status transitions recorded in `order_status_history` by trigger `trg_order_status_audit` are rendered with timeline icons and timestamps.

---

## 5. PAKISTANI LOCATION & DELIVERY RATE PARITY VERIFICATION

Script: `scratch/test_location_rates.py`  
Stored Procedure: `sp_cart_summary(p_cart_id, p_province, p_city, ...)`

| Province / Territory | City Queried | Stored Procedure Fee (PKR) | Stored Procedure Tax (5% GST) | Stored Procedure SLA (Days) | Status |
|---|---|---|---|---|---|
| Sindh | Karachi | 150.00 | Computed from Subtotal | 1–3 | **MATCH** |
| Sindh | Hyderabad | 150.00 | Computed from Subtotal | 1–2 | **MATCH** |
| Punjab | Lahore | 200.00 | Computed from Subtotal | 2–4 | **MATCH** |
| Punjab | Rawalpindi | 200.00 | Computed from Subtotal | 2–4 | **MATCH** |
| Islamabad Capital Territory | Islamabad | 200.00 | Computed from Subtotal | 2–4 | **MATCH** |
| Islamabad (Legacy Key) | Islamabad | 200.00 | Computed from Subtotal | 2–4 | **MATCH** |
| Khyber Pakhtunkhwa | Peshawar | 300.00 | Computed from Subtotal | 3–6 | **MATCH** |
| Balochistan | Quetta | 250.00 | Computed from Subtotal | 3–6 | **MATCH** |

All rates calculated via `sp_cart_summary` exactly match the front-end breakdown in `cart.html` and `checkout.html`.
