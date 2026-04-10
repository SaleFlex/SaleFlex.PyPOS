# Sale Transactions

## Opening the Sale Screen

From the main menu, press **SALES**. If no open document exists the system automatically creates a new draft document and displays an empty sale screen. If an incomplete transaction was interrupted (e.g. by a previous application restart), it is restored automatically.

![SALE form (default dual labels)](../static_files/images/sample_sale_form.jpg)

---

## NumPad — Four Operating Modes

The NumPad in the SALE form supports four distinct interaction modes depending on which action follows the numeric input.

### Mode 1 — Barcode / PLU Code Lookup (ENTER)

Type a number and press **ENTER**.

1. The system searches `ProductBarcode.barcode` for an exact match.
2. If not found it searches `Product.code` for an exact match.
3. On success the product is added to the sale list using the current `pending_quantity` (set by the **X** button, default 1).
4. On failure an error dialog is shown.

```
NumPad: 5000157070008  → ENTER
Result: 1× Coca-Cola added (barcode match)

NumPad: 1001  → ENTER
Result: 1× Salted Crisps added (product code match)
```

> **PLU inquiry (no sale):** If you pressed **PLU** with an *empty* NumPad first, the next ENTER opens an info dialog showing the product **price** and **stock per warehouse** — no line is added to the sale.

### Mode 2 — Inline Quantity × PLU Button

Type a quantity on the NumPad and immediately click a **PLU / barcode product button**. The NumPad value is consumed as the sale quantity; the button supplies the product.

```
NumPad: 3  → click [Coca-Cola button]
Result: 3× Coca-Cola added
```

If the NumPad is empty when a PLU button is clicked, quantity defaults to **1**.

### Mode 3 — X (Quantity Multiplier) and PLU (Inquiry) Buttons

Two adjacent buttons appear on the same row below the payment list:

| Button | Label | `EventName` | Purpose |
|--------|-------|------------|---------|
| Left | **PLU** | `PLU_INQUIRY` | Show price and stock without selling |
| Right | **X** | `INPUT_QUANTITY` | Pre-set quantity multiplier for the next scan |

#### X — Quantity Multiplier

Useful when you cannot type a quantity and click a button simultaneously (e.g. barcode scanner workflows):

1. Type the desired quantity (e.g. `3`).
2. Press **X** — the NumPad clears and the status bar shows **x3**.
3. The next sale (PLU button click *or* barcode ENTER) uses that quantity.
4. After the sale the multiplier resets to **x1**.

```
NumPad: 3  → X  → status bar: "x3"
NumPad: 5000157070008  → ENTER
Result: 3× Coca-Cola added
Status bar returns to "x1"
```

#### PLU — Price and Stock Inquiry

```
NumPad: 5000157070008  → PLU
Result: Info dialog — price and warehouse stock totals (no sale)

PLU (empty NumPad)  → NumPad: 5000157070008  → ENTER
Result: Same info dialog (awaiting_plu_inquiry mode)
```

### Mode 4 — Payment Amount from NumPad

Enter a tender amount on the NumPad before pressing **CASH** or **CREDIT CARD**.

The value is interpreted in the currency's **minor unit**. For GBP (`decimal_places = 2`):

```
NumPad: 10000  → CASH
Result: £100.00 cash payment recorded
```

- Applies to **generic** payment buttons (e.g. the plain CASH button).
- **Preset denomination buttons** (e.g. "20 £", "50 £") always use their encoded amount and ignore the NumPad.

---

## Processing a Sale — Step by Step

1. Navigate to **SALES** from the main menu.
2. Add products using one of:
   - Click a **PLU/barcode product button** (optionally prefix with a NumPad quantity).
   - Type a **barcode or product code** on the NumPad and press **ENTER**.
   - Type a quantity, press **X**, then scan or press a PLU button.
3. When all items are added, accept payment:
   - Click a **denomination button** (e.g. "20 £") for an exact amount.
   - Or type a custom amount on the NumPad then press **CASH** or **CREDIT CARD**.
4. If the payment equals or exceeds the total, the receipt is printed and the document is closed automatically. Change is calculated and displayed. The printed receipt includes all product lines, balance due, payment amount, change, and VAT at the bottom.

---

## Sale List — Item Actions

Tapping any row in the sale list opens an **Item Actions** popup:

| Button | Action |
|--------|--------|
| **REPEAT** | Clones the line as a new entry with the next available `line_no`. Totals update immediately. |
| **DELETE** | Soft-cancels the line (`is_cancel = True`). The line stays visible with a strikethrough style; totals are recalculated excluding it. |
| **CANCEL** | Closes the popup with no change. |

### REPEAT Detail

- A new `TransactionProductTemp` (or `TransactionDepartmentTemp`) record is cloned with a new UUID and saved to the database.
- The **Sales Amount** in the amount table increases immediately.
- The repeated row can itself be REPEAT-ed or DELETE-d later.

### DELETE Detail

- The database record is marked `is_cancel = True` immediately.
- **Sales Amount** decreases by the cancelled line's total.
- The row stays visible (strikethrough) for the remainder of the session but will not appear on the next reload of the sale screen.
- **If the last active line is deleted**, the document is automatically cancelled (`is_closed = True`, `transaction_status = CANCELLED`), `document_data` is reset to `None`, and the status bar clears. The next product sale starts a fresh document.

---

## Applying Item Discounts and Markups

![SALE form — FUNC alternate labels (discount ↔ markup, SUB TOTAL ↔ CUSTOMER, etc.)](../static_files/images/sample_sale_func_dual_functions_form.jpg)

Two **dual-function** buttons appear in the top-right corner of the product shortcut grid on the SALE form (they show a small **F** badge). Each has `form_control_function1` / `caption1` for **discount** and `form_control_function2` / `caption2` for **markup**.

| Button | Colour | State 1 (caption / event) | State 2 (caption / event) |
|--------|--------|---------------------------|---------------------------|
| `DISCOUNT_PERCENT_BTN` | Purple | **DISC %** — `DISCOUNT_BY_PERCENT` | **MARK %** — `MARKUP_BY_PERCENT` |
| `DISCOUNT_AMOUNT_BTN` | Deep orange | **DISC AMT** — `DISCOUNT_BY_AMOUNT` | **MARK AMT** — `MARKUP_BY_AMOUNT` |

### Dual-function behaviour

- A tap runs the **currently shown** function only; the caption does **not** flip on that tap.
- The **FUNC** button switches **all** dual-function controls on the SALE form between state 1 and state 2 **without** invoking any handler (labels only).
- After **any** dual-function button on the form is used, **every** dual-function button returns to state 1 (normal captions), and FUNC’s alternate mode is cleared—press **FUNC** again if you still need alternate labels.

### Prerequisites

- At least one active (non-cancelled) **PLU** or **DEPARTMENT** line must exist before discount or markup.
- If no eligible line exists, an error dialog is displayed.

### Discount by Percentage

1. Sell at least one product.
2. Ensure the button shows **DISC %** (use **FUNC** if it currently shows **MARK %**).
3. Press **DISC %**.
4. A modal dialog opens (purple header): allowed range **1 % – 100 %**.
5. Enter the value with the embedded keypad or a physical keyboard; **Enter** or **APPLY** confirms. (The SALE form’s on-screen virtual keyboard does **not** open in this dialog—the built-in number buttons are sufficient for touch.)
6. The original line is cancelled (strikethrough); a new line is added at total × (1 − pct/100); VAT and document totals refresh.

### Discount by Amount

1. Sell at least one product.
2. Ensure the button shows **DISC AMT** (use **FUNC** if needed).
3. Press **DISC AMT**.
4. Dialog (orange header): amount from **smallest currency step** (from `decimal_places`) **up to the line total**.
5. **APPLY** or **Enter**: original line cancelled; new line at (line total − amount); VAT recalculated.

### Markup by Percentage

1. Sell at least one product.
2. Press **FUNC** until **MARK %** is visible (alternate captions on all dual buttons).
3. Press **MARK %**.
4. Dialog (teal header): **1 % – 100 %**; new line total = line total × (1 + pct/100).
5. Original line cancelled; new line with higher total and recalculated VAT.

### Markup by Amount

1. Sell at least one product.
2. Press **FUNC** until **MARK AMT** is visible.
3. Dialog (blue header): amount from **smallest currency step** up to **current line total** (e.g. for a £5.00 line, up to **5.00**).
4. New line total = line total + entered amount; VAT and document totals update.

### Behind the Scenes

- The original `TransactionProductTemp` record is marked `is_cancel = True` and persisted.
- A new `TransactionProductTemp` is cloned with a new UUID:
  - **Discount:** `unit_price` / `total_price` reduced; `unit_discount` and `discount_rate` (for %) filled; `discount_reason` describes the discount.
  - **Markup:** `unit_price` / `total_price` increased; `unit_discount` = 0, `discount_rate` = NULL; `discount_reason` text starts with `Markup` for traceability.
  - `total_vat` from `VatService.calculate_vat()` using the **original** line VAT rate.
- `calculate_document_totals()` updates `total_amount` and `total_vat_amount` on the document head.
- Currency `decimal_places` (from the `Currency` table) sets the minimum step for amount modes.

### Dialog Controls

| Area | Description |
|------|-------------|
| Header | Coloured title (purple / orange = discount % / amount; teal / blue = markup % / amount) |
| Info row | Product name + allowed range |
| Input field | Editable `TextBox`; **no** window virtual keyboard (embedded numpad covers touch entry; physical keyboard still works) |
| Numpad | 3 × 4 grid: 7 8 9 / 4 5 6 / 1 2 3 / . 0 ⌫ (buttons do not steal focus) |
| CLEAR | Erases the current input |
| APPLY / **Enter** | Validates and applies |
| CANCEL | Closes without changes |

---

## SALE Form — Action Buttons (lower area)

| Button | Name | Normal state | Alternate state (FUNC active) |
|--------|------|-------------|-------------------------------|
| **FUNC** | `FUNC` | Switches all dual-function button **labels** to alternate (`caption2`) | Switches labels back to normal (`caption1`) |
| **CHANGE** | `CHANGE` | Records change given to the customer (`CHANGE_PAYMENT`) | — |
| **SUB TOTAL** *(dual)* | `SUBTOTAL` | `SUB TOTAL` → subtotal | `CUSTOMER` → customer list (sale assignment) |
| **SUSPEND** *(dual)* | `PAYMENT_SUSPEND` | `SUSPEND` → `SUSPEND_SALE` | `CANCEL` → `CANCEL_DOCUMENT` |
| **CREDIT CARD** *(dual)* | `PAYMENT_CREDIT` | `CREDIT CARD` → `CREDIT_PAYMENT` | `PAYMENT` → opens **PAYMENT** form (`FormName.PAYMENT`) |
| **DISC %** *(dual)* | `DISCOUNT_PERCENT_BTN` | `DISC %` → `DISCOUNT_BY_PERCENT` | `MARK %` → `MARKUP_BY_PERCENT` |
| **DISC AMT** *(dual)* | `DISCOUNT_AMOUNT_BTN` | `DISC AMT` → `DISCOUNT_BY_AMOUNT` | `MARK AMT` → `MARKUP_BY_AMOUNT` |

![SALE form — CUSTOMER button visible after FUNC](../static_files/images/sample_sale_customer_form.jpg)

- **FUNC** toggles labels on all dual-function buttons between normal (`caption1`) and alternate (`caption2`); it does not run sale handlers. Any dual-button tap runs the visible function and resets **all** dual buttons to normal captions.
- Dual-function sale buttons (**SUSPEND**, **SUB TOTAL** / **CUSTOMER**, **CREDIT CARD** / **PAYMENT**, **DISC %**, **DISC AMT**) carry a small **"F"** badge in the top-right corner.

---

## PAYMENT form

Enum / DB name: **`FormName.PAYMENT`** (default seed `form_no` **20**). Opened from SALE after **FUNC** → **PAYMENT** (dual caption on **CREDIT CARD**) only when there is a payable open receipt (head present, not closed/cancelled/completed, `total_amount` > 0, document not already complete); otherwise a modal error is shown and the form does not open. **BACK** returns to SALE (form history). The same active sale document is used; payments post through the existing `PaymentService` handlers.

![PAYMENT form — totals, payment grid, tender log, NumPad](../static_files/images/sample_sale_payment_form.jpg)

| Area | Description |
|------|-------------|
| **AMOUNTSTABLE** | Live totals (same control family as SALE); row heights stretch to fill the control height without increasing font size |
| **PAYMENTLIST** | Lines already tendered on the document |
| **NUMPAD** | Tender amount in **minor units** for cash/card/etc.; **Enter** is a no-op (`NONE`). For **BONUS** (loyalty), enter **whole points** (not currency). On this screen you **must** enter a value before each payment type — the app does **not** auto-take the full balance in one tap (unlike the SALE form). Split tenders repeat until the **net** balance is zero, then the receipt completes. |
| **BACK** | `BACK` event → previous form (SALE) |
| **CHANGE** | `CHANGE_PAYMENT` — same as SALE form; when over-tendered, records change and can complete the receipt (no MessageForm fallback if this button exists on the form) |
| Payment grid | Buttons for cash, card, cheque, on credit, prepaid, mobile, **bonus** (loyalty **BONUS_PAYMENT**), exchange, current account, bank transfer (see seed data in `data_layer/db_init_data/forms/payment_screen.py` for `EventName` mapping) |

When the ticket is fully paid from this screen, the app completes the sale, prints, and redraws **SALE** with a new empty document (same behaviour as completing on the main sale layout). The stacked **SALE** entry that was added when opening PAYMENT is then popped from ``form_history`` (`prepare_navigation_return_from_payment_form`) so **BACK** leaves the sale screen for the real previous form (e.g. **MAIN_MENU**), not a duplicate SALE.

**Data sync:** `AMOUNTSTABLE` and `PAYMENTLIST` are filled from the same `document_data` as the SALE screen. After each main-window draw of **SALE** or **PAYMENT**, `Interface.draw` schedules `SaleService.update_sale_screen_controls()` (via `_update_sale_screen_controls`) so totals and payment lines match the active temp document when opening PAYMENT, after partial tenders, and when pressing **BACK** to SALE.

> **DB note:** Form **#20** and its controls are inserted only when the database is first initialised (empty `Form` / `FormControl` tables). Existing deployments need a migration or manual form row + controls if they predate this feature.

> See [UI Controls — Dual-Function Buttons](23-ui-controls.md#dual-function-buttons) and [UI Controls — FUNC Button](23-ui-controls.md#func-button--global-function-mode-toggle) for the full mechanism.

---

## Payment Types

| Button naming convention | Behaviour |
|--------------------------|-----------|
| `CASH_PAYMENT` | Cash — pays exact button amount (or NumPad amount) |
| `CASH{amount}` (e.g. `CASH2000`) | Pays the encoded amount ÷ 100 (£20.00 for GBP) |
| `CREDIT_PAYMENT` | Credit card — capped at remaining balance |
| `CHECK_PAYMENT` | Cheque payment |
| `EXCHANGE_PAYMENT` | Foreign currency exchange |
| `PREPAID_PAYMENT` | Prepaid card — capped at remaining balance |
| `CHARGE_SALE_PAYMENT` | House charge / store credit — capped at remaining |
| `OTHER_PAYMENT` | Any other method — capped at remaining |
| `CHANGE_PAYMENT` | Record change given to the customer |
| `BONUS_PAYMENT` | **Loyalty redemption** — applies a **`LOYALTY`** **`TransactionDiscountTemp`** from numpad **points** (`LoyaltyRedemptionService`); not a cash tender. Requires registered customer with membership and available points. |

When **net** amount due (`total_amount − total_discount_amount`) is fully covered by payments (minus any recorded change), the transaction is automatically completed, the receipt is printed (see [Peripherals — Receipt format](30-peripherals.md#receipt-format)), and the cash drawer is opened.

**Loyalty (local):** **Redemption** on **PAYMENT**: **BONUS** → **`LoyaltyRedemptionService`** (discount line + `loyalty_points_redeemed`); ledger **`REDEEMED`** posts on completion — see [Loyalty Programs — Redemption](41-loyalty-programs.md#redemption-at-payment-loyaltyredemptionservice-bonus_payment). **Earning**: for **sale** receipts with a **registered** (non–walk-in) customer and **`CustomerLoyalty`**, **`LoyaltyEarnService.stage_document_earn`** runs inside **`PaymentService.copy_temp_to_permanent`** — see [Earning engine](41-loyalty-programs.md#earning-engine-loyaltyearnservice). Earn may be restricted by **`earn_eligible_payment_types`** in **`LoyaltyProgram.settings_json`**. Earned/redeemed points are reflected on the receipt when discount/payment adapters emit those lines (e.g. **`LOYALTY`** discount with a points-style code).

**Promotional document discounts (when present):** A future or integrated promotion engine may add **`TransactionDiscountTemp`** rows with **`discount_type="CAMPAIGN"`** and **`discount_code`** set to **`Campaign.code`** or a short coupon token (column limit 15). There is no dedicated SALE/PAYMENT button for this yet. **`PaymentService.copy_temp_to_permanent`** resolves the **`CAMPAIGN`** **`transaction_discount_type`** row and copies **`discount_code`** to **`TransactionDiscount`**; the thermal receipt shows **`CAMPAIGN (code)`** — see [Campaign & Promotions](43-campaign-promotions.md).

---

## Amount Table

The amount table at the bottom of the sale screen shows live totals:

| Row | Content |
|-----|---------|
| Sales Amount | Running total of all active (non-cancelled) lines |
| Discount Amount | Total discount applied (includes **`LOYALTY`** lines from point redemption and any **`CAMPAIGN`** promotion lines when present) |
| Payment Amount | Total already paid |
| Change Amount | Change due to the customer |

**Net due** (for payment caps and completion): gross line total **`total_amount`** minus **`total_discount_amount`**, then minus **`total_payment_amount`** — see **`PaymentService`**.

---

[← Back to Table of Contents](README.md) | [Previous: Virtual Keyboard Configuration](06-virtual-keyboard.md) | [Next: Suspend and Resume Sales →](11-suspend-resume.md)
