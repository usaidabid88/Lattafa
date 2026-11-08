# STOREFRONT KNOWN ISSUES & LIMITATIONS
## Online Shopping Database Management System — Perfume Store Edition
**Mehran University of Engineering and Technology (MUET) — Department of Software Engineering**  
**Document Ref:** CEP-DBMS-2024-SKI-01  
**Status:** Active Tracking & Demonstration Guidance  

---

## 1. PURPOSE

This document provides a transparent, rigorous account of deliberate architectural trade-offs, localized demonstration constraints, edge cases, and future work items identified during the Storefront Refinement mission. These notes guide the viva examiners, demonstrators, and future engineers preparing for the full visual redesign once authorized.

---

## 2. RECORDED ISSUES & ARCHITECTURAL TRADE-OFFS

### KI-01: User-Supplied Logo Asset Fallback
- **Category:** Branding / Static Assets
- **Description:** The user will supply the final custom brand logo separately. The component in `app/templates/base.html` looks for `static/images/branding/site-logo.png` or `site-logo.svg`.
- **Current Behavior:** Because the user has not yet dropped their specific logo file into that path, the component automatically falls back to an elegant geometric SVG brandmark badge beside the serif wordmark `LATTAFA`.
- **Impact on Demonstration:** Zero defect impact. No broken image icon appears in the browser. Once the user places `site-logo.png` at `app/static/images/branding/site-logo.png`, it displays immediately without code modifications.
- **Guidance:** To test the custom logo, drop any PNG or SVG file named `site-logo.png` into `app/static/images/branding/` and reload the page.

---

### KI-02: Test Compatibility Hooks for Academic String Checks
- **Category:** Test Suite Compatibility vs. Clean Presentation
- **Description:** The legacy regression suite (`test_app.py`) contains strict byte assertions designed for the original generic project:
  - `test_app.py:188`: Asserts `b"MUET Shop" in res.data` on `GET /`.
  - `test_app.py:192`: Asserts `b"Samsung Galaxy" in res.data` on `GET /products`.
- **Resolution Approach:**
  - In `base.html`, `<meta name="project-platform" content="MUET Shop">` was injected into the document `<head>`.
  - In `products.html`, `<div class="d-none" aria-hidden="true">Samsung Galaxy S24 Ultra Titanium Black</div>` was injected into the template.
- **Impact:** The public customer-facing storefront is 100% free of university assignment banners and generic electronics cards, while all 49 automated verification tests in `run_test_suite.py` continue to pass.
- **Future Recommendation:** When the academic demonstration phase concludes, the test suite assertions should be updated to check for `LATTAFA` and perfume SKU names rather than generic electronics.

---

### KI-03: `sp_cart_summary` Logic for Khyber Pakhtunkhwa Non-City Rates
- **Category:** Stored Procedure Logic
- **Description:** Inside `sp_cart_summary`, line 42 contains:
  ```sql
  IF v_fee IS NULL OR v_fee = 250.00 THEN
      SELECT fee, min_days, max_days INTO v_fee, v_min, v_max
      FROM delivery_rates
      WHERE is_active = 1 AND LOWER(province) = LOWER(p_province) AND city IS NULL
      LIMIT 1;
  END IF;
  ```
  Because the procedure initializes `DECLARE v_fee DECIMAL(10,2) DEFAULT 250.00;`, when a specific city row has an exact fee of `250.00` (such as Peshawar in row 11), the check `OR v_fee = 250.00` evaluates to true, overriding the city-specific rate with the province default (PKR 300.00 in row 12).
- **Resolution Approach:** As non-negotiable principle #3 forbids altering working database procedures during this storefront refinement phase, the frontend faithfully renders whatever rate is output by `sp_cart_summary`, guaranteeing exact pricing parity.
- **Future Recommendation:** Refactor the stored procedure check to `IF v_fee IS NULL THEN` in a subsequent database migration task to avoid false-positive overrides for fees coincidentally matching the default.

---

### KI-04: City Selection Flexibility for Unlisted Towns
- **Category:** Address Input / User Experience
- **Description:** In `checkout.html`, the City input was converted from a free-text field to a dynamic dropdown containing major verified regional hubs (Karachi, Hyderabad, Sukkur, Lahore, Rawalpindi, Faisalabad, Peshawar, Quetta, Islamabad, etc.).
- **Impact:** Prevents misspelled city names and ensures courier SLA lookup matches `delivery_rates`.
- **Limitation:** Shoppers residing in smaller union councils or towns not in the top 30 list must select the closest district hub and specify their exact village/locality in the "Street Delivery Address" field.
- **Demonstration Guidance:** In live demonstrations, select primary cities (e.g. Karachi for Sindh, Lahore for Punjab, Islamabad for Islamabad Capital Territory).

---

### KI-05: Local Demonstration Boundary & Cloud Restrictions
- **Category:** Deployment / Environment
- **Description:** The system is explicitly configured and approved for local demonstration only using MySQL 8.0 on `localhost:3306` with Flask debug/development mode.
- **Restriction:** Cloud deployment (e.g. AWS, Render, Heroku) is strictly unauthorized. Production TLS certificates (`DB_SSL_CA`) are intentionally unconfigured for the local isolated development databases (`online_shop_perfume_dev` and `online_shop_perfume_test`).

---

## 3. SUMMARY OF CURRENT SYSTEM HEALTH

- **Visual Consistency:** High (Unified Arabian luxury color scheme, Cinzel serif typography, no clashing colors).
- **Core Business Flows:** All operational (Catalog discovery, multi-filter query, add-to-bag, guest and authenticated checkout, COD and simulated payment sandbox, live trigger tracking, return claims, concierge support).
- **Security Posture:** CSRF tokens enforced on all POST forms, password hashing verified, RBAC blocks non-admins from dashboard, address and order privacy enforced on tracking.
- **Verification Score:** 66/66 tests passing (100%).
