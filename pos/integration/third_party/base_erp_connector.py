"""
SaleFlex.PyPOS - Abstract base class for third-party ERP connectors.

Concrete adapters in adapters/erp/ inherit this class and implement all
abstract methods for their specific ERP system (SAP, Oracle, Logo, Netsis,
custom REST/SOAP APIs, etc.).

Activated when gate.manages_erp = false AND third_party.erp.enabled = true.

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


class BaseERPConnector(ExternalDevice):
    """
    Abstract ERP connector.

    All concrete ERP adapters (SAP, Oracle, Logo, Netsis, custom) must
    inherit this class and implement the methods below.  The IntegrationMixin
    calls these methods without knowing which ERP system is in use.
    """

    # ------------------------------------------------------------------
    # ERP-specific operations  (override in concrete adapters)
    # ------------------------------------------------------------------

    def sync_transaction(self, transaction_head_id: str) -> bool:
        """
        Push a completed transaction to the ERP system.

        Args:
            transaction_head_id: UUID of the TransactionHead record.

        Returns:
            True on success, False on failure.
        """
        logger.info("[%s] sync_transaction (stub) head_id=%s",
                    self.logical_name, transaction_head_id)
        return False

    def sync_closure(self, closure_id: str) -> bool:
        """
        Push an end-of-day closure summary to the ERP system.

        Args:
            closure_id: UUID of the Closure record.

        Returns:
            True on success, False on failure.
        """
        logger.info("[%s] sync_closure (stub) closure_id=%s",
                    self.logical_name, closure_id)
        return False

    def pull_product_catalog(self) -> List[Dict[str, Any]]:
        """
        Pull the product catalog and pricing from the ERP system.

        Returns:
            List of product dicts in GATE-compatible format.
        """
        logger.info("[%s] pull_product_catalog (stub)", self.logical_name)
        return []

    def pull_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve customer data from the ERP system by customer ID.

        Args:
            customer_id: Local or ERP customer identifier.

        Returns:
            Customer dict or empty dict when not found.
        """
        logger.info("[%s] pull_customer_data (stub) customer_id=%s",
                    self.logical_name, customer_id)
        return {}

    def sync_inventory(self, warehouse_id: str) -> bool:
        """
        Synchronise local warehouse stock levels with the ERP system.

        Args:
            warehouse_id: UUID of the local Warehouse record.

        Returns:
            True on success, False on failure.
        """
        logger.info("[%s] sync_inventory (stub) warehouse_id=%s",
                    self.logical_name, warehouse_id)
        return False
