"""
Campaign / promotion service helpers (cart snapshot, application policy constants).

Copyright (c) 2025-2026 Ferhat Mousavi
"""

from pos.service.campaign.application_policy import CAMPAIGN_DISCOUNT_TYPE_CODE
from pos.service.campaign.cart_snapshot import (
    CART_SNAPSHOT_SCHEMA_VERSION,
    CartLineSnapshot,
    CartSnapshot,
    CartTotalsSnapshot,
    build_cart_snapshot_from_document_data,
    cart_snapshot_to_dict,
    normalize_cart_data_for_campaign_request,
)

__all__ = [
    "CAMPAIGN_DISCOUNT_TYPE_CODE",
    "CART_SNAPSHOT_SCHEMA_VERSION",
    "CartLineSnapshot",
    "CartSnapshot",
    "CartTotalsSnapshot",
    "build_cart_snapshot_from_document_data",
    "cart_snapshot_to_dict",
    "normalize_cart_data_for_campaign_request",
]
