# SaleFlex.PyPOS

> **Current Status:** Beta v1.0.0b6 - Active Development
> Core POS functionality operational. See [roadmap](#development-roadmap) for upcoming features.

[Watch Demo](https://youtu.be/HoA2p6M8fuM) | [Documentation](docs/README.md) | [Quick Start](#quick-start)

![Python 3.13](https://img.shields.io/badge/python-%3E=_3.13-success.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.11.0-blue.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.48-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0b6-orange.svg)

### Touch Screen Point-of-Sale Application

SaleFlex.PyPOS is a modern, Python-based point-of-sale (POS) system designed for retail businesses, restaurants, and service-oriented establishments. Built with PySide6 (Qt framework), it offers a touch-optimized interface with cross-platform compatibility and robust database support.

[Current Version Demo: 1.0.0b3](https://youtu.be/HoA2p6M8fuM)

## Key Features

SaleFlex.PyPOS POS system is designed to streamline the sales process and improve efficiency with these capabilities:

- **Multi-Payment Processing**: Accept cash, credit cards, debit cards, and mobile payments
- **Receipt & Invoice Generation**: Automated transaction documentation with ESC/P printer support
- **Inventory Management**: Real-time stock tracking with low-stock alerts
- **Customer Management**: Store customer information, preferences, and purchase history
- **Analytics & Reporting**: Comprehensive sales, inventory, and customer behavior analytics
- **System Integration**: Connect with accounting software, warehouse management, and ERP systems
- **Returns & Exchanges**: Handle product returns and exchanges efficiently
- **Employee Management**: Track employee time, attendance, and performance
- **Cashier Management**: Role-based cashier account management with dynamic combobox selection. Admin users can view and edit all cashier accounts and create new cashier accounts directly from the Cashier Management form via the **ADD NEW CASHIER** button (admin-only, hidden for non-admin users). Non-admin cashiers can update only their own password. Field-level read-only protection enforced at the form layer (`is_administrator` flag). New cashier entry uses in-place form manipulation (no full redraw) for seamless UX
- **Campaign & Promotion Management**: Flexible promotional campaigns with time-based, product-specific, and basket discounts
- **Loyalty Programs**: Tiered membership rewards system with points earning, redemption, and customer segmentation
- **Country-Specific Closure Templates**: Flexible template system for country-specific closure data (E-Fatura for Turkey, state tax for USA, VAT reporting for EU, etc.) stored as JSON templates in `static_files/closures/` directory
- **Region Support**: `CountryRegion` model tracks sub-country regions (states, provinces, special economic zones) with ISO 3166-2 compliant fields. Includes 80+ pre-populated regions for region-specific closure templates and compliance
- **Active Closure Management**: Session-based closure tracking system that automatically loads open closures at startup and manages closure lifecycle (open → active → closed). Closure data is maintained in memory during operations and saved to database when closed
- **Document Management System**: Complete transaction lifecycle management with temporary models during processing and automatic conversion to permanent models upon completion. Automatically updates document data during sales operations (PLU and department sales). Supports per-line REPEAT (clone line, save new DB record, update totals) and DELETE (soft-cancel line, mark `is_cancel=True` in DB, recalculate totals) actions from the sale list item popup; if the last active line is deleted the document is automatically cancelled and reset. **CANCEL button:** Red **CANCEL** button on the SALE form (below the denomination buttons, same row as PLU/X/SUSPEND) immediately voids the entire active transaction — sets `transaction_status=CANCELLED`, `is_cancel=True`, `cancel_reason="Canceled by cashier: {username}"`, copies to permanent models, shows a confirmation dialog with receipt/closure number and total, then opens a new draft. If no open document exists, an info dialog is shown instead. **Market suspend:** **SUSPEND** saves the cart as pending, then creates a **new draft** (suspended rows no longer steal the receipt slot in `create_empty_document`). **SUSPENDED_SALES_MARKET** lists suspended receipts (hidden head id + columns); **ACTIVATE** (`RESUME_SALE`) clears `is_pending`, loads lines on **SALE**, and abandons any empty draft left open first. **Closure:** `TransactionHead` rows with `is_pending=True` and open `TransactionHeadTemp` suspended carts for the closure period are **excluded** from aggregated sales totals; their count is stored on `Closure.suspended_transaction_count`. Automatic recovery of incomplete **non-pending** transactions at startup; restores sale UI when re-entering **SALE** with an ACTIVE document
- **Auto-Save Functionality**: Automatic database persistence system using descriptor pattern and wrapper classes. Model instances and dictionaries are automatically saved to the database when attributes are modified, ensuring data integrity and reducing manual save operations. Supports nested model wrapping and skip flags for batch operations
- **Peripherals (OPOS-style)**: `pos/peripherals/` defines cash drawer, receipt printer, line display, scanner, scale, customer display, and remote order display classes. Wired behaviours on **SALE** (log-only until drivers exist): completed sale → receipt text + drawer open; CASH with no document → drawer open; selling and payment steps → three-line customer display updates. See [docs/18-peripherals.md](docs/18-peripherals.md)
- **Startup Guards**: `saleflex.py` entry point runs four pre-flight checks before any module is imported: (1) working-directory normalisation so relative paths always resolve correctly; (2) Python ≥ 3.13 version guard with a clear error message; (3) file-based single-instance lock (`msvcrt.locking` on Windows, `fcntl.flock` on Linux/macOS) that is automatically released on process exit; (4) global exception handler that logs unhandled errors at `CRITICAL` level before terminating. See [docs/19-startup-entry-point.md](docs/19-startup-entry-point.md)
- **Central Logging**: Configurable logging via `core/logger.py` with a single `saleflex` root logger. Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL), console output, and file output are controlled from the `[logging]` section in `settings.toml`. All modules use `get_logger(__name__)` for consistent, hierarchical log records
- **Centralized Exception Handling**: Typed exception hierarchy rooted at `SaleFlexError` (`core/exceptions.py`). Domain-specific subclasses (`PaymentError`, `FiscalDeviceError`, `GATEConnectionError`, `TaxCalculationError`, `DatabaseError`, etc.) replace bare `Exception` raises throughout the codebase. All exceptions are chained with `raise ... from e` to preserve the full traceback
- **Product Management**: Dedicated **Product List** form (form_no=8) accessible from the Main Menu. Supports real-time search by product name or short name with instant DataGrid results. Selecting a row and pressing **DETAIL** opens the **Product Detail** modal dialog (form_no=9, fully DB-driven via `DynamicDialog`) — a tabbed view built with the new `TabControl` widget and `FormControlTab` model, showing Product Info, Barcodes, Attributes, and Variants in four separate read-only tabs. See [docs/20-product-management.md](docs/20-product-management.md)
- **Optimized Performance**: In-memory caching of reference data (`pos_data`) and product data (`product_data`) minimizes disk I/O, extending disk life for POS devices with limited write cycles. All product lookups, currency calculations, VAT rate lookups, button rendering, and sale operations use cached data instead of database queries
- **Smart NumPad (4 Modes)**: The SALE form NumPad supports four operating modes: (1) **Barcode/PLU lookup** — type a barcode or product code and press ENTER to find and sell the product (searches `ProductBarcode` then `Product.code`); (2) **Inline quantity** — type a quantity then press a PLU product button to sell that many units; (3) **X (Quantity Multiplier) button** — pre-set the quantity before a barcode scan; status bar shows the active multiplier (`x1`, `x3`, etc.); (4) **Payment amount** — enter the tendered amount in minor currency units (e.g. 10000 → Â£100.00) then press CASH or CREDIT CARD. **PLU inquiry** (separate green **PLU** button beside **X**) shows price and per-warehouse stock from cached `WarehouseProductStock` without selling — either enter the code then **PLU**, or press **PLU** first then enter the code and **ENTER**

## Architecture Overview

SaleFlex.PyPOS follows a layered architecture pattern with clear separation of concerns:

- **Entry Point** (`saleflex.py`): Pre-flight startup guards — working-directory normalisation, Python version check, single-instance lock, and global exception handler
- **Application Layer** (`pos/manager/application.py`): Main application class implementing Singleton pattern, combining CurrentStatus, CurrentData, and EventHandler
- **Business Logic Layer** (`pos/service/`): Service classes (VatService, SaleService, PaymentService) for centralized business operations
- **Peripherals Layer** (`pos/peripherals/`): OPOS-style device abstractions (cash drawer, receipt printer, line display, scanner, scale, customer display, remote order display). Current implementation is **log-only** (no device probing); see [docs/18-peripherals.md](docs/18-peripherals.md)
- **Event Handling Layer** (`pos/manager/event/`): 10 specialized event handler classes for modular event processing (General, Sale, Payment, Closure, Config, Service, Report, Hardware, Warehouse, **Product**). Event handler methods use `_event` suffix naming convention (e.g., `_sales_form_event`, `_closure_event`, `_product_detail_event`) to distinguish them from properties
- **Data Access Layer** (`data_layer/model/`): 98+ SQLAlchemy models with CRUD operations and auto-save functionality
- **UI Layer** (`user_interface/`): PySide6-based UI components with dynamic form rendering
- **Caching Layer** (`pos/manager/cache_manager.py`): In-memory caching for reference and product data
- **Logging Layer** (`core/logger.py`): Central logging module; all components use `get_logger(__name__)` with configuration from `settings.toml` `[logging]`
- **Exception Layer** (`core/exceptions.py`): Typed exception hierarchy (`SaleFlexError` root) with domain subclasses for payment, hardware, tax, database, document, configuration, and authentication errors

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚            UI Layer (PySide6)                   â”‚
â”‚  Dynamic Forms Â· Virtual Keyboard Â· Controls    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚      Event Handlers (10 specialized modules)    â”‚
â”‚  General Â· Sale Â· Payment Â· Closure Â· Config    â”‚
â”‚  Service Â· Report Â· Hardware Â· Warehouse        â”‚
â”‚  Product                                        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚          Business Logic (Service Layer)         â”‚
â”‚      VatService Â· SaleService Â· PaymentService  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚         OPOS Peripherals (log-only stubs)       â”‚
â”‚   CashDrawer Â· POSPrinter Â· LineDisplay         â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚          Data Access Layer (ORM)                â”‚
â”‚        98+ SQLAlchemy Models Â· CRUD             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚       Cache Layer (pos_data / product_data)     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚            Database (SQLite / PostgreSQL)        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
         ↕ core/logger.py (all layers)
         ↕ core/exceptions.py (all layers)
```

## Project Structure

```
SaleFlex.PyPOS/
â”œâ”€â”€ saleflex.py              # Main application entry point (startup guards, version check, single-instance lock)
â”œâ”€â”€ requirements.txt         # Python dependencies
â”œâ”€â”€ settings.toml           # Application configuration
â”œâ”€â”€ db.sqlite3              # Default SQLite database
â”œâ”€â”€ .saleflex.lock          # Runtime single-instance process lock (auto-created/deleted; not committed)
â”œâ”€â”€ PyPOS_GUIDE.md          # Quick reference guide (redirects to docs/)
â”‚
â”œâ”€â”€ docs/                   # Comprehensive documentation
â”‚   â”œâ”€â”€ README.md           # Documentation index
â”‚   â””â”€â”€ *.md                # Topic-specific documentation files
â”‚
â”œâ”€â”€ data_layer/             # Database & ORM Layer
â”‚   â”œâ”€â”€ engine.py           # Database engine configuration
â”‚   â”œâ”€â”€ db_initializer.py   # Database initialization
â”‚   â”œâ”€â”€ db_manager.py       # Database management utilities
â”‚   â”œâ”€â”€ db_utils.py         # Database helper functions
â”‚   â”‚
â”‚   â”œâ”€â”€ auto_save/          # Auto-save functionality
â”‚   â”‚   â”œâ”€â”€ auto_save_model.py
â”‚   â”‚   â”œâ”€â”€ auto_save_dict.py
â”‚   â”‚   â””â”€â”€ auto_save_descriptor.py
â”‚   â”‚
â”‚   â”œâ”€â”€ db_init_data/       # Initial data seeding
â”‚   â”‚   â”œâ”€â”€ cashier.py
â”‚   â”‚   â”œâ”€â”€ country.py
â”‚   â”‚   â”œâ”€â”€ currency.py
â”‚   â”‚   â”œâ”€â”€ product.py
â”‚   â”‚   â””â”€â”€ ...             # Other initialization modules
â”‚   â”‚
â”‚   â”œâ”€â”€ enums/              # Enumeration definitions
â”‚   â”‚   â”œâ”€â”€ control_name.py
â”‚   â”‚   â”œâ”€â”€ control_type.py
â”‚   â”‚   â”œâ”€â”€ custom_control_type_name.py
â”‚   â”‚   â”œâ”€â”€ event_name.py
â”‚   â”‚   â””â”€â”€ form_name.py
â”‚   â”‚
â”‚   â””â”€â”€ model/              # Data models and CRUD operations
â”‚       â”œâ”€â”€ crud_model.py   # Base CRUD operations
â”‚       â”œâ”€â”€ mixins.py       # Model mixins
â”‚       â””â”€â”€ definition/     # Entity definitions (98+ models)
â”‚
â”œâ”€â”€ user_interface/         # UI Components
â”‚   â”œâ”€â”€ window/             # Application windows and dialogs
â”‚   â”‚   â”œâ”€â”€ base_window.py
â”‚   â”‚   â””â”€â”€ dynamic_dialog.py
â”‚   â”‚
â”‚   â”œâ”€â”€ control/            # Custom UI controls
â”‚   â”‚   â”œâ”€â”€ button.py
â”‚   â”‚   â”œâ”€â”€ textbox.py
â”‚   â”‚   â”œâ”€â”€ checkbox.py
â”‚   â”‚   â”œâ”€â”€ combobox.py
â”‚   â”‚   â”œâ”€â”€ label.py
â”‚   â”‚   â”œâ”€â”€ datagrid.py
â”‚   â”‚   â”œâ”€â”€ panel.py        # Panel control with scrollbar support
â”‚   â”‚   â”œâ”€â”€ toolbar.py
â”‚   â”‚   â”œâ”€â”€ statusbar.py
â”‚   â”‚   â”œâ”€â”€ amount_table/   # Amount table control
â”‚   â”‚   â”œâ”€â”€ numpad/         # Numeric pad control
â”‚   â”‚   â”œâ”€â”€ payment_list/   # Payment list control
â”‚   â”‚   â”œâ”€â”€ sale_list/      # Sale list control
â”‚   â”‚   â”œâ”€â”€ tab_control/    # Tab control (QTabWidget, DB-driven pages via FormControlTab)
â”‚   â”‚   â”œâ”€â”€ transaction_status/  # Transaction status display
â”‚   â”‚   â””â”€â”€ virtual_keyboard/    # Virtual keyboard component
â”‚   â”‚
â”‚   â”œâ”€â”€ form/               # Form definitions
â”‚   â”‚   â”œâ”€â”€ about_form.py
â”‚   â”‚   â””â”€â”€ message_form.py
â”‚   â”‚
â”‚   â”œâ”€â”€ render/             # Dynamic form rendering (database-driven)
â”‚   â”‚   â””â”€â”€ dynamic_renderer.py
â”‚   â”‚
â”‚   â””â”€â”€ manager/            # UI management logic
â”‚       â””â”€â”€ interface.py
â”‚
â”œâ”€â”€ pos/                    # Core POS Business Logic
â”‚   â”œâ”€â”€ data/               # POS-specific data types
â”‚   â”‚   â”œâ”€â”€ document_type.py
â”‚   â”‚   â”œâ”€â”€ document_state.py
â”‚   â”‚   â”œâ”€â”€ payment_type.py
â”‚   â”‚   â””â”€â”€ discount_type.py
â”‚   â”‚
â”‚   â”œâ”€â”€ hardware/           # Hardware integration
â”‚   â”‚   â””â”€â”€ device_info.py  # Device information detection
â”‚   â”‚
â”‚   â”œâ”€â”€ peripherals/        # OPOS-style peripherals (log-only until drivers are added)
â”‚   â”‚   â”œâ”€â”€ cash_drawer.py
â”‚   â”‚   â”œâ”€â”€ pos_printer.py
â”‚   â”‚   â”œâ”€â”€ line_display.py
â”‚   â”‚   â”œâ”€â”€ hooks.py        # SALE form line-display sync helpers
â”‚   â”‚   â””â”€â”€ ...             # scanner, scale, customer_display, remote_order_display stubs
â”‚   â”‚
â”‚   â”œâ”€â”€ service/            # Business logic services
â”‚   â”‚   â”œâ”€â”€ vat_service.py     # VAT calculation service
â”‚   â”‚   â”œâ”€â”€ sale_service.py    # Sale processing service
â”‚   â”‚   â””â”€â”€ payment_service.py # Payment processing service
â”‚   â”‚
â”‚   â””â”€â”€ manager/            # Application management
â”‚       â”œâ”€â”€ application.py  # Main application class
â”‚       â”œâ”€â”€ current_data.py # Current session data
â”‚       â”œâ”€â”€ current_status.py
â”‚       â”œâ”€â”€ cache_manager.py      # Data caching
â”‚       â”œâ”€â”€ closure_manager.py    # Closure management
â”‚       â”œâ”€â”€ document_manager.py   # Document lifecycle
â”‚       â”œâ”€â”€ event_handler.py      # Event handling (combines all event handlers)
â”‚       â””â”€â”€ event/          # Event handlers (9 specialized event handler classes)
â”‚           â”œâ”€â”€ general.py        # GeneralEvent: Login, logout, exit, navigation
â”‚           â”œâ”€â”€ sale.py           # SaleEvent: Sales transaction and product events
â”‚           â”œâ”€â”€ payment.py        # PaymentEvent: Payment processing events
â”‚           â”œâ”€â”€ closure.py        # ClosureEvent: End-of-day closure operations
â”‚           â”œâ”€â”€ configuration.py  # ConfigurationEvent: Settings and configuration
â”‚           â”œâ”€â”€ service.py        # ServiceEvent: Service-related operations
â”‚           â”œâ”€â”€ report.py         # ReportEvent: Report generation and viewing
â”‚           â”œâ”€â”€ hardware.py       # HardwareEvent: Hardware device operations
â”‚           â”œâ”€â”€ warehouse.py      # WarehouseEvent: Warehouse and inventory operations
â”‚           â””â”€â”€ product.py        # ProductEvent: Product list, search, and detail events
â”‚
â”œâ”€â”€ core/                    # Core utilities
â”‚   â”œâ”€â”€ logger.py           # Central logging (get_logger, config via settings.toml [logging])
â”‚   â””â”€â”€ exceptions.py       # Centralized exception hierarchy (SaleFlexError root)
â”‚
â”œâ”€â”€ settings/               # Configuration management
â”‚   â””â”€â”€ settings.py
â”‚
â”œâ”€â”€ static_files/           # Static assets
â”‚   â”œâ”€â”€ closures/           # Country-specific closure templates
â”‚   â”‚   â”œâ”€â”€ tr.json
â”‚   â”‚   â”œâ”€â”€ usa.json
â”‚   â”‚   â”œâ”€â”€ usa_ca.json
â”‚   â”‚   â””â”€â”€ ...
â”‚   â””â”€â”€ images/             # Image assets
â”‚       â”œâ”€â”€ saleflex.ico
â”‚       â””â”€â”€ ...
```

## Business Applications

SaleFlex.PyPOS is designed to meet the diverse needs of various business types:

- **Retail Stores**: Complete retail management with inventory, customer tracking, and sales analytics
- **Fast Food Restaurants**: Quick service restaurant operations with order management
- **Chain Restaurants**: Multi-location restaurant management with centralized control
- **Service Businesses**: Various service-oriented establishments with customizable workflows

## SaleFlex.GATE Integration

SaleFlex.PyPOS integrates seamlessly with **[SaleFlex.GATE](https://github.com/SaleFlex/SaleFlex.GATE)** - a Django-based centralized management system:

- **Centralized Management**: Monitor and manage multiple POS systems from one dashboard
- **Cloud-Based Access**: Remote control and monitoring for business owners and managers
- **ERP Integration**: Seamless data synchronization with existing ERP systems
- **Scalable Architecture**: Support growing businesses with multiple locations
- **Secure Data Flow**: Robust API-based communication between POS terminals and backend

## System Requirements

### Hardware Requirements
- **Devices**: Linux/Windows supported touch screen devices
- **Displays**: Single or dual display configurations
- **Printers**: ESC/P compatible receipt printers
- **Scanners**: 2D and 3D barcode readers
- **Scales**: Weighing scales for retail environments

### Software Requirements
- **Python**: 3.13 or higher (recommended)
- **PySide6**: 6.11.0 (Qt-based GUI framework)
- **SQLAlchemy**: 2.0.48 (ORM for database operations)
- **Requests**: 2.33.0 (HTTP client for API communications)

> **Note on Python 3.14:** Python 3.14 can be used to run the application, but SQLAlchemy does not yet officially support Python 3.14. You may encounter unexpected issues or incompatibilities. It is recommended to use Python 3.13 until official SQLAlchemy support for Python 3.14 is confirmed.

### Supported Database Engines
- **SQLite** (default, included)
- **PostgreSQL**
- **MySQL**
- **Oracle**
- **Microsoft SQL Server**
- **Firebird**
- **Sybase**

## Quick Start
```bash
git clone https://github.com/SaleFlex/SaleFlex.PyPOS.git
cd SaleFlex.PyPOS
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
python saleflex.py
```

**Default credentials:** `admin` / `admin` (administrator) Â· `jdoe` / `1234` (standard cashier)

## Installation & Setup

### Prerequisites
1. Install [Python 3.13](https://www.python.org/downloads/) or higher (**Python 3.14 is not yet officially supported by SQLAlchemy — use 3.13 for best compatibility**)
2. Ensure pip is installed and up to date

### Installation Steps

1. **Clone or Download** the SaleFlex.PyPOS project:
   ```bash
   git clone https://github.com/SaleFlex/SaleFlex.PyPOS.git
   cd SaleFlex.PyPOS
   ```

2. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate Virtual Environment**:
   
   **Windows:**
   ```cmd
   venv\Scripts\activate.bat
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**:
   ```bash
   python saleflex.py
   ```

### First Login

After running the application, you will see the login screen:

![Login Screen](static_files/images/sample_login.jpg)

> Touch-optimised login screen with cashier selection combobox, password field, and on-screen virtual keyboard.

**Default Login Credentials:**

| Username | Password | Role |
|---|---|---|
| `admin` | `admin` | Administrator — can edit all cashier accounts |
| `jdoe` | `1234` | Standard cashier — can update own password only |

After successful login, you will be redirected to the main menu:

![Main Menu](static_files/images/sample_main_menu.jpg)

> Main Menu listing all major modules: Sales, Closure, Settings, Cashier Management, and Products.

If you select "SALES", you will see a form as shown below:

![Sale Form](static_files/images/sample_sale_form.jpg)

> SALE form with PLU product buttons, department buttons, sale list, payment methods (Cash/Credit Card), NumPad, and real-time transaction totals.

Selecting "CLOSURE" opens the end-of-day closure screen:

![Closure Form](static_files/images/sample_closure_form.jpg)

> Closure form listing all completed closures with gross sales, opening cash, and closing cash totals. Administrators can perform end-of-day closure from this screen.

Selecting "SETTINGS" opens the POS settings panel:

![Settings Form](static_files/images/sample_settings_form.jpg)

> Settings panel showing POS hardware configuration (receipt printer, customer display, MAC address, etc.) with scroll support for long field lists.

Selecting "CASHIER MANAGEMENT" allows managing cashier accounts:

![Cashier Management Form](static_files/images/sample_cashier_form.jpg)

> Cashier Management form with cashier selection combobox, editable profile fields, and administrator-only **ADD NEW CASHIER** button. Field-level read-only protection enforced based on the `is_administrator` flag.

Selecting "PRODUCTS" opens the product search and listing screen:

![Product List Form](static_files/images/sample_product_form.jpg)

> Product List form with real-time search by name or short name, paginated DataGrid results, **DETAIL** button (bottom-left) to open the product detail view, and **BACK** button (bottom-right) to return to the Main Menu.

Clicking "DETAIL" on a selected product opens the tabbed product detail dialog:

![Product Detail Form](static_files/images/sample_product_detail_form.jpg)

> Product Detail modal dialog (DB-driven, 1024Ã—768) with four tabs: **Product Info** (code, name, price, stock, unit, manufacturer), **Barcodes**, **Attributes**, and **Variants**. Tabs are fully navigable via touch.

### Configuration
- Edit `settings.toml` to configure database connections and basic application settings
- **Note**: Many POS settings (hardware ports, display settings, backend connections) are now managed through the database (`PosSettings` model) and can be configured via the application UI or API
- The application uses SQLite by default, stored in `db.sqlite3`
- Device information (serial number, OS) is automatically detected and stored on first initialization

### Database Models Overview

The application includes **98+ database models** organized into logical categories:

- **Core System**: Cashier, Store, Table, Country, CountryRegion, City, District
- **Currency & Payment**: Currency, CurrencyTable, PaymentType, ClosureCurrency
- **Product Management**: Product, ProductVariant, ProductAttribute, ProductBarcode, ProductUnit, ProductManufacturer, DepartmentMainGroup, DepartmentSubGroup
- **Transaction Models**: TransactionHead/HeadTemp, TransactionProduct/ProductTemp, TransactionPayment/PaymentTemp, TransactionDiscount/DiscountTemp, TransactionTax/TaxTemp, TransactionTip/TipTemp, TransactionDepartment/DepartmentTemp, TransactionDelivery/DeliveryTemp, TransactionNote/NoteTemp, TransactionRefund/RefundTemp, TransactionSurcharge/SurchargeTemp, TransactionFiscal/FiscalTemp, TransactionKitchenOrder/KitchenOrderTemp, TransactionLoyalty/LoyaltyTemp, TransactionChange/ChangeTemp, TransactionVoid, TransactionLog, TransactionSequence, TransactionDocumentType, TransactionDiscountType, TransactionStatus
- **Warehouse Management**: Warehouse, WarehouseLocation, WarehouseProductStock, WarehouseStockMovement, WarehouseStockAdjustment
- **Customer Management**: Customer, CustomerSegment, CustomerSegmentMember
- **Campaign & Promotion**: CampaignType, Campaign, CampaignRule, CampaignProduct, CampaignUsage, Coupon, CouponUsage
- **Loyalty Programs**: LoyaltyProgram, LoyaltyTier, CustomerLoyalty, LoyaltyPointTransaction
- **Cashier Performance**: CashierWorkSession, CashierWorkBreak, CashierPerformanceMetrics, CashierPerformanceTarget, CashierTransactionMetrics
- **Closure & Reporting**: Closure, ClosureCashierSummary, ClosureCurrency, ClosureDepartmentSummary, ClosureDiscountSummary, ClosureDocumentTypeSummary, ClosurePaymentTypeSummary, ClosureTipSummary, ClosureVATSummary, ClosureCountrySpecific
- **Form & UI**: Form, FormControl (supports parent-child relationships for Panel controls with generic model form pattern), FormControlTab (tab page definitions for TABCONTROL controls — linked to FormControl via FK), PosSettings, PosVirtualKeyboard, ReceiptHeader, ReceiptFooter, LabelValue

All models support:
- **UUID Primary Keys**: Unique identifiers for all records
- **CRUD Operations**: Base CRUD class provides create, read, update, delete operations
- **Audit Trails**: Created/updated timestamps and user tracking
- **Soft Delete**: Records can be marked as deleted without physical removal
- **Auto-Save**: Automatic database persistence when attributes are modified

## Development Roadmap

### Core Infrastructure
- [x] **Project Structure** - Basic application framework
- [x] **Database Layer** - SQLAlchemy ORM integration with 98+ models
- [x] **Database Structure** - POS data layer structure with comprehensive model definitions
- [x] **UI Foundation** - PySide6 interface framework
- [x] **Auto-Save System** - Automatic database persistence with descriptor pattern
- [x] **Startup Entry-Point Guards** - Working-directory normalisation, Python version guard, single-instance file lock, global exception handler in `saleflex.py`
- [ ] **Configuration Management** - Advanced settings system
- [x] **Central Logging** - Configurable logging via `core/logger.py`; level, console, and file output driven by `settings.toml` `[logging]`; application-wide use of `get_logger(__name__)`
- [x] **Centralized Exception Handling** - Typed `SaleFlexError` hierarchy in `core/exceptions.py`; domain-specific subclasses for payment, hardware, tax, database, document, configuration, and authentication errors; all exceptions chained with `raise ... from e`

### POS Core Modules
- [x] **POS Manager Module** - Central business logic and transaction handling with document management system
- [x] **Document Management System** - Transaction lifecycle management with temp/permanent models, pending documents, and restaurant mode support
- [x] **Service Layer Architecture** - Business logic services (VatService, SaleService, PaymentService) for centralized calculations and operations
- [x] **Payment Processing System** - Multi-payment method processing with button name parsing, change calculation, and automatic document completion
- [x] **Event Handler System** - Comprehensive event handling with 9 specialized event handler classes (GeneralEvent, SaleEvent, PaymentEvent, ClosureEvent, ConfigurationEvent, ServiceEvent, ReportEvent, HardwareEvent, WarehouseEvent) for modular and maintainable code organization. All event handler methods use `_event` suffix (e.g., `_sales_form_event`, `_closure_event`) to avoid conflicts with properties
- [x] **Auto-Save System** - Automatic database persistence using descriptor pattern and wrapper classes (AutoSaveModel, AutoSaveDict, AutoSaveDescriptor) for seamless data integrity
- [ ] **SPU/PLU Management** - Product and pricing management
- [ ] **Customer Module** - Customer relationship management
- [ ] **Printer Module** - Receipt and invoice printing
- [ ] **Inventory Management** - Real-time stock tracking and control
- [ ] **Tax & Discount Engine** - Advanced tax calculation and discount management

### Hardware Integration
- [ ] **Payment Device Integration**:
  - [ ] Card Reader Support (Chip & PIN, Contactless)
  - [ ] Mobile Payment Integration (Apple Pay, Google Pay)
  - [ ] Cash Drawer Control
  - [ ] PIN Pad Integration
- [ ] **Peripheral Device Support**:
  - [ ] Barcode Scanner Integration
  - [ ] Electronic Scale Integration
  - [ ] Receipt Printer Drivers
  - [ ] Display Pole Integration
- [ ] **Hardware Abstraction Layer** - Unified hardware communication interface

### User Interface
- [x] **Panel Control** - Scrollable container control with parent-child support for complex forms
- [x] **Parent-Child Control Relationships** - Panel controls can contain child controls (textboxes, checkboxes, labels, buttons)
- [x] **Generic Panel-Based Form Saving** - Automatic model updates from panel textbox and checkbox values on SAVE button click. Works with any model via naming convention (panel name = model name, control name = model field). Automatically loads model data into form and saves changes to database
- [x] **Cashier Management Form** - Role-aware cashier management with `CASHIER_MGMT_LIST` combobox for multi-cashier selection, `editing_cashier` session tracking, and field-level read-only enforcement based on `is_administrator` flag
- [x] **Add New Cashier (Admin Only)** - `ADD_NEW_CASHIER` button on CASHIER form visible only to administrators. Clears panel textboxes in-place, hides combobox and button during entry. On save, cache is updated and form redraws with new cashier pre-selected. Includes `_is_adding_new_cashier` session flag for lifecycle management
- [ ] **Dynamic Interface Interpreter** - Flexible UI rendering system
- [ ] **Interface Functions** - Core UI interaction handlers
- [ ] **Tables Layout Module** - Restaurant table management
- [ ] **Screen Designer App** - Custom interface design tool
- [ ] **Multi-Display Support** - Customer and cashier display management
- [x] **Touch Optimization** - Enhanced touch screen experience with 30px scrollbars for Panel controls

### Business Features
- [ ] **Campaign & Promotion Management**:
  - [ ] Multiple Campaign Types (Product Discount, Basket Discount, Time-Based, Buy X Get Y, Welcome Bonus)
  - [ ] Flexible Discount Rules (Percentage, Fixed Amount, Free Product)
  - [ ] Time-Based Restrictions (Date Range, Daily Hours, Days of Week)
  - [ ] Product/Category/Brand/Payment Type Filters
  - [ ] Usage Limits & Priority Rules
  - [ ] Customer Segment Targeting
  - [ ] Coupon Generation & Management (QR Code, Barcode Support)
  - [ ] Campaign Usage Tracking & Analytics
- [ ] **Loyalty Program Management**:
  - [ ] Points Earning & Redemption Rules
  - [ ] Point Expiry Management
  - [ ] Tiered Membership System (Bronze, Silver, Gold, Platinum)
  - [ ] Welcome & Birthday Bonus Points
  - [ ] Tier-Based Benefits (Points Multiplier, Automatic Discounts)
  - [ ] Complete Point Transaction History
  - [ ] Customer Segmentation (VIP, New, Frequent, High Value, Inactive, Birthday)
  - [ ] GDPR Compliant Consent Management
- [ ] **Reports Module** - Comprehensive business analytics
- [ ] **Employee Management** - Staff scheduling and performance tracking
- [ ] **Returns & Exchanges** - Product return and exchange handling
- [ ] **Multi-Store Support** - Chain store management capabilities

### Warehouse & Inventory Management
- [ ] **Advanced Inventory Control**:
  - [ ] Real-time Stock Tracking
  - [ ] Multi-Location Inventory Management
  - [ ] Stock Transfer Between Locations
  - [ ] Automatic Reorder Points & Alerts
- [ ] **Warehouse Operations**:
  - [ ] Goods Receiving & Put-away
  - [ ] Pick & Pack Operations
  - [ ] Cycle Counting & Physical Inventory
  - [ ] Batch & Serial Number Tracking
- [ ] **Supply Chain Management**:
  - [ ] Vendor Management & Purchase Orders
  - [ ] Supplier Performance Analytics
  - [ ] Automated Procurement Workflows
  - [ ] Cost Analysis & Optimization
- [ ] **Inventory Analytics**:
  - [ ] ABC Analysis (Fast/Slow Moving Items)
  - [ ] Demand Forecasting
  - [ ] Inventory Turnover Reports
  - [ ] Wastage & Shrinkage Tracking

### Sector-Specific Features
- [ ] **Restaurant Management**:
  - [ ] Recipe & Ingredient Management
  - [ ] Kitchen Display System (KDS)
  - [ ] Table Management & Reservations
  - [ ] Menu Engineering & Cost Analysis
  - [ ] Food Safety & Expiration Tracking
- [ ] **Retail Store Management**:
  - [ ] Category & Brand Management
  - [ ] Size & Color Variations
  - [ ] Seasonal Pricing & Promotions
  - [ ] Customer Shopping Behavior Analytics
  - [ ] Planogram & Shelf Management
- [ ] **Fashion & Boutique**:
  - [ ] Size Matrix & Style Variations
  - [ ] Fashion Season Management
  - [ ] Consignment & Vendor Management
  - [ ] Trend Analysis & Buying Recommendations
  - [ ] Alteration & Custom Order Tracking
- [ ] **Grocery & Supermarket**:
  - [ ] Fresh Produce Management
  - [ ] Deli & Bakery Operations
  - [ ] Bulk Item Management
  - [ ] Supplier & Private Label Management
  - [ ] Perishable Item Rotation (FIFO/LIFO)

### Integration & Connectivity
- [ ] **SaleFlex.GATE Integration**:
  - [ ] Data Synchronization Service
  - [ ] ERP Connection Layer
  - [ ] Multi-Store Management
  - [ ] Cloud-Based Remote Access
  - [ ] Real-time Analytics Dashboard
- [ ] **Third-Party Integrations**:
  - [ ] Accounting Software APIs
  - [ ] E-commerce Platform Sync
  - [ ] Warehouse Management Systems
  - [ ] External Payment Gateways
- [ ] **Offline/Online Mode** - Seamless switching between online and offline operations

### Security & Authentication
- [ ] **User Authentication System** - Multi-level user access control
- [ ] **Data Encryption** - Secure data storage and transmission
- [ ] **Audit Trail** - Comprehensive transaction logging
- [ ] **Role-Based Access Control** - Granular permission management
- [ ] **PCI DSS Compliance** - Payment industry security standards

### Performance & Scalability
- [x] **In-Memory Data Caching** - Reference data (`pos_data`) and product data (`product_data`) loaded once at startup to minimize disk I/O
- [x] **Product Data Cache** - All product-related models (including Currency, CurrencyTable, and Vat) cached in memory for fast sale operations, currency calculations, VAT lookups, and button rendering
- [x] **Active Closure Management** - Current closure data maintained in session memory (`CurrentData.closure`) with automatic loading at startup and lifecycle management (open → active → closed)
- [x] **Auto-Save Optimization** - Automatic database persistence reduces manual save operations and ensures data integrity without performance overhead
- [ ] **Database Optimization** - Query optimization and indexing
- [ ] **External Caching Layer** - Redis/Memcached integration (optional)
- [ ] **Load Testing** - Performance testing under high load
- [x] **Memory Management** - Efficient resource utilization via pos_data and product_data caches
- [ ] **Concurrent Transaction Handling** - Multi-terminal support

### Data Management
- [ ] **Data Migration Tools** - Database upgrade and migration utilities
- [ ] **Backup & Recovery** - Automated backup and restore systems
- [ ] **Data Export/Import** - CSV, Excel, and API data exchange
- [ ] **Data Archiving** - Long-term data storage solutions

### Localization & Compliance
- [ ] **Multi-Language Support** - Internationalization (i18n)
- [x] **Currency Support** - Multi-currency handling with exchange rate tracking
- [x] **Tax Compliance** - Country-specific tax regulations with VAT/tax rate management
- [ ] **Fiscal Printer Support** - Government-mandated receipt requirements
- [x] **Local Regulations** - Region-specific compliance features via `ClosureCountrySpecific` model with template-based initialization (supports Turkey E-Fatura, USA state taxes, EU VAT reporting, etc.)
- [x] **Region Management** - `CountryRegion` model for tracking states/provinces/special zones with ISO 3166-2 compliant fields. Includes 80+ pre-populated regions (US states, CA provinces, DE states, FR regions) and integration with closure templates
- [x] **ISO 3166 Compliance** - Country and region models use ISO 3166-1 (alpha-2, alpha-3, numeric) and ISO 3166-2 (subdivision codes) standard field names for international compatibility

## Documentation

Comprehensive documentation is available in the `docs/` directory:

| Document | Description |
|----------|-------------|
| **[Documentation Index](docs/README.md)** | Complete guide organized by topic |
| **[Installation Guide](docs/03-installation.md)** | Detailed setup instructions |
| **[First Login](docs/04-first-login.md)** | Default credentials and role differences |
| **[Basic Navigation](docs/05-basic-navigation.md)** | Sale processing, NumPad modes, SUSPEND/CANCEL |
| **[Dynamic Forms System](docs/06-dynamic-forms.md)** | Database-driven UI system and Panel controls |
| **[Virtual Keyboard](docs/06-virtual-keyboard.md)** | Virtual keyboard configuration and themes |
| **[Data Caching](docs/08-data-caching.md)** | Caching strategy and implementation |
| **[Document Management](docs/09-document-management.md)** | Transaction lifecycle management |
| **[Database Models](docs/10-database-models.md)** | Complete model reference (98+ models) |
| **[Closure Operation](docs/15-closure-operation.md)** | End-of-day closure (authorization, aggregation, sequences) |
| **[Service Layer](docs/14-service-layer.md)** | Business logic services architecture |
| **[Central Logging](docs/16-logging.md)** | Logging configuration and usage |
| **[Exception Handling](docs/17-exception-handling.md)** | Centralized exception hierarchy |
| **[Peripherals](docs/18-peripherals.md)** | OPOS-style device layer (cash drawer, printer, display) |
| **[Startup Entry Point](docs/19-startup-entry-point.md)** | Working-dir fix, Python version guard, single-instance lock, global exception handler |
| **[Troubleshooting](docs/12-troubleshooting.md)** | Common issues and solutions |

## Contributing

We welcome contributions to SaleFlex.PyPOS! Please read our contributing guidelines and feel free to submit issues, feature requests, or pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributors

<table>
<tr>
    <td align="center">
        <a href="https://github.com/ferhat-mousavi">
            <img src="https://avatars.githubusercontent.com/u/5930760?v=4" width="100;" alt="Ferhat Mousavi"/>
            <br />
            <sub><b>Ferhat Mousavi</b></sub>
        </a>
    </td>
</tr>
</table>

## Support & Donations

If you find SaleFlex.PyPOS valuable and want to support its development, you can contribute through cryptocurrency donations:

- **USDT**: `0xa5a87a939bfcd492f056c26e4febe102ea599b5b`
- **BUSD**: `0xa5a87a939bfcd492f056c26e4febe102ea599b5b`
- **BTC**: `184FDZ1qV2KFzEaNqMefw8UssG8Z57FA6F`
- **ETH**: `0xa5a87a939bfcd492f056c26e4febe102ea599b5b`
- **SOL**: `Gt3bDczPcJvfBeg9TTBrBJGSHLJVkvnSSTov8W3QMpQf`

Your support helps us continue developing new features and maintaining this open-source project.

---

**For more information about the SaleFlex ecosystem, visit [SaleFlex.GATE](https://github.com/SaleFlex/SaleFlex.GATE) for centralized management capabilities.**



