"""
SaleFlex.PyPOS - GATE closure serializer.

Converts a completed Closure record and its summary tables into the JSON
structure expected by SaleFlex.GATE's closure endpoint.
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


class ClosureSerializer:
    """
    Serialise a Closure record into the GATE API payload format.

    Includes high-level totals and all summary breakdown tables
    (VAT, payment types, departments, discounts, cashiers, currencies).
    """

    _ENDPOINT: str = "api/closures/"

    @staticmethod
    def serialize(closure_id: str) -> Dict[str, Any]:
        """
        Build the GATE payload for a completed end-of-day closure.

        Args:
            closure_id: UUID of the Closure record.

        Returns:
            Dict ready to be passed to GateClient.push().

        TODO: Load Closure and all ClosureSummary* records from DB.
        """
        logger.info("[ClosureSerializer] serialize (stub) closure_id=%s", closure_id)
        return {
            "_endpoint": ClosureSerializer._ENDPOINT,
            "closure_id": closure_id,
            "vat_summary": [],
            "payment_summary": [],
            "department_summary": [],
            "discount_summary": [],
            "cashier_summary": [],
            "currency_summary": [],
        }
