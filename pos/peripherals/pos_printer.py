"""
SaleFlex.PyPOS - POS receipt printer peripheral (OPOS-style, log-only stub).

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
