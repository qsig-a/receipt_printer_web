import time
import unittest
from unittest.mock import patch, MagicMock

import os
os.environ['ACCESS_PASSWORD'] = 'password'
os.environ['WEBHOOK_URL'] = 'http://fake-printer'

import sys
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

import app as app_module
from app import app, db

class BenchmarkIndexPost(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        db.reset_mock()

    @patch('app.log_to_firestore')
    @patch('app.http_session.post')
    def test_benchmark_post_sync(self, mock_post, mock_log_to_firestore):
        # Simulate webhook taking a small amount of time
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Simulate Firestore taking some time (e.g. 1 second)
        def slow_log(*args, **kwargs):
            time.sleep(1.0)
        mock_log_to_firestore.side_effect = slow_log

        start_time = time.time()
        response = self.app.post('/', data={'password': 'password', 'message': 'Hello world'})
        end_time = time.time()

        print(f"\nTime taken for / with synchronous logging: {end_time - start_time:.4f} seconds")
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
