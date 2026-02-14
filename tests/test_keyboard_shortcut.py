import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock dependencies before importing app
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app

class TestKeyboardShortcut(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_keyboard_shortcut_ui_elements(self):
        """
        Verify that keyboard shortcut UI elements are rendered.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')

        # Check for autocomplete attribute
        self.assertIn('autocomplete="current-password"', content, "Password field missing autocomplete attribute")

        # Check for helper text
        self.assertIn('Press <strong>Ctrl+Enter</strong> to send', content, "Helper text missing")

        # Check for JS keydown listener
        self.assertIn("addEventListener('keydown'", content, "Keydown listener missing")
        self.assertIn("e.ctrlKey", content, "Control key check missing")
        self.assertIn("e.metaKey", content, "Meta key check missing")
        self.assertIn("e.key === 'Enter'", content, "Enter key check missing")

if __name__ == '__main__':
    unittest.main()
