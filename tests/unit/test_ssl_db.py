"""
test_ssl_db.py - Automated verification for Work Package B (Database TLS/SSL Support)
Verifies Quality Gates:
- SG-03: Local database connectivity without remote SSL requirement preserved.
- SG-04: Secure remote TLS/SSL configuration loading and error handling.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch

# Ensure project root and app package are in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
app_dir = os.path.join(root_dir, 'app')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from db import get_ssl_config, get_connection


class TestDatabaseSSLConfiguration(unittest.TestCase):
    """Test suite for environment-based database SSL/TLS configuration."""

    def test_local_connection_no_ssl_default(self):
        """SG-03: Local connections on localhost do not require SSL configuration."""
        with patch.dict(os.environ, {'DB_HOST': 'localhost', 'DB_SSL_CA': ''}, clear=False):
            ssl_cfg = get_ssl_config()
            self.assertIsNone(ssl_cfg, "Localhost connection should not require SSL by default.")

    def test_valid_ca_certificate_loads_ssl_dict(self):
        """SG-04: Providing a valid CA certificate path configures PyMySQL ssl dictionary."""
        with tempfile.NamedTemporaryFile(suffix='.pem', delete=False) as tmp_ca:
            tmp_ca.write(b"-----BEGIN CERTIFICATE-----\nFAKECA\n-----END CERTIFICATE-----\n")
            tmp_ca_path = tmp_ca.name

        try:
            with patch.dict(os.environ, {'DB_SSL_CA': tmp_ca_path}, clear=False):
                ssl_cfg = get_ssl_config()
                self.assertIsNotNone(ssl_cfg)
                self.assertIn('ca', ssl_cfg)
                self.assertEqual(ssl_cfg['ca'], tmp_ca_path)
        finally:
            if os.path.exists(tmp_ca_path):
                os.unlink(tmp_ca_path)

    def test_missing_ca_certificate_raises_file_not_found(self):
        """SG-04: A non-existent DB_SSL_CA path raises a descriptive FileNotFoundError."""
        non_existent_path = os.path.join(tempfile.gettempdir(), 'non_existent_ca_cert_12345.pem')
        if os.path.exists(non_existent_path):
            os.unlink(non_existent_path)

        with patch.dict(os.environ, {'DB_SSL_CA': non_existent_path}, clear=False):
            with self.assertRaises(FileNotFoundError) as ctx:
                get_ssl_config()
            self.assertIn("Configured DB_SSL_CA certificate file was not found", str(ctx.exception))

    def test_production_remote_host_without_ssl_raises_error(self):
        """SG-04: In production, connecting to a remote host without SSL raises RuntimeError."""
        env_overrides = {
            'FLASK_ENV': 'production',
            'DB_HOST': 'mysql-remote.aivencloud.com',
            'DB_SSL_CA': ''
        }
        with patch.dict(os.environ, env_overrides, clear=False):
            with self.assertRaises(RuntimeError) as ctx:
                get_ssl_config()
            self.assertIn("Production security policy violation", str(ctx.exception))

    def test_production_local_host_allowed_without_ssl(self):
        """SG-03: In production, local containers (host='db' or 'localhost') do not require external SSL."""
        env_overrides = {
            'FLASK_ENV': 'production',
            'DB_HOST': 'db',
            'DB_SSL_CA': ''
        }
        with patch.dict(os.environ, env_overrides, clear=False):
            ssl_cfg = get_ssl_config()
            self.assertIsNone(ssl_cfg)

    def test_database_connection_to_test_db(self):
        """SG-03: Live database connection connects successfully to online_shop_test."""
        conn = get_connection(database='online_shop_test')
        self.assertIsNotNone(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT DATABASE() AS current_db")
            row = cur.fetchone()
            self.assertEqual(row['current_db'], 'online_shop_test')
        conn.close()


def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDatabaseSSLConfiguration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
