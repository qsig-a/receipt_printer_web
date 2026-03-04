import time
import os
import sys

# Mock modules before importing app
from unittest.mock import MagicMock
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app, db

def run_benchmark(docs_count, chunk_size, use_bulk=False):
    # Setup mock document references
    mock_docs = [MagicMock() for _ in range(docs_count)]

    # Track the docs left to delete
    state = {'docs': mock_docs.copy()}
    stats = {'batches_committed': 0, 'deletes_called': 0, 'network_calls': 0}

    # Setup mocks
    db_mock = MagicMock()

    # 1. Batch API Mocks
    def mock_stream():
        stats['network_calls'] += 1
        return state['docs'][:chunk_size]

    # Mock for standard batch approach
    query_mock = MagicMock()
    query_mock.stream.side_effect = mock_stream
    select_mock = MagicMock()
    select_mock.select.return_value = query_mock
    limit_mock = MagicMock()
    limit_mock.limit.return_value = select_mock
    db_mock.collection.return_value = limit_mock

    batch_mock = MagicMock()
    def mock_delete(ref):
        stats['deletes_called'] += 1
    batch_mock.delete.side_effect = mock_delete

    def mock_commit():
        stats['batches_committed'] += 1
        stats['network_calls'] += 1
        time.sleep(0.005) # Simulating network latency
        # In reality, commit removes from DB, so our next stream gets less
        state['docs'] = state['docs'][chunk_size:]

    batch_mock.commit.side_effect = mock_commit
    db_mock.batch.return_value = batch_mock

    # 2. BulkWriter API Mocks
    def mock_stream_all():
        stats['network_calls'] += 1
        return state['docs']

    query_all_mock = MagicMock()
    query_all_mock.stream.side_effect = mock_stream_all
    select_all_mock = MagicMock()
    select_all_mock.select.return_value = query_all_mock
    # collection is mocked above, but for bulk writer we might not use limit
    # so we need a separate path if needed, but let's just use the logic

    bw_mock = MagicMock()
    def bw_delete(ref):
        stats['deletes_called'] += 1
    bw_mock.delete.side_effect = bw_delete
    def bw_flush():
        stats['network_calls'] += 1
        time.sleep(0.01) # flush latency
        state['docs'] = []
    def bw_close():
        bw_flush()
    bw_mock.flush.side_effect = bw_flush
    bw_mock.close.side_effect = bw_close

    db_mock.bulk_writer.return_value = bw_mock

    start_time = time.perf_counter()

    # Simulate the code that would be in clear_history
    if not use_bulk:
        # The corrected `while` loop implementation (standard Firestore pattern)
        while True:
            docs = db_mock.collection("collection").limit(chunk_size).select([]).stream()
            batch = db_mock.batch()
            doc_count = 0
            for doc in docs:
                batch.delete(doc.reference)
                doc_count += 1
            if doc_count == 0:
                break
            batch.commit()
    else:
        # Optimization: using BulkWriter
        docs = db_mock.collection("collection").select([]).stream()
        bulk_writer = db_mock.bulk_writer()
        for doc in docs:
            bulk_writer.delete(doc.reference)
        bulk_writer.flush()
        # in some versions it's flush, or close, or context manager

    end_time = time.perf_counter()
    duration = end_time - start_time

    return {
        'duration': duration,
        'docs_deleted': stats['deletes_called'],
        'docs_intended': docs_count,
        'network_calls': stats['network_calls'],
        'batches_committed': stats['batches_committed'],
        'success': stats['deletes_called'] == docs_count
    }

if __name__ == '__main__':
    DOCS = 5000
    CHUNK = 500

    print(f"Benchmarking deletion of {DOCS} documents...")

    # 1. Standard While Loop (Batch)
    res1 = run_benchmark(DOCS, CHUNK)
    print(f"\n1. Standard While Loop (Batch)")
    print(f"  Time: {res1['duration']:.4f}s")
    print(f"  Deleted: {res1['docs_deleted']}/{res1['docs_intended']}")
    print(f"  Network Calls: {res1['network_calls']}")
    print(f"  Batches: {res1['batches_committed']}")

    # 2. Bulk Writer
    # res3 = run_benchmark(DOCS, CHUNK, use_bulk=True)
    # print(f"\n3. Bulk Writer API (Optimized)")
    # print(f"  Time: {res3['duration']:.4f}s")
    # print(f"  Deleted: {res3['docs_deleted']}/{res3['docs_intended']}")
    # print(f"  Network Calls: {res3['network_calls']}")


def run_benchmark_bulk(docs_count, chunk_size):
    import time
    from unittest.mock import MagicMock
    mock_docs = [MagicMock() for _ in range(docs_count)]
    state = {'docs': mock_docs.copy()}
    stats = {'deletes_called': 0, 'network_calls': 0}

    db_mock = MagicMock()

    def mock_stream():
        stats['network_calls'] += 1
        return state['docs']

    query_mock = MagicMock()
    query_mock.stream.side_effect = mock_stream
    select_mock = MagicMock()
    select_mock.select.return_value = query_mock
    db_mock.collection.return_value = select_mock

    bw_mock = MagicMock()
    def mock_delete(ref):
        stats['deletes_called'] += 1
    bw_mock.delete.side_effect = mock_delete
    def mock_flush():
        stats['network_calls'] += 1
        time.sleep(0.005 * (docs_count / 500)) # approximate network time for parallel batches
    bw_mock.flush.side_effect = mock_flush
    db_mock.bulk_writer.return_value = bw_mock

    start_time = time.perf_counter()

    # Bulk Writer pattern
    docs = db_mock.collection("collection").select([]).stream()
    bulk_writer = db_mock.bulk_writer()
    for doc in docs:
        bulk_writer.delete(doc.reference)
    bulk_writer.flush()

    end_time = time.perf_counter()
    return {
        'duration': end_time - start_time,
        'docs_deleted': stats['deletes_called'],
        'docs_intended': docs_count,
        'network_calls': stats['network_calls']
    }

if __name__ == '__main__':
    res3 = run_benchmark_bulk(DOCS, CHUNK)
    print(f"\n3. Bulk Writer API (Optimized)")
    print(f"  Time: {res3['duration']:.4f}s")
    print(f"  Deleted: {res3['docs_deleted']}/{res3['docs_intended']}")
    print(f"  Network Calls: {res3['network_calls']}")
