import time
import unittest
from unittest.mock import MagicMock
import sys
import os

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock external dependencies before importing app
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

# Import app
# We need to set up environment variables or mock them if app.py reads them at module level
# app.py reads them at module level but uses defaults, so it should be fine.
import app

def benchmark():
    print("Starting benchmark...")

    # Mock DB
    mock_db = MagicMock()
    app.db = mock_db

    # Mock stream to simulate latency
    def delayed_stream():
        time.sleep(0.05) # 50ms latency
        yield MagicMock() # Return one doc

    mock_db.collection.return_value.where.return_value.limit.return_value.stream.side_effect = delayed_stream

    # Clear cache
    app.WHITELIST_CACHE.clear()

    number = "+1234567890"
    iterations = 100

    # Measure Cached (Fast)
    start_time = time.time()
    for _ in range(iterations):
        app.is_number_whitelisted(number)
    end_time = time.time()
    fast_duration = end_time - start_time

    print(f"Cached (Fast): {fast_duration:.4f} seconds for {iterations} calls")
    print(f"Avg time per call: {fast_duration/iterations:.4f} seconds")

    # Measure Uncached (Slow) - Simulated
    # We define it here to mimic the unoptimized code
    def is_number_whitelisted_slow(number):
        try:
            # Simulate DB call
            docs = app.db.collection(app.SMS_WHITELIST_COLLECTION).where('number', '==', number).limit(1).stream()
            for _ in docs:
                return True
            return False
        except Exception:
            return False

    start_time = time.time()
    for _ in range(iterations):
        is_number_whitelisted_slow(number)
    end_time = time.time()
    slow_duration = end_time - start_time

    print(f"Uncached (Slow): {slow_duration:.4f} seconds for {iterations} calls")
    print(f"Avg time per call: {slow_duration/iterations:.4f} seconds")

    if fast_duration > 0:
        speedup = slow_duration / fast_duration
        print(f"Speedup: {speedup:.2f}x")
    else:
        print("Speedup: Infinite (fast duration was 0)")

if __name__ == "__main__":
    benchmark()
