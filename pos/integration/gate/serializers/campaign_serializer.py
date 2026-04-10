"""
SaleFlex.PyPOS - GATE campaign serializer.

Handles conversion between GATE campaign definitions and local Campaign
models, and builds real-time discount-calculation request/response payloads.

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

from typing import Any, Dict, List

from core.logger import get_logger
from pos.service.campaign.cart_snapshot import normalize_cart_data_for_campaign_request

logger = get_logger(__name__)


class CampaignSerializer:
    """
    Bi-directional campaign data converter for SaleFlex.GATE.

    - apply_updates(): store campaign definitions pulled from GATE locally.
    - build_discount_request(): build a real-time pricing request payload.
    - apply_discount_response(): merge GATE discount response into cart data.
    """

    @staticmethod
    def apply_updates(campaigns: List[Dict[str, Any]]) -> None:
        """
        Persist active campaign definitions received from GATE to local DB.

        Args:
            campaigns: List of campaign dicts from GATE.

        TODO: Upsert each into Campaign, CampaignRule, CampaignProduct tables.
        """
        logger.info("[CampaignSerializer] apply_updates (stub) count=%d", len(campaigns))
        from pos.service.campaign.active_campaign_cache import ActiveCampaignCache

        ActiveCampaignCache.reload_safely()

    @staticmethod
    def build_discount_request(cart_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the GATE discount-calculation request payload from cart contents.

        Args:
            cart_data: Canonical snapshot (``schema_version`` 1.0) or legacy
                ``document_data``-shaped dict with ``head`` and ``products``.

        Returns:
            Dict suitable for POSTing to GATE's campaign/calculate/ endpoint.

        TODO: Map normalized snapshot fields to GATE API field names.
        """
        body = normalize_cart_data_for_campaign_request(cart_data)
        logger.info("[CampaignSerializer] build_discount_request (stub) schema=%s", body.get("schema_version"))
        return body

    @staticmethod
    def apply_discount_response(cart_data: Dict[str, Any],
                                response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge discount information from a GATE response into cart_data.

        Args:
            cart_data: Original cart dict.
            response:  GATE discount-calculation response.

        Returns:
            Updated cart_data with applied discounts.

        TODO: Parse response["discounts"] and apply to cart_data lines.
        """
        logger.info("[CampaignSerializer] apply_discount_response (stub)")
        return cart_data
