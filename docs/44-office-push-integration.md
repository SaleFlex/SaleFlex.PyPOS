# OFFICE Push Integration

This document describes how `SaleFlex.PyPOS` synchronises completed transaction data with a
`SaleFlex.OFFICE` instance when running in **`office` mode**.

---

## Overview

When `app.mode = "office"` is set in `settings.toml`, every closed document (completed or
cancelled transaction) is automatically pushed to the OFFICE REST API in a **background thread**
so that the cashier's workflow is never interrupted.

Key behaviours:

| Scenario | Behaviour |
|----------|-----------|
| Document closed, OFFICE reachable | Transaction sent immediately in a parallel thread |
| Document closed, OFFICE unreachable | Entry queued as `pending`; retried on next document close |
| No document activity for ≥ 1 hour | Background `OfficePushWorker` flushes all `pending`/`failed` items |
| OFFICE intermittently reachable | Items accumulate in `office_push_queue`; sent in a single batch on next success |

---

## Architecture

```
  Document closed
        │
        ▼
 DocumentManager.complete_document()
        │
        ├── OfficePushService.enqueue()       ← adds row to office_push_queue
        │
        └── threading.Thread(target=flush_pending).start()   ← parallel push
                    │
                    ├── OFFICE reachable?
                    │       Yes → HTTP POST /api/v1/pos/transactions
                    │             mark queue items "sent"
                    │
                    └──  No  → mark items "failed"
                                  │
                                  └── OfficePushWorker (QThread, 1-hour loop)
                                        └── flush_pending() on schedule
```

---

## Components

### `pos/integration/office/office_push_service.py` — `OfficePushService`

| Method | Description |
|--------|-------------|
| `is_office_mode()` | Returns `True` when `app.mode == "office"` |
| `enqueue(head_id, tx_unique_id)` | Adds a `pending` row to `office_push_queue` |
| `flush_pending()` | Pushes all `pending`/`failed` items to OFFICE in one HTTP call |
| `has_pending()` | Returns `True` when unsent items exist in the queue |

### `pos/manager/office_push_worker.py` — `OfficePushWorker`

A `QThread` subclass that wakes every `retry_interval_seconds` (default **3600 s = 1 hour**) and
calls `OfficePushService.flush_pending()` when there are unsent items.

The retry interval is read from `[office].sync_interval_minutes` in `settings.toml`.

### `integration/office_client.py` — `OfficeClient` (extended)

Two new methods added to the existing OFFICE HTTP client:

| Method | HTTP call |
|--------|-----------|
| `push_transactions(pos_id, transactions, sequences)` | `POST /api/v1/pos/transactions` |
| `push_sequences(pos_id, sequences)` | `POST /api/v1/pos/sequences` |

### `data_layer/model/definition/office_push_queue.py` — `OfficePushQueue`

Local SQLite table that tracks every document awaiting delivery to OFFICE.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `fk_transaction_head_id` | UUID | FK → `transaction_head.id` |
| `transaction_unique_id` | String | Human-readable transaction ID |
| `status` | String | `pending` / `sent` / `failed` |
| `retry_count` | Integer | Number of failed attempts |
| `sent_at` | DateTime | Timestamp of successful delivery |
| `last_attempt_at` | DateTime | Timestamp of most recent attempt |
| `error_message` | String | Last error from OFFICE |

---

## Payload Format

Each document close triggers one HTTP `POST` to `/api/v1/pos/transactions` with all
pending documents batched together:

```json
{
  "office_code":   "OFFICE-001",
  "store_code":    "STORE-001",
  "terminal_code": "POS-01",
  "pos_id":        1,
  "transactions": [
    {
      "head":           { ... TransactionHead fields ... },
      "products":       [ ... TransactionProduct rows ... ],
      "payments":       [ ... TransactionPayment rows ... ],
      "discounts":      [ ... ],
      "departments":    [ ... ],
      "taxes":          [ ... ],
      "tips":           [ ... ],
      "surcharges":     [ ... ],
      "notes":          [ ... ],
      "loyalty":        [ ... ],
      "refunds":        [ ... ],
      "changes":        [ ... ],
      "deliveries":     [ ... ],
      "kitchen_orders": [ ... ],
      "fiscal":         { ... } or null
    }
  ],
  "sequences": [
    { "name": "ReceiptNumber", "value": 42 },
    { "name": "ClosureNumber", "value":  3 }
  ]
}
```

OFFICE response:

```json
{ "status": "ok", "accepted": 1, "rejected": 0 }
```

---

## Sequence Number Synchronisation

Every push request includes the current values of **all** `TransactionSequence` rows (e.g.
`ReceiptNumber`, `ClosureNumber`) from the PyPOS local database. OFFICE stores these values
in its own `transaction_sequence` table indexed by `(name, pos_id)` so that each terminal's
counters are maintained independently.

---

## Configuration (`settings.toml`)

```toml
[app]
mode = "office"            # Enable office-push behaviour

[office]
base_url = "http://192.168.1.10:9000"
api_prefix = "/api/v1"
timeout_seconds = 15
sync_interval_minutes = 60   # OfficePushWorker retry interval (default: 60 min)
```

---

## Lifecycle

1. **Application start** – `IntegrationMixin.init_integration()` calls
   `_start_office_push_worker()` which launches the `OfficePushWorker` QThread.
2. **Document close** – `DocumentManager.complete_document()` enqueues the document and
   spawns a daemon thread to flush the queue immediately.
3. **Push success** – Queue item is marked `sent`.
4. **Push failure** – Queue item is marked `failed`.
5. **Hourly retry** – `OfficePushWorker` wakes, detects pending items, and flushes.
6. **Application exit** – The QThread is a daemon; it stops when the main process exits.
