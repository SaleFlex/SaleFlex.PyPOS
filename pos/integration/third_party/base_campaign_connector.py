"""
SaleFlex.PyPOS - Abstract base class for third-party campaign / promotion connectors.

Concrete adapters in adapters/campaign/ inherit this class and implement all
abstract methods for their specific promotion engine.

Activated when gate.manages_campaign = false AND
third_party.campaign.enabled = true in settings.toml.

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

from typing import Dict, Any, List

from pos.integration.external_device import ExternalDevice
from core.logger import get_logger

logger = get_logger(__name__)


class BaseCampaignConnector(ExternalDevice):
    """
    Abstract campaign / promotion module connector.

    All concrete campaign adapters must inherit this class.  The IntegrationMixin
    calls these methods through a uniform interface regardless of the underlying
    promotion engine.
    """

    # ------------------------------------------------------------------
    # Campaign operations  (override in concrete adapters)
    # ------------------------------------------------------------------

    def get_applicable_discounts(self, cart_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request applicable discounts for the current cart from the promotion engine.

        Args:
            cart_data: Dict describing the current cart (products, quantities, totals,
                       customer segment, etc.).

        Returns:
            cart_data enriched with a "discounts" key, or original cart_data unchanged
            when the engine is unreachable.
        """
        logger.info("[%s] get_applicable_discounts (stub)", self.logical_name)
        return cart_data

    def redeem_coupon(self, coupon_code: str, cart_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and apply a coupon code against the promotion engine.

        Args:
            coupon_code: Scanned or manually entered coupon / voucher code.
            cart_data:   Current cart state.

        Returns:
            Updated cart_data with coupon discount applied, or original
            cart_data when the coupon is invalid.
        """
        logger.info("[%s] redeem_coupon (stub) code=%s",
                    self.logical_name, coupon_code)
        return cart_data

    def sync_campaigns(self) -> List[Dict[str, Any]]:
        """
        Pull the full list of active campaigns from the promotion engine
        and store them locally for offline use.

        Returns:
            List of campaign definition dicts.
        """
        logger.info("[%s] sync_campaigns (stub)", self.logical_name)
        return []

    def record_usage(self, campaign_id: str, transaction_head_id: str) -> bool:
        """
        Notify the promotion engine that a campaign was used in a transaction.

        Args:
            campaign_id:         Campaign identifier (local or remote).
            transaction_head_id: UUID of the completed TransactionHead record.

        Returns:
            True on success, False on failure.
        """
        logger.info("[%s] record_usage (stub) campaign=%s head=%s",
                    self.logical_name, campaign_id, transaction_head_id)
        return False
