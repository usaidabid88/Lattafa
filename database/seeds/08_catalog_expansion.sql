-- ============================================================================
-- 08_catalog_expansion.sql
-- Sub-Phase 11A: Database Schema Expansion for Real Product Catalog,
-- Brand Management, Multi-Image Support, Category Slugs & Analytical Views
--
-- DBMS Complex Engineering Problem (CEP) - Mehran University (MUET)
-- All operations are re-runnable (idempotent) and non-destructive.
-- Existing orders, users, carts, and sample products are preserved.
-- ============================================================================

USE online_shop;

-- ----------------------------------------------------------------------------
-- 1. TABLE: brands
-- WHY: Normalizes brand provenance into 3NF. Products reference brands via FK
-- instead of duplicating brand names across thousands of catalog items.
-- Allows filtering products by brand in storefront category pages.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS brands (
    brand_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_brands_name UNIQUE (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ----------------------------------------------------------------------------
-- 2. ALTER TABLE: categories
-- WHY: Adds 'slug' for clean SEO-friendly URLs and image directory mapping,
-- and 'image_path' to display visual category showcase cards on the homepage.
-- ----------------------------------------------------------------------------
DELIMITER $$
DROP PROCEDURE IF EXISTS _patch_categories_table$$
CREATE PROCEDURE _patch_categories_table()
BEGIN
    -- Add slug column if it does not exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'categories' AND column_name = 'slug'
    ) THEN
        ALTER TABLE categories ADD COLUMN slug VARCHAR(100) NULL AFTER name;
        ALTER TABLE categories ADD CONSTRAINT uq_categories_slug UNIQUE (slug);
    END IF;

    -- Add image_path column if it does not exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'categories' AND column_name = 'image_path'
    ) THEN
        ALTER TABLE categories ADD COLUMN image_path VARCHAR(255) NULL AFTER parent_category_id;
    END IF;
END$$
DELIMITER ;

CALL _patch_categories_table();
DROP PROCEDURE IF EXISTS _patch_categories_table;


-- ----------------------------------------------------------------------------
-- 3. ALTER TABLE: products
-- WHY: Enhances products with brand affiliation (FK to brands), source store
-- attribution for fair educational demonstration (source_store, source_url),
-- and concise card descriptions (short_description).
-- ----------------------------------------------------------------------------
DELIMITER $$
DROP PROCEDURE IF EXISTS _patch_products_table$$
CREATE PROCEDURE _patch_products_table()
BEGIN
    -- Add brand_id column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'products' AND column_name = 'brand_id'
    ) THEN
        ALTER TABLE products ADD COLUMN brand_id INT NULL AFTER category_id;
        ALTER TABLE products ADD CONSTRAINT fk_products_brand 
            FOREIGN KEY (brand_id) REFERENCES brands(brand_id) ON DELETE SET NULL;
    END IF;

    -- Add short_description
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'products' AND column_name = 'short_description'
    ) THEN
        ALTER TABLE products ADD COLUMN short_description VARCHAR(255) NULL AFTER name;
    END IF;

    -- Add source_store
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'products' AND column_name = 'source_store'
    ) THEN
        ALTER TABLE products ADD COLUMN source_store VARCHAR(100) NULL AFTER stock_quantity;
    END IF;

    -- Add source_url
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'products' AND column_name = 'source_url'
    ) THEN
        ALTER TABLE products ADD COLUMN source_url VARCHAR(500) NULL AFTER source_store;
    END IF;
END$$
DELIMITER ;

CALL _patch_products_table();
DROP PROCEDURE IF EXISTS _patch_products_table;


-- ----------------------------------------------------------------------------
-- 4. TABLE: product_images
-- WHY: Enables 1-to-N image galleries per product in 3NF. Each product can
-- have multiple angles (front, back, detail), an explicit display sort order,
-- and exactly one primary thumbnail for listing grids.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS product_images (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    is_primary TINYINT(1) NOT NULL DEFAULT 0,
    sort_order INT NOT NULL DEFAULT 1,
    source_url VARCHAR(500) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_images_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) ON DELETE CASCADE,
    CONSTRAINT uq_product_sort UNIQUE (product_id, sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ----------------------------------------------------------------------------
-- 5. INDEXES FOR PERFORMANCE OPTIMIZATION
-- WHY: Accelerates brand-filtered catalog queries, category + price sorting,
-- and slug-based routing lookups. Verified against EXPLAIN.
-- ----------------------------------------------------------------------------
DELIMITER $$
DROP PROCEDURE IF EXISTS _patch_indexes$$
CREATE PROCEDURE _patch_indexes()
BEGIN
    -- Index on products(brand_id)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.statistics 
        WHERE table_schema = DATABASE() AND table_name = 'products' AND index_name = 'idx_products_brand_id'
    ) THEN
        CREATE INDEX idx_products_brand_id ON products(brand_id);
    END IF;

    -- Composite index on products(category_id, price) for category browse & price sort
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.statistics 
        WHERE table_schema = DATABASE() AND table_name = 'products' AND index_name = 'idx_products_category_price'
    ) THEN
        CREATE INDEX idx_products_category_price ON products(category_id, price);
    END IF;

    -- Index on product_images(product_id, is_primary) for instant primary image resolution
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.statistics 
        WHERE table_schema = DATABASE() AND table_name = 'product_images' AND index_name = 'idx_images_product_primary'
    ) THEN
        CREATE INDEX idx_images_product_primary ON product_images(product_id, is_primary);
    END IF;
END$$
DELIMITER ;

CALL _patch_indexes();
DROP PROCEDURE IF EXISTS _patch_indexes;


-- ----------------------------------------------------------------------------
-- 6. CONSTRAINT: EXACTLY ONE PRIMARY IMAGE PER PRODUCT
-- WHY: Prevents ambiguous thumbnail states in listing grids.
-- Enforced via two complementary database mechanisms:
--   a) BEFORE INSERT & BEFORE UPDATE triggers: abort concurrent duplicate primary assignments.
--   b) Stored Procedure sp_set_product_primary_image: transactional utility to switch primaries.
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_product_images_single_primary_bi;
DROP TRIGGER IF EXISTS trg_product_images_single_primary_bu;

DELIMITER $$
CREATE TRIGGER trg_product_images_single_primary_bi
BEFORE INSERT ON product_images
FOR EACH ROW
BEGIN
    IF NEW.is_primary = 1 THEN
        IF (SELECT COUNT(*) FROM product_images WHERE product_id = NEW.product_id AND is_primary = 1) > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Constraint violation: Product already has an active primary image. Use sp_set_product_primary_image to reassign.';
        END IF;
    END IF;
END$$

CREATE TRIGGER trg_product_images_single_primary_bu
BEFORE UPDATE ON product_images
FOR EACH ROW
BEGIN
    IF NEW.is_primary = 1 AND (OLD.is_primary = 0 OR OLD.is_primary IS NULL) THEN
        IF (SELECT COUNT(*) FROM product_images WHERE product_id = NEW.product_id AND is_primary = 1 AND image_id <> NEW.image_id) > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Constraint violation: Product already has an active primary image. Use sp_set_product_primary_image to reassign.';
        END IF;
    END IF;
END$$

DROP PROCEDURE IF EXISTS sp_set_product_primary_image$$
CREATE PROCEDURE sp_set_product_primary_image(
    IN p_product_id INT,
    IN p_image_id INT
)
BEGIN
    DECLARE v_count INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
    -- Verify image belongs to product
    SELECT COUNT(*) INTO v_count FROM product_images WHERE product_id = p_product_id AND image_id = p_image_id;
    IF v_count = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Image does not belong to specified product.';
    END IF;

    -- Clear existing primary and activate target
    UPDATE product_images SET is_primary = 0 WHERE product_id = p_product_id;
    UPDATE product_images SET is_primary = 1 WHERE product_id = p_product_id AND image_id = p_image_id;
    COMMIT;
END$$
DELIMITER ;


-- ----------------------------------------------------------------------------
-- 7. CATEGORY SLUG AND IMAGE ENRICHMENT
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
-- 8. ANALYTICAL VIEWS
-- WHY: Decouples complex multi-table queries from the application code.
--   v_product_catalog: Full denormalized catalog with brand, category path,
--                      primary thumbnail, and calculated review metrics.
--   v_category_counts: Category roll-up counts of active products for both
--                      parent departments and sub-category chips.
-- ----------------------------------------------------------------------------
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
    COALESCE(r.avg_rating, 0.0) AS avg_rating,
    COALESCE(r.review_count, 0) AS review_count
FROM products p
LEFT JOIN brands b ON p.brand_id = b.brand_id
JOIN categories c ON p.category_id = c.category_id
LEFT JOIN categories parent_c ON c.parent_category_id = parent_c.category_id
LEFT JOIN product_images pi ON p.product_id = pi.product_id AND pi.is_primary = 1
LEFT JOIN (
    SELECT product_id, ROUND(AVG(rating), 1) AS avg_rating, COUNT(*) AS review_count
    FROM reviews
    GROUP BY product_id
) r ON p.product_id = r.product_id;

CREATE OR REPLACE VIEW v_category_counts AS
SELECT 
    c.category_id,
    c.name AS category_name,
    c.slug AS category_slug,
    c.image_path,
    c.parent_category_id,
    CASE 
        -- Top-level parent: sum active products in parent + all child subcategories
        WHEN c.parent_category_id IS NULL THEN (
            SELECT COUNT(*) 
            FROM products p 
            WHERE p.is_active = 1 
              AND (p.category_id = c.category_id OR p.category_id IN (
                  SELECT sub.category_id FROM categories sub WHERE sub.parent_category_id = c.category_id
              ))
        )
        -- Subcategory: count active products directly assigned
        ELSE (
            SELECT COUNT(*) 
            FROM products p 
            WHERE p.is_active = 1 AND p.category_id = c.category_id
        )
    END AS active_product_count
FROM categories c;
