import unittest
from unittest.mock import MagicMock
import sys

# Mock dependencies before importing app
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app

class TestShakeAnimation(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_shake_animation_css_present(self):
        """Verify that the shake animation CSS is present in the rendered HTML."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        # Check for keyframes definition
        self.assertIn('@keyframes shake', html)
        self.assertIn('transform: translateX(-5px);', html)
        self.assertIn('transform: translateX(5px);', html)

        # Check for media query
        self.assertIn('@media (prefers-reduced-motion: no-preference)', html)

        # Check for animation application
        self.assertIn('animation: shake 0.4s cubic-bezier(.36,.07,.19,.97) both;', html)

        # Check for slideDown keyframes and animation on status box
        self.assertIn('@keyframes slideDown', html)
        self.assertIn('animation: slideDown 0.3s ease-out both;', html)

    def test_shake_animation_history_css_present(self):
        """Verify that the shake animation CSS is present in the History page HTML."""
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        # Since SHARED_CSS is used, it should be here too
        self.assertIn('@keyframes shake', html)
        self.assertIn('animation: shake 0.4s', html)

if __name__ == '__main__':
    unittest.main()
