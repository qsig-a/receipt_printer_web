import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock google.cloud.firestore before importing app
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app, db

class TestClearHistoryPerf(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.patchers = [
            patch('app.ADMIN_PASSWORD', 'adminsecret'),
            patch('app.db.collection')
        ]
        for p in self.patchers:
            p.start()

    def tearDown(self):
        for p in self.patchers:
            p.stop()

    def test_clear_history_bulk(self):
        pass

if __name__ == '__main__':
    unittest.main()
