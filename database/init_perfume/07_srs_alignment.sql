-- ============================================================================
-- 09_srs_alignment.sql
-- Phase 12B: Database Schema Alignment for SRS Requirements
--
-- Adds:
--  - delivery_rates & tax_rates matrices (FR-01, FR-08, FR-09, AC-01.1)
--  - payment_methods & payment_attempts tables (FR-06, FR-10, FR-11, AC-02.x)
--  - order_status_history & automatic triggers (FR-12, AC-04.3)
--  - support_tickets table (FR-14, AC-04.4, AC-04.5, UR-06)
--  - return_requests & return_status_history with overdue view (FR-20, FR-21, AC-08.4-6)
--  - suppliers expansion into verified sellers (FR-17, FR-18, AC-06.1, AC-06.2)
--  - guest checkout support (nullable user_id, guest fields, carts.session_token)
--  - sp_cart_summary, sp_merge_carts, and enhanced sp_place_order / sp_place_guest_order
--  - shop_seller role (FR-18)
--
-- Safety: Non-destructive, re-runnable (runs cleanly multiple times).
-- ============================================================================

USE online_shop_perfume_dev;

-- ----------------------------------------------------------------------------
-- SECTION 1: COLUMN ADDITIONS TO EXISTING TABLES (IDEMPOTENT MIGRATION)
-- ----------------------------------------------------------------------------

DROP PROCEDURE IF EXISTS _sp_temp_srs_column_migration;
DELIMITER $$
CREATE PROCEDURE _sp_temp_srs_column_migration()
BEGIN
    -- 1. Modify orders.user_id to NULLable to support guest checkout (FR-02, AC-03.1)
    ALTER TABLE orders MODIFY COLUMN user_id INT NULL;

    -- 2. Modify orders.address_id to NULLable so guest orders can record address snapshot directly
    ALTER TABLE orders MODIFY COLUMN address_id INT NULL;

    -- 3. Add financial breakdown columns to orders (FR-01, FR-08, FR-09, NFR-06)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'orders' AND column_name = 'subtotal'
    ) THEN
        ALTER TABLE orders ADD COLUMN subtotal DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER order_date;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'orders' AND column_name = 'tax_amount'
    ) THEN
        ALTER TABLE orders ADD COLUMN tax_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER subtotal;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'orders' AND column_name = 'delivery_fee'
    ) THEN
        ALTER TABLE orders ADD COLUMN delivery_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER tax_amount;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'orders' AND column_name = 'expected_delivery_date'
    ) THEN
        ALTER TABLE orders ADD COLUMN expected_delivery_date DATE NULL AFTER delivery_fee;
    END IF;

    -- 4. Add guest checkout contact and address columns to orders (FR-02, AC-03.1)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'orders' AND column_name = 'guest_name'
    ) THEN
        ALTER TABLE orders ADD COLUMN guest_name VARCHAR(100) NULL AFTER total_amount;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'orders' AND column_name = 'guest_email'
    ) THEN
        ALTER TABLE orders ADD COLUMN guest_email VARCHAR(100) NULL AFTER guest_name;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'orders' AND column_name = 'guest_phone'
    ) THEN
        ALTER TABLE orders ADD COLUMN guest_phone VARCHAR(20) NULL AFTER guest_email;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'orders' AND column_name = 'guest_address_line1'
    ) THEN
        ALTER TABLE orders ADD COLUMN guest_address_line1 VARCHAR(255) NULL AFTER guest_phone;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'orders' AND column_name = 'guest_city'
    ) THEN
        ALTER TABLE orders ADD COLUMN guest_city VARCHAR(50) NULL AFTER guest_address_line1;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'orders' AND column_name = 'guest_province'
    ) THEN
        ALTER TABLE orders ADD COLUMN guest_province VARCHAR(50) NULL AFTER guest_city;
    END IF;

    -- 5. Add historical shipping address snapshot to orders (FR-13, AC-04.2)
    -- WHY: Guarantees that later customer address edits do not mutate historical order records.
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'orders' AND column_name = 'shipping_address_snapshot'
    ) THEN
        ALTER TABLE orders ADD COLUMN shipping_address_snapshot TEXT NULL AFTER guest_province;
    END IF;

    -- 6. Add terms and privacy consent timestamp to orders (FR-19, AC-06.3)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'orders' AND column_name = 'consent_terms_at'
    ) THEN
        ALTER TABLE orders ADD COLUMN consent_terms_at DATETIME NULL AFTER shipping_address_snapshot;
    END IF;

    -- 7. Modify carts.user_id to NULLable and add session_token (FR-03, AC-08.1)
    ALTER TABLE carts MODIFY COLUMN user_id INT NULL;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'carts' AND column_name = 'session_token'
    ) THEN
        ALTER TABLE carts ADD COLUMN session_token VARCHAR(64) NULL AFTER user_id;
        ALTER TABLE carts ADD INDEX idx_carts_session_token (session_token);
    END IF;

    -- 8. Add alt_text to product_images for accessibility (FR-15, AR-06)
    -- WHY: Screen readers require meaningful descriptive text for all catalog merchandise visuals.
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'product_images' AND column_name = 'alt_text'
    ) THEN
        ALTER TABLE product_images ADD COLUMN alt_text VARCHAR(255) NULL AFTER image_path;
    END IF;

    -- 9. Expand users.role to include 'seller' role (FR-17, FR-18)
    ALTER TABLE users MODIFY COLUMN role ENUM('customer', 'seller', 'staff', 'admin') NOT NULL DEFAULT 'customer';

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'users' AND column_name = 'consent_terms_at'
    ) THEN
        ALTER TABLE users ADD COLUMN consent_terms_at DATETIME NULL AFTER role;
    END IF;

    -- 10. Expand suppliers into verified sellers (FR-17, FR-18, AC-06.1, AC-06.2)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'suppliers' AND column_name = 'business_name'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN business_name VARCHAR(150) NULL AFTER name;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'suppliers' AND column_name = 'contact_name'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN contact_name VARCHAR(100) NULL AFTER business_name;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'suppliers' AND column_name = 'address'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN address VARCHAR(255) NULL AFTER phone;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'suppliers' AND column_name = 'city'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN city VARCHAR(50) NULL AFTER address;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'suppliers' AND column_name = 'store_location'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN store_location VARCHAR(100) NULL AFTER city;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'suppliers' AND column_name = 'verification_status'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN verification_status ENUM('pending', 'verified', 'rejected') NOT NULL DEFAULT 'verified' AFTER store_location;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'suppliers' AND column_name = 'verified_at'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN verified_at DATETIME NULL AFTER verification_status;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'suppliers' AND column_name = 'verified_by'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN verified_by VARCHAR(50) NULL AFTER verified_at;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'suppliers' AND column_name = 'created_at'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP AFTER verified_by;
    END IF;

END$$
DELIMITER ;

CALL _sp_temp_srs_column_migration();
DROP PROCEDURE IF EXISTS _sp_temp_srs_column_migration;


-- ----------------------------------------------------------------------------
-- SECTION 2: NEW TABLES REQUIRED BY SRS
-- ----------------------------------------------------------------------------

-- WHY: delivery_rates provides a configurable pricing and delivery SLA schedule by province and city (FR-01, FR-08, AC-04.1).
CREATE TABLE IF NOT EXISTS delivery_rates (
    rate_id INT AUTO_INCREMENT PRIMARY KEY,
    province VARCHAR(50) NOT NULL,
    city VARCHAR(50) NULL,
    fee DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    min_days INT NOT NULL DEFAULT 2,
    max_days INT NOT NULL DEFAULT 5,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_delivery_province_city UNIQUE (province, city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- WHY: tax_rates provides tax computation rates per province/jurisdiction, ensuring transparent calculation (FR-01, FR-09).
CREATE TABLE IF NOT EXISTS tax_rates (
    tax_rate_id INT AUTO_INCREMENT PRIMARY KEY,
    province VARCHAR(50) NOT NULL UNIQUE,
    rate_percentage DECIMAL(5,2) NOT NULL DEFAULT 5.00,
    description VARCHAR(100) NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- WHY: payment_methods manages selectable checkout payment adapters with enable/disable flags (FR-06, AC-02.1).
CREATE TABLE IF NOT EXISTS payment_methods (
    method_id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(255) NULL,
    is_enabled TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- WHY: payment_attempts logs payment gateway interactions, transactions, and failure reasons to allow instant retry (FR-10, FR-11, AC-02.2).
CREATE TABLE IF NOT EXISTS payment_attempts (
    attempt_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status ENUM('initiated', 'pending', 'successful', 'failed', 'cancelled') NOT NULL DEFAULT 'initiated',
    transaction_ref VARCHAR(100) NULL,
    failure_reason VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_payment_attempts_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- WHY: order_status_history records an immutable timeline of every status transition for customer self-service tracking (FR-12, AC-04.3).
CREATE TABLE IF NOT EXISTS order_status_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    old_status VARCHAR(20) NULL,
    new_status VARCHAR(20) NOT NULL,
    changed_by VARCHAR(50) NOT NULL DEFAULT 'system',
    notes VARCHAR(255) NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_order_status_history_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- WHY: support_tickets enables customers to lodge delivery, product, or damaged package issues for staff queue triage (FR-14, AC-04.4, AC-04.5, UR-06).
CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_number VARCHAR(30) NOT NULL UNIQUE,
    order_id INT NULL,
    user_id INT NULL,
    contact_name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(20) NULL,
    issue_type ENUM('delayed', 'damaged', 'wrong_item', 'other') NOT NULL,
    subject VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('open', 'in_progress', 'resolved', 'closed') NOT NULL DEFAULT 'open',
    staff_notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_support_tickets_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL,
    CONSTRAINT fk_support_tickets_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- WHY: return_requests manages customer return and replacement claims with photo proof and refund options (FR-20, AC-08.4).
CREATE TABLE IF NOT EXISTS return_requests (
    return_id INT AUTO_INCREMENT PRIMARY KEY,
    return_number VARCHAR(30) NOT NULL UNIQUE,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    user_id INT NULL,
    guest_email VARCHAR(100) NULL,
    reason ENUM('damaged', 'defective', 'wrong_item', 'not_as_described', 'other') NOT NULL,
    description TEXT NOT NULL,
    proof_image_path VARCHAR(255) NULL,
    status ENUM('requested', 'approved', 'rejected', 'item_returned', 'refunded', 'completed') NOT NULL DEFAULT 'requested',
    refund_method ENUM('original_payment', 'store_credit', 'cod_refund') NOT NULL DEFAULT 'original_payment',
    seller_response TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_return_requests_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_return_requests_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    CONSTRAINT fk_return_requests_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- WHY: return_status_history logs all transitions in the return/replacement lifecycle for SLA compliance (FR-21, AC-08.5).
CREATE TABLE IF NOT EXISTS return_status_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    return_id INT NOT NULL,
    old_status VARCHAR(25) NULL,
    new_status VARCHAR(25) NOT NULL,
    changed_by VARCHAR(50) NOT NULL DEFAULT 'system',
    notes VARCHAR(255) NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_return_status_history_return FOREIGN KEY (return_id) REFERENCES return_requests(return_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ----------------------------------------------------------------------------
-- SECTION 3: TRIGGERS FOR ORDER & RETURN STATUS AUDITING
-- ----------------------------------------------------------------------------

-- WHY: Automatically inserts status transition history when an order status changes (FR-12, AC-04.3).
DROP TRIGGER IF EXISTS trg_order_status_history;
DELIMITER $$
CREATE TRIGGER trg_order_status_history
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO order_status_history (order_id, old_status, new_status, changed_by, notes)
        VALUES (NEW.order_id, OLD.status, NEW.status, 'system', CONCAT('Order status updated from ', OLD.status, ' to ', NEW.status));
    END IF;
END$$
DELIMITER ;

-- WHY: Automatically logs initial 'pending' creation record in order_status_history (FR-12, AC-04.3).
DROP TRIGGER IF EXISTS trg_order_initial_status_history;
DELIMITER $$
CREATE TRIGGER trg_order_initial_status_history
AFTER INSERT ON orders
FOR EACH ROW
BEGIN
    INSERT INTO order_status_history (order_id, old_status, new_status, changed_by, notes)
    VALUES (NEW.order_id, NULL, NEW.status, 'system', 'Order placed successfully');
END$$
DELIMITER ;

-- WHY: Automatically records status transitions on return requests (FR-21, AC-08.5).
DROP TRIGGER IF EXISTS trg_return_status_history;
DELIMITER $$
CREATE TRIGGER trg_return_status_history
AFTER UPDATE ON return_requests
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO return_status_history (return_id, old_status, new_status, changed_by, notes)
        VALUES (NEW.return_id, OLD.status, NEW.status, 'system', CONCAT('Return status transitioned from ', OLD.status, ' to ', NEW.status));
    END IF;
END$$
DELIMITER ;

-- WHY: Automatically logs initial 'requested' creation entry in return_status_history (FR-21, AC-08.5).
DROP TRIGGER IF EXISTS trg_return_initial_status_history;
DELIMITER $$
CREATE TRIGGER trg_return_initial_status_history
AFTER INSERT ON return_requests
FOR EACH ROW
BEGIN
    INSERT INTO return_status_history (return_id, old_status, new_status, changed_by, notes)
    VALUES (NEW.return_id, NULL, NEW.status, 'system', 'Return request lodged');
END$$
DELIMITER ;


-- ----------------------------------------------------------------------------
-- SECTION 4: VIEWS (OVERDUE RETURNS, VERIFIED SELLERS, EXPANDED CATALOG)
-- ----------------------------------------------------------------------------

-- WHY: Surfaces return requests that remain unattended past 3 days for SLA escalation (FR-21, AC-08.6).
CREATE OR REPLACE VIEW v_overdue_return_requests AS
SELECT 
    r.return_id,
    r.return_number,
    r.order_id,
    r.product_id,
    p.name AS product_name,
    s.supplier_id AS seller_id,
    s.name AS seller_name,
    r.reason,
    r.status,
    r.created_at,
    TIMESTAMPDIFF(HOUR, r.created_at, NOW()) AS hours_elapsed,
    DATEDIFF(NOW(), r.created_at) AS days_elapsed
FROM return_requests r
JOIN products p ON r.product_id = p.product_id
JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE r.status = 'requested' 
  AND r.created_at <= DATE_SUB(NOW(), INTERVAL 3 DAY);

-- WHY: Normalized view of seller accounts, contact details, and verification status (FR-17, FR-18, AC-06.1).
CREATE OR REPLACE VIEW v_sellers AS
SELECT 
    s.supplier_id AS seller_id,
    s.name,
    COALESCE(s.business_name, s.name) AS business_name,
    COALESCE(s.contact_name, s.name) AS contact_name,
    s.email,
    s.phone,
    s.address,
    s.city,
    s.store_location,
    s.verification_status,
    s.verified_at,
    s.verified_by,
    s.created_at,
    (SELECT COUNT(*) FROM products p WHERE p.supplier_id = s.supplier_id AND p.is_active = 1) AS active_products_count
FROM suppliers s;

-- WHY: Updates v_product_catalog to enforce seller verification filter and expose accessibility alt_text (FR-15, FR-18, AC-06.2, AR-06).
CREATE OR REPLACE VIEW v_product_catalog AS
SELECT 
    p.product_id,
    p.name AS product_name,
    COALESCE(p.short_description, SUBSTRING(p.description, 1, 120)) AS short_description,
    p.description,
    p.price,
    p.stock_quantity,
    p.is_active,
    p.source_store,
    p.source_url,
    p.created_at,
    b.brand_id,
    COALESCE(b.name, 'Unbranded') AS brand_name,
    b.country AS brand_country,
    c.category_id,
    c.name AS category_name,
    c.slug AS category_slug,
    parent_c.category_id AS parent_category_id,
    parent_c.name AS parent_category_name,
    parent_c.slug AS parent_category_slug,
    CASE 
        WHEN parent_c.name IS NOT NULL THEN CONCAT(parent_c.name, ' > ', c.name)
        ELSE c.name
    END AS category_path,
    pi.image_id AS primary_image_id,
    COALESCE(pi.image_path, 'static/images/placeholder.svg') AS primary_image,
    COALESCE(pi.alt_text, CONCAT(p.name, ' product photo')) AS primary_image_alt,
    COALESCE(r.avg_rating, 0.0) AS avg_rating,
    COALESCE(r.review_count, 0) AS review_count,
    s.supplier_id AS seller_id,
    s.name AS seller_name,
    COALESCE(s.verification_status, 'verified') AS seller_verification_status
FROM products p
LEFT JOIN brands b ON p.brand_id = b.brand_id
JOIN categories c ON p.category_id = c.category_id
LEFT JOIN categories parent_c ON c.parent_category_id = parent_c.category_id
LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
LEFT JOIN product_images pi ON p.product_id = pi.product_id AND pi.is_primary = 1
LEFT JOIN (
    SELECT 
        product_id, 
        ROUND(AVG(rating), 1) AS avg_rating,
        COUNT(*) AS review_count
    FROM reviews
    GROUP BY product_id
) r ON p.product_id = r.product_id
WHERE COALESCE(s.verification_status, 'verified') = 'verified';


-- ----------------------------------------------------------------------------
-- SECTION 5: STORED PROCEDURES (PRICING, CART MERGE, CHECKOUT PIPELINE)
-- ----------------------------------------------------------------------------

-- WHY: Stored procedure sp_cart_summary acts as the SINGLE SOURCE OF TRUTH for pricing, tax, and delivery fee calculations (FR-01, FR-08, FR-09, NFR-06, AC-01.1).
DROP PROCEDURE IF EXISTS sp_cart_summary;
DELIMITER $$
CREATE PROCEDURE sp_cart_summary(
    IN p_cart_id INT,
    IN p_province VARCHAR(50),
    IN p_city VARCHAR(50),
    OUT p_subtotal DECIMAL(10,2),
    OUT p_tax_amount DECIMAL(10,2),
    OUT p_delivery_fee DECIMAL(10,2),
    OUT p_total_amount DECIMAL(10,2),
    OUT p_min_days INT,
    OUT p_max_days INT
)
BEGIN
    DECLARE v_tax_rate DECIMAL(5,2) DEFAULT 5.00;
    DECLARE v_fee DECIMAL(10,2) DEFAULT 250.00;
    DECLARE v_min INT DEFAULT 2;
    DECLARE v_max INT DEFAULT 5;

    -- 1. Calculate raw merchandise subtotal
    SELECT COALESCE(SUM(ci.quantity * p.price), 0.00)
    INTO p_subtotal
    FROM cart_items ci
    JOIN products p ON ci.product_id = p.product_id
    WHERE ci.cart_id = p_cart_id;

    -- If cart is empty, totals are zero
    IF p_subtotal = 0.00 THEN
        SET p_tax_amount = 0.00;
        SET p_delivery_fee = 0.00;
        SET p_total_amount = 0.00;
        SET p_min_days = 0;
        SET p_max_days = 0;
    ELSE
        -- 2. Lookup delivery fee and delivery days from delivery_rates matrix
        -- Match exact city + province first
        SELECT fee, min_days, max_days 
        INTO v_fee, v_min, v_max
        FROM delivery_rates
        WHERE is_active = 1 
          AND LOWER(province) = LOWER(p_province) 
          AND LOWER(city) = LOWER(p_city)
        LIMIT 1;

        -- If no city-specific match, match province default
        IF v_fee IS NULL OR v_fee = 250.00 THEN
            SELECT fee, min_days, max_days 
            INTO v_fee, v_min, v_max
            FROM delivery_rates
            WHERE is_active = 1 
              AND LOWER(province) = LOWER(p_province) 
              AND city IS NULL
            LIMIT 1;
        END IF;

        -- Fallback to standard delivery if unmatched
        IF v_fee IS NULL THEN
            SET v_fee = 250.00;
            SET v_min = 3;
            SET v_max = 5;
        END IF;

        SET p_delivery_fee = v_fee;
        SET p_min_days = v_min;
        SET p_max_days = v_max;

        -- 3. Lookup province sales tax rate
        SELECT rate_percentage 
        INTO v_tax_rate
        FROM tax_rates
        WHERE is_active = 1 AND LOWER(province) = LOWER(p_province)
        LIMIT 1;

        IF v_tax_rate IS NULL THEN
            SET v_tax_rate = 5.00;
        END IF;

        -- Calculate tax on subtotal (standard 5% GST or provincial rate)
        SET p_tax_amount = ROUND(p_subtotal * (v_tax_rate / 100.0), 2);

        -- Total amount = Subtotal + Tax + Delivery Fee
        SET p_total_amount = p_subtotal + p_tax_amount + p_delivery_fee;
    END IF;

    -- Return summary result set for direct SELECT callers
    SELECT 
        p_subtotal AS subtotal,
        p_tax_amount AS tax_amount,
        p_delivery_fee AS delivery_fee,
        p_total_amount AS total_amount,
        p_min_days AS min_days,
        p_max_days AS max_days;
END$$
DELIMITER ;

-- WHY: Merges anonymous guest cart items into a registered customer's active cart upon login (FR-03, AC-08.2).
DROP PROCEDURE IF EXISTS sp_merge_carts;
DELIMITER $$
CREATE PROCEDURE sp_merge_carts(
    IN p_session_token VARCHAR(64),
    IN p_user_id INT,
    OUT p_merged_items_count INT
)
proc_body: BEGIN
    DECLARE v_guest_cart_id INT DEFAULT NULL;
    DECLARE v_user_cart_id INT DEFAULT NULL;

    SET p_merged_items_count = 0;

    -- Find active guest cart by token
    SELECT cart_id INTO v_guest_cart_id
    FROM carts
    WHERE session_token = p_session_token AND status = 'active'
    ORDER BY updated_at DESC
    LIMIT 1;

    -- If no guest cart or empty, exit
    IF v_guest_cart_id IS NULL THEN
        LEAVE proc_body;
    END IF;

    -- Find customer active cart
    SELECT cart_id INTO v_user_cart_id
    FROM carts
    WHERE user_id = p_user_id AND status = 'active'
    ORDER BY updated_at DESC
    LIMIT 1;

    -- If customer has no active cart, convert guest cart to user cart directly
    IF v_user_cart_id IS NULL THEN
        UPDATE carts 
        SET user_id = p_user_id, session_token = NULL, updated_at = NOW() 
        WHERE cart_id = v_guest_cart_id;

        SELECT COUNT(*) INTO p_merged_items_count 
        FROM cart_items WHERE cart_id = v_guest_cart_id;
    ELSE
        -- Merge guest items into existing user cart
        INSERT INTO cart_items (cart_id, product_id, quantity)
        SELECT v_user_cart_id, gci.product_id, gci.quantity
        FROM cart_items gci
        WHERE gci.cart_id = v_guest_cart_id
        ON DUPLICATE KEY UPDATE quantity = cart_items.quantity + VALUES(quantity);

        SELECT COUNT(*) INTO p_merged_items_count 
        FROM cart_items WHERE cart_id = v_guest_cart_id;

        -- Clean up guest cart
        DELETE FROM cart_items WHERE cart_id = v_guest_cart_id;
        UPDATE carts SET status = 'converted', session_token = NULL WHERE cart_id = v_guest_cart_id;
    END IF;
END proc_body$$
DELIMITER ;

-- WHY: Enhanced sp_place_order calculates subtotal, tax, delivery fee, captures address snapshot, and logs payment attempt (FR-01, FR-08, FR-10, FR-13, NFR-06).
DROP PROCEDURE IF EXISTS sp_place_order;
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
    DECLARE v_subtotal DECIMAL(10,2) DEFAULT 0.00;
    DECLARE v_tax DECIMAL(10,2) DEFAULT 0.00;
    DECLARE v_fee DECIMAL(10,2) DEFAULT 0.00;
    DECLARE v_total DECIMAL(10,2) DEFAULT 0.00;
    DECLARE v_min_days INT DEFAULT 2;
    DECLARE v_max_days INT DEFAULT 5;
    DECLARE v_expected_date DATE DEFAULT NULL;
    DECLARE v_addr_snapshot TEXT DEFAULT NULL;
    DECLARE v_province VARCHAR(50) DEFAULT 'Sindh';
    DECLARE v_city VARCHAR(50) DEFAULT 'Karachi';
    DECLARE v_new_order_id INT DEFAULT NULL;
    DECLARE v_err_msg VARCHAR(255) DEFAULT '';

    -- Exception handler rolls back transaction and retains cart in active state (FR-04, NFR-04)
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 v_err_msg = MESSAGE_TEXT;
        ROLLBACK;
        DROP TEMPORARY TABLE IF EXISTS _temp_checkout_items;
        SET p_order_id = NULL;
        SET p_status_message = CONCAT('FAILED: ', COALESCE(v_err_msg, 'Transaction aborted due to error'));
    END;

    -- Validate payment method
    IF p_payment_method NOT IN ('cod', 'card', 'bank_transfer', 'wallet', 'simulated') THEN
        SET p_order_id = NULL;
        SET p_status_message = 'FAILED: Invalid payment method.';
        LEAVE proc_body;
    END IF;

    -- Validate delivery address
    SELECT 
        CONCAT(line1, ', ', city, ', ', province, IF(postal_code IS NOT NULL, CONCAT(' ', postal_code), '')),
        province,
        city
    INTO v_addr_snapshot, v_province, v_city
    FROM addresses 
    WHERE address_id = p_address_id AND user_id = p_user_id;

    IF v_addr_snapshot IS NULL THEN
        SET p_order_id = NULL;
        SET p_status_message = 'FAILED: Delivery address does not belong to this user.';
        LEAVE proc_body;
    END IF;

    -- Find active cart
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

    -- Calculate financial breakdown using sp_cart_summary rules
    CALL sp_cart_summary(v_cart_id, v_province, v_city, v_subtotal, v_tax, v_fee, v_total, v_min_days, v_max_days);

    IF v_subtotal = 0.00 THEN
        SET p_order_id = NULL;
        SET p_status_message = 'FAILED: Shopping cart is empty.';
        LEAVE proc_body;
    END IF;

    SET v_expected_date = DATE_ADD(CURDATE(), INTERVAL v_max_days DAY);

    -- Stage checkout items into temporary table
    DROP TEMPORARY TABLE IF EXISTS _temp_checkout_items;
    CREATE TEMPORARY TABLE _temp_checkout_items AS
    SELECT ci.product_id, ci.quantity, p.price
    FROM cart_items ci
    JOIN products p ON ci.product_id = p.product_id
    WHERE ci.cart_id = v_cart_id;

    -- Begin atomic transaction (NFR-04)
    START TRANSACTION;

    -- 1. Insert order with full financial breakdown and address snapshot (FR-01, FR-13)
    INSERT INTO orders (
        user_id, address_id, order_date, subtotal, tax_amount, delivery_fee, 
        expected_delivery_date, status, total_amount, shipping_address_snapshot, consent_terms_at
    )
    VALUES (
        p_user_id, p_address_id, NOW(), v_subtotal, v_tax, v_fee, 
        v_expected_date, 'pending', v_total, v_addr_snapshot, NOW()
    );

    SET v_new_order_id = LAST_INSERT_ID();

    -- 2. Insert order items (BEFORE INSERT trigger verifies stock; AFTER INSERT trigger deducts stock)
    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
    SELECT v_new_order_id, product_id, quantity, price
    FROM _temp_checkout_items;

    DROP TEMPORARY TABLE IF EXISTS _temp_checkout_items;

    -- 3. Create payment record
    INSERT INTO payments (order_id, method, amount, status, paid_at)
    VALUES (
        v_new_order_id,
        p_payment_method,
        v_total,
        IF(p_payment_method = 'cod', 'pending', 'completed'),
        IF(p_payment_method = 'cod', NULL, NOW())
    );

    -- 4. Log payment attempt (FR-10, AC-02.2)
    INSERT INTO payment_attempts (order_id, payment_method, amount, status, transaction_ref, failure_reason)
    VALUES (
        v_new_order_id,
        p_payment_method,
        v_total,
        IF(p_payment_method = 'cod', 'pending', 'successful'),
        CONCAT('TXN-', UNIX_TIMESTAMP(), '-', v_new_order_id),
        NULL
    );

    -- 5. Update order status if immediate digital payment
    IF p_payment_method <> 'cod' THEN
        UPDATE orders SET status = 'paid' WHERE order_id = v_new_order_id;
    END IF;

    -- 6. Mark cart as converted ONLY after successful order and payment creation (FR-04)
    UPDATE carts SET status = 'converted' WHERE cart_id = v_cart_id;

    -- Commit atomic unit of work
    COMMIT;

    SET p_order_id = v_new_order_id;
    SET p_status_message = 'SUCCESS: Order placed successfully.';
END proc_body$$
DELIMITER ;

-- WHY: Stored procedure for guest checkout placing orders without requiring an account (FR-02, AC-03.1).
DROP PROCEDURE IF EXISTS sp_place_guest_order;
DELIMITER $$
CREATE PROCEDURE sp_place_guest_order(
    IN p_session_token VARCHAR(64),
    IN p_guest_name VARCHAR(100),
    IN p_guest_email VARCHAR(100),
    IN p_guest_phone VARCHAR(20),
    IN p_guest_address VARCHAR(255),
    IN p_guest_city VARCHAR(50),
    IN p_guest_province VARCHAR(50),
    IN p_payment_method VARCHAR(20),
    OUT p_order_id INT,
    OUT p_status_message VARCHAR(255)
)
proc_body: BEGIN
    DECLARE v_cart_id INT DEFAULT NULL;
    DECLARE v_subtotal DECIMAL(10,2) DEFAULT 0.00;
    DECLARE v_tax DECIMAL(10,2) DEFAULT 0.00;
    DECLARE v_fee DECIMAL(10,2) DEFAULT 0.00;
    DECLARE v_total DECIMAL(10,2) DEFAULT 0.00;
    DECLARE v_min_days INT DEFAULT 2;
    DECLARE v_max_days INT DEFAULT 5;
    DECLARE v_expected_date DATE DEFAULT NULL;
    DECLARE v_addr_snapshot TEXT DEFAULT NULL;
    DECLARE v_new_order_id INT DEFAULT NULL;
    DECLARE v_err_msg VARCHAR(255) DEFAULT '';

    -- Exception handler rolls back transaction and preserves guest cart (FR-04)
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 v_err_msg = MESSAGE_TEXT;
        ROLLBACK;
        DROP TEMPORARY TABLE IF EXISTS _temp_guest_checkout_items;
        SET p_order_id = NULL;
        SET p_status_message = CONCAT('FAILED: ', COALESCE(v_err_msg, 'Guest checkout transaction aborted'));
    END;

    -- Validate payment method
    IF p_payment_method NOT IN ('cod', 'card', 'bank_transfer', 'wallet', 'simulated') THEN
        SET p_order_id = NULL;
        SET p_status_message = 'FAILED: Invalid payment method.';
        LEAVE proc_body;
    END IF;

    -- Validate guest cart
    SELECT cart_id INTO v_cart_id
    FROM carts
    WHERE session_token = p_session_token AND status = 'active'
    ORDER BY updated_at DESC
    LIMIT 1;

    IF v_cart_id IS NULL THEN
        SET p_order_id = NULL;
        SET p_status_message = 'FAILED: No active guest cart found.';
        LEAVE proc_body;
    END IF;

    -- Calculate financial breakdown
    CALL sp_cart_summary(v_cart_id, p_guest_province, p_guest_city, v_subtotal, v_tax, v_fee, v_total, v_min_days, v_max_days);

    IF v_subtotal = 0.00 THEN
        SET p_order_id = NULL;
        SET p_status_message = 'FAILED: Guest cart is empty.';
        LEAVE proc_body;
    END IF;

    SET v_expected_date = DATE_ADD(CURDATE(), INTERVAL v_max_days DAY);
    SET v_addr_snapshot = CONCAT(p_guest_name, ' (Guest), ', p_guest_phone, ', ', p_guest_address, ', ', p_guest_city, ', ', p_guest_province);

    -- Stage items
    DROP TEMPORARY TABLE IF EXISTS _temp_guest_checkout_items;
    CREATE TEMPORARY TABLE _temp_guest_checkout_items AS
    SELECT ci.product_id, ci.quantity, p.price
    FROM cart_items ci
    JOIN products p ON ci.product_id = p.product_id
    WHERE ci.cart_id = v_cart_id;

    -- Begin transaction
    START TRANSACTION;

    -- 1. Insert guest order (user_id IS NULL)
    INSERT INTO orders (
        user_id, address_id, order_date, subtotal, tax_amount, delivery_fee, 
        expected_delivery_date, status, total_amount, 
        guest_name, guest_email, guest_phone, guest_address_line1, guest_city, guest_province,
        shipping_address_snapshot, consent_terms_at
    )
    VALUES (
        NULL, NULL, NOW(), v_subtotal, v_tax, v_fee, 
        v_expected_date, 'pending', v_total,
        p_guest_name, p_guest_email, p_guest_phone, p_guest_address, p_guest_city, p_guest_province,
        v_addr_snapshot, NOW()
    );

    SET v_new_order_id = LAST_INSERT_ID();

    -- 2. Insert order items
    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
    SELECT v_new_order_id, product_id, quantity, price
    FROM _temp_guest_checkout_items;

    DROP TEMPORARY TABLE IF EXISTS _temp_guest_checkout_items;

    -- 3. Payment record
    INSERT INTO payments (order_id, method, amount, status, paid_at)
    VALUES (
        v_new_order_id,
        p_payment_method,
        v_total,
        IF(p_payment_method = 'cod', 'pending', 'completed'),
        IF(p_payment_method = 'cod', NULL, NOW())
    );

    -- 4. Payment attempt log
    INSERT INTO payment_attempts (order_id, payment_method, amount, status, transaction_ref, failure_reason)
    VALUES (
        v_new_order_id,
        p_payment_method,
        v_total,
        IF(p_payment_method = 'cod', 'pending', 'successful'),
        CONCAT('GST-', UNIX_TIMESTAMP(), '-', v_new_order_id),
        NULL
    );

    -- 5. Status update if paid digitally
    IF p_payment_method <> 'cod' THEN
        UPDATE orders SET status = 'paid' WHERE order_id = v_new_order_id;
    END IF;

    -- 6. Mark guest cart as converted
    UPDATE carts SET status = 'converted' WHERE cart_id = v_cart_id;

    COMMIT;

    SET p_order_id = v_new_order_id;
    SET p_status_message = 'SUCCESS: Guest order placed successfully.';
END proc_body$$
DELIMITER ;


-- ----------------------------------------------------------------------------
-- SECTION 6: MYSQL 8 ROLE-BASED ACCESS CONTROL (shop_seller)
-- ----------------------------------------------------------------------------

-- WHY: Introduces shop_seller role with least-privilege catalog and returns permissions (FR-18).
CREATE ROLE IF NOT EXISTS 'shop_seller';
GRANT SELECT ON online_shop_perfume_dev.categories TO 'shop_seller';
GRANT SELECT ON online_shop_perfume_dev.brands TO 'shop_seller';
GRANT SELECT ON online_shop_perfume_dev.delivery_rates TO 'shop_seller';
GRANT SELECT ON online_shop_perfume_dev.tax_rates TO 'shop_seller';
GRANT SELECT, INSERT, UPDATE ON online_shop_perfume_dev.products TO 'shop_seller';
GRANT SELECT, INSERT, UPDATE, DELETE ON online_shop_perfume_dev.product_images TO 'shop_seller';
GRANT SELECT, UPDATE ON online_shop_perfume_dev.return_requests TO 'shop_seller';
GRANT SELECT ON online_shop_perfume_dev.return_status_history TO 'shop_seller';
GRANT SELECT ON online_shop_perfume_dev.v_product_catalog TO 'shop_seller';
GRANT SELECT ON online_shop_perfume_dev.v_overdue_return_requests TO 'shop_seller';


-- ----------------------------------------------------------------------------
-- SECTION 7: SEED DATA & BACKFILL FOR NEW MATRICES & PROFILES
-- ----------------------------------------------------------------------------

-- 1. Seed delivery_rates matrix (FR-08, AC-04.1)
INSERT INTO delivery_rates (province, city, fee, min_days, max_days, is_active)
VALUES
    ('Sindh', 'Karachi', 150.00, 1, 3, 1),
    ('Sindh', 'Hyderabad', 150.00, 1, 2, 1),
    ('Sindh', 'Jamshoro', 100.00, 1, 2, 1),
    ('Sindh', NULL, 200.00, 2, 4, 1),
    ('Punjab', 'Lahore', 200.00, 2, 4, 1),
    ('Punjab', 'Rawalpindi', 200.00, 2, 4, 1),
    ('Punjab', 'Faisalabad', 200.00, 2, 4, 1),
    ('Punjab', NULL, 250.00, 3, 5, 1),
    ('Islamabad', 'Islamabad', 200.00, 2, 4, 1),
    ('Islamabad', NULL, 200.00, 2, 4, 1),
    ('Khyber Pakhtunkhwa', 'Peshawar', 250.00, 3, 5, 1),
    ('Khyber Pakhtunkhwa', NULL, 300.00, 3, 6, 1),
    ('Balochistan', 'Quetta', 250.00, 3, 6, 1),
    ('Balochistan', NULL, 350.00, 4, 7, 1)
ON DUPLICATE KEY UPDATE 
    fee = VALUES(fee), 
    min_days = VALUES(min_days), 
    max_days = VALUES(max_days), 
    is_active = VALUES(is_active);

-- 2. Seed tax_rates matrix (FR-09)
INSERT INTO tax_rates (province, rate_percentage, description, is_active)
VALUES
    ('Sindh', 5.00, 'Sindh Sales Tax / General Retail GST', 1),
    ('Punjab', 5.00, 'Punjab Sales Tax / General Retail GST', 1),
    ('Islamabad', 5.00, 'Federal Capital Retail GST', 1),
    ('Khyber Pakhtunkhwa', 5.00, 'KP Sales Tax / General Retail GST', 1),
    ('Balochistan', 5.00, 'Balochistan Sales Tax / Retail GST', 1)
ON DUPLICATE KEY UPDATE 
    rate_percentage = VALUES(rate_percentage),
    description = VALUES(description),
    is_active = VALUES(is_active);

-- 3. Seed payment_methods (FR-06, AC-02.1)
INSERT INTO payment_methods (code, name, description, is_enabled)
VALUES
    ('cod', 'Cash on Delivery', 'Pay with physical cash upon courier parcel arrival', 1),
    ('simulated', 'Simulated Card / Wallet Gateway', 'Test gateway sandbox with immediate success/failure states', 1)
ON DUPLICATE KEY UPDATE 
    name = VALUES(name),
    description = VALUES(description),
    is_enabled = VALUES(is_enabled);

-- 4. Backfill existing suppliers into verified sellers (FR-17, FR-18)
UPDATE suppliers 
SET 
    business_name = COALESCE(business_name, name),
    contact_name = COALESCE(contact_name, name),
    address = COALESCE(address, 'Main Commercial District, Saddar'),
    city = COALESCE(city, 'Karachi'),
    store_location = COALESCE(store_location, 'Flagship Outlet'),
    verification_status = 'verified',
    verified_at = COALESCE(verified_at, NOW()),
    verified_by = COALESCE(verified_by, 'admin_bootstrap')
WHERE verification_status IS NULL OR verification_status = 'pending';

-- 5. Backfill accessibility alt_text on existing product_images (FR-15, AR-06)
UPDATE product_images pi
JOIN products p ON pi.product_id = p.product_id
SET pi.alt_text = CONCAT(p.name, ' - Official Product Image')
WHERE pi.alt_text IS NULL OR pi.alt_text = '';

-- 6. Backfill orders financial breakdown for historic records where subtotal is 0
UPDATE orders 
SET 
    subtotal = total_amount,
    tax_amount = 0.00,
    delivery_fee = 0.00
WHERE subtotal = 0.00 AND total_amount > 0.00;

