import os
import sys
app_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'app')
sys.path.insert(0, app_dir)

from app import app

client = app.test_client()

# 1. Login as zeeshan
client.post('/login', data={'email': 'zeeshan@gmail.com', 'password': 'password123'}, follow_redirects=True)

# 2. Add product 12 to cart
res_add = client.post('/cart/add', data={'product_id': 12, 'quantity': 2}, follow_redirects=True)
print("Add status:", res_add.status_code)

# 3. Post to checkout
res_chk = client.post('/checkout', data={'address_id': 1, 'payment_method': 'cod'}, follow_redirects=True)
print("Checkout status:", res_chk.status_code)
print("Checkout response HTML excerpt (500 chars):")
print(res_chk.data.decode('utf-8', errors='ignore')[:1500])
