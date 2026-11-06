import json

with open('audits/evidence/db_inventory.json', 'r', encoding='utf-8') as f:
    inv = json.load(f)

actual_tables = set(inv['tables'].keys()) - {'test_results'}
print(f"Total actual business tables: {len(actual_tables)}")

expected_tables = {
    'users', 'addresses', 'audit_log', 'support_tickets',
    'brands', 'categories', 'suppliers', 'products', 'product_images', 'reviews',
    'delivery_rates', 'tax_rates', 'payment_methods', 'carts', 'cart_items',
    'orders', 'order_items', 'order_status_history', 'payments', 'payment_attempts',
    'shipments', 'return_requests', 'return_status_history'
}

missing_in_db = expected_tables - actual_tables
unexpected_in_db = actual_tables - expected_tables

print(f"Missing in DB: {missing_in_db}")
print(f"Unexpected in DB: {unexpected_in_db}")

for t in sorted(expected_tables):
    cols = inv['tables'][t]['columns']
    fks = [fk['COLUMN_NAME'] for fk in inv['tables'][t]['foreign_keys']]
    print(f"Table {t:22}: {len(cols)} columns, {len(fks)} FKs")
