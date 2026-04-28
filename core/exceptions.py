"""
SaleFlex.PyPOS - Point of Sale Application
Copyright (C) 2025-2026 Mousavi.Tech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
# External connectivity — SaleFlex.GATE
# ---------------------------------------------------------------------------

class GATEConnectionError(SaleFlexError):
    """Raised when SaleFlex.GATE is unreachable or rejects a connection."""


class GATEAuthError(GATEConnectionError):
    """Raised when the GATE API token is missing, invalid, or expired."""


class GATESyncError(GATEConnectionError):
    """Raised when a push or pull operation against GATE fails after all retries."""


class GATENotificationError(GATEConnectionError):
    """Raised when the notification polling request against GATE fails."""


# ---------------------------------------------------------------------------
# External connectivity — Third-party integrations
# ---------------------------------------------------------------------------

class ThirdPartyIntegrationError(SaleFlexError):
    """Base class for direct third-party connector failures."""


class ERPConnectionError(ThirdPartyIntegrationError):
    """Raised when a direct ERP connector cannot reach the ERP system."""


class ERPSyncError(ERPConnectionError):
    """Raised when an ERP data push or pull operation fails."""


class ThirdPartyPaymentError(ThirdPartyIntegrationError):
    """Raised when a direct payment gateway connector returns an error."""


class ThirdPartyCampaignError(ThirdPartyIntegrationError):
    """Raised when a direct campaign module connector returns an error."""


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
