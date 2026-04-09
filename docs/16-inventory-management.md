# 16. Inventory Management

## Overview

The Inventory Management module provides real-time stock tracking, goods receipt, manual adjustments, stock transfers, and movement-history auditing for SaleFlex.PyPOS.

Stock is always tracked at the **warehouse location** level.  
The **primary deduction location** is `SALES_FLOOR` (`SALES-001-A`). The `product.stock` column mirrors the `WarehouseProductStock.quantity` for that location and is kept in sync automatically after every mutation.

![Warehouse list — product grid, location breakdown, actions](../static_files/images/sample_warehouse_list_form.jpg)

**Stock in** (goods receipt):

![Warehouse stock in](../static_files/images/sample_warehouse_stock_in_form.jpg)

**Manual adjustment:**

![Warehouse adjustment](../static_files/images/sample_warehouse_adjustment_form.jpg)

**Movement history:**

![Warehouse history](../static_files/images/sample_warehouse_history_form.jpg)

---

## Architecture

```
┌─────────────────────────────────────┐
│  UI Layer (PySide6 dynamic forms)   │
│  STOCK_INQUIRY / STOCK_IN /         │
│  STOCK_ADJUSTMENT / STOCK_MOVEMENT  │
└──────────────┬──────────────────────┘
               │ EventName.*
               ▼
┌─────────────────────────────────────┐
│  EventHandler (event_handler.py)    │
│  dispatches to WarehouseEvent       │
└──────────────┬──────────────────────┘
               │ method calls
               ▼
┌─────────────────────────────────────┐
│  WarehouseEvent (event/warehouse.py)│
│  navigation, search, confirm logic  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  InventoryService                   │
│  (pos/service/inventory_service.py) │
│  Pure business logic, @staticmethod │
└──────────────┬──────────────────────┘
               │ SQLAlchemy ORM
               ▼
┌─────────────────────────────────────┐
│  Data Layer models                  │
│  WarehouseProductStock              │
│  WarehouseStockMovement             │
│  WarehouseStockAdjustment           │
│  Product.stock  (mirror)            │
└─────────────────────────────────────┘
```

---

## Key Models

| Model | Purpose |
|---|---|
| `Warehouse` | Physical or logical store area |
| `WarehouseLocation` | Specific spot within a warehouse (rack, shelf, gondola, …) |
| `WarehouseProductStock` | Stock level of a product at a location |
| `WarehouseStockMovement` | Immutable audit record of every stock change |
| `WarehouseStockAdjustment` | Manual adjustment record with reason |

---

## InventoryService API

File: `pos/service/inventory_service.py`

All methods are `@staticmethod` — no instantiation required.

### Stock Validation

```python
allowed, reason = InventoryService.can_sell(product, quantity)
```

- Returns `(True, "")` when the sale is permitted.
- Returns `(False, reason)` when `product.is_allowed_negative_stock` is `False` and available stock is insufficient.

### Automatic Stock Deduction (Sale Completion)

Called automatically in `DocumentManager.complete_document()` when a **SALE** transaction is finalised:

```python
InventoryService.deduct_stock_on_sale(
    transaction_head_id=head.id,
    products=prod_lines,      # list of TempTransactionProduct ORM instances
    cashier_id=cashier_id,
)
```

- Deducts from the `SALES_FLOOR` location.
- Creates a `WarehouseStockMovement` record for each line.
- Syncs `product.stock` to the new `WarehouseProductStock.quantity`.

### Stock Restoration (Cancellation)

```python
InventoryService.restore_stock_on_cancel(
    transaction_head_id=original_head_id,
    products=prod_lines,
    cashier_id=cashier_id,
)
```

Used when a previously paid sale is reversed (refund/void).  
Cancellations that happen **before** payment do not trigger restoration because stock was never deducted.

### Goods Receipt (Stock-In)

```python
success = InventoryService.receive_stock(
    product_id=product_id,
    quantity=qty,
    location_id=location_id,   # defaults to SALES_FLOOR
    notes="PO #1234",
    cashier_id=cashier_id,
)
```

### Manual Adjustment

```python
success = InventoryService.adjust_stock(
    product_id=product_id,
    new_quantity=qty,
    reason="Stocktake correction",
    cashier_id=cashier_id,
)
```

Sets the absolute stock level.  Creates a `WarehouseStockAdjustment` record.

### Stock Inquiry

```python
summary = InventoryService.get_stock_summary(product_id)
# Returns list of {location, warehouse, quantity, available, reserved, …}

history = InventoryService.get_movement_history(product_id=id, limit=50)
# Returns list of WarehouseStockMovement records
```

### Low Stock Alerts

```python
alerts = InventoryService.get_low_stock_products()
# Returns list of (product, wps) tuples where quantity <= reorder_point
```

Alerts are evaluated during each sale in `WarehouseEvent` and logged at `WARNING` level. A dialog is shown when the cashier is on the sales screen.

---

## Stock Deduction Flow (Sale)

```
Cashier scans / enters product
    │
    ▼
SaleEvent._check_stock_for_sale()
    ├─ InventoryService.can_sell(product, qty)
    │       └─ if not allowed → show error dialog → block add
    └─ allowed → product added to sale list
                              │
                              ▼
                  Payment confirmed
                              │
                              ▼
            DocumentManager.complete_document()
                    ├─ Create permanent TransactionHead
                    ├─ Create permanent TransactionProducts
                    └─ InventoryService.deduct_stock_on_sale()
                              ├─ Find SALES_FLOOR location
                              ├─ Reduce WarehouseProductStock.quantity
                              ├─ Update product.stock (mirror)
                              └─ Insert WarehouseStockMovement (SALE)
```

---

## Negative Stock Policy

Controlled by `Product.is_allowed_negative_stock` (boolean, default `False`).

| `is_allowed_negative_stock` | Available Stock | Result |
|---|---|---|
| `True` | any | Sale always allowed |
| `False` | ≥ requested qty | Sale allowed |
| `False` | < requested qty | Sale **blocked**, error dialog shown |

---

## UI Forms

New inventory forms were added to the dynamic forms system.

| Form | `FormName` enum | `form_no` | Access |
|---|---|---|---|
| Stock Inquiry | `STOCK_INQUIRY` | 13 | Product List → STOCK button |
| Goods Receipt (Stock-In) | `STOCK_IN` | 14 | Stock Inquiry form → STOCK IN |
| Manual Adjustment | `STOCK_ADJUSTMENT` | 15 | Stock Inquiry form → ADJUST |
| Movement History | `STOCK_MOVEMENT` | 16 | Stock Inquiry form → HISTORY |

The **STOCK** button was added to the existing `PRODUCT_LIST` form (form_no=8) as `STOCK_INQUIRY_BTN`, positioned at (175, 660) with a dark-blue background (`0x1A5276`).

### New UI Controls (ControlName)

| Constant | Control Type | Purpose |
|---|---|---|
| `STOCK_SEARCH_TEXTBOX` | TEXTBOX | Product search input |
| `STOCK_INQUIRY_DATAGRID` | DATAGRID | Products with stock summary |
| `STOCK_DETAIL_DATAGRID` | DATAGRID | Per-location breakdown |
| `STOCK_IN_PRODUCT_DATAGRID` | DATAGRID | Products for goods receipt |
| `STOCK_ADJUSTMENT_DATAGRID` | DATAGRID | Products for adjustment |
| `STOCK_MOVEMENT_DATAGRID` | DATAGRID | Movement history |
| `STOCK_QUANTITY_TEXTBOX` | TEXTBOX | Quantity entry |
| `STOCK_REASON_TEXTBOX` | TEXTBOX | Reason / notes entry |

---

## New Events

Registered in `EventName` enum and wired in `EventHandler.event_handler_map`:

| EventName | Handler Method | Triggered By |
|---|---|---|
| `STOCK_INQUIRY` | `_stock_inquiry_event` | STOCK_INQUIRY_BTN click |
| `STOCK_SEARCH` | `_stock_search_event` | INV_SEARCH_BTN on inquiry form |
| `STOCK_DETAIL` | `_stock_detail_event` | DETAIL button on inquiry form |
| `STOCK_IN_SEARCH` | `_stock_in_search_event` | SEARCH on stock-in form |
| `STOCK_IN_CONFIRM` | `_stock_in_confirm_event` | RECEIVE button |
| `STOCK_ADJUSTMENT_SEARCH` | `_stock_adjustment_search_event` | SEARCH on adjustment form |
| `STOCK_ADJUSTMENT_CONFIRM` | `_stock_adjustment_confirm_event` | ADJUST button |
| `STOCK_MOVEMENT_SEARCH` | `_stock_movement_search_event` | SEARCH on movement form |

---

## Seed Data

### Warehouse Locations (`data_layer/db_init_data/warehouse_location.py`)

One or more `WarehouseLocation` records are created per warehouse type:

| Warehouse Type | Location Code | Description |
|---|---|---|
| `MAIN` | `MAIN-001-A` | General storage racks |
| `BACKROOM` | `BACK-001-A` | Backroom stock area |
| `SALES_FLOOR` | `SALES-001-A` | **Primary POS deduction location** |
| `SALES_FLOOR` | `SALES-001-B` | Electronics display |
| `SALES_FLOOR` | `SALES-001-C` | Checkout counter |
| `COLD_STORAGE` | `COLD-001-A` | 2–8°C chilled area |
| `SECURITY` | `SEC-001-A` | Locked security cage |
| `TEMPORARY` | `TEMP-001-A` | Returns staging area |

### Initial Stock (`data_layer/db_init_data/warehouse_product_stock.py`)

`WarehouseProductStock` records are inserted for every demo product with:

- `quantity` = 50 (default) or product-specific value
- `min_stock_level` = 5, `reorder_point` = 10
- `fk_warehouse_location_id` → `SALES-001-A`
- `product.stock` column synchronised to the assigned quantity

Insertion order in `__init__.py`:

1. `_insert_warehouses()`
2. `_insert_warehouse_locations()`  ← new
3. *(other seed data …)*
4. `_insert_products()`
5. `_insert_product_barcodes()`
6. `_insert_warehouse_product_stock()`  ← new

---

## Movement Number Format

Generated by `InventoryService.generate_movement_number()`:

```
MVT-{YYYYMMDD}-{HHMMSS}-{uuid4[:8].upper()}
```

Example: `MVT-20260407-143022-A1B2C3D4`

---

## Movement Types

Defined in `WarehouseStockMovement.movement_type` (string):

| Value | Description |
|---|---|
| `SALE` | Deducted during sale completion |
| `CANCEL` | Restored during sale cancellation/void |
| `RECEIVE` | Goods receipt / stock-in |
| `ADJUST` | Manual stocktake correction |
| `TRANSFER_IN` | Received from another location |
| `TRANSFER_OUT` | Sent to another location |

---

## Configuration

No additional configuration is required.  
The feature activates automatically when warehouse locations and product stock records are present in the database.

To reset stock data during development, truncate the following tables in order:

```sql
DELETE FROM warehouse_stock_movement;
DELETE FROM warehouse_stock_adjustment;
DELETE FROM warehouse_product_stock;
DELETE FROM warehouse_location;
```

Then re-run `insert_initial_data()` to re-seed.
