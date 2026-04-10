# SaleFlex.PyPOS Documentation

Complete user and developer guide for the SaleFlex.PyPOS point-of-sale application.

---

## UI screenshots

Touch UI reference images live under [`static_files/images/`](../static_files/images/) in the project root (same paths as the root [`README.md`](../README.md) **First Login** tour). Filenames include:

`sample_login.jpg`, `sample_main_menu.jpg`, `sample_sale_form.jpg`, `sample_sale_func_dual_functions_form.jpg`, `sample_sale_payment_form.jpg`, `sample_sale_customer_form.jpg`, `sample_closure_form.jpg`, `sample_closure_detail_form.jpg`, `sample_closure_receipts_form.jpg`, `sample_closure_receipt_details_form.jpg`, `sample_settings_form.jpg`, `sample_cashier_form.jpg`, `sample_cashier_add_form.jpg`, `sample_product_form.jpg`, `sample_product_detail_form.jpg`, `sample_customer_list_form.jpg`, `sample_customer_detail_form.jpg`, `sample_warehouse_list_form.jpg`, `sample_warehouse_stock_in_form.jpg`, `sample_warehouse_adjustment_form.jpg`, `sample_warehouse_history_form.jpg`.

In Markdown under `docs/`, reference them as `../static_files/images/<filename>`.

---

## Part 1 — Getting Started

| # | Document | Summary |
|---|----------|---------|
| 1 | [Introduction](01-introduction.md) | Overview, key features, application screens, default credentials |
| 2 | [System Requirements](02-system-requirements.md) | Hardware, software, and supported database backends |
| 3 | [Installation Guide](03-installation.md) | Step-by-step setup (Python, venv, pip, first run) |
| 4 | [Configuration](04-configuration.md) | `settings.toml` reference + POS Settings (database) |
| 5 | [First Login](05-first-login.md) | Default credentials, role differences, automatic document recovery |
| 6 | [Virtual Keyboard Configuration](06-virtual-keyboard.md) | DB-driven keyboard themes, enable/disable, custom themes |

---

## Part 2 — Daily Operations

| # | Document | Summary |
|---|----------|---------|
| 10 | [Sale Transactions](10-sale-transactions.md) | NumPad modes, adding products, payments, Item Actions (REPEAT / DELETE) |
| 11 | [Suspend and Resume Sales](11-suspend-resume.md) | SUSPEND button, parked carts, market mode, Suspended Sales list |
| 12 | [Cancellations](12-cancellations.md) | Line cancellation (DELETE), full document cancellation (CANCEL) |
| 13 | [End-of-Day Closure](13-end-of-day-closure.md) | Authorization, aggregation flow, sequence management |
| 14 | [Cashier Management](14-cashier-management.md) | Create/edit cashiers, role permissions, ADD NEW CASHIER |
| 15 | [Product Management](15-product-management.md) | Product List search, Product Detail tabbed dialog |
| 16 | [Inventory Management](16-inventory-management.md) | Stock levels, goods receipt, adjustments, movement history, negative stock policy |
| 17 | [Customer Management](17-customer-management.md) | Customer List search, ADD new customer, Customer Detail tabbed dialog, Walk-in Customer, activity history (`TransactionHead` / `fk_customer_id`), SALE form CUSTOMER dual button, sale-assignment workflow |

---

## Part 3 — Architecture (Developer)

| # | Document | Summary |
|---|----------|---------|
| 20 | [Project Structure](20-project-structure.md) | Folder layout, class inheritance chain, startup sequence, design patterns |
| 21 | [Database Models Overview](21-database-models.md) | 98+ models organized by domain, temp/permanent split, country-specific templates |
| 22 | [Dynamic Forms System](22-dynamic-forms-system.md) | DB-driven UI forms, Panel controls, CheckBox, form transitions, generic save pattern |
| 23 | [UI Controls Catalog](23-ui-controls.md) | All custom Qt widgets: Button, TextBox, NumPad, SaleList, TabControl, ... |
| 24 | [Event System](24-event-system.md) | EventHandler, `event_distributor()`, all event categories with handler mapping |
| 25 | [Service Layer](25-service-layer.md) | VatService, SaleService, PaymentService, REPEAT/DELETE handlers |
| 26 | [Document Management](26-document-management.md) | Transaction lifecycle, suspend/resume, line cancellation, payment flow |
| 27 | [Data Caching](27-data-caching.md) | `pos_data` / `product_data` caches, AutoSave system, closure management |

---

## Part 4 — Operations & Maintenance

| # | Document | Summary |
|---|----------|---------|
| 30 | [Peripherals](30-peripherals.md) | Cash drawer, receipt printer, line display, scanner, scale — OPOS-style stubs |
| 31 | [Central Logging](31-logging.md) | `core/logger.py` configuration, log format, usage patterns |
| 32 | [Exception Handling](32-exception-handling.md) | `SaleFlexError` hierarchy, usage patterns, design guidelines |
| 33 | [Database Initialization](33-database-initialization.md) | Seed data functions, initialization order, adding new seed data |
| 34 | [Startup Entry Point](34-startup-entry-point.md) | Working-directory fix, Python version guard, single-instance lock, global exception handler |
| 35 | [Troubleshooting](35-troubleshooting.md) | Common issues, database problems, closure issues, sale issues |
| 36 | [Support and Resources](36-support.md) | GitHub, issue tracker, donations, license |

---

## Part 5 — Integration

| # | Document | Summary |
|---|----------|---------|
| 40 | [Integration Layer](40-integration-layer.md) | SaleFlex.GATE hub, third-party ERP/payment/campaign connectors, offline outbox, SyncWorker, notification system |

---

## Quick Reference

| Topic | Document |
|-------|----------|
| First time setup | [Installation Guide](03-installation.md) -> [Configuration](04-configuration.md) -> [First Login](05-first-login.md) |
| Processing a sale | [Sale Transactions](10-sale-transactions.md) |
| Applying item discounts or markups (%, amount) | [Sale Transactions → Item Discounts and Markups](10-sale-transactions.md#applying-item-discounts-and-markups) |
| End-of-day | [End-of-Day Closure](13-end-of-day-closure.md) |
| Cashier accounts | [Cashier Management](14-cashier-management.md) |
| Stock management | [Inventory Management](16-inventory-management.md) |
| Customer management / sale assignment | [Customer Management](17-customer-management.md) |
| UI customization | [Dynamic Forms System](22-dynamic-forms-system.md) |
| Database schema | [Database Models Overview](21-database-models.md) |
| Event wiring | [Event System](24-event-system.md) |
| Logging setup | [Central Logging](31-logging.md) |
| Error handling | [Exception Handling](32-exception-handling.md) |
| Hardware devices | [Peripherals](30-peripherals.md) |
| Startup guards | [Startup Entry Point](34-startup-entry-point.md) |
| Common errors | [Troubleshooting](35-troubleshooting.md) |
| GATE & external systems | [Integration Layer](40-integration-layer.md) |

---

**Last Updated:** 2026-04-09
**Version:** 1.0.0b7
**License:** MIT
