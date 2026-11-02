# TASKS.md - Phase 12 & 13 Task Board

| Task ID | Description | Owner | Dependencies | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TASK-12AB-VERIFY** | Verify 12A traceability matrix and 12B schema migration objects | AUDITOR | None | DONE (PASS) |
| **TASK-12C-GUEST-CART** | Guest session cookie token & atomic cart merge on login (`sp_merge_carts`) | CHECKOUT | TASK-12AB-VERIFY | DONE (PASS) |
| **TASK-12C-PRICING** | Single source pricing with `sp_cart_summary` (subtotal, tax, fee, delivery dates) | CHECKOUT | TASK-12C-GUEST-CART | DONE (PASS) |
| **TASK-12C-CHECKOUT-FLOW**| 4-step progress UI, guest & auth checkout, address snapshot, order confirmation | CHECKOUT | TASK-12C-PRICING | DONE (PASS) |
| **TASK-12C-PAYMENTS** | Payment adapter (COD & Simulated Gateway: success, fail, cancel, retry/change) | CHECKOUT | TASK-12C-CHECKOUT-FLOW | DONE (PASS) |
| **TASK-12C-ERRORS** | Friendly error mapping & custom error templates (400, 404, 500) | CHECKOUT | TASK-12C-PAYMENTS | DONE (PASS) |
| **TASK-12C-AUDIT** | Audit 12C checkout & pricing implementation | AUDITOR | TASK-12C-ERRORS | DONE (PASS) |
| **TASK-12D-TRACKING** | Customer order status tracking page with timeline from `order_status_history` | TRUST | TASK-12AB-VERIFY | DONE (PASS) |
| **TASK-12D-TICKETS** | Support tickets customer submission form & staff triage queue | TRUST | TASK-12D-TRACKING | DONE (PASS) |
| **TASK-12D-RETURNS** | Return & replacement claims, photo proof upload, seller queue & overdue SLA view | TRUST | TASK-12D-TICKETS | DONE (PASS) |
| **TASK-12D-SELLERS** | Seller verification dashboard (`/admin/sellers`) & catalog filter enforcement | TRUST | TASK-12D-RETURNS | DONE (PASS) |
| **TASK-12D-POLICIES** | Privacy, terms & returns pages, mandatory consent checkboxes & header/footer link | TRUST | TASK-12D-SELLERS | DONE (PASS) |
| **TASK-12D-ABANDONED** | Admin dashboard abandoned carts view integration (`v_abandoned_carts`) | TRUST | TASK-12D-POLICIES | DONE (PASS) |
| **TASK-12D-AUDIT** | Audit 12D trust, support & seller implementation | AUDITOR | TASK-12D-ABANDONED | DONE (PASS) |
| **TASK-12E-A11Y-MOBILE**| Accessibility audit (labels, contrast, touch targets, alt) & 390px/1280px screenshots | QUALITY | TASK-12C-AUDIT, TASK-12D-AUDIT | DONE (PASS) |
| **TASK-12F-TEST-SHEET** | Complete SRS acceptance criteria test sheet (`docs/srs_test_sheet.md`) | AUDITOR | TASK-12E-A11Y-MOBILE | DONE (PASS) |
| **TASK-12F-EXPAND-TESTS**| Comprehensive automated test additions in `sql/07_tests.sql` & `test_app.py` | AUDITOR | TASK-12F-TEST-SHEET | DONE (PASS) |
| **TASK-12F-DOCS** | Update ER diagram, FINAL_REPORT.md, and viva_notes.md | DOCS | TASK-12F-EXPAND-TESTS | DONE (PASS) |
| **TASK-13A-PROD** | Production readiness: Dockerfile, compose, /health, security headers, Gunicorn | LEAD | TASK-12F-DOCS | DONE (PASS) |
| **TASK-FINAL-REPORT** | Final comprehensive overnight `MORNING_REPORT.md` compilation | LEAD | ALL | DONE (PASS) |
