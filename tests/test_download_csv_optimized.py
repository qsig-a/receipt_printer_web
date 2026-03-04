import unittest
from unittest.mock import MagicMock
import sys
import io
import csv

sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app, db

class TestDownloadCSV(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        db.reset_mock()

    def test_download_csv_content(self):
        class MockDoc:
            def __init__(self, msg):
                self.msg = msg
            def to_dict(self):
                return {
                    'timestamp': None,
                    'source': 'test-source',
                    'status': 'SUCCESS',
                    'message': self.msg
                }

        docs = [MockDoc("msg1"), MockDoc("msg2")]

        # Setup mock db
        stream_mock = MagicMock()
        stream_mock.return_value = docs

        order_mock = MagicMock()
        order_mock.limit.return_value.stream = stream_mock
        order_mock.stream = stream_mock

        db.collection.return_value.order_by.return_value = order_mock

        response = self.app.post('/download-csv', data={'admin_password': 'adminpassword'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/csv')

        # Validate CSV content
        content = response.data.decode('utf-8')
        lines = content.strip().split('\r\n')
        self.assertEqual(len(lines), 3) # Header + 2 rows
        self.assertTrue(lines[0].startswith('Time,Source,Status,Message'))
        self.assertTrue('msg1' in lines[1])
        self.assertTrue('msg2' in lines[2])

if __name__ == '__main__':
    unittest.main()
