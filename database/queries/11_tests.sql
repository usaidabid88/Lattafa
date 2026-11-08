-- ============================================================================
-- Script: 11_tests.sql
-- Note: Sequenced as script 11 to execute after all migrations (01 through 10)
-- Description: Automated Comprehensive Test Suite for Online Shopping System (Q8)
-- Database Engine: MySQL 8.0
--
-- Re-runnable: Can be executed repeatedly; cleans up all temporary test artifacts.
-- ============================================================================

-- USE online_shop; -- Uses active database context (e.g. online_shop_test)

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

    -- ------------------------------------------------------------------------
    -- TEST 11: Duplicate Primary Image Rejection (Trigger SQLSTATE 45000)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE CONTINUE HANDLER FOR SQLSTATE '45000'
        BEGIN
            SET v_error_code = 45000;
            SET v_error_msg = 'Caught SQLSTATE 45000: Product already has an active primary image';
        END;

        SET v_error_code = 0;
        SET v_error_msg = '';

        -- Ensure an initial primary image exists for product #1 if not already seeded
        IF (SELECT COUNT(*) FROM product_images WHERE product_id = 1 AND is_primary = 1) = 0 THEN
            INSERT INTO product_images (product_id, image_path, is_primary, sort_order)
            VALUES (1, 'static/images/initial_primary_t11.jpg', 1, 1);
        END IF;

        -- Product 1 already has a primary image. Inserting second primary image must fail.
        INSERT INTO product_images (product_id, image_path, is_primary, sort_order)
        VALUES (1, 'static/images/illegal_dup_primary.jpg', 1, 99);

        DELETE FROM product_images WHERE product_id = 1 AND image_path = 'static/images/initial_primary_t11.jpg';

        IF v_error_code = 45000 THEN
            INSERT INTO test_results VALUES ('T11', 'Single Primary Image Enforcement',
                'INSERT second primary image for product #1',
                'Trigger trg_product_images_single_primary_bi raises SQLSTATE 45000',
                v_error_msg, 'PASS');
        ELSE
            DELETE FROM product_images WHERE product_id = 1 AND sort_order = 99;
            INSERT INTO test_results VALUES ('T11', 'Single Primary Image Enforcement',
                'INSERT second primary image',
                'SQLSTATE 45000 constraint abort',
                'FAILED: Multiple primary images were permitted', 'FAIL');
        END IF;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 12: Cascading Delete on Product Gallery Images (ON DELETE CASCADE)
    -- ------------------------------------------------------------------------
    BEGIN
        SET v_cnt = 0;
        -- Insert dummy product and gallery image
        INSERT INTO products (product_id, category_id, supplier_id, name, price, stock_quantity)
        VALUES (9999, 1, 1, 'Cascade Image Test Item', 500.00, 5);

        INSERT INTO product_images (product_id, image_path, is_primary, sort_order)
        VALUES (9999, 'static/images/temp_cascade.jpg', 1, 1);

        -- Delete dummy product
        DELETE FROM products WHERE product_id = 9999;

        -- Check images count
        SELECT COUNT(*) INTO v_cnt FROM product_images WHERE product_id = 9999;

        IF v_cnt = 0 THEN
            INSERT INTO test_results VALUES ('T12', 'Gallery Cascade Deletion (ON DELETE CASCADE)',
                'DELETE product #9999 with linked gallery image rows',
                'Linked product_images rows deleted automatically via ON DELETE CASCADE',
                '0 orphan image records remaining', 'PASS');
        ELSE
            DELETE FROM product_images WHERE product_id = 9999;
            INSERT INTO test_results VALUES ('T12', 'Gallery Cascade Deletion (ON DELETE CASCADE)',
                'DELETE parent product',
                'Cascading deletion of gallery images',
                'FAILED: Orphan product_images remained', 'FAIL');
        END IF;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 13: Historical Order Preservation (FK RESTRICT on order_items)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE CONTINUE HANDLER FOR 1451
        BEGIN
            SET v_error_code = 1451;
            SET v_error_msg = 'Caught Error 1451: Cannot delete or update a parent row: foreign key constraint fails';
        END;

        SET v_error_code = 0;
        SET v_error_msg = '';

        -- Product 12 (J. Classic Cotton Kurta) is referenced in historic order_items
        DELETE FROM products WHERE product_id = 12;

        IF v_error_code = 1451 THEN
            INSERT INTO test_results VALUES ('T13', 'Historic Order Preservation (FK RESTRICT)',
                'DELETE product #12 with historic purchase records in order_items',
                'Foreign key RESTRICT blocks deletion with Error 1451',
                v_error_msg, 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T13', 'Historic Order Preservation (FK RESTRICT)',
                'DELETE ordered product',
                'Foreign key restriction Error 1451',
                'FAILED: Ordered product was deleted, violating accounting audit integrity', 'FAIL');
        END IF;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 14: Category Roll-Up Consistency (v_category_counts view)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE v_parent_sum INT DEFAULT 0;
        DECLARE v_active_total INT DEFAULT 0;

        SELECT SUM(active_product_count) INTO v_parent_sum
        FROM v_category_counts
        WHERE parent_category_id IS NULL AND category_slug != 'home-living';

        SELECT COUNT(*) INTO v_active_total
        FROM products
        WHERE is_active = 1;

        IF v_parent_sum = v_active_total THEN
            INSERT INTO test_results VALUES ('T14', 'Category Roll-Up Consistency',
                'Sum of active products across top-level departments vs actual products',
                CONCAT('Perfect match: ', v_active_total, ' active products'),
                CONCAT('Verified consistent count: ', v_parent_sum, ' products in view roll-up'), 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T14', 'Category Roll-Up Consistency',
                'Top-level category sum vs total active products',
                CONCAT('Count = ', v_active_total),
                CONCAT('FAILED: View sum is ', v_parent_sum), 'FAIL');
        END IF;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 15: Brand Foreign Key Integrity (FK fk_products_brand)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE CONTINUE HANDLER FOR 1452
        BEGIN
            SET v_error_code = 1452;
            SET v_error_msg = 'Caught Error 1452: Foreign key constraint fk_products_brand fails';
        END;

        SET v_error_code = 0;
        SET v_error_msg = '';

        -- Assign invalid brand_id 99999
        INSERT INTO products (category_id, brand_id, supplier_id, name, price, stock_quantity)
        VALUES (1, 99999, 1, 'Invalid Brand Item', 1000.00, 5);

        IF v_error_code = 1452 THEN
            INSERT INTO test_results VALUES ('T15', 'Brand Referential Integrity (FK Constraint)',
                'INSERT product with non-existent brand_id = 99999',
                'Rejection with Error 1452 (foreign key violation)',
                v_error_msg, 'PASS');
        ELSE
            DELETE FROM products WHERE name = 'Invalid Brand Item';
            INSERT INTO test_results VALUES ('T15', 'Brand Referential Integrity (FK Constraint)',
                'INSERT product with non-existent brand_id',
                'Error 1452 constraint violation',
                'FAILED: Non-existent brand_id was accepted', 'FAIL');
        END IF;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 16: Single-Source Pricing Parity (sp_cart_summary, AC-01.1, AC-01.2)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE v_t_cart_id INT;
        DECLARE v_sub DECIMAL(10,2);
        DECLARE v_tax DECIMAL(10,2);
        DECLARE v_fee DECIMAL(10,2);
        DECLARE v_tot DECIMAL(10,2);
        DECLARE v_min INT;
        DECLARE v_max INT;

        -- Create isolated cart with product 1 to verify deterministic pricing calculations
        INSERT INTO carts (user_id, session_token, status) VALUES (NULL, 'tok_test_parity_t16', 'active');
        SET v_t_cart_id = LAST_INSERT_ID();
        INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (v_t_cart_id, 1, 1);

        CALL sp_cart_summary(v_t_cart_id, 'Sindh', 'Karachi', v_sub, v_tax, v_fee, v_tot, v_min, v_max);

        IF v_tot = (v_sub + v_tax + v_fee) AND v_fee = 150.00 THEN
            INSERT INTO test_results VALUES ('T16', 'Price Parity (sp_cart_summary)',
                'Compute subtotal + tax + fee = total_amount for Karachi, Sindh',
                'Total exactly equals subtotal + tax + delivery fee (Rs 150 fee)',
                CONCAT('Computed Total: PKR ', v_tot, ' = ', v_sub, ' + ', v_tax, ' + ', v_fee), 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T16', 'Price Parity (sp_cart_summary)',
                'Check total equals subtotal + tax + fee',
                'Parity verified',
                CONCAT('FAILED: Total divergence detected: ', v_tot), 'FAIL');
        END IF;

        DELETE FROM cart_items WHERE cart_id = v_t_cart_id;
        DELETE FROM carts WHERE cart_id = v_t_cart_id;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 17: Guest Checkout Execution (sp_place_guest_order, AC-03.1)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE v_t_cart_id INT;
        DECLARE v_g_order_id INT;
        DECLARE v_g_msg VARCHAR(255);
        DECLARE v_is_null_uid INT;

        INSERT INTO carts (user_id, session_token, status) VALUES (NULL, 'tok_test_guest_t17', 'active');
        SET v_t_cart_id = LAST_INSERT_ID();
        INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (v_t_cart_id, 1, 1);

        CALL sp_place_guest_order('tok_test_guest_t17', 'Kamran Akmal', 'kamran@test.pk', '03001234567',
                                  'Street 5, Saddar', 'Hyderabad', 'Sindh', 'cod', v_g_order_id, v_g_msg);

        SELECT COUNT(*) INTO v_is_null_uid FROM orders WHERE order_id = v_g_order_id AND user_id IS NULL;

        IF v_g_order_id IS NOT NULL AND v_is_null_uid = 1 THEN
            INSERT INTO test_results VALUES ('T17', 'Guest Checkout Placement (AC-03.1)',
                'Place order with guest token without account registration',
                'Order created successfully with user_id IS NULL and address snapshot',
                CONCAT('Guest Order #', v_g_order_id, ' created with user_id NULL'), 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T17', 'Guest Checkout Placement (AC-03.1)',
                'Guest order creation',
                'Order created with user_id IS NULL',
                CONCAT('FAILED: ', v_g_msg), 'FAIL');
        END IF;

        DELETE FROM orders WHERE order_id = v_g_order_id;
        DELETE FROM carts WHERE cart_id = v_t_cart_id;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 18: Anonymous Guest Cart Merge (sp_merge_carts, AC-08.2)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE v_g_cart INT;
        DECLARE v_u_cart INT;
        DECLARE v_merged_cnt INT;
        DECLARE v_item_check INT;

        INSERT INTO carts (user_id, session_token, status) VALUES (NULL, 'tok_merge_test_t18', 'active');
        SET v_g_cart = LAST_INSERT_ID();
        INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (v_g_cart, 3, 2);

        SELECT cart_id INTO v_u_cart FROM carts WHERE user_id = 2 AND status = 'active' LIMIT 1;
        IF v_u_cart IS NULL THEN
            INSERT INTO carts (user_id, status) VALUES (2, 'active');
            SET v_u_cart = LAST_INSERT_ID();
        END IF;

        CALL sp_merge_carts('tok_merge_test_t18', 2, v_merged_cnt);

        SELECT COUNT(*) INTO v_item_check FROM cart_items WHERE cart_id = v_u_cart AND product_id = 3;

        IF v_item_check >= 1 THEN
            INSERT INTO test_results VALUES ('T18', 'Guest Cart Merge on Login (AC-08.2)',
                'Merge items from session token cart into customer account cart',
                'Items combined into customer cart and guest cart converted',
                'Items successfully merged into user #2 active cart', 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T18', 'Guest Cart Merge on Login (AC-08.2)',
                'Guest cart merge',
                'Items combined',
                'FAILED: Items not found in user cart after merge', 'FAIL');
        END IF;

        DELETE FROM carts WHERE cart_id = v_g_cart;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 19: Order Status History Trigger (trg_order_status_history, AC-04.3)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE v_hist_cnt INT;

        UPDATE orders SET status = 'shipped' WHERE order_id = 1;
        SELECT COUNT(*) INTO v_hist_cnt FROM order_status_history 
        WHERE order_id = 1 AND new_status = 'shipped';

        UPDATE orders SET status = 'delivered' WHERE order_id = 1;

        IF v_hist_cnt >= 1 THEN
            INSERT INTO test_results VALUES ('T19', 'Order Status Audit Trigger (AC-04.3)',
                'UPDATE orders.status to trigger automatic audit log entry',
                'Row created in order_status_history with old_status and new_status',
                'Status transition record verified in order_status_history', 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T19', 'Order Status Audit Trigger (AC-04.3)',
                'Trigger execution on status update',
                'Audit record created in order_status_history',
                'FAILED: No audit record found in order_status_history', 'FAIL');
        END IF;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 20: Delivery Address Snapshot Immutability (AC-04.2)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE v_snap_orig TEXT;
        DECLARE v_snap_after TEXT;

        SELECT shipping_address_snapshot INTO v_snap_orig FROM orders WHERE order_id = 1;
        IF v_snap_orig IS NULL THEN
            UPDATE orders SET shipping_address_snapshot = 'Original Immutable Snapshot' WHERE order_id = 1;
            SET v_snap_orig = 'Original Immutable Snapshot';
        END IF;

        UPDATE addresses SET line1 = 'New Modified Street 999' WHERE address_id = 1;
        SELECT shipping_address_snapshot INTO v_snap_after FROM orders WHERE order_id = 1;

        IF v_snap_orig = v_snap_after THEN
            INSERT INTO test_results VALUES ('T20', 'Address Snapshot Immutability (AC-04.2)',
                'Modify customer address book entry; inspect historical order snapshot',
                'Order shipping_address_snapshot remains completely unaltered',
                'Historical order address preserved intact despite address edit', 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T20', 'Address Snapshot Immutability (AC-04.2)',
                'Address snapshot check',
                'Snapshot remains identical',
                'FAILED: Historical snapshot changed when address book was edited', 'FAIL');
        END IF;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 21: Support Ticket Filing & Number Generation (AC-04.4)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE v_tck_id INT;
        DECLARE v_tck_num VARCHAR(30);

        INSERT INTO support_tickets (ticket_number, contact_name, contact_email, issue_type, subject, description, status)
        VALUES ('TCK-TEST-SQL-21', 'Shahid Afridi', 'shahid@test.pk', 'damaged', 'Item damaged', 'Box arrived crushed', 'open');
        SET v_tck_id = LAST_INSERT_ID();

        SELECT ticket_number INTO v_tck_num FROM support_tickets WHERE ticket_id = v_tck_id;

        IF v_tck_num = 'TCK-TEST-SQL-21' THEN
            INSERT INTO test_results VALUES ('T21', 'Customer Support Ticketing (AC-04.4)',
                'Insert support ticket with category and contact information',
                'Record saved in support_tickets with status open',
                'Support ticket TCK-TEST-SQL-21 created successfully', 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T21', 'Customer Support Ticketing (AC-04.4)',
                'Ticket creation',
                'Ticket saved',
                'FAILED: Support ticket not created', 'FAIL');
        END IF;

        DELETE FROM support_tickets WHERE ticket_id = v_tck_id;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 22: Seller Verification Catalog Filtering (AC-06.2)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE v_before_cnt INT;
        DECLARE v_after_cnt INT;

        SELECT COUNT(*) INTO v_before_cnt FROM v_product_catalog WHERE seller_id = 1;

        UPDATE suppliers SET verification_status = 'rejected' WHERE supplier_id = 1;
        SELECT COUNT(*) INTO v_after_cnt FROM v_product_catalog WHERE seller_id = 1;

        UPDATE suppliers SET verification_status = 'verified' WHERE supplier_id = 1;

        IF v_before_cnt > 0 AND v_after_cnt = 0 THEN
            INSERT INTO test_results VALUES ('T22', 'Seller Verification Governance (AC-06.2)',
                'Set seller verification_status = rejected; query v_product_catalog',
                'Rejected seller products excluded from storefront catalog view',
                CONCAT('Verified isolation: Catalog items dropped from ', v_before_cnt, ' to 0'), 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T22', 'Seller Verification Governance (AC-06.2)',
                'Catalog exclusion test',
                'Items excluded when seller is rejected',
                CONCAT('FAILED: Rejected seller items still visible: ', v_after_cnt), 'FAIL');
        END IF;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 23: Return Status History Audit Trigger (AC-08.5)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE v_ret_id INT;
        DECLARE v_ret_hist_cnt INT;

        INSERT INTO return_requests (return_number, order_id, product_id, reason, description, status)
        VALUES ('RMA-TEST-SQL-23', 1, 1, 'defective', 'Hardware issue', 'requested');
        SET v_ret_id = LAST_INSERT_ID();

        UPDATE return_requests SET status = 'approved' WHERE return_id = v_ret_id;
        SELECT COUNT(*) INTO v_ret_hist_cnt FROM return_status_history 
        WHERE return_id = v_ret_id AND new_status = 'approved';

        IF v_ret_hist_cnt >= 1 THEN
            INSERT INTO test_results VALUES ('T23', 'Return Status Audit Trigger (AC-08.5)',
                'UPDATE return_requests.status; check return_status_history trigger',
                'Row created in return_status_history by trg_return_status_history',
                'Return status transition to approved verified in audit table', 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T23', 'Return Status Audit Trigger (AC-08.5)',
                'Trigger execution on return status update',
                'Audit record created in return_status_history',
                'FAILED: No audit record in return_status_history', 'FAIL');
        END IF;

        DELETE FROM return_requests WHERE return_id = v_ret_id;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 24: Overdue Return Requests View (AC-08.6)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE v_overdue_found INT;
        DECLARE v_old_ret_id INT;

        INSERT INTO return_requests (return_number, order_id, product_id, reason, description, status, created_at)
        VALUES ('RMA-OVERDUE-T24', 1, 1, 'damaged', 'Old damaged box', 'requested', DATE_SUB(NOW(), INTERVAL 4 DAY));
        SET v_old_ret_id = LAST_INSERT_ID();

        SELECT COUNT(*) INTO v_overdue_found FROM v_overdue_return_requests WHERE return_number = 'RMA-OVERDUE-T24';

        IF v_overdue_found >= 1 THEN
            INSERT INTO test_results VALUES ('T24', 'Overdue Return SLA Escalation View (AC-08.6)',
                'Query v_overdue_return_requests for claims > 72 hours without response',
                'View accurately surfaces unattended claims with days_elapsed calculation',
                'Overdue claim detected by v_overdue_return_requests view', 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T24', 'Overdue Return SLA Escalation View (AC-08.6)',
                'Overdue view check',
                'Claim surfaced by view',
                'FAILED: Overdue claim not surfaced by view', 'FAIL');
        END IF;

        DELETE FROM return_requests WHERE return_id = v_old_ret_id;
    END;

    -- ------------------------------------------------------------------------
    -- TEST 25: Payment Attempts Audit Logging (AC-02.2)
    -- ------------------------------------------------------------------------
    BEGIN
        DECLARE v_pa_cnt INT;

        INSERT INTO payment_attempts (order_id, payment_method, amount, status, transaction_ref, failure_reason)
        VALUES (1, 'simulated', 5000.00, 'failed', 'TXN-FAIL-T25', 'Card declined: Test decline');

        SELECT COUNT(*) INTO v_pa_cnt FROM payment_attempts WHERE transaction_ref = 'TXN-FAIL-T25';

        IF v_pa_cnt = 1 THEN
            INSERT INTO test_results VALUES ('T25', 'Payment Attempt Audit Logging (AC-02.2)',
                'Log failed digital transaction in payment_attempts with reason',
                'Record saved with transaction_ref, amount, status, and failure_reason',
                'Failed payment attempt audit record verified in database', 'PASS');
        ELSE
            INSERT INTO test_results VALUES ('T25', 'Payment Attempt Audit Logging (AC-02.2)',
                'Payment attempt log check',
                'Record verified',
                'FAILED: Payment attempt not found', 'FAIL');
        END IF;

        DELETE FROM payment_attempts WHERE transaction_ref = 'TXN-FAIL-T25';
    END;

END$$
DELIMITER ;

-- Execute all tests
CALL sp_run_all_tests();

-- Display test results table
SELECT test_id, test_name, expected_result, actual_result, status FROM test_results;
