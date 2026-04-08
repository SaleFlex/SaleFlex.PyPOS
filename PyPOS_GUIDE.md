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

**Default credentials:** `admin` / `admin` (administrator) Â· `jdoe` / `1234` (standard cashier)

---

## Key Operations Quick Reference

### Processing a Sale

1. Log in and press **SALES** from the main menu.
2. Add products by:
   - Clicking a **PLU product button**, or
   - Typing a **barcode/product code** on the NumPad and pressing **ENTER**
3. Accept payment by clicking a **denomination button** (e.g. "20 Â£") or entering a custom amount on the NumPad then pressing **CASH** or **CREDIT CARD**.
4. The receipt is printed and the transaction closes automatically when fully paid. The receipt lists every product line, the balance due (with item count), each payment, change (if any), and VAT — all sent line-by-line to `POSPrinter` and written to the application log.

### NumPad Modes (SALE screen)

| Mode | How to trigger | Effect |
|------|---------------|--------|
| **Barcode/PLU lookup** | Type code → press ENTER | Finds and sells the product |
| **Inline quantity** | Type qty → click PLU button | Sells that many units |
| **Quantity multiplier (X)** | Type qty → press **X** → scan/ENTER | Pre-sets quantity for next scan |
| **Payment amount** | Type amount → press CASH/CREDIT CARD | Pays that amount (minor currency units) |
| **PLU inquiry** | Type code → press **PLU** (or press PLU first → ENTER) | Shows price and stock without selling |

### Suspend a Sale (Market Mode)

Press **SUSPEND** on the SALE screen to park the current cart. A new empty draft is created for the next customer. To resume a parked sale, press **SUSPEND** with no open document → select a row → press **ACTIVATE**.

### Cancel a Transaction

Press **CANCEL** on the SALE screen to void the entire active transaction. A confirmation dialog shows the receipt number, closure number, and total. A new draft opens automatically.

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

From `CLOSURE_RECEIPTS`, select a receipt row and press **DETAIL** to open `CLOSURE_RECEIPT_DETAIL` — a key/value view of the receipt header plus every line item.

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

### Inventory Management (Stock)

From the **Product List** screen, press the **STOCK** button (dark-blue, bottom row) to enter the Inventory Management module.

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

**Virtual keyboard:** [Virtual Keyboard Configuration](docs/06-virtual-keyboard.md)

**TextBox Enter key action:** [UI Controls — TextBox ENTER Key](docs/23-ui-controls.md#enter-key--form_control_function1)

**Receipt printing:** [Peripherals — Receipt format](docs/30-peripherals.md#receipt-format)

**Logging:** [Central Logging](docs/31-logging.md)

**Startup guards:** [Startup Entry Point](docs/34-startup-entry-point.md)

**Product management:** [Product Management](docs/15-product-management.md)

**Inventory & stock management:** [Inventory Management](docs/16-inventory-management.md)

**Project architecture:** [Project Structure](docs/20-project-structure.md)

**Event system:** [Event System](docs/24-event-system.md)

**UI controls:** [UI Controls Catalog](docs/23-ui-controls.md)

**GATE & external integrations:** [Integration Layer](docs/40-integration-layer.md)

---

**Last Updated:** 2026-04-08
**Version:** 1.0.0b6
**License:** MIT
