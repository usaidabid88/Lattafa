"""
test_app.py - End-to-end verification of Flask Web UI (Phase 8)
Tests customer registration, login, catalog browsing, cart operations,
atomic checkout via sp_place_order, role-based protection, and admin views.
"""

import sys
import os

# Add app directory to sys.path
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

from app import app

def run_tests():
    client = app.test_client()
    passed = 0
    failed = 0

    def assert_test(name, condition, extra=""):
        nonlocal passed, failed
        if condition:
            print(f"  [PASS] {name} {extra}")
            passed += 1
        else:
            print(f"  [FAIL] {name} {extra}")
            failed += 1

    print("\n=== FLASK WEB APPLICATION TEST SUITE ===")

    # 1. Homepage
    res = client.get('/')
    assert_test("GET / (Homepage)", res.status_code == 200 and b"MUET Shop" in res.data)

    # 2. Product Catalog
    res = client.get('/products')
    assert_test("GET /products", res.status_code == 200 and b"Samsung Galaxy" in res.data)

    # 3. Product Search
    res = client.get('/products?q=Samsung')
    assert_test("GET /products?q=Samsung", res.status_code == 200 and b"Samsung Galaxy S24 Ultra" in res.data)

    # 4. Product Detail
    res = client.get('/product/1')
    assert_test("GET /product/1", res.status_code == 200 and b"Titanium Black" in res.data)

    # 5. Customer Login Page
    res = client.get('/login')
    assert_test("GET /login", res.status_code == 200 and b"Login" in res.data)

    # 6. Customer Login Action (Zeeshan Ahmed)
    res = client.post('/login', data={'email': 'zeeshan@gmail.com', 'password': 'password123'}, follow_redirects=True)
    assert_test("POST /login (Customer Auth)", res.status_code == 200 and b"Zeeshan Ahmed" in res.data)

    # 7. Add to Cart (Product 12: J. Classic Cotton Kurta)
    res = client.post('/cart/add', data={'product_id': 12, 'quantity': 2}, follow_redirects=True)
    assert_test("POST /cart/add", res.status_code == 200 and b"Classic Cotton Kurta" in res.data)

    # 8. View Cart
    res = client.get('/cart')
    assert_test("GET /cart", res.status_code == 200 and b"PKR" in res.data)

    # 9. Checkout Page
    res = client.get('/checkout')
    assert_test("GET /checkout", res.status_code == 200 and b"Delivery Address" in res.data)

    # 10. Place Order via Checkout (calls sp_place_order)
    res = client.post('/checkout', data={'address_id': 1, 'payment_method': 'cod'}, follow_redirects=True)
    assert_test("POST /checkout (Atomic Order Placement)", res.status_code == 200 and (b"Order placed successfully" in res.data or b"Order #" in res.data))

    # 11. Customer Order History
    res = client.get('/my-orders')
    assert_test("GET /my-orders", res.status_code == 200 and b"Order #" in res.data)

    # 12. Security Test: Customer blocked from Admin Dashboard
    res = client.get('/admin', follow_redirects=False)
    assert_test("RBAC: Customer denied /admin (302 Redirect)", res.status_code == 302)

    # 13. Logout
    client.get('/logout')

    # 14. Admin Login (Ali Raza)
    res = client.post('/login', data={'email': 'admin@muetshop.pk', 'password': 'password123'}, follow_redirects=True)
    assert_test("POST /login (Admin Auth)", res.status_code == 200 and b"Admin & Staff Dashboard" in res.data)

    # 15. Admin Dashboard
    res = client.get('/admin')
    assert_test("GET /admin", res.status_code == 200 and b"Low Stock Alerts" in res.data)

    # 16. Admin Products List
    res = client.get('/admin/products')
    assert_test("GET /admin/products", res.status_code == 200 and b"Manage Products" in res.data)

    # 17. Admin Orders List
    res = client.get('/admin/orders')
    assert_test("GET /admin/orders", res.status_code == 200 and b"Manage Orders" in res.data)

    # 18. Admin Reports Page (Views Invocations)
    res = client.get('/admin/reports')
    assert_test("GET /admin/reports (Views Integration)", res.status_code == 200 and b"v_sales_by_category" in res.data and b"v_low_stock" in res.data and b"v_best_sellers" in res.data)

    # 19. Admin Order Status Update
    res = client.post('/admin/order/status', data={'order_id': 20, 'new_status': 'shipped'}, follow_redirects=True)
    assert_test("POST /admin/order/status", res.status_code == 200 and b"status updated" in res.data)

    # ─── PHASE 11 CATALOG & MULTI-MEDIA EXTENSIONS ─────────────────────────────
    import io

    # 20. Top-Level Department Browsing (11D)
    res = client.get('/category/laptops-computers')
    assert_test("GET /category/laptops-computers (11D)", res.status_code == 200 and b"Laptops and Computers" in res.data and b"Departments:" in res.data)

    # 21. Sub-Category Browsing (11D)
    res = client.get('/category/women-unstitched')
    assert_test("GET /category/women-unstitched (11D)", res.status_code == 200 and b"Unstitched" in res.data)

    # 22. Category Price Sorting (11D)
    res = client.get('/category/laptops-computers?sort=price_asc')
    assert_test("GET /category/laptops-computers?sort=price_asc (11D)", res.status_code == 200 and b"Price: Low to High" in res.data)

    # 23. Category Brand Filtering (11D)
    res = client.get('/category/laptops-computers?brand=Dell')
    assert_test("GET /category/laptops-computers?brand=Dell (11D)", res.status_code == 200 and b"Dell" in res.data)

    # 24. Product Multi-Image Gallery (11E)
    res = client.get('/product/1')
    assert_test("GET /product/1 Gallery (11E)", res.status_code == 200 and b"mainGalleryImage" in res.data)

    # 25. Admin Image Upload Validation - Invalid Extension (11F)
    fake_txt = (io.BytesIO(b'malicious script'), 'shell.txt')
    res = client.post('/admin/product/add', data={
        'name': 'Test Upload Bad Ext', 'category_id': 1, 'supplier_id': 1,
        'price': '1000', 'stock_quantity': '10', 'image': fake_txt
    }, follow_redirects=True)
    assert_test("Admin Upload Format Check (11F)", b"Invalid image format" in res.data)

    # 26. Admin Image Upload Validation - Oversized File (11F)
    huge_file = (io.BytesIO(b'0' * (2 * 1024 * 1024 + 1024)), 'oversized.jpg')
    res = client.post('/admin/product/add', data={
        'name': 'Test Upload Huge File', 'category_id': 1, 'supplier_id': 1,
        'price': '1000', 'stock_quantity': '10', 'image': huge_file
    }, follow_redirects=True)
    assert_test("Admin Upload Size Check (11F)", b"exceeds maximum limit" in res.data)

    print(f"\nTest Summary: {passed} PASSED, {failed} FAILED\n")
    return failed == 0

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
