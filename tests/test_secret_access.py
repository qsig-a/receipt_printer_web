import unittest
from unittest.mock import MagicMock
import sys

# Mock dependencies
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app

class TestSecretAccess(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_secret_access_code_present(self):
        """
        Verify that the secret access code is present in the response.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')

        # Check for the click listener on title
        self.assertIn("document.querySelector('h2')", content)
        self.assertIn("title.addEventListener('click'", content)

        # Check for the obfuscated redirection
        self.assertIn("atob('L2hpc3Rvcnk=')", content)

        # Check for the click counting logic
        self.assertIn("clicks === 5", content)

if __name__ == '__main__':
    unittest.main()
