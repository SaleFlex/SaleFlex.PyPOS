# Database Initialization Functions

The `data_layer/db_init_data` module contains functions that populate the database with initial/default data when the database is first created. These functions are called in a specific order to respect foreign key dependencies.

## Initialization Flow

The `insert_initial_data()` function in `db_init_data/__init__.py` orchestrates the initialization process:

1. **Admin Cashier** (`_insert_admin_cashier`): Creates default administrator user (username: admin, password: admin)
2. **Countries** (`_insert_countries`): Inserts world countries with ISO codes
3. **Country Regions** (`_insert_country_regions`): Inserts 80+ sub-country regions (US states, Canadian provinces, German states, French regions) with ISO 3166-2 codes
4. **Default Store** (`_insert_default_store`): Creates default store with basic business information, address fields, and contact details. Note: System information (MAC address, OS version, serial number) and hardware settings are managed through `PosSettings` model.
5. **Cities** (`_insert_cities`): Inserts city master data
6. **Districts** (`_insert_districts`): Inserts district/region data
7. **Warehouses** (`_insert_warehouses`): Creates default warehouses (Main, Backroom, Sales Floor, etc.)
8. **Currencies** (`_insert_currencies`): Inserts major world currencies (USD, EUR, GBP, etc.)
9. **Currency Table** (`_insert_currency_table`): Sets up currency exchange rates
10. **Payment Types** (`_insert_payment_types`): Creates payment methods (Cash, Credit Card, Debit Card, etc.)
11. **VAT Rates** (`_insert_vat_rates`): Inserts default VAT/tax rates (0%, 5%, 20%, etc.)
12. **Product Units** (`_insert_product_units`): Creates measurement units (PCS, KG, L, M, etc.)
13. **Product Manufacturers** (`_insert_product_manufacturers`): Inserts sample manufacturer data
14. **Department Groups** (`_insert_department_groups`): Creates product category structure (main groups and sub-groups)
15. **Products** (`_insert_products`): Inserts sample products for testing
16. **Product Variants** (`_insert_product_variants`): Creates product variations
17. **Product Attributes** (`_insert_product_attributes`): Inserts product attribute definitions
18. **Product Barcodes** (`_insert_product_barcodes`): Associates barcodes with products
19. **Transaction Discount Types** (`_insert_transaction_discount_types`): Creates discount type definitions (NONE, PERSONAL, MANAGER, CUSTOMER_SATISFACTION, PRODUCT, **LOYALTY** for point redemption)
20. **Transaction Document Types** (`_insert_transaction_document_types`): Creates document types (Sale, Return, etc.)
21. **Transaction Sequences** (`_insert_transaction_sequences`): Sets up transaction numbering sequences
22. **Product Barcode Masks** (`_insert_product_barcode_masks`): Defines barcode format rules
23. **Default Forms** (`_insert_default_forms`): Creates LOGIN and MAIN_MENU forms
24. **Form Controls** (`_insert_form_controls`): Populates forms with controls (buttons, textboxes, checkboxes, comboboxes, panels, etc.). Seeded SETTING and CASHIER forms use **CHECKBOX** (`type_no=11`) for boolean fields (`force_to_work_online`, `is_administrator`, `is_active`).
25. **Label Values** (`_insert_label_values`): Inserts translation labels and configuration values
26. **Cashier Performance Targets** (`_insert_cashier_performance_targets`): Sets up performance targets
27. **Virtual Keyboard Settings** (`_insert_virtual_keyboard_settings`): Creates default keyboard theme
28. **Alternative Keyboard Themes** (`_insert_alternative_keyboard_themes`): Adds additional keyboard themes
29. **Campaigns** (`_insert_campaigns`): Creates sample promotional campaigns
30. **Loyalty Programs** (`_insert_loyalty`): Sets up loyalty program with tiers, `LoyaltyProgramPolicy`, `LoyaltyRedemptionPolicy` (used by **`LoyaltyRedemptionService`** on **BONUS**), default `settings_json` (e.g. **`earn_eligible_payment_types`**), and a default `LoyaltyEarnRule` row (`DOCUMENT_TOTAL`; extra bonuses via `config_json`; full earn logic in **`LoyaltyEarnService`** — see [Loyalty Programs](41-loyalty-programs.md))
31. **Customer Segments** (`_insert_customer_segments`): Creates default `CustomerSegment` rows (VIP, NEW_CUSTOMER, FREQUENT_BUYER, HIGH_VALUE, INACTIVE, BIRTHDAY); VIP seed includes **`honor_preferences_vip`** for `preferences_json` flags. Runtime assignment is **`CustomerSegmentService`** (see [Customer Segmentation](42-customer-segmentation.md))
32. **POS Settings** (`_insert_pos_settings`): Configures system-wide POS settings including device serial number (generated from MAC address and disk serial), operating system information, default country (United Kingdom), default currency (GBP), customer display settings (INTERNAL), barcode reader port (PS/2), backend connection settings (127.0.0.1:5000), and backend type (GATE)

## Function Details

### `_insert_admin_cashier(session)`
Creates the default cashier accounts on first initialization:

**Administrator account:**
- Username: `admin`
- Password: `admin` (should be hashed in production)
- Name: Ferhat Mousavi
- `is_administrator = True` → all fields in Cashier Management form are editable
- Returns the admin cashier object for use in other initialization functions

**Standard cashier account:**
- Username: `jdoe`
- Password: `1234`
- Name: John Doe
- `is_administrator = False` → only password is editable in Cashier Management form; all other fields are read-only

Both accounts are created only if they do not already exist (idempotent).

### `_insert_default_store(session)`
Creates the default store with:
- Basic business information (brand name, company name, description)
- Address fields (street, district, postal code, city, country)
- Contact information (phone, email, fax)
- Manager and technician contact details (can be set later)
- Links to default country (United Kingdom) and city (if available)
- Active status flag

**Note:** System information (MAC address, OS version, serial number) and hardware settings (printers, displays, scales, barcode readers) are managed through the `PosSettings` model, not the Store model.

### `_insert_countries(session)`
Inserts comprehensive country master data including:
- ISO 3166-1 alpha-2 codes (`iso_alpha2`: 2-letter codes like "US", "TR", "CA")
- ISO 3166-1 alpha-3 codes (`iso_alpha3`: 3-letter codes like "USA", "TUR", "CAN")
- ISO 3166-1 numeric codes (`iso_numeric`: 3-digit codes like 840, 792, 124)
- Country names

### `_insert_country_regions(session, admin_cashier_id)`
Inserts sub-country regions for countries with regional variations:
- **United States**: 50 states + DC (California, New York, Texas marked with special requirements)
- **Canada**: 10 provinces + 3 territories (Ontario, British Columbia, Quebec, etc.)
- **Germany**: 16 states/Länder (Bavaria, Baden-Württemberg, Berlin, etc.)
- **France**: 13 regions (Île-de-France, Provence-Alpes-Côte d'Azur, etc.)
- Each region includes: `region_code` (subdivision code), `name` (region name), `iso_3166_2` (full ISO 3166-2 code), `region_type`
- Total: 80+ regions pre-populated

### `_insert_currencies(session)`
Inserts major world currencies:
- Currency codes (USD, EUR, GBP, TRY, etc.)
- Currency names
- Symbols
- Decimal places
- Returns GBP currency for POS settings reference

### `_insert_products(session, admin_cashier_id)`
Inserts sample products covering various categories:
- Fresh food items
- Packaged goods
- Beverages
- Different VAT rates
- Various units (PCS, KG)
- Links to departments, manufacturers, and warehouses

### `_insert_transaction_discount_types(session)`
Inserts default transaction discount types:
- **NONE**: No discount applied
- **PERSONAL**: Personal discount for customer
- **MANAGER**: Manager approved discount
- **CUSTOMER_SATISFACTION**: Discount for customer satisfaction
- **PRODUCT**: Product-specific discount
- **LOYALTY**: Point redemption discount (paired with **`LoyaltyRedemptionService`** / **`TransactionDiscountTemp.discount_type="LOYALTY"`**)

### `_insert_default_forms(session, cashier_id)`
Creates all 20 application forms. Form definitions are organised into topic-based sub-modules under `data_layer/db_init_data/forms/`. Each sub-module provides a `get_form_data(cashier_id)` function that returns the form row dict(s) for that topic:

| Sub-module | Forms |
|---|---|
| `forms/login.py` | #1 LOGIN |
| `forms/main_menu.py` | #2 MAIN_MENU |
| `forms/management.py` | #3 SETTING, #4 CASHIER |
| `forms/sale.py` | #5 SALE, #7 SUSPENDED_SALES_MARKET |
| `forms/closure.py` | #6 CLOSURE, #10 CLOSURE_DETAIL, #11 CLOSURE_RECEIPTS, #12 CLOSURE_RECEIPT_DETAIL |
| `forms/product.py` | #8 PRODUCT_LIST, #9 PRODUCT_DETAIL |
| `forms/stock.py` | #13 STOCK_INQUIRY, #14 STOCK_IN, #15 STOCK_ADJUSTMENT, #16 STOCK_MOVEMENT |
| `forms/customer.py` | #17 CUSTOMER_LIST, #18 CUSTOMER_DETAIL, #19 CUSTOMER_SELECT |
| `forms/payment_screen.py` | #20 PAYMENT |

Each form row includes layout dimensions (1024×768), colors, display mode (`MAIN` or `MODAL`), and the `is_startup` flag (only MAIN_MENU is `True`).

### `_insert_form_controls(session, cashier_id)`
Populates all 20 forms with their controls (buttons, textboxes, labels, comboboxes, panels, tab controls, data grids, etc.). Control definitions live in the same topic-based sub-modules as the form definitions.

**Insertion is performed in three phases:**

**Phase 1 — Bulk insert:** All simple controls (no inter-control UUID dependencies) are collected from the sub-modules and added to the session together.

**Phase 2 — Parent-ID wiring (after first flush):** Panel children that need `fk_parent_id` pointing to their enclosing panel's UUID are wired using `update_config_panel_parents()` and `update_cashier_panel_parents()`.

**Phase 3 — Tab-based and inventory forms:** Forms with `TABCONTROL` hierarchies (`PRODUCT_DETAIL`, `CUSTOMER_DETAIL`) and inventory forms issue their own internal `session.flush()` calls to obtain UUIDs before creating child controls.

**SALE form:** `SALESLIST`, `NUMPAD`, `PAYMENTLIST`, department buttons, PLU buttons, product barcode shortcut buttons, cash payment denomination buttons, and dual-function buttons (`PAYMENT_SUSPEND`, `SUB TOTAL`/`CUSTOMER`, `CREDIT CARD`/`PAYMENT`, `DISC %`/`MARK %`, `DISC AMT`/`MARK AMT`). **FUNC** only swaps their captions between primary and alternate; a dual-button tap runs the visible event and resets **all** dual buttons on the form to primary captions.

**PAYMENT form (#20):** `AMOUNTSTABLE`, `PAYMENTLIST`, `NUMPAD` (Enter → `NONE`), `BACK`, `PAYMENT_CHANGE` (`CHANGE_PAYMENT`), and payment-type buttons (see `forms/payment_screen.py`).

**SUSPENDED_SALES_MARKET form:** `SUSPENDED_SALES_DATAGRID` (receipt no, line count, total), **ACTIVATE** (`RESUME_SALE`), and **BACK** button.

**Closure model:** `Closure.suspended_transaction_count` stores how many suspended documents belonged to the closed period; they are not included in closure financial totals.

**CASHIER form controls in detail:**
- `CASHIER_MGMT_LIST` (COMBOBOX): Appears above the data panel. Admin users see all cashiers; non-admin users see only themselves. Fires `SELECT_CASHIER` event. Hidden during new-cashier entry mode.
- `CASHIER` (PANEL): Scrollable panel containing all cashier data fields
- Field controls inside panel: `NO`, `USER_NAME`, `NAME`, `LAST_NAME`, `PASSWORD`, `IDENTITY_NUMBER`, `DESCRIPTION`, `IS_ADMINISTRATOR` (CHECKBOX), `IS_ACTIVE` (CHECKBOX)
- `SAVE` (BUTTON): Saves the currently selected cashier's data
- `BACK` (BUTTON): Returns to the main menu
- `ADD_NEW_CASHIER` (BUTTON): Visible only to administrators. Fires `ADD_NEW_CASHIER` event; clears the panel fields and hides the combobox for new-cashier entry.

### `_insert_virtual_keyboard_settings(session)`
Creates the default virtual keyboard theme:
- Size: 970x315 pixels
- Light gradient theme
- Font: Noto Sans CJK JP, 20px
- Button styling and colors

### `_insert_loyalty(session, admin_cashier_id)`
Sets up loyalty program:
- Default loyalty program with point earning configuration on `LoyaltyProgram`
- Membership tiers (Bronze, Silver, Gold, Platinum) with benefits and point multipliers
- **`LoyaltyProgramPolicy`** — phone-first identity, default country calling code (`90` in seed), enrollment rules, integration provider (`LOCAL`)
- **`LoyaltyRedemptionPolicy`** — redemption caps/steps; consumed at runtime by **`LoyaltyRedemptionService`** when the cashier uses **BONUS** on the PAYMENT form
- **`LoyaltyEarnRule`** — default `DOCUMENT_TOTAL` row (empty `config_json` in seed); runtime evaluation and additional rule types are implemented in **`LoyaltyEarnService`**

Inserts are idempotent (skip when rows already exist). See [Loyalty Programs](41-loyalty-programs.md).

### `_insert_campaigns(session, admin_cashier_id)`
Creates sample promotional campaigns:
- Product discount campaigns
- Basket discount campaigns
- Time-based promotions
- Campaign rules and conditions

### `_insert_pos_settings(session, admin_cashier_id, gbp_currency=None)`
Configures system-wide POS settings:
- **Device Information**: Automatically generates unique device serial number (combining MAC address and disk serial number hash) and detects operating system
- **Default Values**: Sets POS number in store (1), customer display type (INTERNAL), customer display port (INTERNAL), barcode reader port (PS/2)
- **Backend Configuration**: Sets default backend connection settings (IP: 127.0.0.1, Port: 5000 for both primary and secondary connections) and backend type (GATE)
- **Geographic Settings**: Links to default country (United Kingdom) and currency (GBP)
- **Hardware Module**: Uses `pos.hardware.device_info` module for cross-platform device information collection

## Initialization Behavior

- **Idempotent**: Functions check if data already exists before inserting
- **Dependency Aware**: Functions are called in order to respect foreign key relationships
- **Error Handling**: SQLAlchemy errors are caught and reported
- **Transaction Safe**: All inserts happen within a single database transaction

## Customization

To customize initial data:
1. Modify the respective `_insert_*` functions in `data_layer/db_init_data/`
2. Add new initialization functions and call them in `insert_initial_data()`
3. Ensure proper ordering to respect foreign key dependencies

### Adding or Modifying Forms and Controls

Form and form-control seed data is organized by topic under `data_layer/db_init_data/forms/`. Each sub-module contains:
- `get_form_data(cashier_id)` → returns a list of form-row dicts
- `get_form_controls(form, cashier_id)` → returns a list of `FormControl` objects (simple forms)
- `insert_*_controls(session, form, cashier_id)` → inserts controls with internal flushes (tab-based forms: `PRODUCT_DETAIL`, `CUSTOMER_DETAIL`, and all stock inventory forms)

To add a new form:
1. Add the form row dict in the appropriate sub-module's `get_form_data()` (or create a new sub-module)
2. Add the corresponding control-creation function
3. Register the new form in `FormName` enum (`data_layer/enums/form_name.py`)
4. Import and call the new function in `form.py` and `form_control.py`

---

[← Back to Table of Contents](README.md) | [Previous: Exception Handling](32-exception-handling.md) | [Next: Startup Entry Point →](34-startup-entry-point.md)
