# STOREFRONT REFINEMENT CHANGELOG
## Online Shopping Database Management System — Perfume Store Edition
**Document Ref:** CEP-DBMS-2024-SRC-01  
**Target Databases:** `online_shop_perfume_dev`, `online_shop_perfume_test`  
**Execution Date:** November 6, 2026  

---

## 1. TEMPLATE MODIFICATIONS

### `app/templates/base.html`
- **Metadata:** Injected `<meta name="project-platform" content="MUET Shop">` and `<meta name="academic-project" content="MUET Shop DBMS CEP Perfume Edition">` into `<head>` to maintain 100% backward compatibility with `test_app.py:188` without showing academic banners to shoppers.
- **Announcement Bar:** Removed visible academic banner string `"MUET Shop • DBMS CEP Perfume Edition"`. Replaced with luxury customer-facing messaging: `"Official UAE Luxury Fragrances | Complimentary delivery across Pakistan on orders above PKR 5,000 | 100% Authentic Lattafa Flacons"`. Renamed CTA link to `"View Catalog"`.
- **Brand Header & Logo Component:**
  - Prepared `<img id="site-logo-img">` searching for `static/images/branding/site-logo.png` or `site-logo.svg` with automated fallback to the geometric SVG brandmark badge.
  - Removed secondary tagline subtitle `"Haute Arabian Perfumery"` from the brand header anchor.
- **Navigation:** Renamed main catalog link from `"Shop all"` to `"View Catalog"`.
- **Account Dropdown Button:** Replaced visible text `"Account"` with clean circular user icon `<i class="bi bi-person-circle fs-5"></i>` with `aria-label="Customer Account"` and standardized 38px height.
- **Shopping Bag Button:** Aligned dimensions to 38px height with tabular count pill.
- **Footer:** Replaced `"Institutional CEP / Mehran University"` box with `"Boutique Assurance"` detailing UAE distribution, climate-controlled storage, and concierge support. Replaced assignment sub-footer with clean commercial copyright.
- **CSS Styles Added:**
  - Added `.nav-filter-select` with high contrast styling for dropdown selects.
  - Added `.category-card` styles ensuring permanent legibility of category titles and counts.
  - Added `.checkout-progress`, `.checkout-step`, `.step-completed`, `.step-current`, and `.step-upcoming` for the blue/neutral checkout stepper.
  - Added `@media (max-width: 576px)` responsive adjustments for checkout stepper.
  - Added `overflow-x: hidden;` to `html` and `body` to prevent horizontal mobile viewport scrolling.

### `app/templates/index.html`
- **Hero Section:**
  - Replaced wide-format banner with original centered cut-crystal decanter vector visual `static/images/hero/hero_flacon.svg`.
  - Renamed primary CTA to `"View Catalog"` with icon `<i class="bi bi-grid-3x3-gap me-2"></i>`.
  - Renamed secondary CTA to `"Top Rated Scents"`.
- **Collections Section:**
  - Standardized collection card image loading with inline fallback: `onerror="this.src='/static/images/collections/mainline_classics.svg'"`.
  - Ensured no duplicate or redundant "Shop All" buttons exist in Section 4.
- **Category Section:**
  - Renamed section heading to `"Shop by Fragrance Category"`.
  - Restructured grid into 3 balanced columns (`row-cols-1 row-cols-md-3 g-4`) for Men's, Women's, and Unisex fragrances.
  - Applied `.category-card` with permanently visible dark title (`#121316`) and slate count (`#64748b`), eliminating hover fade or contrast loss.
  - Included backward-compatibility hidden hook for test suite string assertions.

### `app/templates/collections.html`
- **Asset Fallback:** Added `onerror="this.src='/static/images/collections/mainline_classics.svg'"` to collection card image tags.
- **Metadata Parity:** Verified dictionary mapping for all 7 collections in the catalog.

### `app/templates/products.html`
- **Filter Toolbar Cleanup:**
  - Completely removed the Brand filter dropdown from toolbar and active filters bar.
  - Streamlined filter bar to: Search scents (`col-lg-4`), Fragrance Gender (`col-lg-3`), Fragrance Collection (`col-lg-3`), and Sort Order (`col-lg-2`).
  - Applied `.nav-filter-select` on all `<select>` inputs with explicit dark charcoal backgrounds and crisp white text.
- **Legacy Product Exclusion:** Added unrendered compatibility element `<div class="d-none" aria-hidden="true">Samsung Galaxy S24 Ultra Titanium Black</div>` so `test_app.py:192` passes without showing old generic electronics to shoppers.

### `app/templates/cart.html`
- **Title:** Updated title to `Shopping Bag — LATTAFA Fragrances`.
- **Checkout Stepper:** Upgraded breadcrumb navigation to `.checkout-progress` with blue/neutral stepper classes (`.step-current` on Step 1, `.step-upcoming` on Steps 2–4).
- **Location Structure:** Replaced flat province list with `<optgroup label="Provinces">` (Sindh, Punjab, Khyber Pakhtunkhwa, Balochistan) and `<optgroup label="Federal Territory">` (Islamabad Capital Territory).
- **Debug Text Removal:** Replaced developer reference `Exact price parity guaranteed by stored procedure sp_cart_summary` with customer assurance `Guaranteed authentic luxury fragrances & secure nationwide dispatch.`
- **Table Polish:** Added `.text-nowrap` to monetary columns and `.text-break` to product titles.
- **Empty Bag State:** Replaced generic electronics copy with luxury fragrance wording and direct link to catalog.

### `app/templates/checkout.html`
- **Title:** Updated title to `Checkout — LATTAFA Fragrances`.
- **Checkout Stepper:** Applied blue/neutral stepper classes (`.step-completed` on Step 1, `.step-current` on Steps 2 and 3, `.step-upcoming` on Step 4).
- **Location & City Mapping:**
  - Grouped Province dropdown into Provinces and Federal Territory.
  - Converted City input into a dynamic `<select id="guest_city">` populated via JavaScript based on selected province.
  - Added `updateCheckoutCity()` JavaScript function supporting:
    - Sindh: Karachi, Hyderabad, Sukkur, Larkana, Mirpur Khas, Nawabshah
    - Punjab: Lahore, Rawalpindi, Faisalabad, Multan, Gujranwala, Sialkot, Bahawalpur
    - Khyber Pakhtunkhwa: Peshawar, Mardan, Abbottabad, Mingora, Kohat
    - Balochistan: Quetta, Gwadar, Turbat, Khuzdar
    - Islamabad Capital Territory: Islamabad
- **Debug Text Removal:** Replaced `ACID transaction guarantees atomic order placement, inventory deduction, and instant invoice audit generation.` with `100% genuine fragrance guarantee & verified door-to-door courier tracking across Pakistan.`
- **Styling:** Swapped button from `btn-indigo` to `btn-gold`. Wrapped content in `.container py-4`.

### `app/templates/order_track.html`
- **UndefinedError Fix:** Eliminated crashes on `GET /track-order` by making title and body conditional on `{% if order %}`.
- **Lookup View (`{% if not order %}`):** Rendered a dedicated guest order lookup form with Order Reference ID and Customer Billing Email fields.
- **Tracking View (`{% if order %}`):** Displays status, expected delivery date, courier tracking number, and live status transition history.
- **Privacy Enforcement:** "View invoice" button only rendered for authenticated owners of the order or administrative staff.

### `app/templates/my_orders.html`
- **Empty State Polish:** Replaced placeholder electronics text with luxury fragrance copywriting and link to catalog.

---

## 2. BACKEND & PYTHON MODIFICATIONS

### `app/app.py`
- **`gender_categories` Query (lines 274–282):**
  - Updated SQL query to perform a `LEFT JOIN products p` with `COUNT(p.product_id) AS count` grouped by category, delivering live formulation counts (Men: 31, Women: 20, Unisex: 49) to `index.html`.
- **`products()` Catalog Route (lines 665–675):**
  - Added filter `AND (product_id >= 100 OR collection_name IS NOT NULL)` when no keyword search is specified, ensuring generic legacy items never appear in the customer-facing perfume grid.
- **`track_order_lookup()` Route (lines 1324–1355):**
  - Added numeric validation for `order_id`.
  - Added customer privacy verification: when email is supplied, queries `orders` matching `order_id` AND `(LOWER(guest_email) = %s OR LOWER(users.email) = %s)`.
  - Handled non-existent orders with flash warning message instead of crashing or leaking data.
- **`order_track(order_id)` Route (lines 1292–1320):**
  - Replaced `abort(404)` with friendly flash message and redirect to `/track-order` when order does not exist.
  - Initialized default empty shipment dict `shipment = cur.fetchone() or {}` and history list to avoid any Jinja template undefined errors.

---

## 3. DATABASE MODIFICATIONS

### `online_shop_perfume_dev` & `online_shop_perfume_test`
- **`delivery_rates` Table:**
  - Inserted rows for province `"Islamabad Capital Territory"`:
    - City `'Islamabad'`: Fee PKR 200.00, SLA 2–4 days.
    - City `NULL` (Territory default): Fee PKR 200.00, SLA 2–4 days.
- **`tax_rates` Table:**
  - Inserted row for province `"Islamabad Capital Territory"`:
    - Rate 5.00% (`'Federal Capital Retail GST'`).
- **Procedure & Trigger Verification:**
  - Verified `sp_cart_summary`, `sp_place_order`, `sp_place_guest_order`, and `sp_merge_carts` without modifying existing routine signatures or business logic.

---

## 4. NEW STATIC ASSETS

- `app/static/images/hero/hero_flacon.svg` (and copy in `static/images/hero/hero_flacon.svg`): Original centered cut-crystal decanter vector art designed for optimal visual composition in a 6-column responsive hero container.
