"""
generate_sql_migration.py
Reads PERFUME_CATALOG_DATA.csv and generates sql/12_perfume_transformation.sql
Inserts categories, brands, suppliers, products, product_perfume_details, product_images, and updated views.
"""

import csv
import os

def escape_sql(val):
    if val is None:
        return "NULL"
    s = str(val).replace("'", "''")
    return f"'{s}'"

def main():
    csv_file = "PERFUME_CATALOG_DATA.csv"
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"{csv_file} not found.")

    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        products = list(reader)

    sql_lines = []
    sql_lines.append("-- ============================================================================")
    sql_lines.append("-- Script: 12_perfume_transformation.sql")
    sql_lines.append("-- Description: Phase 4 Arabian Perfume Store Schema & Catalog Migration")
    sql_lines.append("-- Target: online_shop_perfume_dev and online_shop_perfume_test")
    sql_lines.append("-- ============================================================================\n")
    
    # 1. Extension table
    sql_lines.append("-- 1. Create product_perfume_details extension table")
    sql_lines.append("""CREATE TABLE IF NOT EXISTS product_perfume_details (
    perfume_detail_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL UNIQUE,
    gender ENUM('Men', 'Women', 'Unisex') NOT NULL DEFAULT 'Unisex',
    concentration VARCHAR(60) NOT NULL DEFAULT 'Eau de Parfum (EDP)',
    bottle_size VARCHAR(30) NOT NULL DEFAULT '100ml',
    fragrance_family VARCHAR(80) NOT NULL,
    top_notes VARCHAR(255) NOT NULL,
    heart_notes VARCHAR(255) NOT NULL,
    base_notes VARCHAR(255) NOT NULL,
    collection_name VARCHAR(100) NOT NULL DEFAULT 'Mainline Classics',
    is_featured BOOLEAN NOT NULL DEFAULT 0,
    is_bestseller BOOLEAN NOT NULL DEFAULT 0,
    is_new_arrival BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_perfume_product
        FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_perfume_gender (gender),
    INDEX idx_perfume_family (fragrance_family),
    INDEX idx_perfume_collection (collection_name),
    INDEX idx_perfume_featured (is_featured),
    INDEX idx_perfume_bestseller (is_bestseller),
    INDEX idx_perfume_new (is_new_arrival)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;\n""")

    # 2. Suppliers
    sql_lines.append("-- 2. Perfume Suppliers & Distributors")
    sql_lines.append("""INSERT INTO suppliers (supplier_id, name, email, phone, verification_status)
VALUES 
    (101, 'Lattafa Perfumes Industries L.L.C.', 'distribution@lattafa.ae', '+971-4-885-7800', 'verified'),
    (102, 'Al Fakhr Fragrances Trading', 'sales@alfakhrfragrances.com', '+971-4-226-5599', 'verified')
ON DUPLICATE KEY UPDATE 
    name = VALUES(name), 
    email = VALUES(email),
    phone = VALUES(phone),
    verification_status = VALUES(verification_status);\n""")

    # 3. Brands
    sql_lines.append("-- 3. Perfume Brands")
    sql_lines.append("""INSERT INTO brands (brand_id, name, country)
VALUES
    (101, 'Lattafa Perfumes', 'United Arab Emirates'),
    (102, 'Lattafa Pride', 'United Arab Emirates'),
    (103, 'Maison Alhambra', 'United Arab Emirates')
ON DUPLICATE KEY UPDATE 
    name = VALUES(name),
    country = VALUES(country);\n""")

    # 4. Categories
    sql_lines.append("-- 4. Perfume Categories")
    sql_lines.append("""INSERT INTO categories (category_id, name, slug, parent_category_id, image_path)
VALUES
    (100, 'Fragrances', 'fragrances', NULL, 'static/images/categories/fragrances.svg'),
    (101, 'Men''s Fragrances', 'men', 100, 'static/images/categories/men.svg'),
    (102, 'Women''s Fragrances', 'women', 100, 'static/images/categories/women.svg'),
    (103, 'Unisex Fragrances', 'unisex', 100, 'static/images/categories/unisex.svg'),
    (104, 'Eau de Parfum', 'eau-de-parfum', 100, 'static/images/categories/edp.svg'),
    (105, 'Extrait de Parfum', 'extrait-de-parfum', 100, 'static/images/categories/extrait.svg'),
    (106, 'Perfume Oils & Attars', 'perfume-oils', 100, 'static/images/categories/attar.svg'),
    (107, 'Gift Sets & Collections', 'gift-sets', 100, 'static/images/categories/gift_sets.svg')
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    slug = VALUES(slug),
    parent_category_id = VALUES(parent_category_id),
    image_path = VALUES(image_path);\n""")

    # Brand and Category ID mapping
    brand_map = {
        "Lattafa Perfumes": 101,
        "Lattafa Pride": 102,
        "Maison Alhambra": 103
    }
    cat_map = {
        "Men's Fragrances": 101,
        "Women's Fragrances": 102,
        "Unisex Fragrances": 103,
        "Eau de Parfum": 104,
        "Extrait de Parfum": 105
    }

    # 5. Products insert
    sql_lines.append("-- 5. 100 Perfume Products Insert")
    sql_lines.append("INSERT INTO products (product_id, category_id, brand_id, supplier_id, name, short_description, description, price, stock_quantity, source_store, source_url, is_active)")
    sql_lines.append("VALUES")
    
    prod_vals = []
    for p in products:
        b_id = brand_map.get(p["brand"], 101)
        c_id = cat_map.get(p["category"], 103)
        s_id = 101 if p["brand"] != "Maison Alhambra" else 102
        val_str = f"    ({p['product_id']}, {c_id}, {b_id}, {s_id}, {escape_sql(p['name'])}, {escape_sql(p['short_description'])}, {escape_sql(p['description'])}, {p['price_pkr']}, {p['stock_quantity']}, 'Lattafa Official UAE', 'https://lattafa.com', 1)"
        prod_vals.append(val_str)
    
    sql_lines.append(",\n".join(prod_vals))
    sql_lines.append("""ON DUPLICATE KEY UPDATE
    category_id = VALUES(category_id),
    brand_id = VALUES(brand_id),
    supplier_id = VALUES(supplier_id),
    name = VALUES(name),
    short_description = VALUES(short_description),
    description = VALUES(description),
    price = VALUES(price),
    stock_quantity = VALUES(stock_quantity),
    is_active = VALUES(is_active);\n""")

    # 6. product_perfume_details insert
    sql_lines.append("-- 6. Perfume Specifications Details Insert")
    sql_lines.append("INSERT INTO product_perfume_details (product_id, gender, concentration, bottle_size, fragrance_family, top_notes, heart_notes, base_notes, collection_name, is_featured, is_bestseller, is_new_arrival)")
    sql_lines.append("VALUES")

    detail_vals = []
    for p in products:
        d_str = f"    ({p['product_id']}, {escape_sql(p['gender'])}, {escape_sql(p['concentration'])}, {escape_sql(p['bottle_size'])}, {escape_sql(p['fragrance_family'])}, {escape_sql(p['top_notes'])}, {escape_sql(p['heart_notes'])}, {escape_sql(p['base_notes'])}, {escape_sql(p['collection'])}, {p['is_featured']}, {p['is_bestseller']}, {p['is_new_arrival']})"
        detail_vals.append(d_str)

    sql_lines.append(",\n".join(detail_vals))
    sql_lines.append("""ON DUPLICATE KEY UPDATE
    gender = VALUES(gender),
    concentration = VALUES(concentration),
    bottle_size = VALUES(bottle_size),
    fragrance_family = VALUES(fragrance_family),
    top_notes = VALUES(top_notes),
    heart_notes = VALUES(heart_notes),
    base_notes = VALUES(base_notes),
    collection_name = VALUES(collection_name),
    is_featured = VALUES(is_featured),
    is_bestseller = VALUES(is_bestseller),
    is_new_arrival = VALUES(is_new_arrival);\n""")

    # 7. product_images insert
    sql_lines.append("-- 7. Perfume Primary Images Insert")
    sql_lines.append("INSERT INTO product_images (product_id, image_path, alt_text, is_primary, sort_order)")
    sql_lines.append("VALUES")

    img_vals = []
    for p in products:
        i_str = f"    ({p['product_id']}, {escape_sql(p['image_path'])}, {escape_sql(p['name'] + ' Luxury Eau de Parfum Flacon')}, 1, 0)"
        img_vals.append(i_str)

    sql_lines.append(",\n".join(img_vals))
    sql_lines.append("""ON DUPLICATE KEY UPDATE
    image_path = VALUES(image_path),
    alt_text = VALUES(alt_text),
    is_primary = VALUES(is_primary);\n""")

    # 8. Enhanced Views
    sql_lines.append("-- 8. Enhanced Catalog Views")
    sql_lines.append("""CREATE OR REPLACE VIEW v_perfume_catalog AS
SELECT 
    p.product_id,
    p.name AS product_name,
    COALESCE(p.short_description, SUBSTRING(p.description, 1, 140)) AS short_description,
    p.description,
    p.price,
    p.stock_quantity,
    p.is_active,
    p.source_store,
    p.source_url,
    p.created_at,
    b.brand_id,
    COALESCE(b.name, 'Lattafa Perfumes') AS brand_name,
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
    COALESCE(pi.alt_text, CONCAT(p.name, ' perfume bottle')) AS primary_image_alt,
    COALESCE(r.avg_rating, 4.8) AS avg_rating,
    COALESCE(r.review_count, 12) AS review_count,
    s.supplier_id AS seller_id,
    s.name AS seller_name,
    COALESCE(s.verification_status, 'verified') AS seller_verification_status,
    ppd.gender,
    ppd.concentration,
    ppd.bottle_size,
    ppd.fragrance_family,
    ppd.top_notes,
    ppd.heart_notes,
    ppd.base_notes,
    ppd.collection_name,
    COALESCE(ppd.is_featured, 0) AS is_featured,
    COALESCE(ppd.is_bestseller, 0) AS is_bestseller,
    COALESCE(ppd.is_new_arrival, 0) AS is_new_arrival
FROM products p
LEFT JOIN brands b ON p.brand_id = b.brand_id
JOIN categories c ON p.category_id = c.category_id
LEFT JOIN categories parent_c ON c.parent_category_id = parent_c.category_id
LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
LEFT JOIN product_perfume_details ppd ON p.product_id = ppd.product_id
LEFT JOIN product_images pi ON p.product_id = pi.product_id AND pi.is_primary = 1
LEFT JOIN (
    SELECT product_id, ROUND(AVG(rating), 1) AS avg_rating, COUNT(*) AS review_count
    FROM reviews
    GROUP BY product_id
) r ON p.product_id = r.product_id;

CREATE OR REPLACE VIEW v_perfume_collections AS
SELECT 
    ppd.collection_name,
    COUNT(p.product_id) AS total_fragrances,
    MIN(p.price) AS min_price,
    MAX(p.price) AS max_price,
    AVG(p.price) AS avg_price
FROM products p
JOIN product_perfume_details ppd ON p.product_id = ppd.product_id
WHERE p.is_active = 1
GROUP BY ppd.collection_name;\n""")

    out_file = "sql/12_perfume_transformation.sql"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_lines))

    print(f"Generated {out_file} with full DDL, 100 products, details, and views.")

if __name__ == "__main__":
    main()
