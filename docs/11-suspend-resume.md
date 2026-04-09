# Suspend and Resume Sales

The **SUSPEND** feature lets you park the current cart and start a new sale immediately. Parked carts can be retrieved at any time. This is the standard flow for **market/retail** environments where multiple customers queue at the same terminal.

---

## The SUSPEND Button (dual-function)

The **SUSPEND** button (`PAYMENT_SUSPEND`) appears on the SALE screen at the bottom-right of the action button area. It is a **dual-function button** with two states controlled by the **FUNC** button:

| State | Label shown | Event dispatched | How to activate |
|-------|-------------|-----------------|-----------------|
| 1 — normal | **SUSPEND** | `SUSPEND_SALE` | Default / press **FUNC** again |
| 2 — alternate | **CANCEL** | `CANCEL_DOCUMENT` | Press **FUNC** first |

A small **"F"** badge in the top-right corner of the button indicates dual-function mode.

**FUNC button:** Pressing **FUNC** (Steel Blue button to the left of CHANGE) flips **labels** on all dual-function buttons on the SALE form between normal and alternate. Press **FUNC** again to return to normal. Tapping **SUSPEND** or **CANCEL** (when shown) runs that action and resets **every** dual-function button on the form to normal captions.

> For the full dual-function button specification see [UI Controls — Dual-Function Buttons](23-ui-controls.md#dual-function-buttons) and [UI Controls — FUNC Button](23-ui-controls.md#func-button--global-function-mode-toggle).

### Behaviour at a Glance

| Situation | What happens |
|-----------|--------------|
| Open document with ≥ 1 active line | Current cart is suspended (parked). A new empty draft opens automatically. |
| Empty draft (no lines yet) | The **Suspended Sales** list opens so you can review or activate a parked cart. |
| No open document | The **Suspended Sales** list opens. |

### Suspending a Cart (parking)

When there is an active sale with at least one product line:

1. The cashier presses **SUSPEND**.
2. The document is marked `is_pending = True`, `transaction_status = PENDING` and saved.
3. `document_data` is cleared.
4. A **new empty draft** is created automatically for the next customer — the receipt number is advanced so the next sale uses a fresh slot.
5. The SALE screen refreshes and is ready for the next customer.

The suspended cart is stored in the database and appears in the **Suspended Sales** list.

### Opening the Suspended Sales List

When **SUSPEND** is pressed with no active lines (or no document), the application navigates to the `SUSPENDED_SALES_MARKET` form, which shows a DataGrid with:

| Column | Content |
|--------|---------|
| (hidden) Id | Internal UUID of the suspended `TransactionHeadTemp` |
| Receipt No | Original receipt number |
| Line count | Number of product/department lines |
| Total | Cart total |

### Resuming (Activating) a Parked Cart

1. Select a row in the Suspended Sales list.
2. Press **ACTIVATE**.
3. The system loads the selected cart: `is_pending` is cleared, `transaction_status` is set back to `ACTIVE`.
4. The SALE screen is redrawn with the restored cart (products, totals, payments).
5. Pressing **BACK** from the sale screen after resuming returns to the main menu — not to the suspended list.

> **Note:** The startup recovery (`load_incomplete_document`) only loads documents with `is_pending = False`. Suspended carts are not auto-restored as the "current" sale on application restart.

---

## Restaurant Mode (pending documents)

In restaurant mode the same `is_pending` mechanism is used to manage table orders. Multiple tables can each have a pending document loaded from `pending_documents_data`. The exact table management forms are configured in the database and routed via events (`TABLE_OPEN`, `TABLE_SELECT`, etc.).

---

## Related Events

| `EventName` | Handler | Description |
|-------------|---------|-------------|
| `SUSPEND_SALE` | `_suspend_sale_event` | Park current cart or open suspended list |
| `RESUME_SALE` | `_resume_sale_event` | Activate a selected suspended cart |
| `SUSPEND_LIST` | `_suspend_list_event` | Open the suspended sales list directly |
| `DELETE_SUSPENDED_SALE` | `_delete_suspended_sale_event` | Remove a parked cart from the list |

---

[← Back to Table of Contents](README.md) | [Previous: Sale Transactions](10-sale-transactions.md) | [Next: Cancellations →](12-cancellations.md)
