import time
import os
import sys
from unittest.mock import MagicMock

# Mock out firebase before doing real stuff
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

# Now import
from app import app, db

# Setup a real benchmark against the actual method implementation via tests

class FirestoreBenchmarkMock:
    def __init__(self, doc_count):
        self.doc_count = doc_count
        self.total_deleted = 0
        self.network_calls = 0
        self.batches_committed = 0
        self.documents = [MagicMock() for _ in range(doc_count)]

    def get_db_mock_for_while_loop(self):
        db_mock = MagicMock()

        # collection -> limit -> select -> stream
        def mock_stream():
            self.network_calls += 1
            batch = self.documents[:500]
            # When batches are deleted, they are removed from DB. So for stream
            # we just take the first 500, and commit removes them from self.documents
            return batch

        stream_mock = MagicMock()
        stream_mock.side_effect = mock_stream

        select_mock = MagicMock()
        select_mock.stream = stream_mock

        limit_mock = MagicMock()
        limit_mock.select.return_value = select_mock

        db_mock.collection.return_value.limit.return_value = limit_mock

        # Batch mock
        batch_mock = MagicMock()
        def mock_delete(ref):
            pass # Just tracking how many

        batch_mock.delete.side_effect = mock_delete

        def mock_commit():
            self.batches_committed += 1
            self.network_calls += 1
            # simulate network wait
            time.sleep(0.01)
            # Remove the 500 docs that were streamed
            batch_size = min(500, len(self.documents))
            self.documents = self.documents[batch_size:]
            self.total_deleted += batch_size

        batch_mock.commit.side_effect = mock_commit

        db_mock.batch.return_value = batch_mock
        return db_mock

    def get_db_mock_for_bulk_writer(self):
        db_mock = MagicMock()

        # collection -> select -> stream
        def mock_stream():
            self.network_calls += 1
            return self.documents

        stream_mock = MagicMock()
        stream_mock.side_effect = mock_stream

        select_mock = MagicMock()
        select_mock.stream = stream_mock

        db_mock.collection.return_value.select.return_value = select_mock

        # BulkWriter mock
        bw_mock = MagicMock()

        def mock_delete(ref):
            self.total_deleted += 1

        bw_mock.delete.side_effect = mock_delete

        def mock_flush():
            self.network_calls += 1
            # simulate some wait for flush
            time.sleep(0.01 * (self.doc_count / 500))
            self.documents = []

        bw_mock.flush.side_effect = mock_flush

        db_mock.bulk_writer.return_value = bw_mock
        return db_mock


def bench_while_loop(doc_count):
    benchmark = FirestoreBenchmarkMock(doc_count)
    db_mock = benchmark.get_db_mock_for_while_loop()

    start_time = time.perf_counter()

    while True:
        docs = db_mock.collection("collection").limit(500).select([]).stream()
        batch = db_mock.batch()
        deleted_in_batch = 0

        # Can't use len(list(docs)) as generators are exhausted
        for doc in docs:
            batch.delete(doc.reference)
            deleted_in_batch += 1

        if deleted_in_batch == 0:
            break

        batch.commit()

    end_time = time.perf_counter()
    return end_time - start_time, benchmark

def bench_bulk_writer(doc_count):
    benchmark = FirestoreBenchmarkMock(doc_count)
    db_mock = benchmark.get_db_mock_for_bulk_writer()

    start_time = time.perf_counter()

    # Notice this drops .limit(500)
    docs = db_mock.collection("collection").select([]).stream()
    bulk_writer = db_mock.bulk_writer()
    for doc in docs:
        bulk_writer.delete(doc.reference)
    bulk_writer.flush()

    end_time = time.perf_counter()
    return end_time - start_time, benchmark

if __name__ == '__main__':
    for doc_count in [500, 5000, 50000]:
        print(f"\n--- Testing with {doc_count} documents ---")

        t1, b1 = bench_while_loop(doc_count)
        print(f"While Loop (limit 500): {t1:.4f}s, Network Calls: {b1.network_calls}, Deleted: {b1.total_deleted}")

        t2, b2 = bench_bulk_writer(doc_count)
        print(f"Bulk Writer (no limit): {t2:.4f}s, Network Calls: {b2.network_calls}, Deleted: {b2.total_deleted}")
