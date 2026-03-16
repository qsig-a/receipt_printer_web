## 2024-03-15 - [Firestore BulkWriter Optimization]
**Learning:** For deleting multiple documents in Firestore, using the `BulkWriter` API is significantly more performant than the standard approach of fetching and deleting in batches (chunking with a `while` loop). The batch chunking approach performs multiple network requests for streaming and committing. The `BulkWriter` batches operations internally, resulting in fewer network calls and about ~35% speedup.
**Action:** Use `db.bulk_writer()` for high-volume mutations. Ensure `bulk_writer.close()` is called to correctly flush and finalize operations.

## 2024-05-18 - [Connection Pooling for Webhooks]
**Learning:** Making repeated webhook HTTP requests (like sending HomeAssistant or Slack notifications) using `requests.post()` creates a new TCP connection every time. Instantiating and reusing a global `requests.Session()` object (`http_session = requests.Session()`) significantly reduces connection overhead, yielding a ~56% speedup for repeated requests.
**Action:** Use `requests.Session()` instead of the module-level `requests` functions when making multiple requests to the same host or when making frequent outward HTTP calls in the background. Note that this requires updating unit tests to `@patch('app.http_session.post')` instead of `@patch('app.requests.post')`.
