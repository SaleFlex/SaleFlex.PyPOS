"""
SaleFlex.PyPOS - Integration layer mixin for the Application class.

Provides integration routing logic as a mixin so it can be added to the
Application inheritance chain alongside CurrentStatus, CurrentData, and
EventHandler without introducing a separate Singleton.

Routing rule (evaluated in order):
    1. If gate.enabled AND gate.manages_<service> → route through GATE.
    2. Else if third_party.<service>.enabled      → route through direct adapter.
    3. Otherwise                                  → no-op, return safe defaults.

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

from typing import Any, Dict, Optional

from core.logger import get_logger

logger = get_logger(__name__)


class IntegrationMixin:
    """
    Routing mixin for the integration layer.

    Add to Application's inheritance chain:
        class Application(CurrentStatus, CurrentData, EventHandler, IntegrationMixin):
            ...

    Then call self.init_integration() inside Application.__init__() after
    settings and database have been initialised.
    """

    # ------------------------------------------------------------------
    # Initialisation  (called once from Application.__init__)
    # ------------------------------------------------------------------

    def init_integration(self) -> None:
        """
        Read integration settings and build the appropriate connector instances.

        Must be called after Settings is initialised and before any event
        handler may call an integration hook.
        """
        self._erp_connector = None
        self._payment_gateway = None
        self._campaign_connector = None

        try:
            from settings.settings import Settings
            s = Settings()
            self._gate_settings = s.gate
            self._tp_settings = s.third_party
        except Exception as e:
            logger.warning("[IntegrationMixin] could not read settings: %s", e)
            self._gate_settings = {}
            self._tp_settings = {}

        self._erp_connector = self._build_erp_connector()
        self._payment_gateway = self._build_payment_gateway()
        self._campaign_connector = self._build_campaign_connector()

        logger.info(
            "[IntegrationMixin] initialised — gate_enabled=%s erp=%s payment=%s campaign=%s",
            self._gate_enabled(),
            type(self._erp_connector).__name__,
            type(self._payment_gateway).__name__,
            type(self._campaign_connector).__name__,
        )

    # ------------------------------------------------------------------
    # Public routing methods  (called by hooks.py)
    # ------------------------------------------------------------------

    def apply_campaign(self, cart_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route campaign discount calculation to GATE or a direct connector.

        Args:
            cart_data: Current cart contents.

        Returns:
            cart_data enriched with discount information, or original dict when
            no integration is active.
        """
        if self._gate_manages("campaign"):
            from pos.integration.gate.gate_pull_service import get_default_gate_pull
            return get_default_gate_pull().get_campaign_discounts(cart_data)

        if self._campaign_connector and self._campaign_connector.is_enabled():
            return self._campaign_connector.get_applicable_discounts(cart_data)

        return cart_data

    def sync_erp_transaction(self, transaction_head_id: str) -> bool:
        """
        Route a completed transaction to GATE's ERP layer or a direct ERP connector.

        Args:
            transaction_head_id: UUID of the TransactionHead record.

        Returns:
            True on successful dispatch (not necessarily confirmed by ERP).
        """
        if self._gate_manages("erp"):
            from pos.integration.gate.gate_sync_service import get_default_gate_sync
            get_default_gate_sync().queue_erp_payload(
                {"head_id": transaction_head_id, "action": "sync_transaction"}
            )
            return True

        if self._erp_connector and self._erp_connector.is_enabled():
            return self._erp_connector.sync_transaction(transaction_head_id)

        return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _gate_enabled(self) -> bool:
        return bool(self._gate_settings.get("enabled", False))

    def _gate_manages(self, service: str) -> bool:
        """Return True when GATE is enabled and configured to handle *service*."""
        return self._gate_enabled() and bool(
            self._gate_settings.get(f"manages_{service}", False)
        )

    def _build_erp_connector(self):
        """
        Instantiate the configured ERP connector.

        Extend the match block with additional ERP types as new adapters are added
        to pos/integration/third_party/adapters/erp/.
        """
        tp = self._tp_settings.get("erp", {})
        if not tp.get("enabled", False):
            return None
        erp_type = tp.get("type", "custom")
        try:
            match erp_type:
                case "custom" | _:
                    from pos.integration.third_party.adapters.erp.custom_erp_connector import (
                        CustomERPConnector,
                    )
                    return CustomERPConnector(
                        base_url=tp.get("base_url", ""),
                        api_key=tp.get("api_key", ""),
                        timeout_seconds=int(tp.get("timeout_seconds", 15)),
                    )
        except Exception as e:
            logger.error("[IntegrationMixin] could not build ERP connector: %s", e)
        return None

    def _build_payment_gateway(self):
        """
        Instantiate the configured payment gateway connector.

        Extend the match block with additional payment types as new adapters are added
        to pos/integration/third_party/adapters/payment/.
        """
        tp = self._tp_settings.get("payment", {})
        if not tp.get("enabled", False):
            return None
        gw_type = tp.get("type", "custom")
        try:
            match gw_type:
                case "custom" | _:
                    from pos.integration.third_party.adapters.payment.custom_payment_gateway import (
                        CustomPaymentGateway,
                    )
                    return CustomPaymentGateway(
                        base_url=tp.get("base_url", ""),
                        api_key=tp.get("api_key", ""),
                        timeout_seconds=int(tp.get("timeout_seconds", 30)),
                    )
        except Exception as e:
            logger.error("[IntegrationMixin] could not build payment gateway: %s", e)
        return None

    def _build_campaign_connector(self):
        """
        Instantiate the configured campaign connector.

        Extend the match block with additional campaign types as new adapters are added
        to pos/integration/third_party/adapters/campaign/.
        """
        tp = self._tp_settings.get("campaign", {})
        if not tp.get("enabled", False):
            return None
        c_type = tp.get("type", "custom")
        try:
            match c_type:
                case "custom" | _:
                    from pos.integration.third_party.adapters.campaign.custom_campaign_connector import (
                        CustomCampaignConnector,
                    )
                    return CustomCampaignConnector(
                        base_url=tp.get("base_url", ""),
                        api_key=tp.get("api_key", ""),
                    )
        except Exception as e:
            logger.error("[IntegrationMixin] could not build campaign connector: %s", e)
        return None
