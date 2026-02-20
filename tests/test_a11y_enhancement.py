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

class TestA11yEnhancement(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Reset mocks
        db.collection.return_value.document.return_value.get.return_value.exists = False

    @patch('app.CHARACTER_LIMIT', 50)
    def test_textarea_aria_describedby_with_limit(self):
        """
        Verify that aria-describedby includes both shortcut-hint and char-count when limit is set.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')

        # Check for ID on the hint
        self.assertIn('id="shortcut-hint"', content)

        # Check for aria-describedby with both IDs
        self.assertIn('aria-describedby="shortcut-hint char-count"', content)

    @patch('app.CHARACTER_LIMIT', None)
    def test_textarea_aria_describedby_without_limit(self):
        """
        Verify that aria-describedby includes only shortcut-hint when limit is NOT set.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')

        # Check for ID on the hint
        self.assertIn('id="shortcut-hint"', content)

        # Check for aria-describedby with only shortcut-hint
        self.assertIn('aria-describedby="shortcut-hint"', content)

        # Verify char-count is NOT in aria-describedby
        self.assertNotIn('char-count"', content.split('aria-describedby="shortcut-hint')[1].split('"')[0])

if __name__ == '__main__':
    unittest.main()
