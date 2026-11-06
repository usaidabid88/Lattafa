"""
db.py – Database connection helper.
WHY: Centralises the MySQL connection so every other module just calls get_connection().
     Credentials are read from .env — never hard-coded.
     Supports environment-based TLS/SSL configuration for cloud database connectivity.
     Supports database name overrides for automated testing isolation.
"""

import os
import pymysql
from dotenv import load_dotenv

# Load .env from the project root (one level above this file)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


def get_ssl_config():
    """Build SSL configuration dictionary from environment variables.

    Returns:
        dict or None: SSL configuration dictionary for PyMySQL, or None if unconfigured.
    Raises:
        FileNotFoundError: If DB_SSL_CA is specified but the certificate file does not exist.
        RuntimeError: If in production mode connecting to a remote host without SSL.
    """
    ssl_ca = os.getenv('DB_SSL_CA', '').strip()
    host = os.getenv('DB_HOST', 'localhost').strip().lower()
    is_prod = (os.getenv('APP_ENV') == 'production') or (os.getenv('FLASK_ENV') == 'production') or (os.getenv('PRODUCTION', '0') == '1')
    is_local = host in ('localhost', '127.0.0.1', '::1', 'db')

    if ssl_ca:
        if not os.path.isfile(ssl_ca):
            raise FileNotFoundError(
                f"Configured DB_SSL_CA certificate file was not found: '{ssl_ca}'"
            )
        ssl_config = {'ca': ssl_ca}
        ssl_cert = os.getenv('DB_SSL_CERT', '').strip()
        ssl_key = os.getenv('DB_SSL_KEY', '').strip()
        if ssl_cert and os.path.isfile(ssl_cert):
            ssl_config['cert'] = ssl_cert
        if ssl_key and os.path.isfile(ssl_key):
            ssl_config['key'] = ssl_key
        return ssl_config

    # Enforce SSL requirement in production when connecting to a remote host
    if is_prod and not is_local:
        raise RuntimeError(
            f"Production security policy violation: Remote database host '{host}' requires "
            f"TLS/SSL configuration, but DB_SSL_CA is not configured."
        )

    return None


def get_connection(database=None):
    """Return a new PyMySQL connection using settings from .env or explicit parameters.

    Args:
        database (str, optional): Target database name. If omitted, checks Flask
            current_app.config['DB_NAME'] if inside an active request/app context,
            falling back to os.getenv('DB_NAME', 'online_shop').

    Returns:
        pymysql.connections.Connection: Configured active database connection.
    """
    target_db = database
    if not target_db:
        try:
            from flask import current_app, has_app_context
            if has_app_context() and current_app and current_app.config.get('DB_NAME'):
                target_db = current_app.config['DB_NAME']
        except ImportError:
            pass

    if not target_db:
        target_db = os.getenv('DB_NAME', 'online_shop')

    connect_kwargs = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': target_db,
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor,
        'autocommit': False,  # Transactions managed explicitly
    }

    ssl_config = get_ssl_config()
    if ssl_config:
        connect_kwargs['ssl'] = ssl_config

    return pymysql.connect(**connect_kwargs)


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
