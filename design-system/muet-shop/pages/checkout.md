# Page Design Specification: Checkout & Settlement

**Page:** Atomic Checkout (`/checkout`)  
**Parent Master:** `design-system/muet-shop/MASTER.md`  

---

## 1. Layout & Rhythm
- **Split Ratio:** `col-lg-7` order reconciliation table + `col-lg-5` address & payment selection panel.
- **Visual Anchor:** Trust banner explaining ACID transaction and inventory lock guarantees.

---

## 2. Component Guidelines

### Order Line Table
- Displays unit prices and line totals in `tabular-nums`.
- Fixed total payable row on `var(--bg-raised)` with prominent indigo figure.

### Selection Panels (Address & Payment)
- Radio inputs wrapped in full-card touch areas with minimum 44px height.
- Checked cards maintain subtle border accent and clean spacing.
- Clear distinction between regional Pakistani payment rails (Cash on Delivery, 1Link/PayPak, IBFT Raast, Easypaisa/JazzCash).

### Primary Action
- Single primary indigo button: "Confirm and place order".
- Disabled state or instant loading feedback upon form submit to prevent double-charging.
