# Data Caching Strategy

## Overview

SaleFlex.PyPOS implements an **in-memory caching strategy** to minimize disk I/O and improve performance, especially critical for POS devices with limited disk write cycles. All reference data models are loaded once at application startup and cached in memory throughout the session.

The caching system is divided into two main categories:
1. **POS Reference Data** (`pos_data`): System configuration and reference data
2. **Product Data** (`product_data`): Product-related models used in sales operations

## POS Reference Data Cache (`pos_data`)

The following reference data models are loaded into `pos_data` dictionary at startup:

- **Cashier**: User accounts for POS operators
- **CashierPerformanceMetrics**: Cashier performance metrics and statistics
- **CashierPerformanceTarget**: Cashier performance targets and goals
- **CashierTransactionMetrics**: Transaction-level performance metrics
- **CashierWorkBreak**: Cashier break records and tracking
- **CashierWorkSession**: Cashier work session records
- **City**: City master data
- **Country**: Country master data
- **CountryRegion**: Sub-country regions (states, provinces, special economic zones)
- **District**: District/region master data
- **Form**: Dynamic form definitions
- **FormControl**: Form controls (buttons, textboxes, etc.)
- **LabelValue**: Label/value pairs for translations
- **PaymentType**: Payment method definitions
- **PosSettings**: POS system-wide settings (also cached as `pos_settings` attribute)
- **PosVirtualKeyboard**: Virtual keyboard configurations
- **ReceiptFooter**: Receipt footer templates
- **ReceiptHeader**: Receipt header templates
- **Store**: Store/outlet information
- **Table**: Restaurant table management
- **TransactionDiscountType**: Transaction discount type definitions
- **TransactionDocumentType**: Transaction document type definitions
- **TransactionSequence**: Transaction sequence number generators

## Product Data Cache (`product_data`)

The following product-related models are loaded into `product_data` dictionary at startup:

- **Currency**: Currency master data (USD, EUR, GBP, etc.)
- **CurrencyTable**: Currency exchange rates with historical tracking
- **DepartmentMainGroup**: Main product category groups
- **DepartmentSubGroup**: Sub-categories within main groups
- **Product**: Product master data with pricing, stock, and descriptions
- **ProductAttribute**: Product attributes and specifications
- **ProductBarcode**: Barcode associations for products
- **ProductBarcodeMask**: Barcode format definitions
- **ProductManufacturer**: Manufacturer/brand information
- **ProductUnit**: Measurement units (PCS, KG, L, M, etc.)
- **ProductVariant**: Product variations (size, color, style)
- **Vat**: VAT/tax rate definitions
- **Warehouse**: Warehouse/depot definitions
- **WarehouseLocation**: Specific locations within warehouses
- **WarehouseProductStock**: Current stock levels per product per warehouse
- **WarehouseStockAdjustment**: Stock adjustment records
- **WarehouseStockMovement**: Stock movement history

## Implementation

### CurrentData Class

The `CurrentData` class manages both caching systems. The class uses a mixin pattern to organize functionality into focused components:

- **DocumentManager**: Handles document/transaction operations (create, load, complete, suspend)
- **CacheManager**: Manages POS and product data caching (populate, update, refresh)
- **ClosureManager**: Manages closure operations (load, create, close)

This modular structure improves code organization and maintainability while preserving all existing functionality through inheritance.

```python
# pos_data is populated at application startup
self.pos_data = {
    "Cashier": [...],
    "CashierPerformanceMetrics": [...],
    "CashierPerformanceTarget": [...],
    "CashierTransactionMetrics": [...],
    "CashierWorkBreak": [...],
    "CashierWorkSession": [...],
    "City": [...],
    "Country": [...],
    "District": [...],
    "Form": [...],
    "FormControl": [...],
    # ... other reference models
}

# product_data is populated at application startup
self.product_data = {
    "Currency": [...],
    "CurrencyTable": [...],
    "Product": [...],
    "ProductBarcode": [...],
    "DepartmentMainGroup": [...],
    "Vat": [...],
    # ... other product models
}

# Special cached references
self.pos_settings = pos_data["PosSettings"][0]  # First PosSettings record
self.current_currency = "GBP"  # Loaded from PosSettings

# Current active closure (session data, not cached reference data)
self.closure = {
    "closure": Closure instance,
    "cashier_summaries": [...],
    "country_specific": ClosureCountrySpecific or None,
    "currencies": [...],
    "department_summaries": [...],
    "discount_summaries": [...],
    "document_type_summaries": [...],
    "payment_type_summaries": [...],
    "tip_summaries": [...],
    "vat_summaries": [...]
}
```

### Accessing Cached Data

**POS Reference Data:**
```python
# Access cashier list from cache
cashiers = self.pos_data.get("Cashier", [])

# Find specific cashier
cashier = next((c for c in cashiers if c.user_name == "admin"), None)

# Access PosSettings (cached reference)
settings = self.pos_settings

# Access forms
forms = self.pos_data.get("Form", [])
```

**Product Data:**
```python
# Access currency list from cache
currencies = self.product_data.get("Currency", [])

# Find currency by sign (used in sale operations)
currency = next((c for c in currencies 
                 if c.sign == "GBP" 
                 and not (hasattr(c, 'is_deleted') and c.is_deleted)), None)

# Access product list from cache
products = self.product_data.get("Product", [])

# Find product by code (used in sale operations)
product = next((p for p in products 
                if p.code == "PROD001" 
                and not (hasattr(p, 'is_deleted') and p.is_deleted)), None)

# Access product barcodes
barcodes = self.product_data.get("ProductBarcode", [])

# Find barcode record
barcode = next((b for b in barcodes 
                if b.barcode == "1234567890123"
                and not (hasattr(b, 'is_deleted') and b.is_deleted)), None)

# Access departments
departments = self.product_data.get("DepartmentMainGroup", [])

# Access VAT rates
vat_rates = self.product_data.get("Vat", [])
```

### Cache Synchronization

When reference data is modified, the cache must be updated:

**POS Reference Data:**
```python
# After creating/updating a cashier
cashier.save()
self.update_pos_data_cache(cashier)

# To refresh entire model from database
self.refresh_pos_data_model(Cashier)
```

**Product Data:**
```python
# After creating/updating a product
product.save()
self.update_product_data_cache(product)

# To refresh entire model from database
self.refresh_product_data_model(Product)
```

## Benefits

1. **Reduced Disk I/O**: Reference data loaded once at startup, no repeated database reads
2. **Improved Performance**: In-memory lookups are significantly faster than database queries
3. **Extended Disk Life**: Critical for POS devices with limited disk write cycles
4. **Consistent Data**: All components access the same cached data
5. **Automatic Synchronization**: Cache updates when data is modified

## Performance Optimizations

**Login Operations:**
Login operations are optimized to use cached data:

```python
# Login uses pos_data cache instead of database queries
all_cashiers = self.pos_data.get("Cashier", [])
cashiers = [c for c in all_cashiers 
            if c.user_name == username 
            and c.password == password 
            and not c.is_deleted]
```

This eliminates database reads during authentication, improving login performance.

**Sale Operations:**
All product lookups in sale operations use `product_data` cache:

```python
# Currency lookup (for decimal places calculation)
currencies = [c for c in self.product_data.get("Currency", [])
              if c.sign == currency_sign 
              and not (hasattr(c, 'is_deleted') and c.is_deleted)]

# Product lookup by code (SALE_PLU_CODE)
products = [p for p in self.product_data.get("Product", [])
            if p.code == product_code 
            and not (hasattr(p, 'is_deleted') and p.is_deleted)]

# Barcode lookup (SALE_PLU_BARCODE)
barcodes = [b for b in self.product_data.get("ProductBarcode", [])
            if b.barcode == barcode
            and not (hasattr(b, 'is_deleted') and b.is_deleted)]
```

**Quantity Input from NumPad:**

When using `SALE_PLU_CODE` or `SALE_PLU_BARCODE` functions, the system automatically reads quantity from the NumPad if available:

```python
# In _sale_plu_code() or _sale_plu_barcode() methods:
# 1. Check NumPad for quantity input
numpad = current_window.findChildren(NumPad)[0] if current_window.findChildren(NumPad) else None
if numpad:
    numpad_text = numpad.get_text()
    if numpad_text and numpad_text.strip():
        quantity = float(numpad_text)  # Use NumPad value as quantity
    # NumPad is automatically cleared after use
```

**Benefits:**
- Fast quantity entry without separate quantity input step
- Improved user experience for bulk sales
- Automatic NumPad cleanup prevents accidental re-use

# Department lookup (SALE_DEPARTMENT)
departments = [d for d in self.product_data.get("DepartmentMainGroup", [])
               if d.code == department_code
               and not (hasattr(d, 'is_deleted') and d.is_deleted)]

# VAT rate lookup
vat_rates = [v for v in self.product_data.get("Vat", [])
             if v.code == vat_code
             and not (hasattr(v, 'is_deleted') and v.is_deleted)]
```

**Button Rendering:**
Button text loading in sale forms uses `product_data` cache instead of database queries, significantly improving form rendering speed.

## Cache Population

Both caches are populated during application initialization:

```python
# In Application.__init__()
# Load POS reference data
self.populate_pos_data(progress_callback=about.update_message)

# Load product data
self.populate_product_data(progress_callback=about.update_message)
```

These methods load all models from the database once and store them in their respective dictionaries (`pos_data` and `product_data`).

## Closure Management

The `CurrentData` class (via `ClosureManager` mixin) manages the current active closure through the `closure` attribute. Unlike `pos_data` and `product_data` which cache reference data, `closure` holds session-specific closure data that is actively updated during operations.

**Closure Lifecycle:**
1. **Application Startup**: The system loads the last open closure (where `closure_end_time` is None) or creates a new empty closure if none exists
2. **During Operations**: Closure data is updated in memory as transactions occur
3. **Closure Completion**: When a closure is closed, `closure_end_time` is set, all data is saved to the database, and a new empty closure is automatically created

**Closure Structure:**
```python
# Access current closure
closure = self.closure["closure"]  # Main Closure record

# Access summaries
cashier_summaries = self.closure["cashier_summaries"]
currencies = self.closure["currencies"]
department_summaries = self.closure["department_summaries"]
# ... etc
```

**Closure Methods:**
- `load_open_closure()`: Loads the last open closure from database or creates empty one
- `create_empty_closure()`: Creates a new empty closure with all summary structures initialized
- `close_closure()`: Closes current closure, saves to database, and creates new empty closure

**Usage Example:**
```python
# Closure is automatically loaded at application startup
# Access current closure data
if self.closure and self.closure.get("closure"):
    closure = self.closure["closure"]
    print(f"Current closure: {closure.closure_unique_id}")
    print(f"Start time: {closure.closure_start_time}")
    print(f"End time: {closure.closure_end_time}")  # None if open

# Close current closure
self.close_closure(
    closing_cash_amount=1500.00,
    description="End of day closure"
)
```

---

[← Back to Table of Contents](README.md) | [Previous: Virtual Keyboard Configuration](07-virtual-keyboard.md) | [Next: Document Management System →](09-document-management.md)

