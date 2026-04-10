# Introduction

SaleFlex.PyPOS is a modern point-of-sale application designed for retail stores, restaurants, and service-oriented businesses. This touch-screen enabled POS system streamlines sales transactions, inventory management, and customer relationship management in a user-friendly interface.

Built with PySide6 (Qt framework) and SQLAlchemy ORM, SaleFlex.PyPOS features:

- **Dynamic Forms System**: Database-driven UI forms that can be customized without code changes
- **Document Management**: Complete transaction lifecycle management with temporary and permanent models
- **Service Layer Architecture**: Centralized business logic services (VatService, SaleService, PaymentService, LoyaltyService)
- **In-Memory Caching**: Optimized performance with reference data and product data caching
- **Auto-Save Functionality**: Automatic database persistence ensuring data integrity
- **Event-Driven Architecture**: Modular event handling with 9 specialized event handler classes
- **100+ Database Models**: Comprehensive data model covering all POS operations (including loyalty policy and customer `phone_normalized`)
- **Cashier Management**: Role-based access control with admin and standard cashier roles
- **Smart NumPad**: Four operating modes — barcode/PLU lookup, inline quantity, quantity multiplier (X), and payment amount
- **Transaction Suspend/Resume**: Park and resume sales (market mode) or table orders (restaurant mode)
- **Closure Operations**: End-of-day closure with aggregated totals, VAT summaries, and cashier reports
- **OPOS-style Peripherals**: Cash drawer, receipt printer, line display, scanner, scale, and customer display stubs ready for driver integration
- **Central Logging**: Configurable logging via `core/logger.py` with file and console output controlled from `settings.toml`
- **Centralized Exception Handling**: Typed `SaleFlexError` hierarchy in `core/exceptions.py` with domain-specific subclasses
- **Country-Specific Compliance**: JSON template system for country/region-specific closure data (Turkey E-Fatura, US state taxes, EU VAT, etc.)
- **Multi-Currency Support**: Currency exchange rate tracking with VAT-aware rounding

## Application Screens

| Screen | Description |
|--------|-------------|
| **LOGIN** | Cashier selection and password entry |
| **MAIN MENU** | Navigation hub to Sales, Closure, Configuration, Cashier Management |
| **SALE** | Point-of-sale transaction screen with NumPad, product list, payment area |
| **PAYMENT** | Dedicated payment form (`FormName.PAYMENT`): **AMOUNTSTABLE** shows live totals with row heights stretched to fill the control (font size unchanged), plus payment-type grid, tender log, NumPad — opened from SALE after **FUNC** → **PAYMENT** (see [Sale Transactions — PAYMENT form](10-sale-transactions.md#payment-form)) |
| **SUSPENDED SALES** | List of parked (pending) transactions for resumption |
| **CLOSURE** | End-of-day closure execution screen |
| **SETTING** | POS system configuration (IP, ports, currency, hardware) |
| **CASHIER** | Cashier account management |

## Default Login Credentials

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin` | Administrator — full access, can manage all cashier accounts |
| `jdoe` | `1234` | Standard cashier — can update own password only |

> **Important:** Change the default administrator password after first login.

This comprehensive guide covers installation, configuration, and advanced features of SaleFlex.PyPOS.

---

[← Back to Table of Contents](README.md) | [Next: System Requirements →](02-system-requirements.md)
