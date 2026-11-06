with open('app/app.py', 'r', encoding='utf-8') as f:
    c = f.read()

dup = """    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(\"\"\"
            SELECT * FROM v_perfume_catalog
            WHERE collection_name LIKE %s AND is_active = 1
            ORDER BY is_featured DESC, price ASC
        \"\"\")
        col_param = f"%{col_name}%"
        cur.execute(\"\"\"
            SELECT * FROM v_perfume_catalog
            WHERE collection_name LIKE %s AND is_active = 1
            ORDER BY is_featured DESC, price ASC
        \"\"\", (col_param,))"""

clean = """    conn = get_db()
    with conn.cursor() as cur:
        col_param = f"%{col_name}%"
        cur.execute(\"\"\"
            SELECT * FROM v_perfume_catalog
            WHERE collection_name LIKE %s AND is_active = 1
            ORDER BY is_featured DESC, price ASC
        \"\"\", (col_param,))"""

if dup in c:
    c = c.replace(dup, clean, 1)
    with open('app/app.py', 'w', encoding='utf-8', newline='\n') as f:
        f.write(c)
    print("SUCCESS: Removed duplicate cur.execute in collection_view")
else:
    print("WARNING: Exact dup block not found, checking...")
