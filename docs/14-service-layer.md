# Service Layer Architecture

## Overview

SaleFlex.PyPOS implements a **service layer pattern** to separate business logic from event handlers and UI components. This architecture improves code organization, reusability, and testability by centralizing business operations in dedicated service classes.

The service layer is located in the `pos/service/` directory and contains business logic services that handle core POS operations such as VAT calculations, sale processing, and transaction management.

## Service Layer Structure

```
pos/service/
├── __init__.py          # Service layer exports
├── vat_service.py       # VAT calculation service
└── sale_service.py      # Sale processing service
```

## Available Services

### VatService

The `VatService` provides centralized VAT (Value Added Tax) calculation functionality with currency-aware rounding.

#### Key Features

- **Centralized VAT Calculation**: All VAT calculations use the standard formula: `vat_amount = price * (vat_rate / (100 + vat_rate))`
- **Currency-Aware Rounding**: Automatically rounds VAT amounts based on the currency's `decimal_places` setting
- **Custom Rounding Rules**: 
  - If the digit after `decimal_places` is 5 or greater, round up
  - If the digit after `decimal_places` is less than 5, round down
  - Examples: `1.12345 → 1.12`, `1.34567 → 1.35`, `1.56789 → 1.57`

#### Usage Examples

```python
from pos.service import VatService

# Calculate VAT with currency-aware rounding
vat_amount = VatService.calculate_vat(
    price=100.0,
    vat_rate=18.0,  # 18% VAT
    currency_sign="GBP",  # Uses GBP's decimal_places (typically 2)
    product_data=product_data  # Optional: cached product data
)

# Calculate VAT with explicit decimal places
vat_amount = VatService.calculate_vat_with_decimal_places(
    price=100.0,
    vat_rate=18.0,
    decimal_places=2
)

# Get currency decimal places
decimal_places = VatService.get_currency_decimal_places(
    currency_sign="GBP",
    product_data=product_data  # Optional: cached product data
)

# Round value according to currency rules
rounded_value = VatService.round_by_currency(
    value=1.34567,
    decimal_places=2
)
```

#### Methods

- **`calculate_vat(price, vat_rate, currency_sign=None, product_data=None)`**: Calculate VAT amount with currency-aware rounding
- **`calculate_vat_with_decimal_places(price, vat_rate, decimal_places)`**: Calculate VAT with explicit decimal places
- **`get_currency_decimal_places(currency_sign, product_data=None)`**: Get decimal places for a currency (default: 2)
- **`round_by_currency(value, decimal_places)`**: Round a value according to currency rounding rules

### SaleService

The `SaleService` provides business logic for processing sales including PLU (code/barcode) sales and department sales.

#### Key Features

- **PLU Sale Calculations**: Handles product sales by code or barcode
- **Department Sale Calculations**: Handles department-based sales
- **VAT Integration**: Uses `VatService` for all VAT calculations
- **Transaction Model Creation**: Creates transaction temp models with proper field mapping

#### Usage Examples

```python
from pos.service import SaleService

# Calculate PLU sale (code or barcode)
sale_calc = SaleService.calculate_plu_sale(
    quantity=2.0,
    unit_price=10.0,
    product=product_object,
    product_data=product_data,
    currency_sign="GBP"
)
# Returns: {
#     "total_price": 20.0,
#     "vat_rate": 18.0,
#     "total_vat": 3.05,  # Rounded according to currency
#     "dept_main_group_id": uuid,
#     "dept_sub_group_id": uuid
# }

# Calculate department sale
dept_calc = SaleService.calculate_department_sale(
    quantity=1.0,
    unit_price=50.0,
    department=department_object,
    department_no=101,
    product_data=product_data,
    currency_sign="GBP"
)
# Returns: {
#     "total_department": 50.0,
#     "vat_rate": 18.0,
#     "total_department_vat": 7.63,  # Rounded
#     "dept_main_group": DepartmentMainGroup object,
#     "dept_sub_group": DepartmentSubGroup object or None
# }

# Create TransactionProductTemp
product_temp = SaleService.create_transaction_product_temp(
    head_id=transaction_head_id,
    line_no=1,
    product=product_object,
    quantity=2.0,
    unit_price=10.0,
    total_price=20.0,
    vat_rate=18.0,
    total_vat=3.05,
    product_barcode=barcode_object  # Optional
)

# Create TransactionDepartmentTemp
dept_temp = SaleService.create_transaction_department_temp(
    head_id=transaction_head_id,
    line_no=1,
    dept_main_group=main_group_object,
    dept_sub_group=sub_group_object,  # Optional
    total_department=50.0,
    vat_rate=18.0,
    total_department_vat=7.63,
    department_no=101,  # Optional
    product_data=product_data  # Optional
)

# Calculate document totals
totals = SaleService.calculate_document_totals(document_data)
# Returns: {
#     "total_amount": Decimal('100.00'),
#     "total_vat_amount": Decimal('15.25')
# }
```

#### Methods

- **`calculate_plu_sale(quantity, unit_price, product, product_data, currency_sign=None)`**: Calculate PLU sale totals and VAT
- **`calculate_department_sale(quantity, unit_price, department, department_no, product_data, currency_sign=None)`**: Calculate department sale totals and VAT
- **`create_transaction_product_temp(...)`**: Create a TransactionProductTemp record
- **`create_transaction_department_temp(...)`**: Create a TransactionDepartmentTemp record
- **`calculate_document_totals(document_data)`**: Calculate total amounts for a document
- **`get_vat_rate_for_product(product, product_data)`**: Get VAT rate for a product
- **`get_vat_rate_for_department(department, department_no, product_data)`**: Get VAT rate for a department

## Integration with Event Handlers

Event handlers in `pos/manager/event/` use services to perform business operations:

```python
# In sale.py event handler
from pos.service import SaleService

def _update_document_data_for_sale(self, sale_type, ...):
    # Use SaleService for calculations
    sale_calc = SaleService.calculate_plu_sale(
        quantity=quantity,
        unit_price=unit_price,
        product=product,
        product_data=self.product_data,
        currency_sign=self.current_currency
    )
    
    # Create transaction model
    product_temp = SaleService.create_transaction_product_temp(...)
    
    # Calculate totals
    totals = SaleService.calculate_document_totals(self.document_data)
```

## Benefits of Service Layer

1. **Separation of Concerns**: Business logic is separated from UI and event handling
2. **Reusability**: Services can be used across multiple event handlers and components
3. **Testability**: Services can be unit tested independently
4. **Maintainability**: Changes to business logic are centralized in service classes
5. **Consistency**: All VAT calculations and sale operations use the same logic
6. **Currency Awareness**: Automatic currency-based rounding ensures accurate calculations

## Best Practices

1. **Always use services for business logic**: Don't duplicate calculation logic in event handlers
2. **Pass product_data cache**: Services can use cached data for better performance
3. **Use currency_sign**: Always pass currency sign for accurate rounding
4. **Handle errors**: Services return safe defaults (e.g., 0.0 for VAT if rate is 0)

## Future Services

Additional services may be added for:
- Payment processing
- Discount calculations
- Inventory management
- Customer management
- Reporting and analytics

---

**Last Updated:** 2025-01-27  
**Version:** 1.0.0b2

