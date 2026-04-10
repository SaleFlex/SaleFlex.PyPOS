"""
Canonical cart snapshot for local campaign evaluation and GATE ``cart_data``.

``schema_version`` 1.0 — stable JSON-oriented dict via :func:`cart_snapshot_to_dict`.

Copyright (c) 2025-2026 Ferhat Mousavi
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union
from uuid import UUID

from core.logger import get_logger

logger = get_logger(__name__)

CART_SNAPSHOT_SCHEMA_VERSION = "1.0"


def _iso_utc(when: datetime) -> str:
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when.astimezone(timezone.utc).isoformat()


def _uuid_str(value: Union[None, str, UUID]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    return str(value)


def _dec_str(value: Any) -> str:
    if value is None:
        return "0"
    try:
        return str(Decimal(str(value)))
    except Exception:
        logger.debug("cart_snapshot: non-decimal value %r treated as 0", value)
        return "0"


@dataclass
class CartLineSnapshot:
    """One sale line after line-level pricing; campaign rules use these fields."""

    line_id: str
    line_no: int
    fk_product_id: Optional[str]
    fk_department_main_group_id: str
    product_code: Optional[str]
    product_name: Optional[str]
    quantity: str
    unit_price: str
    line_total: str
    is_cancel: bool
    is_voided: bool
    vat_rate: str


@dataclass
class CartTotalsSnapshot:
    """Money buckets for thresholds; strings are decimal serialisations."""

    merchandise_subtotal: str
    head_total_amount: str
    head_total_discount_amount: str
    document_discount_total: str
    document_discount_non_campaign_total: str


@dataclass
class CartSnapshot:
    """
    Full cart context for `apply_campaign` / local engine / GATE calculate API.

    * ``customer_segment_codes`` — optional hint (e.g. from `CustomerSegmentService`);
      empty until wired.
    * ``active_coupon_codes`` — scanned or entered coupons for this document; empty
      until coupon flow exists.
    """

    schema_version: str
    evaluated_at: str
    transaction_head_temp_id: str
    transaction_unique_id: str
    pos_id: int
    fk_store_id: str
    fk_customer_id: str
    loyalty_member_id: Optional[str]
    currency_code: str
    lines: List[CartLineSnapshot] = field(default_factory=list)
    totals: Optional[CartTotalsSnapshot] = None
    customer_segment_codes: List[str] = field(default_factory=list)
    active_coupon_codes: List[str] = field(default_factory=list)


def _sum_merchandise_subtotal(lines: Sequence[CartLineSnapshot]) -> Decimal:
    total = Decimal("0")
    for ln in lines:
        if ln.is_cancel or ln.is_voided:
            continue
        total += Decimal(ln.line_total)
    return total


def _sum_document_discounts(
    discounts: Sequence[Any],
    *,
    exclude_campaign_type: bool,
    campaign_type_code: str,
) -> tuple[Decimal, Decimal]:
    """Returns (all_non_cancelled, subset excluding CAMPAIGN type if excluded)."""
    all_d = Decimal("0")
    non_camp = Decimal("0")
    code_u = campaign_type_code.strip().upper()
    for d in discounts:
        if getattr(d, "is_cancel", False):
            continue
        amt = getattr(d, "discount_amount", None)
        try:
            part = Decimal(str(amt)) if amt is not None else Decimal("0")
        except Exception:
            part = Decimal("0")
        all_d += part
        dt = getattr(d, "discount_type", None) or ""
        if not (exclude_campaign_type and str(dt).strip().upper() == code_u):
            non_camp += part
    return all_d, non_camp


def build_cart_snapshot_from_document_data(
    document_data: Mapping[str, Any],
    *,
    evaluated_at: Optional[datetime] = None,
    customer_segment_codes: Optional[Sequence[str]] = None,
    active_coupon_codes: Optional[Sequence[str]] = None,
    campaign_discount_type_code: str = "CAMPAIGN",
) -> Optional[CartSnapshot]:
    """
    Build a snapshot from ``DocumentManager``-style ``document_data`` (``head``,
    ``products``, ``discounts``).

    Returns ``None`` if there is no usable head.
    """
    head = document_data.get("head")
    if head is None:
        return None

    when = evaluated_at or datetime.now(timezone.utc)

    products = document_data.get("products") or []
    discounts = document_data.get("discounts") or []

    lines: List[CartLineSnapshot] = []
    for p in products:
        lines.append(
            CartLineSnapshot(
                line_id=_uuid_str(getattr(p, "id", None)) or "",
                line_no=int(getattr(p, "line_no", 0) or 0),
                fk_product_id=_uuid_str(getattr(p, "fk_product_id", None)),
                fk_department_main_group_id=_uuid_str(
                    getattr(p, "fk_department_main_group_id", None)
                )
                or "",
                product_code=getattr(p, "product_code", None),
                product_name=getattr(p, "product_name", None),
                quantity=_dec_str(getattr(p, "quantity", None)),
                unit_price=_dec_str(getattr(p, "unit_price", None)),
                line_total=_dec_str(getattr(p, "total_price", None)),
                is_cancel=bool(getattr(p, "is_cancel", False)),
                is_voided=bool(getattr(p, "is_voided", False)),
                vat_rate=_dec_str(getattr(p, "vat_rate", None)),
            )
        )

    merch = _sum_merchandise_subtotal(lines)
    doc_all, doc_non_camp = _sum_document_discounts(
        discounts,
        exclude_campaign_type=True,
        campaign_type_code=campaign_discount_type_code,
    )

    totals = CartTotalsSnapshot(
        merchandise_subtotal=_dec_str(merch),
        head_total_amount=_dec_str(getattr(head, "total_amount", None)),
        head_total_discount_amount=_dec_str(getattr(head, "total_discount_amount", None)),
        document_discount_total=_dec_str(doc_all),
        document_discount_non_campaign_total=_dec_str(doc_non_camp),
    )

    return CartSnapshot(
        schema_version=CART_SNAPSHOT_SCHEMA_VERSION,
        evaluated_at=_iso_utc(when),
        transaction_head_temp_id=_uuid_str(getattr(head, "id", None)) or "",
        transaction_unique_id=str(getattr(head, "transaction_unique_id", "") or ""),
        pos_id=int(getattr(head, "pos_id", 0) or 0),
        fk_store_id=_uuid_str(getattr(head, "fk_store_id", None)) or "",
        fk_customer_id=_uuid_str(getattr(head, "fk_customer_id", None)) or "",
        loyalty_member_id=_uuid_str(getattr(head, "loyalty_member_id", None)),
        currency_code=str(getattr(head, "base_currency", None) or "USD"),
        lines=lines,
        totals=totals,
        customer_segment_codes=list(customer_segment_codes or ()),
        active_coupon_codes=list(active_coupon_codes or ()),
    )


def cart_snapshot_to_dict(snapshot: CartSnapshot) -> Dict[str, Any]:
    """Recursive dict suitable for JSON and GATE; all keys present for version 1.0."""
    d = asdict(snapshot)
    return d


def normalize_cart_data_for_campaign_request(
    cart_data: Mapping[str, Any],
    *,
    evaluated_at: Optional[datetime] = None,
    customer_segment_codes: Optional[Sequence[str]] = None,
    active_coupon_codes: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """
    If ``cart_data`` is already canonical (``schema_version`` 1.0), return a plain
    dict copy of it. If it is ``document_data`` (has ``head`` and ``products``),
    build the canonical snapshot dict. Otherwise return ``dict(cart_data)`` unchanged
    (legacy / stub callers).
    """
    if cart_data.get("schema_version") == CART_SNAPSHOT_SCHEMA_VERSION:
        return dict(cart_data)
    if "head" in cart_data and "products" in cart_data:
        snap = build_cart_snapshot_from_document_data(
            cart_data,
            evaluated_at=evaluated_at,
            customer_segment_codes=customer_segment_codes,
            active_coupon_codes=active_coupon_codes,
        )
        if snap is None:
            return dict(cart_data)
        return cart_snapshot_to_dict(snap)
    return dict(cart_data)


__all__ = [
    "CART_SNAPSHOT_SCHEMA_VERSION",
    "CartLineSnapshot",
    "CartTotalsSnapshot",
    "CartSnapshot",
    "build_cart_snapshot_from_document_data",
    "cart_snapshot_to_dict",
    "normalize_cart_data_for_campaign_request",
]
