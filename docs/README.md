# SaleFlex.PyPOS Documentation

Welcome to the SaleFlex.PyPOS documentation. This directory contains the complete user and developer guide for the SaleFlex.PyPOS point-of-sale application.

## Table of Contents

1. [Introduction](01-introduction.md) — Overview, key features, default credentials
2. [System Requirements](02-system-requirements.md) — Hardware, software, and database requirements
3. [Installation Guide](03-installation.md) — Step-by-step setup instructions
4. [First Login](04-first-login.md) — Default credentials, role differences, and post-login flow
5. [Basic Navigation](05-basic-navigation.md) — Main menu, NumPad modes, sale processing, SUSPEND/CANCEL/REPEAT/DELETE, cashier management
6. [Dynamic Forms System](06-dynamic-forms.md) — Database-driven UI forms, Panel controls, CheckBox, form transitions, generic save pattern
7. [Virtual Keyboard Configuration](07-virtual-keyboard.md) — Database-driven keyboard themes, enable/disable, custom themes
8. [Data Caching Strategy](08-data-caching.md) — `pos_data` and `product_data` caches, closure management, auto-save system
9. [Document Management System](09-document-management.md) — Transaction lifecycle, suspend/resume, line cancellation, full document cancellation, payment flow
10. [Database Models Overview](10-database-models.md) — 98+ models, country-specific closure templates, model features
11. [Database Initialization Functions](11-database-initialization.md) — Seed data, initialization order, function details
12. [Troubleshooting](12-troubleshooting.md) — Common issues, database problems, closure issues, sale issues
13. [Support and Resources](13-support.md) — GitHub, issue tracker, donations, legal
14. [Service Layer Architecture](14-service-layer.md) — VatService, SaleService, PaymentService, REPEAT/DELETE handlers
15. [Closure Operation (End-of-Day)](15-closure-operation.md) — Authorization, aggregation flow, sequence management
16. [Central Logging](16-logging.md) — `core/logger.py` configuration, log format, usage
17. [Centralized Exception Handling](17-exception-handling.md) — `SaleFlexError` hierarchy, usage patterns, design guidelines
18. [Peripherals (OPOS-style devices)](18-peripherals.md) — Cash drawer, receipt printer, line display, stubs
19. [Startup Entry Point](19-startup-entry-point.md) — Working-directory fix, Python version guard, single-instance lock, global exception handler
20. [Product Management](20-product-management.md) — TabControl widget, FormControlTab model, Product List form (search), Product Detail dialog (DB-driven, 4-tab view), UUID handling, VirtualKeyboard hide fix

---

## Quick Links

| Topic | Document |
|-------|----------|
| Getting started | [Installation Guide](03-installation.md) |
| First time use | [First Login](04-first-login.md) |
| Processing sales | [Basic Navigation](05-basic-navigation.md) |
| End-of-day | [Closure Operation](15-closure-operation.md) |
| Cashier accounts | [Basic Navigation — Cashier Management](05-basic-navigation.md#cashier-management) |
| UI customization | [Dynamic Forms System](06-dynamic-forms.md) |
| Database schema | [Database Models Overview](10-database-models.md) |
| Logging setup | [Central Logging](16-logging.md) |
| Error handling | [Centralized Exception Handling](17-exception-handling.md) |
| Hardware devices | [Peripherals](18-peripherals.md) |
| Startup guards | [Startup Entry Point](19-startup-entry-point.md) |
| Common errors | [Troubleshooting](12-troubleshooting.md) |
| Product management | [Product Management](20-product-management.md) |

---

**Last Updated:** 2026-04-05  
**Version:** 1.0.0b6  
**License:** MIT
