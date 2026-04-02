"""
SaleFlex.PyPOS - Glue between SALE form flows and default peripheral instances.

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

from decimal import Decimal
from typing import Any, Dict, Optional

from data_layer.enums import FormName
from pos.peripherals.document_adapter import build_three_lines_from_document
from pos.peripherals.line_display import get_default_line_display


def _is_sale_form(app: Any) -> bool:
    return getattr(app, "current_form_type", None) == FormName.SALE


def sync_line_display_from_document(app: Any, document_data: Optional[Dict[str, Any]]) -> None:
    if not _is_sale_form(app):
        return
    l1, l2, l3 = build_three_lines_from_document(document_data)
    get_default_line_display().send_three_lines(l1, l2, l3)


def sync_line_display_payment(
    app: Any,
    document_data: Optional[Dict[str, Any]],
    payment_amount: Decimal,
) -> None:
    """
    Payment step: line1 = tendered amount, line2 = document total, line3 = balance due.
    """
    if not _is_sale_form(app):
        return
    if not document_data or not document_data.get("head"):
        return

    from data_layer.auto_save import AutoSaveModel

    head = document_data["head"]
    if isinstance(head, AutoSaveModel):
        head = head.unwrap()

    def _m(v: Any) -> str:
        try:
            return format(Decimal(str(v)), "f")
        except Exception:
            return str(v)

    total = Decimal(str(getattr(head, "total_amount", 0)))
    paid = Decimal(str(getattr(head, "total_payment_amount", 0)))
    balance = total - paid

    get_default_line_display().send_three_lines(
        _m(payment_amount),
        _m(total),
        _m(balance),
    )


def sync_line_display_cleared(app: Any) -> None:
    if not _is_sale_form(app):
        return
    get_default_line_display().send_three_lines("Ready", "—", "0")
