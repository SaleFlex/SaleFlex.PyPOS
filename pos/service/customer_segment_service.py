"""
Automatic customer segment assignment from ``CustomerSegment.criteria_json``.

Segments are for marketing / campaign targeting. Loyalty tier stays on
``CustomerLoyalty``; combine both in ``marketing_profile`` when needed.

Copyright (c) 2025-2026 Ferhat Mousavi
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SegmentEvaluationContext:
    """Snapshot used only for rule evaluation (not persisted)."""

    annual_spent: Decimal
    lifetime_spent: Decimal
    total_purchases: int
    last_purchase_date: Optional[datetime]
    registered_at: Optional[datetime]
    date_of_birth: Optional[date]
    preferences_vip: bool


class CustomerSegmentService:
    """Evaluates ``criteria_json`` and maintains ``CustomerSegmentMember`` rows with ``assigned_by=AUTO``."""

    _AUTO = "AUTO"

    @staticmethod
    def _safe_json(text: Optional[str]) -> Dict[str, Any]:
        if not text or not str(text).strip():
            return {}
        try:
            data = json.loads(text)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _preferences_vip_flag(customer: Any) -> bool:
        raw = getattr(customer, "preferences_json", None)
        data = CustomerSegmentService._safe_json(raw)
        return bool(data.get("vip") or data.get("is_vip") or data.get("marketing_vip"))

    @staticmethod
    def _aggregate_sales_from_heads(session: Session, customer_id: UUID) -> tuple[Decimal, Decimal, int, Optional[datetime]]:
        from data_layer.model.definition.transaction_head import TransactionHead
        from data_layer.model.definition.transaction_status import TransactionStatus, TransactionType

        base = [
            TransactionHead.fk_customer_id == customer_id,
            TransactionHead.is_deleted.is_(False),
            TransactionHead.is_cancel.is_(False),
            TransactionHead.transaction_status == TransactionStatus.COMPLETED.value,
            TransactionHead.transaction_type == TransactionType.SALE.value,
        ]
        lifetime = session.query(func.coalesce(func.sum(TransactionHead.total_amount), 0)).filter(*base).scalar()
        lifetime_dec = Decimal(str(lifetime or 0))
        count = session.query(func.count(TransactionHead.id)).filter(*base).scalar() or 0
        last_dt = session.query(func.max(TransactionHead.transaction_date_time)).filter(*base).scalar()

        y = datetime.now().year
        annual = (
            session.query(func.coalesce(func.sum(TransactionHead.total_amount), 0))
            .filter(
                *base,
                extract("year", TransactionHead.transaction_date_time) == y,
            )
            .scalar()
        )
        annual_dec = Decimal(str(annual or 0))
        return annual_dec, lifetime_dec, int(count), last_dt

    @staticmethod
    def build_evaluation_context(session: Session, customer: Any) -> SegmentEvaluationContext:
        from data_layer.model.definition.customer_loyalty import CustomerLoyalty

        prefs_vip = CustomerSegmentService._preferences_vip_flag(customer)
        mem = (
            session.query(CustomerLoyalty)
            .filter(
                CustomerLoyalty.fk_customer_id == customer.id,
                CustomerLoyalty.is_deleted.is_(False),
            )
            .first()
        )
        if mem:
            return SegmentEvaluationContext(
                annual_spent=Decimal(str(mem.annual_spent or 0)),
                lifetime_spent=Decimal(str(mem.total_spent or 0)),
                total_purchases=int(mem.total_purchases or 0),
                last_purchase_date=mem.last_activity_date,
                registered_at=getattr(customer, "created_at", None),
                date_of_birth=getattr(customer, "date_of_birth", None),
                preferences_vip=prefs_vip,
            )

        annual, lifetime, count, last_dt = CustomerSegmentService._aggregate_sales_from_heads(session, customer.id)
        return SegmentEvaluationContext(
            annual_spent=annual,
            lifetime_spent=lifetime,
            total_purchases=count,
            last_purchase_date=last_dt,
            registered_at=getattr(customer, "created_at", None),
            date_of_birth=getattr(customer, "date_of_birth", None),
            preferences_vip=prefs_vip,
        )

    @staticmethod
    def _days_since(dt: Optional[Any]) -> Optional[int]:
        if dt is None:
            return None
        if isinstance(dt, datetime):
            start = dt.date()
        elif isinstance(dt, date):
            start = dt
        else:
            return None
        return max(0, (datetime.now().date() - start).days)

    @staticmethod
    def segment_matches(segment: Any, ctx: SegmentEvaluationContext, customer: Any) -> bool:
        crit = CustomerSegmentService._safe_json(getattr(segment, "criteria_json", None))
        stype = (getattr(segment, "segment_type", None) or "").upper()

        if stype == "VIP":
            min_a = crit.get("min_annual_spending")
            min_l = crit.get("min_lifetime_spending")
            spend_ok = False
            if min_a is not None and ctx.annual_spent >= Decimal(str(min_a)):
                spend_ok = True
            if min_l is not None and ctx.lifetime_spent >= Decimal(str(min_l)):
                spend_ok = True
            if crit.get("honor_preferences_vip") and ctx.preferences_vip:
                return True
            return spend_ok

        if stype == "NEW_CUSTOMER":
            max_days = crit.get("days_since_registration")
            max_purchases = crit.get("max_purchases")
            if ctx.registered_at is None:
                return False
            age_days = CustomerSegmentService._days_since(ctx.registered_at)
            if age_days is None or max_days is None:
                return False
            if age_days > int(max_days):
                return False
            if max_purchases is not None and ctx.total_purchases > int(max_purchases):
                return False
            return True

        if stype == "FREQUENT_BUYER":
            min_total = crit.get("min_total_purchases")
            if min_total is None:
                return False
            return ctx.total_purchases >= int(min_total)

        if stype == "HIGH_VALUE":
            min_avg = crit.get("min_avg_transaction")
            min_ann = crit.get("min_annual_spending")
            ok = True
            if min_ann is not None:
                ok = ok and (ctx.annual_spent >= Decimal(str(min_ann)))
            if min_avg is not None:
                if ctx.total_purchases <= 0:
                    ok = False
                else:
                    avg = ctx.lifetime_spent / ctx.total_purchases
                    ok = ok and (avg >= Decimal(str(min_avg)))
            return ok

        if stype == "INACTIVE":
            min_idle = crit.get("days_since_last_purchase")
            if min_idle is None:
                return False
            if ctx.total_purchases <= 0 or ctx.last_purchase_date is None:
                return False
            idle = CustomerSegmentService._days_since(ctx.last_purchase_date)
            if idle is None:
                return False
            return idle >= int(min_idle)

        if stype == "BIRTHDAY":
            if crit.get("birthday_month") != "current" and crit.get("birthday_month") is not None:
                return False
            dob = ctx.date_of_birth
            if dob is None:
                return False
            return dob.month == datetime.now().month

        # CUSTOM or unknown: optional generic keys with join all
        join_any = crit.get("join", "all") == "any"
        checks: List[bool] = []
        if "min_annual_spending" in crit:
            checks.append(ctx.annual_spent >= Decimal(str(crit["min_annual_spending"])))
        if "min_lifetime_spending" in crit:
            checks.append(ctx.lifetime_spent >= Decimal(str(crit["min_lifetime_spending"])))
        if "min_total_purchases" in crit:
            checks.append(ctx.total_purchases >= int(crit["min_total_purchases"]))
        if not checks:
            return False
        return any(checks) if join_any else all(checks)

    @staticmethod
    def _refresh_segment_count(session: Session, segment_id: UUID) -> None:
        from data_layer.model.definition.customer_segment import CustomerSegment
        from data_layer.model.definition.customer_segment_member import CustomerSegmentMember

        n = (
            session.query(func.count(CustomerSegmentMember.id))
            .filter(
                CustomerSegmentMember.fk_customer_segment_id == segment_id,
                CustomerSegmentMember.is_active.is_(True),
                CustomerSegmentMember.is_deleted.is_(False),
            )
            .scalar()
        )
        seg = session.query(CustomerSegment).filter(CustomerSegment.id == segment_id).first()
        if seg:
            seg.customer_count = int(n or 0)

    @staticmethod
    def _is_auto_managed_member(row: Any) -> bool:
        ab = (getattr(row, "assigned_by", None) or "").upper()
        return ab in ("", "AUTO", "SYSTEM")

    @staticmethod
    def sync_memberships_for_customer(session: Session, customer_id: UUID) -> None:
        from data_layer.model.definition.customer import Customer
        from data_layer.model.definition.customer_segment import CustomerSegment
        from data_layer.model.definition.customer_segment_member import CustomerSegmentMember

        customer = session.query(Customer).filter(Customer.id == customer_id).first()
        if not customer or customer.is_walkin or customer.is_deleted:
            return

        ctx = CustomerSegmentService.build_evaluation_context(session, customer)
        segments = (
            session.query(CustomerSegment)
            .filter(CustomerSegment.is_active.is_(True), CustomerSegment.is_deleted.is_(False))
            .order_by(CustomerSegment.display_order.asc(), CustomerSegment.name.asc())
            .all()
        )
        touched: List[UUID] = []

        for seg in segments:
            matches = CustomerSegmentService.segment_matches(seg, ctx, customer)
            row = (
                session.query(CustomerSegmentMember)
                .filter(
                    CustomerSegmentMember.fk_customer_id == customer.id,
                    CustomerSegmentMember.fk_customer_segment_id == seg.id,
                    CustomerSegmentMember.is_deleted.is_(False),
                )
                .order_by(CustomerSegmentMember.assigned_date.desc())
                .first()
            )

            if matches:
                if row is None:
                    session.add(
                        CustomerSegmentMember(
                            fk_customer_id=customer.id,
                            fk_customer_segment_id=seg.id,
                            assigned_by=CustomerSegmentService._AUTO,
                            assignment_reason="criteria_json",
                            is_active=True,
                        )
                    )
                    touched.append(seg.id)
                elif not row.is_active:
                    if CustomerSegmentService._is_auto_managed_member(row):
                        row.is_active = True
                        row.assigned_by = CustomerSegmentService._AUTO
                        touched.append(seg.id)
            else:
                if row and row.is_active and CustomerSegmentService._is_auto_managed_member(row):
                    row.is_active = False
                    touched.append(seg.id)

        for sid in touched:
            CustomerSegmentService._refresh_segment_count(session, sid)

    @staticmethod
    def sync_for_customer_id(customer_id: UUID) -> None:
        """Open a short session, run rules, commit (safe to call from UI after save)."""
        from data_layer.engine import Engine

        cid = UUID(str(customer_id)) if not isinstance(customer_id, UUID) else customer_id
        try:
            engine = Engine()
            with engine.get_session() as session:
                CustomerSegmentService.sync_memberships_for_customer(session, cid)
                session.commit()
        except Exception as exc:
            logger.error("[SEGMENT] sync_for_customer_id %s: %s", customer_id, exc)

    @staticmethod
    def on_sale_transaction_completed(document_data: Optional[Dict[str, Any]]) -> None:
        """After a completed sale is persisted, refresh auto segment memberships."""
        if not document_data or not document_data.get("head"):
            return
        try:
            from pos.service.loyalty_service import LoyaltyService
            from data_layer.model.definition.transaction_status import TransactionType

            head = LoyaltyService._unwrap_document_head(document_data["head"])
            tx_type = (getattr(head, "transaction_type", None) or "").lower()
            if tx_type != TransactionType.SALE.value:
                return
            cid = getattr(head, "fk_customer_id", None)
            if not cid:
                return
            CustomerSegmentService.sync_for_customer_id(cid)
        except Exception as exc:
            logger.error("[SEGMENT] on_sale_transaction_completed: %s", exc)

    @staticmethod
    def marketing_profile(session: Session, customer_id: UUID) -> Dict[str, Any]:
        """
        Read-only view for campaign targeting: active segment codes plus loyalty tier code.
        Keeps tier data out of ``CustomerSegment`` / ``criteria_json``.
        """
        from data_layer.model.definition.customer_segment_member import CustomerSegmentMember
        from data_layer.model.definition.customer_segment import CustomerSegment
        from data_layer.model.definition.customer_loyalty import CustomerLoyalty
        from data_layer.model.definition.loyalty_tier import LoyaltyTier

        codes = (
            session.query(CustomerSegment.code)
            .join(
                CustomerSegmentMember,
                CustomerSegmentMember.fk_customer_segment_id == CustomerSegment.id,
            )
            .filter(
                CustomerSegmentMember.fk_customer_id == customer_id,
                CustomerSegmentMember.is_active.is_(True),
                CustomerSegmentMember.is_deleted.is_(False),
                CustomerSegment.is_deleted.is_(False),
            )
            .all()
        )
        segment_codes = [c[0] for c in codes if c[0]]

        tier_code = None
        mem = (
            session.query(CustomerLoyalty)
            .filter(
                CustomerLoyalty.fk_customer_id == customer_id,
                CustomerLoyalty.is_deleted.is_(False),
            )
            .first()
        )
        if mem and mem.fk_loyalty_tier_id:
            tier = session.query(LoyaltyTier).filter(LoyaltyTier.id == mem.fk_loyalty_tier_id).first()
            if tier:
                tier_code = tier.code

        return {"segment_codes": segment_codes, "loyalty_tier_code": tier_code}
