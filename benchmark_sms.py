import time
import unittest
from unittest.mock import patch, MagicMock

# Set env vars to avoid issues loading module
import os
os.environ['ACCESS_PASSWORD'] = 'secret'
os.environ['SIGNALWIRE_PROJECT_ID'] = 'fake_pid'
os.environ['SIGNALWIRE_TOKEN'] = 'fake_token'
os.environ['SIGNALWIRE_SPACE_URL'] = 'fake_url'
os.environ['SIGNALWIRE_FROM_NUMBER'] = 'fake_from'
os.environ['WEBHOOK_URL'] = 'http://fake-printer'

import sys
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

import app as app_module
from app import app, db

class BenchmarkSMS(unittest.TestCase):
    def setUp(self):
        app_module._signalwire_client = None
        self.app = app.test_client()
        db.reset_mock()

        # Default behavior: Document pending check finds nothing
        self.mock_doc_ref = MagicMock()
        self.mock_doc_ref.get.return_value.exists = False
        db.collection.return_value.document.return_value = self.mock_doc_ref
        db.collection.return_value.where.return_value.limit.return_value.stream.return_value = []

    @patch('app.get_signalwire_client')
    def test_benchmark_new_message(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Simulate send_sms taking 1 second
        def slow_send(*args, **kwargs):
            time.sleep(1.0)
            mock_message = MagicMock()
            mock_message.sid = "SM123"
            return mock_message

        mock_client.messages.create.side_effect = slow_send

        start_time = time.time()
        response = self.app.post('/sms', data={'From': '+1234567890', 'Body': 'Hello'})
        end_time = time.time()

        print(f"Time taken for new message: {end_time - start_time:.4f} seconds")
        self.assertEqual(response.status_code, 200)

    @patch('app.get_signalwire_client')
    def test_benchmark_wrong_password(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Simulate send_sms taking 1 second
        def slow_send(*args, **kwargs):
            time.sleep(1.0)
            mock_message = MagicMock()
            mock_message.sid = "SM123"
            return mock_message

        mock_client.messages.create.side_effect = slow_send

        self.mock_doc_ref.get.return_value.exists = True
        self.mock_doc_ref.get.return_value.to_dict.return_value = {'message': 'Hello'}

        start_time = time.time()
        response = self.app.post('/sms', data={'From': '+1234567890', 'Body': 'wrongpass'})
        end_time = time.time()

        print(f"Time taken for wrong password: {end_time - start_time:.4f} seconds")
        self.assertEqual(response.status_code, 200)

    @patch('app.get_signalwire_client')
    def test_benchmark_long_message(self, mock_get_client):
        # Need to patch CHARACTER_LIMIT
        app_module.CHARACTER_LIMIT = 5

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Simulate send_sms taking 1 second
        def slow_send(*args, **kwargs):
            time.sleep(1.0)
            mock_message = MagicMock()
            mock_message.sid = "SM123"
            return mock_message

        mock_client.messages.create.side_effect = slow_send

        start_time = time.time()
        response = self.app.post('/sms', data={'From': '+1234567890', 'Body': 'Too long message'})
        end_time = time.time()

        print(f"Time taken for long message: {end_time - start_time:.4f} seconds")
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
