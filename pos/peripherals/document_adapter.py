"""
SaleFlex.PyPOS - Format current document_data for peripherals (log / future drivers).

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

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from data_layer.auto_save import AutoSaveModel

# ---------------------------------------------------------------------------
# Receipt / closure layout constants
# ---------------------------------------------------------------------------

RECEIPT_WIDTH: int = 38
CLOSURE_WIDTH: int = 42

_CURRENCY_SYMBOLS: Dict[str, str] = {
    "GBP": "£", "USD": "$", "EUR": "€", "TRY": "₺",
    "JPY": "¥", "CNY": "¥", "KRW": "₩", "INR": "₹",
    "AUD": "A$", "CAD": "C$", "CHF": "Fr",
}

_PAYMENT_TYPE_LABELS: Dict[str, str] = {
    "CASH_PAYMENT": "CASH",
    "CREDIT_PAYMENT": "CREDIT",
    "CHECK_PAYMENT": "CHECK",
    "EXCHANGE_PAYMENT": "EXCHANGE",
    "PREPAID_PAYMENT": "PREPAID",
    "CHARGE_SALE_PAYMENT": "CHARGE",
    "OTHER_PAYMENT": "OTHER",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

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


def _currency_symbol(code: str) -> str:
    """Return a printable currency symbol for the given ISO-4217 code."""
    return _CURRENCY_SYMBOLS.get((code or "").upper(), (code or "USD")[:3])


def _fmt_amount(v: Any, symbol: str) -> str:
    """Format a monetary value as '<symbol><amount:.2f>'."""
    try:
        d = Decimal(str(v)) if v is not None else Decimal("0")
        return f"{symbol}{d:.2f}"
    except Exception:
        return f"{symbol}0.00"


def _receipt_line(left: str, right: str, width: int = RECEIPT_WIDTH) -> str:
    """
    Build a single receipt line: *left* text left-aligned, *right* text
    right-aligned, padded with spaces to *width* characters.  *left* is
    truncated if it would otherwise overlap *right*.
    """
    max_left = width - len(right) - 1          # at least one space between
    if len(left) > max_left:
        left = left[:max_left]
    spaces = width - len(left) - len(right)
    return f"{left}{' ' * max(1, spaces)}{right}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def format_receipt_lines(document_data: Dict[str, Any]) -> List[str]:
    """
    Build a thermal-printer-style receipt as a list of plain-text lines.

    Layout (RECEIPT_WIDTH = 38 chars):

        ======================================
                   SALE RECEIPT
        Receipt: 00001  06/04/2026 14:35:22
        ======================================
        PRODUCT NAME A                  £1.00
        PRODUCT NAME B
          2 x £0.50                     £1.00
        --------------------------------------
        2 BALANCE DUE                   £2.00
           CASH                         £5.00

           CHANGE                       £3.00
           VAT                          £0.18
        **************************************

    Each product with qty != 1 is printed on two lines (name, then
    "  qty x unit_price  total").  VAT is printed below CHANGE.
    """
    W = RECEIPT_WIDTH
    SEP = "-" * W
    STAR = "*" * W
    EQ = "=" * W

    lines: List[str] = []

    if not document_data or not document_data.get("head"):
        lines.append("(no document)")
        return lines

    head = _unwrap(document_data["head"])
    currency = getattr(head, "base_currency", None) or "GBP"
    sym = _currency_symbol(currency)

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    lines.append(EQ)
    lines.append(f"{'SALE RECEIPT':^{W}}")

    receipt_no = getattr(head, "receipt_number", "") or ""
    dt_raw = getattr(head, "transaction_date_time", None)
    if dt_raw and hasattr(dt_raw, "strftime"):
        dt_str = dt_raw.strftime("%d/%m/%Y %H:%M:%S")
    else:
        dt_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    lines.append(_receipt_line(f"Receipt: {receipt_no}", dt_str, W))
    lines.append(EQ)

    # ------------------------------------------------------------------
    # Product lines
    # ------------------------------------------------------------------
    item_count = 0

    for p in document_data.get("products") or []:
        row = _unwrap(p)
        if getattr(row, "is_cancel", False) or getattr(row, "is_voided", False):
            continue

        name = (getattr(row, "product_name", None) or "ITEM").upper().strip()
        qty = Decimal(str(getattr(row, "quantity", 1) or 1))
        unit_price = getattr(row, "unit_price", 0)
        total_price = getattr(row, "total_price", 0)
        amount_str = _fmt_amount(total_price, sym)

        if qty != Decimal("1"):
            # Two-line format: name first, then qty × unit on the next
            lines.append(name[:W])
            qty_label = f"  {qty:g} x {_fmt_amount(unit_price, sym)}"
            lines.append(_receipt_line(qty_label, amount_str, W))
        else:
            lines.append(_receipt_line(name, amount_str, W))

        item_count += 1

    # Department lines (shown when departments are sold without explicit products)
    for d in document_data.get("departments") or []:
        row = _unwrap(d)
        if getattr(row, "is_cancel", False):
            continue
        dept_label = f"DEPT {getattr(row, 'line_no', '')}".upper()
        amount_str = _fmt_amount(getattr(row, "total_department", 0), sym)
        lines.append(_receipt_line(dept_label, amount_str, W))
        item_count += 1

    # Discount lines
    for disc in document_data.get("discounts") or []:
        row = _unwrap(disc)
        if getattr(row, "is_cancel", False):
            continue
        dtype = (getattr(row, "discount_type", None) or "DISCOUNT").upper()
        disc_amount = getattr(row, "discount_amount", 0)
        amount_str = f"-{_fmt_amount(disc_amount, sym)}"
        lines.append(_receipt_line(dtype, amount_str, W))

    # ------------------------------------------------------------------
    # Totals section
    # ------------------------------------------------------------------
    lines.append(SEP)

    balance_label = f"{item_count} BALANCE DUE" if item_count > 0 else "BALANCE DUE"
    lines.append(_receipt_line(balance_label, _fmt_amount(getattr(head, "total_amount", 0), sym), W))

    # Payment lines
    for pay in document_data.get("payments") or []:
        row = _unwrap(pay)
        pay_type = (getattr(row, "payment_type", None) or "PAYMENT")
        pay_label = _PAYMENT_TYPE_LABELS.get(pay_type, pay_type.replace("_", " ").upper())
        lines.append(_receipt_line(f"   {pay_label}", _fmt_amount(getattr(row, "payment_total", 0), sym), W))

    # Change
    change_total = Decimal("0")
    for ch in document_data.get("changes") or []:
        row = _unwrap(ch)
        change_total += Decimal(str(getattr(row, "change_amount", 0) or 0))

    if change_total > Decimal("0"):
        lines.append("")
        lines.append(_receipt_line("   CHANGE", _fmt_amount(change_total, sym), W))

    # VAT (always shown, even when zero)
    vat_amount = getattr(head, "total_vat_amount", 0)
    lines.append(_receipt_line("   VAT", _fmt_amount(vat_amount, sym), W))

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------
    lines.append(STAR)

    return lines


def format_receipt_text_for_log(document_data: Dict[str, Any]) -> str:
    """Return the full receipt as a single newline-joined string (for logging)."""
    return "\n".join(format_receipt_lines(document_data))


# ---------------------------------------------------------------------------
# Closure (end-of-day) receipt
# ---------------------------------------------------------------------------

def format_closure_lines(closure_data: Dict[str, Any]) -> List[str]:
    """
    Build a thermal-printer-style end-of-day closure report as a list of lines.

    Expected keys in *closure_data*:

    ``closure``
        Closure ORM record (fields: closure_number, closure_unique_id,
        closure_date, closure_start_time, closure_end_time,
        gross_sales_amount, net_sales_amount, total_tax_amount,
        total_discount_amount, total_tip_amount, valid_transaction_count,
        canceled_transaction_count, return_transaction_count,
        suspended_transaction_count, opening_cash_amount,
        closing_cash_amount, expected_cash_amount, cash_difference,
        paid_in_count, paid_in_total, paid_out_count, paid_out_total).

    ``totals``
        The aggregated-totals dict produced by
        ``ClosureEvent._aggregate_closure_totals``.  Relevant sub-dicts:

        * ``by_tax``  — Dict[tuple, dict] keyed by (rate, name, jurisdiction).
        * ``by_payment_type`` — Dict[str, dict] keyed by EventName value.
        * ``by_document_type`` — Dict[str, dict].

    ``currency_code``
        ISO-4217 currency code string (e.g. ``"GBP"``).

    ``cashier_name``   (optional) Closing cashier display name.
    ``pos_name``       (optional) POS register name.
    ``pos_serial``     (optional) POS device serial number.

    Layout (CLOSURE_WIDTH = 42 chars):

        ==========================================
                  END-OF-DAY CLOSURE
        ==========================================
        Closure: #0001    03/01/2025 10:18
        ID: 20250103-0001
        Period: 30/10/2024 13:46 to 03/01/2025 10:18
        Cashier: John Doe
        Register: Main POS
        ==========================================
                                             GBP
        NET SALES
          34  Sales                        417.96
           0  Returns                        0.00
        ------------------------------------------
          Total net sales:                 417.96
          Taxes:                            75.61
          Total gross sum:                 493.57
        ------------------------------------------
        CANCELLED RECEIPTS:                     0
        ------------------------------------------
        CASH BALANCE
          Opening cash:                      0.00
          Gross sales (cash):              493.57
          Deposits (0):                      0.00
          Withdrawals (0):                   0.00
          Change (non-cash):                 0.00
          Tips:                              0.00
        ------------------------------------------
          Cash register balance:           493.57
          Expected:                        493.57
          Difference:                        0.00
        ------------------------------------------
        VAT SUMMARY
          Rate%       Net       Tax     Gross
           0.00%   19.99      0.00    19.99
          19.00%  397.97     75.61   473.58
          Total   417.96     75.61   493.57
        ------------------------------------------
        PAYMENT METHODS
          CASH                             493.57
          Total                            493.57
        ------------------------------------------
        DOCUMENT TYPES
          FISCAL_RECEIPT  34 valid   0 cancel
        ------------------------------------------
        TRANSACTION SUMMARY
          Valid:      34       Cancelled:     0
          Returns:     0       Suspended:     0
        ==========================================
    """
    W = CLOSURE_WIDTH
    SEP = "-" * W
    EQ = "=" * W

    lines: List[str] = []

    if not closure_data:
        lines.append("(no closure data)")
        return lines

    closure = closure_data.get("closure")
    totals: Dict[str, Any] = closure_data.get("totals") or {}
    currency_code = closure_data.get("currency_code") or "GBP"
    cashier_name = closure_data.get("cashier_name") or ""
    pos_name = closure_data.get("pos_name") or ""
    pos_serial = closure_data.get("pos_serial") or ""
    sym = _currency_symbol(currency_code)

    # ------------------------------------------------------------------
    # Helper scoped to this receipt
    # ------------------------------------------------------------------
    def cl(left: str, right: str) -> str:
        return _receipt_line(left, right, W)

    def m(v: Any) -> str:
        return _fmt_amount(v, sym)

    def _dec(v: Any) -> Decimal:
        try:
            return Decimal(str(v)) if v is not None else Decimal("0")
        except Exception:
            return Decimal("0")

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    lines.append(EQ)
    lines.append(f"{'END-OF-DAY CLOSURE':^{W}}")
    lines.append(EQ)

    if closure:
        closure_no = getattr(closure, "closure_number", "")
        unique_id = getattr(closure, "closure_unique_id", "") or ""
        closure_end = getattr(closure, "closure_end_time", None)
        closure_start = getattr(closure, "closure_start_time", None)

        end_str = closure_end.strftime("%d/%m/%Y %H:%M") if closure_end and hasattr(closure_end, "strftime") else datetime.now().strftime("%d/%m/%Y %H:%M")
        lines.append(cl(f"Closure: #{closure_no:04d}" if isinstance(closure_no, int) else f"Closure: #{closure_no}", end_str))

        if unique_id:
            lines.append(f"  ID: {unique_id}")

        if closure_start and hasattr(closure_start, "strftime"):
            start_str = closure_start.strftime("%d/%m/%Y %H:%M")
            lines.append(f"  Period: {start_str} to {end_str}")

    if cashier_name:
        lines.append(f"  Cashier: {cashier_name}"[:W])
    if pos_name:
        lines.append(f"  Register: {pos_name}"[:W])
    if pos_serial:
        lines.append(f"  Serial: {pos_serial}"[:W])

    # ------------------------------------------------------------------
    # Net sales section
    # ------------------------------------------------------------------
    lines.append(EQ)
    lines.append(f"{currency_code.upper():>{W}}")
    lines.append("NET SALES")

    valid_count = totals.get("valid_transaction_count", 0) or 0
    return_count = totals.get("return_transaction_count", 0) or 0
    gross_sales = _dec(totals.get("gross_sales_amount", 0))
    total_tax = _dec(totals.get("total_tax_amount", 0))

    # Net sales = gross - VAT (VAT-inclusive prices)
    net_sales_display = gross_sales - total_tax
    # Returns amount: we don't track this separately yet, show 0
    returns_amount = Decimal("0")

    lines.append(cl(f"  {valid_count:>4}  Sales", m(net_sales_display)))
    lines.append(cl(f"  {return_count:>4}  Returns", m(returns_amount)))
    lines.append(SEP)

    lines.append(cl("  Total net sales:", m(net_sales_display)))
    lines.append(cl("  Taxes:", m(total_tax)))
    lines.append(cl("  Total gross sum:", m(gross_sales)))

    # ------------------------------------------------------------------
    # Cancelled receipts
    # ------------------------------------------------------------------
    lines.append(SEP)
    canceled_count = totals.get("canceled_transaction_count", 0) or 0
    lines.append(cl("CANCELLED RECEIPTS:", str(canceled_count)))

    # ------------------------------------------------------------------
    # Discount summary (if any)
    # ------------------------------------------------------------------
    total_discount = _dec(totals.get("total_discount_amount", 0))
    if total_discount > Decimal("0"):
        lines.append(SEP)
        lines.append("DISCOUNTS")
        lines.append(cl("  Total discount:", m(total_discount)))

    # ------------------------------------------------------------------
    # Cash balance
    # ------------------------------------------------------------------
    lines.append(SEP)
    lines.append("CASH BALANCE")

    opening_cash = _dec(totals.get("opening_cash_amount", 0)) if closure is None else _dec(getattr(closure, "opening_cash_amount", 0))
    expected_cash = _dec(totals.get("expected_cash_amount", 0))
    closing_cash = _dec(totals.get("closing_cash_amount", 0)) if closure is None else _dec(getattr(closure, "closing_cash_amount", 0))
    cash_diff = _dec(totals.get("cash_difference", 0)) if closure is None else _dec(getattr(closure, "cash_difference", 0))

    # Gross cash sales = sum of CASH payments
    cash_sales = Decimal("0")
    by_payment = totals.get("by_payment_type") or {}
    for pt_key, pt_data in by_payment.items():
        if "CASH" in str(pt_key).upper():
            cash_sales += _dec(pt_data.get("amount", 0))

    paid_in_count = totals.get("paid_in_count", 0) or (getattr(closure, "paid_in_count", 0) if closure else 0)
    paid_in_total = _dec(totals.get("paid_in_total", 0)) if not closure else _dec(getattr(closure, "paid_in_total", 0))
    paid_out_count = totals.get("paid_out_count", 0) or (getattr(closure, "paid_out_count", 0) if closure else 0)
    paid_out_total = _dec(totals.get("paid_out_total", 0)) if not closure else _dec(getattr(closure, "paid_out_total", 0))
    total_tip = _dec(totals.get("total_tip_amount", 0))

    lines.append(cl("  Opening cash:", m(opening_cash)))
    lines.append(cl("  Gross sales (cash):", m(cash_sales)))
    lines.append(cl(f"  Deposits ({paid_in_count}):", m(paid_in_total)))
    lines.append(cl(f"  Withdrawals ({paid_out_count}):", m(paid_out_total)))
    # Change for non-cash (change from credit/other payment)
    non_cash_change = Decimal("0")
    lines.append(cl("  Change (non-cash):", m(non_cash_change)))
    lines.append(cl("  Tips:", m(total_tip)))
    lines.append(SEP)
    lines.append(cl("  Cash register balance:", m(cash_sales + opening_cash + paid_in_total - paid_out_total)))
    lines.append(cl("  Expected:", m(expected_cash)))
    lines.append(cl("  Difference:", m(cash_diff)))

    # ------------------------------------------------------------------
    # VAT summary table
    # ------------------------------------------------------------------
    lines.append(SEP)
    lines.append("VAT SUMMARY")
    by_tax = totals.get("by_tax") or {}
    if by_tax:
        # Header row
        lines.append(f"  {'Rate%':<7}  {'Net':>8}  {'Tax':>8}  {'Gross':>8}")
        lines.append(f"  {'-'*7}  {'-'*8}  {'-'*8}  {'-'*8}")

        vat_net_total = Decimal("0")
        vat_tax_total = Decimal("0")
        vat_gross_total = Decimal("0")

        sorted_keys = sorted(by_tax.keys(), key=lambda k: _dec(k[0]) if isinstance(k, tuple) else _dec(k))
        for key in sorted_keys:
            data = by_tax[key]
            rate = _dec(key[0]) if isinstance(key, tuple) and key else Decimal("0")
            tax_amt = _dec(data.get("tax_amount", 0))
            taxable = _dec(data.get("taxable_amount", 0))
            gross = taxable + tax_amt
            rate_str = f"{rate:.2f}%"
            lines.append(f"  {rate_str:>7}  {taxable:>8.2f}  {tax_amt:>8.2f}  {gross:>8.2f}")
            vat_net_total += taxable
            vat_tax_total += tax_amt
            vat_gross_total += gross

        lines.append(f"  {'-'*7}  {'-'*8}  {'-'*8}  {'-'*8}")
        lines.append(f"  {'Total':<7}  {vat_net_total:>8.2f}  {vat_tax_total:>8.2f}  {vat_gross_total:>8.2f}")
    else:
        lines.append(cl("  Total tax:", m(total_tax)))

    # ------------------------------------------------------------------
    # Payment methods
    # ------------------------------------------------------------------
    lines.append(SEP)
    lines.append("PAYMENT METHODS")
    payment_total_all = Decimal("0")
    if by_payment:
        for pt_key, pt_data in sorted(by_payment.items()):
            label = _PAYMENT_TYPE_LABELS.get(str(pt_key), str(pt_key).replace("_", " ").upper())
            amt = _dec(pt_data.get("amount", 0))
            cnt = pt_data.get("count", 0)
            lines.append(cl(f"  {label} ({cnt})", m(amt)))
            payment_total_all += amt
    lines.append(SEP)
    lines.append(cl("  Total", m(payment_total_all)))

    # ------------------------------------------------------------------
    # Document types
    # ------------------------------------------------------------------
    by_doc_type = totals.get("by_document_type") or {}
    if by_doc_type:
        lines.append(SEP)
        lines.append("DOCUMENT TYPES")
        for doc_type, data in sorted(by_doc_type.items()):
            vc = data.get("valid_count", 0)
            cc = data.get("canceled_count", 0)
            label = str(doc_type).replace("_", " ")
            lines.append(f"  {label[:22]:<22}  {vc:>3} valid  {cc:>3} cancel"[:W])

    # ------------------------------------------------------------------
    # Transaction summary
    # ------------------------------------------------------------------
    lines.append(SEP)
    lines.append("TRANSACTION SUMMARY")
    suspended = totals.get("suspended_transaction_count", 0) or (getattr(closure, "suspended_transaction_count", 0) if closure else 0)
    lines.append(f"  {'Valid:':<10}{valid_count:>6}   {'Cancelled:':<12}{canceled_count:>4}")
    lines.append(f"  {'Returns:':<10}{return_count:>6}   {'Suspended:':<12}{suspended:>4}")

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------
    lines.append(EQ)
    return lines


# ---------------------------------------------------------------------------
# Customer / pole-display helpers
# ---------------------------------------------------------------------------

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
