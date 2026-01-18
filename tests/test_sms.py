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

# Set env vars
os.environ['ACCESS_PASSWORD'] = 'secret'
os.environ['SIGNALWIRE_PROJECT_ID'] = 'fake_pid'
os.environ['SIGNALWIRE_TOKEN'] = 'fake_token'
os.environ['SIGNALWIRE_SPACE_URL'] = 'fake_url'
os.environ['SIGNALWIRE_FROM_NUMBER'] = 'fake_from'

from app import app, db

class TestSMS(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Reset mocks
        db.collection.return_value.document.return_value.get.return_value.exists = False
        db.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {}

    @patch('app.requests.post')
    @patch('app.signalwire_client')
    def test_sms_new_message(self, mock_sw_client, mock_requests_post):
        # Scenario: User sends a new message "Hello"
        # Expectation: Stores "Hello" in Firestore and replies "Please reply with password"

        # Mock Firestore: Document does not exist (new message)
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value.exists = False
        db.collection.return_value.document.return_value = mock_doc_ref

        response = self.client.post('/sms', data={'From': '+1234567890', 'Body': 'Hello'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "OK")

        # Check if saved to pending
        db.collection.assert_any_call("sms_pending")
        mock_doc_ref.set.assert_called_with({
            'message': 'Hello',
            'timestamp': ANY # We can't predict timestamp object easily
        })

        # Check if SMS reply sent
        mock_sw_client.return_value.messages.create.assert_called_with(
            from_='fake_from',
            to='+1234567890',
            body="Please reply with the access password to print your message."
        )

    @patch('app.requests.post')
    @patch('app.signalwire_client')
    def test_sms_verification_success(self, mock_sw_client, mock_requests_post):
        # Scenario: User replies with correct password
        # Expectation: Prints original message, Logs success, Clears pending, Replies "Printed"

        # Mock Firestore: Document exists (pending message "Hello")
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value.exists = True
        mock_doc_ref.get.return_value.to_dict.return_value = {'message': 'Hello'}
        db.collection.return_value.document.return_value = mock_doc_ref

        # Mock Printer Webhook success
        mock_requests_post.return_value.status_code = 200

        response = self.client.post('/sms', data={'From': '+1234567890', 'Body': 'secret'})

        self.assertEqual(response.status_code, 200)

        # Check if printed
        mock_requests_post.assert_called_with(ANY, json={'message': 'Hello'}, timeout=10)

        # Check if logged to history
        # We need to distinguish between pending collection and history collection calls
        # This is a bit tricky with the mock setup, but we can check if set was called with success status
        # A clearer way is to inspect the calls to set()

        # Check if pending deleted
        mock_doc_ref.delete.assert_called()

        # Check if success SMS sent
        mock_sw_client.return_value.messages.create.assert_called_with(
            from_='fake_from',
            to='+1234567890',
            body="✅ Message printed successfully!"
        )

    @patch('app.requests.post')
    @patch('app.signalwire_client')
    def test_sms_verification_failure(self, mock_sw_client, mock_requests_post):
        # Scenario: User replies with wrong password
        # Expectation: Logs DENIED, Replies "Invalid password", Clears pending (as per design)

        # Mock Firestore: Document exists
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value.exists = True
        mock_doc_ref.get.return_value.to_dict.return_value = {'message': 'Hello'}
        db.collection.return_value.document.return_value = mock_doc_ref

        response = self.client.post('/sms', data={'From': '+1234567890', 'Body': 'wrongpass'})

        self.assertEqual(response.status_code, 200)

        # Check NOT printed
        mock_requests_post.assert_not_called()

        # Check if error SMS sent
        mock_sw_client.return_value.messages.create.assert_called_with(
            from_='fake_from',
            to='+1234567890',
            body="❌ Invalid password. Access denied."
        )

        # Check if pending deleted
        mock_doc_ref.delete.assert_called()

if __name__ == '__main__':
    unittest.main()
