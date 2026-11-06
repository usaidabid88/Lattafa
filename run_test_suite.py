import os
import sys

os.environ['TEST_DB_NAME'] = 'online_shop_perfume_test'

import test_app
success = test_app.run_tests()
if not success:
    sys.exit(1)
