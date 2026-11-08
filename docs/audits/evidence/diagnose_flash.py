import os
import sys
app_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'app')
sys.path.insert(0, app_dir)
from app import app
import re

client = app.test_client()
client.post('/login', data={'email': 'zeeshan@gmail.com', 'password': 'password123'}, follow_redirects=True)
client.post('/cart/add', data={'product_id': 12, 'quantity': 2}, follow_redirects=True)
res_chk = client.post('/checkout', data={'address_id': 1, 'payment_method': 'cod'}, follow_redirects=True)

html = res_chk.data.decode('utf-8', errors='ignore')
alerts = re.findall(r'<div[^>]*class="[^"]*alert[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
print("Alerts found:", len(alerts))
for a in alerts:
    clean = re.sub(r'<[^>]+>', '', a).strip()
    print("  ->", clean)
