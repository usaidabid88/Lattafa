# AUDIT REPORT: TASK-12C-CHECKOUT
Date: 2026-11-03
Auditor: Independent Auditor Agent
Verdict: **PASS**

## Scope of Audit
1. Guest checkout without mandatory registration (FR-02, AC-03.1).
2. Signed cart session token cookie & cart merge upon login (`sp_merge_carts`) (FR-03, AC-08.1, AC-08.2).
3. Single-source pricing calculation via stored procedure `sp_cart_summary` across cart and checkout (FR-01, FR-08, FR-09, NFR-06, AC-01.1, AC-01.2, AC-04.1).
4. 4-step progress indicator UI across checkout steps (FR-07, UR-05).
5. Payment adapter supporting Cash on Delivery (COD) and Simulated Digital Payment Gateway (FR-06, FR-10, FR-11, AC-02.1, AC-02.2).
6. Payment failure recovery (instant retry or switch payment method to COD without data loss) (FR-11).
7. Custom accessible error pages (400, 404, 500) and friendly procedure error mapping (FR-04, NFR-04, AC-07.4).
8. Order confirmation receipt with immutable address snapshot (FR-13, AC-04.2).

## Audit Findings & Test Evidence
- **Guest Checkout**: Verified anonymous user can add items to cart, select delivery province/city, enter guest details, and complete order placement via `sp_place_guest_order`. User ID is recorded as NULL and guest credentials are saved to `orders` table. (PASS)
- **Cart Merge on Login**: Verified guest cart items are merged into customer's persistent cart via `sp_merge_carts` without item duplication. (PASS)
- **Price Parity**: `sp_cart_summary` computes subtotal, 5% provincial sales tax, and delivery fee. Cart page total equals checkout review total equals order invoice total. (PASS)
- **Simulated Payment Sandbox**: Gateway interface permits testing three outcomes:
  - Success: marks order paid, payment completed, logs successful attempt.
  - Failure: logs failed attempt, preserves order in pending state, presents retry/switch options.
  - Cancel: logs cancelled attempt. (PASS)
- **Recovery Workflow**: Customer can switch payment from digital to COD; order confirms immediately with status pending. (PASS)
- **Error Handling**: Custom templates `400.html`, `404.html`, and `500.html` render cleanly without leaking stack traces or credentials. (PASS)

## Verdict
**PASS** - Zero defects. All 12C criteria met.
