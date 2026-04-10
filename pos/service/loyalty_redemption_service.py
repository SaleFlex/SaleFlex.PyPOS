"""
Apply loyalty point redemption as a document discount (BONUS / PAY_TYPE_BONUS).

Copyright (c) 2025-2026 Ferhat Mousavi
"""

from __future__ import annotations

import json
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from typing import Any, Dict, Optional, Tuple
from uuid import uuid4

from core.logger import get_logger
from data_layer.auto_save import AutoSaveModel

logger = get_logger(__name__)

DISCOUNT_TYPE_CODE = "LOYALTY"


class LoyaltyRedemptionService:
    """Stages ``TransactionDiscountTemp`` rows and updates head loyalty/discount totals."""

    @staticmethod
    def _unwrap(obj: Any) -> Any:
        return obj.unwrap() if isinstance(obj, AutoSaveModel) else obj

    @staticmethod
    def _head(document_data: Dict[str, Any]) -> Any:
        return LoyaltyRedemptionService._unwrap(document_data["head"])

    @staticmethod
    def net_amount_due(head: Any) -> Decimal:
        """Gross line total minus document discounts (matches AmountTable net)."""
        from pos.service.payment_service import PaymentService

        gross = PaymentService._safe_decimal(getattr(head, "total_amount", None))
        disc = PaymentService._safe_decimal(getattr(head, "total_discount_amount", None))
        return gross - disc

    @staticmethod
    def remaining_after_payments(document_data: Dict[str, Any]) -> Decimal:
        head = LoyaltyRedemptionService._head(document_data)
        from pos.service.payment_service import PaymentService

        net = LoyaltyRedemptionService.net_amount_due(head)
        paid = PaymentService._safe_decimal(getattr(head, "total_payment_amount", None))
        return net - paid

    @staticmethod
    def _decimal_places_from_app(handler: Any) -> int:
        try:
            sign = None
            if handler and getattr(handler, "current_currency", None):
                sign = handler.current_currency
            if not sign and handler and getattr(handler, "document_data", None):
                h = handler.document_data.get("head")
                if h:
                    hu = LoyaltyRedemptionService._unwrap(h)
                    sign = getattr(hu, "base_currency", None) or "GBP"
            sign = sign or "GBP"
            pd = getattr(handler, "product_data", None) or {}
            for c in pd.get("Currency") or []:
                if getattr(c, "sign", None) == sign and not getattr(c, "is_deleted", False):
                    return int(getattr(c, "decimal_places", None) or 2)
        except Exception:
            pass
        return 2

    @staticmethod
    def _quantize_money(amount: Decimal, places: int) -> Decimal:
        q = Decimal("1").scaleb(-places)
        return amount.quantize(q, rounding=ROUND_HALF_UP)

    @staticmethod
    def _next_discount_line_no(document_data: Dict[str, Any]) -> int:
        mx = 0
        for d in document_data.get("discounts") or []:
            row = LoyaltyRedemptionService._unwrap(d)
            mx = max(mx, int(getattr(row, "line_no", 0) or 0))
        return mx + 1

    @staticmethod
    def apply_points_redemption(
        document_data: Dict[str, Any],
        points_requested: int,
        *,
        decimal_places: int = 2,
    ) -> Tuple[bool, Optional[str]]:
        """
        Convert *points_requested* into a basket discount using ``LoyaltyProgram.currency_per_point``,
        ``LoyaltyRedemptionPolicy`` caps/steps, and member ``available_points``.

        Creates a ``TransactionDiscountTemp`` (``discount_type=LOYALTY``) and increments
        ``head.loyalty_points_redeemed`` and ``head.total_discount_amount``.
        """
        if not document_data or not document_data.get("head"):
            return False, "No active document"
        if points_requested is None or int(points_requested) <= 0:
            return False, "Enter the number of points on the numpad (whole points), then press BONUS."

        head = LoyaltyRedemptionService._head(document_data)
        from data_layer.engine import Engine
        from data_layer.model.definition.customer import Customer
        from data_layer.model.definition.customer_loyalty import CustomerLoyalty
        from data_layer.model.definition.loyalty_program import LoyaltyProgram
        from data_layer.model.definition.loyalty_redemption_policy import LoyaltyRedemptionPolicy
        from data_layer.model.definition.transaction_discount_temp import TransactionDiscountTemp
        from data_layer.model.definition.transaction_status import TransactionType
        from pos.service.payment_service import PaymentService

        tx_type = (getattr(head, "transaction_type", None) or "").lower()
        if tx_type != TransactionType.SALE.value:
            return False, "Points redemption is only available on sale receipts."

        cid = getattr(head, "fk_customer_id", None)
        if not cid:
            return False, "Assign a customer before redeeming points."

        remaining = LoyaltyRedemptionService.remaining_after_payments(document_data)
        if remaining <= Decimal("0"):
            return False, "Nothing left to pay; points redemption is not needed."

        pts_req = int(points_requested)

        try:
            engine = Engine()
            with engine.get_session() as session:
                customer = session.query(Customer).filter(Customer.id == cid).first()
                if not customer or customer.is_walkin:
                    return False, "Walk-in customers cannot redeem points."

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
                    return False, "No loyalty membership for this customer."

                program = (
                    session.query(LoyaltyProgram)
                    .filter(LoyaltyProgram.id == mem.fk_loyalty_program_id)
                    .first()
                )
                if not program or not program.is_active:
                    return False, "Loyalty program is not active."

                cpp = program.currency_per_point
                if cpp is None or Decimal(str(cpp)) <= 0:
                    return False, "Program currency_per_point is not configured."

                cpp_dec = Decimal(str(cpp))
                policy = (
                    session.query(LoyaltyRedemptionPolicy)
                    .filter(
                        LoyaltyRedemptionPolicy.fk_loyalty_program_id == program.id,
                        LoyaltyRedemptionPolicy.is_deleted.is_(False),
                    )
                    .first()
                )
                min_pts = int(policy.minimum_points_to_redeem or 0) if policy else 0
                step = int(policy.points_redemption_step or 1) if policy else 1
                if step < 1:
                    step = 1
                allow_partial = True if not policy else bool(policy.allow_partial_redemption)

                available = int(mem.available_points or 0)
                max_by_balance = min(pts_req, available)

                gross = PaymentService._safe_decimal(head.total_amount)
                max_share = None
                if policy and policy.max_basket_amount_share_from_points is not None:
                    share = Decimal(str(policy.max_basket_amount_share_from_points))
                    if share > 0:
                        max_share = (gross * share).quantize(Decimal("0.0001"), rounding=ROUND_DOWN)

                max_currency = remaining
                if max_share is not None:
                    max_currency = min(max_currency, max_share)

                max_points_by_currency = int((max_currency / cpp_dec).to_integral_value(rounding=ROUND_DOWN))
                points = min(max_by_balance, max_points_by_currency)

                if step > 1:
                    points = (points // step) * step

                if min_pts > 0 and points < min_pts:
                    return (
                        False,
                        f"Minimum redemption is {min_pts} points (policy). "
                        f"Maximum applicable now: {points} points toward this balance.",
                    )

                if points <= 0:
                    return False, "Not enough points or basket limit prevents redemption."

                if not allow_partial and points != pts_req:
                    return False, f"Redemption must be in steps of {step} points (policy)."

                discount_money = LoyaltyRedemptionService._quantize_money(
                    Decimal(points) * cpp_dec, decimal_places
                )
                if discount_money > max_currency:
                    discount_money = LoyaltyRedemptionService._quantize_money(max_currency, decimal_places)
                    points = int((discount_money / cpp_dec).to_integral_value(rounding=ROUND_DOWN))
                    if step > 1:
                        points = (points // step) * step
                    discount_money = LoyaltyRedemptionService._quantize_money(
                        Decimal(points) * cpp_dec, decimal_places
                    )

                if discount_money <= 0 or points <= 0:
                    return False, "Unable to apply redemption for the current basket."

        except Exception as exc:
            logger.error("[LOYALTY_REDEEM] apply_points_redemption: %s", exc)
            return False, "Could not apply points redemption."

        disc = TransactionDiscountTemp()
        disc.id = uuid4()
        disc.fk_transaction_head_id = head.id
        disc.fk_transaction_product_id = None
        disc.fk_transaction_payment_id = None
        disc.fk_transaction_department_id = None
        disc.line_no = LoyaltyRedemptionService._next_discount_line_no(document_data)
        disc.discount_type = DISCOUNT_TYPE_CODE
        disc.discount_amount = discount_money
        disc.discount_rate = None
        disc.discount_code = f"{points}PTS"[:15]
        disc.is_cancel = False
        disc.create()

        document_data.setdefault("discounts", []).append(disc)

        prev_disc = PaymentService._safe_decimal(getattr(head, "total_discount_amount", None))
        head.total_discount_amount = prev_disc + discount_money
        prev_lp = int(getattr(head, "loyalty_points_redeemed", None) or 0)
        head.loyalty_points_redeemed = prev_lp + points
        if hasattr(head, "save"):
            head.save()

        logger.info(
            "[LOYALTY_REDEEM] Applied %s points -> %s discount",
            points,
            discount_money,
        )
        return True, None
