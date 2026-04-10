"""
Loyalty membership and phone-normalization helpers (local program only).

Copyright (c) 2025-2026 Ferhat Mousavi
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from core.logger import get_logger

if TYPE_CHECKING:
    from data_layer.model.definition.customer import Customer
    from data_layer.model.definition.customer_loyalty import CustomerLoyalty
    from data_layer.model.definition.loyalty_program import LoyaltyProgram
    from data_layer.model.definition.loyalty_program_policy import LoyaltyProgramPolicy

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
        return mem

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
