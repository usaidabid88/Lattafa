import os
import re

os.environ['TEST_DB_NAME'] = 'online_shop_perfume_test'
import test_app

client = test_app.app.test_client()
# Run reset_test_state
test_app.reset_test_state()

# Place guest order first
res = client.get('/products')
# Get product
# test guest flow
client.get('/cart')
# add item
res_add = test_app.post_csrf(client, None, '/cart/add', data={'product_id': 101, 'quantity': 1}, follow_redirects=True)
# get csrf for checkout
res_chk = client.get('/checkout')
m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_chk.data.decode('utf-8'))
token = m.group(1) if m else None

res_order = client.post('/checkout', data={
    'guest_name': 'Perfume Tester',
    'guest_email': 'tester@perfume.com',
    'shipping_address': 'Fragrance Ave, Karachi',
    'payment_method': 'card',
    'csrf_token': token
}, follow_redirects=True)

print("res_order status:", res_order.status_code)
print("res_order url/data:", res_order.request.path if hasattr(res_order, 'request') else 'N/A')
print("res_order text snippet:", res_order.data[:300].decode('utf-8', errors='ignore'))

# Check order_id match
m_order = re.search(r'/payment/sandbox/(\d+)', res_order.data.decode('utf-8', errors='ignore'))
if not m_order:
    m_order = re.search(r'order[_\s#:]+(\d+)', res_order.data.decode('utf-8', errors='ignore'), re.I)
print("Matched order:", m_order.groups() if m_order else "None")
