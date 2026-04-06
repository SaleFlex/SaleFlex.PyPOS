"""
SaleFlex.PyPOS - GATE closure serializer.

Converts a completed Closure record and its summary tables into the JSON
structure expected by SaleFlex.GATE's closure endpoint.

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
