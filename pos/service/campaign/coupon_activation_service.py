"""
Validate coupon codes / barcodes and track redemptions via ``Coupon`` / ``CouponUsage``.

Copyright (c) 2025-2026 Ferhat Mousavi
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple
from uuid import UUID, uuid4

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from core.logger import get_logger
from data_layer.auto_save import AutoSaveModel
from data_layer.model.definition.campaign import Campaign
from data_layer.model.definition.coupon import Coupon
from data_layer.model.definition.coupon_usage import CouponUsage
from data_layer.model.definition.transaction_status import TransactionType
from pos.service.campaign.application_policy import CAMPAIGN_DISCOUNT_TYPE_CODE

logger = get_logger(__name__)


def _unwrap(obj: Any) -> Any:
    return obj.unwrap() if isinstance(obj, AutoSaveModel) else obj


def _head(document_data: Mapping[str, Any]) -> Any:
    return _unwrap(document_data["head"])


class CouponActivationService:
    """POS-side coupon validation and post-sale ``CouponUsage`` recording."""

    @staticmethod
    def _now_cmp() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    @staticmethod
    def _coupon_valid_dates(coupon: Coupon, when: datetime) -> bool:
        sd = coupon.start_date
        ed = coupon.end_date
        if sd is not None:
            if getattr(sd, "tzinfo", None) is not None:
                sd = sd.astimezone(timezone.utc).replace(tzinfo=None)
            if when < sd:
                return False
        if ed is not None:
            if getattr(ed, "tzinfo", None) is not None:
                ed = ed.astimezone(timezone.utc).replace(tzinfo=None)
            if when > ed:
                return False
        return True

    @staticmethod
    def _usage_count_for_coupon(session: Session, fk_coupon_id: Any) -> int:
        return (
            session.query(func.count(CouponUsage.id))
            .filter(
                CouponUsage.fk_coupon_id == fk_coupon_id,
                CouponUsage.is_deleted.is_(False),
            )
            .scalar()
            or 0
        )

    @staticmethod
    def _usage_count_coupon_customer(
        session: Session, fk_coupon_id: Any, fk_customer_id: Any
    ) -> int:
        if fk_customer_id is None:
            return 0
        return (
            session.query(func.count(CouponUsage.id))
            .filter(
                CouponUsage.fk_coupon_id == fk_coupon_id,
                CouponUsage.fk_customer_id == fk_customer_id,
                CouponUsage.is_deleted.is_(False),
            )
            .scalar()
            or 0
        )

    @staticmethod
    def find_coupon_by_raw(session: Session, raw: str) -> Optional[Coupon]:
        token = (raw or "").strip()
        if not token:
            return None
        token_u = token.upper()
        return (
            session.query(Coupon)
            .filter(
                Coupon.is_deleted.is_(False),
                Coupon.is_active.is_(True),
                or_(
                    func.upper(Coupon.code) == token_u,
                    Coupon.barcode == token,
                    Coupon.barcode == token_u,
                ),
            )
            .first()
        )

    @staticmethod
    def validate_for_open_sale(
        session: Session,
        raw: str,
        document_data: Dict[str, Any],
    ) -> Tuple[bool, str, Optional[UUID]]:
        """
        Return (ok, message, coupon_id).

        Validates ``Coupon`` row (dates, limits, PERSONAL / SINGLE_USE) and that the
        linked ``Campaign`` has ``requires_coupon`` (coupon-backed activation only).
        """
        if not document_data or not document_data.get("head"):
            return False, "No active sale document.", None

        head = _head(document_data)
        if (getattr(head, "transaction_type", None) or "").lower() != TransactionType.SALE.value:
            return False, "Coupons apply only to sale receipts.", None

        token = (raw or "").strip()
        if not token:
            return False, "Enter a coupon code or scan a barcode.", None

        coupon = CouponActivationService.find_coupon_by_raw(session, token)
        if not coupon:
            return False, "Coupon code not found.", None

        campaign = (
            session.query(Campaign)
            .filter(
                Campaign.id == coupon.fk_campaign_id,
                Campaign.is_deleted.is_(False),
                Campaign.is_active.is_(True),
            )
            .first()
        )
        if not campaign:
            return False, "Campaign for this coupon is not available.", None
        if not campaign.requires_coupon:
            return False, "This promotion does not use coupon activation.", None

        when = CouponActivationService._now_cmp()
        if not CouponActivationService._coupon_valid_dates(coupon, when):
            return False, "Coupon is outside its valid dates.", None

        if not CouponActivationService._coupon_valid_dates_campaign(campaign, when):
            return False, "Campaign is outside its valid dates.", None

        cust_id = getattr(head, "fk_customer_id", None)
        ctype = (coupon.coupon_type or "").strip().upper()
        if ctype == "PERSONAL":
            if coupon.fk_customer_id is None:
                return False, "Personal coupon is not assigned to a customer.", None
            if cust_id is None or UUID(str(coupon.fk_customer_id)) != UUID(str(cust_id)):
                return False, "This coupon is tied to another customer.", None

        lim = coupon.usage_limit
        if lim is not None and int(lim) > 0:
            used = CouponActivationService._usage_count_for_coupon(session, coupon.id)
            if used >= int(lim):
                return False, "Coupon usage limit reached.", None

        if ctype == "SINGLE_USE":
            if coupon.fk_customer_id is not None:
                n = CouponActivationService._usage_count_coupon_customer(
                    session, coupon.id, cust_id
                )
                if n >= 1:
                    return False, "This single-use coupon was already used.", None
            else:
                n = CouponActivationService._usage_count_for_coupon(session, coupon.id)
                if n >= 1:
                    return False, "This single-use coupon was already used.", None

        applied: List[str] = document_data.setdefault("applied_coupon_ids", [])
        sid = str(coupon.id)
        if sid in applied:
            return False, "This coupon is already applied to the sale.", None

        return True, str(coupon.code or "").strip() or (campaign.code or ""), coupon.id

    @staticmethod
    def _coupon_valid_dates_campaign(campaign: Campaign, when: datetime) -> bool:
        sd = campaign.start_date
        ed = campaign.end_date
        d = when.date()
        if sd is not None:
            sdd = sd.date() if hasattr(sd, "date") else sd
            if d < sdd:
                return False
        if ed is not None:
            edd = ed.date() if hasattr(ed, "date") else ed
            if d > edd:
                return False
        return True

    @staticmethod
    def evaluation_campaign_codes(document_data: Optional[Dict[str, Any]]) -> Set[str]:
        """
        Uppercased ``Campaign.code`` values derived from ``applied_coupon_ids`` for
        ``CampaignService.evaluate_proposals`` (``requires_coupon`` gate).
        """
        out: Set[str] = set()
        if not document_data:
            return out
        ids: Sequence[str] = document_data.get("applied_coupon_ids") or []
        if not ids:
            return out
        try:
            from data_layer.engine import Engine

            with Engine().get_session() as session:
                for sid in ids:
                    try:
                        cid = UUID(str(sid))
                    except ValueError:
                        continue
                    c = (
                        session.query(Coupon)
                        .filter(Coupon.id == cid, Coupon.is_deleted.is_(False))
                        .first()
                    )
                    if not c:
                        continue
                    camp = (
                        session.query(Campaign)
                        .filter(Campaign.id == c.fk_campaign_id, Campaign.is_deleted.is_(False))
                        .first()
                    )
                    if camp and camp.code:
                        out.add(str(camp.code).strip().upper())
        except Exception as exc:
            logger.error("[CouponActivationService] evaluation_campaign_codes: %s", exc)
        return out

    @staticmethod
    def record_usages_after_completed_sale(
        document_data: Dict[str, Any],
        *,
        permanent_head_id: Any,
        fk_store_id: Any,
        fk_cashier_id: Any,
    ) -> None:
        """
        After permanent ``TransactionHead`` is created, insert ``CouponUsage`` rows and
        bump ``Coupon.usage_count`` for coupons that contributed to this sale.

        Allocates CAMPAIGN discount totals per campaign across applied coupons for that campaign.
        """
        ids = list(document_data.get("applied_coupon_ids") or [])
        if not ids:
            return

        head_u = _head(document_data)
        fk_customer_id = getattr(head_u, "fk_customer_id", None)
        when = datetime.now()

        from data_layer.engine import Engine

        with Engine().get_session() as session:

            def _campaign_discount_total(camp_id: Any) -> Decimal:
                total = Decimal("0")
                camp = session.query(Campaign).filter(Campaign.id == camp_id).first()
                if not camp or not camp.code:
                    return total
                key = str(camp.code).strip().upper()[:15]
                for d in document_data.get("discounts") or []:
                    row = _unwrap(d)
                    if getattr(row, "is_cancel", False):
                        continue
                    dt = (getattr(row, "discount_type", None) or "").strip().upper()
                    if dt != CAMPAIGN_DISCOUNT_TYPE_CODE.upper():
                        continue
                    dc = (getattr(row, "discount_code", None) or "").strip().upper()
                    if dc == key:
                        total += Decimal(str(getattr(row, "discount_amount", 0) or 0))
                return total

            by_campaign: Dict[Any, List[Coupon]] = defaultdict(list)
            for sid in ids:
                try:
                    cid = UUID(str(sid))
                except ValueError:
                    continue
                c = (
                    session.query(Coupon)
                    .filter(Coupon.id == cid, Coupon.is_deleted.is_(False))
                    .first()
                )
                if c:
                    by_campaign[c.fk_campaign_id].append(c)

            for camp_id, coupons in by_campaign.items():
                if not coupons:
                    continue
                amt_total = _campaign_discount_total(camp_id)
                if amt_total <= 0:
                    continue
                share = (amt_total / Decimal(len(coupons))).quantize(Decimal("0.01"))
                for coupon in coupons:
                    usage = CouponUsage()
                    usage.id = uuid4()
                    usage.fk_coupon_id = coupon.id
                    usage.fk_customer_id = fk_customer_id
                    usage.fk_transaction_head_id = permanent_head_id
                    usage.fk_store_id = fk_store_id
                    usage.fk_cashier_id = fk_cashier_id
                    usage.discount_amount = share
                    usage.usage_date = when
                    usage.notes = None
                    session.add(usage)

                    row = session.query(Coupon).filter(Coupon.id == coupon.id).first()
                    if row:
                        row.usage_count = int(getattr(row, "usage_count", 0) or 0) + 1

                camp = session.query(Campaign).filter(Campaign.id == camp_id).first()
                if camp:
                    camp.total_usage_count = int(getattr(camp, "total_usage_count", 0) or 0) + len(
                        coupons
                    )

            session.commit()


__all__ = ["CouponActivationService"]
