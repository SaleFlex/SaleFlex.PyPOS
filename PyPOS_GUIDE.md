# SaleFlex.PyPOS Comprehensive Guide

> **Note:** This guide provides a quick overview and links to detailed documentation in the [docs/](docs/) directory.

## Quick Links

- [Complete Documentation](docs/README.md) - Full guide organized by topic
- [Installation Guide](docs/03-installation.md) - Setup instructions
- [User Guide](docs/05-basic-navigation.md) - Basic navigation and usage
- [Developer Guide](docs/06-dynamic-forms.md) - Advanced features for developers

---

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

1. Log in and select **SALES** from the main menu
2. Add products by:
   - Clicking a **PLU product button**, or
   - Typing a **barcode/product code** on the NumPad and pressing **ENTER**
3. Accept payment by clicking a **denomination button** (e.g. "20 £") or entering a custom amount on the NumPad then pressing **CASH** or **CREDIT CARD**
4. The receipt is printed and the transaction closes automatically when fully paid

### Suspend a Sale (Market Mode)

Press **SUSPEND** on the SALE screen to park the current cart. A new empty draft is created for the next customer. To resume a parked sale, press **SUSPEND** again with no open document to open the **Suspended Sales** list, then press **ACTIVATE**.

### Cancel a Transaction

Press the red **CANCEL** button on the SALE screen to void the entire active transaction. A confirmation dialog shows the receipt number, closure number, and total. A new draft opens automatically after cancellation.

### Cancel a Single Line Item

Tap a row in the sale list → choose **DELETE** from the popup. The line is soft-cancelled (strikethrough) and totals are recalculated. If the last active line is deleted, the document is automatically cancelled.

### End-of-Day Closure

From the main menu, press **CLOSURE** (administrators only). The system aggregates all transactions for the current closure period, creates a `Closure` record with VAT, payment, and cashier summaries, and increments the closure sequence number.

---

## NumPad Modes (SALE screen)

| Mode | How to trigger | Effect |
|------|---------------|--------|
| **Barcode/PLU lookup** | Type code → press ENTER | Finds and sells the product |
| **Inline quantity** | Type qty → click PLU button | Sells that many units |
| **Quantity multiplier (X)** | Type qty → press **X** → scan/ENTER | Pre-sets quantity for next scan |
| **Payment amount** | Type amount → press CASH/CREDIT CARD | Pays that amount (minor currency units) |
| **PLU inquiry** | Type code → press **PLU** (or press PLU first → ENTER) | Shows price and stock without selling |

---

## Specific Feature Guides

**Suspend / parked sales (market):** On the **SALE** screen, **SUSPEND** holds the current cart in the database (`is_pending`) and clears the register; with no open sale it opens the **Suspended Sales (Market)** list. See [Basic Navigation — SUSPEND](docs/05-basic-navigation.md) and [Document Management](docs/09-document-management.md).

**Cancel transaction (CANCEL button):** On the **SALE** screen, the red **CANCEL** button immediately voids the entire active transaction — sets `is_cancel=True`, `cancel_reason="Canceled by cashier: {username}"`, copies to permanent models, and opens a confirmation dialog. If no open document exists an info dialog is shown. See [Basic Navigation — CANCEL](docs/05-basic-navigation.md) and [Document Management — Full Document Cancellation](docs/09-document-management.md).

**Cashier Management:** Administrators can create and edit all cashier accounts. Standard cashiers can only update their own password. See [Basic Navigation — Cashier Management](docs/05-basic-navigation.md) and [Dynamic Forms — Add New Cashier](docs/06-dynamic-forms.md).

**Closure operation:** Only administrators can perform end-of-day closure. See [Closure Operation](docs/15-closure-operation.md) for the full aggregation and sequencing process.

**Virtual keyboard:** The on-screen keyboard is database-driven and supports multiple themes (default light, dark, compact). See [Virtual Keyboard Configuration](docs/07-virtual-keyboard.md).

**Logging:** Configure log level, console, and file output in the `[logging]` section of `settings.toml`. See [Central Logging](docs/16-logging.md).

---

## Table of Contents

1. [Introduction](docs/01-introduction.md)
2. [System Requirements](docs/02-system-requirements.md)
3. [Installation Guide](docs/03-installation.md)
4. [First Login](docs/04-first-login.md)
5. [Basic Navigation](docs/05-basic-navigation.md)
6. [Dynamic Forms System](docs/06-dynamic-forms.md)
7. [Virtual Keyboard Configuration](docs/07-virtual-keyboard.md)
8. [Data Caching Strategy](docs/08-data-caching.md)
9. [Document Management System](docs/09-document-management.md)
10. [Database Models Overview](docs/10-database-models.md)
11. [Database Initialization Functions](docs/11-database-initialization.md)
12. [Troubleshooting](docs/12-troubleshooting.md)
13. [Support and Resources](docs/13-support.md)
14. [Service Layer Architecture](docs/14-service-layer.md)
15. [Closure Operation (End-of-Day)](docs/15-closure-operation.md)
16. [Central Logging](docs/16-logging.md)
17. [Centralized Exception Handling](docs/17-exception-handling.md)
18. [Peripherals (OPOS-style devices)](docs/18-peripherals.md)

---

**Last Updated:** 2026-04-05  
**Version:** 1.0.0b5  
**License:** MIT
