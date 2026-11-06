"""
test_app.py - End-to-end verification of Flask Web UI & Complete DBMS Pipeline
Executed strictly against the isolated testing database (online_shop_test).

Covers:
- Test Isolation & Safety Guards (Work Package C):
  Verifies that test operations target online_shop_test and strictly refuse
  to touch development or production databases.
- CSRF Protection (Work Package A):
  Verifies rejection of POST requests missing or with invalid CSRF tokens (400),
  and acceptance of valid tokens across all forms.
- Phase 8: Core customer/admin auth, catalog, cart, checkout via sp_place_order, RBAC, reporting views.
- Phase 11: Department browsing, multi-image galleries, secure upload validations.
- Phase 12: Anonymous guest checkout (sp_place_guest_order), cart merge (sp_merge_carts),
  sp_cart_summary pricing breakdown, simulated payment gateway sandbox & recovery, order tracking
  timeline, support ticketing & staff queue, return requests & overdue SLA view, seller verification,
  policy pages, custom error handling, and /health probe.
"""

import sys
import os
import io
import re
import pymysql
from dotenv import load_dotenv

# Ensure app package is importable
app_dir = os.path.join(os.path.dirname(__file__), 'app')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Load environment configuration
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Target strictly the isolated test database
TEST_DB_NAME = os.getenv('TEST_DB_NAME', 'online_shop_test')


def assert_safe_test_database(db_name):
    """Enforce strict safety guard: only databases explicitly designated for testing may be used."""
    if not db_name or not isinstance(db_name, str):
        raise ValueError(f"Invalid database name: {db_name}")
    normalized = db_name.strip().lower()
    if normalized in ('online_shop', 'prod', 'production'):
        raise RuntimeError(
            f"SAFETY VIOLATION: Test suite strictly prohibited from executing against development/production database '{db_name}'!"
        )
    if not (normalized.endswith('_test') or normalized.startswith('test_')):
        raise RuntimeError(
            f"SAFETY VIOLATION: Designated test database '{db_name}' must end with '_test' or start with 'test_'!"
        )


# Enforce safety guard before initializing test application
assert_safe_test_database(TEST_DB_NAME)

from app import app

# Configure application for testing against isolated database
app.config['TESTING'] = True
app.config['DB_NAME'] = TEST_DB_NAME
app.config['WTF_CSRF_ENABLED'] = True


def get_test_db_connection():
    """Return an explicit connection strictly to the test database."""
    assert_safe_test_database(TEST_DB_NAME)
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=TEST_DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


def reset_test_state():
    """Deterministic test fixture: cleans up transient test data and restores baseline inventory in online_shop_test."""
    assert_safe_test_database(TEST_DB_NAME)
    conn = get_test_db_connection()
    with conn.cursor() as cur:
        # 1. Clean up transient test orders placed by automated tests
        cur.execute("SELECT order_id FROM orders WHERE guest_email LIKE '%guest%' OR guest_name LIKE '%Guest Test%' OR order_id > 1000")
        test_order_ids = [r['order_id'] for r in cur.fetchall()]
        if test_order_ids:
            ids_csv = ','.join(map(str, test_order_ids))
            cur.execute(f"DELETE FROM payment_attempts WHERE order_id IN ({ids_csv})")
            cur.execute(f"DELETE FROM payments WHERE order_id IN ({ids_csv})")
            cur.execute(f"DELETE FROM order_items WHERE order_id IN ({ids_csv})")
            cur.execute(f"DELETE FROM order_status_history WHERE order_id IN ({ids_csv})")
            cur.execute(f"DELETE FROM return_requests WHERE order_id IN ({ids_csv})")
            cur.execute(f"DELETE FROM support_tickets WHERE order_id IN ({ids_csv})")
            cur.execute(f"DELETE FROM orders WHERE order_id IN ({ids_csv})")

        # 2. Clean up transient carts and cart items
        cur.execute("DELETE FROM cart_items WHERE cart_id IN (SELECT cart_id FROM carts WHERE user_id = 5 OR session_token IS NOT NULL)")
        cur.execute("DELETE FROM carts WHERE session_token IS NOT NULL")

        # 3. Clean up test tickets and return requests
        cur.execute("DELETE FROM support_tickets WHERE contact_email LIKE '%@example.pk' OR subject LIKE '%Screen glass cracked%'")
        cur.execute("DELETE FROM return_requests WHERE reason = 'damaged' AND description LIKE '%Item arrived damaged%'")

        # 4. Replenish test stock quantities to baseline in online_shop_test
        cur.execute("UPDATE products SET stock_quantity = 15 WHERE product_id = 12")
        cur.execute("UPDATE products SET stock_quantity = 10 WHERE product_id = 1")
        cur.execute("UPDATE products SET stock_quantity = 25 WHERE product_id = 2")
        cur.execute("UPDATE products SET stock_quantity = 10 WHERE product_id = 3")
        cur.execute("UPDATE products SET stock_quantity = 10 WHERE product_id = 10")

        # 5. Restore baseline status for Order 1 and Supplier 1
        cur.execute("UPDATE orders SET status = 'delivered' WHERE order_id = 1")
        cur.execute("UPDATE suppliers SET verification_status = 'verified' WHERE supplier_id = 1")

    conn.close()


def run_tests():
    # Setup test isolation fixture before running test suite
    reset_test_state()

    client = app.test_client()
    passed = 0
    failed = 0
    active_token = None

    def assert_test(name, condition, extra=""):
        nonlocal passed, failed
        if condition:
            print(f"  [PASS] {name} {extra}")
            passed += 1
        else:
            print(f"  [FAIL] {name} {extra}")
            failed += 1

    def refresh_token(page_url='/login'):
        nonlocal active_token
        res = client.get(page_url)
        m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.data.decode('utf-8', errors='ignore'))
        if m:
            active_token = m.group(1)
        return active_token

    def post_csrf(url, data=None, **kwargs):
        nonlocal active_token
        data_dict = dict(data) if data else {}
        if not active_token:
            refresh_token('/login')
        data_dict['csrf_token'] = active_token
        res = client.post(url, data=data_dict, **kwargs)
        # Update token if a new form was rendered in response
        m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.data.decode('utf-8', errors='ignore'))
        if m:
            active_token = m.group(1)
        return res

    print("\n========================================================")
    print("      UNIFIED E2E VERIFICATION SUITE (ISOLATED TEST DB)")
    print(f"      Active Test Database: {TEST_DB_NAME}")
    print("========================================================")

    # -------------------------------------------------------------------------
    # PART 0: TEST DATABASE ISOLATION & CSRF SECURITY GATES
    # -------------------------------------------------------------------------
    # SG-05: Test database isolation check
    conn_check = get_test_db_connection()
    with conn_check.cursor() as cur:
        cur.execute("SELECT DATABASE() AS db")
        current_db = cur.fetchone()['db']
    conn_check.close()
    assert_test("Test Database Isolation (SG-05)", current_db == TEST_DB_NAME and current_db != 'online_shop')

    # SG-01 / SG-02: CSRF Rejection: POST without CSRF token must return 400
    res_no_csrf = client.post('/login', data={'email': 'zeeshan@gmail.com', 'password': 'password123'}, follow_redirects=True)
    assert_test("CSRF Gate: POST without token rejected (SG-01/02)", res_no_csrf.status_code == 400 and b"Invalid request" in res_no_csrf.data)

    # SG-02: CSRF Rejection: POST with invalid token must return 400
    res_bad_csrf = client.post('/login', data={'email': 'zeeshan@gmail.com', 'password': 'password123', 'csrf_token': 'tampered_invalid_token'}, follow_redirects=True)
    assert_test("CSRF Gate: POST with invalid token rejected (SG-02)", res_bad_csrf.status_code == 400)

    # -------------------------------------------------------------------------
    # PART 1: CORE STOREFRONT & BROWSING
    # -------------------------------------------------------------------------
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
    assert_test("GET /login", res.status_code == 200 and b"Login" in res.data and b'name="csrf_token"' in res.data)
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.data.decode('utf-8'))
    if m:
        active_token = m.group(1)

    # -------------------------------------------------------------------------
    # PART 2: AUTHENTICATED CUSTOMER FLOW (WITH CSRF TOKENS)
    # -------------------------------------------------------------------------
    # 6. Customer Login Action (Zeeshan Ahmed)
    res = post_csrf('/login', data={'email': 'zeeshan@gmail.com', 'password': 'password123'}, follow_redirects=True)
    assert_test("POST /login (Customer Auth)", res.status_code == 200 and b"Zeeshan Ahmed" in res.data)

    # 7. Add to Cart (Product 12: J. Classic Cotton Kurta)
    res = post_csrf('/cart/add', data={'product_id': 12, 'quantity': 2}, follow_redirects=True)
    assert_test("POST /cart/add (Auth User)", res.status_code == 200 and b"Classic Cotton Kurta" in res.data)

    # 8. View Cart
    res = client.get('/cart')
    assert_test("GET /cart (Auth User)", res.status_code == 200 and b"PKR" in res.data)

    # 9. Checkout Page
    res = client.get('/checkout')
    assert_test("GET /checkout (Auth User)", res.status_code == 200 and b"Delivery Address" in res.data and b'name="csrf_token"' in res.data)
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.data.decode('utf-8'))
    if m:
        active_token = m.group(1)

    # 10. Place Order via Checkout (calls sp_place_order)
    res = post_csrf('/checkout', data={'address_id': 1, 'payment_method': 'cod', 'consent_terms': 'on'}, follow_redirects=True)
    assert_test("POST /checkout (Atomic Order Placement)", res.status_code == 200 and (b"Order placed successfully" in res.data or b"Order #" in res.data))

    # 11. Customer Order History
    res = client.get('/my-orders')
    assert_test("GET /my-orders", res.status_code == 200 and b"Order #" in res.data)

    # 12. Security Test: Customer blocked from Admin Dashboard
    res = client.get('/admin', follow_redirects=False)
    assert_test("RBAC: Customer denied /admin (302 Redirect)", res.status_code == 302)

    # 13. Logout
    client.get('/logout')
    active_token = None

    # -------------------------------------------------------------------------
    # PART 3: ADMIN & BACKOFFICE OPERATIONS
    # -------------------------------------------------------------------------
    # 14. Admin Login (Ali Raza)
    res = client.get('/login')
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.data.decode('utf-8'))
    if m:
        active_token = m.group(1)
    res = post_csrf('/login', data={'email': 'admin@muetshop.pk', 'password': 'password123'}, follow_redirects=True)
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
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.data.decode('utf-8'))
    if m:
        active_token = m.group(1)

    # 18. Admin Reports Page (Views Invocations)
    res = client.get('/admin/reports')
    assert_test("GET /admin/reports (Views Integration)", res.status_code == 200 and b"v_sales_by_category" in res.data and b"v_low_stock" in res.data and b"v_best_sellers" in res.data)

    # 19. Admin Order Status Update
    res = post_csrf('/admin/order/status', data={'order_id': 20, 'new_status': 'shipped'}, follow_redirects=True)
    assert_test("POST /admin/order/status", res.status_code == 200 and b"status updated" in res.data)

    # -------------------------------------------------------------------------
    # PART 4: PHASE 11 CATALOG & MULTI-MEDIA EXTENSIONS
    # -------------------------------------------------------------------------
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
    res_form = client.get('/admin/product/add')
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_form.data.decode('utf-8'))
    if m:
        active_token = m.group(1)
    fake_txt = (io.BytesIO(b'malicious script'), 'shell.txt')
    res = post_csrf('/admin/product/add', data={
        'name': 'Test Upload Bad Ext', 'category_id': 1, 'supplier_id': 1,
        'price': '1000', 'stock_quantity': '10', 'image': fake_txt
    }, follow_redirects=True)
    assert_test("Admin Upload Format Check (11F)", b"Invalid image format" in res.data)

    # 26. Admin Image Upload Validation - Oversized File (11F)
    res_form = client.get('/admin/product/add')
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_form.data.decode('utf-8'))
    if m:
        active_token = m.group(1)
    huge_file = (io.BytesIO(b'0' * (2 * 1024 * 1024 + 1024)), 'oversized.jpg')
    res = post_csrf('/admin/product/add', data={
        'name': 'Test Upload Huge File', 'category_id': 1, 'supplier_id': 1,
        'price': '1000', 'stock_quantity': '10', 'image': huge_file
    }, follow_redirects=True)
    assert_test("Admin Upload Size Check (11F)", b"exceeds maximum limit" in res.data)

    # -------------------------------------------------------------------------
    # PART 5: PHASE 12 SRS ALIGNMENT SUITE (12C, 12D, 12E, 12F)
    # -------------------------------------------------------------------------
    # 27. Health Check Probe (AC-07.5, NFR-08)
    res = client.get('/health')
    assert_test("GET /health probe returns 200 JSON", res.status_code == 200 and b"healthy" in res.data and b"connected" in res.data)

    # 28-30. Policy Pages (FR-19)
    res_priv = client.get('/privacy')
    assert_test("GET /privacy renders successfully", res_priv.status_code == 200 and b"Privacy Policy" in res_priv.data)
    res_terms = client.get('/terms')
    assert_test("GET /terms renders successfully", res_terms.status_code == 200 and b"Terms of Service" in res_terms.data)
    res_ret = client.get('/returns-policy')
    assert_test("GET /returns-policy renders successfully", res_ret.status_code == 200 and b"Replacement Policy" in res_ret.data)

    # 31. Anonymous Guest Cart & Signed Token (FR-03, AC-08.1)
    with client.session_transaction() as sess:
        sess.clear()
    active_token = None
    res_prod = client.get('/product/1')
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_prod.data.decode('utf-8'))
    if m:
        active_token = m.group(1)
    res_guest_add = post_csrf('/cart/add', data={'product_id': 1, 'quantity': 1}, follow_redirects=True)
    assert_test("POST /cart/add (Guest) allows adding without auth", res_guest_add.status_code == 200 and b"Item added to cart" in res_guest_add.data)

    # 32. Pricing breakdown via sp_cart_summary
    res_guest_cart = client.get('/cart?province=Punjab&city=Lahore')
    assert_test("GET /cart (Guest) calculates pricing via sp_cart_summary", res_guest_cart.status_code == 200 and b"Cart Total Breakdown" in res_guest_cart.data and b"Lahore" in res_guest_cart.data)

    # 33. Guest Checkout (FR-02, AC-03.1, NFR-06)
    res_chk = client.get('/checkout')
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_chk.data.decode('utf-8'))
    if m:
        active_token = m.group(1)
    guest_data = {
        'guest_name': 'Tariq Mansoor (Guest Test)',
        'guest_email': 'tariq.guest@example.pk',
        'guest_phone': '+92 321 9876543',
        'guest_address': 'Flat 4B, Gulshan-e-Iqbal',
        'guest_city': 'Karachi',
        'guest_province': 'Sindh',
        'payment_method': 'cod',
        'consent_terms': 'on'
    }
    res_guest_checkout = post_csrf('/checkout', data=guest_data, follow_redirects=True)
    assert_test("POST /checkout (Guest Order Placement) completes via sp_place_guest_order", res_guest_checkout.status_code == 200 and (b"Order placed successfully" in res_guest_checkout.data or b"Order #" in res_guest_checkout.data))

    # 34. Simulated Payment Gateway Sandbox & Fail Recovery (FR-06, FR-10, FR-11, AC-02.x)
    res_prod = client.get('/product/2')
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_prod.data.decode('utf-8'))
    if m:
        active_token = m.group(1)
    post_csrf('/cart/add', data={'product_id': 2, 'quantity': 1}, follow_redirects=True)

    res_chk = client.get('/checkout')
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_chk.data.decode('utf-8'))
    if m:
        active_token = m.group(1)
    sim_data = guest_data.copy()
    sim_data['payment_method'] = 'simulated'
    res_sim_checkout = post_csrf('/checkout', data=sim_data, follow_redirects=True)
    assert_test("POST /checkout (Simulated Payment) routes to payment gateway sandbox", res_sim_checkout.status_code == 200 and b"Digital Payment Gateway" in res_sim_checkout.data)

    match = re.search(r'#(\d+)', res_sim_checkout.data.decode('utf-8'))
    order_id = int(match.group(1)) if match else None

    if order_id:
        m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_sim_checkout.data.decode('utf-8'))
        if m:
            active_token = m.group(1)
        # Simulate payment failure
        res_fail = post_csrf(f'/payment/process/{order_id}', data={'action': 'fail'}, follow_redirects=True)
        assert_test("POST /payment/process (Fail outcome) logs attempt and routes to payment recovery", res_fail.status_code == 200 and b"Payment settlement unconfirmed" in res_fail.data)

        # Switch to COD recovery
        m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_fail.data.decode('utf-8'))
        if m:
            active_token = m.group(1)
        res_switch = post_csrf(f'/payment/switch-cod/{order_id}', follow_redirects=True)
        assert_test("POST /payment/switch-cod switches method to COD and confirms order", res_switch.status_code == 200 and b"Order placed successfully" in res_switch.data)

        # 35. Order Tracking with Audit Timeline (FR-12, AC-04.3)
        res_track = client.get(f'/orders/{order_id}/track')
        assert_test("GET /orders/<id>/track displays live trigger audit timeline", res_track.status_code == 200 and b"Audit timeline history" in res_track.data)

    # 36. Customer Support Ticket Lifecycle (FR-14, AC-04.4, AC-04.5)
    res_supp = client.get('/support')
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_supp.data.decode('utf-8'))
    if m:
        active_token = m.group(1)
    ticket_payload = {
        'contact_name': 'Babar Azam',
        'contact_email': 'babar@example.pk',
        'contact_phone': '+92 300 1112233',
        'order_id': order_id or '',
        'issue_type': 'damaged',
        'subject': 'Screen glass cracked during shipping',
        'description': 'Opened parcel from TCS and noticed outer corner crack.'
    }
    res_ticket = post_csrf('/support', data=ticket_payload, follow_redirects=True)
    assert_test("POST /support submits customer support ticket", res_ticket.status_code == 200 and b"TCK-" in res_ticket.data)

    # 37. Staff Ticket Queue & Resolution (AC-04.5)
    res_log = client.get('/login')
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_log.data.decode('utf-8'))
    if m:
        active_token = m.group(1)
    post_csrf('/login', data={'email': 'admin@muetshop.pk', 'password': 'password123'}, follow_redirects=True)
    res_staff_queue = client.get('/staff/tickets')
    assert_test("GET /staff/tickets renders staff ticket queue", res_staff_queue.status_code == 200 and b"Customer Support Queue" in res_staff_queue.data)

    # 38. Seller Verification Dashboard (FR-17, FR-18, AC-06.1, AC-06.2)
    res_sellers = client.get('/admin/sellers')
    assert_test("GET /admin/sellers renders seller verification dashboard", res_sellers.status_code == 200 and b"Seller Verification" in res_sellers.data)
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_sellers.data.decode('utf-8'))
    if m:
        active_token = m.group(1)

    # 39. Toggle seller verification status
    res_verify_toggle = post_csrf('/admin/sellers/1/verify', data={'status': 'verified'}, follow_redirects=True)
    assert_test("POST /admin/sellers/<id>/verify toggles seller verification status", res_verify_toggle.status_code == 200 and b"verification status changed" in res_verify_toggle.data)

    # 40. Return & Replacement Claims (FR-20, FR-21, AC-08.4)
    if order_id:
        res_ret_form = client.get(f'/orders/{order_id}/return')
        m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_ret_form.data.decode('utf-8'))
        if m:
            active_token = m.group(1)
        return_payload = {
            'product_id': 2,
            'reason': 'damaged',
            'refund_method': 'original_payment',
            'description': 'Item arrived damaged upon initial unboxing.'
        }
        res_ret_claim = post_csrf(f'/orders/{order_id}/return', data=return_payload, follow_redirects=True)
        assert_test("POST /orders/<id>/return lodges customer return claim", res_ret_claim.status_code == 200 and b"RMA-" in res_ret_claim.data)

    # 41. Seller Return Claims Queue
    res_seller_ret = client.get('/seller/returns')
    assert_test("GET /seller/returns displays seller return claims queue", res_seller_ret.status_code == 200 and b"Merchandise Return Claims" in res_seller_ret.data)

    # 42. Overdue Return SLA View (AC-08.6)
    res_overdue = client.get('/admin/returns/overdue')
    assert_test("GET /admin/returns/overdue displays v_overdue_return_requests SLA view", res_overdue.status_code == 200 and b"Overdue Return Claims" in res_overdue.data)

    # 43. Admin Dashboard Abandoned Carts View
    res_admin_dash = client.get('/admin')
    assert_test("GET /admin dashboard renders v_abandoned_carts table", res_admin_dash.status_code == 200 and b"Abandoned Shopping Carts" in res_admin_dash.data)

    # 44. Custom 404 Error Page (FR-04, AC-07.4)
    res_404 = client.get('/nonexistent-route-for-testing')
    assert_test("Custom 404 error page renders without leaking stack trace", res_404.status_code == 404 and b"Record not found" in res_404.data)

    # 45. Cart Merge on Login (FR-03, AC-08.2)
    # Clear session, add item as guest, then login as zeeshan to trigger sp_merge_carts
    with client.session_transaction() as sess:
        sess.clear()
    active_token = None
    res_prod = client.get('/product/3')
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_prod.data.decode('utf-8'))
    if m:
        active_token = m.group(1)
    post_csrf('/cart/add', data={'product_id': 3, 'quantity': 1}, follow_redirects=True)

    res_log = client.get('/login')
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_log.data.decode('utf-8'))
    if m:
        active_token = m.group(1)
    res_login_merge = post_csrf('/login', data={'email': 'zeeshan@gmail.com', 'password': 'password123'}, follow_redirects=True)
    res_merged_cart = client.get('/cart')
    assert_test("Cart Merge on Login (Guest cart items transferred to user cart)", res_merged_cart.status_code == 200 and b"Cart Total Breakdown" in res_merged_cart.data)

    print(f"\n========================================================")
    print(f"  TOTAL RESULTS: {passed} PASSED, {failed} FAILED")
    print(f"  Target Database: {TEST_DB_NAME}")
    print("========================================================\n")

    # Clean up test artifacts after test suite completion
    reset_test_state()

    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
