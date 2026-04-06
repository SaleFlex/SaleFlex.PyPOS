"""
SaleFlex.PyPOS - Custom payment gateway adapter (template).

Copy and rename this file to implement a specific payment provider
(e.g. iyzico_gateway.py, paytr_gateway.py, stripe_gateway.py).

Set third_party.payment.type = "custom" (or your chosen name) in settings.toml
and register the class in IntegrationMixin._build_payment_gateway().

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

from core.exceptions import ThirdPartyPaymentError
from core.logger import get_logger
from pos.integration.third_party.base_payment_gateway import BasePaymentGateway

logger = get_logger(__name__)


class CustomPaymentGateway(BasePaymentGateway):
    """
    Template payment gateway adapter.

    Replace the stub implementations with the provider's SDK or REST API calls.
    Raise ThirdPartyPaymentError (not bare Exception) on unrecoverable failures.
    """

    def __init__(self, base_url: str = "", api_key: str = "",
                 timeout_seconds: int = 30) -> None:
        super().__init__(logical_name="CustomPaymentGW")
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout_seconds
        self._enabled = bool(base_url and api_key)

    # ------------------------------------------------------------------
    # ExternalDevice lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> bool:
        if not self._enabled:
            logger.info("[CustomPaymentGW] connect skipped — not configured")
            return False
        logger.info("[CustomPaymentGW] connect (stub) %s", self._base_url)
        # TODO: test credentials / connectivity
        return False

    def is_enabled(self) -> bool:
        return self._enabled

    # ------------------------------------------------------------------
    # Payment operations
    # ------------------------------------------------------------------

    def initiate_payment(
        self,
        amount: Decimal,
        currency_code: str,
        transaction_ref: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        logger.info("[CustomPaymentGW] initiate_payment (stub) amount=%s ref=%s",
                    amount, transaction_ref)
        # TODO: POST to provider's charge / create-payment endpoint
        return {"success": False, "gateway_ref": "", "message": "stub"}

    def confirm_payment(self, gateway_ref: str) -> Dict[str, Any]:
        logger.info("[CustomPaymentGW] confirm_payment (stub) ref=%s", gateway_ref)
        # TODO: POST to provider's capture endpoint
        return {"success": False, "status": "stub", "message": "stub"}

    def void_payment(self, gateway_ref: str) -> bool:
        logger.info("[CustomPaymentGW] void_payment (stub) ref=%s", gateway_ref)
        # TODO: POST to provider's void endpoint
        return False

    def refund_payment(self, gateway_ref: str, amount: Decimal) -> bool:
        logger.info("[CustomPaymentGW] refund_payment (stub) ref=%s amount=%s",
                    gateway_ref, amount)
        # TODO: POST to provider's refund endpoint
        return False
