"""
SaleFlex.PyPOS - POS receipt printer peripheral (OPOS-style, log-only stub).

Copyright (c) 2025 Ferhat Mousavi

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
from pos.peripherals.document_adapter import format_receipt_text_for_log
from pos.peripherals.opos_device import OposDevice

logger = get_logger(__name__)

_default_printer: "POSPrinter | None" = None


class POSPrinter(OposDevice):
    """Receipt printer; `print_sale_document` logs the full ticket as plain text."""

    def print_sale_document(self, document_data: Dict[str, Any]) -> None:
        body = format_receipt_text_for_log(document_data)
        logger.info("[POSPrinter] print_sale_document begin (%s)", self.logical_name)
        for line in body.splitlines():
            logger.info("[POSPrinter] | %s", line)
        logger.info("[POSPrinter] print_sale_document end")


def get_default_pos_printer() -> POSPrinter:
    global _default_printer
    if _default_printer is None:
        _default_printer = POSPrinter("default")
    return _default_printer
