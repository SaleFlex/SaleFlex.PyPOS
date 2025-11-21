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
19. **Transaction Discount Types** (`_insert_transaction_discount_types`): Creates discount type definitions (NONE, PERSONAL, MANAGER, CUSTOMER_SATISFACTION, PRODUCT)
20. **Transaction Document Types** (`_insert_transaction_document_types`): Creates document types (Sale, Return, etc.)
21. **Transaction Sequences** (`_insert_transaction_sequences`): Sets up transaction numbering sequences
22. **Product Barcode Masks** (`_insert_product_barcode_masks`): Defines barcode format rules
23. **Default Forms** (`_insert_default_forms`): Creates LOGIN and MAIN_MENU forms
24. **Form Controls** (`_insert_form_controls`): Populates forms with controls (buttons, textboxes, etc.)
25. **Label Values** (`_insert_label_values`): Inserts translation labels and configuration values
26. **Cashier Performance Targets** (`_insert_cashier_performance_targets`): Sets up performance targets
27. **Virtual Keyboard Settings** (`_insert_virtual_keyboard_settings`): Creates default keyboard theme
28. **Alternative Keyboard Themes** (`_insert_alternative_keyboard_themes`): Adds additional keyboard themes
29. **Campaigns** (`_insert_campaigns`): Creates sample promotional campaigns
30. **Loyalty Programs** (`_insert_loyalty`): Sets up loyalty program with tiers
31. **Customer Segments** (`_insert_customer_segments`): Creates default customer segments
32. **POS Settings** (`_insert_pos_settings`): Configures system-wide POS settings including device serial number (generated from MAC address and disk serial), operating system information, default country (United Kingdom), default currency (GBP), customer display settings (INTERNAL), barcode reader port (PS/2), backend connection settings (127.0.0.1:5000), and backend type (GATE)

## Function Details

### `_insert_admin_cashier(session)`
Creates the default administrator cashier account:
- Username: `admin`
- Password: `admin` (should be hashed in production)
- Name: Ferhat Mousavi
- Administrator privileges enabled
- Returns the created cashier object for use in other initialization functions

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

### `_insert_default_forms(session, cashier_id)`
Creates essential forms:
- **LOGIN**: Login screen with authentication fields
- **MAIN_MENU**: Main menu with navigation options
- Forms include layout, colors, and display settings

### `_insert_form_controls(session, cashier_id)`
Populates forms with controls:
- Buttons for navigation and actions
- Textboxes for input
- Labels for display
- Proper positioning and styling

### `_insert_virtual_keyboard_settings(session)`
Creates the default virtual keyboard theme:
- Size: 970x315 pixels
- Light gradient theme
- Font: Noto Sans CJK JP, 20px
- Button styling and colors

### `_insert_loyalty(session, admin_cashier_id)`
Sets up loyalty program:
- Default loyalty program with point earning rules
- Membership tiers (Bronze, Silver, Gold, Platinum)
- Tier benefits and point multipliers

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

---

[← Back to Table of Contents](README.md) | [Previous: Database Models Overview](10-database-models.md) | [Next: Troubleshooting →](12-troubleshooting.md)

