-- ============================================================================
-- Script: 02_sample_data.sql
-- Description: Realistic Pakistani Sample Data for Online Shopping System
-- All prices in PKR. Realistic Pakistani names, cities, phone numbers.
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
SET FOREIGN_KEY_CHECKS = 1;

-- Categories (Top-level and subcategories)
INSERT INTO categories (category_id, name, parent_category_id) VALUES (1, 'Electronics', NULL);
INSERT INTO categories (category_id, name, parent_category_id) VALUES (2, 'Laptops & Computers', 1);
INSERT INTO categories (category_id, name, parent_category_id) VALUES (3, 'Mobile Phones & Tablets', 1);
INSERT INTO categories (category_id, name, parent_category_id) VALUES (4, 'Fashion & Apparel', NULL);
INSERT INTO categories (category_id, name, parent_category_id) VALUES (5, 'Men''s Clothing', 4);
INSERT INTO categories (category_id, name, parent_category_id) VALUES (6, 'Women''s Clothing', 4);
INSERT INTO categories (category_id, name, parent_category_id) VALUES (7, 'Home & Kitchen', NULL);
INSERT INTO categories (category_id, name, parent_category_id) VALUES (8, 'Kitchen Appliances', 7);

-- Suppliers
INSERT INTO suppliers (supplier_id, name, email, phone) VALUES (1, 'TechZone Distribution Karachi', 'contact@techzone.pk', '021-34567890');
INSERT INTO suppliers (supplier_id, name, email, phone) VALUES (2, 'Haier Pakistan Appliance Hub', 'info@haierpakistan.pk', '042-35789123');
INSERT INTO suppliers (supplier_id, name, email, phone) VALUES (3, 'Al-Karam Textile Mills Ltd', 'sales@alkaram.com', '021-111555222');
INSERT INTO suppliers (supplier_id, name, email, phone) VALUES (4, 'J. Junaid Jamshed Retailers', 'support@junaidjamshed.com', '021-111112111');
INSERT INTO suppliers (supplier_id, name, email, phone) VALUES (5, 'MegaTech Electronics Islamabad', 'distro@megatech.com.pk', '051-2894567');

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

-- Products (30 items, PKR pricing, realistic stock levels)
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (1, 3, 1, 'Samsung Galaxy S24 Ultra', '512GB Titanium Black, 12GB RAM, 200MP Camera', 399999.00, 15, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (2, 3, 1, 'Infinix Note 40 Pro', '256GB Vintage Green, 70W Fast Charge, AMOLED Display', 69999.00, 25, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (3, 3, 5, 'Xiaomi Redmi Note 13', '128GB Midnight Black, 108MP Triple Camera', 49999.00, 4, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (4, 3, 1, 'Apple iPhone 15 Pro Max', '256GB Natural Titanium, A17 Pro Chip', 485000.00, 8, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (5, 3, 5, 'Tecno Camon 30 Premier', '512GB Alps Snowy White, 5G Dual SIM', 84999.00, 20, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (6, 2, 1, 'Dell XPS 15 9530', 'Intel Core i7 13th Gen, 16GB RAM, 1TB SSD, RTX 4050', 450000.00, 5, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (7, 2, 5, 'HP Pavilion 15', 'Intel Core i5 12th Gen, 8GB RAM, 512GB SSD, Silver', 165000.00, 12, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (8, 2, 1, 'Lenovo IdeaPad 3', 'AMD Ryzen 5 5500U, 8GB RAM, 512GB SSD', 135000.00, 3, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (9, 2, 5, 'Apple MacBook Air M2', '8GB Unified Memory, 256GB SSD, Space Gray', 315000.00, 10, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (10, 2, 1, 'Logitech MX Master 3S Mouse', 'Wireless Performance Mouse, 8K DPI Sensor', 28500.00, 30, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (11, 2, 5, 'Dell 27 Inch 4K Monitor', 'UltraSharp IPS Display, USB-C Hub, 60Hz', 125000.00, 7, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (12, 5, 4, 'J. Classic Cotton Kurta White', 'Premium stitched Egyptian cotton kurta for men', 6490.00, 40, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (13, 5, 4, 'J. Boski Unstitched Fabric', 'Traditional Pakistani pure Boski suit length', 18500.00, 15, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (14, 5, 4, 'J. Casual Linen Shirt Navy', 'Slim-fit summer linen casual shirt for men', 4290.00, 50, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (15, 5, 3, 'Al-Karam Men Formal Trousers', 'Wrinkle-free straight fit formal pants Charcoal', 5100.00, 2, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (16, 6, 3, 'Al-Karam 3-Piece Lawn Embroidered', 'Unstitched digital printed lawn suit with chiffon dupatta', 7950.00, 45, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (17, 6, 3, 'Al-Karam Pret Stitched Kurti', 'Embroidered cambric ready-to-wear daily shirt', 3850.00, 60, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (18, 6, 4, 'J. Silk Festive 3-Piece Suit', 'Luxury raw silk stitched formal wedding suit', 24500.00, 10, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (19, 6, 3, 'Al-Karam Chiffon Shawl Maroon', 'Winter warm embroidered Pashmina style shawl', 4500.00, 22, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (20, 8, 2, 'Dawlance Microwave Oven 20L', 'Digital display, Grill function, Defrost series', 26500.00, 18, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (21, 8, 2, 'Dawlance Food Processor 7-in-1', 'Multi-function kitchen chopper and blender', 19500.00, 25, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (22, 8, 2, 'Haier Electric Kettle 1.7L', 'Stainless steel rapid boil auto shut-off', 5800.00, 35, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (23, 8, 2, 'Haier Air Fryer 5.5L', 'Digital touchscreen oil-free healthy cooking', 24000.00, 14, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (24, 8, 2, 'Dawlance Automatic Citrus Juicer', 'Stainless steel electric orange juicer extractor', 8900.00, 3, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (25, 3, 1, 'Audionic Airbud 550 TWS', 'Wireless gaming earbuds with quad mic ENC', 6499.00, 50, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (26, 3, 5, 'Anker 20000mAh Power Bank', 'PowerIQ fast charging portable battery pack', 13999.00, 28, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (27, 2, 1, 'Redragon Mechanical Keyboard', 'RGB backlit blue switch gaming keyboard', 9500.00, 16, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (28, 5, 4, 'J. Leather Peshawari Chappal', 'Handmade traditional genuine leather footwear Mustard', 8200.00, 20, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (29, 6, 3, 'Al-Karam Velvet Winter Stole', 'Embossed floral velvet party wrap', 3200.00, 30, 1);
INSERT INTO products (product_id, category_id, supplier_id, name, description, price, stock_quantity, is_active) VALUES (30, 8, 2, 'Haier Deep Fryer 3L', 'Non-stick adjustable temperature commercial fryer', 17500.00, 8, 1);

-- Carts (active, converted, and abandoned carts for testing)
INSERT INTO carts (cart_id, user_id, status, created_at, updated_at) VALUES (1, 5, 'active', NOW(), NOW());
INSERT INTO carts (cart_id, user_id, status, created_at, updated_at) VALUES (2, 8, 'active', NOW(), NOW());
INSERT INTO carts (cart_id, user_id, status, created_at, updated_at) VALUES (3, 11, 'abandoned', DATE_SUB(NOW(), INTERVAL 14 DAY), DATE_SUB(NOW(), INTERVAL 10 DAY));
INSERT INTO carts (cart_id, user_id, status, created_at, updated_at) VALUES (4, 14, 'abandoned', DATE_SUB(NOW(), INTERVAL 20 DAY), DATE_SUB(NOW(), INTERVAL 12 DAY));
INSERT INTO carts (cart_id, user_id, status, created_at, updated_at) VALUES (5, 7, 'converted', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY));

-- Cart Items
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (1, 2, 1);
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (1, 25, 2);
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (2, 16, 1);
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (3, 1, 1);
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (3, 10, 1);
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (4, 20, 1);
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (5, 12, 2);

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

-- Order Items (exact subtotals match orders.total_amount)
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (1, 12, 2, 6490.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (1, 25, 1, 6499.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (2, 16, 2, 7950.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (3, 2, 1, 69999.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (3, 26, 1, 13999.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (4, 17, 3, 3850.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (5, 20, 1, 26500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (5, 22, 1, 5800.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (6, 18, 1, 24500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (7, 10, 1, 28500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (7, 27, 1, 9500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (8, 16, 1, 7950.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (8, 19, 2, 4500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (9, 13, 1, 18500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (9, 28, 1, 8200.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (10, 21, 1, 19500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (11, 7, 1, 165000.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (12, 22, 2, 5800.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (12, 23, 1, 24000.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (13, 29, 3, 3200.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (14, 14, 2, 4290.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (14, 28, 1, 8200.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (15, 16, 1, 7950.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (15, 17, 1, 3850.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (16, 10, 2, 28500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (17, 23, 1, 24000.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (17, 24, 1, 8900.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (18, 2, 1, 69999.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (19, 17, 2, 3850.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (19, 29, 1, 3200.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (20, 12, 1, 6490.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (20, 14, 1, 4290.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (21, 25, 2, 6499.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (22, 26, 1, 13999.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (22, 27, 1, 9500.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (23, 3, 1, 49999.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (24, 15, 1, 5100.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (24, 12, 1, 6490.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (25, 8, 1, 135000.00);

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

-- Reviews (20 realistic reviews from verified purchasers)
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (1, 5, 12, 5, 'Exceptional Egyptian cotton fabric. Very comfortable for Friday prayers.', DATE_SUB(NOW(), INTERVAL 1 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (2, 5, 25, 4, 'Good bass and fast Bluetooth connection. Battery lasts about 5 hours.', DATE_SUB(NOW(), INTERVAL 2 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (3, 6, 16, 5, 'Beautiful lawn print with delicate embroidery. Colors did not fade after washing.', DATE_SUB(NOW(), INTERVAL 3 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (4, 7, 2, 5, 'Infinix 70W charging is insane, charges to full in 40 minutes. Great screen.', DATE_SUB(NOW(), INTERVAL 4 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (5, 7, 26, 4, 'Solid power bank, charges my phone three full times during loadshedding.', DATE_SUB(NOW(), INTERVAL 5 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (6, 8, 17, 4, 'Stitching quality is neat and sizing is true to Pakistani standard.', DATE_SUB(NOW(), INTERVAL 6 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (7, 9, 20, 5, 'Heating is uniform and quick. Defrost function works well on frozen meat.', DATE_SUB(NOW(), INTERVAL 7 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (8, 9, 22, 4, 'Fast electric kettle, boils 1.5 liters in under 4 minutes.', DATE_SUB(NOW(), INTERVAL 8 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (9, 10, 18, 5, 'Royal fabric and luxurious embroidery. Perfect for my cousin''s wedding reception.', DATE_SUB(NOW(), INTERVAL 9 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (10, 11, 10, 5, 'Ergonomic mouse is life-changing for programming. Scroll wheel is magic.', DATE_SUB(NOW(), INTERVAL 10 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (11, 11, 27, 4, 'Crisp tactile clicks on blue switches. RGB lighting is bright and customizable.', DATE_SUB(NOW(), INTERVAL 11 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (12, 12, 16, 5, 'Received so many compliments at university. Al-Karam always delivers quality.', DATE_SUB(NOW(), INTERVAL 12 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (13, 12, 19, 4, 'Warm and cozy shawl for winter evenings in Hyderabad.', DATE_SUB(NOW(), INTERVAL 13 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (14, 13, 13, 5, 'Authentic Boski fabric with natural fall. Very satisfied with delivery.', DATE_SUB(NOW(), INTERVAL 14 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (15, 13, 28, 5, 'Mustard Peshawari chappal fits perfectly, soft leather that does not bite.', DATE_SUB(NOW(), INTERVAL 15 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (16, 14, 21, 4, 'Motor is powerful enough for onions, cabbage, and mint chutney.', DATE_SUB(NOW(), INTERVAL 16 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (17, 15, 7, 5, 'Fast boot with NVMe SSD. Handles software development and IDEs smoothly.', DATE_SUB(NOW(), INTERVAL 17 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (18, 5, 23, 5, 'Air fryer makes crispy samosas with just a spray of oil. Highly recommended.', DATE_SUB(NOW(), INTERVAL 18 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (19, 6, 29, 4, 'Plush velvet material with elegant borders. Looks expensive.', DATE_SUB(NOW(), INTERVAL 19 DAY));
INSERT INTO reviews (review_id, user_id, product_id, rating, comment, created_at) VALUES (20, 7, 14, 4, 'Breathable summer linen shirt. Color matches the product photo accurately.', DATE_SUB(NOW(), INTERVAL 20 DAY));

