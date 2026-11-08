-- ============================================================================
-- Script: 03_views_indexes.sql
-- Description: Analytical Views & Performance Indexes for Online Shopping System
-- Database Engine: MySQL 8.0 (InnoDB)
--
-- Re-runnable: Can be executed multiple times safely.
-- Module Ownership:
--   Member A: v_order_summary, idx_orders_user_date
--   Member B: v_low_stock, v_best_sellers, idx_products_name, idx_products_category
--   Member C: v_sales_by_category, v_abandoned_carts, idx_order_items_product
-- ============================================================================

USE online_shop_perfume_dev;

-- ============================================================================
-- SECTION 1: PERFORMANCE INDEXES
-- ============================================================================

-- Helper procedure to safely drop indexes if they already exist
DROP PROCEDURE IF EXISTS _drop_index_if_exists;
DELIMITER $$
CREATE PROCEDURE _drop_index_if_exists(IN in_table VARCHAR(64), IN in_idx VARCHAR(64))
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.statistics 
        WHERE table_schema = DATABASE() 
          AND table_name = in_table 
          AND index_name = in_idx
    ) THEN
        SET @sql = CONCAT('ALTER TABLE ', in_table, ' DROP INDEX ', in_idx);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$
DELIMITER ;

-- Index 1: idx_products_name on products(name)
-- WHY: Speeds up customer search queries by product name (e.g., WHERE name LIKE 'Samsung%')
--      avoiding full-table scans across the catalog.
CALL _drop_index_if_exists('products', 'idx_products_name');
CREATE INDEX idx_products_name ON products(name);

-- Index 2: idx_products_category on products(category_id)
-- WHY: Accelerates catalog filtering when shoppers browse products by category.
CALL _drop_index_if_exists('products', 'idx_products_category');
CREATE INDEX idx_products_category ON products(category_id);

-- Index 3: idx_orders_user_date on orders(user_id, order_date DESC)
-- WHY: Composite index enabling instant lookup of a specific customer's order
--      history pre-sorted chronologically without requiring an expensive filesort.
CALL _drop_index_if_exists('orders', 'idx_orders_user_date');
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date DESC);

-- Index 4: idx_order_items_product on order_items(product_id)
-- WHY: Speeds up multi-table joins between products and order line items,
--      dramatically accelerating best-seller and category sales reporting.
CALL _drop_index_if_exists('order_items', 'idx_order_items_product');
CREATE INDEX idx_order_items_product ON order_items(product_id);

-- Clean up helper procedure
DROP PROCEDURE IF EXISTS _drop_index_if_exists;


-- ============================================================================
-- SECTION 2: BUSINESS VIEWS
-- ============================================================================

-- View 1: v_order_summary
-- WHY: Flattens the normalization across orders, users, payments, and shipments
--      into a single reusable view for administrative dashboards, invoice rendering,
--      and customer order tracking.
CREATE OR REPLACE VIEW v_order_summary AS
SELECT 
    o.order_id,
    o.order_date,
    u.user_id,
    u.full_name AS customer_name,
    u.email AS customer_email,
    u.phone AS customer_phone,
    o.total_amount,
    o.status AS order_status,
    p.method AS payment_method,
    p.status AS payment_status,
    p.paid_at,
    s.courier,
    s.tracking_number,
    s.shipped_at,
    s.delivered_at
FROM orders o
JOIN users u ON o.user_id = u.user_id
LEFT JOIN payments p ON o.order_id = p.order_id
LEFT JOIN shipments s ON o.order_id = s.order_id;


-- View 2: v_low_stock
-- WHY: Provides real-time automated alerts for inventory managers showing products
--      with stock at or below critical threshold (<= 5 units), complete with
--      supplier contact numbers for immediate purchase order placement.
CREATE OR REPLACE VIEW v_low_stock AS
SELECT 
    p.product_id,
    p.name AS product_name,
    c.name AS category_name,
    p.stock_quantity,
    p.price,
    s.supplier_id,
    s.name AS supplier_name,
    s.phone AS supplier_phone,
    s.email AS supplier_email
FROM products p
JOIN categories c ON p.category_id = c.category_id
JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE p.stock_quantity <= 5
  AND p.is_active = 1;


-- View 3: v_sales_by_category
-- WHY: Executive business intelligence view that calculates gross sales revenue,
--      distinct orders, and total item units sold per merchandise category,
--      filtering out cancelled or abandoned orders.
CREATE OR REPLACE VIEW v_sales_by_category AS
SELECT 
    c.category_id,
    c.name AS category_name,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COALESCE(SUM(oi.quantity), 0) AS total_units_sold,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0.00) AS total_revenue_pkr
FROM categories c
LEFT JOIN products p ON c.category_id = p.category_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.status IN ('paid', 'shipped', 'delivered')
GROUP BY c.category_id, c.name
ORDER BY total_revenue_pkr DESC;


-- View 4: v_best_sellers
-- WHY: Ranks products by actual sales volume (units sold) and revenue generated,
--      used by the web storefront to display "Top Trending" items and by managers
--      to forecast reorder quantities.
CREATE OR REPLACE VIEW v_best_sellers AS
SELECT 
    p.product_id,
    p.name AS product_name,
    c.name AS category_name,
    COALESCE(SUM(oi.quantity), 0) AS total_units_sold,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0.00) AS total_revenue_pkr,
    p.stock_quantity AS current_stock
FROM products p
JOIN categories c ON p.category_id = c.category_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status IN ('paid', 'shipped', 'delivered')
GROUP BY p.product_id, p.name, c.name, p.stock_quantity
ORDER BY total_units_sold DESC, total_revenue_pkr DESC;


-- View 5: v_abandoned_carts
-- WHY: Detects potential lost sales by identifying active shopping carts that have
--      sat untouched for 7 or more days, including customer contact details for
--      automated email marketing recovery reminders.
CREATE OR REPLACE VIEW v_abandoned_carts AS
SELECT 
    c.cart_id,
    u.user_id,
    u.full_name AS customer_name,
    u.email AS customer_email,
    u.phone AS customer_phone,
    c.updated_at AS last_activity,
    DATEDIFF(NOW(), c.updated_at) AS days_idle,
    COUNT(ci.product_id) AS item_count,
    COALESCE(SUM(ci.quantity * p.price), 0.00) AS estimated_cart_value
FROM carts c
JOIN users u ON c.user_id = u.user_id
LEFT JOIN cart_items ci ON c.cart_id = ci.cart_id
LEFT JOIN products p ON ci.product_id = p.product_id
WHERE (c.status = 'abandoned' OR (c.status = 'active' AND c.updated_at <= DATE_SUB(NOW(), INTERVAL 7 DAY)))
GROUP BY c.cart_id, u.user_id, u.full_name, u.email, u.phone, c.updated_at
ORDER BY days_idle DESC;

