import unittest
from unittest.mock import MagicMock, patch, ANY
import sys

# Mock dependencies
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app, db

class TestPersistInput(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Patch app configuration
        self.patchers = [
            patch('app.ACCESS_PASSWORD', 'secret'),
            patch('app.WEBHOOK_URL', 'http://fake-printer'),
            patch('app.CHARACTER_LIMIT', 100),
            patch('app.log_to_firestore', MagicMock())
        ]
        for p in self.patchers:
            p.start()

    def tearDown(self):
        for p in self.patchers:
            p.stop()

    def test_message_persists_on_error(self):
        """
        Verify that the message input is preserved when submission fails (e.g., wrong password).
        """
        # Sending wrong password
        response = self.client.post('/', data={
            'password': 'wrong_password',
            'message': 'This is a test message that should be preserved.'
        })
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')

        # Check if the message is present in the textarea
        # Note: Initially this will fail because it's not implemented
        self.assertIn('This is a test message that should be preserved.', content)

    def test_message_clears_on_success(self):
        """
        Verify that the message input is cleared when submission succeeds.
        """
        with patch('app.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            response = self.client.post('/', data={
                'password': 'secret',
                'message': 'This message should vanish.'
            })
            self.assertEqual(response.status_code, 200)
            content = response.data.decode('utf-8')

            # Message should NOT be in the textarea
            # It might appear in the log or success message, but not in the textarea value
            # Since we check for `>message_content</textarea>`, let's be specific
            # But the message might be empty string which is fine.
            self.assertNotIn('>This message should vanish.</textarea>', content)

if __name__ == '__main__':
    unittest.main()
