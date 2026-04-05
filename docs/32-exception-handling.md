# Centralized Exception Handling

SaleFlex.PyPOS uses a **centralized exception hierarchy** located at `core/exceptions.py` so that every layer of the application raises typed, meaningful errors instead of bare `Exception` or built-in types.  
All custom exceptions inherit from `SaleFlexError`, making it easy to catch all application-level errors with a single `except SaleFlexError` clause or to catch only a specific domain.

## Exception Hierarchy

```
SaleFlexError                          ← Root base class
│
├── PaymentError                       ← Payment processing failures
│   ├── InvalidAmountError             ← Zero, negative, or malformed amount
│   └── PaymentAlreadyCompleteError    ← Document already fully paid
│
├── HardwareError                      ← Hardware communication failures
│   ├── FiscalDeviceError              ← Fiscal printer unreachable / error response
│   │   └── PrinterError              ← Print job failure (paper out, jam, etc.)
│   └── CashDrawerError               ← Cash drawer cannot be opened or queried
│
├── GATEConnectionError                ← Payment gateway unreachable / request rejected
│
├── TaxCalculationError                ← VAT / tax calculation produces invalid result
│
├── DatabaseError                      ← Unexpected database operation failure
│
├── DocumentError                      ← Transaction / document lifecycle errors
│   ├── NoActiveDocumentError          ← Operation requires a document but none exists
│   └── DocumentAlreadyClosedError     ← Attempt to modify a closed document
│
├── ConfigurationError                 ← Missing or invalid configuration values
│
└── AuthenticationError                ← Invalid credentials or expired session
```

## File Location

```
core/
└── exceptions.py    ← entire exception hierarchy lives here
```

## Usage

### Importing

```python
from core.exceptions import (
    SaleFlexError,
    PaymentError,
    InvalidAmountError,
    TaxCalculationError,
    DatabaseError,
    FiscalDeviceError,
    GATEConnectionError,
    DocumentError,
    ConfigurationError,
    AuthenticationError,
)
```

### Raising a domain-specific exception

```python
from core.exceptions import InvalidAmountError

def calculate_payment_amount(button_name: str, ...) -> Decimal:
    try:
        amount_value = int(button_name[4:])
    except (ValueError, IndexError):
        raise InvalidAmountError(f"Invalid CASH button name format: {button_name}")
```

### Chaining with the original cause (`raise ... from e`)

Always use `raise NewError(...) from e` when wrapping a lower-level exception.  
This preserves the full traceback for debugging.

```python
from core.exceptions import DatabaseError
from sqlalchemy.exc import SQLAlchemyError

try:
    session.commit()
except SQLAlchemyError as e:
    logger.error("Save operation error: %s", e)
    raise DatabaseError(f"Save operation failed: {e}") from e
```

### Catching only application errors

```python
from core.exceptions import SaleFlexError

try:
    result = some_pos_operation()
except SaleFlexError as e:
    logger.error("POS operation failed: %s", e)
    show_user_message(str(e))
```

### Catching a specific domain

```python
from core.exceptions import TaxCalculationError

try:
    vat = VatService.calculate_vat(price, vat_rate)
except TaxCalculationError as e:
    logger.warning("VAT fallback to 0.0: %s", e)
    vat = 0.0
```

## Where Exceptions Are Used

| Module | Exception(s) |
|--------|-------------|
| `pos/service/payment_service.py` | `PaymentError`, `InvalidAmountError` |
| `pos/service/vat_service.py` | `TaxCalculationError` |
| `data_layer/model/crud_model.py` | `DatabaseError` (wraps `SQLAlchemyError`) |
| `pos/manager/event/hardware.py` | `CashDrawerError`, `FiscalDeviceError` |

## Design Guidelines

- **Always chain** — use `raise NewError(...) from original_exception` so the original traceback is never lost.
- **Log before raising** — call `logger.error(...)` before raising from a low-level handler so the error is recorded even if the caller silently handles it.
- **Prefer specific subtypes** — raise `InvalidAmountError` rather than the parent `PaymentError` when the more specific type applies.
- **Never catch `SaleFlexError` silently** — if you catch an application exception, either re-raise it, log it, or surface it to the user.

---

**See also:** [Central Logging](16-logging.md) | [Service Layer Architecture](14-service-layer.md) | [Troubleshooting](12-troubleshooting.md)

---

[← Back to Table of Contents](README.md) | [Previous: Central Logging](31-logging.md) | [Next: Database Initialization →](33-database-initialization.md)
