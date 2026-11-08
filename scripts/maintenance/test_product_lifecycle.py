"""
Integration test script to verify full Admin Product Lifecycle:
Create -> Olfactory Details -> Update -> Verify -> Delete
Against online_shop_perfume_dev or online_shop_perfume_test.
"""

import os
import sys
import re

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)

from app.app import app, get_db

def test_admin_product_crud():
    app.config['TESTING'] = True
    client = app.test_client()

    print("\n--- Verifying Admin Product CRUD Lifecycle ---")

    # 1. Login as Admin
    res = client.get('/login')
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.data.decode('utf-8'))
    csrf_token = m.group(1) if m else None
    assert csrf_token, "Failed to get CSRF token"

    login_res = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': 'admin@muetshop.pk',
        'password': 'password123'
    }, follow_redirects=True)
    assert b"Admin & Staff Dashboard" in login_res.data, "Admin login failed"
    print("  [PASS] Admin login authenticated successfully")

    # 2. Get add product form
    add_form_res = client.get('/admin/product/add')
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', add_form_res.data.decode('utf-8'))
    csrf_token = m.group(1) if m else None

    # 3. Create a new test fragrance
    payload = {
        'csrf_token': csrf_token,
        'name': 'Test Imperial Amber Oud',
        'category_id': '103',
        'brand_id': '101',
        'supplier_id': '101',
        'price': '8900',
        'stock_quantity': '25',
        'gender': 'Unisex',
        'concentration': 'Eau de Parfum (EDP)',
        'bottle_size': '100ml',
        'fragrance_family': 'Amber Woody Oriental',
        'top_notes': 'Cardamom, Bergamot, Pink Pepper',
        'heart_notes': 'Damask Rose, Amber, Cedarwood',
        'base_notes': 'Cambodian Oud, Vanilla, Musk',
        'collection_name': 'Imperial Collection',
        'is_active': 'on'
    }

    create_res = client.post('/admin/product/add', data=payload, follow_redirects=True)
    assert create_res.status_code == 200, f"Expected 200, got {create_res.status_code}"
    assert b"Fragrance added to catalog successfully" in create_res.data, "Add fragrance failed"
    print("  [PASS] Admin successfully created new fragrance with full olfactory pyramid")

    # 4. Verify in DB
    with app.app_context():
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT product_id, name, price FROM products WHERE name = %s", ('Test Imperial Amber Oud',))
            prod = cur.fetchone()
            assert prod, "Product not found in database"
            prod_id = prod['product_id']

            cur.execute("SELECT * FROM product_perfume_details WHERE product_id = %s", (prod_id,))
            details = cur.fetchone()
            assert details, "Perfume details not found in database"
            assert details['top_notes'] == 'Cardamom, Bergamot, Pink Pepper'
            assert details['fragrance_family'] == 'Amber Woody Oriental'
            print(f"  [PASS] Database verified product #{prod_id} and olfactory pyramid records")

    # 5. Test edit product
    edit_form_res = client.get(f'/admin/product/edit/{prod_id}')
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', edit_form_res.data.decode('utf-8'))
    csrf_token = m.group(1) if m else None

    edit_payload = payload.copy()
    edit_payload['csrf_token'] = csrf_token
    edit_payload['name'] = 'Test Imperial Amber Oud (Updated Edition)'
    edit_payload['price'] = '9500'

    edit_res = client.post(f'/admin/product/edit/{prod_id}', data=edit_payload, follow_redirects=True)
    assert b"Product updated successfully" in edit_res.data, "Update fragrance failed"
    print("  [PASS] Admin successfully edited fragrance details")

    # 6. Clean up test product
    with app.app_context():
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM product_perfume_details WHERE product_id = %s", (prod_id,))
            cur.execute("DELETE FROM product_images WHERE product_id = %s", (prod_id,))
            cur.execute("DELETE FROM products WHERE product_id = %s", (prod_id,))
        conn.commit()
    print("  [PASS] Cleaned up temporary test records cleanly")
    print("--- ALL ADMIN PRODUCT CRUD LIFECYCLE CHECKS PASSED ---\n")

if __name__ == '__main__':
    test_admin_product_crud()
