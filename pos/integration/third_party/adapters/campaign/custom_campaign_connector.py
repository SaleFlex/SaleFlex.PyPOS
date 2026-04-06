"""
SaleFlex.PyPOS - Custom campaign / promotion connector adapter (template).

Copy and rename this file to implement a specific promotion engine.
Set third_party.campaign.type = "custom" in settings.toml and register
the class in IntegrationMixin._build_campaign_connector().

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

from core.exceptions import ThirdPartyCampaignError
from core.logger import get_logger
from pos.integration.third_party.base_campaign_connector import BaseCampaignConnector

logger = get_logger(__name__)


class CustomCampaignConnector(BaseCampaignConnector):
    """
    Template campaign connector adapter.

    Replace stubs with calls to your promotion engine's API.
    Raise ThirdPartyCampaignError (not bare Exception) on unrecoverable failures.
    """

    def __init__(self, base_url: str = "", api_key: str = "") -> None:
        super().__init__(logical_name="CustomCampaign")
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._enabled = bool(base_url and api_key)

    def connect(self) -> bool:
        if not self._enabled:
            logger.info("[CustomCampaign] connect skipped — not configured")
            return False
        logger.info("[CustomCampaign] connect (stub) %s", self._base_url)
        return False

    def is_enabled(self) -> bool:
        return self._enabled

    def get_applicable_discounts(self, cart_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("[CustomCampaign] get_applicable_discounts (stub)")
        # TODO: POST cart_data to promotion engine and merge returned discounts
        return cart_data

    def redeem_coupon(self, coupon_code: str, cart_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("[CustomCampaign] redeem_coupon (stub) code=%s", coupon_code)
        # TODO: POST coupon code to promotion engine for validation
        return cart_data

    def sync_campaigns(self) -> List[Dict[str, Any]]:
        logger.info("[CustomCampaign] sync_campaigns (stub)")
        # TODO: GET active campaigns from promotion engine
        return []

    def record_usage(self, campaign_id: str, transaction_head_id: str) -> bool:
        logger.info("[CustomCampaign] record_usage (stub) campaign=%s head=%s",
                    campaign_id, transaction_head_id)
        # TODO: POST usage event to promotion engine
        return False
