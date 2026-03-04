import time
import os
import io
import csv
import sys
import psutil
from unittest.mock import MagicMock
from flask import Response

sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app, db, ADMIN_PASSWORD

class MockDoc:
    def __init__(self, t):
        self.t = t
    def to_dict(self):
        return {
            'timestamp': None,
            'source': '127.0.0.1',
            'status': 'SUCCESS',
            'message': 'Hello world ' * 10
        }

def setup_mock_db(doc_count):
    # Instead of generating a list, let's use a generator for docs
    def gen_docs():
        for i in range(doc_count):
            yield MockDoc(i)

    stream_mock = MagicMock()
    stream_mock.return_value = gen_docs()

    order_mock = MagicMock()
    order_mock.limit.return_value.stream = stream_mock
    order_mock.stream = stream_mock

    db.collection.return_value.order_by.return_value = order_mock
    return stream_mock

def bench_optimized():
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024

    # We define the generator logic to simulate what the app will do
    def generate_csv():
        from app import get_logs_from_firestore
        logs = get_logs_from_firestore()

        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['Time', 'Source', 'Status', 'Message'])
        yield si.getvalue()
        si.truncate(0)
        si.seek(0)

        for log in logs:
            cw.writerow([log['time'], log['source'], log['status'], log['msg']])
            yield si.getvalue()
            si.truncate(0)
            si.seek(0)

    # Mocking the route directly for exact streaming behavior measurement
    with app.test_request_context('/download-csv', method='POST', data={'admin_password': ADMIN_PASSWORD}):
        response = Response(generate_csv(), mimetype="text/csv")
        # Consume the stream
        for chunk in response.iter_encoded():
            pass

    mem_after = process.memory_info().rss / 1024 / 1024
    return mem_after - mem_before

if __name__ == '__main__':
    import app as my_app
    doc_count = 500000
    my_app.LOG_HISTORY_LIMIT = doc_count

    setup_mock_db(doc_count)

    start = time.perf_counter()
    mem_diff = bench_optimized()
    end = time.perf_counter()

    print(f"Optimized implementation with {doc_count} logs:")
    print(f"Time: {end - start:.4f}s")
    print(f"Memory Diff (approximate): {mem_diff:.2f} MB")
