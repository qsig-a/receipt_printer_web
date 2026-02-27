import unittest
from unittest.mock import MagicMock
import sys

# Mock dependencies before importing app
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app

class TestErrorPages(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_404_page(self):
        """Test that a non-existent route returns a custom 404 page."""
        response = self.client.get('/non-existent-page')
        self.assertEqual(response.status_code, 404)
        content = response.data.decode('utf-8')
        self.assertIn('Page Not Found', content)
        self.assertIn('Return Home', content)
        self.assertIn('href="/"', content)

if __name__ == '__main__':
    unittest.main()
