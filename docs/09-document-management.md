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
    "totals": List[TransactionTotalTemp],
    "deliveries": List[TransactionDeliveryTemp],
    "kitchen_orders": List[TransactionKitchenOrderTemp],
    "loyalty": List[TransactionLoyaltyTemp],
    "notes": List[TransactionNoteTemp],
    "fiscal": TransactionFiscalTemp or None,
    "refunds": List[TransactionRefundTemp],
    "surcharges": List[TransactionSurchargeTemp],
    "taxes": List[TransactionTaxTemp],
    "tips": List[TransactionTipTemp]
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
- `document_type`: First `TransactionDocumentType` record from database
- `transaction_type`: `TransactionType.SALE`
- `transaction_status`: `TransactionStatus.DRAFT`
- `closure_number`: Value from `TransactionSequence` where `name="ClosureNumber"`
- `receipt_number`: Value from `TransactionSequence` where `name="ReceiptNumber"`
- `fk_store_id`: First `Store` record from `pos_data`
- `pos_id`: `pos_no_in_store` from `PosSettings`
- `is_closed`: `False`
- `is_pending`: `False`
- `is_cancel`: `False`

### 2. Document Loading

**Incomplete Documents:**
At application startup, the system automatically loads any incomplete transaction:

```python
# Automatically called at startup
self.load_incomplete_document()
```

An incomplete document is one where:
- `is_closed = False`
- `is_pending = False`
- `is_cancel = False`

**Pending Documents:**
All pending documents (suspended transactions) are loaded at startup:

```python
# Automatically called at startup
self.load_pending_documents()
```

Pending documents are used in restaurant mode for managing tables/orders that are temporarily suspended.

### 3. Document Suspension (Restaurant Mode)

In restaurant mode, documents can be suspended (put on hold) to allow adding more items later:

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
   - `TransactionPaymentTemp` → `TransactionPayment`
   - And all other related temp models
3. Updates foreign keys correctly (maps temp IDs to permanent IDs)
4. Saves everything to database
5. Resets `document_data` to `None`

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

# Add payment
payment = TransactionPaymentTemp()
payment.fk_transaction_head_id = document["head"].id
payment.payment_type = "cash"
payment.payment_total = 20.00
# ... set other fields
document["payments"].append(payment)

# Complete transaction
self.complete_document()
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

### Example 3: Loading Incomplete Document at Startup

```python
# In Application.__init__()
# After loading pos_data and product_data

# Load incomplete document if exists
if self.load_incomplete_document():
    print(f"Resumed transaction: {self.document_data['head'].transaction_unique_id}")
else:
    print("No incomplete transaction found")

# Load pending documents
self.load_pending_documents()
print(f"Loaded {len(self.pending_documents_data)} pending documents")
```

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

[← Back to Table of Contents](README.md) | [Previous: Data Caching Strategy](08-data-caching.md) | [Next: Database Models Overview →](10-database-models.md)

