"""
SaleFlex.PyPOS - Glue between SALE form flows and default peripheral instances.
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

from decimal import Decimal
from typing import Any, Dict, Optional

from data_layer.enums import FormName
from pos.peripherals.document_adapter import build_three_lines_from_document
from pos.peripherals.line_display import get_default_line_display


def _is_sale_form(app: Any) -> bool:
    """True on SALE or PAYMENT screen (same active ticket / line display context)."""
    ft = getattr(app, "current_form_type", None)
    return ft in (FormName.SALE, FormName.PAYMENT)


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

    from pos.service.payment_service import PaymentService

    net = PaymentService.net_amount_due(head)
    paid = Decimal(str(getattr(head, "total_payment_amount", 0)))
    balance = net - paid

    get_default_line_display().send_three_lines(
        _m(payment_amount),
        _m(net),
        _m(balance),
    )


def sync_line_display_cleared(app: Any) -> None:
    if not _is_sale_form(app):
        return
    get_default_line_display().send_three_lines("Ready", "—", "0")
