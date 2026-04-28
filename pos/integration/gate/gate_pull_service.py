"""
SaleFlex.PyPOS - SaleFlex.GATE inbound synchronisation service.

Responsible for pulling updates from SaleFlex.GATE: product/price changes,
campaign definitions, and terminal-to-terminal notifications.  Called
periodically by SyncWorker and on application startup via GeneralEvent.
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

from typing import List, Dict, Any

from core.logger import get_logger
from pos.integration.gate.gate_client import get_default_gate_client
from pos.integration.gate.serializers.product_serializer import ProductSerializer
from pos.integration.gate.serializers.campaign_serializer import CampaignSerializer
from pos.integration.gate.serializers.notification_serializer import NotificationSerializer

logger = get_logger(__name__)

_default_gate_pull: "GatePullService | None" = None


class GatePullService:
    """
    Inbound pull service for SaleFlex.GATE.

    Each pull_*() method fetches a specific resource from GATE and applies
    the update locally (cache refresh, DB write, or notification dispatch).
    All methods are stubs that log the intended operation.
    """

    def __init__(self) -> None:
        self._client = get_default_gate_client()

    # ------------------------------------------------------------------
    # Public: enable check
    # ------------------------------------------------------------------

    def is_enabled(self) -> bool:
        """Return True when GATE pull is configured and active."""
        return self._client.is_enabled()

    # ------------------------------------------------------------------
    # Pull methods  (called by SyncWorker and hooks.pull_updates_from_gate)
    # ------------------------------------------------------------------

    def pull_product_updates(self) -> List[Dict[str, Any]]:
        """
        Fetch product and pricing updates from GATE since the last sync.

        After retrieval the local product_data cache should be invalidated
        and rebuilt so that price changes take effect immediately.

        Returns:
            List of product update dicts from GATE.
        """
        logger.info("[GatePullService] pull_product_updates (stub)")
        # TODO: raw = self._client.pull("api/products/updates/", {"since": last_sync_ts})
        # TODO: ProductSerializer.apply_updates(raw.get("results", []))
        return []

    def pull_campaign_updates(self) -> List[Dict[str, Any]]:
        """
        Fetch active campaign and promotion definitions from GATE.

        Returns:
            List of campaign dicts from GATE.
        """
        logger.info("[GatePullService] pull_campaign_updates (stub)")
        # TODO: raw = self._client.pull("api/campaigns/active/")
        # TODO: CampaignSerializer.apply_updates(raw.get("results", []))
        return []

    def pull_notifications(self) -> List[Dict[str, Any]]:
        """
        Fetch pending terminal notifications and inter-POS messages from GATE.

        Notifications are written to the local GateNotification table and
        surfaced to the UI via the NotificationWorker signal.

        Returns:
            List of notification dicts from GATE.
        """
        logger.info("[GatePullService] pull_notifications (stub)")
        # TODO: raw = self._client.pull("api/notifications/", {"terminal_id": terminal_id})
        # TODO: NotificationSerializer.save_and_dispatch(raw.get("results", []))
        return []

    def get_campaign_discounts(self, cart_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request real-time campaign discount calculation from GATE.

        Called when gate.manages_campaign = true and a cart requires pricing.

        Args:
            cart_data: Current cart contents (products, quantities, totals).

        Returns:
            cart_data dict enriched with discount information from GATE,
            or original cart_data unchanged when GATE is unreachable.
        """
        logger.info("[GatePullService] get_campaign_discounts (stub)")
        # TODO: payload = CampaignSerializer.build_discount_request(cart_data)
        # TODO: response = self._client.push({**payload, "_endpoint": "api/campaigns/calculate/"})
        # TODO: return CampaignSerializer.apply_discount_response(cart_data, response)
        return cart_data


# ---------------------------------------------------------------------------
# Module-level factory
# ---------------------------------------------------------------------------

def get_default_gate_pull() -> GatePullService:
    """Return the module-level GatePullService singleton."""
    global _default_gate_pull
    if _default_gate_pull is None:
        _default_gate_pull = GatePullService()
    return _default_gate_pull
