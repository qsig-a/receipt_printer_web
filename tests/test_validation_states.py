import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock dependencies before importing app
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app, ACCESS_PASSWORD

class TestValidationStates(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_aria_invalid_on_access_denied(self):
        response = self.client.post('/', data={'password': 'wrong', 'message': 'test'})
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        self.assertIn('aria-invalid="true"', html)
        self.assertIn('aria-errormessage="status-feedback"', html)

    @patch('app.CHARACTER_LIMIT', 5)
    def test_aria_invalid_on_limit_exceeded(self):
        response = self.client.post('/', data={'password': ACCESS_PASSWORD, 'message': 'aaaaaa'})
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        self.assertIn('aria-invalid="true"', html)
        self.assertIn('aria-errormessage="status-feedback"', html)

    def test_aria_invalid_on_admin_error(self):
        response = self.client.post('/history', data={'admin_password': 'wrong'})
        self.assertEqual(response.status_code, 401)
        html = response.data.decode('utf-8')

        self.assertIn('aria-invalid="true"', html)
        self.assertIn('aria-errormessage="status-feedback"', html)

    def test_js_listener_exists(self):
        response = self.client.get('/')
        html = response.data.decode('utf-8')

        self.assertIn("this.classList.remove('input-error');", html)
        self.assertIn("this.removeAttribute('aria-invalid');", html)
        self.assertIn("this.removeAttribute('aria-errormessage');", html)

if __name__ == '__main__':
    unittest.main()
