import unittest
import sys

# load tests
suite = unittest.TestSuite()
loader = unittest.TestLoader()

from tests.test_whitelist_performance import TestWhitelistCacheEviction
from tests.test_sms import TestSMS
from tests.test_app import TestApp

suite.addTests(loader.loadTestsFromTestCase(TestWhitelistCacheEviction))
suite.addTests(loader.loadTestsFromTestCase(TestSMS))
suite.addTests(loader.loadTestsFromTestCase(TestApp))

runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
