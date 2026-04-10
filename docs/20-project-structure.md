# Project Structure

This document describes the top-level folder layout, the purpose of every package, and the class inheritance chain that ties the application together.

---

## Folder Layout

```
SaleFlex.PyPOS/
├── saleflex.py                 ← Entry point (startup guards, single-instance lock)
├── settings.toml               ← Infrastructure config (DB, logging)
├── requirements.txt
│
├── core/                       ← Cross-cutting concerns
│   ├── logger.py               ← Centralised logging factory
│   └── exceptions.py           ← SaleFlexError hierarchy
│
├── settings/
│   └── settings.py             ← Reads settings.toml → typed Settings object
│
├── data_layer/                 ← Persistence layer
│   ├── engine.py               ← SQLAlchemy engine + session factory
│   ├── db_manager.py           ← init_db() orchestrator
│   ├── db_initializer.py       ← Creates tables and runs seed functions
│   ├── db_utils.py             ← Shared query helpers
│   ├── model/
│   │   ├── crud_model.py       ← BaseModel with CRUD + UUID + soft-delete
│   │   ├── mixins.py           ← AutoSave, AuditMixin, etc.
│   │   └── definition/         ← 100+ SQLAlchemy model classes (one file each)
│   ├── db_init_data/           ← Seed data functions (one file per model)
│   │   └── forms/              ← Form + control definitions split by topic
│   ├── auto_save/              ← AutoSaveDescriptor / AutoSaveModel / AutoSaveDict
│   └── enums/                  ← ControlName, ControlType, EventName, FormName, …
│
├── pos/                        ← Business logic layer
│   ├── data/                   ← Lightweight data classes / enums (DocumentState, etc.)
│   ├── hardware/               ← Device info detection
│   ├── peripherals/            ← OPOS-style device stubs (printer, drawer, scanner, …)
│   ├── service/                ← VatService, SaleService, PaymentService, LoyaltyEarnService, LoyaltyRedemptionService, LoyaltyService, …
│   └── manager/
│       ├── application.py      ← Singleton Application (inherits all managers)
│       ├── current_status.py   ← CurrentStatus mixin (login state, form stack)
│       ├── current_data.py     ← CurrentData mixin (document, cache, closure)
│       ├── event_handler.py    ← EventHandler (event map + distributor)
│       ├── cache_manager.py    ← CacheManager mixin (pos_data / product_data)
│       ├── document_manager.py ← DocumentManager mixin (create, load, complete)
│       ├── closure_manager.py  ← ClosureManager mixin (load, close, sync seq)
│       └── event/              ← 10 specialised event handler mixins
│           ├── general.py      ← Login, logout, navigation, save, redraw
│           ├── sale.py         ← PLU lookup, department sale, suspend, cancel
│           ├── payment.py      ← Cash, card, change, payment detail
│           ├── closure.py      ← End-of-day closure execution
│           ├── configuration.py← Settings, definitions, brightness, …
│           ├── product.py      ← Product list, search, detail dialog
│           ├── report.py       ← Reports and lists
│           ├── service.py      ← Service-level operations
│           ├── hardware.py     ← Open cash drawer, etc.
│           └── warehouse.py    ← Stock in/out, transfers, counts
│
├── user_interface/             ← Presentation layer (PySide6 / Qt)
│   ├── manager/
│   │   └── interface.py        ← Interface: draw / redraw / show_modal
│   ├── render/
│   │   └── dynamic_renderer.py ← Reads DB → form dict for BaseWindow
│   ├── window/
│   │   ├── base_window.py      ← Base QMainWindow: creates all control types
│   │   └── dynamic_dialog.py   ← QDialog version of BaseWindow (modal forms)
│   ├── form/
│   │   ├── about_form.py       ← Splash/about screen during startup
│   │   └── message_form.py     ← General-purpose message/dialog box
│   └── control/                ← Custom Qt widgets (one folder per widget type)
│       ├── button.py
│       ├── label.py
│       ├── textbox.py
│       ├── checkbox.py
│       ├── combobox.py
│       ├── datagrid.py
│       ├── panel.py
│       ├── statusbar.py
│       ├── toolbar.py
│       ├── numpad/
│       ├── sale_list/
│       ├── payment_list/
│       ├── amount_table/
│       ├── tab_control/
│       ├── transaction_status/
│       └── virtual_keyboard/
│
├── static_files/
│   ├── images/                 ← Application icons
│   └── closures/               ← Country/region JSON closure templates
│
├── docs/                       ← This documentation
└── logs/                       ← Runtime log files (auto-created)
```

---

## Class Inheritance Chain

The main `Application` class combines the core managers with **`IntegrationMixin`** for external routing:

```
Application
├── CurrentStatus          ← login state, active form ID, form history stack
├── CurrentData            ← session data (pos_data, product_data, document_data, closure)
│   ├── CacheManager       ← populate_pos_data(), populate_product_data(), update_*_cache()
│   ├── DocumentManager    ← create_empty_document(), load_incomplete_document(), complete_document()
│   └── ClosureManager     ← load_open_closure(), create_empty_closure(), close_closure()
├── EventHandler           ← event_distributor() + _not_defined_function()
│   ├── GeneralEvent        ← login, logout, navigation, save, redraw
│   ├── SaleEvent           ← PLU, barcode, department, suspend, cancel, REPEAT/DELETE
│   ├── PaymentEvent        ← cash, card, change, payment detail
│   ├── ClosureEvent        ← end-of-day closure
│   ├── ConfigurationEvent  ← settings, definitions
│   ├── ProductEvent        ← product list, search, detail
│   ├── ReportEvent         ← reports and lists
│   ├── ServiceEvent        ← service-mode operations
│   ├── HardwareEvent       ← peripheral control
│   └── WarehouseEvent      ← stock operations
└── IntegrationMixin       ← init_integration(); apply_campaign (GATE / third-party / local proposals)
```

**`CurrentStatus`**, **`CurrentData`**, **`EventHandler`**, and **`IntegrationMixin`** are the direct bases of **`Application`**; nested event classes are attributes of **`EventHandler`**. Python's MRO resolves method calls (e.g. **`apply_campaign`** comes from **`IntegrationMixin`**).

---

## Startup Sequence

```
saleflex.py
│  1. Fix working directory (os.chdir to script folder)
│  2. Python ≥ 3.13 version guard
│  3. Acquire single-instance file lock
│  4. Initialise logger (from settings.toml)
│  5. Create Application() singleton
│        │
│        ├── init_db()  (create tables + run seed functions)
│        ├── QApplication setup (icon, window size)
│        ├── populate_pos_data()   → fills pos_data dict
│        ├── populate_product_data() → fills product_data dict
│        ├── load_startup_form()   → finds is_startup=True form in DB
│        ├── load_open_closure()   → loads or creates active closure
│        └── load_incomplete_document() → recovers any interrupted sale
│  6. app.run()  → qt.exec() main loop
└── on exit: release file lock
```

---

## Key Design Patterns

| Pattern | Where used | Purpose |
|---------|------------|---------|
| Singleton | `Application` | One POS process per terminal |
| Multiple inheritance / Mixin | All manager classes | Organize concerns without deep class trees |
| Descriptor + wrapper | `auto_save/` | Automatic DB persistence when model attributes change |
| Dictionary-based dispatch | `EventHandler.event_distributor()` | Map string event names → handler callables without large `if/elif` chains |
| DB-driven UI | `DynamicFormRenderer` + `BaseWindow` | Forms defined in the database, not in Python source |
| Two-phase temp/permanent | `TransactionHeadTemp` → `TransactionHead` | Protect reporting tables from incomplete transactions |
| In-memory cache | `pos_data` / `product_data` | Avoid repeated DB reads during sale operations |

---

[← Back to Table of Contents](README.md) | [Previous: Product Management](15-product-management.md) | [Next: Database Models Overview →](21-database-models.md)
