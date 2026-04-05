# Cancellations

SaleFlex.PyPOS distinguishes between two types of cancellation:

| Type | Scope | Button |
|------|-------|--------|
| **Line cancellation** | Single product/department line | **DELETE** in the Item Actions popup |
| **Full document cancellation** | Entire open transaction | **CANCEL** button on the SALE screen |

---

## Line Cancellation (Item DELETE)

### How to cancel a single line

1. Tap the row in the sale list → the **Item Actions** popup opens.
2. Press **DELETE**.
3. The line's `TransactionProductTemp` (or `TransactionDepartmentTemp`) record is immediately marked `is_cancel = True` and saved to the database.
4. The row remains visible in the current session with a **strikethrough** style.
5. `SaleService.calculate_document_totals()` recalculates the document total, skipping cancelled lines.
6. `TransactionHeadTemp.total_amount` and `total_vat_amount` are updated and saved.
7. The amount table refreshes with the new totals.

### Cancelled lines on reload

When the sale screen is re-entered (e.g. after navigating to the menu and back), cancelled lines are **not** shown in the restored sale list.

### Last-line cancellation (auto-document cancel)

If DELETE cancels the **last remaining active line** in the document:

| Field | Value set |
|-------|-----------|
| `TransactionHeadTemp.is_cancel` | `True` |
| `TransactionHeadTemp.is_closed` | `True` |
| `TransactionHeadTemp.transaction_status` | `CANCELLED` |
| `total_amount` / `total_vat_amount` | `0` |
| `document_data` (in memory) | `None` |

After this the status bar clears, the amount table shows zeros, and the next product sale starts a **new empty document** automatically.

---

## Full Document Cancellation (CANCEL Button)

### Where is the CANCEL button?

The red **CANCEL** button is located on the SALE screen in the same button row as **PLU**, **X**, and **SUSPEND** — at the bottom of the payment area, below the denomination buttons.

### What it does

| Situation | Result |
|-----------|--------|
| Open document with ≥ 1 active line | Entire transaction is voided immediately |
| No open document / empty draft / already closed | Info dialog: *"There is no open document to cancel."* No database change. |

### Cancellation flow

1. The handler reads `cashier_data.user_name` to build the cancel reason.
2. `cancel_reason` is set to `"Canceled by cashier: {username}"`.
3. `complete_document(is_cancel=True, cancel_reason=…)` is called:
   - `TransactionHeadTemp.transaction_status` → `CANCELLED`
   - `TransactionHeadTemp.is_cancel` → `True`
   - `TransactionHeadTemp.is_closed` → `True`
   - All temp models are copied to permanent models (`TransactionHead`, `TransactionProduct`, etc.).
   - `document_data` is reset to `None`.
4. UI controls (`sale_list`, `payment_list`, `amount_table`) are cleared.
5. A **confirmation dialog** is shown with:
   - Receipt No
   - Closure No
   - Total amount
   - Cancel reason (cashier name)
6. After dismissal, a **new empty draft document** is created automatically.

### Database state after CANCEL

| Field | Value |
|-------|-------|
| `TransactionHeadTemp.transaction_status` | `cancelled` |
| `TransactionHeadTemp.is_cancel` | `True` |
| `TransactionHeadTemp.is_closed` | `True` |
| `TransactionHeadTemp.cancel_reason` | `"Canceled by cashier: {username}"` |
| `TransactionHead.*` (permanent copy) | Same values |

---

## Related Events

| `EventName` | Handler | Description |
|-------------|---------|-------------|
| `CANCEL_DOCUMENT` | `_cancel_document_event` | Full document cancellation (CANCEL button) |
| `CANCEL_SALE` | `_cancel_sale_event` | Cancel sale (same as above, alternate event name) |
| `CANCEL_PLU` | `_cancel_plu_event` | Cancel last PLU line |
| `CANCEL_LAST_SALE` | `_cancel_last_sale_event` | Cancel last sale line |
| `CANCEL_DEPARTMENT` | `_cancel_department_event` | Cancel department line |

> For the complete document lifecycle, see [Document Management System](26-document-management.md).

---

[← Back to Table of Contents](README.md) | [Previous: Suspend and Resume Sales](11-suspend-resume.md) | [Next: End-of-Day Closure →](13-end-of-day-closure.md)
