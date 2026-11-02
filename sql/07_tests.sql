-- ============================================================================
-- Script: 07_tests.sql
-- Description: Automated Comprehensive Test Suite for Online Shopping System (Q8)
-- Database Engine: MySQL 8.0
--
-- Re-runnable: Can be executed repeatedly; cleans up all temporary test artifacts.
-- ============================================================================

USE online_shop;

DROP TABLE IF EXISTS test_results;
CREATE TABLE test_results (
    test_id VARCHAR(10) PRIMARY KEY,
    test_name VARCHAR(100) NOT NULL,
    input_description TEXT NOT NULL,
    expected_result TEXT NOT NULL,
    actual_result TEXT NOT NULL,
    status ENUM('PASS', 'FAIL') NOT NULL
) ENGINE=InnoDB;

DROP PROCEDURE IF EXISTS sp_run_all_tests;
DELIMITER $$
CREATE PROCEDURE sp_run_all_tests()
BEGIN
    DECLARE v_error_code INT DEFAULT 0;
    DECLARE v_error_msg VARCHAR(255) DEFAULT '';
    DECLARE v_val_before INT DEFAULT 0;
    DECLARE v_val_after INT DEFAULT 0;
    DECLARE v_cnt INT DEFAULT 0;
    DECLARE v_test_uid INT DEFAULT 0;
    DECLARE v_test_pid INT DEFAULT 0;
    DECLARE v_order_id INT DEFAULT NULL;
    DECLARE v_status_msg VARCHAR(255) DEFAULT '';

    -- ------------------------------------------------------------------------
    -- TEST 1: Duplicate Email Rejection (UNIQUE constraint on users.email)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE CONTINUE HANDLER FOR 1062
        BEGIN
            SET v_error_code = 1062;
            SET v_error_msg = 'Caught Error 1062: Duplicate entry for key users.email';
        END;

        SET v_error_code = 0;
        SET v_error_msg = '';

        INSERT INTO users (full_name, email, password_hash, role)
        VALUES ('Imposter Admin', 'admin@muetshop.pk', 'fake_hash', 'customer');

        IF v_error_code = 1062 THEN
            INSERT INTO test_results VALUES ('T1', 'Duplicate Email Rejection',
                'INSERT user with existing email admin@muetshop.pk',
                'Rejection with Error 1062 (Duplicate entry)',
                v_error_msg, 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T1', 'Duplicate Email Rejection',
                'INSERT user with existing email admin@muetshop.pk',
                'Rejection with Error 1062',
                'FAILED: Duplicate email was accepted', 'FAIL');
        END IF;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 2: Negative Product Price Rejection (CHECK chk_products_price)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE CONTINUE HANDLER FOR 3819
        BEGIN
            SET v_error_code = 3819;
            SET v_error_msg = 'Caught Error 3819: Check constraint chk_products_price violated';
        END;

        SET v_error_code = 0;
        SET v_error_msg = '';

        INSERT INTO products (category_id, supplier_id, name, price, stock_quantity)
        VALUES (1, 1, 'Negative Price Test Item', -250.00, 10);

        IF v_error_code = 3819 THEN
            INSERT INTO test_results VALUES ('T2', 'Negative Price Rejection',
                'INSERT product with price = -250.00 PKR',
                'Engine CHECK constraint chk_products_price violated',
                v_error_msg, 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T2', 'Negative Price Rejection',
                'INSERT product with price = -250.00 PKR',
                'CHECK constraint violation',
                'FAILED: Negative price was accepted', 'FAIL');
        END IF;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 3: Negative Stock Quantity Rejection (CHECK chk_products_stock)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE CONTINUE HANDLER FOR 3819
        BEGIN
            SET v_error_code = 3819;
            SET v_error_msg = 'Caught Error 3819: Check constraint chk_products_stock violated';
        END;

        SET v_error_code = 0;
        SET v_error_msg = '';

        INSERT INTO products (category_id, supplier_id, name, price, stock_quantity)
        VALUES (1, 1, 'Negative Stock Test Item', 500.00, -10);

        IF v_error_code = 3819 THEN
            INSERT INTO test_results VALUES ('T3', 'Negative Stock Rejection',
                'INSERT product with stock_quantity = -10',
                'Engine CHECK constraint chk_products_stock violated',
                v_error_msg, 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T3', 'Negative Stock Rejection',
                'INSERT product with stock_quantity = -10',
                'CHECK constraint violation',
                'FAILED: Negative stock was accepted', 'FAIL');
        END IF;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 4: Invalid Review Rating Rejection (CHECK chk_reviews_rating)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE CONTINUE HANDLER FOR 3819
        BEGIN
            SET v_error_code = 3819;
            SET v_error_msg = 'Caught Error 3819: Check constraint chk_reviews_rating violated';
        END;

        SET v_error_code = 0;
        SET v_error_msg = '';

        INSERT INTO reviews (user_id, product_id, rating, comment)
        VALUES (5, 12, 6, 'Rating 6 out of 5 stars');

        IF v_error_code = 3819 THEN
            INSERT INTO test_results VALUES ('T4', 'Invalid Review Rating Rejection',
                'INSERT review with rating = 6 (valid range 1-5)',
                'Engine CHECK constraint chk_reviews_rating violated',
                v_error_msg, 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T4', 'Invalid Review Rating Rejection',
                'INSERT review with rating = 6',
                'CHECK constraint violation',
                'FAILED: Invalid rating was accepted', 'FAIL');
        END IF;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 5: Overselling Blocked & Atomic Transaction Rollback
    -- ------------------------------------------------------------------------
    BEGIN
        -- Setup user 15 with temporary cart exceeding stock of product 8 (stock=3, request 99)
        DELETE FROM cart_items WHERE cart_id = 998;
        DELETE FROM carts WHERE cart_id = 998;
        INSERT INTO carts (cart_id, user_id, status) VALUES (998, 15, 'active');
        INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (998, 8, 99);

        SELECT stock_quantity INTO v_val_before FROM products WHERE product_id = 8;
        SELECT COUNT(*) INTO v_cnt FROM orders;

        CALL sp_place_order(15, 17, 'cod', v_order_id, v_status_msg);

        SELECT stock_quantity INTO v_val_after FROM products WHERE product_id = 8;

        IF v_order_id IS NULL AND v_status_msg LIKE '%Oversell Error%' AND v_val_before = v_val_after THEN
            INSERT INTO test_results VALUES ('T5', 'Oversell Prevention & ACID Rollback',
                'Checkout 99 units when available stock is 3',
                'Transaction aborted, 0 orders added, stock unchanged',
                CONCAT('Rollback confirmed. Result: ', v_status_msg, ', Stock remained: ', v_val_after),
                'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T5', 'Oversell Prevention & ACID Rollback',
                'Checkout 99 units with 3 in stock',
                'Rollback and error',
                CONCAT('FAILED: Order created or stock mutated. Msg: ', v_status_msg), 'FAIL');
        END IF;

        DELETE FROM cart_items WHERE cart_id = 998;
        DELETE FROM carts WHERE cart_id = 998;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 6: Automatic Stock Reduction via Trigger (trg_after_order_items_insert)
    -- ------------------------------------------------------------------------
    BEGIN
        SELECT stock_quantity INTO v_val_before FROM products WHERE product_id = 10;

        -- Create active cart with 2 units of product 10 (Logitech Mouse)
        DELETE FROM cart_items WHERE cart_id = 997;
        DELETE FROM carts WHERE cart_id = 997;
        INSERT INTO carts (cart_id, user_id, status) VALUES (997, 15, 'active');
        INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (997, 10, 2);

        CALL sp_place_order(15, 17, 'cod', v_order_id, v_status_msg);

        SELECT stock_quantity INTO v_val_after FROM products WHERE product_id = 10;

        IF v_order_id IS NOT NULL AND (v_val_before - v_val_after) = 2 THEN
            INSERT INTO test_results VALUES ('T6', 'Automatic Stock Reduction Trigger',
                'Order 2 units of product #10 via sp_place_order',
                'Stock quantity decremented by exactly 2 via AFTER INSERT trigger',
                CONCAT('Stock changed from ', v_val_before, ' to ', v_val_after, ' (Decremented by 2)'),
                'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T6', 'Automatic Stock Reduction Trigger',
                'Order 2 units of product #10',
                'Stock decremented by 2',
                CONCAT('FAILED: Stock before: ', v_val_before, ', after: ', v_val_after), 'FAIL');
        END IF;

        -- Clean up test order
        DELETE FROM payments WHERE order_id = v_order_id;
        DELETE FROM order_items WHERE order_id = v_order_id;
        DELETE FROM orders WHERE order_id = v_order_id;
        UPDATE products SET stock_quantity = v_val_before WHERE product_id = 10;
        DELETE FROM cart_items WHERE cart_id = 997;
        DELETE FROM carts WHERE cart_id = 997;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 7: Automated Audit Trail on Order Status Change (trg_after_orders_update_audit)
    -- ------------------------------------------------------------------------
    BEGIN
        INSERT INTO orders (order_id, user_id, address_id, status, total_amount)
        VALUES (9999, 15, 17, 'pending', 5000.00);

        -- Update status to cancelled: trigger should log this
        UPDATE orders SET status = 'cancelled' WHERE order_id = 9999;

        SELECT COUNT(*) INTO v_cnt 
        FROM audit_log 
        WHERE table_name = 'orders' AND record_id = 9999 AND action = 'STATUS_CHANGE';

        IF v_cnt > 0 THEN
            INSERT INTO test_results VALUES ('T7', 'Automated Audit Trail Trigger',
                'Update order #9999 status from pending to cancelled',
                'Row created automatically in audit_log by trg_after_orders_update_audit',
                CONCAT('Audit record verified in audit_log for order #9999'), 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T7', 'Automated Audit Trail Trigger',
                'Update order status',
                'Audit log row created',
                'FAILED: No audit log row found', 'FAIL');
        END IF;

        DELETE FROM audit_log WHERE table_name = 'orders' AND record_id = 9999;
        DELETE FROM orders WHERE order_id = 9999;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 8: Unverified Purchase Review Blocked (trg_before_reviews_insert)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE CONTINUE HANDLER FOR SQLSTATE '45000'
        BEGIN
            SET v_error_code = 45000;
            SET v_error_msg = 'Caught SQLSTATE 45000: Review Error (Unverified purchase)';
        END;

        SET v_error_code = 0;
        SET v_error_msg = '';

        -- Customer 15 never purchased product 1 (Samsung S24 Ultra)
        INSERT INTO reviews (user_id, product_id, rating, comment)
        VALUES (15, 1, 5, 'Fake unverified review submission');

        IF v_error_code = 45000 THEN
            INSERT INTO test_results VALUES ('T8', 'Unverified Review Trigger Block',
                'Customer #15 attempts review on product #1 (never delivered)',
                'Engine trigger trg_before_reviews_insert raises 45000 custom error',
                v_error_msg, 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T8', 'Unverified Review Trigger Block',
                'Customer attempts review on unpurchased product',
                'Trigger error 45000',
                'FAILED: Unverified review was allowed', 'FAIL');
        END IF;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 9: Referential Integrity (RESTRICT on Ordered Products)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE CONTINUE HANDLER FOR 1451
        BEGIN
            SET v_error_code = 1451;
            SET v_error_msg = 'Caught Error 1451: Cannot delete or update a parent row: foreign key constraint fails (RESTRICT)';
        END;

        SET v_error_code = 0;
        SET v_error_msg = '';

        -- Product 12 is referenced in order_items for order 1
        DELETE FROM products WHERE product_id = 12;

        IF v_error_code = 1451 THEN
            INSERT INTO test_results VALUES ('T9', 'Referential Integrity (RESTRICT Delete)',
                'DELETE product #12 which has historic order_items records',
                'Engine blocks deletion with Error 1451 (foreign key RESTRICT)',
                v_error_msg, 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T9', 'Referential Integrity (RESTRICT Delete)',
                'DELETE ordered product',
                'Foreign key restriction 1451',
                'FAILED: Referenced product was deleted', 'FAIL');
        END IF;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 10: Cascading Delete on Dependent Addresses (ON DELETE CASCADE)
    -- ------------------------------------------------------------------------
    BEGIN
        -- Insert temporary user and address
        INSERT INTO users (user_id, full_name, email, password_hash, role)
        VALUES (8888, 'Temporary Cascading User', 'cascade.test@muetshop.pk', 'hash', 'customer');

        INSERT INTO addresses (user_id, line1, city, province, postal_code, is_default)
        VALUES (8888, '123 Cascade Test Road', 'Hyderabad', 'Sindh', '71000', 1);

        -- Delete user: address MUST cascade delete automatically
        DELETE FROM users WHERE user_id = 8888;

        SELECT COUNT(*) INTO v_cnt FROM addresses WHERE user_id = 8888;

        IF v_cnt = 0 THEN
            INSERT INTO test_results VALUES ('T10', 'Cascading Delete (ON DELETE CASCADE)',
                'DELETE user with linked delivery address records',
                'Dependent addresses deleted automatically via ON DELETE CASCADE',
                'Child address rows cleaned up cleanly (0 orphan records remaining)', 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T10', 'Cascading Delete (ON DELETE CASCADE)',
                'DELETE parent user',
                'Cascading deletion of child addresses',
                'FAILED: Orphan address records remained', 'FAIL');
        END IF;
    END;

END$$
DELIMITER ;

-- Execute all tests
CALL sp_run_all_tests();

-- Display test results table
SELECT test_id, test_name, expected_result, actual_result, status FROM test_results;
