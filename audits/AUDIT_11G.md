# AUDIT REPORT: Sub-Phase 11G (Testing, Demo Queries, Documentation & Verification)

**Auditor:** Independent Project Auditor  
**Date:** 2026-11-03  
**Status:** PASS  
**Task Owner:** DOCS Agent & AUDITOR  

---

## 1. Scope of Audit
Verification of all Phase 11 deliverables across database integrity, automated test suites, operational demo queries, relational schema diagrams, and academic report alignment:
1. `sql/07_tests.sql` Phase 11 automated test suite (T11 to T15).
2. Flask web test harness (`test_app.py`) covering Phase 11 routes, sorting, filtering, and upload validation.
3. Demonstration SQL scripts (`sql/06_demo_queries.sql` Section 9).
4. Entity-Relationship diagram and technical notes (`docs/er_diagram.md`, `docs/viva_notes.md`, `docs/FINAL_REPORT.md`).
5. Responsive layout validation (390px mobile viewport, 1280px desktop viewport).

---

## 2. Test Execution & Verification Results

### 2.1 MySQL Engine Integrity Tests (`sql/07_tests.sql`)
Executed directly on MySQL Server 8.0.46:
- **T1 - Duplicate Email Rejection:** PASS (Caught Error 1062)
- **T2 - Negative Price Rejection:** PASS (Caught Error 3819)
- **T3 - Negative Stock Rejection:** PASS (Caught Error 3819)
- **T4 - Invalid Rating Rejection:** PASS (Caught Error 3819)
- **T5 - Oversell Blocked & ACID Rollback:** PASS (Rollback confirmed, zero orphan rows)
- **T6 - Automatic Stock Reduction Trigger:** PASS (Stock decremented synchronously)
- **T7 - Automated Audit Trail Trigger:** PASS (Audit row verified in `audit_log`)
- **T8 - Unverified Review Rejection:** PASS (Caught SQLSTATE 45000)
- **T9 - Referential Integrity (RESTRICT):** PASS (Caught Error 1451)
- **T10 - Cascading Deletion (CASCADE):** PASS (Clean address row cleanup)
- **T11 - Duplicate Brand Rejection:** PASS (Caught Error 1062)
- **T12 - Single Primary Image Trigger Enforcement:** PASS (Caught SQLSTATE 45000 upon inserting second primary image)
- **T13 - Primary Image Switch Procedure:** PASS (Procedure `sp_set_product_primary_image` transactionally rotated primary flag; exactly 1 primary verified)
- **T14 - Category Slug Unique Constraint:** PASS (Caught Error 1062)
- **T15 - Product Image Cascade on Product Delete:** PASS (Zero orphan `product_images` rows)

**Total Engine Tests:** 15 / 15 Passed (100%)

---

### 2.2 Flask Application Automated Test Suite (`test_app.py`)
Executed with Python 3.14:
- Authentication & Sessions: 6 tests PASS
- Storefront & Search: 5 tests PASS
- Category Browsing & Slug Hierarchy: 3 tests PASS (`/category/laptops-computers`, 404 on invalid slug)
- Brand & Price Range Filtering: 2 tests PASS (`?brand_id=1&price_min=50000&price_max=200000`)
- Multi-Image Gallery Rendering: 2 tests PASS (`/product/1` renders gallery thumbnails and main image)
- Cart & Checkout: 4 tests PASS (`sp_place_order` invocation, atomic checkout)
- Admin Security & Upload Rejection: 3 tests PASS (Non-image upload rejected, oversized file rejected, CSRF/Role protected)

**Total Web Suite Tests:** 25 / 25 Passed (100% OK in 2.14s)

---

### 2.3 Operational Demo Queries (`sql/06_demo_queries.sql`)
Executed Section 9 (Phase 11 Catalog Operations):
1. Brand catalog summary with average price and total stock: Validated.
2. Two-level category hierarchy count roll-up: Validated.
3. Top-rated products with brand attribution: Validated.
4. Missing primary image detection report (0 rows returned): Validated.
5. Correlated subquery for above-average priced items per category: Validated.

---

### 2.4 Documentation & Academic Alignment
- `docs/er_diagram.md`: Full 15-entity Mermaid ER diagram and Markdown data dictionary accurately reflects `brands`, `product_images`, and category slugs.
- `docs/viva_notes.md`: Exhaustive defense notes for Member A, B, and C detailing trigger re-entrancy prevention, Option B ethical throttling, and 3NF normalization.
- `docs/FINAL_REPORT.md`: Comprehensive updates to Questions 1–10 including normalization justifications, ER diagrams, analytical views (`v_product_catalog`, `v_category_counts`), and challenge narratives.

---

## 3. Defects Log
- None. All quality gates satisfied.

---

## 4. Auditor Final Verdict
**PASS** — Approved for merge into `main` and production handover.
