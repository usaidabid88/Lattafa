# COMPLEX ENGINEERING PROBLEM (CEP) PROJECT REPORT
## Online Shopping Database Management System (Enterprise Architecture & SRS Alignment)

**Department of Software Engineering**  
**Mehran University of Engineering and Technology (MUET), Jamshoro**  

- **Course:** Database Management Systems (DBMS)  
- **Course Instructor:** Aisha Ashfaque  
- **Semester:** 3rd Semester, 2nd Year  
- **Assessment Score:** 10 Marks  
- **Team Ownership:**
  - **Member A:** Users, Access, Support & Compliance Module (`users`, `addresses`, `audit_log`, `support_tickets`, Roles, Security)
  - **Member B:** Catalog, Brands, Media & Multi-Vendor Module (`categories`, `brands`, `suppliers`, `products`, `product_images`, `reviews`, Inventory Triggers, Seller Verification)
  - **Member C:** Orders, Payments, Fiscal Rates & Return Lifecycle Module (`delivery_rates`, `tax_rates`, `payment_methods`, `payment_attempts`, `carts`, `cart_items`, `orders`, `order_items`, `order_status_history`, `payments`, `shipments`, `return_requests`, `return_status_history`, ACID Checkout Procedures)

---

## 1. Problem Identification

### 1.1 Problem Statement
Small-to-medium retail and wholesale enterprises in Pakistan routinely manage inventory, customer inquiries, order bookings, and shipping dispatches across fragmented spreadsheets (Microsoft Excel), messaging threads (WhatsApp), and manual paper ledgers. This non-relational, ad-hoc methodology leads to critical business and technical failures:

1. **Customer Record Duplication & Drift:** A single individual placing multiple orders under slightly varying names or telephone formats produces redundant, inconsistent records with no unified order history.
2. **Catalog Overselling & Phantom Inventory:** Multiple sales channels selling concurrently without concurrency control result in accepting payments for inventory that does not physically exist.
3. **Financial Inaccuracy & Price Mutation:** Calculating order totals manually frequently results in arithmetic discrepancy. Furthermore, updating a product's retail price in a naive table inadvertently retroactively alters past financial receipts and accounting balances.
4. **Absence of Tamper-Proof Audit Trails:** Changes to delivery milestones or order statuses cannot be attributed to specific users or timestamps, leading to customer disputes and lack of operational transparency.
5. **Operational Blindness:** Without structured relational aggregation, store managers cannot readily identify high-velocity stockouts, dormant carts, or regional market demand.
6. **Checkout Drop-Off & Guest Shopper Friction:** Requiring full registration before browsing or checking out creates high cart abandonment. Conversely, naive guest checkouts lead to untracked orders, lost carts, and missing legal consent.

### 1.2 Intended Stakeholders

| Stakeholder | Key Responsibilities & Use Cases |
|---|---|
| **Customers (Guest & Authenticated)** | Browse categorized catalog, filter by brand, inspect verified ratings, manage transient or merged shopping carts, place orders anonymously or logged-in, make simulated digital/COD payments, track delivery stages, submit support inquiries, and lodge return claims. |
| **Warehouse & Support Staff** | Monitor real-time low-stock alerts, advance fulfillment stages (`pending` &rarr; `paid` &rarr; `shipped` &rarr; `delivered`), update courier tracking codes, triage customer support tickets, and process merchandise return claims against strict SLAs. |
| **Sellers / Suppliers** | Manage vendor profiles, track order fulfillment, view return/exchange requests, and undergo administrative verification before merchandise appears in public search. |
| **System Administrators** | Manage platform security, assign least-privilege database roles, perform catalog CRUD, execute cancellations with inventory restoration, evaluate financial revenue reports, inspect abandoned carts, and resolve overdue RMA claims. |

---

## 2. Requirements Specification

### 2.1 Functional Requirements (FR)
- **FR-1 [Transparent Price Calculation]:** Unified breakdown of subtotal, provincial sales tax, delivery fee, and grand total in PKR via `sp_cart_summary`.
- **FR-2 [Guest Checkout]:** Unauthenticated visitors can place orders by capturing contact details without mandatory upfront registration.
- **FR-3 [Persistent Guest Cart & Merge]:** Anonymous sessions store signed cart tokens that merge seamlessly into user carts upon login via `sp_merge_carts`.
- **FR-4 [Atomic Transaction Checkout]:** Order placement occurs in an ACID transaction (`sp_place_order` / `sp_place_guest_order`), leaving carts untouched if aborts occur.
- **FR-5 [Dynamic Delivery SLA]:** Dynamic expected delivery date range computed from `delivery_rates` based on destination province and city.
- **FR-6 [Multi-Channel Payments]:** Flexible payment adapter supporting Cash on Delivery (COD) and simulated card/wallet gateway sandboxes.
- **FR-7 [Four-Step Progress Flow]:** Visual checkout indicator guiding users through Cart, Delivery, Payment, and Confirmation.
- **FR-8 [Configurable Delivery Matrix]:** Database-driven provincial rate matrix with minimum and maximum transit day windows.
- **FR-9 [Provincial Tax Matrix]:** Database-driven tax tables providing engine-level single-source-of-truth calculations.
- **FR-10 [Payment Attempt Audit Logging]:** All gateway attempts (success, failure, cancel) recorded in `payment_attempts` with provider transaction refs.
- **FR-11 [Payment Failure Recovery]:** Dedicated retry workflow allowing immediate re-attempt or switching to Cash on Delivery.
- **FR-12 [Immutable Order Status History]:** Automatic trigger `trg_order_status_history` recording all status mutations with timestamps and user IDs.
- **FR-13 [Address Snapshot Immutability]:** Orders snapshot delivery address text at placement time to prevent historical mutation when users edit address books.
- **FR-14 [Customer Support Ticketing]:** Centralized ticketing system for shipment delays, damaged parcels, and general inquiries with staff triage queues.
- **FR-15 [Accessible Media]:** Standardized product image galleries with semantic `alt` attributes and fallback placeholders.
- **FR-16 [Minimal Friction Registration]:** Streamlined registration with PBKDF2:SHA256 password hashing.
- **FR-17 [Seller Profile Governance]:** Vendor profile management extending commercial supplier records.
- **FR-18 [Seller Verification Enforcement]:** Catalog view `v_product_catalog` restricts merchandise from unverified vendors.
- **FR-19 [Explicit Legal Consent]:** Checkbox verification recording consent to Terms of Service, Privacy Policy, and Return Policy.
- **FR-20 [Merchandise Return Claims]:** Return and replacement request lodging with issue categories, refund method, and status tracking.
- **FR-21 [Return Lifecycle & SLA Escalation]:** Trigger-audited return transitions and analytical view `v_overdue_return_requests` highlighting breaches > 48 hours.

### 2.2 Non-Functional Requirements (NFR)
- **NF-1 [Data Integrity & 3NF Normalization]:** 23 relational entities in strict Third Normal Form with explicit cascading and restrict foreign key constraints.
- **NF-2 [ACID Transaction Consistency]:** Atomic execution of checkout and order cancellations with automated rollback and inventory consistency.
- **NF-3 [Defensive Security & Injection Prevention]:** 100% parameterized queries (`%s`), CSRF protection, secure cookies (`HttpOnly`, `SameSite=Lax`), and least-privilege MySQL 8 roles.
- **NF-4 [Performance & Indexing]:** Strategic B-Tree indexes on search attributes, foreign keys, and guest cart tokens eliminating full-table scans.
- **NF-5 [Engine Auditability]:** Database-level triggers guaranteeing tamper-proof audit trails for both orders and return requests.

---

## 3. Conceptual & Logical Database Design

The schema is partitioned into 23 relational tables across 3 functional modules:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        MODULE RELATIONSHIP MAP                         │
└────────────────────────────────────────────────────────────────────────┘
 Member A: Users, Support & Compliance
   [users] ──┬──< [addresses]
             ├──< [support_tickets] >── [orders]
             └──< [audit_log]

 Member B: Catalog, Brands, Media & Multi-Vendor
   [categories] (self-ref) ──< [products] >── [reviews] >── [users]
   [brands]                 ──< [products]
   [suppliers] (sellers)    ──< [products] ──< [product_images]

 Member C: Orders, Payments, Fiscal Rates & Returns
   [delivery_rates]  ──┐
   [tax_rates]       ──┼──> [sp_cart_summary] ──> [orders] ──< [order_items]
   [payment_methods] ──┘                             │              │
   [carts] ──< [cart_items]                          ├──< [order_status_history]
                                                     ├──< [payment_attempts]
                                                     ├──= [payments]
                                                     ├──? [shipments]
                                                     └──< [return_requests] ──< [return_status_history]
```

---

## 4. Physical Database Implementation

### 4.1 Technology Stack & Engine Configuration
- **DBMS:** MySQL Community Server 8.0.46 (x86_64)
- **Storage Engine:** InnoDB (Row-level locking, ACID transactions, foreign key enforcement)
- **Character Encoding:** `utf8mb4` with `utf8mb4_unicode_ci` collation
- **Driver / ORM Layer:** PyMySQL 1.1.1 executing pure, parameterized SQL queries
- **Application Web Framework:** Python 3.14 + Flask 3.0.3 + Jinja2 + Bootstrap 5.3

### 4.2 Summary of Database Scripts
- `sql/01_schema.sql`: Full baseline DDL defining 13 tables, keys, cascade rules, and check constraints.
- `sql/02_sample_data.sql`: Realistic Pakistani seed data (PKR currency, Pakistani names/cities, salted hashes).
- `sql/03_views_indexes.sql`: 4 performance B-Tree indexes and 5 business views.
- `sql/04_procedures_triggers.sql`: 4 business triggers and 3 stored procedures.
- `sql/05_roles.sql`: MySQL 8 RBAC security definitions and grant matrices.
- `sql/06_demo_queries.sql`: Advanced operational demonstration queries across 9 thematic sections.
- `sql/07_tests.sql`: Automated test harness asserting database integrity (25 tests, T1-T25).
- `sql/08_catalog_expansion.sql`: Phase 11 catalog migration adding `brands`, `product_images`, slug/image columns, trigger `trg_product_images_single_primary_bi`, procedure `sp_set_product_primary_image`, views `v_product_catalog` and `v_category_counts`.
- `sql/09_srs_alignment.sql`: Phase 12 SRS alignment adding `delivery_rates`, `tax_rates`, `payment_methods`, `payment_attempts`, `order_status_history`, `support_tickets`, `return_requests`, `return_status_history`, procedures `sp_cart_summary`, `sp_place_guest_order`, `sp_merge_carts`, `sp_cleanup_expired_carts`, views `v_overdue_return_requests`, and triggers `trg_order_status_history`, `trg_return_status_history`.
- `sql/10_srs_alignment_fixes.sql`: Safe patch aligning `payments.method` ENUM with simulated payment gateway codes.

### 4.3 Comprehensive Dataset Overview
- **Entities / Tables:** 23 normalized tables in 3NF
- **Categories:** 14 (5 top-level departments, 9 specialized subcategories with URL slugs)
- **Brands:** 14 leading Pakistani and international brands (Paklap, Samsung, Dell, Khaadi, Dawlance, etc.)
- **Suppliers / Sellers:** 6 commercial vendors with verified credentials
- **Products:** 81 active catalog items with high-resolution photography
- **Product Images:** 81 multi-image assets with `is_primary` flags and local fallbacks
- **Users:** 15 accounts (2 Administrators, 2 Staff Members, 11 Active Customers)
- **Delivery Rates:** 5 provincial rate matrices with minimum/maximum transit days
- **Tax Rates:** 5 provincial tax brackets
- **Payment Methods:** 4 operational rails (`cod`, `simulated`, `card`, `wallet`)

---

## 5. Database Operations & Functionality

### 5.1 Advanced Stored Procedures
1. **`sp_cart_summary(p_cart_id, p_province, p_city)`:** The single source of truth for pricing calculations across cart, checkout, and invoice generation. Itemizes gross subtotal, applies provincial sales tax, calculates weight-based or flat delivery fees, and computes expected delivery date windows.
2. **`sp_place_order(p_user_id, p_address_id, p_payment_method, OUT p_order_id, OUT p_status)`:** Atomically validates stock, decrements inventory, creates order header and line items, generates payment record, and marks cart as converted within an ACID transaction.
3. **`sp_place_guest_order(...)`:** Allows unauthenticated checkout by validating contact credentials, capturing address snapshots, and executing atomic placement without requiring upfront user creation.
4. **`sp_merge_carts(p_user_id, p_guest_token)`:** Resolves guest session cart merging upon login, transferring quantities with conflict resolution (`ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)`).
5. **`sp_cancel_order(p_order_id, p_reason)`:** Transactionally transitions order to `cancelled`, automatically restoring product stock and marking payments refunded.

### 5.2 Business Triggers
1. **`trg_before_order_items_insert`:** Real-time stock validation preventing overselling by signalling SQLSTATE 45000 if line quantity exceeds on-hand stock.
2. **`trg_after_order_items_insert`:** Synchronous automatic stock deduction upon order item insertion.
3. **`trg_order_status_history`:** Tamper-evident order audit trigger logging all status changes into `order_status_history` with actor ID and timestamp.
4. **`trg_return_status_history`:** Tamper-evident merchandise return trigger logging all RMA status changes into `return_status_history`.
5. **`trg_before_reviews_insert`:** Enforces verified purchases directly in the database engine, blocking review creation unless customer has a delivered order for that product.

### 5.3 Analytical & Reporting Views
1. **`v_product_catalog`:** Denormalized catalog view combining products, categories, brands, suppliers, aggregate ratings, and primary image paths with COALESCE fallback. Restricts unverified seller goods.
2. **`v_order_summary`:** Comprehensive order audit view joining users, addresses, line items, payments, and shipments.
3. **`v_abandoned_carts`:** Identifies dormant carts untouched for &ge; 7 days, itemizing tied-up merchandise value for remarketing.
4. **`v_overdue_return_requests`:** Identifies pending return requests open for > 48 hours without staff resolution, flagging SLA violations.
5. **`v_low_stock`:** Real-time inventory replenishment warning for items with stock &le; 5 units.
6. **`v_sales_by_category`:** Aggregates gross revenue, completed order count, and units sold per department.

---

## 6. Project Challenges & Engineering Solutions

### Challenge 1: MySQL Error 1442 Trigger Re-Entrancy
- **Problem:** When inserting cart items into `order_items`, the `trg_after_order_items_insert` trigger attempted to execute `UPDATE products SET stock_quantity = ...`. Because the outer statement already had `products` open in its `FROM` clause, MySQL aborted with Error 1442.
- **Solution:** In stored procedure `sp_place_order`, we decoupled the locks by selecting cart items into a session `TEMPORARY TABLE _temp_checkout_items`. The subsequent insert read exclusively from the temporary table, allowing the trigger to safely acquire an exclusive lock on `products`.

### Challenge 2: Preservation of Diagnostics Prior to Rollback
- **Problem:** Calling `ROLLBACK;` before `GET DIAGNOSTICS` reset the diagnostic area, wiping out the trigger's custom error message (`Oversell Error: Requested quantity exceeds...`).
- **Solution:** Reordered the exception handler to capture `GET DIAGNOSTICS CONDITION 1 v_err_msg = MESSAGE_TEXT;` *before* issuing `ROLLBACK;`, preserving the exact root-cause failure string for the web UI.

### Challenge 3: Enforcing Verified Purchases at the Database Layer
- **Problem:** Web applications often enforce review eligibility in frontend code, which can be bypassed via direct API calls or SQL injection.
- **Solution:** Implemented `trg_before_reviews_insert` which directly queries relational order history inside the database engine. If zero orders exist for that `(user_id, product_id)` with status `'delivered'`, the trigger executes `SIGNAL SQLSTATE '45000'`.

### Challenge 4: Price Parity Across Cart, Checkout, and Invoices
- **Problem:** Client-side JavaScript calculations routinely drift from server-side order amounts due to tax rounding differences, leading to financial discrepancies.
- **Solution:** Mandated stored procedure `sp_cart_summary` as the single authoritative source of pricing truth for both transient cart summaries and final order invoices.

### Challenge 5: Guest Cart Merging Without Primary Key Collision
- **Problem:** When an anonymous shopper logs in, transferring line items from a guest cart into their existing user cart risks duplicate key collisions on `(cart_id, product_id)`.
- **Solution:** Procedure `sp_merge_carts` utilizes `INSERT INTO cart_items ... ON DUPLICATE KEY UPDATE quantity = cart_items.quantity + VALUES(quantity)`, seamlessly consolidating quantities before soft-deleting the guest cart.

### Challenge 6: Address Snapshot Immutability
- **Problem:** Updating a customer's address in their account profile retroactively mutated delivery addresses on historical completed orders.
- **Solution:** Added `shipping_address_text` to the `orders` table. During order placement, the address is converted to an immutable text snapshot stored directly on the order record, ensuring historical non-repudiation.

---

## 7. Testing & Verification

Verification was conducted across two independent, fully automated test harnesses:
1. `sql/07_tests.sql`: 25 automated database engine test cases verifying schema constraints, cascade rules, ACID transactions, and triggers directly inside MySQL 8.
2. `test_app.py`: 46 automated integration tests asserting HTTP responses, authentication, session tokens, RBAC, payment sandboxes, support workflows, and error handling.

### 7.1 Automated Database Test Results Matrix (`sql/07_tests.sql`)

| Test ID | Test Category & Objective | Input / Test Action | Expected Result | Actual Engine Output | Status |
|---|---|---|---|---|---|
| **T1** | Duplicate Email Rejection | `INSERT` user with existing email | Rejection with Error 1062 | `Caught Error 1062: Duplicate entry for key users.email` | **PASS** |
| **T2** | Negative Price Rejection | `INSERT` product with `price = -250` | Rejection with Error 3819 | `Caught Error 3819: Check constraint chk_products_price violated` | **PASS** |
| **T3** | Negative Stock Rejection | `INSERT` product with `stock = -10` | Rejection with Error 3819 | `Caught Error 3819: Check constraint chk_products_stock violated` | **PASS** |
| **T4** | Invalid Rating Rejection | `INSERT` review with `rating = 6` | Rejection with Error 3819 | `Caught Error 3819: Check constraint chk_reviews_rating violated` | **PASS** |
| **T5** | Oversell Prevention & ACID Rollback | Checkout 99 units when stock is 3 | Transaction aborted, 0 orders committed, stock preserved | `Rollback confirmed. Stock remained at 3. Zero orphan rows.` | **PASS** |
| **T6** | Automatic Stock Reduction Trigger | Order 2 units via `sp_place_order` | Stock decremented by 2 via `AFTER INSERT` trigger | `Stock changed from 30 to 28 (Decremented by 2)` | **PASS** |
| **T7** | Automated Audit Trail Trigger | Update order status to `cancelled` | Row created in `audit_log` via trigger | `Audit record verified in audit_log for order #9999` | **PASS** |
| **T8** | Unverified Review Rejection | Customer reviews unpurchased product | Rejected with SQLSTATE 45000 | `Caught SQLSTATE 45000: Review Error (Unverified purchase)` | **PASS** |
| **T9** | Referential Integrity (RESTRICT) | Delete product with order history | Engine blocks delete with Error 1451 | `Caught Error 1451: foreign key constraint fails (RESTRICT)` | **PASS** |
| **T10** | Cascading Deletion (CASCADE) | Delete user with delivery addresses | Child address rows deleted automatically | `Child address rows cleaned up cleanly (0 orphan rows)` | **PASS** |
| **T11** | Duplicate Brand Rejection | `INSERT` brand with existing name | Rejection with Error 1062 | `Caught Error 1062: Duplicate entry for key brands.name` | **PASS** |
| **T12** | Single Primary Image Trigger | `INSERT` second primary image | Rejected with SQLSTATE 45000 | `Caught SQLSTATE 45000: Product already has a primary image` | **PASS** |
| **T13** | Primary Image Switching Proc | Execute `sp_set_product_primary_image` | Exactly 1 image flagged primary | `Exactly 1 primary image verified after sp_set_product_primary_image` | **PASS** |
| **T14** | Category Slug Unique Constraint | `INSERT` category with existing slug | Rejection with Error 1062 | `Caught Error 1062: Duplicate entry for key categories.slug` | **PASS** |
| **T15** | Product Image Cascade on Delete | Delete non-ordered product with images | Child image rows deleted via cascade | `Cascade delete verified (0 orphan product_images rows)` | **PASS** |
| **T16** | Price Parity via `sp_cart_summary` | Call `sp_cart_summary` for Cart #1 | Returns exact subtotal, tax, delivery fee | `sp_cart_summary computed exact financial parity with zero drift` | **PASS** |
| **T17** | Guest Checkout Placement | Call `sp_place_guest_order` | Order placed with NULL user_id and guest info | `Guest order placed successfully via sp_place_guest_order` | **PASS** |
| **T18** | Guest Cart Merge on Login | Call `sp_merge_carts` with active token | Guest items moved to user cart, guest cart converted | `Guest cart merged into user cart cleanly without collision` | **PASS** |
| **T19** | Order Status Audit Trigger | Update order status to `shipped` | Trigger logs transition into `order_status_history` | `trg_order_status_history verified: new record created` | **PASS** |
| **T20** | Address Snapshot Immutability | Update address after placing order | Order snapshot remains identical to original | `Address snapshot remained identical after customer profile edit` | **PASS** |
| **T21** | Customer Support Ticketing | Insert ticket via `support_tickets` | Auto-generates unique ticket number | `Support ticket created and verified in staff queue` | **PASS** |
| **T22** | Seller Verification Governance | Query `v_product_catalog` for unverified seller | Unverified seller merchandise hidden from catalog | `v_product_catalog successfully filtered unverified seller goods` | **PASS** |
| **T23** | Return Status Audit Trigger | Update return status to `approved` | Trigger logs transition into `return_status_history` | `trg_return_status_history verified: new record created` | **PASS** |
| **T24** | Overdue Return SLA View | Query `v_overdue_return_requests` | Displays RMA requests open > 48 hours | `v_overdue_return_requests correctly highlighted aged requests` | **PASS** |
| **T25** | Payment Attempt Logging | Insert failed attempt in `payment_attempts` | Attempt logged with provider ref and reason | `Payment failure attempt verified in audit log with retry link` | **PASS** |

### 7.2 Automated Web Application Test Results (`test_app.py`)
- **Total Tests Executed:** 46
- **Total Tests Passed:** 46
- **Total Tests Failed:** 0
- **Success Rate:** 100%

---

## 8. Conclusion & Team Contribution Summary

This project delivers a complete, enterprise-grade relational database management system for e-commerce operations. By shifting business logic, integrity constraints, and audit logging into MySQL 8 stored procedures and triggers, the system achieves complete reliability, zero data corruption, and absolute non-repudiation.

| Team Member | Module Ownership | Deliverables & Viva Defense Focus |
|---|---|---|
| **Member A** | **Users, Support & Compliance** | `users`, `addresses`, `audit_log`, `support_tickets`, `05_roles.sql`, password hashing, session management, RBAC enforcement, support ticket lifecycle, customer privacy/terms consent. |
| **Member B** | **Catalog, Brands & Multi-Vendor** | `categories`, `brands`, `suppliers`, `products`, `product_images`, `reviews`, `v_product_catalog`, `v_category_counts`, self-referencing joins, verified purchase trigger, multi-image gallery management, seller verification. |
| **Member C** | **Orders, Payments, Fiscal & Returns** | `delivery_rates`, `tax_rates`, `payment_methods`, `payment_attempts`, `carts`, `cart_items`, `orders`, `order_items`, `order_status_history`, `payments`, `shipments`, `return_requests`, `return_status_history`, `sp_cart_summary`, `sp_place_order`, `sp_place_guest_order`, `sp_merge_carts`, `sp_cancel_order`, payment sandbox recovery, overdue RMA view. |

**Instructor Evaluation Sign-off:**  
Department of Software Engineering, Mehran University of Engineering and Technology, Jamshoro.
