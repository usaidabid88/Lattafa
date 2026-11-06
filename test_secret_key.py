"""
test_secret_key.py - Automated Unit Tests for Flask Secret Key Security (Stage 1.5 Work Package B)
WHY: Validates that production mode strictly enforces a secure FLASK_SECRET_KEY, rejecting missing,
     empty, or placeholder values, while allowing local development and testing environments
     to initialize smoothly.
"""

import os
import unittest
import secrets
from unittest.mock import patch
from flask import Flask


class TestFlaskSecretKeySecurity(unittest.TestCase):
    """Test suite verifying environment-aware secret key configuration and validation."""

    def test_local_dev_with_custom_key(self):
        """Dev mode with custom key loads the key properly."""
        with patch.dict(os.environ, {'APP_ENV': 'development', 'FLASK_SECRET_KEY': 'my-custom-dev-key'}, clear=False):
            from app.app import configure_secret_key
            app = Flask('test_dev_custom')
            configure_secret_key(app)
            self.assertEqual(app.secret_key, 'my-custom-dev-key')

    def test_local_dev_empty_key_generates_ephemeral(self):
        """Dev mode without key auto-generates a secure 64-char hex ephemeral key."""
        with patch.dict(os.environ, {'APP_ENV': 'development', 'FLASK_SECRET_KEY': ''}, clear=False):
            from app.app import configure_secret_key
            app = Flask('test_dev_ephemeral')
            configure_secret_key(app)
            self.assertTrue(len(app.secret_key) >= 32)
            self.assertNotEqual(app.secret_key, 'fallback-dev-secret-key')

    def test_testing_environment_isolated_key(self):
        """Testing mode uses isolated test key and does not reuse production secrets."""
        with patch.dict(os.environ, {'APP_ENV': 'testing', 'FLASK_SECRET_KEY': ''}, clear=False):
            from app.app import configure_secret_key
            app = Flask('test_testing_env')
            configure_secret_key(app)
            self.assertIn('test-isolated-secret-key', app.secret_key)

    def test_production_valid_secret_key_succeeds(self):
        """Production mode with valid high-entropy key initializes successfully."""
        secure_key = secrets.token_hex(32)
        with patch.dict(os.environ, {'APP_ENV': 'production', 'FLASK_SECRET_KEY': secure_key}, clear=False):
            from app.app import configure_secret_key
            app = Flask('test_prod_valid')
            configure_secret_key(app)
            self.assertEqual(app.secret_key, secure_key)

    def test_production_missing_secret_key_raises_error(self):
        """Production mode without FLASK_SECRET_KEY raises RuntimeError."""
        with patch.dict(os.environ, {'APP_ENV': 'production', 'FLASK_SECRET_KEY': ''}, clear=False):
            from app.app import configure_secret_key
            app = Flask('test_prod_missing')
            with self.assertRaises(RuntimeError) as ctx:
                configure_secret_key(app)
            self.assertIn("CRITICAL SECURITY CONFIGURATION ERROR", str(ctx.exception))
            self.assertIn("missing or empty", str(ctx.exception))

    def test_production_short_secret_key_raises_error(self):
        """Production mode with secret key shorter than 16 chars raises RuntimeError."""
        with patch.dict(os.environ, {'APP_ENV': 'production', 'FLASK_SECRET_KEY': 'too_short_key'}, clear=False):
            from app.app import configure_secret_key
            app = Flask('test_prod_short')
            with self.assertRaises(RuntimeError) as ctx:
                configure_secret_key(app)
            self.assertIn("too short", str(ctx.exception))

    def test_production_placeholder_secret_key_raises_error(self):
        """Production mode with obvious placeholder raises RuntimeError."""
        placeholders = [
            'default_dev_key',
            'change_this_to_a_random_string',
            'fallback-dev-secret-key',
            'your_secret_key_here',
            'muet-dbs-production-secret-2026',
        ]
        from app.app import configure_secret_key
        for ph in placeholders:
            with patch.dict(os.environ, {'APP_ENV': 'production', 'FLASK_SECRET_KEY': ph}, clear=False):
                app = Flask('test_prod_placeholder')
                with self.assertRaises(RuntimeError) as ctx:
                    configure_secret_key(app)
                self.assertIn("insecure placeholder", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
