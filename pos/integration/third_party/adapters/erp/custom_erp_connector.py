"""
SaleFlex.PyPOS - Custom ERP connector adapter (template).

Copy and rename this file to implement a specific ERP integration
(e.g. sap_connector.py, logo_connector.py, netsis_connector.py).

Set third_party.erp.type = "custom" (or your chosen name) in settings.toml
and register the class in IntegrationMixin._build_erp_connector().

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
