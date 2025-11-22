# Database Models Overview

SaleFlex.PyPOS uses a comprehensive database schema with over 80 models organized into logical categories. All models inherit from base classes that provide CRUD operations, audit trails, and soft delete functionality.

## Core System Models

### User and Store Management
- **Cashier**: User accounts for POS operators with authentication, permissions, and personal information
- **Store**: Store/outlet information including address, contact details, manager and technician information, and business details. Note: Hardware configuration and POS system settings are managed through the `PosSettings` model, not the Store model.
- **Table**: Restaurant table management for table service operations

### Location and Geography
- **Country**: Country master data with ISO 3166-1 compliant fields (`iso_alpha2`, `iso_alpha3`, `iso_numeric`) for standardized country identification
- **CountryRegion**: Sub-country regions (states, provinces, special economic zones) with ISO 3166-2 codes (`iso_3166_2` field). Supports region-specific closure templates and compliance tracking. Pre-populated with 80+ regions (US states, Canadian provinces, German states, French regions)
- **City**: City master data linked to countries
- **District**: District/region master data linked to cities

### Currency and Payment
- **Currency**: Currency master data (USD, EUR, GBP, etc.)
- **CurrencyTable**: Currency exchange rates with historical tracking
- **PaymentType**: Payment method definitions (Cash, Card, Mobile Payment, etc.)
- **ClosureCurrency**: End-of-day currency reconciliation

## Product Management Models

### Product Core
- **Product**: Main product catalog with pricing, stock, descriptions, and product attributes
- **ProductVariant**: Product variations (size, color, style) linked to base products
- **ProductAttribute**: Product attributes and specifications (dimensions, weight, materials, etc.)
- **ProductBarcode**: Barcode associations for products (EAN, UPC, custom barcodes)
- **ProductBarcodeMask**: Barcode format definitions and validation rules
- **ProductUnit**: Measurement units (PCS, KG, L, M, etc.)
- **ProductManufacturer**: Manufacturer/brand information

### Product Organization
- **DepartmentMainGroup**: Main product category groups
- **DepartmentSubGroup**: Sub-categories within main groups

## Transaction Models

### Transaction Headers
- **TransactionHead**: Main transaction record with customer, date, totals, and status
- **TransactionHeadTemp**: Temporary transaction header during transaction processing
- **TransactionSequence**: Transaction numbering sequences per document type
- **TransactionDocumentType**: Document type definitions (Sale, Return, Refund, etc.)
- **TransactionLog**: Transaction audit log for all transaction events

### Transaction Details
- **TransactionProduct**: Line items in transactions (products sold)
- **TransactionProductTemp**: Temporary transaction line items
- **TransactionPayment**: Payment records for transactions
- **TransactionPaymentTemp**: Temporary payment records
- **TransactionChange**: Change records for overpayments
- **TransactionChangeTemp**: Temporary change records
- **TransactionTax**: Tax calculations per transaction
- **TransactionTaxTemp**: Temporary tax calculations
- **TransactionDiscountType**: Discount type definitions (NONE, PERSONAL, MANAGER, CUSTOMER_SATISFACTION, PRODUCT)
- **TransactionDiscount**: Discounts applied to transactions (linked to TransactionDiscountType via foreign key)
- **TransactionDiscountTemp**: Temporary discount records
- **TransactionSurcharge**: Surcharges applied to transactions
- **TransactionSurchargeTemp**: Temporary surcharge records
- **TransactionTip**: Tip/gratuity records
- **TransactionTipTemp**: Temporary tip records
- **TransactionDepartment**: Department totals summary for department-based sales
- **TransactionDepartmentTemp**: Temporary department totals

### Transaction Extensions
- **TransactionDelivery**: Delivery information for transactions
- **TransactionDeliveryTemp**: Temporary delivery records
- **TransactionNote**: Notes and comments on transactions
- **TransactionNoteTemp**: Temporary notes
- **TransactionRefund**: Refund transaction records
- **TransactionRefundTemp**: Temporary refund records
- **TransactionVoid**: Voided transaction records
- **TransactionFiscal**: Fiscal printer records (for compliance)
- **TransactionFiscalTemp**: Temporary fiscal records
- **TransactionKitchenOrder**: Kitchen display system orders
- **TransactionKitchenOrderTemp**: Temporary kitchen orders
- **TransactionLoyalty**: Loyalty points earned/redeemed in transactions
- **TransactionLoyaltyTemp**: Temporary loyalty records

## Warehouse Management Models

- **Warehouse**: Warehouse/depot definitions with location, capacity, and environmental settings
- **WarehouseLocation**: Specific locations within warehouses (aisles, shelves, bins)
- **WarehouseProductStock**: Current stock levels per product per warehouse location
- **WarehouseStockMovement**: Stock movement history (receipts, transfers, adjustments)
- **WarehouseStockAdjustment**: Stock adjustment records with reasons and approvals

## Customer Management Models

- **Customer**: Customer master data with contact information, preferences, and consent management
- **CustomerSegment**: Customer segmentation definitions (VIP, New, Frequent, etc.)
- **CustomerSegmentMember**: Customer membership in segments

## Campaign and Promotion Models

- **CampaignType**: Campaign type definitions (Product Discount, Basket Discount, etc.)
- **Campaign**: Promotional campaigns with rules, dates, and conditions
- **CampaignRule**: Detailed campaign rules (product filters, time restrictions, etc.)
- **CampaignProduct**: Products eligible for campaigns
- **CampaignUsage**: Campaign usage tracking per customer/transaction
- **Coupon**: Coupon/voucher definitions with barcode/QR code support
- **CouponUsage**: Coupon redemption tracking

## Loyalty Program Models

- **LoyaltyProgram**: Loyalty program definitions with point earning rules
- **LoyaltyTier**: Membership tiers (Bronze, Silver, Gold, Platinum) with benefits
- **CustomerLoyalty**: Customer loyalty account with current points and tier
- **LoyaltyPointTransaction**: Point transaction history (earned, redeemed, expired)

## Cashier Performance Models

- **CashierWorkSession**: Cashier work shift sessions with start/end times
- **CashierWorkBreak**: Break records during work sessions
- **CashierPerformanceMetrics**: Performance metrics per cashier (sales, transactions, etc.)
- **CashierPerformanceTarget**: Performance targets and goals for cashiers
- **CashierTransactionMetrics**: Detailed transaction metrics per cashier

## Closure and End-of-Day Models

- **Closure**: End-of-day closure records with cash reconciliation and high-level totals. The `closure_end_time` field is nullable (None for open closures), allowing the system to track active closures until they are closed.
- **ClosureCashierSummary**: Cashier performance tracking per closure (transactions, sales, voids, hours worked)
- **ClosureCurrency**: Currency breakdown for multi-currency operations with exchange rates
- **ClosureDepartmentSummary**: Department/category breakdown with gross, net, tax, and discount amounts
- **ClosureDiscountSummary**: Discount breakdown by type with count, amount, and affected amount
- **ClosureDocumentTypeSummary**: Document type tracking (receipt, invoice, etc.) with valid and canceled counts
- **ClosurePaymentTypeSummary**: Payment method breakdown per closure
- **ClosureTipSummary**: Tip tracking by payment method with distribution tracking (for restaurants)
- **ClosureVATSummary**: Tax rate breakdown with taxable amounts, tax amounts, and exemptions
- **ClosureCountrySpecific**: Country-specific closure data stored as JSON with template-based initialization. Supports all countries without creating separate models. Templates are stored in `static_files/closures/` directory and can be loaded automatically based on country code and optional region code. Linked to `CountryRegion` model via `fk_region_id` for region-specific closures (e.g., `usa_ca.json` for California). See [Country-Specific Closure Templates](#country-specific-closure-templates) section below for details.

## Form and UI Models

- **Form**: Dynamic form definitions with layout, colors, and display settings
- **FormControl**: Form controls (buttons, textboxes, comboboxes) with positioning and behavior
- **PosVirtualKeyboard**: Virtual keyboard theme and configuration settings
- **PosSettings**: POS system-wide settings and configuration including device information (serial number, OS), backend connection settings (IP/port), display configuration, hardware port settings, and working currency (`fk_working_currency_id`) for multi-currency operations
- **ReceiptHeader**: Receipt header templates
- **ReceiptFooter**: Receipt footer templates
- **LabelValue**: Label/value pairs for translations and configuration

## Country Region Model

The `CountryRegion` model tracks sub-country regions (states, provinces, special economic zones) that have different tax rates, regulations, or compliance requirements. This enables region-specific closure templates and better compliance tracking.

### Features
- **Region Types**: Supports states, provinces, territories, regions, districts, free zones, and special economic zones
- **ISO 3166-2 Codes**: Each region includes ISO 3166-2 code in `iso_3166_2` field (e.g., US-CA, CA-ON, DE-BY)
- **Standardized Fields**: Uses ISO-compliant field names (`iso_3166_2` for full code, `region_code` for subdivision code, `name` for region name)
- **Special Requirements Flag**: Marks regions with special tax/compliance requirements
- **Metadata Support**: JSON field for storing additional region-specific data (tax rates, time zones, etc.)
- **Template Integration**: Region codes are used for template file naming (e.g., `usa_ca.json`)

### Pre-populated Regions
- **United States**: 50 states + DC (80+ regions total)
- **Canada**: 10 provinces + 3 territories
- **Germany**: 16 states (Länder)
- **France**: 13 regions

### Usage Example

```python
from data_layer.model.definition.country_region import CountryRegion

# Get California region
california = session.query(CountryRegion).filter_by(
    region_code='CA',
    fk_country_id=usa_id
).first()

# Use in closure
closure = ClosureCountrySpecific.create_from_template(
    fk_closure_id=closure_id,
    country_code='US',
    fk_region_id=california.id  # Automatically loads usa_ca.json template
)
```

## Country-Specific Closure Templates

SaleFlex.PyPOS supports country-specific closure data through a flexible template system. Instead of creating separate models for each country, closure data is stored as JSON in the `ClosureCountrySpecific` model, with templates defining the structure for each country. Regions are tracked via the `CountryRegion` model for region-specific templates.

### Template System Overview

- **Location**: Templates are stored in `static_files/closures/` directory
- **Naming Convention**: 
  - Country-level: `{country_code}.json` (e.g., `tr.json`, `usa.json`)
  - Region-level: `{country_code}_{region_code}.json` (e.g., `usa_ca.json`, `usa_ny.json`, `ca_on.json`)
  - Default fallback: `default.json`
- **Template Resolution**: System tries region-specific → country-specific → default template
- **Auto-initialization**: Templates can be automatically loaded when creating closure records
- **Region Support**: Uses `CountryRegion` model for region-specific templates. Region codes are automatically resolved from `fk_region_id` or can be provided directly via `region_code` parameter

### Available Templates

- **tr.json**: Turkey (E-Fatura, E-İrsaliye, Diplomatic invoices, Tourist tax-free)
- **usa.json**: United States (general)
- **usa_ca.json**: California, USA (state tax, tip reporting, gift cards)
- **usa_ny.json**: New York, USA
- **usa_tx.json**: Texas, USA
- **de.json**: Germany (VAT by rate, reverse charge, EU sales)
- **fr.json**: France (VAT rates, EU sales)
- **gb.json**: United Kingdom (VAT rates)
- **jp.json**: Japan (Consumption tax, point programs)

### Usage Example

```python
from data_layer.model.definition.closure_country_specific import ClosureCountrySpecific

# Create closure with template automatically loaded
closure = ClosureCountrySpecific.create_from_template(
    fk_closure_id=closure_id,
    country_code='TR',
    region_code=None  # Optional, for region-specific templates (e.g., 'CA' for California)
)

# Or using CountryRegion foreign key
region = session.query(CountryRegion).filter_by(region_code='CA', fk_country_id=usa_id).first()
closure = ClosureCountrySpecific.create_from_template(
    fk_closure_id=closure_id,
    country_code='US',
    fk_region_id=region.id  # Automatically resolves region_code='CA'
)

# Access country-specific data
data = closure.get_country_data()
e_invoice_count = closure.get_field('electronic_invoice_count', 0)
```

### GATE Integration

When connected to SaleFlex.GATE, templates can be:
- Downloaded from GATE for centralized management
- Updated remotely without POS code changes
- Validated before deployment

For more details, see `static_files/closures/README.md`.

## Tax and Compliance Models

- **Vat**: VAT/tax rate definitions with percentages and effective dates. The `rate` field uses `Numeric(precision=5, scale=2)` to support decimal VAT rates (e.g., 0.00, 5.00, 20.00)

## Model Features

All models include:
- **UUID Primary Keys**: Unique identifiers for all records
- **Audit Fields**: Created/updated timestamps and user tracking
- **Soft Delete**: Records are marked as deleted rather than physically removed
- **CRUD Operations**: Standard create, read, update, delete methods
- **Server Synchronization**: Support for multi-store synchronization via `fk_server_id`

---

[← Back to Table of Contents](README.md) | [Previous: Document Management System](09-document-management.md) | [Next: Database Initialization Functions →](11-database-initialization.md)

