"""
SaleFlex.PyPOS - GATE transaction serializer.

Converts a completed TransactionHead (and its related lines, payments, taxes)
into the JSON structure expected by SaleFlex.GATE's transaction endpoint.

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
