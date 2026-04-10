"""
Apply evaluated campaign proposals to ``document_data`` as ``TransactionDiscountTemp`` rows.

Cancels prior CAMPAIGN lines, re-evaluates, inserts new rows, and recomputes
``head.total_discount_amount`` from all non-cancelled discount lines.

Copyright (c) 2025-2026 Ferhat Mousavi
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Mapping, Optional, Sequence
from uuid import uuid4

from core.logger import get_logger
from data_layer.auto_save import AutoSaveModel
from data_layer.model.definition.transaction_discount_temp import TransactionDiscountTemp
from data_layer.model.definition.transaction_status import TransactionStatus, TransactionType
from pos.service.campaign.application_policy import CAMPAIGN_DISCOUNT_TYPE_CODE
from pos.service.campaign.campaign_service import CampaignDiscountProposal, CampaignService

logger = get_logger(__name__)


def gate_manages_campaign() -> bool:
    """True when GATE is enabled and configured to own campaign pricing."""
    try:
        from settings.settings import Settings

        g = getattr(Settings(), "gate", None) or {}
        return bool(g.get("enabled")) and bool(g.get("manages_campaign"))
    except Exception:
        return False


def _unwrap(obj: Any) -> Any:
    return obj.unwrap() if isinstance(obj, AutoSaveModel) else obj


def _head(document_data: Mapping[str, Any]) -> Any:
    return _unwrap(document_data["head"])


def recompute_head_total_discount_amount(document_data: Dict[str, Any]) -> None:
    """Set ``head.total_discount_amount`` from active (non-cancelled) temp discount rows."""
    if not document_data or not document_data.get("head"):
        return
    head = _head(document_data)
    total = Decimal("0")
    for d in document_data.get("discounts") or []:
        row = _unwrap(d)
        if getattr(row, "is_cancel", False):
            continue
        amt = getattr(row, "discount_amount", None)
        if amt is None:
            continue
        total += Decimal(str(amt))
    head.total_discount_amount = total
    if hasattr(head, "save"):
        head.save()


def _next_discount_line_no(document_data: Dict[str, Any]) -> int:
    mx = 0
    for d in document_data.get("discounts") or []:
        row = _unwrap(d)
        mx = max(mx, int(getattr(row, "line_no", 0) or 0))
    return mx + 1


def _cancel_existing_campaign_discounts(document_data: Dict[str, Any]) -> None:
    code_u = CAMPAIGN_DISCOUNT_TYPE_CODE.strip().upper()
    for d in list(document_data.get("discounts") or []):
        row = _unwrap(d)
        dt = (getattr(row, "discount_type", None) or "").strip().upper()
        if dt != code_u:
            continue
        if getattr(row, "is_cancel", False):
            continue
        row.is_cancel = True
        if hasattr(row, "save"):
            row.save()


def _quantize_rate(rate: Optional[Decimal]) -> Optional[Decimal]:
    if rate is None:
        return None
    try:
        return Decimal(str(rate)).quantize(Decimal("0.01"))
    except Exception:
        return None


def _persist_proposals(
    document_data: Dict[str, Any],
    proposals: Sequence[CampaignDiscountProposal],
) -> None:
    if not proposals:
        return
    head = _head(document_data)
    line_no = _next_discount_line_no(document_data)
    document_data.setdefault("discounts", [])
    for pr in proposals:
        disc = TransactionDiscountTemp()
        disc.id = uuid4()
        disc.fk_transaction_head_id = head.id
        disc.fk_transaction_product_id = pr.fk_transaction_product_temp_id
        disc.fk_transaction_payment_id = None
        disc.fk_transaction_department_id = None
        disc.line_no = line_no
        line_no += 1
        disc.discount_type = pr.temp_discount_type
        disc.discount_amount = pr.discount_amount
        disc.discount_rate = _quantize_rate(pr.discount_rate)
        disc.discount_code = (pr.discount_code or "")[:15] or None
        disc.is_cancel = False
        disc.create()
        document_data["discounts"].append(disc)


def sync_campaign_discounts_on_document(
    document_data: Optional[Dict[str, Any]],
    *,
    active_coupon_codes: Optional[Sequence[str]] = None,
) -> None:
    """
    Refresh CAMPAIGN discount lines on the open sale document.

    Skips when GATE manages campaigns. Only runs for ACTIVE sale receipts.
    """
    if not document_data or not document_data.get("head"):
        return
    if gate_manages_campaign():
        return

    head = _head(document_data)
    tx_type = (getattr(head, "transaction_type", None) or "").lower()
    if tx_type != TransactionType.SALE.value:
        return
    if getattr(head, "transaction_status", None) != TransactionStatus.ACTIVE.value:
        return

    try:
        _cancel_existing_campaign_discounts(document_data)
        recompute_head_total_discount_amount(document_data)

        proposals: List[CampaignDiscountProposal] = CampaignService.evaluate_proposals(
            document_data,
            active_coupon_codes=active_coupon_codes,
        )
        _persist_proposals(document_data, proposals)
        recompute_head_total_discount_amount(document_data)
    except Exception as exc:
        logger.error("[campaign_document_sync] sync_campaign_discounts_on_document: %s", exc)


__all__ = [
    "gate_manages_campaign",
    "recompute_head_total_discount_amount",
    "sync_campaign_discounts_on_document",
]
