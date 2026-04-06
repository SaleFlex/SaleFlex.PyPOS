"""
SaleFlex.PyPOS - GATE product serializer.

Handles bi-directional product data conversion:
- serialize(): local Product → GATE wire format (push)
- apply_updates(): GATE response → local DB / cache update (pull)

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

from core.logger import get_logger

logger = get_logger(__name__)


class ProductSerializer:
    """
    Product data converter between local ORM models and GATE API format.
    """

    _ENDPOINT: str = "api/products/"

    @staticmethod
    def serialize(product_id: str) -> Dict[str, Any]:
        """
        Convert a local Product record to the GATE wire format.

        Args:
            product_id: UUID of the Product record.

        Returns:
            Dict ready for GateClient.push().

        TODO: Load Product, ProductBarcode, ProductVariant from DB.
        """
        logger.info("[ProductSerializer] serialize (stub) product_id=%s", product_id)
        return {
            "_endpoint": ProductSerializer._ENDPOINT,
            "product_id": product_id,
            "barcodes": [],
            "variants": [],
            "attributes": [],
        }

    @staticmethod
    def apply_updates(updates: List[Dict[str, Any]]) -> None:
        """
        Apply product updates received from GATE to the local database.

        After applying updates the product_data cache must be rebuilt so
        that the new prices and stock levels are used immediately.

        Args:
            updates: List of product update dicts returned by GATE.

        TODO: Upsert each update into the local Product / ProductBarcode tables,
              then call CacheManager.populate_product_data() to refresh memory.
        """
        logger.info("[ProductSerializer] apply_updates (stub) count=%d", len(updates))
