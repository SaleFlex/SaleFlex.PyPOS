"""
SaleFlex.PyPOS - Format current document_data for peripherals (log / future drivers).

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
from typing import Any, Dict, List, Optional, Tuple

from data_layer.auto_save import AutoSaveModel


def _unwrap(m: Any) -> Any:
    if isinstance(m, AutoSaveModel):
        return m.unwrap()
    return m


def _money(v: Any) -> str:
    try:
        d = Decimal(str(v)) if v is not None else Decimal("0")
        return format(d, "f")
    except Exception:
        return str(v) if v is not None else "0"


def format_receipt_text_for_log(document_data: Dict[str, Any]) -> str:
    """Build a plain-text receipt body for logging (not sent to hardware yet)."""
    lines: List[str] = []
    if not document_data or not document_data.get("head"):
        return "(no document)"

    head = _unwrap(document_data["head"])
    lines.append("=== SALE DOCUMENT (log receipt) ===")
    lines.append(f"transaction_unique_id: {getattr(head, 'transaction_unique_id', '')}")
    lines.append(f"receipt_number: {getattr(head, 'receipt_number', '')}")
    lines.append(f"total_amount: {_money(getattr(head, 'total_amount', 0))}")
    lines.append(f"total_vat_amount: {_money(getattr(head, 'total_vat_amount', 0))}")
    lines.append(f"total_discount_amount: {_money(getattr(head, 'total_discount_amount', 0))}")
    lines.append(f"total_payment_amount: {_money(getattr(head, 'total_payment_amount', 0))}")
    lines.append(f"total_change_amount: {_money(getattr(head, 'total_change_amount', 0))}")
    lines.append("--- Products ---")
    for p in document_data.get("products") or []:
        row = _unwrap(p)
        if getattr(row, "is_cancel", False):
            continue
        name = getattr(row, "product_name", "") or "Product"
        lines.append(
            f"  {name}  qty={_money(getattr(row, 'quantity', 0))}  "
            f"unit={_money(getattr(row, 'unit_price', 0))}  "
            f"line_total={_money(getattr(row, 'total_price', 0))}"
        )
    lines.append("--- Departments ---")
    for d in document_data.get("departments") or []:
        row = _unwrap(d)
        if getattr(row, "is_cancel", False):
            continue
        lines.append(
            f"  line {getattr(row, 'line_no', '')}  "
            f"total={_money(getattr(row, 'total_department', 0))}  "
            f"vat={_money(getattr(row, 'total_department_vat', 0))}"
        )
    lines.append("--- Discounts ---")
    for disc in document_data.get("discounts") or []:
        row = _unwrap(disc)
        if getattr(row, "is_cancel", False):
            continue
        lines.append(
            f"  type={getattr(row, 'discount_type', '')}  "
            f"amount={_money(getattr(row, 'discount_amount', 0))}"
        )
    lines.append("--- Surcharges ---")
    for s in document_data.get("surcharges") or []:
        row = _unwrap(s)
        lines.append(
            f"  {getattr(row, 'surcharge_name', '')}  "
            f"amount={_money(getattr(row, 'surcharge_amount', 0))}"
        )
    lines.append("--- Payments ---")
    for pay in document_data.get("payments") or []:
        row = _unwrap(pay)
        lines.append(
            f"  {getattr(row, 'payment_type', '')}  "
            f"total={_money(getattr(row, 'payment_total', 0))}  "
            f"currency={getattr(row, 'currency_code', '')}"
        )
    lines.append("--- Change ---")
    for ch in document_data.get("changes") or []:
        row = _unwrap(ch)
        lines.append(f"  change_amount={_money(getattr(row, 'change_amount', 0))}")
    lines.append("=== END ===")
    return "\n".join(lines)


def _head_total(document_data: Dict[str, Any]) -> str:
    if not document_data or not document_data.get("head"):
        return _money(0)
    head = _unwrap(document_data["head"])
    return _money(getattr(head, "total_amount", 0))


def build_three_lines_from_document(document_data: Optional[Dict[str, Any]]) -> Tuple[str, str, str]:
    """
    Infer last sale-affecting line (product, department, or discount) and document total.
    Used for customer line display during selling.
    """
    if not document_data or not document_data.get("head"):
        return "Ready", "—", _money(0)

    head = _unwrap(document_data["head"])
    total = _money(getattr(head, "total_amount", 0))

    candidates: List[Tuple[int, str, str, str]] = []

    for p in document_data.get("products") or []:
        row = _unwrap(p)
        if getattr(row, "is_cancel", False):
            continue
        ln = int(getattr(row, "line_no", 0) or 0)
        name = (getattr(row, "product_name", None) or "Product").strip() or "Product"
        price = _money(getattr(row, "unit_price", 0))
        candidates.append((ln, name, price, total))

    for d in document_data.get("departments") or []:
        row = _unwrap(d)
        if getattr(row, "is_cancel", False):
            continue
        ln = int(getattr(row, "line_no", 0) or 0)
        name = f"Department ({getattr(row, 'line_no', '')})"
        price = _money(getattr(row, "total_department", 0))
        candidates.append((ln, name, price, total))

    for disc in document_data.get("discounts") or []:
        row = _unwrap(disc)
        if getattr(row, "is_cancel", False):
            continue
        ln = int(getattr(row, "line_no", 0) or 0)
        dtype = (getattr(row, "discount_type", None) or "Discount").strip() or "Discount"
        price = _money(getattr(row, "discount_amount", 0))
        candidates.append((ln, dtype, price, total))

    if not candidates:
        return "Ready", "—", total

    candidates.sort(key=lambda x: x[0])
    _, line1, line2, line3 = candidates[-1]
    return line1, line2, line3
