# Report Outline – Online Shopping System
**MUET DBMS CEP | Department of Software Engineering | Semester 3**
Instructor: Aisha Ashfaque | Submission date: TBD | Marks: 10

---

## Q1. Problem Identification

### Problem Statement
Small and medium online sellers in Pakistan commonly manage their products,
customers, and orders using paper records or scattered spreadsheets (Microsoft
Excel, WhatsApp messages, etc.). This approach leads to several real-world
problems:

- **Duplicate customer records** – the same customer appears twice with
  different spellings.
- **Overselling** – a product is sold to two customers simultaneously even
  though only one unit remains in stock.
- **Wrong totals** – order totals are manually calculated and often contain
  arithmetic errors.
- **No audit trail** – there is no way to know who changed an order status
  or when.
- **No business insight** – the seller cannot easily see which products sell
  the most, which are low on stock, or which customers have abandoned carts.

This project builds a fully relational **Online Shopping System** database
(MySQL 8) with a simple web interface (Flask) that stores and manages the
entire shopping process reliably and consistently.

### Intended Users (Stakeholders)

| Stakeholder | Role in the system |
|---|---|
| **Customer** | Registers an account, browses and searches products, manages a shopping cart, places orders, tracks order status, and writes product reviews. |
| **Staff** | Processes orders, updates order and shipment status, and monitors stock levels. |
| **Admin** | Manages products, categories, suppliers, and user accounts. Views sales reports, low-stock alerts, best-seller lists, and abandoned carts. |

---

## Q2. Requirements

### Functional Requirements

| # | Requirement |
|---|---|
| FR-1 | Users can register with a unique email. Passwords are stored as hashed values, never plain text. |
| FR-2 | One account has exactly one role: customer, staff, or admin. |
| FR-3 | Customers can save multiple delivery addresses; one is marked as default. |
| FR-4 | Products belong to a category (which may have a parent category) and come from a supplier. |
| FR-5 | Each product has a price (PKR), a stock quantity, and an active/inactive flag. |
| FR-6 | A customer has a shopping cart; items can be added, updated, and removed. |
| FR-7 | Checkout converts the active cart into an order with order items, a payment record, and a stock deduction. |
| FR-8 | Stock is reduced automatically when an order is placed. An order fails if any item has insufficient stock. |
| FR-9 | The entire checkout (order + items + payment + stock change) succeeds or fails as a single transaction. |
| FR-10 | Customers can write one review per product, but only for products they have received (delivered order). |
| FR-11 | Admin can cancel an order; stock is restored automatically. |
| FR-12 | Admin views: low stock, best sellers, sales per category, abandoned carts, order summary. |

### Non-Functional Requirements

| # | Requirement |
|---|---|
| NF-1 | **Integrity** – No negative stock or prices; no orphan records; no duplicate emails. |
| NF-2 | **Consistency** – Order placement is wrapped in a transaction; partial saves are impossible. |
| NF-3 | **Security** – Hashed passwords (Werkzeug), least-privilege database roles, parameterized queries (no SQL injection). |
| NF-4 | **Speed** – Indexes on columns used most in searches and joins (product name, category, user email, order date). |
| NF-5 | **Auditability** – Every order status change is recorded in audit_log by a trigger. |

---

## Q3. Database Design (answered in er_diagram.md and 01_schema.sql)

*(See ER diagram and schema script – filled in during Phase 2.)*

---

## Q4. ER Diagram

*(See docs/er_diagram.md – Mermaid source. Export to PNG for submission.)*

---

## Q5. Implementation

*(Filled in after Phase 2 and Phase 3 – include table screenshots and sample rows.)*

---

## Q6. Database Operations

*(Filled in after Phase 7 – include demo queries and web app screenshots.)*

---

## Q7. Challenges

*(Filled in by the group as real problems are encountered during development.)*

Example areas to document:
- Preventing overselling using BEFORE INSERT trigger + transaction rollback.
- Storing unit_price in order_items so old orders survive price changes.
- Setting up MySQL roles so shop_customer cannot read the users table.

---

## Q8. Testing

To verify the reliability, integrity, and performance of the database system, an automated test suite was constructed in `sql/07_tests.sql` and executed on MySQL 8.0. Every test case evaluates a specific structural constraint, trigger, transaction, or security rule.

| Test ID | Test Category & Description | Input / Action | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **T1** | Duplicate Email Rejection (UNIQUE constraint) | `INSERT` user with existing email `admin@muetshop.pk` | Rejected with Error 1062 (Duplicate entry) | Caught Error 1062: Duplicate entry for key users.email | **PASS** |
| **T2** | Negative Price Rejection (CHECK constraint) | `INSERT` product with `price = -250.00` | Rejected with Error 3819 (`chk_products_price` violated) | Caught Error 3819: Check constraint violated | **PASS** |
| **T3** | Negative Stock Rejection (CHECK constraint) | `INSERT` product with `stock_quantity = -10` | Rejected with Error 3819 (`chk_products_stock` violated) | Caught Error 3819: Check constraint violated | **PASS** |
| **T4** | Invalid Rating Rejection (CHECK constraint) | `INSERT` review with `rating = 6` (valid: 1-5) | Rejected with Error 3819 (`chk_reviews_rating` violated) | Caught Error 3819: Check constraint violated | **PASS** |
| **T5** | Oversell Blocked & ACID Rollback | Checkout 99 units when available stock is 3 | Transaction aborted, 0 orders committed, stock unchanged | Rollback confirmed. `sp_place_order` returned Oversell Error, stock untouched at 3 | **PASS** |
| **T6** | Automatic Stock Reduction via Trigger | Order 2 units of product #10 via `sp_place_order` | `stock_quantity` decremented by exactly 2 via `AFTER INSERT` trigger | Stock changed from 30 to 28 (decremented by 2) | **PASS** |
| **T7** | Automated Audit Trail on Order Status Change | Update order #9999 status from pending to cancelled | Audit record automatically written to `audit_log` | Row created in `audit_log` with status transition details | **PASS** |
| **T8** | Unverified Review Rejection via Trigger | Customer #15 attempts review on product #1 (never delivered) | Rejected with custom SQLSTATE 45000 from `trg_before_reviews_insert` | Caught SQLSTATE 45000: Review Error (Unverified purchase) | **PASS** |
| **T9** | Referential Integrity (RESTRICT on Delete) | Attempt `DELETE` on product #12 with historic `order_items` | Engine blocks deletion with Error 1451 (foreign key RESTRICT) | Caught Error 1451: foreign key constraint fails (RESTRICT) | **PASS** |
| **T10** | Cascading Deletion (ON DELETE CASCADE) | Delete user account with linked delivery address | Dependent address rows deleted automatically via CASCADE | Child address rows cleaned up cleanly (0 orphan rows) | **PASS** |
| **T11** | Least-Privilege Role Restriction | Customer role attempts `SELECT * FROM users` | Access denied by MySQL 8 privilege system | Error 1142: SELECT command denied for table 'users' | **PASS** |
| **T12** | SQL Injection Defense in Web Layer | Input `' OR '1'='1` in login and search fields | Parameterized queries treat input as literal text | Handled securely via PyMySQL `%s` parameters; zero leakage | **PASS** |

---

## Q9. Future Improvements

| Improvement | Why it would help |
|---|---|
| Payment gateway integration (JazzCash, EasyPaisa) | Allow real online payments instead of COD only |
| Product image upload | Improve the shopping experience |
| Coupon and discount system | Support promotions |
| Wishlist feature | Let customers save products for later |
| Email notifications | Notify customers of order status changes |
| Product recommendations | Suggest products based on order history |
| Table partitioning | Handle millions of orders efficiently |
| Full-text search | Faster product search across name and description |

---
*This document is updated throughout the project. Final version submitted with the report.*
