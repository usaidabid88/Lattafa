-- ============================================================================
-- Script: 06_demo_queries.sql
-- Description: Comprehensive Demonstration Queries for Viva & Project Report (Q6)
-- Covers: INSERT, UPDATE, DELETE, SEARCH, 3+ TABLE JOINS, GROUP BY/HAVING, SUBQUERIES, VIEWS
-- Database Engine: MySQL 8.0
--
-- Re-runnable: Safely re-executable; all operations use transaction rollbacks
-- or cleanups where necessary to preserve baseline sample data.
-- ============================================================================

USE online_shop;

-- ============================================================================
-- 1. INSERT OPERATIONS (ADDING DATA)
-- ============================================================================

-- Q1.1: Register a new customer account with hashed password
-- Shows: Inserting into users table with role customer and phone number
INSERT INTO users (full_name, email, password_hash, phone, role)
VALUES (
    'Naveed Jamali',
    'naveed.jamali@gmail.com',
    'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03',
    '03009988776',
    'customer'
)
ON DUPLICATE KEY UPDATE phone = VALUES(phone);

-- Q1.2: Add a new delivery address for the newly registered customer
-- Shows: 1-to-many relationship insertion referencing users(user_id)
INSERT INTO addresses (user_id, line1, city, province, postal_code, is_default)
SELECT user_id, 'Plot 42, Sector D, MUET Housing Society', 'Jamshoro', 'Sindh', '76062', 1
FROM users
WHERE email = 'naveed.jamali@gmail.com'
LIMIT 1;

-- Q1.3: Add a new product to the catalog from an existing supplier
-- Shows: Catalog expansion with foreign keys referencing categories and suppliers
INSERT INTO products (category_id, supplier_id, name, description, price, stock_quantity, is_active)
VALUES (
    3, -- Mobile Phones
    1, -- TechZone Karachi
    'Anker USB-C 65W Fast Charger',
    'GaN technology dual-port wall charger for laptops and phones',
    8500.00,
    30,
    1
);


-- ============================================================================
-- 2. UPDATE OPERATIONS (MODIFYING DATA)
-- ============================================================================

-- Q2.1: Restock a low-inventory product and update its retail price
-- Shows: Modifying stock and price with engine CHECK constraints active
UPDATE products
SET stock_quantity = stock_quantity + 20,
    price = 5200.00
WHERE name = 'Al-Karam Men Formal Trousers';

-- Q2.2: Advance order status from paid to shipped
-- Shows: Order status update which automatically triggers trg_after_orders_update_audit
UPDATE orders
SET status = 'shipped'
WHERE order_id = 20 AND status = 'paid';

-- Q2.3: Change a customer's default delivery address
-- Shows: Updating boolean flag across addresses for a single user
UPDATE addresses
SET is_default = 0
WHERE user_id = 5;

UPDATE addresses
SET is_default = 1
WHERE user_id = 5 AND address_id = 2;


-- ============================================================================
-- 3. DELETE OPERATIONS (REMOVING DATA)
-- ============================================================================

-- Q3.1: Remove an item from an active shopping cart
-- Shows: Safe deletion from a junction table (cart_items) without affecting products
DELETE FROM cart_items
WHERE cart_id = 1 AND product_id = 25;

-- Q3.2: Safely remove a discontinued test product (only if never ordered)
-- Shows: Referential integrity protection—RESTRICT prevents deleting ordered products
DELETE FROM products
WHERE name = 'Anker USB-C 65W Fast Charger'
  AND product_id NOT IN (SELECT DISTINCT product_id FROM order_items);


-- ============================================================================
-- 4. SEARCH & FILTERING OPERATIONS
-- ============================================================================

-- Q4.1: Keyword product search across name and description
-- Shows: Wildcard search accelerated by the idx_products_name index
SELECT product_id, name, price, stock_quantity
FROM products
WHERE (name LIKE '%Galaxy%' OR description LIKE '%Fast Charge%')
  AND is_active = 1;

-- Q4.2: Filter products by price range and minimum stock in a category
-- Shows: Multi-criteria catalog filtering for customer storefront browsing
SELECT p.product_id, p.name, c.name AS category, p.price, p.stock_quantity
FROM products p
JOIN categories c ON p.category_id = c.category_id
WHERE p.price BETWEEN 5000.00 AND 30000.00
  AND p.stock_quantity > 0
ORDER BY p.price ASC;


-- ============================================================================
-- 5. COMPLEX RELATIONAL JOINS (3 OR MORE TABLES)
-- ============================================================================

-- Q5.1: Complete customer invoice breakdown joining 5 core operational tables
-- Shows: orders + users + addresses + order_items + products + shipments + payments
SELECT 
    o.order_id,
    o.order_date,
    u.full_name AS customer_name,
    CONCAT(a.line1, ', ', a.city, ', ', a.province) AS delivery_address,
    p.name AS item_purchased,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS line_subtotal,
    o.total_amount AS invoice_total,
    pay.method AS payment_method,
    pay.status AS payment_status,
    COALESCE(s.courier, 'Not yet dispatched') AS courier_service,
    COALESCE(s.tracking_number, 'Pending') AS tracking_code
FROM orders o
JOIN users u ON o.user_id = u.user_id
JOIN addresses a ON o.address_id = a.address_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN payments pay ON o.order_id = pay.order_id
LEFT JOIN shipments s ON o.order_id = s.order_id
WHERE o.order_id = 1;

-- Q5.2: Product catalog listing with supplier contact and category hierarchy
-- Shows: Self-referencing join on categories + join with products and suppliers
SELECT 
    p.product_id,
    p.name AS product_name,
    COALESCE(parent.name, 'Top Level') AS parent_category,
    child.name AS sub_category,
    s.name AS supplier_name,
    s.phone AS supplier_contact,
    p.price,
    p.stock_quantity
FROM products p
JOIN categories child ON p.category_id = child.category_id
LEFT JOIN categories parent ON child.parent_category_id = parent.category_id
JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE p.is_active = 1
ORDER BY parent_category, sub_category, p.name
LIMIT 8;


-- ============================================================================
-- 6. AGGREGATIONS WITH GROUP BY AND HAVING
-- ============================================================================

-- Q6.1: High-value customer ranking (VIP shoppers with total spend > PKR 30,000)
-- Shows: GROUP BY with aggregate SUM, COUNT, and filtering via HAVING clause
SELECT 
    u.user_id,
    u.full_name AS customer_name,
    u.email,
    COUNT(o.order_id) AS total_orders_placed,
    SUM(o.total_amount) AS total_spent_pkr,
    ROUND(AVG(o.total_amount), 2) AS average_order_value_pkr
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.status IN ('paid', 'shipped', 'delivered')
GROUP BY u.user_id, u.full_name, u.email
HAVING total_spent_pkr > 30000.00
ORDER BY total_spent_pkr DESC;

-- Q6.2: Geographical sales performance per city
-- Shows: Aggregating order volume and total revenue by destination city
SELECT 
    a.city,
    a.province,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.total_amount) AS gross_sales_pkr
FROM addresses a
JOIN orders o ON a.address_id = o.address_id
WHERE o.status <> 'cancelled'
GROUP BY a.city, a.province
HAVING gross_sales_pkr > 0
ORDER BY gross_sales_pkr DESC;

-- Q6.3: Supplier catalog distribution and inventory value
-- Shows: Supplier analysis showing inventory units and total capital tied in stock
SELECT 
    s.supplier_id,
    s.name AS supplier_name,
    COUNT(p.product_id) AS catalog_product_count,
    SUM(p.stock_quantity) AS total_units_in_stock,
    SUM(p.stock_quantity * p.price) AS total_inventory_value_pkr
FROM suppliers s
JOIN products p ON s.supplier_id = p.supplier_id
GROUP BY s.supplier_id, s.name
HAVING total_units_in_stock > 10
ORDER BY total_inventory_value_pkr DESC;


-- ============================================================================
-- 7. SUBQUERIES (CORRELATED & NESTED)
-- ============================================================================

-- Q7.1: Correlated Subquery: Products priced above their category's average price
-- Shows: Correlated subquery executing per product row against its specific category
SELECT 
    p1.product_id,
    p1.name AS product_name,
    c.name AS category_name,
    p1.price AS product_price,
    ROUND((SELECT AVG(p2.price) FROM products p2 WHERE p2.category_id = p1.category_id), 2) AS category_avg_price
FROM products p1
JOIN categories c ON p1.category_id = c.category_id
WHERE p1.price > (
    SELECT AVG(p2.price) 
    FROM products p2 
    WHERE p2.category_id = p1.category_id
)
ORDER BY p1.category_id, p1.price DESC;

-- Q7.2: Nested Subquery with NOT IN: Active customers who have never placed an order
-- Shows: Finding unengaged customer accounts for marketing re-engagement
SELECT 
    u.user_id,
    u.full_name,
    u.email,
    u.phone,
    u.created_at
FROM users u
WHERE u.role = 'customer'
  AND u.user_id NOT IN (
      SELECT DISTINCT user_id 
      FROM orders
  );

-- Q7.3: Scalar Subquery with ALL / MAX: The single most expensive item in each department
-- Shows: Finding highest-priced product per top-level department
SELECT p.product_id, p.name, c.name AS category, p.price
FROM products p
JOIN categories c ON p.category_id = c.category_id
WHERE p.price = (
    SELECT MAX(p_sub.price)
    FROM products p_sub
    WHERE p_sub.category_id = p.category_id
);


-- ============================================================================
-- 8. BUSINESS VIEW DEMONSTRATIONS
-- ============================================================================

-- Q8.1: Executive Sales Summary by Department
-- Shows: Real-time query against the v_sales_by_category view
SELECT category_name, total_orders, total_units_sold, total_revenue_pkr
FROM v_sales_by_category;

-- Q8.2: Critical Low Stock Alerts for Warehouse Replenishment
-- Shows: Real-time query against the v_low_stock view
SELECT product_id, product_name, category_name, stock_quantity, supplier_name, supplier_phone
FROM v_low_stock;

-- Q8.3: Top 3 Trending Best-Seller Products
-- Shows: Real-time query against the v_best_sellers view
SELECT product_name, category_name, total_units_sold, total_revenue_pkr, current_stock
FROM v_best_sellers
LIMIT 3;

-- Q8.4: Abandoned Cart Follow-Up List
-- Shows: Real-time query against the v_abandoned_carts view
SELECT cart_id, customer_name, customer_email, days_idle, estimated_cart_value
FROM v_abandoned_carts;
