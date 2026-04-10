"""
``CampaignUsage`` audit rows, ``Campaign.total_usage_count`` alignment, and reversal.

Copyright (c) 2025-2026 Ferhat Mousavi
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Mapping, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from core.logger import get_logger
from data_layer.auto_save import AutoSaveModel
from data_layer.model.definition.campaign import Campaign
from data_layer.model.definition.campaign_usage import CampaignUsage
from data_layer.model.definition.coupon import Coupon
from data_layer.model.definition.coupon_usage import CouponUsage
from data_layer.model.definition.transaction_status import TransactionType
from pos.service.campaign.active_campaign_cache import ActiveCampaignCache
from pos.service.campaign.application_policy import CAMPAIGN_DISCOUNT_TYPE_CODE
from pos.service.campaign.coupon_activation_service import CouponActivationService

logger = get_logger(__name__)


def _unwrap(obj: Any) -> Any:
    return obj.unwrap() if isinstance(obj, AutoSaveModel) else obj


def _head(document_data: Mapping[str, Any]) -> Any:
    return _unwrap(document_data["head"])


def _resolve_campaign_by_discount_code(session: Session, discount_code: Optional[str]) -> Optional[Campaign]:
    dc = (discount_code or "").strip().upper()
    if not dc:
        return None
    bundle = ActiveCampaignCache.get()
    if bundle is not None:
        campaigns = sorted(bundle.campaigns, key=lambda x: str(x.code or ""))
    else:
        campaigns = (
            session.query(Campaign)
            .filter(Campaign.is_deleted.is_(False), Campaign.is_active.is_(True))
            .order_by(Campaign.code)
            .all()
        )
    for c in campaigns:
        cc = (c.code or "").strip().upper()
        if not cc:
            continue
        if cc[:15] == dc or cc == dc:
            return c
    return None


class CampaignAuditService:
    """Persist ``CampaignUsage`` after a completed sale and reverse on void/refund hooks."""

    @staticmethod
    def record_after_completed_sale(
        document_data: Dict[str, Any],
        *,
        permanent_head_id: Any,
        fk_store_id: Any,
        fk_cashier_id: Any,
    ) -> None:
        """
        Insert ``CampaignUsage`` for each campaign present on non-cancelled CAMPAIGN discount
        lines and increment ``Campaign.total_usage_count`` once per campaign on this receipt.

        Then record ``CouponUsage`` / per-coupon counters (coupon path does not bump campaign
        totals — those come from this aggregation).
        """
        if not document_data or not document_data.get("head"):
            return

        head_u = _head(document_data)
        tt = (getattr(head_u, "transaction_type", None) or "").lower()
        if tt != TransactionType.SALE.value:
            return

        fk_customer_id = getattr(head_u, "fk_customer_id", None)
        when = datetime.now()

        from data_layer.engine import Engine

        with Engine().get_session() as session:
            totals_by_campaign: Dict[Any, Decimal] = defaultdict(lambda: Decimal("0"))
            for d in document_data.get("discounts") or []:
                row = _unwrap(d)
                if getattr(row, "is_cancel", False):
                    continue
                dt = (getattr(row, "discount_type", None) or "").strip().upper()
                if dt != CAMPAIGN_DISCOUNT_TYPE_CODE.upper():
                    continue
                camp = _resolve_campaign_by_discount_code(
                    session, getattr(row, "discount_code", None)
                )
                if not camp:
                    logger.warning(
                        "[CampaignAuditService] CAMPAIGN discount code %r matched no campaign",
                        getattr(row, "discount_code", None),
                    )
                    continue
                totals_by_campaign[camp.id] += Decimal(
                    str(getattr(row, "discount_amount", 0) or 0)
                )

            coupon_hint = CampaignAuditService._coupon_code_hints_by_campaign(session, document_data)

            for camp_id, amt in totals_by_campaign.items():
                if amt <= 0:
                    continue
                amt_q = amt.quantize(Decimal("0.01"))
                usage = CampaignUsage()
                usage.id = uuid4()
                usage.fk_campaign_id = camp_id
                usage.fk_customer_id = fk_customer_id
                usage.fk_transaction_head_id = permanent_head_id
                usage.fk_store_id = fk_store_id
                usage.fk_cashier_id = fk_cashier_id
                usage.discount_amount = amt_q
                usage.usage_date = when
                usage.coupon_code = coupon_hint.get(camp_id)
                usage.notes = None
                session.add(usage)

                c = session.query(Campaign).filter(Campaign.id == camp_id).first()
                if c:
                    c.total_usage_count = int(getattr(c, "total_usage_count", 0) or 0) + 1

            CouponActivationService.record_coupon_usages_in_session(
                session,
                document_data,
                permanent_head_id=permanent_head_id,
                fk_store_id=fk_store_id,
                fk_cashier_id=fk_cashier_id,
            )
            session.commit()

    @staticmethod
    def _coupon_code_hints_by_campaign(
        session: Session, document_data: Mapping[str, Any]
    ) -> Dict[Any, str]:
        out: Dict[Any, str] = {}
        for sid in document_data.get("applied_coupon_ids") or []:
            try:
                cid = UUID(str(sid))
            except ValueError:
                continue
            c = (
                session.query(Coupon)
                .filter(Coupon.id == cid, Coupon.is_deleted.is_(False))
                .first()
            )
            if not c or not c.fk_campaign_id:
                continue
            if c.fk_campaign_id not in out:
                code = (c.code or "").strip()
                if code:
                    out[c.fk_campaign_id] = code
        return out

    @staticmethod
    def revoke_entitlements_for_transaction_head(
        fk_transaction_head_id: Any,
        *,
        reason: str = "Campaign/coupon reversal (void or refund)",
    ) -> None:
        """
        Soft-delete ``CampaignUsage`` and ``CouponUsage`` for a completed sale and roll back
        ``Campaign.total_usage_count`` / ``Coupon.usage_count``.

        Call this when business rules treat the sale as voided or refunded so campaign benefit
        must not remain counted (e.g. from a dedicated void/refund flow once wired).
        """
        from data_layer.engine import Engine

        with Engine().get_session() as session:
            CampaignAuditService._revoke_in_session(session, fk_transaction_head_id, reason=reason)
            session.commit()

    @staticmethod
    def _revoke_in_session(session: Session, fk_transaction_head_id: Any, *, reason: str) -> None:
        cu_rows = (
            session.query(CampaignUsage)
            .filter(
                CampaignUsage.fk_transaction_head_id == fk_transaction_head_id,
                CampaignUsage.is_deleted.is_(False),
            )
            .all()
        )
        by_camp = Counter(r.fk_campaign_id for r in cu_rows)
        for r in cu_rows:
            r.is_deleted = True
            r.delete_description = reason[:1000] if reason else None
        for camp_id, n in by_camp.items():
            c = session.query(Campaign).filter(Campaign.id == camp_id).first()
            if c:
                c.total_usage_count = max(0, int(getattr(c, "total_usage_count", 0) or 0) - int(n))

        coup_rows = (
            session.query(CouponUsage)
            .filter(
                CouponUsage.fk_transaction_head_id == fk_transaction_head_id,
                CouponUsage.is_deleted.is_(False),
            )
            .all()
        )
        by_coupon = Counter(r.fk_coupon_id for r in coup_rows)
        for r in coup_rows:
            r.is_deleted = True
            r.delete_description = reason[:1000] if reason else None
        for coupon_id, n in by_coupon.items():
            co = session.query(Coupon).filter(Coupon.id == coupon_id).first()
            if co:
                co.usage_count = max(0, int(getattr(co, "usage_count", 0) or 0) - int(n))


__all__ = ["CampaignAuditService"]
