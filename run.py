"""
run.py - Primary Application Entry Point for Development and Demonstration
Usage:
    python run.py
"""

import os
import sys
from dotenv import load_dotenv

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Load environment configuration from .env
load_dotenv(os.path.join(root_dir, '.env'))

from app.app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_DEBUG', '1').strip().lower() in ('1', 'true', 'yes')

    print("==================================================")
    print("  LUXE FRAGRANCE - ONLINE SHOPPING SYSTEM")
    print(f"  Running on: http://{host}:{port}/")
    print(f"  Debug mode: {debug}")
    print(f"  Active DB:  {os.environ.get('DB_NAME', 'online_shop_perfume_dev')}")
    print("==================================================")

    app.run(host=host, port=port, debug=debug)
