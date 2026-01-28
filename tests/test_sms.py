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

import app as app_module
from app import app, db

class TestSMS(unittest.TestCase):
    def setUp(self):
        # Reset global client to ensure fresh initialization for each test
        app_module._signalwire_client = None

        self.client = app.test_client()

        # Reset mocks
        db.reset_mock()

        # Default behavior: Whitelist check finds nothing
        # db.collection(...).where(...).limit(1).stream() -> []
        db.collection.return_value.where.return_value.limit.return_value.stream.return_value = []

        # Default behavior: Document pending check finds nothing
        self.mock_doc_ref = MagicMock()
        self.mock_doc_ref.get.return_value.exists = False
        self.mock_doc_ref.get.return_value.to_dict.return_value = {}
        db.collection.return_value.document.return_value = self.mock_doc_ref

        # Patch app configuration globals
        self.patchers = [
            patch('app.SIGNALWIRE_PROJECT_ID', 'fake_pid'),
            patch('app.SIGNALWIRE_TOKEN', 'fake_token'),
            patch('app.SIGNALWIRE_SPACE_URL', 'fake_url'),
            patch('app.SIGNALWIRE_FROM_NUMBER', 'fake_from'),
            patch('app.ACCESS_PASSWORD', 'secret'),
            patch('app.WEBHOOK_URL', 'http://fake-printer')
        ]
        for p in self.patchers:
            p.start()

    def tearDown(self):
        for p in self.patchers:
            p.stop()

    @patch('app.requests.post')
    @patch('app.signalwire_client')
    def test_sms_new_message(self, mock_sw_client, mock_requests_post):
        # Scenario: User sends a new message "Hello"
        # Expectation: Stores "Hello" in Firestore and replies "Please reply with password"

        response = self.client.post('/sms', data={'From': '+1234567890', 'Body': 'Hello'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "OK")

        # Check if saved to pending
        db.collection.assert_any_call("sms_pending")
        self.mock_doc_ref.set.assert_called_with({
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
        self.mock_doc_ref.get.return_value.exists = True
        self.mock_doc_ref.get.return_value.to_dict.return_value = {'message': 'Hello'}

        # Mock Printer Webhook success
        mock_requests_post.return_value.status_code = 200

        response = self.client.post('/sms', data={'From': '+1234567890', 'Body': 'secret'})

        self.assertEqual(response.status_code, 200)

        # Check if printed
        mock_requests_post.assert_called_with(ANY, json={'message': 'Hello'}, timeout=10)

        # Check if pending deleted
        self.mock_doc_ref.delete.assert_called()

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
        self.mock_doc_ref.get.return_value.exists = True
        self.mock_doc_ref.get.return_value.to_dict.return_value = {'message': 'Hello'}

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
        self.mock_doc_ref.delete.assert_called()

    @patch('app.requests.post')
    @patch('app.signalwire_client')
    def test_sms_whitelist(self, mock_sw_client, mock_requests_post):
        # Scenario: User sends a message from a whitelisted number
        # Expectation: Prints directly without asking for password

        # Mock Whitelist check finding a match
        db.collection.return_value.where.return_value.limit.return_value.stream.return_value = [MagicMock()]

        # Mock Printer Webhook success
        mock_requests_post.return_value.status_code = 200

        response = self.client.post('/sms', data={'From': '+1999999999', 'Body': 'Direct Print'})

        self.assertEqual(response.status_code, 200)

        # Check if printed
        mock_requests_post.assert_called_with(ANY, json={'message': 'Direct Print'}, timeout=10)

        # Check if success SMS sent
        mock_sw_client.return_value.messages.create.assert_called_with(
            from_='fake_from',
            to='+1999999999',
            body="✅ Message printed successfully!"
        )
