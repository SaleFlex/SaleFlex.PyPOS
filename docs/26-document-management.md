# Document Management System

## Overview

SaleFlex.PyPOS implements a **transaction document management system** that handles the complete lifecycle of sales transactions from creation to completion. The system uses temporary models (`*_temp`) during transaction processing and copies them to permanent models upon completion.

## Document Structure

The `CurrentData` class (via `DocumentManager` mixin) manages two key document-related attributes:

1. **`document_data`**: Dictionary containing the current active transaction being processed
2. **`pending_documents_data`**: List of dictionaries containing suspended/pending transactions (used in restaurant mode for managing tables/orders)

## Document Data Structure

The `document_data` dictionary contains all transaction temp models:

```python
self.document_data = {
    "head": TransactionHeadTemp instance,  # Main transaction header
    "products": List[TransactionProductTemp],
    "payments": List[TransactionPaymentTemp],
    "discounts": List[TransactionDiscountTemp],
    "departments": List[TransactionDepartmentTemp],
    "deliveries": List[TransactionDeliveryTemp],
    "kitchen_orders": List[TransactionKitchenOrderTemp],
    "loyalty": List[TransactionLoyaltyTemp],
    "notes": List[TransactionNoteTemp],
    "fiscal": TransactionFiscalTemp or None,
    "refunds": List[TransactionRefundTemp],
    "surcharges": List[TransactionSurchargeTemp],
    "taxes": List[TransactionTaxTemp],
    "tips": List[TransactionTipTemp],
    "changes": List[TransactionChangeTemp]  # Change records for overpayments
}
```

## Document Lifecycle

### 1. Document Creation

When starting a new transaction, an empty document is created with default values:

```python
# Create new empty document
document = self.create_empty_document()
```

**Default Values:**
- `document_type`: From `CurrentStatus.document_type` property (converted from `DocumentType` enum to string)
- `transaction_type`: Mapped from `CurrentStatus.document_type` property (e.g., `DocumentType.RETURN_SLIP` → `TransactionType.RETURN`, default: `TransactionType.SALE`)
- `transaction_status`: `TransactionStatus.DRAFT`
- `closure_number`: Value from `TransactionSequence` where `name="ClosureNumber"` (from `pos_data` cache, verified against the active open `Closure` object)
- `receipt_number`: Starting value from `TransactionSequence` where `name="ReceiptNumber"` (from `pos_data` cache); automatically advanced through the conflict-check loop if earlier receipts within the same closure period already occupy the slot
- `transaction_unique_id`: Computed as `"{YYYYMMDD}-{closure_number:04d}-{receipt_number:06d}"` (e.g. `"20250406-0002-000001"` for 6 April 2025, closure 2, receipt 1). Embedding `closure_number` between the date and receipt number ensures that resetting `ReceiptNumber` to 1 after end-of-day closure **never conflicts** with receipts from the previous period on the same calendar day.
- `fk_store_id`: First `Store` record from `pos_data`
- `pos_id`: `pos_no_in_store` from `PosSettings`
- `is_closed`: `False`
- `is_pending`: `False`
- `is_cancel`: `False`

**Receipt Number Reset on Closure:**
When end-of-day closure is performed (`ClosureEvent._closure_event`):
1. `TransactionSequence.ClosureNumber` is incremented by 1.
2. `TransactionSequence.ReceiptNumber` is reset to 1.
3. The `pos_data` cache is refreshed.
4. A new open `Closure` record is created with the new closure number.
5. `abandon_empty_open_document_if_any()` is called to soft-delete the pre-created empty draft that `_check_and_complete_document` left in `TransactionHeadTemp` (and therefore in `self.document_data`) after the last completed sale.
6. `self.document_data` is set to `None`.

**Why step 5–6 are necessary:** after every completed payment, `_increment_receipt_number()` advances `ReceiptNumber` in the DB and cache (e.g. to 6), then `create_empty_document()` immediately creates a new empty draft with `receipt_number = 6`. Without clearing this draft, the guard at the top of `create_empty_document()` would return it on the next SALE navigation, keeping `receipt_number = 6` instead of resetting to 1. Steps 5–6 ensure the stale draft is discarded so the next `create_empty_document()` call builds a fresh document with `receipt_number = 1`.

Because `transaction_unique_id` also embeds `closure_number` (e.g. `"20250406-0002-000001"`), the fresh document never conflicts with any prior receipt from the same day, even if the DB still holds closed temp records from the previous closure period. Within each closure period, receipts count from 1 upward: 1, 2, 3 …

**Automatic Document Creation:**
Documents are automatically created in the following scenarios:
- **After Login**: When a cashier successfully logs in, the system attempts to load an incomplete document. If none exists, a new empty document is created.
- **When Opening Sale Form**: When navigating to the sale form, if no document exists, the system loads incomplete document or creates a new one.
- **When Adding First Product**: If a product is added and no document exists, a new document is automatically created.

This ensures that document information (document_type, transaction_type, receipt_number) is always available for display in the status bar and for transaction processing.

**Automatic UI Restoration:**
When entering the sale screen, if `document_data` contains an ACTIVE transaction (`transaction_status = ACTIVE`), the system automatically restores the transaction state by updating UI controls:
- **sale_list**: Products and departments are loaded from `TransactionProductTemp` and `TransactionDepartmentTemp`, ordered by `line_no`
- **amount_table**: Totals are restored from `TransactionHeadTemp` (total_amount, total_discount_amount, total_payment_amount)
- **payment_list**: Payments are loaded from `TransactionPaymentTemp`, ordered by `line_no`

This allows users to resume incomplete transactions seamlessly when navigating back to the sale screen or after application restart.

**Automatic Document Data Updates:**
During sales operations, the `document_data` is automatically updated:
- **PLU Sales** (SALE_PLU_CODE, SALE_PLU_BARCODE): Automatically creates `TransactionProductTemp` records with product details, VAT calculations, and pricing
- **Department Sales** (SALE_DEPARTMENT): Automatically creates `TransactionDepartmentTemp` records with department information, VAT rates, and totals
- **Sale List Item REPEAT**: Clones the selected `TransactionProductTemp` / `TransactionDepartmentTemp` record with a new UUID and the next `line_no`, saves it to the database, and recalculates the document totals
- **Sale List Item DELETE**: Marks the matching `TransactionProductTemp` / `TransactionDepartmentTemp` record as `is_cancel = True`, saves it to the database, and recalculates the document totals. If no active lines remain, the document is automatically cancelled (see [Empty Document Handling](#empty-document-handling))
- **Payment Processing**: Automatically creates `TransactionPaymentTemp` records when payment buttons are clicked, updates `total_payment_amount`, and calculates change
- **Change Recording**: Change is recorded manually when `CHANGE_PAYMENT` button is clicked, or via MessageForm dialog if button doesn't exist in form
- **Transaction Head Updates**: Automatically updates `TransactionHeadTemp` fields including:
  - `transaction_date_time`: Set to current time if empty
  - `transaction_status`: Changed from `DRAFT` to `ACTIVE` when first item is added, `COMPLETED` when fully paid, `CANCELLED` when all items are deleted
  - `closure_number`: Set from active closure
  - `base_currency`: Set from `CurrentStatus.current_currency`
  - `order_source`: Set to "in_store"
  - `order_channel`: Set to "cashier"
  - `total_amount` and `total_vat_amount`: Automatically calculated from active (non-cancelled) products and departments
  - `total_payment_amount`: Updated with each payment
  - `total_change_amount`: Updated when change is recorded
  - `is_closed`: Set to `True` when document is completed or all items are deleted
- **Customer Assignment**: Automatically assigns a default walk-in customer if not set
- **Batch Number**: Automatically set to match `closure_number`

All temp models are automatically saved to the database when created during sales operations. This automatic persistence is handled by the auto-save system using descriptor pattern and wrapper classes (AutoSaveModel, AutoSaveDict, AutoSaveDescriptor) located in `data_layer/auto_save/`, ensuring data integrity without manual save operations.

### 2. Document Loading

**Incomplete Documents:**
The system automatically attempts to load incomplete documents in the following scenarios:
- After successful login
- When opening the sale form
- At application startup (if implemented)

```python
# Automatically called after login and when opening sale form
self.load_incomplete_document()
```

An incomplete document is one where:
- `is_closed = False`
- `is_pending = False`
- `is_cancel = False`

If no incomplete document is found, a new empty document is automatically created.

**Pending Documents:**
All pending documents (suspended transactions) are loaded at startup:

```python
# Automatically called at startup
self.load_pending_documents()
```

Pending documents are used in restaurant mode for managing tables/orders that are temporarily suspended.

### 3. Document Suspension (Restaurant and market retail)

Documents can be suspended (put on hold) to allow completing the sale later—for example tables/orders in restaurants, or parked carts in market retail.

```python
# Suspend current document
self.set_document_pending(is_pending=True)

# Resume suspended document
self.set_document_pending(is_pending=False)
```

When suspended:
- `is_pending` is set to `True`
- `transaction_status` is set to `TransactionStatus.PENDING`
- Document is saved to database and added to `pending_documents_data` list

**Market retail — SALE form `SUSPEND` button (`EventName.SUSPEND_SALE`):**

- If there is an open document with at least one sale line (`TransactionProductTemp` and/or `TransactionDepartmentTemp`), the handler calls `set_document_pending(True)`, clears `document_data`, then **`create_empty_document()`** so the next sale uses a new draft and receipt slot (suspended temp heads are skipped in `create_empty_document`’s open-document reuse logic when `is_pending=True`). The **SALE** form is redrawn and sale controls refreshed.
- If the open document has **no lines** (typical **DRAFT** before the first item), **SUSPEND** opens **`SUSPENDED_SALES_MARKET`** so the operator can review or **ACTIVATE** parked carts without suspending an empty ticket.
- If there is no open document, the app navigates to form **`SUSPENDED_SALES_MARKET`** (`FormName.SUSPENDED_SALES_MARKET`), which shows a DataGrid (`ControlName.SUSPENDED_SALES_DATAGRID`) with a hidden **Id** column plus **Receipt No**, **Line count**, and **Total**. The **ACTIVATE** button (`EventName.RESUME_SALE`) loads the selected row’s head via `DocumentManager.resume_suspended_market_document`, sets `is_pending=False` and `transaction_status=active`, redraws **SALE** with `skip_history_update=True`, and calls `CurrentStatus.prepare_navigation_resume_sale_from_suspended_market()` so **BACK** on the sale screen does not return to the suspended list (same history as pressing **BACK** on the list, then continuing on **SALE**).
- Startup recovery via `load_incomplete_document()` still only loads documents with `is_pending = False`; suspended carts are not auto-restored as the “current” sale.

### 4. Document Completion

When a transaction is completed, all temp models are copied to permanent models:

```python
# Complete document (normal completion)
self.complete_document()

# Complete document (cancelled)
self.complete_document(is_cancel=True, cancel_reason="Customer cancelled")
```

**Completion Process:**
1. Updates `TransactionHeadTemp`:
   - Sets `transaction_status` to `COMPLETED` (or `CANCELLED` if cancelled)
   - Sets `is_closed = True`
   - Sets `is_cancel = True` if cancelled
2. Copies all temp models to permanent models:
   - `TransactionHeadTemp` → `TransactionHead`
   - `TransactionProductTemp` → `TransactionProduct`
   - `TransactionDepartmentTemp` → `TransactionDepartment`
   - `TransactionPaymentTemp` → `TransactionPayment`
   - `TransactionChangeTemp` → `TransactionChange`
   - And all other related temp models
3. Updates foreign keys correctly (maps temp IDs to permanent IDs)
4. Updates closure totals:
   - `total_document_count`: Incremented
   - `gross_sales_amount`: Added transaction total
   - `net_sales_amount`: Added (total - VAT)
   - `total_tax_amount`: Added VAT amount
   - `total_discount_amount`: Added discount amount
   - `total_tip_amount`: Added tip amount
   - `valid_transaction_count`: Incremented
   - `closing_cash_amount`: Added cash payments total
   - `paid_in_count`: Added payment count
   - `paid_in_total`: Added total payment amount
5. Increments receipt number sequence (`TransactionSequence` where `name="ReceiptNumber"`)
6. Saves everything to database
7. Clears UI controls (PaymentList, AmountTable, SaleList)
8. Resets `document_data` to `None`

On the **SALE** form, the event layer also triggers **peripheral hooks** after a successful paid completion (log-only today): a full receipt snapshot is sent to the default `POSPrinter`, then the default `CashDrawer` open command runs. See [Peripherals](30-peripherals.md).

**Automatic Document Completion:**
Documents are automatically completed when fully paid. The completion check happens after each payment (and after any **LOYALTY** discount from **BONUS** redemption, which reduces the amount due):
- **Condition** (net): `(total_amount - total_discount_amount) = total_payment_amount - total_change_amount`
- If condition is met, document is automatically marked as COMPLETED and closed
- Change is calculated if payment exceeds total, but recording requires manual action:
  - If `CHANGE_PAYMENT` button exists: User clicks button to record change
  - If `CHANGE_PAYMENT` button doesn't exist: MessageForm dialog shows change amount, OK records change
- UI controls are automatically cleared after completion
- New empty document is ready for next transaction

## Usage Examples

### Example 1: Starting a New Sale

```python
# Create new empty document
document = self.create_empty_document()

# Add products
product = TransactionProductTemp()
product.fk_transaction_head_id = document["head"].id
product.fk_product_id = product_id
product.quantity = 2
product.unit_price = 10.00
# ... set other fields
document["products"].append(product)

# Process payment using PaymentService
from pos.service import PaymentService

success, payment_temp, error = PaymentService.process_payment(
    document_data=document_data,
    payment_type="CASH_PAYMENT",
    button_name="CASH2000"  # Pays 20.00 (2000 / 100)
)

# If payment exceeds total, change is calculated
change_amount = PaymentService.calculate_change(document_data)
if change_amount > 0:
    # Change recording requires manual action:
    # - Click CHANGE_PAYMENT button if it exists in form
    # - Or MessageForm dialog will appear automatically if button doesn't exist
    PaymentService.record_change(document_data)

# Check if document is complete (automatically checked after payment)
if PaymentService.is_document_complete(document_data):
    # Mark as complete
    PaymentService.mark_document_complete(document_data)
    
    # Update closure
    PaymentService.update_closure_for_completion(closure, document_data)
    
    # Copy to permanent models (loyalty earn staging, discounts incl. LOYALTY, TransactionLoyalty copy, REDEEMED/EARNED + tier)
    PaymentService.copy_temp_to_permanent(document_data)
    
    # Clear UI controls (automatically done)
    # Reset document_data (automatically done)
```

### Example 2: Restaurant Table Order (Suspend/Resume)

```python
# Start order for table
document = self.create_empty_document()
document["head"].fk_table_id = table_id

# Add initial items
# ... add products

# Suspend order (customer wants to add more later)
self.set_document_pending(is_pending=True)

# Later, resume order
# Load from pending_documents_data or database
pending_doc = self.pending_documents_data[0]
self.document_data = pending_doc

# Resume
self.set_document_pending(is_pending=False)

# Add more items
# ... add more products

# Complete order
self.complete_document()
```

### Example 3: Automatic Document Creation After Login

```python
# In _login() method after successful authentication
# Document is automatically created if none exists

# Login successful - set cashier_data
self.cashier_data = cashiers[0]
self.login_succeed = True

# Try to load incomplete document first
if not self.document_data:
    if not self.load_incomplete_document():
        # If no incomplete document, create new empty document
        self.create_empty_document()

# Navigate to appropriate form
self._navigate_after_login()
```

### Example 4: Document Creation When Opening Sale Form

```python
# In _sales_form() method
# Document is automatically created if none exists
# UI controls are automatically restored if transaction is ACTIVE

if self.login_succeed:
    # Ensure document_data exists
    if not self.document_data:
        if not self.load_incomplete_document():
            self.create_empty_document()
    
    self.current_form_type = FormName.SALE
    self.interface.redraw(form_name=FormName.SALE.name)
    
    # UI controls are automatically restored if transaction_status is ACTIVE
    # This happens via SaleService.update_sale_screen_controls()
```

### Example 5: Automatic UI Restoration on Sale Screen Entry

```python
# When entering sale screen with ACTIVE transaction
# The system automatically restores UI state

# After form is redrawn, SaleService updates controls:
from pos.service import SaleService

# This is called automatically in _sales_form()
SaleService.update_sale_screen_controls(
    window=window,
    document_data=self.document_data,
    pos_data=self.pos_data
)

# Results:
# - sale_list shows all products and departments in line_no order
# - amount_table displays current totals
# - payment_list shows all payments in line_no order
```

## Line Item Cancellation (Sale List DELETE)

Individual transaction lines can be soft-cancelled during an active sale session via the **Item Actions** popup (DELETE button). This is distinct from cancelling an entire document.

### How it works

1. The cashier taps a row in the sale list → the **Item Actions** popup opens.
2. Pressing **DELETE** marks that row's `TransactionProductTemp` (or `TransactionDepartmentTemp`) record as `is_cancel = True` and saves it to the database.
3. The row remains visible in the current session with a strikethrough style.
4. `SaleService.calculate_document_totals()` recalculates the document total, **skipping all cancelled lines**.
5. `TransactionHeadTemp.total_amount` and `total_vat_amount` are updated and saved.
6. The `amount_table` UI control is refreshed with the new totals.

### Cancelled items on reload

When the sale screen is re-entered (e.g. after navigating to the menu and back), `SaleService.update_sale_list_from_document()` is called. It **filters out** all records where `is_cancel = True`, so cancelled lines are **not displayed** in the restored sale list.

### Empty Document Handling

If the DELETE action cancels the **last remaining active line** in the document (i.e. there are no uncancelled products or departments left), the following automatic cleanup occurs:

1. `TransactionHeadTemp.is_cancel` is set to `True`
2. `TransactionHeadTemp.is_closed` is set to `True`
3. `TransactionHeadTemp.transaction_status` is set to `CANCELLED`
4. `total_amount` and `total_vat_amount` are set to `0`
5. The head record is saved to the database
6. `document_data` is reset to `None`
7. The status bar is cleared
8. The amount table is zeroed out

After this cleanup, the next sale will trigger `_ensure_document_open()` which creates a **new empty document** automatically. No manual action is required from the cashier.

**Summary of empty-document state combinations after last-item delete:**

| Flag | Value |
|------|-------|
| `is_closed` | `True` |
| `is_cancel` | `True` |
| `is_pending` | `False` |
| `transaction_status` | `CANCELLED` |
| `document_data` in memory | `None` |

## Full Document Cancellation (CANCEL Button)

Pressing the **CANCEL** button on the SALE form immediately voids the entire active transaction.

### How it works

1. The handler checks that an open document with at least one active (non-cancelled) line exists.
   - If no open document is found, an information dialog is shown and no changes are made.
2. The cashier's username is read from `cashier_data`.
3. `cancel_reason` is set to `"Canceled by cashier: {username}"`.
4. `complete_document(is_cancel=True, cancel_reason=...)` is called, which:
   - Sets `TransactionHeadTemp.transaction_status = CANCELLED`
   - Sets `TransactionHeadTemp.is_cancel = True`, `is_closed = True`
   - Copies all temp models to permanent models (`TransactionHead`, `TransactionProduct`, etc.)
   - Resets `document_data` to `None`
5. The UI controls (`sale_list`, `payment_list`, `amount_table`) are cleared.
6. A confirmation message box is displayed showing:
   - Receipt No
   - Closure No
   - Total amount
   - The cancel reason (cashier name)
7. A **new empty draft document** is created automatically for the next sale.

### When there is no open document

If `document_data` is `None`, the document is already closed/pending/cancelled, or there are no active lines, an info dialog is shown: *"There is no open document to cancel."* No database changes are made.

### Database state after cancellation

| Field | Value |
|-------|-------|
| `TransactionHeadTemp.transaction_status` | `cancelled` |
| `TransactionHeadTemp.is_cancel` | `True` |
| `TransactionHeadTemp.is_closed` | `True` |
| `TransactionHeadTemp.cancel_reason` | `"Canceled by cashier: {username}"` |
| `TransactionHead.transaction_status` | `cancelled` (permanent copy) |
| `TransactionHead.is_cancel` | `True` (permanent copy) |
| `TransactionHead.cancel_reason` | `"Canceled by cashier: {username}"` (permanent copy) |

> **Note:** This is different from the line-item **DELETE** action (which soft-cancels a single line). The CANCEL button voids the full document in one step.

---

## Line Item REPEAT (Sale List REPEAT)

Pressing **REPEAT** in the Item Actions popup adds an identical new transaction line immediately below the existing items.

### How it works

1. The original `TransactionProductTemp` (or `TransactionDepartmentTemp`) record is found in `document_data` using the row's `reference_id`.
2. A new record is cloned from the original with:
   - A freshly generated UUID (`id`)
   - `line_no` set to the next available line number
   - `is_cancel = False`
3. The clone is saved to the database and appended to `document_data["products"]` (or `["departments"]`).
4. The new row's `reference_id` in the `SaleList` is updated to the new DB record's UUID so that future REPEAT/DELETE actions on that row are correctly linked.
5. `calculate_document_totals()` recalculates the total and the `amount_table` is refreshed.

## Document Status Flags

The `TransactionHeadTemp` model includes three boolean flags:

- **`is_closed`**: `True` when transaction is completed and copied to permanent models
- **`is_pending`**: `True` when transaction is suspended (restaurant mode)
- **`is_cancel`**: `True` when transaction is cancelled

**Status Combinations:**
- `is_closed=False, is_pending=False, is_cancel=False`: Active/incomplete document
- `is_closed=False, is_pending=True, is_cancel=False`: Suspended document
- `is_closed=True, is_pending=False, is_cancel=False`: Completed document
- `is_closed=True, is_pending=False, is_cancel=True`: Cancelled document

## Transaction Status Enum

The `transaction_status` field uses `TransactionStatus` enum values:

- **`DRAFT`**: Initial state when document is created
- **`ACTIVE`**: Document is active and being processed
- **`PENDING`**: Document is suspended (restaurant mode)
- **`COMPLETED`**: Transaction completed successfully
- **`CANCELLED`**: Transaction was cancelled

## Methods Reference

### `create_empty_document()`

Creates a new empty document with all temp models initialized.

**Returns:** Dictionary with document structure or `None` if error

**Example:**
```python
document = self.create_empty_document()
if document:
    print(f"Created document: {document['head'].transaction_unique_id}")
```

### `load_incomplete_document()`

Loads the last incomplete document from database.

**Returns:** `True` if document loaded, `False` otherwise

**Example:**
```python
if self.load_incomplete_document():
    print("Resumed incomplete transaction")
```

### `load_pending_documents()`

Loads all pending documents (`is_pending=True`) from database into `pending_documents_data` list.

**Example:**
```python
self.load_pending_documents()
for doc in self.pending_documents_data:
    print(f"Pending: {doc['head'].transaction_unique_id}")
```

### `complete_document(is_cancel=False, cancel_reason=None)`

Completes the current document by copying all temp models to permanent models.

**Parameters:**
- `is_cancel`: If `True`, marks transaction as cancelled
- `cancel_reason`: Optional reason for cancellation

**Returns:** `True` if successful, `False` otherwise

**Example:**
```python
# Normal completion
self.complete_document()

# Cancelled transaction
self.complete_document(
    is_cancel=True,
    cancel_reason="Customer requested cancellation"
)
```

### Payment Processing

Payment processing is handled through `PaymentService` and payment event handlers. The system supports multiple payment types and automatic change calculation.

**Payment Types:**
- `CASH_PAYMENT`: Cash payment
- `CREDIT_PAYMENT`: Credit card payment
- `CHECK_PAYMENT`: Check payment
- `EXCHANGE_PAYMENT`: Exchange/trade-in payment
- `PREPAID_PAYMENT`: Prepaid card payment
- `CHARGE_SALE_PAYMENT`: Charge sale (house account)
- `OTHER_PAYMENT`: Other payment methods
- `BONUS_PAYMENT`: Loyalty point redemption (adds **`LOYALTY`** discount via **`LoyaltyRedemptionService`**, not `TransactionPaymentTemp`)
- `CHANGE_PAYMENT`: Calculate and record change

**Payment Button Naming Conventions:**
- Buttons starting with `PAYMENT`: Pay remaining balance
- Buttons starting with `CASH`: Pay specific amount (number after CASH divided by 100)
  - Example: `CASH1000` = 10.00 payment (1000 / 100)
  - Example: `CASH5000` = 50.00 payment (5000 / 100)

**Payment Amount Behavior:**
- **CASH_PAYMENT, CHECK_PAYMENT, EXCHANGE_PAYMENT**: Use exact button amount
- **CREDIT_PAYMENT, PREPAID_PAYMENT, CHARGE_SALE_PAYMENT, OTHER_PAYMENT**: Limit to remaining **net** balance (min(button_amount, remaining_balance))

**Payment Flow:**
1. User clicks payment button
2. Payment amount is calculated based on button name and payment type
3. `TransactionPaymentTemp` record is created and saved
4. `TransactionHeadTemp.total_payment_amount` is updated
5. UI controls (PaymentList, AmountTable) are updated
6. Change is calculated if payment exceeds **net** due
7. **Change Recording Behavior:**
   - If `CHANGE_PAYMENT` button exists in form: User is informed to click change button to record change
   - If `CHANGE_PAYMENT` button doesn't exist: MessageForm dialog is shown with change amount, and change is recorded when OK is clicked
8. Document completion is checked automatically after change is recorded (or if no change needed)
9. If complete (net: `(total_amount - total_discount_amount) = total_payment_amount - total_change_amount`):
   - Document is marked as COMPLETED
   - Closure totals are updated
   - Receipt number is incremented
   - Temp models are copied to permanent models: **`LoyaltyEarnService.stage_document_earn`**, then head/**discounts**/payments/changes/**`TransactionLoyalty`**; then **`LoyaltyService.on_sale_transaction_completed`** (spend counters, **`LoyaltyPointTransaction` REDEEMED / EARNED**, tier) and **`CustomerSegmentService.on_sale_transaction_completed`** for non–walk-in **sale** receipts
   - UI controls are cleared
   - `document_data` is reset

**Example:**
```python
from pos.service import PaymentService

# Process cash payment with button name CASH1000 (pays 10.00)
success, payment_temp, error = PaymentService.process_payment(
    document_data=document_data,
    payment_type="CASH_PAYMENT",
    button_name="CASH1000"
)

# Calculate change amount
change_amount = PaymentService.calculate_change(document_data)
if change_amount > 0:
    # Record change manually (or via MessageForm if CHANGE_PAYMENT button doesn't exist)
    # This is typically done by clicking CHANGE_PAYMENT button or via MessageForm dialog
    PaymentService.record_change(document_data)

# Check if document is complete (automatically done after payment)
if PaymentService.is_document_complete(document_data):
    PaymentService.mark_document_complete(document_data)
    PaymentService.update_closure_for_completion(closure, document_data)
    # copy_temp_to_permanent: LoyaltyEarnService + discounts + LoyaltyService + CustomerSegmentService
    PaymentService.copy_temp_to_permanent(document_data)
```

### `set_document_pending(is_pending=True)`

Sets the current document as pending (suspended) or resumes it.

**Parameters:**
- `is_pending`: `True` to suspend, `False` to resume

**Returns:** `True` if successful, `False` otherwise

**Example:**
```python
# Suspend document
self.set_document_pending(is_pending=True)

# Resume document
self.set_document_pending(is_pending=False)
```

## Benefits

1. **Transaction Safety**: Temp models ensure incomplete transactions don't affect reporting
2. **Restaurant Mode Support**: Pending documents enable table/order management
3. **Data Integrity**: Clear separation between active and completed transactions
4. **Resume Capability**: Incomplete transactions can be resumed after application restart
5. **Audit Trail**: All transaction states are tracked in the database

---

[← Back to Table of Contents](README.md) | [Previous: Service Layer](25-service-layer.md) | [Next: Data Caching →](27-data-caching.md)

