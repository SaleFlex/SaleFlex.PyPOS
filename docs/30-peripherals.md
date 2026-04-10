# Peripherals (OPOS-style device layer)

**Last Updated:** 2026-04-06

SaleFlex.PyPOS exposes a small **peripheral** package under `pos/peripherals/`. The API is inspired by OPOS-style devices (logical names, open/claim/release/close on the base type), but **no hardware connections are opened** in the current build: commands are written to the application log so drivers can be added later without changing call sites.

## Package layout

| Module | Class | Role |
|--------|--------|------|
| `opos_device.py` | `OposDevice` | Minimal lifecycle stubs (`open`, `claim`, `release`, `close`). |
| `cash_drawer.py` | `CashDrawer` | `open_drawer(reason=...)` — logged as `[CashDrawer]`. |
| `pos_printer.py` | `POSPrinter` | `print_sale_document(document_data)` — formats sale receipt and logs each line as `[POSPrinter] \| <line>`. `print_closure_document(closure_data)` — formats end-of-day Z-report and logs each line. |
| `line_display.py` | `LineDisplay` | `send_three_lines(line1, line2, line3)` — logged as `[LineDisplay]`. |
| `scanner.py` | `Scanner` | Stub for future barcode integration. |
| `scale.py` | `Scale` | Stub for future weight integration. |
| `customer_display.py` | `CustomerDisplay` | Stub for a secondary customer-facing screen. |
| `remote_order_display.py` | `RemoteOrderDisplay` | Stub for kitchen / remote order displays. |
| `document_adapter.py` | (functions) | `format_receipt_lines()` builds a thermal-printer-style receipt as a list of strings; `build_three_lines_from_document()` infers pole-display lines. |
| `hooks.py` | (functions) | `sync_line_display_*` helpers gated on `FormName.SALE`. |

Default singleton-style accessors: `get_default_cash_drawer()`, `get_default_pos_printer()`, `get_default_line_display()`.

## Sale receipt format

`POSPrinter.print_sale_document` calls `format_receipt_lines(document_data)` which returns each receipt line as a plain string. The printer logs every line individually with an `[POSPrinter] |` prefix, making it easy to grep from the log or to forward to a real ESC/POS driver.

Receipt width is **38 characters**. Layout:

```
======================================
           SALE RECEIPT
Receipt: 00001  06/04/2026 14:35:22
======================================
CHSE/SPRNG ONION              £1.00
CHSE/SPRNG ONION              £1.00
SEED L3.45 (NO VAT)           £3.49
SEEDS L1.99 (NO VAT)          £1.99
TWIN DARJ LSE TEA125          £1.69
ENG/BREAKFST TEA              £1.69
ASSAM TEA 125G
  2 x £1.69                   £3.38
--------------------------------------
7 BALANCE DUE                £15.93
   CASH                      £20.00

   CHANGE                     £4.07
   VAT                        £1.40
**************************************
```

Rules:
- Product with `quantity == 1` → single line: name left, price right.
- Product with `quantity > 1` → two lines: name on first line, `  qty x unit_price` + total on the second.
- Cancelled / voided lines (`is_cancel=True` or `is_voided=True`) are omitted.
- Department lines (sold without a specific product) appear as `DEPT {line_no}`.
- Discount lines appear as `{discount_type}  -£{amount}`. **`LOYALTY`** lines use **`discount_code`** when present (e.g. `100PTS`). **`CAMPAIGN`** lines use **`discount_code`** for **`Campaign.code`** or a short coupon token (e.g. `CAMPAIGN (WELCOME10)`).
- The `{N} BALANCE DUE` label shows the count of active (non-cancelled) lines and reflects **net** due (after discounts, including loyalty redemption and campaign lines when present).
- Each payment method is shown on its own line (e.g. `CASH`, `CREDIT`, `CHECK`).
- `CHANGE` is printed only when change > 0, preceded by a blank line.
- `VAT` (from `head.total_vat_amount`) is always printed, even when zero.
- The footer is a row of `*` characters.

### Currency symbols

| ISO code | Symbol |
|----------|--------|
| GBP | £ |
| USD | $ |
| EUR | € |
| TRY | ₺ |
| JPY / CNY | ¥ |
| KRW | ₩ |
| INR | ₹ |
| AUD | A$ |
| CAD | C$ |
| CHF | Fr |
| (other) | raw 3-letter code |

### Payment type display labels

| `payment_type` value | Receipt label |
|----------------------|---------------|
| `CASH_PAYMENT` | `CASH` |
| `CREDIT_PAYMENT` | `CREDIT` |
| `CHECK_PAYMENT` | `CHECK` |
| `EXCHANGE_PAYMENT` | `EXCHANGE` |
| `PREPAID_PAYMENT` | `PREPAID` |
| `CHARGE_SALE_PAYMENT` | `CHARGE` |
| `OTHER_PAYMENT` | `OTHER` |

## Closure Z-report format

`POSPrinter.print_closure_document` calls `format_closure_lines(closure_data)` which returns the full end-of-day report as a list of strings. The printer logs every line individually with the same `[POSPrinter] |` prefix.

Report width is **42 characters**. Layout:

```
==========================================
          END-OF-DAY CLOSURE
==========================================
Closure: #0001    03/01/2025 10:18
  ID: 20250103-0001
  Period: 30/10/2024 13:46 to 03/01/2025 10:18
  Cashier: John Doe
  Register: Main POS
==========================================
                                       GBP
NET SALES
    34  Sales                        417.96
     0  Returns                        0.00
------------------------------------------
  Total net sales:                   417.96
  Taxes:                              75.61
  Total gross sum:                   493.57
------------------------------------------
CANCELLED RECEIPTS:                      0
------------------------------------------
CASH BALANCE
  Opening cash:                        0.00
  Gross sales (cash):                493.57
  Deposits (0):                        0.00
  Withdrawals (0):                     0.00
  Change (non-cash):                   0.00
  Tips:                                0.00
------------------------------------------
  Cash register balance:             493.57
  Expected:                          493.57
  Difference:                          0.00
------------------------------------------
VAT SUMMARY
  Rate%       Net       Tax     Gross
  -------  --------  --------  --------
   0.00%     19.99      0.00     19.99
  19.00%    397.97     75.61    473.58
  -------  --------  --------  --------
  Total     417.96     75.61    493.57
------------------------------------------
PAYMENT METHODS
  CASH (34)                          493.57
------------------------------------------
  Total                              493.57
------------------------------------------
DOCUMENT TYPES
  FISCAL RECEIPT      34 valid    0 cancel
------------------------------------------
TRANSACTION SUMMARY
  Valid:         34   Cancelled:         0
  Returns:        0   Suspended:         0
==========================================
```

### `closure_data` dict

| Key | Type | Description |
|-----|------|-------------|
| `closure` | `Closure` ORM record | All head-level fields (number, dates, amounts, counts). |
| `totals` | `dict` | Aggregated totals from `ClosureEvent._aggregate_closure_totals`. Contains `by_tax`, `by_payment_type`, `by_document_type`, scalar amounts and counts. |
| `currency_code` | `str` | ISO-4217 code used for the symbol lookup. |
| `cashier_name` | `str` | Closing cashier display name (optional). |
| `pos_name` | `str` | POS register name from `PosSettings.name` (optional). |
| `pos_serial` | `str` | Device serial from `PosSettings.device_serial_number` (optional). |

The report is assembled in `ClosureEvent._print_closure_report()` and sent immediately after all closure DB records are committed and sequences are updated, just before the success dialog is shown.

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

---

[← Back to Table of Contents](README.md) | [Previous: Data Caching](27-data-caching.md) | [Next: Central Logging →](31-logging.md)
