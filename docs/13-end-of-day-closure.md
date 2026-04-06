# Closure Operation (End-of-Day)

## Overview

The **closure operation** is triggered when an authorized cashier presses the CLOSURE button. It aggregates all completed transactions that share the current closure number, creates a single `Closure` record with all summary tables, then advances the transaction sequences so the next sale uses a new closure number and receipt number 1.

## Authorization

- Only **administrators** (`Cashier.is_administrator == True`) may perform closure.
- If a non-authorized user presses the CLOSURE button, an error is shown via `MessageForm` (error mode) and the process stops.
- The user must be logged in and have valid `cashier_data`; otherwise an error is shown and the process stops.

## Flow

1. **Authorization check**  
   - If not logged in or no cashier: show error, return `False`.  
   - If cashier is not administrator: show error (e.g. "Only authorized cashiers can perform closure"), return `False`.

2. **Read current closure number**  
   - From `TransactionSequence`: row with `name = "ClosureNumber"`, use its `value` as `current_closure_number`.  
   - If not found: show configuration error, return `False`.

3. **Load transactions**  
   - All `TransactionHead` with `closure_number == current_closure_number` and `is_deleted == False`.  
   - Heads with **`is_pending == True`** are **excluded** from sales totals, payment/tax/discount aggregation, and document counts used for the closure batch.  
   - Additionally, **`TransactionHeadTemp`** rows with the same `closure_number`, `is_pending == True`, `is_closed == False`, and not deleted are counted as suspended but **not** included in those totals.  
   - **`suspended_transaction_count`** on the `Closure` record = count of pending permanent heads in the batch + count of such temp pending heads.  
   - **If there are no non-pending heads and no suspended documents (temp or permanent):** show error ("No transactions found …"), return `False`. If there are only suspended documents, closure is still allowed with zero financial totals and a non-zero `suspended_transaction_count`.

4. **Resolve context**  
   - Store, POS, and base currency from the first transaction or from `pos_data` / `pos_settings` / `product_data` as fallback.  
   - If store, POS or base currency cannot be resolved: show error, return `False`.

5. **Aggregate totals**  
   From the selected heads and related tables:
   - **Heads**: gross/net sales, tax, discount, tip, valid/canceled/return counts, expected cash.  
   - **TransactionPayment**: by payment type (count, amount), by currency (amount, base amount, exchange rate), and tip by payment type.  
   - **TransactionTax**: by (tax_rate, tax_name, jurisdiction) for VAT/tax summary.  
   - **TransactionDiscount**: by discount type (count, amount).  
   - **TransactionDepartment**: by department (count, gross, tax, net, discount).  
   - **Document type**: from head `document_type` (valid/canceled counts and amounts).

6. **Create main Closure record**  
   - `closure_number`, `fk_store_id`, `fk_pos_id`, `closure_date`, `closure_start_time`, `closure_end_time`, `fk_base_currency_id`, cashier opened/closed, and all aggregated totals (document count, gross/net, tax, discount, tip, valid/canceled/return counts, **`suspended_transaction_count`**, expected cash, etc.).

7. **Create summary records**  
   - **ClosureVATSummary**: one row per (tax rate, name, jurisdiction) from tax aggregation.  
   - **ClosureTipSummary**: one row per payment type that has tips.  
   - **ClosureDiscountSummary**: one row per discount type.  
   - **ClosurePaymentTypeSummary**: one row per payment type.  
   - **ClosureDocumentTypeSummary**: one row per document type (valid/canceled counts and amounts).  
   - **ClosureDepartmentSummary**: one row per department.  
   - **ClosureCurrency**: one row per currency used in payments.  
   - **ClosureCashierSummary**: one row for the closing cashier with period totals (transaction count, total sales, averages, void/correction if available).

8. **Update sequences**  
   - In `TransactionSequence`:  
     - Row with `name = "ClosureNumber"`: set `value = value + 1`.  
     - Row with `name = "ReceiptNumber"`: set `value = 1`.  
   - Then refresh `pos_data` for `TransactionSequence` so the next document uses the new values.

9. **Discard the pre-created empty draft**  
   - After every completed payment `PaymentEvent._check_and_complete_document()` calls `_increment_receipt_number()` and then immediately calls `create_empty_document()`, leaving an empty `TransactionHeadTemp` draft in `self.document_data` with the **old** `receipt_number`.  
   - `abandon_empty_open_document_if_any()` soft-deletes that draft from the database.  
   - `self.document_data` is set to `None`.  
   - Without this step the guard at the top of `create_empty_document()` would return the stale draft on the next SALE navigation, keeping the old receipt number instead of resetting to 1.  
   - **Result**: The very next sale document will carry `receipt_number = 1` and the new `closure_number`.

10. **Create new open closure**  
   - Call `create_empty_closure()` which reads the new `ClosureNumber` value directly from `transaction_sequence` (the global monotonic counter just incremented in step 8) and creates a new open `Closure` row with that number.  
   - This sets `CurrentData.closure` to the new open closure for the next period.  
   - **Important:** `create_empty_closure()` must always source the next closure number from `transaction_sequence.ClosureNumber`, not from `max(closure_number WHERE closure_date = today)`. The per-day approach resets to 1 at the start of each new calendar day, overwriting the global counter.

11. **Return**  
   - On success: `True`.  
   - On any error: show error (if applicable), return `False`.

## Event and Code Location

- **Event**: `EventName.CLOSURE` (CLOSURE button), handled in `pos/manager/event_handler.py`.  
- **Handler**: `ClosureEvent._closure_event()` in `pos/manager/event/closure.py`.  
- **Error display**: `user_interface/form/message_form.py` (`MessageForm.show_error`).

## Models Involved

- **Sequence**: `TransactionSequence` (ClosureNumber, ReceiptNumber).  
- **Transactions**: `TransactionHead`, `TransactionPayment`, `TransactionTax`, `TransactionDiscount`, `TransactionDepartment`, `TransactionTip`, `TransactionVoid`, `TransactionRefund`, `TransactionDocumentType`, `TransactionDiscountType`.  
- **Closure**: `Closure`, `ClosureVATSummary`, `ClosureTipSummary`, `ClosureDiscountSummary`, `ClosurePaymentTypeSummary`, `ClosureDocumentTypeSummary`, `ClosureDepartmentSummary`, `ClosureCurrency`, `ClosureCashierSummary`.  
- **Reference**: `PaymentType`, `Currency`, `Vat`, `TransactionDocumentType`, `TransactionDiscountType`, `DepartmentMainGroup`, store and POS from `pos_data`/`pos_settings`.

## Result

- One closed `Closure` row and multiple summary rows are stored in the database.  
- A new open `Closure` row is created for the next period (see step 10).  
- `CurrentData.closure` is updated to the new open closure.  
- The next sale will use `ClosureNumber = current + 1` and `ReceiptNumber = 1`.  
- Every closure period's receipts are numbered independently: receipt 1, 2, 3 … starting fresh after each closure.

## Transaction Unique ID Format

`transaction_unique_id` (stored on both `TransactionHeadTemp` and `TransactionHead`) uses the format:

```
{YYYYMMDD}-{closure_number:04d}-{receipt_number:06d}
```

Examples:
- `20250406-0001-000001` — 6 April 2025, closure 1, receipt 1
- `20250406-0001-000042` — 6 April 2025, closure 1, receipt 42
- `20250406-0002-000001` — 6 April 2025, closure 2, receipt 1 (first receipt **after** end-of-day closure)

Including `closure_number` between the date and the receipt number guarantees that resetting `ReceiptNumber` to 1 after closure **never conflicts** with earlier receipts from the same calendar day. Each closure period is fully namespace-isolated.

## Closure Number Sequencing

`transaction_sequence.ClosureNumber` is a **global monotonic counter** — it never resets across calendar days or application restarts.

| Who reads it | When | Purpose |
|---|---|---|
| `ClosureEvent._closure_event()` | On CLOSURE button press | Identifies which transactions belong to the batch being closed |
| `ClosureManager.create_empty_closure()` | After closure or at startup | Sets the `closure_number` on the new open closure |

**`_sync_closure_number_sequence()`** (called from `load_open_closure` and `create_empty_closure`) synchronises the DB row **upward only** — if the active closure's number is greater than the DB value, it corrects the DB. It never decreases the counter, preventing any per-day reset from corrupting the sequence.

---

[← Back to Table of Contents](README.md) | [Previous: Cancellations](12-cancellations.md) | [Next: Cashier Management →](14-cashier-management.md)
