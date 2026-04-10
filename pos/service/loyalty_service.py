"""
Loyalty membership and phone-normalization helpers (local program only).

Copyright (c) 2025-2026 Ferhat Mousavi
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from core.logger import get_logger

if TYPE_CHECKING:
    from data_layer.model.definition.customer import Customer
    from data_layer.model.definition.customer_loyalty import CustomerLoyalty
    from data_layer.model.definition.loyalty_program import LoyaltyProgram
    from data_layer.model.definition.loyalty_program_policy import LoyaltyProgramPolicy
    from data_layer.model.definition.loyalty_tier import LoyaltyTier

logger = get_logger(__name__)


class LoyaltyService:
    """Phone-centric customer recognition and automatic enrollment into the active local program."""

    @staticmethod
    def normalize_phone(phone: Optional[str], default_country_calling_code: Optional[str] = None) -> Optional[str]:
        """
        Produce a digits-only canonical key for matching (no '+' stored).
        When ``default_country_calling_code`` is set (e.g. '90'), local numbers
        starting with '0' or without the country prefix are normalized to CC+national.
        """
        if phone is None:
            return None
        raw = str(phone).strip()
        if not raw:
            return None
        digits = "".join(ch for ch in raw if ch.isdigit())
        if not digits:
            return None
        cc = "".join(ch for ch in (default_country_calling_code or "") if ch.isdigit())
        if not cc:
            return digits
        if digits.startswith(cc):
            return digits
        if digits.startswith("0"):
            digits = digits[1:]
        if digits.startswith(cc):
            return digits
        return cc + digits

    @staticmethod
    def _policy_for_active_program(session: Session) -> tuple[Optional["LoyaltyProgram"], Optional["LoyaltyProgramPolicy"]]:
        from data_layer.model.definition.loyalty_program import LoyaltyProgram
        from data_layer.model.definition.loyalty_program_policy import LoyaltyProgramPolicy

        program = (
            session.query(LoyaltyProgram)
            .filter(LoyaltyProgram.is_active.is_(True), LoyaltyProgram.is_deleted.is_(False))
            .order_by(LoyaltyProgram.name)
            .first()
        )
        if not program:
            return None, None
        policy = (
            session.query(LoyaltyProgramPolicy)
            .filter(
                LoyaltyProgramPolicy.fk_loyalty_program_id == program.id,
                LoyaltyProgramPolicy.is_deleted.is_(False),
            )
            .first()
        )
        return program, policy

    @staticmethod
    def sync_customer_phone_normalized(session: Session, customer: "Customer") -> None:
        """Refresh ``customer.phone_normalized`` from ``phone_number`` using program policy (if any)."""
        _, policy = LoyaltyService._policy_for_active_program(session)
        cc = policy.default_phone_country_calling_code if policy else None
        customer.phone_normalized = LoyaltyService.normalize_phone(customer.phone_number, cc)

    @staticmethod
    def validate_unique_phone_normalized(session: Session, customer: "Customer") -> Optional[str]:
        """
        Returns an error message if another non-deleted customer already uses this normalized phone.
        """
        if not customer.phone_normalized:
            return None
        from data_layer.model.definition.customer import Customer

        other = (
            session.query(Customer)
            .filter(
                Customer.phone_normalized == customer.phone_normalized,
                Customer.id != customer.id,
                Customer.is_deleted.is_(False),
            )
            .first()
        )
        if other:
            return (
                "Bu telefon numarası başka bir müşteriye kayıtlı. "
                "Sadakat için telefon benzersiz olmalıdır."
            )
        return None

    @staticmethod
    def _ensure_membership_in_session(session: Session, customer: "Customer") -> Optional["CustomerLoyalty"]:
        from data_layer.model.definition.customer_loyalty import CustomerLoyalty
        from data_layer.model.definition.loyalty_point_transaction import LoyaltyPointTransaction
        from data_layer.model.definition.loyalty_tier import LoyaltyTier

        program, policy = LoyaltyService._policy_for_active_program(session)
        if not program:
            return None

        existing = (
            session.query(CustomerLoyalty)
            .filter(
                CustomerLoyalty.fk_customer_id == customer.id,
                CustomerLoyalty.is_deleted.is_(False),
            )
            .first()
        )
        if existing:
            LoyaltyService.recalculate_membership_tier(session, existing)
            return existing

        if policy and policy.require_customer_phone_for_enrollment:
            LoyaltyService.sync_customer_phone_normalized(session, customer)
            if not customer.phone_normalized:
                logger.info(
                    "[LOYALTY] Skip enrollment for customer %s — phone required and missing/invalid",
                    customer.id,
                )
                return None

        first_tier = (
            session.query(LoyaltyTier)
            .filter(
                LoyaltyTier.fk_loyalty_program_id == program.id,
                LoyaltyTier.is_active.is_(True),
                LoyaltyTier.is_deleted.is_(False),
            )
            .order_by(LoyaltyTier.tier_level.asc(), LoyaltyTier.display_order.asc())
            .first()
        )

        welcome = int(program.welcome_points or 0)
        mem = CustomerLoyalty(
            fk_customer_id=customer.id,
            fk_loyalty_program_id=program.id,
            fk_loyalty_tier_id=first_tier.id if first_tier else None,
            total_points=welcome,
            available_points=welcome,
            lifetime_points=welcome,
        )
        session.add(mem)
        session.flush()

        if welcome > 0:
            session.add(
                LoyaltyPointTransaction(
                    fk_customer_loyalty_id=mem.id,
                    fk_customer_id=customer.id,
                    transaction_type="WELCOME",
                    points_amount=welcome,
                    balance_after=welcome,
                    description="Welcome bonus",
                )
            )

        logger.info("[LOYALTY] Enrolled customer %s in program %s (welcome=%s)", customer.id, program.id, welcome)
        LoyaltyService.recalculate_membership_tier(session, mem)
        return mem

    @staticmethod
    def _unwrap_document_head(head: Any) -> Any:
        from data_layer.auto_save import AutoSaveModel

        return head.unwrap() if isinstance(head, AutoSaveModel) else head

    @staticmethod
    def member_qualifies_for_tier(membership: "CustomerLoyalty", tier: "LoyaltyTier") -> bool:
        """
        Threshold semantics match ``LoyaltyTier`` docstring: if both ``min_points_required`` and
        ``min_annual_spending`` are set, the member qualifies when either condition is met.
        If only one is set, that condition alone applies. If neither is set, the tier is always allowed.
        """
        lp = int(membership.lifetime_points or 0)
        annual = Decimal(str(membership.annual_spent or 0))
        mp = tier.min_points_required
        ma = tier.min_annual_spending
        has_p = mp is not None
        has_a = ma is not None
        if not has_p and not has_a:
            return True
        if has_p and has_a:
            return lp >= int(mp) or annual >= Decimal(str(ma))
        if has_p:
            return lp >= int(mp)
        return annual >= Decimal(str(ma))

    @staticmethod
    def recalculate_membership_tier(session: Session, membership: "CustomerLoyalty") -> bool:
        """
        Set ``fk_loyalty_tier_id`` to the highest active tier the member qualifies for.
        Returns True if the tier foreign key changed.
        """
        from data_layer.model.definition.loyalty_tier import LoyaltyTier

        tiers = (
            session.query(LoyaltyTier)
            .filter(
                LoyaltyTier.fk_loyalty_program_id == membership.fk_loyalty_program_id,
                LoyaltyTier.is_active.is_(True),
                LoyaltyTier.is_deleted.is_(False),
            )
            .order_by(LoyaltyTier.tier_level.desc(), LoyaltyTier.display_order.desc())
            .all()
        )
        chosen_id = None
        for tier in tiers:
            if LoyaltyService.member_qualifies_for_tier(membership, tier):
                chosen_id = tier.id
                break
        if chosen_id is None:
            logger.warning(
                "[LOYALTY] No qualifying tier for membership %s — leaving tier unchanged",
                membership.id,
            )
            return False
        old = membership.fk_loyalty_tier_id
        if old != chosen_id:
            membership.fk_loyalty_tier_id = chosen_id
            logger.info("[LOYALTY] Tier updated for membership %s -> tier_id %s", membership.id, chosen_id)
            return True
        return False

    @staticmethod
    def apply_completed_sale_to_membership(
        session: Session,
        membership: "CustomerLoyalty",
        head: Any,
        *,
        recalculate_tier: bool = True,
    ) -> bool:
        """
        Increment purchase counters and spending from a completed sale header, roll calendar-year
        ``annual_spent`` when the sale date moves to a new year. Tier refresh is optional so
        earned points can be credited first when both run in the same session.
        """
        sale_amount = Decimal(str(getattr(head, "total_amount", None) or 0))
        if sale_amount < 0:
            return False
        sale_dt = getattr(head, "transaction_date_time", None) or datetime.now()
        if hasattr(sale_dt, "year"):
            pass
        else:
            sale_dt = datetime.now()

        membership.total_purchases = int(membership.total_purchases or 0) + 1
        prev_total = Decimal(str(membership.total_spent or 0))
        membership.total_spent = prev_total + sale_amount

        last = membership.last_activity_date
        annual = Decimal(str(membership.annual_spent or 0))
        if last is not None and hasattr(last, "year") and last.year < sale_dt.year:
            annual = Decimal("0")
        membership.annual_spent = annual + sale_amount
        membership.last_activity_date = sale_dt

        if recalculate_tier:
            LoyaltyService.recalculate_membership_tier(session, membership)
        return True

    @staticmethod
    def _credit_sale_earned_points(
        session: Session,
        membership: "CustomerLoyalty",
        customer: "Customer",
        points: int,
        permanent_head_id: Optional[UUID],
    ) -> None:
        """Persist ``EARNED`` ledger row and bump membership point balances."""
        if points <= 0:
            return
        from data_layer.model.definition.loyalty_point_transaction import LoyaltyPointTransaction

        membership.available_points = int(membership.available_points or 0) + points
        membership.total_points = int(membership.total_points or 0) + points
        membership.lifetime_points = int(membership.lifetime_points or 0) + points
        bal = int(membership.available_points or 0)
        session.add(
            LoyaltyPointTransaction(
                fk_customer_loyalty_id=membership.id,
                fk_customer_id=customer.id,
                transaction_type="EARNED",
                points_amount=points,
                balance_after=bal,
                fk_transaction_head_id=permanent_head_id,
                description="Purchase points",
            )
        )

    @staticmethod
    def _loyalty_discount_currency_note(document_data: Optional[Dict[str, Any]]) -> Optional[str]:
        if not document_data:
            return None
        from decimal import Decimal

        from data_layer.auto_save import AutoSaveModel

        total = Decimal("0")
        for d in document_data.get("discounts") or []:
            row = d.unwrap() if isinstance(d, AutoSaveModel) else d
            if getattr(row, "is_cancel", False):
                continue
            if (getattr(row, "discount_type", None) or "").upper() != "LOYALTY":
                continue
            total += Decimal(str(getattr(row, "discount_amount", None) or 0))
        if total <= 0:
            return None
        return f"Loyalty discount total {total}"

    @staticmethod
    def _debit_redeemed_points(
        session: Session,
        membership: "CustomerLoyalty",
        customer: "Customer",
        points: int,
        permanent_head_id: Optional[UUID],
        document_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Persist ``REDEEMED`` ledger row (negative points) and reduce spendable balances."""
        if points <= 0:
            return
        from data_layer.model.definition.loyalty_point_transaction import LoyaltyPointTransaction

        membership.available_points = max(0, int(membership.available_points or 0) - points)
        membership.total_points = max(0, int(membership.total_points or 0) - points)
        bal = int(membership.available_points or 0)
        notes = LoyaltyService._loyalty_discount_currency_note(document_data)
        session.add(
            LoyaltyPointTransaction(
                fk_customer_loyalty_id=membership.id,
                fk_customer_id=customer.id,
                transaction_type="REDEEMED",
                points_amount=-points,
                balance_after=bal,
                fk_transaction_head_id=permanent_head_id,
                description="Points redeemed (receipt discount)",
                notes=notes,
            )
        )

    @staticmethod
    def on_sale_transaction_completed(
        document_data: Optional[Dict[str, Any]],
        *,
        permanent_head_id: Optional[UUID] = None,
    ) -> None:
        """
        After temp rows are copied to permanent tables, refresh loyalty spending, credit any
        staged ``loyalty_points_earned``, then recalculate tier once (so new lifetime points
        affect tier). No-op for walk-in, non-sale types, or missing membership.
        """
        if not document_data or not document_data.get("head"):
            return
        try:
            head = LoyaltyService._unwrap_document_head(document_data["head"])
            from data_layer.model.definition.transaction_status import TransactionType

            tx_type = (getattr(head, "transaction_type", None) or "").lower()
            if tx_type != TransactionType.SALE.value:
                return

            from data_layer.engine import Engine
            from data_layer.model.definition.customer import Customer
            from data_layer.model.definition.customer_loyalty import CustomerLoyalty

            cid = getattr(head, "fk_customer_id", None)
            if not cid:
                return

            earned = int(getattr(head, "loyalty_points_earned", None) or 0)
            redeemed = int(getattr(head, "loyalty_points_redeemed", None) or 0)

            engine = Engine()
            with engine.get_session() as session:
                customer = session.query(Customer).filter(Customer.id == cid).first()
                if not customer or customer.is_walkin:
                    return

                mem = None
                lid = getattr(head, "loyalty_member_id", None)
                if lid:
                    mem = (
                        session.query(CustomerLoyalty)
                        .filter(
                            CustomerLoyalty.id == lid,
                            CustomerLoyalty.is_deleted.is_(False),
                        )
                        .first()
                    )
                if not mem:
                    mem = (
                        session.query(CustomerLoyalty)
                        .filter(
                            CustomerLoyalty.fk_customer_id == cid,
                            CustomerLoyalty.is_deleted.is_(False),
                        )
                        .first()
                    )
                if not mem:
                    return

                LoyaltyService.apply_completed_sale_to_membership(
                    session, mem, head, recalculate_tier=False
                )
                LoyaltyService._debit_redeemed_points(
                    session, mem, customer, redeemed, permanent_head_id, document_data
                )
                LoyaltyService._credit_sale_earned_points(
                    session, mem, customer, earned, permanent_head_id
                )
                LoyaltyService.recalculate_membership_tier(session, mem)
                session.commit()
        except Exception as exc:
            logger.error("[LOYALTY] on_sale_transaction_completed: %s", exc)

    @staticmethod
    def on_void_or_cancel_completed_sale(permanent_head_id: UUID, reason: str = "") -> None:
        """
        Reserved for voided or returned sales: reverse ``EARNED`` / ``REDEEMED`` per
        ``LoyaltyProgramPolicy.void_loyalty_points_policy`` and claw back redemption value
        on refunds/exchanges. Not wired to UI yet — implement with refund/void flows.
        """
        logger.info(
            "[LOYALTY] on_void_or_cancel_completed_sale stub head=%s reason=%s",
            permanent_head_id,
            reason,
        )

    @staticmethod
    def ensure_loyalty_on_sale_assignment(head_obj, customer_id) -> None:
        """
        After ``fk_customer_id`` is set on the sale head, create or resolve ``CustomerLoyalty``
        and set ``loyalty_member_id`` when the customer qualifies (non walk-in, active program).
        """
        from data_layer.engine import Engine
        from data_layer.model.definition.customer import Customer

        cid = UUID(str(customer_id)) if not isinstance(customer_id, UUID) else customer_id
        engine = Engine()
        membership_id = None
        try:
            with engine.get_session() as session:
                customer = session.query(Customer).filter(Customer.id == cid).first()
                if not customer or customer.is_walkin:
                    membership_id = None
                else:
                    LoyaltyService.sync_customer_phone_normalized(session, customer)
                    dup = LoyaltyService.validate_unique_phone_normalized(session, customer)
                    if dup:
                        logger.warning("[LOYALTY] %s — skipping enrollment for this sale", dup)
                        session.rollback()
                        membership_id = None
                    else:
                        mem = LoyaltyService._ensure_membership_in_session(session, customer)
                        session.commit()
                        membership_id = mem.id if mem else None
        except Exception as exc:
            logger.error("[LOYALTY] ensure_loyalty_on_sale_assignment: %s", exc)
            membership_id = None

        head_obj.loyalty_member_id = membership_id
        if hasattr(head_obj, "save"):
            head_obj.save()

    @staticmethod
    def default_phone_country_for_search() -> Optional[str]:
        """Country calling code digits for normalizing search queries (e.g. cashier types local mobile)."""
        from data_layer.engine import Engine

        engine = Engine()
        with engine.get_session() as session:
            _, policy = LoyaltyService._policy_for_active_program(session)
            if policy and policy.default_phone_country_calling_code:
                return "".join(c for c in policy.default_phone_country_calling_code if c.isdigit()) or None
        return None
