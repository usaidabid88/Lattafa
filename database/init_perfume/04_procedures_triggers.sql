-- ============================================================================
-- Script: 04_procedures_triggers.sql
-- Description: Stored Procedures, Business Triggers, and ACID Transactions
-- Database Engine: MySQL 8.0 (InnoDB)
--
-- Re-runnable: Can be executed multiple times safely.
-- Module Ownership:
--   Member A: trg_after_orders_update_audit (audit_log automation)
--   Member B: trg_before_order_items_insert, trg_after_order_items_insert, trg_before_reviews_insert
--   Member C: sp_place_order, sp_cancel_order, sp_mark_abandoned_carts
-- ============================================================================

USE online_shop_perfume_dev;

-- Drop existing triggers before re-creating
DROP TRIGGER IF EXISTS trg_before_order_items_insert;
DROP TRIGGER IF EXISTS trg_after_order_items_insert;
DROP TRIGGER IF EXISTS trg_after_orders_update_audit;
DROP TRIGGER IF EXISTS trg_before_reviews_insert;

-- Drop existing procedures before re-creating
DROP PROCEDURE IF EXISTS sp_place_order;
DROP PROCEDURE IF EXISTS sp_cancel_order;
DROP PROCEDURE IF EXISTS sp_mark_abandoned_carts;


-- ============================================================================
-- SECTION 1: BUSINESS TRIGGERS
-- ============================================================================

-- Trigger 1: trg_before_order_items_insert (BEFORE INSERT on order_items)
-- WHY: Enforces inventory availability rule directly at the storage engine level.
--      If requested quantity exceeds real-time in-stock quantity, the trigger throws
--      a 45000 custom error, aborting the statement and preventing overselling.
DELIMITER $$
CREATE TRIGGER trg_before_order_items_insert
BEFORE INSERT ON order_items
FOR EACH ROW
BEGIN
    DECLARE v_available_stock INT;
    DECLARE v_product_name VARCHAR(150);

    SELECT stock_quantity, name 
    INTO v_available_stock, v_product_name
    FROM products
    WHERE product_id = NEW.product_id;

    IF v_available_stock < NEW.quantity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Oversell Error: Requested quantity exceeds available inventory stock.';
    END IF;
END$$
DELIMITER ;


-- Trigger 2: trg_after_order_items_insert (AFTER INSERT on order_items)
-- WHY: Automatically decreases inventory count as soon as an item is reserved in an order.
--      Guarantees atomic synchronization between order line items and product stock.
DELIMITER $$
CREATE TRIGGER trg_after_order_items_insert
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    UPDATE products
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE product_id = NEW.product_id;
END$$
DELIMITER ;


-- Trigger 3: trg_after_orders_update_audit (AFTER UPDATE on orders)
-- WHY: Automatically captures an immutable audit record in audit_log whenever an
--      order's lifecycle status transitions (e.g. pending -> paid -> shipped),
--      ensuring zero reliance on developers manually writing log statements.
DELIMITER $$
CREATE TRIGGER trg_after_orders_update_audit
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
    IF OLD.status <> NEW.status THEN
        INSERT INTO audit_log (table_name, action, record_id, details, changed_at)
        VALUES (
            'orders',
            'STATUS_CHANGE',
            NEW.order_id,
            CONCAT('Order #', NEW.order_id, ' status changed from ''', OLD.status, ''' to ''', NEW.status, '''. Total: PKR ', NEW.total_amount),
            NOW()
        );
    END IF;
END$$
DELIMITER ;


-- Trigger 4: trg_before_reviews_insert (BEFORE INSERT on reviews)
-- WHY: Enforces verified purchase rule (FR-10). A customer is only permitted to leave
--      a review if they have completed an order for that exact product that has
--      already been delivered, preventing spam, fake reviews, or competitor attacks.
DELIMITER $$
CREATE TRIGGER trg_before_reviews_insert
BEFORE INSERT ON reviews
FOR EACH ROW
BEGIN
    DECLARE v_delivered_count INT DEFAULT 0;

    SELECT COUNT(*) INTO v_delivered_count
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.user_id = NEW.user_id
      AND oi.product_id = NEW.product_id
      AND o.status = 'delivered';

    IF v_delivered_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Review Error: Customer has not purchased and received this product.';
    END IF;
END$$
DELIMITER ;


-- ============================================================================
-- SECTION 2: STORED PROCEDURES & TRANSACTIONS
-- ============================================================================

-- Procedure 1: sp_place_order
-- WHY: Implements an atomic checkout transaction. Checks out the active cart,
--      validates address ownership, copies cart items to order items (which triggers
--      stock validation and inventory reduction), creates the payment entry, and
--      marks the cart converted. If ANY step fails (e.g. insufficient stock or
--      invalid data), everything is rolled back completely with zero orphaned records.
DELIMITER $$
CREATE PROCEDURE sp_place_order(
    IN p_user_id INT,
    IN p_address_id INT,
    IN p_payment_method VARCHAR(20),
    OUT p_order_id INT,
    OUT p_status_message VARCHAR(255)
)
proc_body: BEGIN
    DECLARE v_cart_id INT DEFAULT NULL;
    DECLARE v_item_count INT DEFAULT 0;
    DECLARE v_order_total DECIMAL(10,2) DEFAULT 0.00;
    DECLARE v_new_order_id INT DEFAULT NULL;
    DECLARE v_err_msg VARCHAR(255) DEFAULT '';

    -- Exception handler: GET DIAGNOSTICS MUST be called BEFORE ROLLBACK
    -- because executing statements (including ROLLBACK) resets the diagnostic area!
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 v_err_msg = MESSAGE_TEXT;
        ROLLBACK;
        DROP TEMPORARY TABLE IF EXISTS _temp_checkout_items;
        SET p_order_id = NULL;
        SET p_status_message = CONCAT('FAILED: ', COALESCE(v_err_msg, 'Transaction aborted due to error'));
    END;

    -- Pre-validation 1: Validate payment method
    IF p_payment_method NOT IN ('cod', 'card', 'bank_transfer', 'wallet') THEN
        SET p_order_id = NULL;
        SET p_status_message = 'FAILED: Invalid payment method.';
        LEAVE proc_body;
    END IF;

    -- Pre-validation 2: Validate delivery address ownership
    IF NOT EXISTS (SELECT 1 FROM addresses WHERE address_id = p_address_id AND user_id = p_user_id) THEN
        SET p_order_id = NULL;
        SET p_status_message = 'FAILED: Delivery address does not belong to this user.';
        LEAVE proc_body;
    END IF;

    -- Pre-validation 3: Find user's active shopping cart
    SELECT cart_id INTO v_cart_id
    FROM carts
    WHERE user_id = p_user_id AND status = 'active'
    ORDER BY updated_at DESC
    LIMIT 1;

    IF v_cart_id IS NULL THEN
        SET p_order_id = NULL;
        SET p_status_message = 'FAILED: No active shopping cart found for user.';
        LEAVE proc_body;
    END IF;

    -- Pre-validation 4: Verify cart has items and compute order total
    SELECT COUNT(*), COALESCE(SUM(ci.quantity * p.price), 0.00)
    INTO v_item_count, v_order_total
    FROM cart_items ci
    JOIN products p ON ci.product_id = p.product_id
    WHERE ci.cart_id = v_cart_id;

    IF v_item_count = 0 THEN
        SET p_order_id = NULL;
        SET p_status_message = 'FAILED: Shopping cart is empty.';
        LEAVE proc_body;
    END IF;

    -- Decouple products read from order_items trigger using a temporary snapshot.
    -- This prevents MySQL ERROR 1442 (updating products while products is in FROM clause).
    DROP TEMPORARY TABLE IF EXISTS _temp_checkout_items;
    CREATE TEMPORARY TABLE _temp_checkout_items AS
    SELECT ci.product_id, ci.quantity, p.price
    FROM cart_items ci
    JOIN products p ON ci.product_id = p.product_id
    WHERE ci.cart_id = v_cart_id;

    -- BEGIN ATOMIC TRANSACTION
    START TRANSACTION;

    -- 1. Create order header row
    INSERT INTO orders (user_id, address_id, order_date, status, total_amount)
    VALUES (p_user_id, p_address_id, NOW(), 'pending', v_order_total);

    SET v_new_order_id = LAST_INSERT_ID();

    -- 2. Populate order_items from temporary snapshot
    --    NOTE: trg_before_order_items_insert verifies stock per item;
    --          trg_after_order_items_insert decrements stock per item.
    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
    SELECT v_new_order_id, product_id, quantity, price
    FROM _temp_checkout_items;

    DROP TEMPORARY TABLE IF EXISTS _temp_checkout_items;

    -- 3. Create 1:1 payment record
    INSERT INTO payments (order_id, method, amount, status, paid_at)
    VALUES (
        v_new_order_id,
        p_payment_method,
        v_order_total,
        IF(p_payment_method = 'cod', 'pending', 'completed'),
        IF(p_payment_method = 'cod', NULL, NOW())
    );

    -- 4. If paid instantly via electronic rail, update order status to 'paid'
    IF p_payment_method <> 'cod' THEN
        UPDATE orders SET status = 'paid' WHERE order_id = v_new_order_id;
    END IF;

    -- 5. Mark the cart as converted so it cannot be checked out again
    UPDATE carts SET status = 'converted' WHERE cart_id = v_cart_id;

    -- COMMIT ALL ATOMIC CHANGES
    COMMIT;

    SET p_order_id = v_new_order_id;
    SET p_status_message = 'SUCCESS: Order placed successfully.';

END proc_body$$
DELIMITER ;


-- Procedure 2: sp_cancel_order
-- WHY: Handles customer or admin order cancellation within a transaction.
--      Restores deducted stock back into the products catalog, marks payments
--      as refunded if previously completed, updates order status to 'cancelled',
--      and triggers an automated audit trail row via trg_after_orders_update_audit.
DELIMITER $$
CREATE PROCEDURE sp_cancel_order(
    IN p_order_id INT,
    OUT p_status_message VARCHAR(255)
)
proc_body: BEGIN
    DECLARE v_current_status VARCHAR(20);
    DECLARE v_err_msg VARCHAR(255) DEFAULT '';

    -- Rollback on any SQL exception
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 v_err_msg = MESSAGE_TEXT;
        ROLLBACK;
        SET p_status_message = CONCAT('FAILED: ', COALESCE(v_err_msg, 'Cancellation error'));
    END;

    -- Check order existence and status
    SELECT status INTO v_current_status
    FROM orders
    WHERE order_id = p_order_id;

    IF v_current_status IS NULL THEN
        SET p_status_message = 'FAILED: Order not found.';
        LEAVE proc_body;
    END IF;

    IF v_current_status = 'cancelled' THEN
        SET p_status_message = 'FAILED: Order is already cancelled.';
        LEAVE proc_body;
    END IF;

    IF v_current_status = 'delivered' THEN
        SET p_status_message = 'FAILED: Cannot cancel an order that has already been delivered.';
        LEAVE proc_body;
    END IF;

    -- BEGIN ATOMIC TRANSACTION
    START TRANSACTION;

    -- 1. Restore stock to product inventory
    UPDATE products p
    JOIN order_items oi ON p.product_id = oi.product_id
    SET p.stock_quantity = p.stock_quantity + oi.quantity
    WHERE oi.order_id = p_order_id;

    -- 2. Mark payment as refunded if completed, or failed if pending
    UPDATE payments
    SET status = IF(status = 'completed', 'refunded', 'failed')
    WHERE order_id = p_order_id;

    -- 3. Update order status to 'cancelled' (fires audit trigger)
    UPDATE orders
    SET status = 'cancelled'
    WHERE order_id = p_order_id;

    COMMIT;

    SET p_status_message = 'SUCCESS: Order cancelled and inventory stock restored.';

END proc_body$$
DELIMITER ;


-- Procedure 3: sp_mark_abandoned_carts
-- WHY: Maintenance batch job that detects all active shopping carts left idle
--      for 7 or more days and changes their status to 'abandoned' for cleanup
--      and sales funnel analytics.
DELIMITER $$
CREATE PROCEDURE sp_mark_abandoned_carts(
    OUT p_affected_count INT
)
BEGIN
    UPDATE carts
    SET status = 'abandoned'
    WHERE status = 'active'
      AND updated_at <= DATE_SUB(NOW(), INTERVAL 7 DAY);

    SET p_affected_count = ROW_COUNT();
END$$
DELIMITER ;

