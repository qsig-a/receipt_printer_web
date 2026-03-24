## 2026-03-18 - [Offload synchronous pending_ref.set to background thread in sms_webhook]
The synchronous Firestore operation `pending_ref.set()` in the `/sms` webhook route was blocking the network call, slowing down the response. Moving it to be handled by the background ThreadPoolExecutor via `executor.submit(pending_ref.set, ...)` significantly improved the response time. The benchmark showed a speedup from ~1.00s to ~0.02s.

## 2024-05-15 - Offloaded Synchronous pending_ref.delete() in SMS Webhook
- **Optimization Impact**: Replaced synchronous `pending_ref.delete()` calls with `executor.submit(pending_ref.delete)` inside the `/sms` webhook handler.
- **Architecture Bottleneck**: By blocking the webhook thread waiting for the Firestore delete to complete, the response time was tied to network latency and DB speed, limiting concurrent processing capability.
- **Benchmark Results**: In local benchmarking where `pending_ref.delete()` was simulated to take 1.0 seconds:
  - Baseline: Response time took ~1.0 seconds.
  - Improvement: Response time dropped to ~0.005 - 0.008 seconds, completely eliminating the bottleneck and demonstrating a roughly 99% speedup for this specific scenario.
