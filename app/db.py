"""
db.py – Database connection helper.
WHY: Centralises the MySQL connection so every other module just calls get_connection().
     Credentials are read from .env — never hard-coded.
     Phase 0 test: run this file directly to confirm MySQL is reachable.
"""

import os
import pymysql
from dotenv import load_dotenv

# Load .env from the project root (one level above this file)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


def get_connection():
    """Return a new PyMySQL connection using settings from .env."""
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'online_shop'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,          # We manage transactions explicitly
    )


# ── Phase 0 smoke-test ──────────────────────────────────────────────────────
if __name__ == '__main__':
    try:
        # Connect without specifying a database yet (it may not exist)
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
        )
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION() AS version")
            row = cur.fetchone()
            print(f"[OK] Connected to MySQL  -  Server version: {row['version']}")
        conn.close()
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
