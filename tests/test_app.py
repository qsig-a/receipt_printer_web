import unittest
from unittest.mock import MagicMock, patch, ANY
import os
import sys

# Mock google.cloud.firestore before importing app
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()

# Mock signalwire
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app, db

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Reset mocks
        db.collection.return_value.document.return_value.get.return_value.exists = False
        db.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {}

        # Patch app configuration globals
        self.patchers = [
            patch('app.ACCESS_PASSWORD', 'secret'),
            patch('app.ADMIN_PASSWORD', 'adminsecret'),
            patch('app.WEBHOOK_URL', 'http://fake-printer'),
            patch('app.CHARACTER_LIMIT', 100),
            patch('app.log_to_firestore', MagicMock())
        ]
        for p in self.patchers:
            p.start()

    def tearDown(self):
        for p in self.patchers:
            p.stop()

    def test_index_get(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Remote Print", response.data)

    @patch('app.requests.post')
    def test_index_post_success(self, mock_post):
        mock_post.return_value.status_code = 200
        response = self.client.post('/', data={'password': 'secret', 'message': 'Hello'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"PRINT_SUCCESS", response.data)
        mock_post.assert_called_with('http://fake-printer', json={'message': 'Hello'}, timeout=10)

    def test_index_post_invalid_password(self):
        response = self.client.post('/', data={'password': 'wrong', 'message': 'Hello'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ACCESS_DENIED", response.data)

    def test_index_post_too_long(self):
        long_message = 'a' * 101
        response = self.client.post('/', data={'password': 'secret', 'message': long_message})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"LIMIT_EXCEEDED", response.data)

    @patch('app.requests.post')
    def test_index_post_webhook_failure(self, mock_post):
        mock_post.return_value.status_code = 500
        response = self.client.post('/', data={'password': 'secret', 'message': 'Hello'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"HA_ERR", response.data)
        self.assertIn(b"Error: 500", response.data)

    @patch('app.requests.post')
    def test_index_post_connection_failure(self, mock_post):
        mock_post.side_effect = Exception("Connection refused")
        response = self.client.post('/', data={'password': 'secret', 'message': 'Hello'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CONN_FAIL", response.data)
        self.assertIn(b"Connection refused", response.data)

    def test_history_get_unauthorized(self):
        # GET request doesn't show logs, just the form
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Print History", response.data)
        # Should not show logs table
        self.assertNotIn(b"<table", response.data)

    def test_history_post_unauthorized(self):
        response = self.client.post('/history', data={'admin_password': 'wrong'})
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Unauthorized", response.data)

    @patch('app.get_logs_from_firestore')
    def test_history_post_authorized(self, mock_get_logs):
        mock_get_logs.return_value = [{'time': '2023-01-01', 'source': '1.2.3.4', 'status': 'SUCCESS', 'msg': 'Test'}]
        response = self.client.post('/history', data={'admin_password': 'adminsecret'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test", response.data)
        self.assertIn(b"SUCCESS", response.data)

    def test_download_csv_unauthorized(self):
        response = self.client.post('/download-csv', data={'admin_password': 'wrong'})
        self.assertEqual(response.status_code, 401)

    @patch('app.get_logs_from_firestore')
    def test_download_csv_authorized(self, mock_get_logs):
        mock_get_logs.return_value = [{'time': '2023-01-01', 'source': '1.2.3.4', 'status': 'SUCCESS', 'msg': 'Test'}]
        response = self.client.post('/download-csv', data={'admin_password': 'adminsecret'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Disposition'], 'attachment; filename=history.csv')
        self.assertIn(b"Test", response.data)

    def test_clear_history_unauthorized(self):
        response = self.client.post('/clear-history', data={'admin_password': 'wrong'})
        self.assertEqual(response.status_code, 401)

    @patch('app.db')
    def test_clear_history_authorized(self, mock_db):
        # Mock batch deletion
        mock_docs = [MagicMock(), MagicMock()]
        # Mock the chain: db.collection().limit().select([]).stream()
        mock_db.collection.return_value.limit.return_value.select.return_value.stream.return_value = mock_docs

        response = self.client.post('/clear-history', data={'admin_password': 'adminsecret'})
        self.assertEqual(response.status_code, 302) # Redirects to index

        # Verify select([]) was called
        mock_db.collection.return_value.limit.return_value.select.assert_called_with([])

        mock_db.batch.return_value.delete.assert_any_call(mock_docs[0].reference)
        mock_db.batch.return_value.delete.assert_any_call(mock_docs[1].reference)
        mock_db.batch.return_value.commit.assert_called()

if __name__ == '__main__':
    unittest.main()
