"""
SaleFlex.PyPOS - Third-party direct integration connectors.

This package contains abstract base classes and concrete adapters for
systems that PyPOS connects to directly, bypassing SaleFlex.GATE.

Each connector type is activated only when:
    1. gate.manages_<type> = false  in settings.toml, AND
    2. third_party.<type>.enabled = true  in settings.toml.

Copyright (c) 2026 Ferhat Mousavi
"""

from pos.integration.third_party.base_erp_connector import BaseERPConnector
from pos.integration.third_party.base_payment_gateway import BasePaymentGateway
from pos.integration.third_party.base_campaign_connector import BaseCampaignConnector

__all__ = [
    "BaseERPConnector",
    "BasePaymentGateway",
    "BaseCampaignConnector",
]
