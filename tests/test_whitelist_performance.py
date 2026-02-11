import unittest
from unittest.mock import MagicMock, patch
import sys
import time
from collections import OrderedDict

# Mock external dependencies
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

# Import app
from app import is_number_whitelisted, db, WHITELIST_CACHE, WHITELIST_CACHE_LIMIT

class TestWhitelistCacheEviction(unittest.TestCase):
    def setUp(self):
        # Clear cache
        WHITELIST_CACHE.clear()
        # Reset mock
        db.reset_mock()

        # Mock DB response to return one document (whitelisted)
        self.mock_stream = MagicMock()
        self.mock_stream.return_value = [MagicMock()] # 1 doc
        db.collection.return_value.where.return_value.limit.return_value.stream = self.mock_stream

    def test_eviction_strategy(self):
        # Fill cache up to the limit
        for i in range(WHITELIST_CACHE_LIMIT):
            number = f"+1{i:010d}"
            is_number_whitelisted(number)

        # Access item 0 again to refresh it (move to end)
        first_number = f"+1{0:010d}"
        is_number_whitelisted(first_number)

        # Now add one more item (1000)
        # Should evict item 1 (the new head)
        new_number = "+19999999999"
        is_number_whitelisted(new_number)

        # At this point:
        # Item 0: Refreshed, SAFE.
        # Item 1: Evicted (LRU victim).
        # Item 2: Head of LRU, SAFE.

        # Check Item 2 (Safe) FIRST
        third_number = f"+1{2:010d}"
        self.mock_stream.reset_mock()
        is_number_whitelisted(third_number)
        if self.mock_stream.call_count == 0:
            print("Item 2 (Safe) was correctly FOUND in cache.")
        else:
            print("Item 2 (Safe) was INCORRECTLY evicted.")

        self.assertEqual(self.mock_stream.call_count, 0, "Item 2 should remain in cache")

        # Check Item 0 (Refreshed)
        self.mock_stream.reset_mock()
        is_number_whitelisted(first_number)
        if self.mock_stream.call_count == 0:
            print("Item 0 (Refreshed) was correctly FOUND in cache.")
        else:
            print("Item 0 (Refreshed) was INCORRECTLY evicted.")

        self.assertEqual(self.mock_stream.call_count, 0, "Item 0 should remain in cache")

        # Check Item 1 (LRU victim) LAST
        second_number = f"+1{1:010d}"
        self.mock_stream.reset_mock()
        is_number_whitelisted(second_number)
        if self.mock_stream.call_count == 1:
            print("Item 1 (LRU victim) was correctly EVICTED.")
        else:
            print("Item 1 (LRU victim) was INCORRECTLY found in cache.")

        self.assertEqual(self.mock_stream.call_count, 1, "Item 1 should have been evicted")

if __name__ == '__main__':
    unittest.main()
