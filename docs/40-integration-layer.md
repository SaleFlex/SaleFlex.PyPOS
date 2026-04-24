# Integration Layer

The integration layer connects SaleFlex.PyPOS to external systems: **SaleFlex.GATE** (the primary hub) and optional **third-party connectors** for ERP, payment gateways, and campaign modules.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        SaleFlex.PyPOS                            │
│                                                                  │
│  PaymentEvent ─────┐                                             │
│  ClosureEvent ─────┤                                             │
│  WarehouseEvent ───┼──→  pos/integration/hooks.py                │
│  SaleEvent ────────┤         │                                   │
│  GeneralEvent ─────┘         ▼                                   │
│                       IntegrationMixin                           │
│                      (routing logic)                             │
│              /               |               \                   │
│       OFFICE mode?      GATE mode?      Third-party?             │
│           │                  │                │                  │
│   OfficePushService  GateSyncService   BaseERPConnector          │
│   OfficeClient       GatePullService   BasePaymentGateway        │
│   OfficePushWorker       │             BaseCampaignConnector     │
│   (QThread, hourly)  SyncQueueItem            │                  │
│   OfficePushQueue    (offline outbox)  adapters/erp|payment      │
│   (local queue)                                                  │
└──────────────────────────────────────────────────────────────────┘
         │                    │                 ▲
         ▼                    ▼                 │
  SaleFlex.OFFICE      SaleFlex.GATE       Third-party
  (local hub, serves   (central hub)       ERP / Payment / Campaign
   from its own DB;
   receives pushes
   from PyPOS)
```

**Mode routing (controlled by `app.mode` in `settings.toml`):**

| `app.mode` | Remote target | Data source | Transaction push |
|------------|--------------|-------------|-----------------|
| `standalone` | None | Local SQLite only | None |
| `office` | SaleFlex.OFFICE REST API | OFFICE's local database | On every document close (parallel thread) + hourly retry |
| `gate` | SaleFlex.GATE REST API | GATE central database | Via SyncQueueItem outbox |

**Legacy routing rule for `gate` mode (evaluated in order):**

1. If `gate.manages_<service> = true` → routed through GATE.
2. If `third_party.<service>.enabled = true` → routed to the direct connector.
3. Otherwise → no-op; the POS continues without integration.

---

## SaleFlex.OFFICE Integration

### When to use `office` mode

Use `office` mode when you have a SaleFlex.OFFICE instance on your local network
and **do not** require a direct connection to SaleFlex.GATE from PyPOS terminals.
OFFICE acts as the store-level intermediary: it serves master-data to POS terminals
and receives their operational data.

### Configuration

```toml
# SaleFlex.PyPOS settings.toml
[app]
mode          = "office"
terminal_code = "POS-001"    # Unique within the store; registered in OFFICE
store_code    = "STORE-001"  # Identifies this store; must match OFFICE Store.store_code
office_code   = "OFFICE-001" # Identifies which OFFICE instance owns this terminal

[office]
base_url    = "http://192.168.1.x:9000"  # OFFICE [network] host:port
api_key     = ""                          # Reserved – leave empty (future use)
api_prefix  = "/api/v1"

# Which data domains does OFFICE manage for this terminal?
manages_transactions = true
manages_closures     = true
manages_warehouse    = true
manages_campaign     = true
manages_loyalty      = true
manages_users        = true

# Sync behaviour
sync_interval_minutes             = 5
retry_attempts                    = 3
timeout_seconds                   = 10
notification_poll_interval_seconds = 30
```

The matching OFFICE side configuration (set via **System Settings** module):

```toml
# SaleFlex.OFFICE settings.toml
[app]
store_code  = "STORE-001"   # Must match the store_code used by PyPOS terminals
office_code = "OFFICE-001"  # Unique identifier for this OFFICE instance

[network]
host = "0.0.0.0"   # or specific LAN IP
port = 9000
api_prefix = "/api/v1"
```

### Startup Bootstrap (database initialisation from OFFICE)

When a PyPOS terminal starts for the **first time** in `office` mode, its local
SQLite database does not yet exist.  Instead of inserting built-in default data,
PyPOS connects to OFFICE and pulls all reference data:

```
PyPOS startup (no db.sqlite3, mode == "office")
        │
        │  GET /api/v1/health
        ▼
SaleFlex.OFFICE (:9000) — liveness check
        │
        │  200 OK  ✓ OFFICE is reachable
        ▼
        │  GET /api/v1/pos/init
        │     ?office_code=OFFICE-001
        │     &store_code=STORE-001
        │     &terminal_code=POS-001
        ▼
OFFICE validates:
  1. Store with store_code="STORE-001" AND office_code="OFFICE-001" exists
  2. PosTerminal with terminal_code="POS-001" linked to that Store exists
  3. terminal.is_allowed_pull == True
        │
        │  200 OK  {"status":"ok","data":{...all init tables...}}
        ▼
PyPOS OfficeSeeder writes all records into the local SQLite database
(preserving OFFICE UUIDs for cross-system consistency)
        │
        ▼
Normal startup continues (UI forms, virtual keyboard, etc.)
```

If OFFICE is unreachable or rejects the credentials, PyPOS automatically falls
back to its built-in default seed data so the terminal can operate in
standalone mode.

### Runtime Data Flow (after initial bootstrap)

```
PyPOS (office mode) — transaction event
        │
        │  POST /api/v1/transactions, /api/v1/closures, …
        ▼
SaleFlex.OFFICE REST server (:9000)
        │  Stores locally → updates OFFICE local DB
        ▼
     (if OFFICE.mode = "gate") SyncWorker pushes to SaleFlex.GATE on schedule
```

Key principles:
- PyPOS **never waits for GATE** when in `office` mode.
- OFFICE always responds with its **locally stored** data immediately.
- The `(office_code, store_code, terminal_code)` triplet uniquely identifies a
  terminal across the entire SaleFlex ecosystem.  A single store can have
  multiple OFFICE instances, each serving a different subset of terminals.

### Settings properties (PyPOS `Settings` class)

| Property | Description |
|----------|-------------|
| `app_mode` | `"standalone"` \| `"office"` \| `"gate"` |
| `terminal_code` | This terminal's unique code (from `[app]`) |
| `store_code` | Store identifier (from `[app]`) |
| `office_code` | OFFICE instance identifier (from `[app]`) |
| `office_base_url` | OFFICE REST server URL |
| `office_api_prefix` | API path prefix (default `/api/v1`) |
| `office_api_key` | Authentication key (reserved, leave empty) |
| `office_timeout_seconds` | Per-request HTTP timeout |
| `office_sync_interval_seconds` | Converted from `sync_interval_minutes` |
| `office_notification_poll_interval_seconds` | Notification polling interval |
| `office_manages(service)` | `True` when OFFICE handles the given service domain |

---

## Folder Structure

```
pos/
└── integration/
    ├── __init__.py
    ├── external_device.py          # Base stub (mirrors OposDevice pattern)
    ├── hooks.py                    # Event-to-integration glue (mirrors peripherals/hooks.py)
    │
    ├── gate/                       # SaleFlex.GATE — primary hub
    │   ├── __init__.py
    │   ├── gate_client.py          # HTTP transport (requests wrapper)
    │   ├── gate_auth.py            # JWT / API token management
    │   ├── gate_sync_service.py    # Outbound push (transactions, closures, warehouse)
    │   ├── gate_pull_service.py    # Inbound pull (products, campaigns, notifications)
    │   └── serializers/
    │       ├── transaction_serializer.py
    │       ├── closure_serializer.py
    │       ├── product_serializer.py
    │       ├── warehouse_serializer.py
    │       ├── campaign_serializer.py
    │       └── notification_serializer.py
    │
    └── third_party/                # Direct third-party connectors
        ├── __init__.py
        ├── base_erp_connector.py
        ├── base_payment_gateway.py
        ├── base_campaign_connector.py
        └── adapters/
            ├── erp/
            │   └── custom_erp_connector.py
            ├── payment/
            │   └── custom_payment_gateway.py
            └── campaign/
                └── custom_campaign_connector.py

pos/manager/
├── integration_mixin.py            # Routing mixin added to Application
└── sync_worker.py                  # QThread background worker

data_layer/model/definition/
├── sync_queue_item.py              # Offline outbox table
└── gate_notification.py            # Inbound notification log table
```

---

## Configuration (`settings.toml`)

```toml
[gate]
enabled     = false
base_url    = ""        # e.g. https://your-gate.example.com
api_key     = ""
terminal_id = ""

# Which services does GATE manage?
manages_transactions = true
manages_closures     = true
manages_warehouse    = true
manages_campaign     = false   # false → third_party.campaign is used instead
manages_erp          = false   # false → third_party.erp is used instead
manages_payment      = false   # false → third_party.payment is used instead

sync_interval_minutes              = 30
retry_attempts                     = 3
timeout_seconds                    = 10
notification_enabled               = false
notification_poll_interval_seconds = 60

[third_party.erp]
enabled = false
type    = ""    # "sap" | "oracle" | "logo" | "netsis" | "custom"
base_url = ""
api_key  = ""

[third_party.payment]
enabled = false
type    = ""    # "iyzico" | "paytr" | "stripe" | "nets" | "custom"
base_url = ""
api_key  = ""

[third_party.campaign]
enabled  = false
type     = ""
base_url = ""
api_key  = ""
```

---

## SaleFlex.GATE Integration

### What GATE manages

| Feature | Description |
|---------|-------------|
| **Transactions** | Completed sale documents pushed to GATE after payment |
| **Closures** | End-of-day closure summaries pushed after closure |
| **Warehouse** | Stock movement events pushed in real time |
| **Products / Prices** | Pulled from GATE; triggers local cache refresh |
| **Campaigns** | Campaign definitions pulled; optional real-time discount calc (request body normalized via `pos.service.campaign` — see [Campaign & Promotions](43-campaign-promotions.md)) |
| **Notifications** | Terminal-to-terminal messages, system alerts, cache signals |
| **ERP (optional)** | When `manages_erp = true` GATE relays ERP sync payloads |
| **Payment (optional)** | When `manages_payment = true` GATE relays payment requests |

### Push flow (outbound)

```
Event occurs (sale completed, closure done, …)
       ↓
hooks.py function called from event handler
       ↓
GateSyncService.queue_*()
       ↓
SyncQueueItem row written with status="pending"
       ↓
SyncWorker (QThread) runs on schedule
       ↓
GateSyncService.flush_pending_queue()
       ↓
Serializer builds payload → GateClient.push()
       ↓
Success: status="sent"    Failure: retry_count++ → "failed" after max retries
```

### Pull flow (inbound)

```
SyncWorker periodic cycle (or startup)
       ↓
hooks.pull_updates_from_gate(app)
       ↓
GatePullService.pull_product_updates()    → ProductSerializer.apply_updates()
GatePullService.pull_campaign_updates()   → CampaignSerializer.apply_updates()
GatePullService.pull_notifications()      → NotificationSerializer.save_and_dispatch()
       ↓
SyncWorker emits signals:
  cache_refresh_needed("product" | "campaign" | "price")  → UI may rebuild caches (wire in Application)
  message_received(title, body)    → UI shows notification dialog
```

`hooks.pull_updates_from_gate` and `SyncWorker` call **`ActiveCampaignCache.reload_safely()`** after a successful pull so local **`CampaignService`** sees updated definitions. **`campaign_update`** notifications still emit **`cache_refresh_needed("campaign")`** for optional UI wiring; the in-memory campaign snapshot reloads in the worker during the same cycle.

### Authentication

`GateAuth` manages the API token lifecycle:
- Acquires a token from GATE's auth endpoint using the configured `api_key`.
- Caches the token in memory with its expiry timestamp.
- Automatically renews the token 60 seconds before expiry.
- All `GateClient` requests attach `Authorization: Bearer <token>`.

---

## Third-Party Connectors

### Adding a new ERP adapter

1. Copy `pos/integration/third_party/adapters/erp/custom_erp_connector.py`
   to e.g. `logo_erp_connector.py` in the same folder.
2. Rename the class to `LogoERPConnector` and implement the overridden methods.
3. Add a `case "logo":` branch in `IntegrationMixin._build_erp_connector()`.
4. Set `third_party.erp.type = "logo"` in `settings.toml`.

The same pattern applies to payment gateways (`base_payment_gateway.py`,
`_build_payment_gateway()`) and campaign connectors (`base_campaign_connector.py`,
`_build_campaign_connector()`).

### Abstract interfaces

| Class | Location | Override methods |
|-------|----------|-----------------|
| `BaseERPConnector` | `third_party/base_erp_connector.py` | `sync_transaction`, `sync_closure`, `pull_product_catalog`, `pull_customer_data`, `sync_inventory` |
| `BasePaymentGateway` | `third_party/base_payment_gateway.py` | `initiate_payment`, `confirm_payment`, `void_payment`, `refund_payment` |
| `BaseCampaignConnector` | `third_party/base_campaign_connector.py` | `get_applicable_discounts`, `redeem_coupon`, `sync_campaigns`, `record_usage` |

### Campaign discount routing

`Application` (`pos/manager/application.py`) inherits **`IntegrationMixin`** and calls **`init_integration()`** after **`load_open_closure()`** during startup.

**`IntegrationMixin.apply_campaign(cart_data)`** chooses the campaign source in order:

1. **GATE** — if **`gate.enabled`** and **`gate.manages_campaign`** → **`GatePullService.get_campaign_discounts`** (HTTP body still a stub; shape aligns with **`CampaignSerializer`** / **`normalize_cart_data_for_campaign_request`**).
2. **Third-party** — else if **`third_party.campaign.enabled`** and the built connector **`is_enabled()`** → **`get_applicable_discounts`**.
3. **Local preview** — else, if **`cart_data`** includes both **`head`** and **`products`** (typical embedded **`document_data`**), runs **`CampaignService.evaluate_proposals(cart_data)`** and returns a new dict: all keys from **`cart_data`** plus **`campaign_proposals`**: a list of **`CampaignService.campaign_discount_proposal_to_dict(...)`** entries. This does **not** write **`TransactionDiscountTemp`** rows; it is for integration-style callers and tooling.

**`pos/integration/hooks.apply_campaign_discounts(app, cart_data)`** calls **`app.apply_campaign(cart_data)`** when that method exists on the **`Application`** instance (or a future **`_integration_mixin`** delegate).

**SALE screen totals:** Automatic **`CAMPAIGN`** lines on the open document are driven by **`sync_campaign_discounts_on_document`** in **`pos/service/campaign/campaign_document_sync.py`**, not by **`apply_campaign`**. See [Campaign & Promotions — Sale document sync](43-campaign-promotions.md#sale-document-sync-local-engine).

**After a completed sale:** **`PaymentService.copy_temp_to_permanent`** calls **`CampaignAuditService.record_after_completed_sale`** (**`CampaignUsage`**, **`CouponUsage`**, counters). To roll back entitlements when a completed receipt is voided or refunded under your policy, use **`CampaignAuditService.revoke_entitlements_for_transaction_head`** (see [Campaign & Promotions — Usage audit and reversal](43-campaign-promotions.md#usage-audit-and-reversal-void--refund)).

---

## Background Worker (`SyncWorker`)

`SyncWorker` is a `PySide6.QThread` that runs continuously without blocking the UI.

```python
# Signals emitted by SyncWorker
sync_completed       = Signal(str, bool)    # (connector_type, success)
sync_failed          = Signal(str, str)     # (connector_type, error_msg)
cache_refresh_needed = Signal(str)          # cache name: "product" | "campaign"
message_received     = Signal(str, str)     # (title, body)
```

**Lifecycle** (wired in `application.py`):
```python
# Start on application init (after settings are loaded)
self._sync_worker = SyncWorker(
    interval_seconds=Settings().gate_sync_interval_seconds
)
self._sync_worker.cache_refresh_needed.connect(self._reload_cache)
self._sync_worker.message_received.connect(self._show_terminal_message)
self._sync_worker.start()

# Stop on application exit
self._sync_worker.stop()
self._sync_worker.wait()
```

---

## Offline Outbox (`SyncQueueItem`)

Every event is written to the local SQLite database before any network call is attempted. This ensures **zero data loss** during connectivity gaps.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `connector_type` | str | `"gate"` \| `"gate_erp"` \| `"erp"` \| `"payment"` |
| `event_type` | str | `"transaction"` \| `"closure"` \| `"warehouse_movement"` \| … |
| `payload` | JSON | Serialised data to transmit |
| `status` | str | `"pending"` → `"sent"` or `"failed"` |
| `retry_count` | int | Current retry count |
| `max_retries` | int | Maximum retries before marking as `"failed"` |
| `error_message` | str | Last failure description |
| `created_at` | datetime | Row creation time |
| `sent_at` | datetime | Successful transmission time |

---

## Notification Log (`GateNotification`)

Inbound notifications from GATE are persisted in `gate_notification` table.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `notification_type` | str | `"product_update"` \| `"terminal_message"` \| … |
| `title` | str | Notification title |
| `body` | str | Notification body text |
| `source_terminal_id` | str | Originating terminal (nullable) |
| `gate_notification_id` | str | GATE-side ID for deduplication |
| `is_read` | bool | Whether acknowledged by the operator |
| `received_at` | datetime | Local receipt timestamp |

---

## Exception Hierarchy

```
SaleFlexError
├── GATEConnectionError          # GATE unreachable
│   ├── GATEAuthError            # Token missing / invalid / expired
│   ├── GATESyncError            # Push / pull failed after retries
│   └── GATENotificationError    # Notification polling failed
└── ThirdPartyIntegrationError   # Base for all direct connectors
    ├── ERPConnectionError        # ERP unreachable
    │   └── ERPSyncError          # ERP data exchange failed
    ├── ThirdPartyPaymentError    # Payment gateway error
    └── ThirdPartyCampaignError   # Campaign module error
```

All integration exceptions are subclasses of `SaleFlexError` and are chained
with `raise ... from e` to preserve the full traceback.  See
[Exception Handling](32-exception-handling.md) for the complete hierarchy.

---

## Design Notes

### Why `pos/integration/` and not root-level `integration/`?

The integration layer is a POS concern — it is the terminal that syncs, not a
generic system.  Placing it under `pos/` keeps it consistent with
`pos/peripherals/` and `pos/service/`.

### Why the `hooks.py` glue file?

`pos/peripherals/hooks.py` already establishes this pattern: event handlers import
thin glue functions instead of integration internals.  This keeps event handler
code free from knowledge of which connector is active or how retries work.

### Why module-level factories instead of a Singleton manager?

The project uses module-level `get_default_*()` factories (same as
`get_default_pos_printer()`).  A separate `IntegrationManager` Singleton would
introduce a new pattern that conflicts with the existing codebase.  Instead,
`IntegrationMixin` is added to the `Application` inheritance chain, and all
routing logic lives there.

### Current implementation status

**GATE and third-party connectors** remain largely **log-only stubs** for network I/O; serializers and queue shapes are in place with `TODO:` markers where HTTP or vendor APIs will attach.

**Local campaign behaviour** is implemented in **`pos/service/campaign/`**: evaluation (**`CampaignService.evaluate_proposals`** — basket, time-window, product, buy-X-get-Y, payment-method types, rules, stacking), **SALE** and **PAYMENT** document sync (**`sync_campaign_discounts_on_document`** via cart changes and **`PaymentService.process_payment`**), and the **`apply_campaign`** fallback that adds **`campaign_proposals`** to **`document_data`-shaped** dicts when GATE and the campaign connector are not active.

---

**Last Updated:** 2026-04-11
**Version:** 1.0.0b6
**Related:** [Project Structure](20-project-structure.md) · [Exception Handling](32-exception-handling.md) · [Peripherals](30-peripherals.md) · [Event System](24-event-system.md)
