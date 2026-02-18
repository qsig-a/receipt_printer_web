import unittest
from unittest.mock import MagicMock, patch, ANY
import os
import sys

# Mock dependencies
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app, db

class TestCopyButton(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Mock Firestore response for logs
        self.mock_docs = []
        db.collection.return_value.order_by.return_value.limit.return_value.stream.return_value = self.mock_docs

    @patch('app.ADMIN_PASSWORD', 'adminpassword')
    def test_copy_button_present(self):
        """Verify that the copy button and script exist in the History page HTML."""
        # Create a mock log entry
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {
            'timestamp': None, # Will be "Just now"
            'source': '127.0.0.1',
            'status': 'SUCCESS',
            'message': 'Test Message'
        }
        self.mock_docs.append(mock_doc)

        # Authenticate and get History page
        response = self.client.post('/history', data={'admin_password': 'adminpassword'})
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        # Check for CSS class
        self.assertIn('.copy-btn', html)
        self.assertIn('.msg-cell', html)

        # Check for HTML structure
        self.assertIn('class="msg-cell"', html)
        self.assertIn('class="copy-btn"', html)
        self.assertIn('aria-label="Copy message"', html)
        self.assertIn('onclick="copyToClipboard(this)"', html)

        # Check for Script
        self.assertIn('function copyToClipboard(btn)', html)
        self.assertIn('navigator.clipboard.writeText', html)

if __name__ == '__main__':
    unittest.main()
