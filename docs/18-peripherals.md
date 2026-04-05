# Peripherals (OPOS-style device layer)

**Last Updated:** 2026-04-05

SaleFlex.PyPOS exposes a small **peripheral** package under `pos/peripherals/`. The API is inspired by OPOS-style devices (logical names, open/claim/release/close on the base type), but **no hardware connections are opened** in the current build: commands are written to the application log so drivers can be added later without changing call sites.

## Package layout

| Module | Class | Role |
|--------|--------|------|
| `opos_device.py` | `OposDevice` | Minimal lifecycle stubs (`open`, `claim`, `release`, `close`). |
| `cash_drawer.py` | `CashDrawer` | `open_drawer(reason=...)` — logged as `[CashDrawer]`. |
| `pos_printer.py` | `POSPrinter` | `print_sale_document(document_data)` — full receipt text logged as `[POSPrinter]`. |
| `line_display.py` | `LineDisplay` | `send_three_lines(line1, line2, line3)` — logged as `[LineDisplay]`. |
| `scanner.py` | `Scanner` | Stub for future barcode integration. |
| `scale.py` | `Scale` | Stub for future weight integration. |
| `customer_display.py` | `CustomerDisplay` | Stub for a secondary customer-facing screen. |
| `remote_order_display.py` | `RemoteOrderDisplay` | Stub for kitchen / remote order displays. |
| `document_adapter.py` | (functions) | Builds receipt text and infers pole-display lines from `document_data`. |
| `hooks.py` | (functions) | `sync_line_display_*` helpers gated on `FormName.SALE`. |

Default singleton-style accessors: `get_default_cash_drawer()`, `get_default_pos_printer()`, `get_default_line_display()`.

## Behaviour on `FormName.SALE`

- **Document completed (paid in full, change recorded if required)**  
  When `_check_and_complete_document` finishes successfully, **every** completion path runs `POSPrinter.print_sale_document` (log only) and then `CashDrawer.open_drawer("document_completed")` — not only on `FormName.SALE`. The UI is cleared, a new empty document is created, and on the SALE form the line display is refreshed from the new totals.

- **CASH payment when there is nothing to pay on the ticket**  
  The session usually still has a `TransactionHeadTemp` (empty pre-created document), so “no document” is detected as: **no head**, or **no balance left to collect** with **no payments yet** (`total_amount - total_payment_amount <= 0` and `total_payment_amount == 0`, i.e. empty/zero ticket). In that case only `CashDrawer.open_drawer("CASH_PAYMENT_no_open_sale_or_nothing_to_pay")` runs and `PaymentService` is not called. If there is a positive balance, normal cash payment processing runs.

- **Line display while selling**  
  After each successful `_update_document_data_for_sale` (PLU / barcode / department), and after sale-list **REPEAT** / **DELETE** sync, the pole display is updated. **DELETE** that cancels the whole document clears the display to a ready state.

  - **Selling:** line 1 = last active line description (product name, department label, or discount type), line 2 = unit price / line amount / discount amount, line 3 = document `total_amount`.

- **Line display during payment**  
  After each payment row is applied (`_update_payment_ui`), line 1 = tendered payment amount, line 2 = document total, line 3 = remaining balance (`total_amount - total_payment_amount`).

## `OPEN_CASH_DRAWER` event

`HardwareEvent._open_cash_drawer_event` delegates to the same default `CashDrawer` instance so manual drawer opens share logging and future driver wiring.

## Related documentation

- [Document Management](09-document-management.md) — transaction lifecycle and temp/permanent models.
- [Service Layer](14-service-layer.md) — `SaleService` / `PaymentService` and document completion rules.
- [Central Logging](16-logging.md) — where peripheral log lines appear.
