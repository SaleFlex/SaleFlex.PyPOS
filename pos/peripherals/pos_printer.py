"""
SaleFlex.PyPOS - POS receipt printer peripheral (OPOS-style, log-only stub).
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

from typing import Any, Dict

from core.logger import get_logger
from pos.peripherals.document_adapter import format_closure_lines, format_receipt_lines
from pos.peripherals.opos_device import OposDevice

logger = get_logger(__name__)

_default_printer: "POSPrinter | None" = None


class POSPrinter(OposDevice):
    """
    Receipt printer peripheral (OPOS-style stub).

    `print_sale_document` formats the completed sale document into a
    thermal-printer-style receipt and writes each line individually to the
    application log.  A real driver would replace (or extend) this method to
    forward the lines to actual hardware via ESC/POS or a similar protocol.

    Receipt layout (38-character width):
        ======================================
                   SALE RECEIPT
        Receipt: 00001  06/04/2026 14:35:22
        ======================================
        PRODUCT NAME                    £1.00
        PRODUCT NAME
          2 x £0.50                     £1.00
        --------------------------------------
        2 BALANCE DUE                   £2.00
           CASH                         £5.00

           CHANGE                       £3.00
           VAT                          £0.18
        **************************************
    """

    def print_sale_document(self, document_data: Dict[str, Any]) -> None:
        """
        Format *document_data* as a receipt and log every line individually.

        Each receipt line is sent to the logger with an ``[POSPrinter] |``
        prefix so it can be easily grepped from the application log and later
        forwarded to a real printer driver without changing call sites.

        Args:
            document_data: The completed ``document_data`` dict produced by
                           ``DocumentManager`` / ``PaymentEvent``.
        """
        receipt_lines = format_receipt_lines(document_data)
        logger.info("[POSPrinter] print_sale_document begin (%s)", self.logical_name)
        for line in receipt_lines:
            logger.info("[POSPrinter] | %s", line)
        logger.info("[POSPrinter] print_sale_document end")

    def print_closure_document(self, closure_data: Dict[str, Any]) -> None:
        """
        Format *closure_data* as an end-of-day closure report and log every
        line individually.

        Uses ``format_closure_lines`` from ``document_adapter`` to build a
        42-character-wide thermal-printer-style Z-report.  Each line is logged
        with an ``[POSPrinter] |`` prefix so it can be grepped or forwarded to
        a real ESC/POS driver without changing call sites.

        Args:
            closure_data: Dict with keys ``closure`` (Closure ORM record),
                          ``totals`` (aggregated totals dict from
                          ``ClosureEvent._aggregate_closure_totals``),
                          ``currency_code``, ``cashier_name``, ``pos_name``,
                          ``pos_serial``.
        """
        closure_lines = format_closure_lines(closure_data)
        logger.info("[POSPrinter] print_closure_document begin (%s)", self.logical_name)
        for line in closure_lines:
            logger.info("[POSPrinter] | %s", line)
        logger.info("[POSPrinter] print_closure_document end")


def get_default_pos_printer() -> POSPrinter:
    global _default_printer
    if _default_printer is None:
        _default_printer = POSPrinter("default")
    return _default_printer
