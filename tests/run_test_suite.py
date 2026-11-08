"""
tests/run_test_suite.py - Master Automated Test Harness
Executes all 4 test suites (69 tests) against the isolated testing database (online_shop_perfume_test).
"""

import os
import sys
import unittest

# Enforce isolated test database
os.environ['TEST_DB_NAME'] = 'online_shop_perfume_test'

# Ensure root directory is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from tests.integration import test_app
from tests.integration import test_perfume_suite
from tests.unit import test_secret_key
from tests.unit import test_ssl_db

def main():
    print("========================================================")
    print("  EXECUTING COMPREHENSIVE PROJECT TEST HARNESS")
    print("  Target Database: online_shop_perfume_test")
    print("========================================================\n")

    print("--- SUITE 1: Unified Core E2E Regression Suite (test_app.py) ---")
    e2e_ok = test_app.run_tests()

    print("\n--- SUITE 2: Perfume Domain Transformation Suite (test_perfume_suite.py) ---")
    perfume_suite = unittest.TestLoader().loadTestsFromModule(test_perfume_suite)
    perfume_res = unittest.TextTestRunner(verbosity=2).run(perfume_suite)

    print("\n--- SUITE 3: Secret Key Security Suite (test_secret_key.py) ---")
    secret_suite = unittest.TestLoader().loadTestsFromModule(test_secret_key)
    secret_res = unittest.TextTestRunner(verbosity=2).run(secret_suite)

    print("\n--- SUITE 4: SSL & Database Connectivity Suite (test_ssl_db.py) ---")
    ssl_suite = unittest.TestLoader().loadTestsFromModule(test_ssl_db)
    ssl_res = unittest.TextTestRunner(verbosity=2).run(ssl_suite)

    all_passed = e2e_ok and perfume_res.wasSuccessful() and secret_res.wasSuccessful() and ssl_res.wasSuccessful()

    total_tests = 49 + perfume_res.testsRun + secret_res.testsRun + ssl_res.testsRun
    print("\n========================================================")
    print(f"  ALL TEST SUITES SUMMARY: {total_tests} TESTS EXECUTED")
    print(f"  Core E2E Regression:      {'PASSED (49/49)' if e2e_ok else 'FAILED'}")
    print(f"  Perfume Transformation:  {'PASSED (' + str(perfume_res.testsRun) + '/' + str(perfume_res.testsRun) + ')' if perfume_res.wasSuccessful() else 'FAILED'}")
    print(f"  Secret Key Security:     {'PASSED (' + str(secret_res.testsRun) + '/' + str(secret_res.testsRun) + ')' if secret_res.wasSuccessful() else 'FAILED'}")
    print(f"  SSL Database Config:     {'PASSED (' + str(ssl_res.testsRun) + '/' + str(ssl_res.testsRun) + ')' if ssl_res.wasSuccessful() else 'FAILED'}")
    print(f"  OVERALL HARNESS VERDICT: {'ALL TESTS PASSED (100%)' if all_passed else 'FAILURES DETECTED'}")
    print("========================================================\n")

    if not all_passed:
        sys.exit(1)

if __name__ == '__main__':
    main()
