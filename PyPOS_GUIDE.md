# SaleFlex.PyPOS Comprehensive Guide

> **Note:** This guide is a quick-reference companion to the detailed documentation in the [docs/](docs/) directory.

## Quick Start

```bash
git clone https://github.com/SaleFlex/SaleFlex.PyPOS.git
cd SaleFlex.PyPOS
python -m venv venv
venv\Scripts\activate.bat        # Windows
# or: source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
python saleflex.py
```

**Default credentials:** `admin` / `admin` (administrator) · `jdoe` / `1234` (standard cashier)

---

## Key Operations Quick Reference

### Processing a Sale

1. Log in and press **SALES** from the main menu.
2. Add products by:
   - Clicking a **PLU product button**, or
   - Typing a **barcode/product code** on the NumPad and pressing **ENTER**
3. Accept payment by clicking a **denomination button** (e.g. "20 £") or entering a custom amount on the NumPad then pressing **CASH** or **CREDIT CARD**.
4. The receipt is printed and the transaction closes automatically when fully paid. The receipt lists every product line, the balance due (with item count), each payment, change (if any), and VAT — all sent line-by-line to `POSPrinter` and written to the application log.

### NumPad Modes (SALE screen)

| Mode | How to trigger | Effect |
|------|---------------|--------|
| **Barcode/PLU lookup** | Type code → press ENTER | Finds and sells the product |
| **Inline quantity** | Type qty → click PLU button | Sells that many units |
| **Quantity multiplier (X)** | Type qty → press **X** → scan/ENTER | Pre-sets quantity for next scan |
| **Payment amount** | Type amount → press CASH/CREDIT CARD (or a type on the **PAYMENT** screen) | Pays that amount (minor currency units) |
| **Loyalty points (PAYMENT only)** | On **PAYMENT**: type **whole points** → **BONUS** | Adds a **`LOYALTY`** line discount (not cash tender); capped by balance, net due, and redemption policy — see [Loyalty Programs — Redemption](docs/41-loyalty-programs.md#redemption-at-payment-loyaltyredemptionservice-bonus_payment) |
| **PLU inquiry** | Type code → press **PLU** (or press PLU first → ENTER) | Shows price and stock without selling |

![SALE form](static_files/images/sample_sale_form.jpg)

After **FUNC**, dual-function buttons show their alternate labels (e.g. **SUB TOTAL** → **CUSTOMER**, **CREDIT CARD** → **PAYMENT**, discount buttons → markup):

![SALE form — FUNC alternate labels](static_files/images/sample_sale_func_dual_functions_form.jpg)

**Full payment screen:** With alternate labels visible, **PAYMENT** opens `FormName.PAYMENT` — same document as SALE, with **AMOUNTSTABLE**, **PAYMENTLIST**, **NUMPAD**, **BACK**, and one button per payment category (aligned with `PaymentType` in code: cash, card, cheque, on credit, prepaid, mobile, bonus, exchange, current account, bank transfer). **AMOUNTSTABLE** stretches its rows to fill the control height without changing font size. Details: [Sale Transactions — PAYMENT form](docs/10-sale-transactions.md#payment-form).

![PAYMENT form](static_files/images/sample_sale_payment_form.jpg)

### Suspend a Sale (Market Mode)

Press **SUSPEND** on the SALE screen to park the current cart. A new empty draft is created for the next customer. To resume a parked sale, press **SUSPEND** with no open document → select a row → press **ACTIVATE**.

### Cancel a Transaction

Press **CANCEL** on the SALE screen to void the entire active transaction. A confirmation dialog shows the receipt number, closure number, and total. A new draft opens automatically.

### Apply a Discount or Markup to the Last Item

Two **dual-function** buttons (small **F** badge) sit in the top-right corner of the product shortcut grid:

| Button (state 1 → state 2) | Normal action | Alternate action |
|--------------------------|---------------|------------------|
| **DISC %** → **MARK %** (purple) | Percentage **discount** 1–100 % on the last line | Percentage **markup** 1–100 % on the last line |
| **DISC AMT** → **MARK AMT** (deep orange) | Fixed **discount** from minimum currency step up to line total | Fixed **markup** over the same range (adds up to the current line total) |

Press **FUNC** to switch **all** dual-function buttons on the SALE form between their first and second labels **without** running a sale action. Tapping a dual-function button always runs **only** the function that matches the label currently shown; the tap does **not** change that button’s caption. After **any** dual-function button is used, **every** dual-function button on the form resets to its **first** label—press **FUNC** again when you need the second function.

Each dialog has a text field, an embedded numeric keypad (7 8 9 / 4 5 6 / 1 2 3 / . 0 ⌫) for touch entry—the SALE window’s on-screen **virtual keyboard** is **not** used here (redundant with the built-in keys). **CLEAR / APPLY / CANCEL**, and **Enter** (physical keyboard) to apply. On **APPLY**:
- The original product line is cancelled (strikethrough).
- A new line is added with the recalculated price and VAT (lower for discount, higher for markup).
- Document totals update immediately.

See [Sale Transactions — Applying Item Discounts and Markups](docs/10-sale-transactions.md#applying-item-discounts-and-markups) for full details.

### Cancel a Single Line Item

Tap a row in the sale list → choose **DELETE** from the popup. The line is soft-cancelled (strikethrough) and totals are recalculated. If the last active line is deleted, the document is automatically cancelled.

### End-of-Day Closure

From the main menu, press **CLOSURE** (administrators only). The system aggregates all transactions for the current closure period, increments the closure sequence number by 1, and **resets the receipt number back to 1**. The next sale after closure starts at receipt 1 for the new closure period.

- **Z-report printed**: The closure Z-report is sent line-by-line to `POSPrinter` (log-only) immediately after all records are committed. It includes: net/gross sales, cash balance, VAT breakdown, payment method totals, and transaction counts. See [Peripherals — Closure Z-report format](docs/30-peripherals.md#closure-z-report-format).
- **Success**: A green info dialog ("End-of-Day Closure Complete") confirms the closure number that was closed.
- **Failure**: A red error dialog explains the reason (e.g. not logged in, insufficient permissions, no transactions found, configuration error).

### Browsing Closure History

The CLOSURE form also allows browsing previously completed closures. Select a row in the Closure History datagrid and use the bottom-left buttons:

| Button | Opens Form | Shows |
|--------|-----------|-------|
| **DETAIL** | `CLOSURE_DETAIL` | Key/value summary of the selected closure (dates, cashier, document counts, sales totals, cash amounts) |
| **RECEIPTS** | `CLOSURE_RECEIPTS` | List of all receipts (TransactionHead records) within that closure period |

From `CLOSURE_RECEIPTS`, select a receipt row and press **DETAIL** to open `CLOSURE_RECEIPT_DETAIL` — a key/value view of the receipt header (including **Loyalty — points earned** / **redeemed** from `TransactionHead` when present) plus every line item.

All three sub-forms are DB-driven dynamic forms. Each has a **BACK** button (bottom-right) that navigates back through the form history stack:

```
CLOSURE → CLOSURE_DETAIL [BACK → CLOSURE]
CLOSURE → CLOSURE_RECEIPTS → CLOSURE_RECEIPT_DETAIL [BACK → CLOSURE_RECEIPTS]
CLOSURE_RECEIPTS [BACK → CLOSURE]
```

### Product Management

From the **Main Menu**, press **PRODUCTS** to open the Product List form.

| Action | How |
|--------|-----|
| **Search products** | Type name or short name in the search box — press **SEARCH** |
| **View & edit product** | Select a row — press **DETAIL** |
| **Save product changes** | In Product Detail — edit fields — press **SAVE** |
| **Return to product list** | In Product Detail — press **BACK** (bottom-right) |

**Product Detail form** shows four tabs:

| Tab | Content |
|-----|---------|
| **Product Info** | Editable fields: Code, Name, Short Name, Sale Price, Purchase Price, Stock, Min Stock, Max Stock, Description |
| **Barcodes** | Read-only list of assigned barcodes |
| **Attributes** | Read-only list of custom product attributes |
| **Variants** | Read-only list of product variants (colour, size, etc.) |

Press **SAVE** (green, bottom-left) to persist changes to the database. Press **BACK** (blue, bottom-right) to close the dialog without saving.

See [Product Management](docs/15-product-management.md) for full documentation.

---

### Cashier Management

From the **Main Menu**, press **CASHIER MANAGEMENT**. Administrators see all accounts and **ADD NEW CASHIER**; standard cashiers only edit their own password.

![Cashier Management](static_files/images/sample_cashier_form.jpg)

![Add New Cashier](static_files/images/sample_cashier_add_form.jpg)

See [Cashier Management](docs/14-cashier-management.md) for full documentation.

---

### Customer Management

#### From the Main Menu

From the **Main Menu**, press **CUSTOMER** (purple button, bottom row) to open the Customer List form.

![Customer List](static_files/images/sample_customer_list_form.jpg)

| Action | How |
|--------|-----|
| **Search customers** | Type name, phone or e-mail in the search box — press **SEARCH** (phone queries also match normalized digits when applicable) |
| **View & edit customer** | Select a row — press **DETAIL** |
| **Add new customer** | Press **ADD** (green, bottom-left) — fill in the blank form — press **SAVE** |
| **Save customer changes** | In Customer Detail — edit fields — press **SAVE** |
| **Close customer detail** | In Customer Detail — press **BACK** (bottom-right) |
| **Return to Main Menu** | Press **BACK** (blue, bottom-right of the list) |

#### Assigning a Customer to the Active Sale (from SALE Form)

1. On the **SALE** form, press **FUNC** to activate alternate button functions.
2. The **SUB TOTAL** button switches to **CUSTOMER**.
3. Press **CUSTOMER** — the Customer List opens in *sale-assignment context*.
4. Either select an existing customer (DETAIL) or add a new one (ADD → SAVE).
5. Press **BACK** — the selected/added customer is linked to the active sale transaction.

![SALE form — CUSTOMER (after FUNC)](static_files/images/sample_sale_customer_form.jpg)

**Customer Detail form** shows two tabs:

| Tab | Content |
|-----|---------|
| **Customer Info** | Editable fields: First Name, Last Name, Phone, E-mail, Address lines, Post Code, Description |
| **Activity History** | Read-only grid of completed receipts from `TransactionHead` where `fk_customer_id` matches the open customer (newest first; up to 500 rows). Refreshes after SAVE when a new customer is created. |
| **Point movements** | Read-only grid of `LoyaltyPointTransaction` rows for audit (type, points, balance after, linked receipt). |

Press **SAVE** (green) to persist changes or create a new customer. Press **BACK** (blue) to close the dialog without saving.

![Customer Detail](static_files/images/sample_customer_detail_form.jpg)

> **Walk-in Customer:** A special "Walk-in Customer" record is pre-seeded in the database (`is_walkin = True`). All sale transactions that have no customer explicitly assigned are automatically linked to this record. The Walk-in Customer is excluded from the customer list search and cannot be edited.

**Loyalty (local):** Saving a customer updates **`phone_normalized`** (digits-only, unique). Assigning a registered customer to the active sale can create **`CustomerLoyalty`**, set **`loyalty_member_id`** on the open document, apply **welcome** points, and **recompute tier**. On the **PAYMENT** form, **BONUS** (`BONUS_PAYMENT`) applies **point redemption** as a **`LOYALTY`** discount via **`LoyaltyRedemptionService`** (`currency_per_point` + **`LoyaltyRedemptionPolicy`**); completion then debits **`REDEEMED`** in **`LoyaltyPointTransaction`**. When the receipt is fully paid, **`PaymentService.copy_temp_to_permanent`** runs **`LoyaltyEarnService`** (optional **`earn_eligible_payment_types`** in program **`settings_json`**), copies discounts and loyalty rows, then **`LoyaltyService`** posts **`EARNED`** (and already-handled **`REDEEMED`**), updates spending counters, and **refreshes tier**. **Customer Detail → Point movements** lists **`LoyaltyPointTransaction`** for audit; **Closure → receipt detail** shows per-receipt points earned/redeemed. Void/refund point clawback is still a stub. Details: [Loyalty Programs](docs/41-loyalty-programs.md).

**Marketing segments:** **`CustomerSegmentService`** updates **`CustomerSegmentMember`** from each segment’s **`criteria_json`** after **SAVE** on Customer Detail and after each **completed sale** (same payment path as loyalty). This is separate from loyalty **tier**; combine both for campaigns via **`marketing_profile()`**. Details: [Customer Segmentation](docs/42-customer-segmentation.md).

**Campaigns:** Promotional **`Campaign`** rows and related tables exist in the database (seed examples; end dates are about **one year** from insert on new seeds). **Administrators** can open **CAMPAIGNS** from the **Main Menu** or **SETTINGS** to search campaigns, edit the selected row in **CAMPAIGN_DETAIL**, and **SAVE** (which runs **`refresh_active_campaign_cache()`**). Non-administrators do not see those navigation buttons. Details: [Dynamic Forms — Campaign management](docs/22-dynamic-forms-system.md#campaign-management-administrators). On the **SALE** screen, **`sync_campaign_discounts_on_document`** applies eligible promotions as **`TransactionDiscountTemp`** lines (`discount_type` **`CAMPAIGN`**) when you add or change lines, apply line discount/markup, use **DELETE** / **REPEAT**, assign a customer, or apply a **COUPON**; on the **PAYMENT** screen, **`PaymentService.process_payment`** runs the same sync after each tender line so **payment-method** campaigns (`PAYMENT_DISCOUNT`) can apply. Supported local types include **basket**, **time-window**, **product** (with **`CampaignProduct`**), **buy-X-get-Y**, and **payment-method** discounts; **`CampaignRule`** can filter by product, department, **brand**, **barcode pattern**, **category** (sub-group UUID), and (for payment promos) **payment type**. **Stacking** uses **`priority`** (higher first) and **`is_combinable`**; the engine applies discounts in one greedy pass and reduces the remaining merchandise net for later candidates. **`head.total_discount_amount`** is recomputed so the amount table matches. **`CampaignService.evaluate_proposals`** reads definitions from **`ActiveCampaignCache`** when loaded (warm-up at app startup; refreshed after GATE pull / **`SyncWorker`** / **`CampaignSerializer.apply_updates`**; call **`refresh_active_campaign_cache()`** after out-of-band DB edits). It enforces **`CampaignUsageLimits`** and merges **`active_coupon_codes`** with **`Coupon`**-backed codes (**`applied_coupon_ids`**). Disabled when **`gate.manages_campaign`** is true; **COUPON** then shows an informational message only. The **`pos/service/campaign/`** package also defines a **cart snapshot** (`schema_version` 1.0) for **GATE**. **`transaction_discount_type`** includes **`CAMPAIGN`** (startup patch **`ensure_transaction_discount_type_campaign`**). **`PaymentService.copy_temp_to_permanent`** runs **`CampaignAuditService.record_after_completed_sale`** (**`CampaignUsage`**, **`CouponUsage`**, counters). **`CampaignAuditService.distinct_applied_campaign_count(document_data)`** equals the number of distinct campaigns on the receipt (same as **`CampaignUsage`** rows) and should feed **`CashierTransactionMetrics.number_of_promotions_applied`** when you persist per-transaction metrics. Receipts show **`CAMPAIGN (code)`**. Void/refund rollback: **`CampaignAuditService.revoke_entitlements_for_transaction_head`**. **`IntegrationMixin.apply_campaign`** attaches **`campaign_proposals`** for **`document_data`-shaped** previews when GATE and the third-party campaign connector are off. Full reference: [Campaign & Promotions](docs/43-campaign-promotions.md).

See [Customer Management](docs/17-customer-management.md) for full documentation.

---

### Inventory Management (Stock)

From the **Main Menu**, press **WAREHOUSE** to enter the Inventory Management module.

![Warehouse stock list](static_files/images/sample_warehouse_list_form.jpg)

| Action | How |
|---|---|
| **View current stock** | Press STOCK → type product name/code → SEARCH |
| **Breakdown by location** | Select a product → press DETAIL |
| **Receive goods (stock-in)** | Press STOCK → navigate to STOCK IN → search → enter qty → RECEIVE |
| **Adjust stock (stocktake)** | Press STOCK → navigate to ADJUST → search → enter new qty + reason → ADJUST |
| **View movement history** | Press STOCK → navigate to HISTORY → search |

**Negative stock:** If `is_allowed_negative_stock` is `FALSE` for a product and you attempt to sell more than available, the sale is blocked and a red error dialog is displayed.

See [Inventory Management](docs/16-inventory-management.md) for full documentation.

---

## Table of Contents

### Part 1 — Getting Started

1. [Introduction](docs/01-introduction.md)
2. [System Requirements](docs/02-system-requirements.md)
3. [Installation Guide](docs/03-installation.md)
4. [Configuration](docs/04-configuration.md)
5. [First Login](docs/05-first-login.md)
   — [Virtual Keyboard Configuration](docs/06-virtual-keyboard.md)

### Part 2 — Daily Operations

10. [Sale Transactions](docs/10-sale-transactions.md)
11. [Suspend and Resume Sales](docs/11-suspend-resume.md)
12. [Cancellations](docs/12-cancellations.md)
13. [End-of-Day Closure](docs/13-end-of-day-closure.md)
14. [Cashier Management](docs/14-cashier-management.md)
15. [Product Management](docs/15-product-management.md)
16. [Inventory Management](docs/16-inventory-management.md)
17. [Customer Management](docs/17-customer-management.md)
41. [Loyalty Programs](docs/41-loyalty-programs.md)
42. [Customer Segmentation](docs/42-customer-segmentation.md)
43. [Campaign & Promotions](docs/43-campaign-promotions.md)

### Part 3 — Architecture (Developer)

20. [Project Structure](docs/20-project-structure.md)
21. [Database Models Overview](docs/21-database-models.md)
22. [Dynamic Forms System](docs/22-dynamic-forms-system.md)
23. [UI Controls Catalog](docs/23-ui-controls.md)
24. [Event System](docs/24-event-system.md)
25. [Service Layer](docs/25-service-layer.md)
26. [Document Management](docs/26-document-management.md)
27. [Data Caching](docs/27-data-caching.md)

### Part 4 — Operations & Maintenance

30. [Peripherals](docs/30-peripherals.md)
31. [Central Logging](docs/31-logging.md)
32. [Exception Handling](docs/32-exception-handling.md)
33. [Database Initialization](docs/33-database-initialization.md)
34. [Startup Entry Point](docs/34-startup-entry-point.md)
35. [Troubleshooting](docs/35-troubleshooting.md)
36. [Support and Resources](docs/36-support.md)

### Part 5 — Integration

40. [Integration Layer](docs/40-integration-layer.md)

---

## Specific Feature Quick Links

**Sale transactions:** [Sale Transactions](docs/10-sale-transactions.md)

**Suspend / parked sales:** [Suspend and Resume Sales](docs/11-suspend-resume.md)

**Cancel transaction:** [Cancellations — Full Document Cancellation](docs/12-cancellations.md#full-document-cancellation-cancel-button)

**Cancel a single line:** [Cancellations — Line Cancellation](docs/12-cancellations.md#line-cancellation-item-delete)

**Cashier management:** [Cashier Management](docs/14-cashier-management.md)

**Closure operation:** [End-of-Day Closure](docs/13-end-of-day-closure.md)

**Closure history (DETAIL / RECEIPTS):** [Closure History Navigation](docs/13-end-of-day-closure.md#closure-history-navigation-detail-and-receipts)

**SETTINGS (POS + loyalty):** [Configuration](docs/04-configuration.md) — tabbed **SETTING** form; **SAVE** writes all open tabs (`PosSettings`, `LoyaltyProgram`, policies). Existing DBs get tabs via `ensure_setting_form_tabs` on startup.

**Virtual keyboard:** [Virtual Keyboard Configuration](docs/06-virtual-keyboard.md) (item discount/markup dialogs use the embedded numpad only, not the QWERTY keyboard)

**TextBox Enter key action:** [UI Controls — TextBox ENTER Key](docs/23-ui-controls.md#enter-key--form_control_function1)

**Receipt printing:** [Peripherals — Receipt format](docs/30-peripherals.md#receipt-format)

**Logging:** [Central Logging](docs/31-logging.md)

**Startup guards:** [Startup Entry Point](docs/34-startup-entry-point.md)

**Product management:** [Product Management](docs/15-product-management.md)

**Customer management:** [Customer Management](docs/17-customer-management.md) (includes **Point movements** loyalty audit tab)

**Assign customer to sale (FUNC → CUSTOMER button):** [Customer Management — Sale-Assignment Workflow](docs/17-customer-management.md#sale-assignment-workflow)

**Loyalty (phone ID, earn/redeem, tier, point audit UI):** [Loyalty Programs](docs/41-loyalty-programs.md)

**Customer segments (auto rules):** [Customer Segmentation](docs/42-customer-segmentation.md)

**Campaigns** (snapshot, `ActiveCampaignCache`, SALE + PAYMENT sync, buy-X-get-Y, payment-method promos, stacking, limits, `CampaignUsage` audit, `distinct_applied_campaign_count` for metrics alignment, coupons, `apply_campaign`, **admin CAMPAIGNS** UI): [Campaign & Promotions](docs/43-campaign-promotions.md) · [Dynamic Forms — Campaign management](docs/22-dynamic-forms-system.md#campaign-management-administrators)

**Inventory & stock management:** [Inventory Management](docs/16-inventory-management.md)

**Project architecture:** [Project Structure](docs/20-project-structure.md)

**Event system:** [Event System](docs/24-event-system.md)

**UI controls:** [UI Controls Catalog](docs/23-ui-controls.md)

**GATE & external integrations:** [Integration Layer](docs/40-integration-layer.md)

---

**Last Updated:** 2026-04-11
**Version:** 1.0.0b7
**License:** MIT
