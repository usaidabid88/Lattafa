# 10-Minute Presentation & Live Demo Guide
**MUET DBMS Complex Engineering Problem (CEP) - Online Shopping System**
**Instructor:** Aisha Ashfaque | **Total Marks:** 10

---

## ⏱️ Presentation Timing Breakdown (10 Minutes Total)

| Minute | Stage | Activity | Presenter |
|---|---|---|---|
| **00:00 - 02:00** | Introduction & ER Diagram | Problem statement, 13 entities, 3NF design, and relationship walkthrough | Member A |
| **02:00 - 04:00** | Database Architecture | Engine constraints, catalog taxonomy, views, and index EXPLAIN proof | Member B |
| **04:00 - 06:00** | Live Web App Demo | Customer browsing, cart manipulation, and live atomic checkout | Member C |
| **06:00 - 08:00** | ACID Rollback & Triggers | Live overselling failure demonstration, automatic audit log capture | Member C & B |
| **08:00 - 10:00** | Security & RBAC | MySQL 8 role denial demo, viva questions defense | Member A |

---

## 🎯 Step-by-Step Live Demo Script

### Part 1: Schema & ER Diagram (Minutes 0 - 2)
1. **Open the ER Diagram:**
   - Display `docs/er_diagram.png`.
   - Point out the 3 functional modules:
     - *Users & Access* (`users`, `addresses`, `audit_log`)
     - *Catalog & Inventory* (`categories`, `suppliers`, `products`, `reviews`)
     - *Orders & Payments* (`carts`, `cart_items`, `orders`, `order_items`, `payments`, `shipments`)
   - **Key Viva Point to Highlight:** Explain why `order_items` stores `unit_price` at checkout time:
     > *"We intentionally store unit_price on order_items so that future product price adjustments never mutate past historical accounting records or customer invoices."*

---

### Part 2: Starting the System (Minute 2 - 3)
1. **Open PowerShell in the project directory:**
   ```powershell
   cd "d:\university\semister 3\DBS\DBS project"
   .\venv\Scripts\activate
   ```
2. **Start the Flask Web App:**
   ```powershell
   python app/app.py
   ```
3. Open browser at: `http://127.0.0.1:5000`

---

### Part 3: Live Customer Journey (Minutes 3 - 5)
1. **Show Storefront:**
   - Navigate to `/products`.
   - Search for `Samsung` in the search bar. Show that `idx_products_name` immediately returns the product.
   - Filter by Category: Select `Kitchen Appliances` from the dropdown.
2. **Login as Customer:**
   - Click **Login** in navbar.
   - Credentials: `zeeshan@gmail.com` / `password123`.
3. **Cart & Atomic Checkout:**
   - View *J. Classic Cotton Kurta White* (PKR 6,490.00).
   - Add 2 units to cart.
   - Go to `/cart`, click **Proceed to Checkout**.
   - Select delivery address: `House 45-B, Block 6, PECHS, Karachi`.
   - Select Payment Method: `Cash on Delivery (COD)`.
   - Click **Place Order**.
   - **Explain to Instructor:**
     > *"This single button click invoked our stored procedure `sp_place_order`, executing inside an isolated transaction. The cart was converted, order items were created, payment was logged, and product inventory was decremented automatically via our AFTER INSERT trigger."*

---

### Part 4: Proving ACID Rollback & Concurrency Control (Minutes 5 - 7)
Open a new terminal window to demonstrate database-level engine defense:
1. **Connect to MySQL:**
   ```powershell
   mysql -u root -p online_shop
   # When prompted, enter your database root password interactively
   ```
2. **Attempt Overselling Checkout:**
   ```sql
   -- Check current stock of Product 15 (Al-Karam Formal Trousers - stock is 2 units)
   SELECT product_id, name, stock_quantity FROM products WHERE product_id = 15;

   -- Create a cart with 50 units
   INSERT INTO carts (cart_id, user_id, status) VALUES (777, 5, 'active');
   INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (777, 15, 50);

   -- Attempt checkout
   CALL sp_place_order(5, 1, 'cod', @oid, @msg);
   SELECT @oid AS created_order, @msg AS engine_response;

   -- Prove stock was NOT decremented
   SELECT product_id, name, stock_quantity FROM products WHERE product_id = 15;

   -- Clean up
   DELETE FROM cart_items WHERE cart_id = 777;
   DELETE FROM carts WHERE cart_id = 777;
   ```
   - **Show Output:** `FAILED: Oversell Error: Requested quantity exceeds available inventory stock.`
   - **Point Out:** Stock remained at 2, and zero phantom orders were written.

---

### Part 5: Proving MySQL 8 Role Privileges (Minutes 7 - 9)
Demonstrate that security is enforced at the database engine, not just the web app:
1. **Login as Customer via MySQL CLI:**
   ```powershell
   mysql -u test_customer -p online_shop
   # When prompted, enter password interactively (CustomerPass123!)
   ```
2. **Run Allowed Statement:**
   ```sql
   SELECT product_id, name, price FROM products LIMIT 2;
   -- SUCCESS
   ```
3. **Run Denied Statement (Attempt to steal passwords):**
   ```sql
   SELECT * FROM users;
   -- ERROR 1142 (42000): SELECT command denied to user 'test_customer'@'localhost' for table 'users'
   ```
4. **Run Denied Statement (Attempt to delete catalog item):**
   ```sql
   DELETE FROM products WHERE product_id = 1;
   -- ERROR 1142 (42000): DELETE command denied to user 'test_customer'@'localhost' for table 'products'
   ```

---

### Part 6: Admin Dashboard & Analytical Views (Minute 9 - 10)
1. In the browser, log out and log in as Administrator:
   - Credentials: `admin@muetshop.pk` / `password123`.
2. Navigate to `/admin`:
   - Show live metrics: Total Sales, Pending Orders, Low Stock Alerts, Customers.
3. Click **View Reports** (`/admin/reports`):
   - Highlight Section 1: Departmental Sales from `v_sales_by_category`.
   - Highlight Section 2: Low Stock Alerts from `v_low_stock` with supplier phone numbers.
   - Highlight Section 3: Trending Best Sellers from `v_best_sellers`.
   - Highlight Section 4: Dormant baskets from `v_abandoned_carts`.

---

## 💡 Quick Viva Defense Tips for Each Member

### Member A (Users, Access, Audit, Roles):
- **Question:** *"Why did you use MySQL roles instead of just checking role in Python?"*
  - **Answer:** *"Defense in depth. If our Python application had a vulnerability or an attacker obtained direct database access, MySQL roles guarantee that customer accounts still cannot read credential tables or alter schema definitions."*

### Member B (Catalog, Inventory, Triggers, Views):
- **Question:** *"Why did you use an engine trigger for inventory rather than updating stock in Python?"*
  - **Answer:** *"Triggers operate at the database storage engine level inside the transaction boundary. Whether an order is placed from the Flask app, an external mobile app, or a direct SQL console, inventory is guaranteed to stay synchronized without relying on developers writing manual updates."*

### Member C (Orders, Payments, Procedures, Transactions):
- **Question:** *"What happens if the server crashes right after inserting into orders but before payments?"*
  - **Answer:** *"Because sp_place_order runs inside START TRANSACTION with an exception handler, InnoDB ensures atomicity. If a crash or failure occurs before COMMIT, InnoDB's undo logs roll back the entire transaction upon recovery, leaving zero partial records."*
