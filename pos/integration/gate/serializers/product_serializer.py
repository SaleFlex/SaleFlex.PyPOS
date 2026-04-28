"""
SaleFlex.PyPOS - GATE product serializer.

Handles bi-directional product data conversion:
- serialize(): local Product → GATE wire format (push)
- apply_updates(): GATE response → local DB / cache update (pull)
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
