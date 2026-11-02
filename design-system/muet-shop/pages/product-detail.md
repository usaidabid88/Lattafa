# Page Design Specification: Product Detail & Gallery

**Page:** Product Detail View (`/product/<id>`)  
**Parent Master:** `design-system/muet-shop/MASTER.md`  

---

## 1. Layout & Rhythm
- **Split Ratio:** Balanced two-column split (`col-lg-6` gallery column + `col-lg-6` specification & purchasing column).
- **Below Fold:** Full-width verified customer review module and review submission form.

---

## 2. Component Guidelines

### Multi-Image Gallery
- **Primary Stage:** `aspect-ratio: 1/1` square container on `var(--bg-raised)` neutral fill with `object-fit: contain` to preserve product geometry.
- **Thumbnail Strip:** 68&times;68px touch targets with 8px gaps (`overflow-x-auto`).
- **Active Indicator:** Selected thumbnail has `opacity: 1` and `aria-pressed="true"`; inactive thumbnails have `opacity: 0.75` and `aria-pressed="false"`.
- **Image Switcher Motion:** 100ms quick opacity tween without layout reflow.

### Purchasing Box
- **Price Block:** Large headline `tabular-nums` in `var(--accent-indigo)` on `var(--bg-raised)` card.
- **Quantity Selector:** Number input with 40px height and centered text alignment.
- **Primary CTA:** Full-width `btn-indigo` with high-contrast text and minimum 44px touch target.
- **Out of Stock Alert:** Quiet amber banner explaining replenishment status.

### Verified Reviews Module
- Enforced at database engine layer via `trg_before_reviews_insert`.
- Review cards sit on `var(--bg-raised)` with star ratings in architectural gold (`#c59b27`).
- Timestamps set in monospace `tabular-nums`.
