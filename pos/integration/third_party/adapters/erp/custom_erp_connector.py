"""
SaleFlex.PyPOS - Custom ERP connector adapter (template).

Copy and rename this file to implement a specific ERP integration
(e.g. sap_connector.py, logo_connector.py, netsis_connector.py).

Set third_party.erp.type = "custom" (or your chosen name) in settings.toml
and register the class in IntegrationMixin._build_erp_connector().
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

from typing import Dict, Any, List

from core.exceptions import ERPConnectionError
from core.logger import get_logger
from pos.integration.third_party.base_erp_connector import BaseERPConnector

logger = get_logger(__name__)


class CustomERPConnector(BaseERPConnector):
    """
    Template ERP connector.

    Replace the stub implementations with real HTTP / SOAP / SDK calls
    for your target ERP system.  All methods must raise ERPConnectionError
    (not bare Exception) on unrecoverable failures so the caller can react
    appropriately.
    """

    def __init__(self, base_url: str = "", api_key: str = "",
                 timeout_seconds: int = 15) -> None:
        super().__init__(logical_name="CustomERP")
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout_seconds
        self._enabled = bool(base_url and api_key)

    # ------------------------------------------------------------------
    # ExternalDevice lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> bool:
        if not self._enabled:
            logger.info("[CustomERP] connect skipped — not configured")
            return False
        logger.info("[CustomERP] connect (stub) %s", self._base_url)
        # TODO: authenticate and set self._connected = True on success
        return False

    def is_enabled(self) -> bool:
        return self._enabled

    # ------------------------------------------------------------------
    # ERP operations
    # ------------------------------------------------------------------

    def sync_transaction(self, transaction_head_id: str) -> bool:
        logger.info("[CustomERP] sync_transaction (stub) head_id=%s",
                    transaction_head_id)
        # TODO: POST transaction data to ERP endpoint
        return False

    def sync_closure(self, closure_id: str) -> bool:
        logger.info("[CustomERP] sync_closure (stub) closure_id=%s", closure_id)
        # TODO: POST closure summary to ERP endpoint
        return False

    def pull_product_catalog(self) -> List[Dict[str, Any]]:
        logger.info("[CustomERP] pull_product_catalog (stub)")
        # TODO: GET product list from ERP
        return []

    def pull_customer_data(self, customer_id: str) -> Dict[str, Any]:
        logger.info("[CustomERP] pull_customer_data (stub) id=%s", customer_id)
        # TODO: GET customer record from ERP
        return {}

    def sync_inventory(self, warehouse_id: str) -> bool:
        logger.info("[CustomERP] sync_inventory (stub) warehouse=%s", warehouse_id)
        # TODO: Synchronise stock levels with ERP
        return False
