"""
Reconciles database/init_perfume/02_sample_data.sql and 06_catalog_expansion.sql
(and seeds/ counterparts) to eliminate obsolete marketplace data and align with
the authentic Arabian Perfume catalog (Lattafa, Lattafa Pride, Maison Alhambra).
"""

import os

NEW_SAMPLE_DATA_SQL = '''-- ============================================================================
-- Script: 02_sample_data.sql
-- Description: Authentic Arabian Perfume Store Seed Data
-- Target: online_shop_perfume_dev and online_shop_perfume_test
-- All prices in PKR. Authentic perfume categories, suppliers, and customer orders.
-- All user passwords are: password123
-- ============================================================================
USE online_shop_perfume_dev;
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE shipments;
TRUNCATE TABLE payments;
TRUNCATE TABLE order_items;
TRUNCATE TABLE orders;
TRUNCATE TABLE cart_items;
TRUNCATE TABLE carts;
TRUNCATE TABLE reviews;
TRUNCATE TABLE products;
TRUNCATE TABLE suppliers;
TRUNCATE TABLE categories;
TRUNCATE TABLE audit_log;
TRUNCATE TABLE addresses;
TRUNCATE TABLE users;

-- Categories (Fragrance Department Hierarchy)
INSERT INTO categories (category_id, name, parent_category_id) VALUES (100, 'Fragrances', NULL);
INSERT INTO categories (category_id, name, parent_category_id) VALUES (101, 'Men\\'s Fragrances', 100);
INSERT INTO categories (category_id, name, parent_category_id) VALUES (102, 'Women\\'s Fragrances', 100);
INSERT INTO categories (category_id, name, parent_category_id) VALUES (103, 'Unisex Fragrances', 100);
INSERT INTO categories (category_id, name, parent_category_id) VALUES (104, 'Eau de Parfum', 100);
INSERT INTO categories (category_id, name, parent_category_id) VALUES (105, 'Extrait de Parfum', 100);
INSERT INTO categories (category_id, name, parent_category_id) VALUES (106, 'Perfume Oils & Attars', 100);
INSERT INTO categories (category_id, name, parent_category_id) VALUES (107, 'Gift Sets & Collections', 100);

-- Suppliers (Authorized UAE Distributors)
INSERT INTO suppliers (supplier_id, name, email, phone) VALUES (101, 'Lattafa Perfumes Industries L.L.C.', 'distribution@lattafa.ae', '+971-4-885-7800');
INSERT INTO suppliers (supplier_id, name, email, phone) VALUES (102, 'Al Fakhr Fragrances Trading', 'sales@alfakhrfragrances.com', '+971-4-226-5599');

-- Users (Password for all accounts is: password123)
INSERT INTO users (user_id, full_name, email, password_hash, phone, role) VALUES (1, 'Ali Raza', 'admin@muetshop.pk', 'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03', '03001234567', 'admin');
INSERT INTO users (user_id, full_name, email, password_hash, phone, role) VALUES (2, 'Aisha Ashfaque', 'aisha.ashfaque@muet.edu.pk', 'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03', '03129876543', 'admin');
INSERT INTO users (user_id, full_name, email, password_hash, phone, role) VALUES (3, 'Bilal Tariq', 'bilal.staff@muetshop.pk', 'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03', '03332145678', 'staff');
INSERT INTO users (user_id, full_name, email, password_hash, phone, role) VALUES (4, 'Sana Mir', 'sana.staff@muetshop.pk', 'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03', '03456789012', 'staff');
INSERT INTO users (user_id, full_name, email, password_hash, phone, role) VALUES (5, 'Zeeshan Ahmed', 'zeeshan@gmail.com', 'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03', '03012345678', 'customer');
INSERT INTO users (user_id, full_name, email, password_hash, phone, role) VALUES (6, 'Fatima Noor', 'fatima.noor@yahoo.com', 'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03', '03134567890', 'customer');
INSERT INTO users (user_id, full_name, email, password_hash, phone, role) VALUES (7, 'Hamza Khan', 'hamza.khan@gmail.com', 'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03', '03217654321', 'customer');
INSERT INTO users (user_id, full_name, email, password_hash, phone, role) VALUES (8, 'Areeba Sheikh', 'areeba.s@outlook.com', 'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03', '03348901234', 'customer');
INSERT INTO users (user_id, full_name, email, password_hash, phone, role) VALUES (9, 'Usman Ghani', 'usman.ghani@gmail.com', 'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03', '03461239876', 'customer');
INSERT INTO users (user_id, full_name, email, password_hash, phone, role) VALUES (10, 'Hira Mani', 'hira.mani@gmail.com', 'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03', '03023456789', 'customer');
INSERT INTO users (user_id, full_name, email, password_hash, phone, role) VALUES (11, 'Daniyal Tariq', 'daniyal.tariq@gmail.com', 'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03', '03145678901', 'customer');
INSERT INTO users (user_id, full_name, email, password_hash, phone, role) VALUES (12, 'Mahnoor Baloch', 'mahnoor.b@gmail.com', 'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03', '03226789012', 'customer');
INSERT INTO users (user_id, full_name, email, password_hash, phone, role) VALUES (13, 'Tariq Mehmood', 'tariq.m@gmail.com', 'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03', '03357890123', 'customer');
INSERT INTO users (user_id, full_name, email, password_hash, phone, role) VALUES (14, 'Zainab Abbas', 'zainab.a@gmail.com', 'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03', '03478901234', 'customer');
INSERT INTO users (user_id, full_name, email, password_hash, phone, role) VALUES (15, 'Shahmeer Ali', 'shahmeer.ali@gmail.com', 'pbkdf2:sha256:600000$E9sgUUnBfGEllYfS$f93a42d503076ed8a159e13dfecbd06322feb8fcfb819d98f4c457cf1a5b2c03', '03039012345', 'customer');

-- Addresses (20 addresses across Pakistani cities)
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (1, 5, 'House 45-B, Block 6, PECHS', 'Karachi', 'Sindh', '75400', 1);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (2, 5, 'Office 302, Business Avenue, Shahrah-e-Faisal', 'Karachi', 'Sindh', '75350', 0);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (3, 6, 'Flat 12, Gulshan-e-Iqbal Block 13-D', 'Karachi', 'Sindh', '75300', 1);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (4, 7, 'Bungalow 18, Citizen Colony', 'Hyderabad', 'Sindh', '71000', 1);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (5, 7, 'MUET Staff Colony, House 7', 'Jamshoro', 'Sindh', '76062', 0);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (6, 8, 'House 88, Defence Phase 5', 'Lahore', 'Punjab', '54000', 1);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (7, 8, 'Plaza 4, Gulberg III', 'Lahore', 'Punjab', '54660', 0);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (8, 9, 'Street 9, F-7/2', 'Islamabad', 'Federal', '44000', 1);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (9, 10, 'Flat 401, Clifton Block 2', 'Karachi', 'Sindh', '75600', 1);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (10, 10, 'House 22, Saddar', 'Hyderabad', 'Sindh', '71000', 0);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (11, 11, 'Plot 104, Model Town', 'Lahore', 'Punjab', '54700', 1);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (12, 12, 'House 55, Latifabad Unit 7', 'Hyderabad', 'Sindh', '71800', 1);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (13, 12, 'Girls Hostel 3, MUET Campus', 'Jamshoro', 'Sindh', '76062', 0);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (14, 13, 'House 14, Chaklala Scheme 3', 'Rawalpindi', 'Punjab', '46000', 1);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (15, 14, 'Street 15, G-11/3', 'Islamabad', 'Federal', '44000', 1);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (16, 14, 'Blue Area, Office 12', 'Islamabad', 'Federal', '44000', 0);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (17, 15, 'Bungalow 67, Qasimabad Phase 1', 'Hyderabad', 'Sindh', '71000', 1);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (18, 5, 'Plot 88, Korangi Industrial Area', 'Karachi', 'Sindh', '74900', 0);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (19, 6, 'North Nazimabad Block H', 'Karachi', 'Sindh', '74700', 0);
INSERT INTO addresses (address_id, user_id, line1, city, province, postal_code, is_default) VALUES (20, 11, 'DHA Phase 6, Street 12', 'Lahore', 'Punjab', '54792', 0);

-- Carts (active, converted, and abandoned carts for testing)
INSERT INTO carts (cart_id, user_id, status, created_at, updated_at) VALUES (1, 5, 'active', NOW(), NOW());
INSERT INTO carts (cart_id, user_id, status, created_at, updated_at) VALUES (2, 8, 'active', NOW(), NOW());
INSERT INTO carts (cart_id, user_id, status, created_at, updated_at) VALUES (3, 11, 'abandoned', DATE_SUB(NOW(), INTERVAL 14 DAY), DATE_SUB(NOW(), INTERVAL 10 DAY));
INSERT INTO carts (cart_id, user_id, status, created_at, updated_at) VALUES (4, 14, 'abandoned', DATE_SUB(NOW(), INTERVAL 20 DAY), DATE_SUB(NOW(), INTERVAL 12 DAY));
INSERT INTO carts (cart_id, user_id, status, created_at, updated_at) VALUES (5, 7, 'converted', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY));

-- Cart Items (referencing authentic perfume catalog IDs)
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (1, 102, 1);
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (1, 125, 2);
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (2, 116, 1);
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (3, 101, 1);
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (3, 110, 1);
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (4, 120, 1);
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (5, 112, 2);

-- Orders (25 orders: delivered, shipped, paid, pending, cancelled)
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (1, 5, 1, DATE_SUB(NOW(), INTERVAL 45 DAY), 'delivered', 19479.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (2, 6, 3, DATE_SUB(NOW(), INTERVAL 42 DAY), 'delivered', 15900.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (3, 7, 4, DATE_SUB(NOW(), INTERVAL 38 DAY), 'delivered', 83998.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (4, 8, 6, DATE_SUB(NOW(), INTERVAL 35 DAY), 'delivered', 11550.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (5, 9, 8, DATE_SUB(NOW(), INTERVAL 30 DAY), 'delivered', 32300.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (6, 10, 9, DATE_SUB(NOW(), INTERVAL 28 DAY), 'delivered', 24500.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (7, 11, 11, DATE_SUB(NOW(), INTERVAL 26 DAY), 'delivered', 38000.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (8, 12, 12, DATE_SUB(NOW(), INTERVAL 24 DAY), 'delivered', 16950.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (9, 13, 14, DATE_SUB(NOW(), INTERVAL 22 DAY), 'delivered', 26700.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (10, 14, 15, DATE_SUB(NOW(), INTERVAL 20 DAY), 'delivered', 19500.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (11, 15, 17, DATE_SUB(NOW(), INTERVAL 18 DAY), 'delivered', 165000.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (12, 5, 2, DATE_SUB(NOW(), INTERVAL 16 DAY), 'delivered', 35600.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (13, 6, 19, DATE_SUB(NOW(), INTERVAL 15 DAY), 'delivered', 9600.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (14, 7, 5, DATE_SUB(NOW(), INTERVAL 14 DAY), 'delivered', 16780.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (15, 8, 7, DATE_SUB(NOW(), INTERVAL 12 DAY), 'delivered', 11800.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (16, 9, 8, DATE_SUB(NOW(), INTERVAL 10 DAY), 'delivered', 57000.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (17, 10, 10, DATE_SUB(NOW(), INTERVAL 7 DAY), 'shipped', 32900.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (18, 11, 20, DATE_SUB(NOW(), INTERVAL 6 DAY), 'shipped', 69999.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (19, 12, 13, DATE_SUB(NOW(), INTERVAL 5 DAY), 'shipped', 10900.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (20, 13, 14, DATE_SUB(NOW(), INTERVAL 4 DAY), 'paid', 10780.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (21, 14, 16, DATE_SUB(NOW(), INTERVAL 3 DAY), 'paid', 12998.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (22, 15, 17, DATE_SUB(NOW(), INTERVAL 2 DAY), 'paid', 23499.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (23, 5, 1, DATE_SUB(NOW(), INTERVAL 1 DAY), 'pending', 49999.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (24, 7, 4, DATE_SUB(NOW(), INTERVAL 1 DAY), 'pending', 11590.00);
INSERT INTO orders (order_id, user_id, address_id, order_date, status, total_amount) VALUES (25, 8, 6, DATE_SUB(NOW(), INTERVAL 8 DAY), 'cancelled', 135000.00);

-- Order Items (exact subtotals matching genuine perfume catalog items)
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (1, 112, 2, 6490.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (1, 125, 1, 6499.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (2, 116, 2, 7950.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (3, 102, 1, 69999.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (3, 126, 1, 13999.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (4, 117, 3, 3850.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (5, 120, 1, 26500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (5, 122, 1, 5800.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (6, 118, 1, 24500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (7, 110, 1, 28500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (7, 127, 1, 9500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (8, 116, 1, 7950.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (8, 119, 2, 4500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (9, 113, 1, 18500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (9, 128, 1, 8200.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (10, 121, 1, 19500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (11, 107, 1, 165000.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (12, 122, 2, 5800.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (12, 123, 1, 24000.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (13, 129, 3, 3200.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (14, 114, 2, 4290.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (14, 128, 1, 8200.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (15, 116, 1, 7950.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (15, 117, 1, 3850.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (16, 110, 2, 28500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (17, 123, 1, 24000.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (17, 124, 1, 8900.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (18, 102, 1, 69999.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (19, 117, 2, 3850.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (19, 129, 1, 3200.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (20, 112, 1, 6490.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (20, 114, 1, 4290.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (21, 125, 2, 6499.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (22, 126, 1, 13999.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (22, 127, 1, 9500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (23, 103, 1, 49999.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (24, 115, 1, 5100.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (24, 112, 1, 6490.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (25, 108, 1, 135000.00);

-- Payments (1:1 with orders)
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (1, 1, 'card', 19479.00, 'completed', DATE_SUB(NOW(), INTERVAL 45 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (2, 2, 'bank_transfer', 15900.00, 'completed', DATE_SUB(NOW(), INTERVAL 42 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (3, 3, 'wallet', 83998.00, 'completed', DATE_SUB(NOW(), INTERVAL 38 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (4, 4, 'cod', 11550.00, 'completed', DATE_SUB(NOW(), INTERVAL 35 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (5, 5, 'card', 32300.00, 'completed', DATE_SUB(NOW(), INTERVAL 30 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (6, 6, 'bank_transfer', 24500.00, 'completed', DATE_SUB(NOW(), INTERVAL 28 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (7, 7, 'wallet', 38000.00, 'completed', DATE_SUB(NOW(), INTERVAL 26 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (8, 8, 'cod', 16950.00, 'completed', DATE_SUB(NOW(), INTERVAL 24 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (9, 9, 'card', 26700.00, 'completed', DATE_SUB(NOW(), INTERVAL 22 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (10, 10, 'bank_transfer', 19500.00, 'completed', DATE_SUB(NOW(), INTERVAL 20 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (11, 11, 'wallet', 165000.00, 'completed', DATE_SUB(NOW(), INTERVAL 18 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (12, 12, 'cod', 35600.00, 'completed', DATE_SUB(NOW(), INTERVAL 16 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (13, 13, 'card', 9600.00, 'completed', DATE_SUB(NOW(), INTERVAL 15 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (14, 14, 'bank_transfer', 16780.00, 'completed', DATE_SUB(NOW(), INTERVAL 14 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (15, 15, 'wallet', 11800.00, 'completed', DATE_SUB(NOW(), INTERVAL 12 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (16, 16, 'cod', 57000.00, 'completed', DATE_SUB(NOW(), INTERVAL 10 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (17, 17, 'card', 32900.00, 'completed', DATE_SUB(NOW(), INTERVAL 7 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (18, 18, 'bank_transfer', 69999.00, 'completed', DATE_SUB(NOW(), INTERVAL 6 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (19, 19, 'wallet', 10900.00, 'completed', DATE_SUB(NOW(), INTERVAL 5 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (20, 20, 'cod', 10780.00, 'completed', DATE_SUB(NOW(), INTERVAL 4 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (21, 21, 'card', 12998.00, 'completed', DATE_SUB(NOW(), INTERVAL 3 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (22, 22, 'bank_transfer', 23499.00, 'completed', DATE_SUB(NOW(), INTERVAL 2 DAY));
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (23, 23, 'wallet', 49999.00, 'pending', NULL);
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (24, 24, 'cod', 11590.00, 'pending', NULL);
INSERT INTO payments (payment_id, order_id, method, amount, status, paid_at) VALUES (25, 25, 'card', 135000.00, 'refunded', DATE_SUB(NOW(), INTERVAL 8 DAY));

-- Shipments (for delivered and shipped orders)
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (1, 1, 'Leopards Courier', 'PK-100001', DATE_SUB(NOW(), INTERVAL 44 DAY), DATE_SUB(NOW(), INTERVAL 42 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (2, 2, 'M&P Express', 'PK-100002', DATE_SUB(NOW(), INTERVAL 41 DAY), DATE_SUB(NOW(), INTERVAL 39 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (3, 3, 'Trax Logistics', 'PK-100003', DATE_SUB(NOW(), INTERVAL 37 DAY), DATE_SUB(NOW(), INTERVAL 35 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (4, 4, 'TCS Express', 'PK-100004', DATE_SUB(NOW(), INTERVAL 34 DAY), DATE_SUB(NOW(), INTERVAL 32 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (5, 5, 'Leopards Courier', 'PK-100005', DATE_SUB(NOW(), INTERVAL 29 DAY), DATE_SUB(NOW(), INTERVAL 27 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (6, 6, 'M&P Express', 'PK-100006', DATE_SUB(NOW(), INTERVAL 27 DAY), DATE_SUB(NOW(), INTERVAL 25 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (7, 7, 'Trax Logistics', 'PK-100007', DATE_SUB(NOW(), INTERVAL 25 DAY), DATE_SUB(NOW(), INTERVAL 23 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (8, 8, 'TCS Express', 'PK-100008', DATE_SUB(NOW(), INTERVAL 23 DAY), DATE_SUB(NOW(), INTERVAL 21 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (9, 9, 'Leopards Courier', 'PK-100009', DATE_SUB(NOW(), INTERVAL 21 DAY), DATE_SUB(NOW(), INTERVAL 19 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (10, 10, 'M&P Express', 'PK-100010', DATE_SUB(NOW(), INTERVAL 19 DAY), DATE_SUB(NOW(), INTERVAL 17 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (11, 11, 'Trax Logistics', 'PK-100011', DATE_SUB(NOW(), INTERVAL 17 DAY), DATE_SUB(NOW(), INTERVAL 15 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (12, 12, 'TCS Express', 'PK-100012', DATE_SUB(NOW(), INTERVAL 15 DAY), DATE_SUB(NOW(), INTERVAL 13 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (13, 13, 'Leopards Courier', 'PK-100013', DATE_SUB(NOW(), INTERVAL 14 DAY), DATE_SUB(NOW(), INTERVAL 12 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (14, 14, 'M&P Express', 'PK-100014', DATE_SUB(NOW(), INTERVAL 13 DAY), DATE_SUB(NOW(), INTERVAL 11 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (15, 15, 'Trax Logistics', 'PK-100015', DATE_SUB(NOW(), INTERVAL 11 DAY), DATE_SUB(NOW(), INTERVAL 9 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (16, 16, 'TCS Express', 'PK-100016', DATE_SUB(NOW(), INTERVAL 9 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY));
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (17, 17, 'Leopards Courier', 'PK-100017', DATE_SUB(NOW(), INTERVAL 6 DAY), NULL);
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (18, 18, 'M&P Express', 'PK-100018', DATE_SUB(NOW(), INTERVAL 5 DAY), NULL);
INSERT INTO shipments (shipment_id, order_id, courier, tracking_number, shipped_at, delivered_at) VALUES (19, 19, 'Trax Logistics', 'PK-100019', DATE_SUB(NOW(), INTERVAL 4 DAY), NULL);

-- Reviews (20 verified purchaser fragrance reviews)
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (1, 5, 101, 5, 'Khamrah is extraordinary. Warm cinnamon, sweet dates, and praline amber that lasts 12+ hours.', DATE_SUB(NOW(), INTERVAL 1 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (2, 5, 102, 4, 'Asad has incredible masculine projection. Smoky black pepper, coffee, and smooth vanilla.', DATE_SUB(NOW(), INTERVAL 2 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (3, 6, 103, 5, 'The viral pink Yara is heavenly! Fluffy marshmallow, tropical fruits, and vanilla cream.', DATE_SUB(NOW(), INTERVAL 3 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (4, 7, 104, 5, 'Yara Candy smells delicious. Effervescent candied berries and sparkling sugar fizz.', DATE_SUB(NOW(), INTERVAL 4 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (5, 7, 105, 5, 'Eclaire is the ultimate caramel waffle pastry perfume. Sweet, buttery, and long-lasting.', DATE_SUB(NOW(), INTERVAL 5 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (6, 8, 106, 4, 'Angham is so refined. French lavender and ginger praline that feels regal and calming.', DATE_SUB(NOW(), INTERVAL 6 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (7, 9, 107, 5, 'Khamrah Dukhan brings dark frankincense smoke to the iconic date sweetness. Sensational.', DATE_SUB(NOW(), INTERVAL 7 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (8, 9, 108, 5, 'Quentin Bisch outdid himself with Teriaq. Rhubarb, wild honey, and butter-soft leather.', DATE_SUB(NOW(), INTERVAL 8 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (9, 10, 109, 5, 'Badee Al Oud Noble Blush is pure lactonic luxury. Candied almonds and whipped rose petals.', DATE_SUB(NOW(), INTERVAL 9 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (10, 11, 110, 5, 'His Confession is dark, powdery, and magnetic. Fiery cinnamon and Tuscan iris.', DATE_SUB(NOW(), INTERVAL 10 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (11, 11, 111, 4, 'Victoria is a gorgeous royal bouquet. Fresh peony, red berries, and cashmeran.', DATE_SUB(NOW(), INTERVAL 11 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (12, 12, 112, 5, 'The Kingdom Men has a majestic mint-lavender aura with smooth tonka drydown.', DATE_SUB(NOW(), INTERVAL 12 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (13, 12, 113, 5, 'Liam Grey is the quintessential fig and black tea fragrance. Niche quality for sure.', DATE_SUB(NOW(), INTERVAL 13 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (14, 13, 114, 4, 'Asad Zanzibar is an oceanic spice bomb. Salted coconut water and incense.', DATE_SUB(NOW(), INTERVAL 14 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (15, 13, 115, 5, 'Atheeri is pure Arabian royalty. Saffron, Taif rose, and sunlit amber.', DATE_SUB(NOW(), INTERVAL 15 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (16, 14, 116, 5, 'Art Of Universe in Pride collection is magnificent. Blood orange and frankincense.', DATE_SUB(NOW(), INTERVAL 16 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (17, 15, 117, 4, 'Art Of Nature II has incredible green moss and forest accords. Very unique.', DATE_SUB(NOW(), INTERVAL 17 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (18, 5, 121, 5, 'Khamrah Qahwa with roasted Arabic coffee is unbelievable in cold weather.', DATE_SUB(NOW(), INTERVAL 18 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (19, 6, 122, 5, 'Oud For Glory is an absolute masterpiece. Rich saffron and smoky agarwood.', DATE_SUB(NOW(), INTERVAL 19 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (20, 7, 126, 5, 'Nebras is cozy hot chocolate and red berries in a bottle. Unmatched sillage.', DATE_SUB(NOW(), INTERVAL 20 DAY));

SET FOREIGN_KEY_CHECKS = 1;
'''

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # 1. Update database/init_perfume/02_sample_data.sql
    init_sample_path = os.path.join(root, 'database', 'init_perfume', '02_sample_data.sql')
    with open(init_sample_path, 'w', encoding='utf-8') as f:
        f.write(NEW_SAMPLE_DATA_SQL)
    print(f"Updated {init_sample_path}")

    # 2. Update database/seeds/02_sample_data.sql
    seed_sample_path = os.path.join(root, 'database', 'seeds', '02_sample_data.sql')
    if os.path.exists(seed_sample_path):
        with open(seed_sample_path, 'w', encoding='utf-8') as f:
            f.write(NEW_SAMPLE_DATA_SQL)
        print(f"Updated {seed_sample_path}")

    # 3. Update database/init_perfume/06_catalog_expansion.sql
    init_catalog_path = os.path.join(root, 'database', 'init_perfume', '06_catalog_expansion.sql')
    with open(init_catalog_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace category hierarchy setup section
    target_section_start = "-- 7. CATEGORY HIERARCHY SETUP & SLUG MAPPING"
    target_section_end = "-- 8. ANALYTICAL VIEWS"

    replacement_section = """-- 7. CATEGORY SLUG AND IMAGE ENRICHMENT
-- WHY: Ensures category slugs and showcase image paths for fragrance hierarchy.
-- ----------------------------------------------------------------------------
UPDATE categories SET slug = 'fragrances', image_path = 'static/images/categories/fragrances.svg' WHERE category_id = 100;
UPDATE categories SET slug = 'men', image_path = 'static/images/categories/men.svg' WHERE category_id = 101;
UPDATE categories SET slug = 'women', image_path = 'static/images/categories/women.svg' WHERE category_id = 102;
UPDATE categories SET slug = 'unisex', image_path = 'static/images/categories/unisex.svg' WHERE category_id = 103;
UPDATE categories SET slug = 'eau-de-parfum', image_path = 'static/images/categories/edp.svg' WHERE category_id = 104;
UPDATE categories SET slug = 'extrait-de-parfum', image_path = 'static/images/categories/extrait.svg' WHERE category_id = 105;
UPDATE categories SET slug = 'perfume-oils', image_path = 'static/images/categories/attar.svg' WHERE category_id = 106;
UPDATE categories SET slug = 'gift-sets', image_path = 'static/images/categories/gift_sets.svg' WHERE category_id = 107;


-- ----------------------------------------------------------------------------
"""

    if target_section_start in content and target_section_end in content:
        start_idx = content.find(target_section_start)
        end_idx = content.find(target_section_end)
        new_content = content[:start_idx] + replacement_section + content[end_idx:]
        with open(init_catalog_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {init_catalog_path}")

    # 4. Update database/seeds/08_catalog_expansion.sql
    seed_catalog_path = os.path.join(root, 'database', 'seeds', '08_catalog_expansion.sql')
    if os.path.exists(seed_catalog_path):
        with open(seed_catalog_path, 'r', encoding='utf-8') as f:
            c = f.read()
        if target_section_start in c and target_section_end in c:
            s_idx = c.find(target_section_start)
            e_idx = c.find(target_section_end)
            new_c = c[:s_idx] + replacement_section + c[e_idx:]
            with open(seed_catalog_path, 'w', encoding='utf-8') as f:
                f.write(new_c)
            print(f"Updated {seed_catalog_path}")

if __name__ == '__main__':
    main()
