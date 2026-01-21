import unittest
from unittest.mock import MagicMock, patch, ANY
import os
import sys
from datetime import datetime, timedelta
import json

# Mock google.cloud.firestore before importing app
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

# Set env vars for Slack Rate Limiting
os.environ['SLACK_MESSAGE_LIMIT'] = '2'
os.environ['SLACK_LIMIT_PERIOD'] = '1' # 1 minute
os.environ['WEBHOOK_URL'] = 'http://fake-printer'

from app import app, db

class TestSlack(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Reset mocks
        db.collection.return_value.document.return_value.get.return_value.exists = False
        db.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {}

    def test_url_verification(self):
        """Test Slack URL verification challenge."""
        data = {
            "token": "Jhj5dZrVaK7ZwHHjRyZWjbDl",
            "challenge": "3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P",
            "type": "url_verification"
        }
        response = self.client.post('/slack', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"challenge": "3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P"})

    @patch('app.process_slack_async')
    @patch('app.requests.post')
    def test_slack_slash_command_success(self, mock_requests_post, mock_process_async):
        """Test a valid Slash Command message that is under the rate limit."""
        # Mock Firestore: User not blocked, no previous messages
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value.exists = False # New user/no history
        db.collection.return_value.document.return_value = mock_doc_ref

        data = {
            'user_id': 'U12345',
            'user_name': 'testuser',
            'text': 'Hello Printer',
            'command': '/print',
            'response_url': 'https://hooks.slack.com/commands/T123/456/789'
        }
        response = self.client.post('/slack', data=data)

        self.assertEqual(response.status_code, 200)
        # Expect the immediate "Sending..." message (Async behavior)
        self.assertIn(b"Sending to printer", response.data)

        # Ensure the background task was started
        mock_process_async.assert_called_once()
        # Ensure the synchronous webhook was NOT called in the main thread
        mock_requests_post.assert_not_called()

        # Check Firestore update (timestamps updated)
        # Should set timestamps with one entry (now)
        # We need to find the call that updated timestamps among all calls (including log_to_firestore)
        found_timestamps_update = False
        for call in mock_doc_ref.set.call_args_list:
            args, _ = call
            if 'timestamps' in args[0]:
                found_timestamps_update = True
                self.assertEqual(len(args[0]['timestamps']), 1)
                break

        self.assertTrue(found_timestamps_update, "Did not find update to timestamps")

    @patch('app.requests.post')
    def test_slack_rate_limit_exceeded(self, mock_requests_post):
        """Test blocking a user who exceeds the rate limit."""
        # Limit is 2 per 1 minute.
        # User has sent 2 messages recently.

        now = datetime.utcnow()
        past = now - timedelta(seconds=10)

        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value.exists = True
        # Timestamps of 2 recent messages
        mock_doc_ref.get.return_value.to_dict.return_value = {
            'timestamps': [past, past],
            'blocked_until': None
        }
        db.collection.return_value.document.return_value = mock_doc_ref

        data = {
            'user_id': 'UHEAVYUSER',
            'user_name': 'spammer',
            'text': 'Spam message',
            'command': '/print'
        }
        response = self.client.post('/slack', data=data)

        # Should be success 200 OK (Slack expects 200 even for error messages usually, but with text)
        self.assertEqual(response.status_code, 200)
        # Should return a blocking message
        self.assertIn(b"blocked", response.data.lower())

        # Webhook should NOT be called
        mock_requests_post.assert_not_called()

        # Firestore should be updated with blocked_until
        args, _ = mock_doc_ref.set.call_args # or update
        self.assertIn('blocked_until', args[0])
        self.assertIsNotNone(args[0]['blocked_until'])

    @patch('app.requests.post')
    def test_slack_currently_blocked(self, mock_requests_post):
        """Test that a blocked user is rejected immediately."""
        now = datetime.utcnow()
        future = now + timedelta(minutes=5)

        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value.exists = True
        mock_doc_ref.get.return_value.to_dict.return_value = {
            'timestamps': [],
            'blocked_until': future
        }
        db.collection.return_value.document.return_value = mock_doc_ref

        data = {
            'user_id': 'UBLOCKED',
            'user_name': 'blockeduser',
            'text': 'Trying again',
            'command': '/print'
        }
        response = self.client.post('/slack', data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"blocked", response.data.lower())

        mock_requests_post.assert_not_called()

if __name__ == '__main__':
    unittest.main()
