"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2026 Ferhat Mousavi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class SaleFlexError(Exception):
    """Root exception for all SaleFlex application errors."""


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------

class PaymentError(SaleFlexError):
    """Raised for any payment processing failure."""


class InvalidAmountError(PaymentError):
    """Raised when a payment amount is zero, negative, or malformed."""


class PaymentAlreadyCompleteError(PaymentError):
    """Raised when a payment is attempted on an already-completed document."""


# ---------------------------------------------------------------------------
# Fiscal / Hardware
# ---------------------------------------------------------------------------

class HardwareError(SaleFlexError):
    """Base class for hardware communication failures."""


class FiscalDeviceError(HardwareError):
    """Raised when the fiscal printer is unreachable or returns an error."""


class PrinterError(FiscalDeviceError):
    """Raised for print job failures (paper out, jam, etc.)."""


class CashDrawerError(HardwareError):
    """Raised when the cash drawer cannot be opened or queried."""


# ---------------------------------------------------------------------------
# External connectivity
# ---------------------------------------------------------------------------

class GATEConnectionError(SaleFlexError):
    """Raised when the payment gateway (GATE) is unreachable or rejects a request."""


# ---------------------------------------------------------------------------
# Tax / VAT
# ---------------------------------------------------------------------------

class TaxCalculationError(SaleFlexError):
    """Raised when VAT or tax calculation produces an invalid result."""


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

class DatabaseError(SaleFlexError):
    """Raised when a database operation fails unexpectedly."""


# ---------------------------------------------------------------------------
# Document / Transaction
# ---------------------------------------------------------------------------

class DocumentError(SaleFlexError):
    """Base class for document (transaction) lifecycle errors."""


class NoActiveDocumentError(DocumentError):
    """Raised when an operation requires an active document but none exists."""


class DocumentAlreadyClosedError(DocumentError):
    """Raised when an attempt is made to modify a closed document."""


# ---------------------------------------------------------------------------
# Configuration / Startup
# ---------------------------------------------------------------------------

class ConfigurationError(SaleFlexError):
    """Raised when required configuration values are missing or invalid."""


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class AuthenticationError(SaleFlexError):
    """Raised when login credentials are invalid or a session has expired."""
