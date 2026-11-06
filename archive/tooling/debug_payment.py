import os
import sys
import re

sys.path.insert(0, os.path.abspath('.'))
os.environ['TEST_DB_NAME'] = 'online_shop_perfume_test'
import test_app

client = test_app.app.test_client()
test_app.reset_test_state()

# 34. Simulated Payment Gateway Sandbox & Fail Recovery
res_prod = client.get('/product/2')
m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_prod.data.decode('utf-8'))
active_token = m.group(1) if m else None

def post_csrf(url, data=None, **kwargs):
    global active_token
    d = (data or {}).copy()
    if active_token and 'csrf_token' not in d:
        d['csrf_token'] = active_token
    return client.post(url, data=d, **kwargs)

res_add = post_csrf('/cart/add', data={'product_id': 2, 'quantity': 1}, follow_redirects=True)
res_chk = client.get('/checkout')
m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_chk.data.decode('utf-8'))
if m:
    active_token = m.group(1)

guest_data = {
    'guest_name': 'Guest Test Shopper',
    'guest_email': 'guest.tester@muetshop.pk',
    'shipping_address': 'Room 14, Hostels, Jamshoro',
    'payment_method': 'cod'
}
sim_data = guest_data.copy()
sim_data['payment_method'] = 'simulated'
res_sim_checkout = post_csrf('/checkout', data=sim_data, follow_redirects=True)
print("res_sim_checkout status:", res_sim_checkout.status_code)
print("Digital Payment Gateway in data?:", b"Digital Payment Gateway" in res_sim_checkout.data)

match = re.search(r'#(\d+)', res_sim_checkout.data.decode('utf-8'))
order_id = int(match.group(1)) if match else None
print("Extracted order_id:", order_id)

if order_id:
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_sim_checkout.data.decode('utf-8'))
    if m:
        active_token = m.group(1)
    res_fail = post_csrf(f'/payment/process/{order_id}', data={'action': 'fail'}, follow_redirects=True)
    print("res_fail status:", res_fail.status_code)
    print("res_fail data sample:", res_fail.data[:400].decode('utf-8', errors='ignore'))
    print("Payment settlement unconfirmed in res_fail?:", b"Payment settlement unconfirmed" in res_fail.data)
