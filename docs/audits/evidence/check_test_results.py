import os
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
cursor.execute('SELECT test_id, test_name, status, expected_result, actual_result FROM test_results ORDER BY CAST(SUBSTRING(test_id, 2) AS UNSIGNED)')
rows = cursor.fetchall()
print(f"Total in test_results: {len(rows)}")
for r in rows:
    print(f"  {r['test_id']:4}: [{r['status']}] {r['test_name']}")

cursor.close()
conn.close()
