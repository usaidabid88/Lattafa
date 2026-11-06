import sys

path = 'app/app.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """        cur.execute(\"\"\"
            SELECT p.product_id, p.name, c.name AS category_name, b.name AS brand_name,
                   p.price, p.stock_quantity, p.is_active,
                   COALESCE(pi.image_path, 'static/images/placeholder.svg') AS primary_image
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN brands b ON p.brand_id = b.brand_id
            LEFT JOIN product_images pi ON p.product_id = pi.product_id AND pi.is_primary = 1
            ORDER BY p.product_id DESC
        \"\"\")"""

replacement = """        cur.execute(\"\"\"
            SELECT p.product_id, p.name, c.name AS category_name, b.name AS brand_name,
                   p.price, p.stock_quantity, p.is_active,
                   COALESCE(pi.image_path, 'static/images/placeholder.svg') AS primary_image,
                   ppd.concentration, ppd.bottle_size_ml, ppd.gender, ppd.collection_name, ppd.fragrance_family
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN brands b ON p.brand_id = b.brand_id
            LEFT JOIN product_images pi ON p.product_id = pi.product_id AND pi.is_primary = 1
            LEFT JOIN product_perfume_details ppd ON p.product_id = ppd.product_id
            ORDER BY p.product_id DESC
        \"\"\")"""

normalized = content.replace('\r\n', '\n')
if target in normalized:
    normalized = normalized.replace(target, replacement, 1)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(normalized)
    print("SUCCESS: app/app.py admin_products query updated with perfume details.")
else:
    print("ERROR: Target query block not found.")
