# OFFICE Push Integration

This document describes how `SaleFlex.PyPOS` synchronises completed transaction and
end-of-day closure data with a `SaleFlex.OFFICE` instance when running in **`office` mode**.

---

## Overview

When `app.mode = "office"` is set in `settings.toml`, every closed document and completed
end-of-day closure is queued locally and pushed to the OFFICE REST API by a background
`QThread` so that the cashier's workflow is never interrupted.

Key behaviours:

| Scenario | Behaviour |
|----------|-----------|
| Document or closure completed, OFFICE reachable | Pending documents and closures are sent immediately by `OfficePushWorker` |
| OFFICE unreachable | Entries remain queued as `failed`; retried on the next document close, closure, or scheduled retry |
| No POS activity for ≥ 1 hour | Background `OfficePushWorker` flushes all `pending`/`failed` documents and closures |
| OFFICE intermittently reachable | Items accumulate in local queues and are sent one by one on the next successful connection |

---

## Architecture

```
  Document closed / closure completed
        │
        ▼
 PaymentService.copy_temp_to_permanent() / ClosureEvent._closure_event()
        │
        ├── OfficePushService.enqueue() / enqueue_closure()
        │       ← adds row to office_push_queue / office_closure_push_queue
        │
        └── OfficePushWorker.wake()   ← non-blocking parallel flush
                    │
                    ├── OFFICE reachable?
                    │       Yes → POST /api/v1/pos/transactions or /pos/closures
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
| `enqueue_closure(closure_id, closure_unique_id)` | Adds a `pending` row to `office_closure_push_queue` |
| `flush_pending()` | Pushes all `pending`/`failed` documents and closures to OFFICE one by one |
| `has_pending()` | Returns `True` when unsent documents or closures exist |

### `pos/manager/office_push_worker.py` — `OfficePushWorker`

A `QThread` subclass that wakes every `retry_interval_seconds` (default **3600 s = 1 hour**) and
calls `OfficePushService.flush_pending()` when there are unsent items.

The retry interval is read from `[office].sync_interval_minutes` in `settings.toml`.

### `integration/office_client.py` — `OfficeClient` (extended)

OFFICE HTTP client methods used by the worker:

| Method | HTTP call |
|--------|-----------|
| `push_transactions(pos_id, transactions, sequences)` | `POST /api/v1/pos/transactions` |
| `push_closures(pos_id, closures, sequences)` | `POST /api/v1/pos/closures` |
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

### `data_layer/model/definition/office_closure_push_queue.py` — `OfficeClosurePushQueue`

Local SQLite table that tracks every completed closure awaiting delivery to OFFICE.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `fk_closure_id` | UUID | FK → `closure.id` |
| `closure_unique_id` | String | Human-readable closure ID |
| `status` | String | `pending` / `sent` / `failed` |
| `retry_count` | Integer | Number of failed attempts |
| `sent_at` | DateTime | Timestamp of successful delivery |
| `last_attempt_at` | DateTime | Timestamp of most recent attempt |
| `error_message` | String | Last error from OFFICE |

---

## Payload Format

Each queue item is sent in its own HTTP request.  Document requests use
`POST /api/v1/pos/transactions`:

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

Closure requests use `POST /api/v1/pos/closures`:

```json
{
  "office_code":   "OFFICE-001",
  "store_code":    "STORE-001",
  "terminal_code": "POS-01",
  "pos_id":        1,
  "closures": [
    {
      "closure":                 { "...": "Closure fields" },
      "vat_summaries":           [ { "...": "ClosureVATSummary fields" } ],
      "tip_summaries":           [ { "...": "ClosureTipSummary fields" } ],
      "discount_summaries":      [ { "...": "ClosureDiscountSummary fields" } ],
      "payment_type_summaries":  [ { "...": "ClosurePaymentTypeSummary fields" } ],
      "document_type_summaries": [ { "...": "ClosureDocumentTypeSummary fields" } ],
      "department_summaries":    [ { "...": "ClosureDepartmentSummary fields" } ],
      "currency_summaries":      [ { "...": "ClosureCurrency fields" } ],
      "cashier_summaries":       [ { "...": "ClosureCashierSummary fields" } ],
      "country_specific":        { "...": "ClosureCountrySpecific fields" } or null
    }
  ],
  "sequences": [
    { "name": "ReceiptNumber", "value": 1 },
    { "name": "ClosureNumber", "value": 4 }
  ]
}
```

OFFICE response:

```json
{ "status": "ok", "accepted": 1, "rejected": 0 }
```

---

## Sequence Number Synchronisation

Every document and closure push request includes the current values of **all**
`TransactionSequence` rows (e.g. `ReceiptNumber`, `ClosureNumber`) from the PyPOS local
database. OFFICE stores these values in its own `transaction_sequence` table indexed by
`(name, pos_id)` so that each terminal's counters are maintained independently.

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
2. **Document close** – `PaymentService.copy_temp_to_permanent()` enqueues the document
   and wakes the worker.
3. **Closure complete** – `ClosureEvent._closure_event()` enqueues the closure and wakes
   the same worker.
4. **Push success** – Queue item is marked `sent`.
5. **Push failure** – Queue item is marked `failed`.
6. **Hourly retry** – `OfficePushWorker` wakes, detects pending items, and flushes.
7. **Application exit** – The worker is stopped by the application shutdown path.
