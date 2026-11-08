"""
tests/conftest.py - Pytest fixtures and test environment setup.
WHY: Centralizes test database configuration and reusable test clients for pytest execution.
"""

import os
import sys
import pytest

# Ensure project root is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Enforce isolated test database
os.environ['TEST_DB_NAME'] = 'online_shop_perfume_test'
os.environ['APP_ENV'] = 'testing'


@pytest.fixture(scope='session')
def app():
    """Provides the Flask application instance configured for isolated testing."""
    from app.app import app as flask_app
    flask_app.config['TESTING'] = True
    flask_app.config['DB_NAME'] = 'online_shop_perfume_test'
    return flask_app


@pytest.fixture(scope='session')
def client(app):
    """Provides a test client for simulating HTTP requests."""
    return app.test_client()
