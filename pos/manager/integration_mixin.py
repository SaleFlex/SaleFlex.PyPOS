"""
SaleFlex.PyPOS - Integration layer mixin for the Application class.

Provides integration routing logic as a mixin so it can be added to the
Application inheritance chain alongside CurrentStatus, CurrentData, and
EventHandler without introducing a separate Singleton.

Routing rule (evaluated in order):
    1. If gate.enabled AND gate.manages_<service> → route through GATE.
    2. Else if third_party.<service>.enabled      → route through direct adapter.
    3. Otherwise                                  → no-op, return safe defaults.
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

        # Start the OFFICE push worker when running in 'office' mode.
        self._office_push_worker = self._start_office_push_worker()

        logger.info(
            "[IntegrationMixin] initialised — gate_enabled=%s erp=%s payment=%s campaign=%s office_push=%s",
            self._gate_enabled(),
            type(self._erp_connector).__name__,
            type(self._payment_gateway).__name__,
            type(self._campaign_connector).__name__,
            "active" if self._office_push_worker else "inactive",
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

        if isinstance(cart_data, dict) and "head" in cart_data and "products" in cart_data:
            try:
                from pos.service.campaign.campaign_service import CampaignService

                proposals = CampaignService.evaluate_proposals(cart_data)
                enriched = {**cart_data, "campaign_proposals": [CampaignService.campaign_discount_proposal_to_dict(p) for p in proposals]}
                return enriched
            except Exception as e:
                logger.warning("[IntegrationMixin] local apply_campaign failed (non-fatal): %s", e)

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

    def _start_office_push_worker(self):
        """
        Start the OfficePushWorker background thread when in 'office' mode.

        Reads the sync interval from settings ([office].sync_interval_minutes).
        Defaults to 60 minutes when the setting is absent.

        Returns the running OfficePushWorker instance, or None when not in
        'office' mode or when the worker fails to start.
        """
        try:
            from settings.settings import Settings
            if Settings().app_mode != "office":
                return None

            from pos.manager.office_push_worker import OfficePushWorker

            interval_minutes = int(
                self._gate_settings.get("sync_interval_minutes", 60)
            )
            # Fall back to the office section if gate section has no interval.
            try:
                office_interval = Settings().office_sync_interval_seconds
                if office_interval > 0:
                    interval_seconds = office_interval
                else:
                    interval_seconds = interval_minutes * 60
            except Exception:
                interval_seconds = interval_minutes * 60

            worker = OfficePushWorker(retry_interval_seconds=interval_seconds)

            # Connect signals before starting the thread so no emission is missed.
            worker.data_refresh_needed.connect(self._on_office_data_refresh_needed)

            worker.start()
            logger.info(
                "[IntegrationMixin] OfficePushWorker started (interval=%ds)",
                interval_seconds,
            )
            return worker
        except Exception as exc:
            logger.warning(
                "[IntegrationMixin] Could not start OfficePushWorker: %s", exc
            )
            return None

    def _on_office_data_refresh_needed(self, domains: str) -> None:
        """
        Slot connected to ``OfficePushWorker.data_refresh_needed``.

        Called in the main Qt thread after the worker has successfully upserted
        fresh data from OFFICE into the local SQLite database.  Rebuilds the
        in-memory caches so the next sale period operates with up-to-date
        master-data.

        Parameters
        ----------
        domains:
            Comma-separated list of cache domains to reload.  ``"all"`` reloads
            every cache (pos_data, product_data, ActiveCampaignCache).
        """
        logger.info(
            "[IntegrationMixin] Post-closure OFFICE data refresh received – reloading caches (domains=%s)",
            domains,
        )
        try:
            reload_all = "all" in domains
            if reload_all or "pos_data" in domains:
                self.populate_pos_data()
                logger.info("[IntegrationMixin] pos_data cache reloaded")
            if reload_all or "product" in domains:
                self.populate_product_data()
                logger.info("[IntegrationMixin] product_data cache reloaded")
            if reload_all or "campaign" in domains:
                self.refresh_active_campaign_cache()
                logger.info("[IntegrationMixin] ActiveCampaignCache reloaded")
            logger.info("[IntegrationMixin] ✓ All requested caches reloaded after OFFICE refresh")
        except Exception as exc:
            logger.error(
                "[IntegrationMixin] Cache reload after OFFICE refresh failed: %s",
                exc,
                exc_info=True,
            )

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
