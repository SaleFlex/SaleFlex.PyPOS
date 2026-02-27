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
   - **If no such records exist:** show error ("No transactions found for closure number …"), stop and return `False`. Closure is not performed.
   - Otherwise these heads are the sales that belong to this closure batch.

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
   - `closure_number`, `fk_store_id`, `fk_pos_id`, `closure_date`, `closure_start_time`, `closure_end_time`, `fk_base_currency_id`, cashier opened/closed, and all aggregated totals (document count, gross/net, tax, discount, tip, valid/canceled/return counts, expected cash, etc.).

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

9. **Update current_data**  
   - Call `create_empty_closure()` so that the in-memory closure (`CurrentData.closure`) is set to a new open closure for the next period.

10. **Return**  
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

- One new `Closure` row and multiple summary rows are stored.  
- The next sale will use `ClosureNumber = current + 1` and `ReceiptNumber = 1`.  
- In-memory closure (e.g. in `CurrentData.closure`) is not modified by this flow; this operation only writes the closure batch to the database and advances sequences.
