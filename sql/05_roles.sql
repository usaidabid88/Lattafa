-- ============================================================================
-- Script: 05_roles.sql
-- Description: MySQL 8 Role-Based Access Control (RBAC) & Principle of Least Privilege
-- Database Engine: MySQL 8.0
--
-- Re-runnable: Can be executed multiple times safely.
-- Module Ownership:
--   Member A: RBAC architecture, roles definition, user creation, privilege grants
-- ============================================================================

USE online_shop;

-- Drop existing test users if they exist
DROP USER IF EXISTS 'test_admin'@'localhost';
DROP USER IF EXISTS 'test_staff'@'localhost';
DROP USER IF EXISTS 'test_customer'@'localhost';

-- Drop existing roles if they exist
DROP ROLE IF EXISTS 'shop_admin';
DROP ROLE IF EXISTS 'shop_staff';
DROP ROLE IF EXISTS 'shop_customer';


-- ============================================================================
-- SECTION 1: ROLE DEFINITIONS
-- ============================================================================

-- Role 1: shop_admin
-- WHY: Represents the database and store superadministrator. Possesses complete
--      administrative command over schema objects, configurations, and all records.
CREATE ROLE 'shop_admin';
GRANT ALL PRIVILEGES ON online_shop.* TO 'shop_admin';


-- Role 2: shop_staff
-- WHY: Warehouse and customer support personnel. Needs read access to orders and
--      inventory, and restricted write access to update delivery statuses and
--      replenish product stock. Strictly denied DROP/ALTER and DELETE on users.
CREATE ROLE 'shop_staff';
GRANT SELECT ON online_shop.* TO 'shop_staff';
GRANT UPDATE (stock_quantity) ON online_shop.products TO 'shop_staff';
GRANT UPDATE (status) ON online_shop.orders TO 'shop_staff';
GRANT UPDATE (courier, tracking_number, shipped_at, delivered_at) ON online_shop.shipments TO 'shop_staff';
GRANT EXECUTE ON online_shop.* TO 'shop_staff';


-- Role 3: shop_customer
-- WHY: Implements the Principle of Least Privilege for end-users. Customers can
--      read public storefront data (products, categories, reviews, bestsellers)
--      and manage their personal session carts/addresses. Crucially, they are
--      DENIED read access to table `users` to prevent credential scraping or
--      data leaks, and DENIED DELETE permissions on catalog or financial tables.
CREATE ROLE 'shop_customer';
GRANT SELECT ON online_shop.products TO 'shop_customer';
GRANT SELECT ON online_shop.categories TO 'shop_customer';
GRANT SELECT ON online_shop.reviews TO 'shop_customer';
GRANT SELECT ON online_shop.v_best_sellers TO 'shop_customer';
GRANT SELECT, INSERT, UPDATE, DELETE ON online_shop.carts TO 'shop_customer';
GRANT SELECT, INSERT, UPDATE, DELETE ON online_shop.cart_items TO 'shop_customer';
GRANT SELECT, INSERT, UPDATE, DELETE ON online_shop.addresses TO 'shop_customer';
GRANT EXECUTE ON PROCEDURE online_shop.sp_place_order TO 'shop_customer';


-- ============================================================================
-- SECTION 2: TEST USERS & ROLE ASSIGNMENTS
-- ============================================================================

-- Create test accounts for demonstration and automated testing
CREATE USER 'test_admin'@'localhost' IDENTIFIED BY 'AdminPass123!';
CREATE USER 'test_staff'@'localhost' IDENTIFIED BY 'StaffPass123!';
CREATE USER 'test_customer'@'localhost' IDENTIFIED BY 'CustomerPass123!';

-- Grant roles to respective test accounts
GRANT 'shop_admin' TO 'test_admin'@'localhost';
GRANT 'shop_staff' TO 'test_staff'@'localhost';
GRANT 'shop_customer' TO 'test_customer'@'localhost';

-- Set default roles active upon initial authentication (MySQL 8 requirement)
SET DEFAULT ROLE 'shop_admin' TO 'test_admin'@'localhost';
SET DEFAULT ROLE 'shop_staff' TO 'test_staff'@'localhost';
SET DEFAULT ROLE 'shop_customer' TO 'test_customer'@'localhost';

FLUSH PRIVILEGES;
