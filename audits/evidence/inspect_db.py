import os
import json
import pymysql
from dotenv import load_dotenv

load_dotenv()

conn = pymysql.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'online_shop')
)
cursor = conn.cursor(pymysql.cursors.DictCursor)

inventory = {}

# 1. Base Tables and Row Counts
cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
table_names = [list(r.values())[0] for r in cursor.fetchall()]
inventory['tables'] = {}
for t in sorted(table_names):
    cursor.execute(f"SELECT COUNT(*) as cnt FROM `{t}`")
    cnt = cursor.fetchone()['cnt']
    
    # Columns
    cursor.execute(f"DESCRIBE `{t}`")
    cols = cursor.fetchall()
    
    # Foreign Keys
    cursor.execute("""
        SELECT COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND REFERENCED_TABLE_NAME IS NOT NULL
    """, (t,))
    fks = cursor.fetchall()

    inventory['tables'][t] = {
        'row_count': cnt,
        'columns': [c['Field'] for c in cols],
        'foreign_keys': fks
    }

# 2. Views
cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
view_names = [list(r.values())[0] for r in cursor.fetchall()]
inventory['views'] = {}
for v in sorted(view_names):
    try:
        cursor.execute(f"SELECT COUNT(*) as cnt FROM `{v}`")
        cnt = cursor.fetchone()['cnt']
        inventory['views'][v] = {'status': 'VALID', 'row_count': cnt}
    except Exception as e:
        inventory['views'][v] = {'status': 'ERROR', 'error': str(e)}

# 3. Stored Procedures
cursor.execute("""
    SELECT ROUTINE_NAME, ROUTINE_DEFINITION, SECURITY_TYPE, DEFINER
    FROM INFORMATION_SCHEMA.ROUTINES
    WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_TYPE = 'PROCEDURE'
""")
inventory['procedures'] = [r['ROUTINE_NAME'] for r in cursor.fetchall()]

# 4. Triggers
cursor.execute("""
    SELECT TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE, ACTION_TIMING
    FROM INFORMATION_SCHEMA.TRIGGERS
    WHERE TRIGGER_SCHEMA = DATABASE()
""")
inventory['triggers'] = cursor.fetchall()

# 5. MySQL Roles
cursor.execute("SELECT user, host FROM mysql.user WHERE account_locked = 'Y' OR user LIKE 'shop_%'")
inventory['roles_and_users'] = cursor.fetchall()

with open('audits/evidence/db_inventory.json', 'w', encoding='utf-8') as f:
    json.dump(inventory, f, indent=2, default=str)

print("Database inventory complete.")
print(f"Tables: {len(inventory['tables'])}")
print(f"Views: {len(inventory['views'])}")
print(f"Procedures: {len(inventory['procedures'])}")
print(f"Triggers: {len(inventory['triggers'])}")
print(f"Roles/Special Users: {len(inventory['roles_and_users'])}")

cursor.close()
conn.close()
