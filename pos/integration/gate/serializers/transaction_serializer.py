"""
SaleFlex.PyPOS - GATE transaction serializer.

Converts a completed TransactionHead (and its related lines, payments, taxes)
into the JSON structure expected by SaleFlex.GATE's transaction endpoint.
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


class TransactionSerializer:
    """
    Serialise a TransactionHead record into the GATE API payload format.

    Usage:
        payload = TransactionSerializer.serialize(transaction_head_id)
        gate_client.push(payload)
    """

    # GATE REST endpoint that receives this payload.
    _ENDPOINT: str = "api/transactions/"

    @staticmethod
    def serialize(transaction_head_id: str) -> Dict[str, Any]:
        """
        Build the GATE payload for a single completed transaction.

        Loads TransactionHead, its product lines, payments, taxes, and discounts
        from the local database and converts them to the GATE wire format.

        Args:
            transaction_head_id: UUID of the TransactionHead record.

        Returns:
            Dict ready to be passed to GateClient.push().
            The special key ``_endpoint`` tells GateClient which URL to use.

        TODO: Load real data from DB and map to GATE field names.
        """
        logger.info("[TransactionSerializer] serialize (stub) head_id=%s",
                    transaction_head_id)
        return {
            "_endpoint": TransactionSerializer._ENDPOINT,
            "transaction_id": transaction_head_id,
            "lines": [],
            "payments": [],
            "taxes": [],
            "discounts": [],
        }
