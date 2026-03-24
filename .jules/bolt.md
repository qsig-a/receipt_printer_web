## 2026-03-18 - [Offload synchronous pending_ref.set to background thread in sms_webhook]
The synchronous Firestore operation `pending_ref.set()` in the `/sms` webhook route was blocking the network call, slowing down the response. Moving it to be handled by the background ThreadPoolExecutor via `executor.submit(pending_ref.set, ...)` significantly improved the response time. The benchmark showed a speedup from ~1.00s to ~0.02s.

## 2024-03-24 - Async Firestore Operations in SMS Webhook
Wrapped synchronous Firestore operations (`pending_ref.delete()` and `log_to_firestore`) within the SMS webhook handler (`/sms`) with `executor.submit()`. This effectively minimizes response latency in the `/sms` route by backgrounding IO bound operations so they do not block the thread processing the request. This avoids unnecessary thread locking and increases the response speed.
