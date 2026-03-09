import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock dependencies
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app, db

class TestHistoryEmptyState(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch('app.get_logs_from_firestore')
    @patch('app.ADMIN_PASSWORD', 'adminsecret')
    def test_history_empty_state(self, mock_get_logs):
        # Case: Empty logs
        mock_get_logs.return_value = []
        response = self.client.post('/history', data={'admin_password': 'adminsecret'})
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')

        # Verify empty state message
        self.assertIn('No print history found', content)
        self.assertIn('📭', content)

        # Verify buttons are disabled
        self.assertIn('disabled title="No logs to download"', content)
        self.assertIn('disabled title="No logs to clear"', content)

    @patch('app.get_logs_from_firestore')
    @patch('app.ADMIN_PASSWORD', 'adminsecret')
    def test_history_with_logs(self, mock_get_logs):
        # Case: Logs exist
        mock_get_logs.return_value = [{'time': 'Now', 'source': 'IP', 'status': 'OK', 'msg': 'Hi', 'iso_time': '2025-01-01T12:00:00'}]
        response = self.client.post('/history', data={'admin_password': 'adminsecret'})
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')

        # Verify message is absent
        self.assertNotIn('No print history found', content)
        # Verify log content is present
        self.assertIn('Hi', content)

        # Verify buttons are NOT disabled
        self.assertNotIn('disabled title="No logs to download"', content)
        self.assertNotIn('disabled title="No logs to clear"', content)

if __name__ == '__main__':
    unittest.main()
