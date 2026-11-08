#!/usr/bin/env python3
"""
import_catalog.py - Idempotent Catalog Importer (Sub-Phase 11B)
Imports products from data/products_manifest.csv into MySQL 8.0 online_shop.
Safely upserts brands, suppliers, categories, products, and product_images.
"""

import os
import sys
import csv
from decimal import Decimal
from pathlib import Path
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# Base paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / 'app'))

# Load environment
load_dotenv(ROOT_DIR / '.env')
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASSWORD') or os.getenv('DB_PASS', '')
DB_NAME = os.getenv('DB_NAME', 'online_shop')
DB_PORT = int(os.getenv('DB_PORT', 3306))


def get_db():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT,
        charset='utf8mb4',
        cursorclass=DictCursor,
        autocommit=False
    )


def import_catalog(manifest_path=None):
    if manifest_path is None:
        manifest_path = ROOT_DIR / 'data' / 'products_manifest.csv'
    
    if not os.path.exists(manifest_path):
        print(f"[ERROR] Manifest file not found at: {manifest_path}")
        return False

    print(f"\n=======================================================")
    print(f"  CATALOG IMPORT PIPELINE: {manifest_path.name}")
    print(f"=======================================================\n")

    conn = get_db()
    rows_processed = 0
    rows_imported = 0
    rows_skipped = 0
    missing_images = []

    try:
        with conn.cursor() as cur:
            # 1. Cache Category Mapping (slug -> category_id)
            cur.execute("SELECT category_id, name, slug FROM categories WHERE slug IS NOT NULL")
            cat_rows = cur.fetchall()
            cat_map = {c['slug']: c['category_id'] for c in cat_rows}

            # 2. Cache Supplier Mapping (name -> supplier_id)
            cur.execute("SELECT supplier_id, name FROM suppliers")
            sup_rows = cur.fetchall()
            sup_map = {s['name']: s['supplier_id'] for s in sup_rows}

            # Default supplier fallback if none provided
            default_supplier_id = sup_rows[0]['supplier_id'] if sup_rows else 1

            # 3. Read and process manifest CSV
            with open(manifest_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for line_no, row in enumerate(reader, start=2):
                    rows_processed += 1
                    name = row.get('product_name', '').strip()
                    brand_name = row.get('brand', '').strip()
                    cat_slug = row.get('category_slug', '').strip()
                    desc = row.get('description', '').strip()
                    price_str = row.get('price_pkr', '').strip()
                    stock_str = row.get('stock_quantity', '').strip()
                    sup_name = row.get('supplier_name', '').strip()
                    source_store = row.get('source_store', '').strip()
                    source_url = row.get('source_url', '').strip()
                    image_files_str = row.get('image_files', '').strip()
                    primary_image_rel = row.get('primary_image', '').strip()

                    # Basic validation
                    if not name or not cat_slug or not price_str:
                        print(f"  [SKIP] Line {line_no}: Missing required fields for '{name or 'Unknown'}'")
                        rows_skipped += 1
                        continue

                    # Validate category
                    if cat_slug not in cat_map:
                        print(f"  [SKIP] Line {line_no}: Unknown category slug '{cat_slug}' for '{name}'")
                        rows_skipped += 1
                        continue
                    category_id = cat_map[cat_slug]

                    # Parse numbers
                    try:
                        price = Decimal(price_str)
                        stock = int(stock_str) if stock_str else 10
                    except Exception as e:
                        print(f"  [SKIP] Line {line_no}: Invalid price/stock for '{name}': {e}")
                        rows_skipped += 1
                        continue

                    # Brand Upsert
                    brand_id = None
                    if brand_name:
                        cur.execute(
                            "INSERT INTO brands (name) VALUES (%s) "
                            "ON DUPLICATE KEY UPDATE name = VALUES(name)",
                            (brand_name,)
                        )
                        cur.execute("SELECT brand_id FROM brands WHERE name = %s", (brand_name,))
                        b_row = cur.fetchone()
                        if b_row:
                            brand_id = b_row['brand_id']

                    # Supplier resolution
                    supplier_id = sup_map.get(sup_name, default_supplier_id)

                    # Product Upsert by Name
                    cur.execute("SELECT product_id FROM products WHERE name = %s", (name,))
                    prod_row = cur.fetchone()

                    short_desc = desc[:120] if desc else None
                    if prod_row:
                        product_id = prod_row['product_id']
                        cur.execute(
                            """
                            UPDATE products SET
                                category_id = %s,
                                brand_id = %s,
                                supplier_id = %s,
                                short_description = %s,
                                description = %s,
                                price = %s,
                                stock_quantity = %s,
                                source_store = %s,
                                source_url = %s,
                                is_active = 1
                            WHERE product_id = %s
                            """,
                            (category_id, brand_id, supplier_id, short_desc, desc, price, stock,
                             source_store, source_url, product_id)
                        )
                    else:
                        cur.execute(
                            """
                            INSERT INTO products 
                                (category_id, brand_id, supplier_id, name, short_description, 
                                 description, price, stock_quantity, source_store, source_url, is_active)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                            """,
                            (category_id, brand_id, supplier_id, name, short_desc, desc, price,
                             stock, source_store, source_url)
                        )
                        product_id = cur.lastrowid

                    # Product Images Handling
                    image_paths = [p.strip() for p in image_files_str.split(';') if p.strip()]
                    if not image_paths:
                        image_paths = [primary_image_rel] if primary_image_rel else ['static/images/placeholder.svg']

                    # Check image files on disk
                    valid_images = []
                    for img_rel in image_paths:
                        # Check either root-relative or inside app/
                        disk_path_root = ROOT_DIR / img_rel
                        disk_path_app = ROOT_DIR / 'app' / img_rel
                        if disk_path_root.exists() or disk_path_app.exists():
                            valid_images.append(img_rel)
                        else:
                            # Not on disk yet
                            missing_images.append((name, img_rel))

                    # Remove existing image mappings for this product to avoid trigger duplicate conflict
                    cur.execute("DELETE FROM product_images WHERE product_id = %s", (product_id,))

                    # Insert images
                    # If any image is found on disk, use it; otherwise use the designated path (fallback to placeholder if missing)
                    target_images = image_paths if image_paths else ['static/images/placeholder.svg']
                    
                    for sort_order, img_rel in enumerate(target_images, start=1):
                        is_primary = 1 if (sort_order == 1 or img_rel == primary_image_rel) else 0
                        # Enforce exactly one primary on first insert
                        if sort_order > 1 and is_primary:
                            is_primary = 0
                            
                        cur.execute(
                            """
                            INSERT INTO product_images 
                                (product_id, image_path, is_primary, sort_order, source_url)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (product_id, img_rel, is_primary, sort_order, source_url)
                        )

                    rows_imported += 1

            # Ensure all legacy active products have at least a placeholder primary image
            cur.execute("""
                INSERT INTO product_images (product_id, image_path, is_primary, sort_order)
                SELECT p.product_id, 'static/images/placeholder.svg', 1, 1
                FROM products p
                LEFT JOIN product_images pi ON p.product_id = pi.product_id
                WHERE pi.image_id IS NULL
            """)

            conn.commit()

        # Final Report
        print(f"[OK] Rows processed in CSV:    {rows_processed}")
        print(f"[OK] Products imported/updated: {rows_imported}")
        print(f"[OK] Rows skipped:              {rows_skipped}")
        print(f"[INFO] Missing images on disk:  {len(missing_images)}")
        if missing_images:
            print(f"       (First 5 missing: {missing_images[:5]})")
            print(f"       (Note: Placeholder will render gracefully until downloaded)")

        # Verify active count in MySQL
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total_active FROM products WHERE is_active = 1")
            active_count = cur.fetchone()['total_active']
            cur.execute("SELECT COUNT(*) AS total_catalog FROM v_product_catalog")
            catalog_count = cur.fetchone()['total_catalog']
            print(f"[VERIFY] Total active products in database: {active_count}")
            print(f"[VERIFY] Total products in v_product_catalog: {catalog_count}\n")

        return True

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Pipeline transaction rolled back due to error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    manifest = sys.argv[1] if len(sys.argv) > 1 else None
    success = import_catalog(manifest)
    sys.exit(0 if success else 1)
