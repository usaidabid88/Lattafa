# Viva Notes
**Project:** Online Shopping System – DBMS CEP, MUET SE Semester 3
**Instructor:** Aisha Ashfaque

---

---

## Phase 0 – Setup

### Member A – Users and Access
The project uses a `.env` file to store database credentials (host, port, user, password, database name). This means if you change the password or move to a server, you only edit one file — the code never needs to change. In a viva, say: "We separated configuration from code so credentials are never accidentally shared."

### Member B – Catalog and Inventory
`db.py` provides a single `get_connection()` function that the whole app uses. Every query goes through this function, which means all connections use the same settings (utf8mb4 encoding, DictCursor for named columns, autocommit off so we control transactions). In a viva, say: "Centralising the connection avoids repeating code and makes it easy to change settings in one place."

### Member C – Orders and Payments
We installed PyMySQL (a pure-Python MySQL driver) and python-dotenv (reads .env files). `autocommit=False` is critical for Phase 5: it means a group of SQL statements (place order + deduct stock + create payment) either all succeed or all roll back together. In a viva, say: "autocommit=False is the foundation of our transaction safety."

---

---

## Phase 1 – Requirements and ER Design

### Member A – Users and Access
1. We designed `users` with a UNIQUE constraint on `email` so no duplicate accounts can exist.
2. A user can have multiple delivery addresses (1-to-many relationship with `addresses`), with one flagged as default.
3. Passwords will be stored as cryptographic hashes, never plaintext, meeting non-functional security requirements.
4. The `audit_log` entity captures changes independently to maintain accountability without modifying operational tables.
5. In the viva, say: "Our user entity model decouples identity from physical shipping locations and provides full auditability."

### Member B – Catalog and Inventory
1. The `categories` table uses a self-referencing foreign key (`parent_category_id`) to support multi-level subcategories (e.g., Electronics -> Laptops).
2. `products` has mandatory foreign keys to `categories` and `suppliers`, ensuring every product has a clear classification and source.
3. Product pricing and stock constraints (`price >= 0`, `stock_quantity >= 0`) enforce business domain rules at the database engine level.
4. `reviews` links users and products with a composite UNIQUE rule, ensuring a customer cannot spam multiple reviews for the same product.
5. In the viva, say: "We used a self-referencing relationship for categories and database-level constraints to prevent negative stock and fake review spam."

### Member C – Orders and Payments
1. The shopping cart and order workflows are separated into `carts`/`cart_items` (temporary) and `orders`/`order_items` (immutable history).
2. Many-to-many relationships between orders/carts and products are resolved cleanly through `order_items` and `cart_items` junction tables.
3. `order_items` deliberately stores `unit_price` at the moment of purchase, preserving historical transaction totals even if catalog prices change later.
4. Each order has a 1-to-1 relationship with `payments` and a 1-to-(0 or 1) relationship with `shipments` created after payment confirmation.
5. In the viva, say: "Storing unit_price in order_items is deliberate intentional denormalization to protect past accounting records from future catalog price edits."

---

---

## Phase 2 – Schema Implementation

### Member A – Users and Access
1. In `users`, `email` has a UNIQUE constraint and index to prevent account collision and accelerate login lookup.
2. In `addresses`, we chose `ON DELETE CASCADE` because if a user is completely deleted, their delivery addresses become irrelevant.
3. In `orders`, the foreign key `fk_orders_user` has `ON DELETE RESTRICT` so a user with order history cannot be accidentally erased.
4. Passwords in `users` are allocated `VARCHAR(255)` to accommodate modern hash algorithms like bcrypt/scrypt/argon2 with salt.
5. In the viva, say: "We used cascading delete on ephemeral address data, but restricted delete on users who have active order history to preserve financial records."

### Member B – Catalog and Inventory
1. In `categories`, `parent_category_id` references `category_id` with `ON DELETE SET NULL` so deleting a parent moves children to top-level.
2. `products` uses explicit `CHECK (price >= 0.00)` and `CHECK (stock_quantity >= 0)` constraints enforced by MySQL 8.
3. The foreign keys from `products` to `categories` and `suppliers` use `ON DELETE RESTRICT` to protect against orphan products.
4. `reviews` features a composite unique constraint `UNIQUE (user_id, product_id)` to prevent multiple duplicate reviews per user.
5. In the viva, say: "MySQL 8 enforces CHECK constraints at the storage engine level, guaranteeing prices and quantities never become negative even if an application bug occurs."

### Member C – Orders and Payments
1. In `order_items`, `unit_price` is stored explicitly instead of referencing `products.price` so historical invoice prices never change.
2. Both `cart_items` and `order_items` utilize composite primary keys `(cart_id, product_id)` and `(order_id, product_id)` for natural uniqueness.
3. `payments` and `shipments` have a UNIQUE constraint on `order_id` to strictly enforce a 1-to-1 relationship with `orders`.
4. `ON DELETE CASCADE` on `order_items`, `payments`, and `shipments` ensures that if an uncommitted draft order is purged, its child rows are cleaned up cleanly.
5. In the viva, say: "Our design uses composite primary keys for junction tables and UNIQUE constraints on foreign keys to model true 1-to-1 relationships in relational standard."

---

---

## Phase 3 – Sample Data

### Member A – Users and Access
1. We populated 15 user accounts spanning three roles (2 admin, 2 staff, 11 customer) with Pakistani names and contacts.
2. All sample passwords are encrypted with standard PBKDF2:SHA256 salted hashes, matching real production security.
3. 20 realistic postal addresses across Karachi, Hyderabad, Jamshoro, Lahore, and Islamabad were mapped to user accounts.
4. Users have default and secondary delivery addresses to demonstrate 1-to-many relationship capability in queries.
5. In the viva, say: "We populated multi-role user accounts with salted password hashes so the database is secure from day one and immediately ready for Flask authentication."

### Member B – Catalog and Inventory
1. The catalog contains 8 categories arranged hierarchically (e.g. Electronics has children Laptops and Mobile Phones).
2. 5 domestic Pakistani suppliers provide stock across 30 realistic consumer products priced in Pakistani Rupees (PKR).
3. Inventory levels were seeded with realistic variations, including deliberate low-stock products (e.g. stock < 5) to test inventory alerts.
4. 20 customer reviews were seeded with diverse ratings (1 to 5) and contextual feedback reflecting local use cases.
5. In the viva, say: "Our catalog includes self-referencing subcategories and intentionally seeded low-stock items to rigorously test reporting views and replenishment alerts."

### Member C – Orders and Payments
1. 25 realistic orders were inserted covering all lifecycle stages: delivered, shipped, paid, pending, and cancelled.
2. Every order total mathematically reconciles to the exact sum of its `order_items` quantity multiplied by stored `unit_price`.
3. 25 payment rows reflect diverse payment rails (Cash on Delivery, Debit/Credit Card, Bank Transfer, JazzCash/EasyPaisa wallet).
4. 19 shipments track couriers (TCS, Leopards, M&P, Trax) with realistic dispatch and delivery timestamps.
5. In the viva, say: "We verified with a SQL integrity check that 100% of order totals match the sum of their line items, proving financial consistency across the sample dataset."

---

---

## Phase 4 – Views and Indexes

### Member A – Users and Access
1. We created `v_order_summary` to denormalize `orders`, `users`, `payments`, and `shipments` into a single queryable object.
2. This protects customer passwords and internal database IDs by selecting only relevant profile fields for receipts and customer care.
3. We built the composite index `idx_orders_user_date` on `(user_id, order_date DESC)` to optimize user order history lookup.
4. The EXPLAIN output confirms MySQL uses this index directly, eliminating costly sorting operations (`Using filesort`).
5. In the viva, say: "Our composite index on (user_id, order_date) satisfies both the WHERE filter and ORDER BY clause simultaneously with zero temporary file sorting."

### Member B – Catalog and Inventory
1. The `v_low_stock` view filters products where `stock_quantity <= 5` and joins supplier contact numbers for rapid replenishment.
2. `v_best_sellers` computes sales velocity by summing line-item quantities for delivered/shipped orders to highlight trending items.
3. We created `idx_products_name` on `products(name)` to turn full-table catalog scans into targeted index ref lookups.
4. Our EXPLAIN output demonstrates an indexed product name lookup examines exactly 1 row instead of reading all rows sequentially.
5. In the viva, say: "We used indexing on product names to achieve O(log N) lookup time and built dedicated inventory views so staff never miss low stock warnings."

### Member C – Orders and Payments
1. The `v_sales_by_category` view aggregates gross revenue and items sold by department, ignoring uncompleted or refunded orders.
2. The `v_abandoned_carts` view detects carts inactive for 7+ days, calculating potential lost revenue to assist remarketing.
3. We created `idx_order_items_product` on `order_items(product_id)` to speed up line-item joins across thousands of historic orders.
4. Using database views provides data abstraction: if report calculation rules change, we update the view definition without touching application code.
5. In the viva, say: "Views provide logical data independence—the web dashboard queries v_sales_by_category without needing to understand the underlying 4-table join."

---

---

## Phase 5 – Procedures, Triggers, and Transactions

### Member A – Users and Access
1. We implemented `trg_after_orders_update_audit` on `orders` to capture every lifecycle status change automatically into `audit_log`.
2. This creates an unforgeable compliance trail of order progress (pending -> paid -> shipped -> delivered -> cancelled) with timestamps.
3. Because auditing is triggered inside the database engine, even direct updates via MySQL console are logged without bypassing security.
4. Passwords and sensitive user credentials are excluded from operational logs to preserve customer privacy.
5. In the viva, say: "By placing our audit logging in an AFTER UPDATE database trigger, we achieve tamper-proof accountability independent of web application code."

### Member B – Catalog and Inventory
1. The `trg_before_order_items_insert` trigger checks inventory and throws custom SQLSTATE 45000 if requested quantity exceeds stock.
2. The `trg_after_order_items_insert` trigger immediately deducts product inventory as line items are added to an order.
3. To prevent MySQL Error 1442 (mutating a table used in the same query), our stored procedure uses an isolated temporary snapshot.
4. The `trg_before_reviews_insert` trigger rejects review submissions unless the customer has a confirmed 'delivered' order for that product.
5. In the viva, say: "We enforce stock verification and verified-purchase review integrity using engine-level triggers that abort fraudulent transactions before data enters the table."

### Member C – Orders and Payments
1. The `sp_place_order` procedure wraps checkout inside an atomic transaction with `DECLARE EXIT HANDLER FOR SQLEXCEPTION`.
2. Crucially, `GET DIAGNOSTICS` is invoked before `ROLLBACK` to preserve the trigger's error message before diagnostic state resets.
3. If an item exceeds stock, the procedure initiates a complete rollback: zero orders, zero order items, and zero payments remain.
4. The `sp_cancel_order` procedure runs inside a transaction to restore inventory counts back to catalog products and trigger audit updates.
5. In the viva, say: "Our checkout procedure guarantees the Atomicity and Consistency of ACID—either the whole order, items, payments, and stock update commit together, or none of them do."

---

---

## Phase 6 – Roles and Privileges

### Member A – Users and Access
1. We implemented MySQL 8 native Role-Based Access Control (RBAC) with three distinct roles: `shop_admin`, `shop_staff`, and `shop_customer`.
2. The `shop_customer` role is strictly denied SELECT access on the `users` table, preventing malicious extraction of credential hashes.
3. Neither staff nor customers have DELETE privileges on `users`, preserving foreign key reference integrity across orders.
4. Using roles allows database administrators to grant privileges to a role once, rather than manually configuring each individual database account.
5. In the viva, say: "We applied the Principle of Least Privilege so customer accounts can only browse catalog data, while customer credential tables remain strictly forbidden."

### Member B – Catalog and Inventory
1. The `shop_staff` role receives targeted column-level UPDATE privileges on `products.stock_quantity` for inventory adjustments.
2. Staff members cannot execute structural DDL statements (like `DROP TABLE` or `ALTER TABLE`) on catalog tables.
3. Customer accounts possess read-only privileges on `products`, `categories`, and `reviews`, preventing catalog vandalism.
4. Product deletions are restricted to `shop_admin`, protecting against inadvertent catalog disruption.
5. In the viva, say: "Column-level GRANTs in MySQL 8 permit warehouse staff to update stock counts without granting them permission to modify product names or retail prices."

### Member C – Orders and Payments
1. The `shop_customer` role is granted EXECUTE permission on `sp_place_order` to conduct checkout through our secured transaction pipeline.
2. Direct insertion or modification of `orders` and `payments` tables is withheld from customer accounts to prevent price tampering.
3. The `shop_staff` role has column-level UPDATE on `orders.status` and `shipments` courier tracking columns to advance shipments.
4. Because the checkout procedure runs with DEFINER rights, customers execute the controlled business logic without direct table permissions.
5. In the viva, say: "Customers place orders solely through stored procedures, preventing users from forging order amounts or directly manipulating invoice tables."

---

---

## Phase 7 – Demonstration Operations (Assignment Question 6)

### Member A – Users and Access
1. We demonstrated customer account registration and delivery address association using parameterized INSERT statements.
2. Our customer ranking query uses `GROUP BY` and `HAVING total_spent_pkr > 30000` to isolate VIP customers for loyalty perks.
3. We showed address state updates where toggling `is_default` ensures exactly one default shipping destination per account.
4. An unengaged user subquery with `NOT IN (SELECT user_id FROM orders)` identifies registered shoppers who never completed an order.
5. In the viva, say: "Our user queries showcase 1-to-many relationship traversal, aggregation by customer ID, and subquery filtering for targeted marketing."

### Member B – Catalog and Inventory
1. We demonstrated multi-criteria catalog searches combining `LIKE` wildcards with index range scans (`price BETWEEN x AND y`).
2. Our supplier valuation query aggregates total capital tied in warehouse inventory grouped by merchant with `HAVING total_units > 10`.
3. A correlated subquery calculates category-specific average prices on the fly to detect premium-tier products.
4. The hierarchical category query performs a self-referencing `LEFT JOIN` on `categories` to reconstruct the department-subcategory tree.
5. In the viva, say: "We used correlated subqueries to evaluate relative pricing and self-joins on categories to display full catalog taxonomy."

### Member C – Orders and Payments
1. We wrote a 5-table relational JOIN uniting `orders`, `users`, `addresses`, `order_items`, `products`, `payments`, and `shipments`.
2. This master join computes line subtotals `(quantity * unit_price)` dynamically alongside shipping tracking numbers and payment states.
3. Our geographical aggregation query calculates gross revenue and parcel volume by destination city (Karachi, Hyderabad, Islamabad, etc.).
4. Demonstrating DELETE on `cart_items` proves that transient cart entries can be deleted without cascading destruction of catalog products.
5. In the viva, say: "Our 5-table invoice query demonstrates how normalized tables come together cleanly into a single customer receipt without data redundancy."

---

---

## Phase 8 – Web User Interface (Flask & Jinja)

### Member A – Users and Access
1. We implemented secure authentication using `werkzeug.security` with salted cryptographic hashing and validation.
2. User sessions store authenticated credentials in encrypted browser cookies, tracking active customer and admin roles.
3. We created `@login_required` and `@admin_required` route decorators to protect sensitive endpoints from unauthorized access.
4. If an ordinary customer attempts to access `/admin`, the application instantly intercepts and redirects with an access-denied alert.
5. In the viva, say: "We used parameterized SQL queries (%s) everywhere, making our Flask application 100% immune to SQL injection attacks."

### Member B – Catalog and Inventory
1. The storefront catalog (`/products`) provides real-time search and category filtering powered directly by parameterized SQL.
2. Product detail pages display live inventory status badges (In Stock, Low Stock, Out of Stock) based on database quantities.
3. The Admin Product Manager (`/admin/products`) allows staff to add and edit catalog items, update retail prices, and toggle visibility.
4. Verified customer reviews and 1-5 star ratings are displayed on product detail pages with custom trigger error handling.
5. In the viva, say: "Our catalog interface dynamically reflects live database state, ensuring customers never see outdated prices or phantom stock."

### Member C – Orders and Payments
1. The shopping cart (`/cart`) maintains session item selections in the database, allowing quantity edits and safe line item removals.
2. The checkout page (`/checkout`) calls stored procedure `sp_place_order`, ensuring atomic order generation in a single database round-trip.
3. If checkout fails due to insufficient stock, the exact trigger error message is caught and displayed cleanly to the customer.
4. The admin reports interface (`/admin/reports`) renders analytical views (`v_sales_by_category`, `v_low_stock`, `v_best_sellers`, `v_abandoned_carts`).
5. In the viva, say: "Our checkout button executes our stored procedure directly, keeping complex ACID transactional logic inside MySQL where it belongs."

---

---

## Phase 9 – Testing and Validation (Assignment Question 8)

### Member A – Users and Access
1. We verified that UNIQUE email constraints reject duplicate registrations with MySQL Error 1062.
2. We tested cascading deletion: deleting a parent user automatically purges dependent address rows without leaving orphan records.
3. We proved that the `shop_customer` role is strictly denied SELECT access on `users`, throwing Error 1142.
4. Parameterized query testing confirmed that malicious SQL injection inputs (e.g. `' OR '1'='1`) are escaped as inert strings.
5. In the viva, say: "Our testing matrix proves that user security holds at both the database role level and the web application input layer."

### Member B – Catalog and Inventory
1. We tested MySQL 8 engine CHECK constraints, proving that negative prices and negative stock are blocked with Error 3819.
2. Review rating values outside the 1 to 5 star range were verified to be rejected at the database schema level.
3. Our verified-purchase trigger test proved that customers cannot submit reviews for products they have not received.
4. Attempting to delete a product associated with historic order items was blocked by foreign key RESTRICT (Error 1451).
5. In the viva, say: "Engine-level CHECK constraints guarantee data integrity before application logic even touches the database."

### Member C – Orders and Payments
1. We simulated an overselling event (ordering 99 units with only 3 in stock) and verified an immediate transaction rollback.
2. The atomicity test proved zero phantom records were saved across `orders`, `order_items`, and `payments` during failed checkout.
3. Successful orders were verified to decrement stock by the exact ordered quantity using `trg_after_order_items_insert`.
4. Updating an order's status was verified to trigger an automated compliance record in `audit_log`.
5. In the viva, say: "We used automated test assertions to mathematically verify ACID rollback, inventory synchronization, and audit logging."

---

---

## Phase 10 – Report, Presentation, and Viva Defense

### Member A – Users and Access
1. In the viva, defend our 3NF normalization: `users` and `addresses` are segregated so users can store multiple delivery locations without duplicating account details.
2. Defend our password security: passwords are never stored in plaintext or basic MD5; we use industry-standard salted PBKDF2:SHA256 hashes.
3. Defend MySQL RBAC: three distinct engine roles prevent privilege escalation even if the web server credentials are leaked.
4. Defend our audit logging: database-level triggers guarantee that changes to financial records cannot be made silently without an audit log entry.
5. In the viva, say: "Our module enforces complete security and traceability across user identities, physical shipping destinations, and system access levels."

### Member B – Catalog and Inventory
1. In the viva, defend category hierarchy: self-referencing foreign keys allow infinite subcategory nesting in a single table with zero schema redundancy.
2. Defend catalog constraints: negative prices and negative stock quantities are physically blocked at the storage engine level via MySQL 8 CHECK constraints.
3. Defend verified reviews: `trg_before_reviews_insert` prevents review fraud by checking historic order records for confirmed delivery before accepting reviews.
4. Defend performance indexing: `idx_products_name` and `idx_products_category` eliminate full table scans, delivering sub-millisecond search performance.
5. In the viva, say: "Our catalog architecture guarantees product data integrity through engine constraints and provides executive business intelligence via specialized database views."

### Member C – Orders and Payments
1. In the viva, defend the unit_price decision: storing unit_price in `order_items` is intentional denormalization that locks historical prices against future catalog changes.
2. Defend ACID transactions: `sp_place_order` ensures that order generation, stock deduction, payment recording, and cart conversion either all commit together or all roll back.
3. Defend oversell prevention: the BEFORE INSERT trigger throws custom SQLSTATE 45000, triggering an automatic rollback before stock can become negative.
4. Defend cancellation logic: `sp_cancel_order` atomically restores inventory counts back to catalog products while transitioning orders to cancelled.
5. In the viva, say: "Our orders module maintains strict ACID transaction guarantees, preventing overselling, phantom inventory, and partial record corruption."

---

---

## Phase 11 – Real Product Catalog, Images, and Category Browsing

### Sub-Phase 11A – Database Schema Expansion & Constraints Defense

#### Member B – Catalog and Inventory (Primary Lead for 11A)
1. **Why normalize `brands` into its own table?**  
   *Viva Defense:* Placing brand names directly into `products` would introduce redundant text storage and update anomalies (e.g. changing "Dell" to "Dell Technologies" would require mass updates). The `brands` table (`brand_id`, `name`, `country`) enforces Third Normal Form (3NF). Products maintain a nullable foreign key `brand_id` (`ON DELETE SET NULL`) so deleting a brand retains the product record.
2. **Why normalize `product_images` into a 1-to-N relationship instead of an `image_url` column on `products`?**  
   *Viva Defense:* Real e-commerce listings require multiple gallery images (angles, colorways, packaging). Storing multiple image URLs in a single column violates First Normal Form (atomicity). The `product_images` table stores each image as an atomic record with `is_primary` flag, `sort_order`, and `ON DELETE CASCADE` so deleting a product automatically purges its gallery metadata without leaving orphan rows.
3. **How is the "Exactly One Primary Image" constraint enforced in MySQL?**  
   *Viva Defense:* We implemented dual database protections:
   * **Trigger (`trg_product_images_single_primary_bi` & `_bu`)**: Aborts concurrent attempts to mark multiple images as primary with custom error code `SQLSTATE 45000`.
   * **Stored Procedure (`sp_set_product_primary_image`)**: In MySQL, updating the same table inside a trigger causes Error 1442 (table re-entrancy). The stored procedure solves this cleanly by running an atomic transaction (`START TRANSACTION ... UPDATE product_images SET is_primary = 0 ... UPDATE ... SET is_primary = 1 ... COMMIT;`) to switch primary images safely.
4. **Why add composite index `idx_products_category_price`?**  
   *Viva Defense:* When users browse a category and sort by price (e.g. low-to-high or high-to-low), a composite index on `(category_id, price)` allows MySQL's InnoDB engine to filter and order records in a single B-tree index scan, eliminating temporary tables and expensive `filesort` operations.

#### Member A – Users and Access
1. **How did the category migration preserve existing data?**  
   *Viva Defense:* We applied an idempotent migration script `sql/08_catalog_expansion.sql` using `ALTER TABLE` procedures checking `information_schema.columns`. We re-organized the category hierarchy into 5 top-level departments while keeping foreign keys on existing products (`category_id` 2, 3, 5, 6, 8) completely intact. Zero customer carts, zero orders, and zero historic invoices were disrupted.

#### Member C – Orders and Payments
1. **How do the new analytical views benefit reporting?**  
   *Viva Defense:* `v_product_catalog` pre-joins products with brands, categories, review aggregates, and primary images so the web application executes simple `SELECT * FROM v_product_catalog WHERE ...` queries. `v_category_counts` calculates active product roll-ups across both parent categories and child subcategories using correlated subqueries, ensuring homepage category cards always display accurate real-time inventory counts.

---

---

### Sub-Phase 11B – Catalog Data Pipeline & Idempotent Loader Defense

#### Member B – Catalog and Inventory
1. **What is the purpose of data/products_manifest.csv?**  
   *Viva Defense:* The manifest serves as a declarative, version-controlled source of truth containing 51 verified Pakistani merchandise specimens with exact names, brands, categories, approximate PKR prices, inventory levels, and attribution source URLs.
2. **How does import_catalog.py achieve 100% idempotence?**  
   *Viva Defense:* The script uses INSERT ... ON DUPLICATE KEY UPDATE for brands and categories, matches products by unique 
ame to perform non-destructive updates, and transactional deletes/re-inserts for product_images. Running the pipeline repeatedly produces zero duplicate rows and zero orphan foreign keys.
3. **Why use a placeholder image fallback?**  
   *Viva Defense:* In production systems, missing assets degrade user trust and cause visual errors (404s). If an image file is absent from disk, the view and application automatically fall back to static/images/placeholder.svg, maintaining visual consistency without data failure.

---

### Sub-Phase 11C – Ethical Image Acquisition & Politeness Policy Defense

#### Member A – Users and Access
1. **How does Option B comply with web scraping ethics and store terms?**  
   *Viva Defense:* Our collector script etch_images.py operates under strict fair-use educational guidelines:
   * **Robots.txt Adherence**: Checks and respects 
obots.txt per domain using Python's RobotFileParser.
   * **Polite Throttling**: Enforces a mandatory delay of >= 3.0 seconds between network requests to the same host.
   * **Rate-Limit Cutoff**: Halts immediately if a domain returns HTTP 403 or 429 twice, logging remaining items as manual fallbacks.
   * **No Bypass**: Never bypasses logins, captchas, or Cloudflare bot shields.
2. **How are images optimized before storage?**  
   *Viva Defense:* Downloaded images are processed using Pillow (PIL), resized to a maximum width of 1000px preserving aspect ratio, and compressed to WebP/JPEG under 300 KB to optimize page load speed and minimize storage footprints.

---

### Sub-Phases 11D & 11E – Category Browsing & Gallery UI Defense

#### Member B – Catalog and Inventory
1. **How is Cumulative Layout Shift (CLS) prevented?**  
   *Viva Defense:* Product cards and gallery containers enforce CSS spect-ratio: 4 / 3 and spect-ratio: 1 / 1 with object-fit: cover/contain. The browser allocates image layout geometry before images finish downloading, completely eliminating layout shifting.
2. **How does category navigation work?**  
   *Viva Defense:* Top-level department pages (/category/<slug>) render sub-category chips for granular filtering. When clicked, queries dynamically filter by sub-category IDs while displaying available brand facets and price ranges without reloading entire layouts.

---

### Sub-Phase 11F – Admin Catalog & Media Management Defense

#### Member A – Users and Access
1. **How are uploaded files validated for security?**  
   *Viva Defense:* We enforce three-tier file security:
   * **MIME/Extension Verification**: Accepts only .jpg, .jpeg, .png, .webp. Executable files (.exe, .php, .py) are immediately rejected.
   * **Payload Size Restriction**: Files larger than 2 MB are rejected at the application gateway.
   * **Sanitization**: Filenames are sanitized via secure_filename() with timestamp prefixes to prevent directory traversal attacks (../../).

---

### Sub-Phase 11G – Automated Testing & Verification Defense

#### Member C – Orders and Payments
1. **What does the expanded automated test suite verify?**  
   *Viva Defense:*
   * **15 Database Test Assertions (sql/07_tests.sql)**: Mathematically validates single primary image triggers, gallery cascade deletions, category count roll-up consistency, brand FK constraints, and historic order preservation.
   * **25 Web Route Assertions (	est_app.py)**: Tests full end-to-end customer workflows, category filters, sorting, responsive views, and admin upload security with 100% pass rates.


---

---

## Phase 12 – SRS Alignment

### Sub-Phase 12A – Requirements Traceability Defense

#### Member A – Users and Access
1. **What is the purpose of the Requirements Traceability Matrix (`docs/traceability.csv`)?**  
   *Viva Defense:* "The traceability matrix provides bi-directional verification between formal software engineering specifications and our actual database/software implementation. It maps all 63 requirements (21 Functional Requirements, 25 Acceptance Criteria, 7 Non-Functional Requirements, 6 Accessibility Requirements, 3 Usability Requirements, and 1 Operational Indicator) directly to their implementing MySQL tables/procedures, Flask route endpoints, Jinja templates, and test cases."
2. **How does traceability protect user authentication and role-based access?**  
   *Viva Defense:* "Requirements FR-02, FR-16, and AC-06.5 trace directly to our decoupled user management and guest session token architecture. We verify that sensitive customer credentials remain protected with salted cryptographic hashes and that guest checkout can proceed smoothly without compromising system auditability."

#### Member B – Catalog and Inventory
1. **How does the traceability matrix govern multi-vendor catalog integrity?**  
   *Viva Defense:* "Requirements FR-17, FR-18, AC-06.1, and AC-06.2 map the expansion of suppliers into verified sellers. The matrix guarantees that views such as `v_product_catalog` enforce seller verification filters so that merchandise from unverified or rejected vendors is systematically excluded from the public catalog."
2. **How does the matrix ensure accessibility compliance for catalog items?**  
   *Viva Defense:* "Requirements FR-15 and AR-06 link the `product_images.alt_text` column directly to template rendering and accessibility assertions in `test_app.py`, ensuring all product imagery conforms to WCAG 2.1 Level AA screen reader standards."

#### Member C – Orders and Payments
1. **How does the traceability matrix eliminate financial divergence between cart and checkout?**  
   *Viva Defense:* "Requirements FR-01, FR-08, FR-09, and NFR-06 mandate a single source of truth for all calculations. The matrix maps both `/cart` and `/checkout` to stored procedure `sp_cart_summary` and tables `delivery_rates` and `tax_rates`, preventing any discrepancy between the displayed cart total and the final charged order total."
2. **How does traceability guarantee transactional recovery upon checkout failure?**  
   *Viva Defense:* "Requirements FR-04, FR-10, and FR-11 link our payment attempt logger (`payment_attempts`) and atomic order placement procedure (`sp_place_order`) to specific automated rollback tests. The matrix proves that carts remain active if a payment fails or cancels, allowing instant customer retry without data loss."


---

### Sub-Phase 12B – Database Schema Alignment Defense

#### Member A – Users and Access
1. **How did we enable guest checkout without breaking referential integrity?**  
   *Viva Defense:* "We altered `orders.user_id` and `orders.address_id` to be `NULLABLE` while creating dedicated guest capture columns (`guest_name`, `guest_email`, `guest_phone`, `guest_address_line1`, etc.). This satisfies FR-02 and AC-03.1. When an authenticated user checks out, `user_id` is linked via foreign key; when a guest checks out, `user_id` is NULL and customer contact information is stored directly on the order record alongside an immutable address snapshot."
2. **What permissions does the new `shop_seller` MySQL role have?**  
   *Viva Defense:* "In accordance with the principle of least privilege (POLP), the `shop_seller` role can SELECT categories, brands, delivery rates, and active catalog views. It has INSERT and UPDATE privileges on `products` and `product_images`, and SELECT/UPDATE privileges on `return_requests`. It has NO DELETE permissions on users, orders, or carts."

#### Member B – Catalog and Inventory
1. **How does the schema support multi-vendor seller governance?**  
   *Viva Defense:* "We extended `suppliers` into audited `sellers` with `business_name`, `contact_name`, `store_location`, and `verification_status` ENUM ('pending', 'verified', 'rejected'). View `v_product_catalog` was updated to include an inner join filter `WHERE verification_status = 'verified'`, mathematically ensuring that items from unverified or rejected vendors are never displayed to shoppers (AC-06.2)."
2. **How does the schema handle accessibility attributes on images?**  
   *Viva Defense:* "We added an `alt_text VARCHAR(255)` column to `product_images`. View `v_product_catalog` projects `primary_image_alt`, which defaults to the product name and photo description, ensuring screen readers receive descriptive accessibility text (FR-15, AR-06)."

#### Member C – Orders and Payments
1. **Why is `sp_cart_summary` critical to preventing price divergence?**  
   *Viva Defense:* "`sp_cart_summary` computes subtotal, provincial tax (from `tax_rates`), and delivery fee / estimated days (from `delivery_rates`) in a single stored procedure. Both `/cart` and `sp_place_order` invoke this exact same procedure. This eliminates duplicate calculation logic between frontend and backend and guarantees that the total displayed to the customer in the cart is identical to the amount charged on the invoice (FR-01, NFR-06, AC-01.2)."
2. **How does `sp_merge_carts` handle anonymous to authenticated transitions?**  
   *Viva Defense:* "When a guest browsing with a session cookie logs into their account, `sp_merge_carts` looks up both the guest cart and the customer's active account cart. It merges item quantities using `ON DUPLICATE KEY UPDATE quantity = cart_items.quantity + VALUES(quantity)` inside a single atomic operation, then cleans up the guest cart so the shopper never loses selected merchandise (FR-03, AC-08.2)."
3. **How are status changes on orders and returns audited?**  
   *Viva Defense:* "We implemented triggers `trg_order_status_history` and `trg_return_status_history`. Any time the status column on `orders` or `return_requests` changes, the engine synchronously records the previous status, new status, actor, and timestamp into dedicated audit tables, creating an immutable history for self-service package tracking (FR-12, FR-21)."
