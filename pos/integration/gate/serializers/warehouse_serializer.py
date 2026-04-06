"""
SaleFlex.PyPOS - GATE warehouse / stock movement serializer.

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

from typing import Dict, Any

from core.logger import get_logger

logger = get_logger(__name__)


class WarehouseSerializer:
    """
    Converts WarehouseStockMovement records to the GATE API wire format.
    """

    _ENDPOINT: str = "api/warehouse/movements/"

    @staticmethod
    def serialize(movement_id: str) -> Dict[str, Any]:
        """
        Build the GATE payload for a single stock movement event.

        Args:
            movement_id: UUID of the WarehouseStockMovement record.

        Returns:
            Dict ready for GateClient.push().

        TODO: Load WarehouseStockMovement from DB and map fields.
        """
        logger.info("[WarehouseSerializer] serialize (stub) movement_id=%s", movement_id)
        return {
            "_endpoint": WarehouseSerializer._ENDPOINT,
            "movement_id": movement_id,
            "product_id": None,
            "warehouse_id": None,
            "quantity": 0,
            "movement_type": None,
        }
