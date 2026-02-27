"""
SaleFlex.PyPOS - Core utilities (logging, exceptions, etc.)
"""

from core.logger import get_logger
from core.exceptions import (
    SaleFlexError,
    PaymentError,
    InvalidAmountError,
    PaymentAlreadyCompleteError,
    HardwareError,
    FiscalDeviceError,
    PrinterError,
    CashDrawerError,
    GATEConnectionError,
    TaxCalculationError,
    DatabaseError,
    DocumentError,
    NoActiveDocumentError,
    DocumentAlreadyClosedError,
    ConfigurationError,
    AuthenticationError,
)

__all__ = [
    "get_logger",
    "SaleFlexError",
    "PaymentError",
    "InvalidAmountError",
    "PaymentAlreadyCompleteError",
    "HardwareError",
    "FiscalDeviceError",
    "PrinterError",
    "CashDrawerError",
    "GATEConnectionError",
    "TaxCalculationError",
    "DatabaseError",
    "DocumentError",
    "NoActiveDocumentError",
    "DocumentAlreadyClosedError",
    "ConfigurationError",
    "AuthenticationError",
]
