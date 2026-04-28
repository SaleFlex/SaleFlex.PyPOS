"""
SaleFlex.PyPOS - GATE campaign serializer.

Handles conversion between GATE campaign definitions and local Campaign
models, and builds real-time discount-calculation request/response payloads.
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
