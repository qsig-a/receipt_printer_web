import unittest
from unittest.mock import MagicMock
import sys

# Mock dependencies
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app, INDEX_HTML, HISTORY_HTML, ERROR_404_HTML

class TestPageMetadata(unittest.TestCase):
    def test_index_html_metadata(self):
        self.assertIn('<html lang="en">', INDEX_HTML)
        self.assertIn('<title>Remote Print</title>', INDEX_HTML)

    def test_history_html_metadata(self):
        self.assertIn('<html lang="en">', HISTORY_HTML)
        self.assertIn('<title>Print History</title>', HISTORY_HTML)

    def test_error_404_html_metadata(self):
        self.assertIn('<html lang="en">', ERROR_404_HTML)
        self.assertIn('<title>Page Not Found</title>', ERROR_404_HTML)

if __name__ == '__main__':
    unittest.main()
