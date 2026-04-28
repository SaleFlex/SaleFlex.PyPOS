"""
SaleFlex.PyPOS - Custom payment gateway adapter (template).

Copy and rename this file to implement a specific payment provider
(e.g. iyzico_gateway.py, paytr_gateway.py, stripe_gateway.py).

Set third_party.payment.type = "custom" (or your chosen name) in settings.toml
and register the class in IntegrationMixin._build_payment_gateway().
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
