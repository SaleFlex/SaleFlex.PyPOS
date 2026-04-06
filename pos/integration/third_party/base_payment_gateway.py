"""
SaleFlex.PyPOS - Abstract base class for third-party payment gateways.

Concrete adapters in adapters/payment/ inherit this class and implement
all abstract methods for their specific payment provider (iyzico, PayTR,
Stripe, Nets, custom terminal APIs, etc.).

Activated when gate.manages_payment = false AND
third_party.payment.enabled = true in settings.toml.

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

from __future__ import annotations

from decimal import Decimal
from typing import Dict, Any, Optional

from pos.integration.external_device import ExternalDevice
from core.logger import get_logger

logger = get_logger(__name__)


class BasePaymentGateway(ExternalDevice):
    """
    Abstract payment gateway connector.

    All concrete payment adapters (iyzico, PayTR, Stripe, Nets, custom) must
    inherit this class and implement the methods below.  The POS payment flow
    calls these methods through the IntegrationMixin without knowing which
    provider is active.
    """

    # ------------------------------------------------------------------
    # Payment operations  (override in concrete adapters)
    # ------------------------------------------------------------------

    def initiate_payment(
        self,
        amount: Decimal,
        currency_code: str,
        transaction_ref: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Initiate a payment transaction with the gateway.

        Args:
            amount:          Payment amount (always positive).
            currency_code:   ISO 4217 currency code (e.g. "TRY", "USD").
            transaction_ref: Local transaction identifier for correlation.
            metadata:        Optional additional data for the gateway.

        Returns:
            Dict with at minimum:
            {"success": bool, "gateway_ref": str, "message": str}
        """
        logger.info("[%s] initiate_payment (stub) amount=%s ref=%s",
                    self.logical_name, amount, transaction_ref)
        return {"success": False, "gateway_ref": "", "message": "stub"}

    def confirm_payment(self, gateway_ref: str) -> Dict[str, Any]:
        """
        Confirm / capture a previously initiated payment.

        Args:
            gateway_ref: Gateway reference returned by initiate_payment().

        Returns:
            Dict with at minimum:
            {"success": bool, "status": str, "message": str}
        """
        logger.info("[%s] confirm_payment (stub) gateway_ref=%s",
                    self.logical_name, gateway_ref)
        return {"success": False, "status": "stub", "message": "stub"}

    def void_payment(self, gateway_ref: str) -> bool:
        """
        Void / cancel a payment that has not yet been captured.

        Args:
            gateway_ref: Gateway reference returned by initiate_payment().

        Returns:
            True on success, False on failure.
        """
        logger.info("[%s] void_payment (stub) gateway_ref=%s",
                    self.logical_name, gateway_ref)
        return False

    def refund_payment(self, gateway_ref: str, amount: Decimal) -> bool:
        """
        Refund a previously captured payment.

        Args:
            gateway_ref: Gateway reference of the original payment.
            amount:      Amount to refund (must be <= original amount).

        Returns:
            True on success, False on failure.
        """
        logger.info("[%s] refund_payment (stub) gateway_ref=%s amount=%s",
                    self.logical_name, gateway_ref, amount)
        return False
