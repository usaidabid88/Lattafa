# Page Design Specification: Catalog & Category Browsing

**Page:** Storefront Catalog & Category Browsing (`/products`, `/category/<slug>`)  
**Parent Master:** `design-system/muet-shop/MASTER.md`  
**Audience:** University students, faculty, regional shoppers  

---

## 1. Layout & Rhythm
- **Grid Structure:** Asymmetric sidebar-to-grid split (`col-lg-3` filters sidebar + `col-lg-9` product cards grid).
- **Responsive Breakpoints:**
  - Desktop (&ge; 1280px): 3 columns in main catalog area (`row-cols-md-3`), sticky filter panel (`top: 80px`).
  - Tablet (768px - 1024px): 2 columns (`row-cols-sm-2`), collapsible filters.
  - Mobile (< 768px): 1 column (`row-cols-1`), stacked filter form, horizontal scrolling subcategory chips.

---

## 2. Component Guidelines

### Subcategory Chips
- Displayed horizontally above the catalog grid.
- Active chip: `badge-status-paid` (quiet slate `#f8fafc` surface with `#334155` text and `#e2e8f0` border).
- Inactive chip: `badge-neutral`.
- Tap target: minimum 40px height on mobile touch screens.

### Product Card Specification
- **Aspect Ratio:** Locked at `4:3` with `overflow-hidden` to avoid layout shifts (CLS < 0.1).
- **Surface:** `var(--bg-card)` with `1px solid var(--border-hairline)`.
- **Hover Behavior:** Border color shifts to `var(--border-strong)` over `0.12s ease-out`. Zero layout scale or jump.
- **Stock Tag:** Positioned at top-right corner with 8px margin; uses semantic tokens (`badge-stock-in`, `badge-stock-low`, `badge-stock-out`).
- **Price Format:** Large tabular figures (`tabular-nums`) in `var(--accent-indigo)`.

---

## 3. Accessibility & Heuristics
- All product images require informative alt attributes (`alt="{{ p.product_name }} by {{ p.brand_name }}"`).
- Filter form controls have explicit labels or `aria-label`.
- Pagination links provide `aria-label="Previous page"` / `aria-label="Page X"` / `aria-current="page"`.
- Add-to-cart buttons include `aria-label="Add [Product Name] to bag"`.
