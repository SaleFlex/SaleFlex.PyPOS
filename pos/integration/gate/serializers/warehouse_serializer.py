"""
SaleFlex.PyPOS - GATE warehouse / stock movement serializer.
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
