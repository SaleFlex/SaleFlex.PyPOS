"""
Loyalty point earning for completed sales (document total, line/category rules, product sets).

Copyright (c) 2025-2026 Ferhat Mousavi
"""

from __future__ import annotations

import json
from decimal import Decimal, ROUND_FLOOR
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from core.logger import get_logger
from data_layer.auto_save import AutoSaveModel

logger = get_logger(__name__)


class LoyaltyEarnService:
    """
    Stages ``loyalty_points_earned`` on the temp sale head and appends a
    ``TransactionLoyaltyTemp`` snapshot. Actual balance updates and
    ``LoyaltyPointTransaction`` rows are applied in ``LoyaltyService`` after the
    permanent ``TransactionHead`` exists.
    """

    @staticmethod
    def _unwrap(obj: Any) -> Any:
        return obj.unwrap() if isinstance(obj, AutoSaveModel) else obj

    @staticmethod
    def _parse_config(rule: Any) -> dict:
        raw = getattr(rule, "config_json", None) or ""
        if not str(raw).strip():
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning(
                "[LOYALTY_EARN] Invalid config_json for rule %s",
                getattr(rule, "rule_code", ""),
            )
            return {}

    @staticmethod
    def _tier_multiplier(session, membership) -> Decimal:
        from data_layer.model.definition.loyalty_tier import LoyaltyTier

        tid = getattr(membership, "fk_loyalty_tier_id", None)
        if not tid:
            return Decimal("1")
        tier = session.query(LoyaltyTier).filter(LoyaltyTier.id == tid).first()
        if not tier or tier.points_multiplier is None:
            return Decimal("1")
        return Decimal(str(tier.points_multiplier))

    @staticmethod
    def _tier_display(session, membership) -> str:
        from data_layer.model.definition.loyalty_tier import LoyaltyTier

        tid = getattr(membership, "fk_loyalty_tier_id", None)
        if not tid:
            return ""
        tier = session.query(LoyaltyTier).filter(LoyaltyTier.id == tid).first()
        return (tier.name or "") if tier else ""

    @staticmethod
    def _active_product_lines(document_data: Dict[str, Any]) -> List[Any]:
        out: List[Any] = []
        for p in document_data.get("products") or []:
            line = LoyaltyEarnService._unwrap(p)
            if getattr(line, "is_cancel", False) or getattr(line, "is_voided", False):
                continue
            out.append(line)
        return out

    @staticmethod
    def _document_net(head: Any) -> Decimal:
        try:
            d = Decimal(str(getattr(head, "total_amount", None) or 0))
        except Exception:
            d = Decimal("0")
        return d if d > 0 else Decimal("0")

    @staticmethod
    def _floor_money(x: Decimal) -> int:
        return int(x.to_integral_value(rounding=ROUND_FLOOR))

    @staticmethod
    def _rules_for_program(session, program_id) -> List[Any]:
        from data_layer.model.definition.loyalty_earn_rule import LoyaltyEarnRule

        return (
            session.query(LoyaltyEarnRule)
            .filter(
                LoyaltyEarnRule.fk_loyalty_program_id == program_id,
                LoyaltyEarnRule.is_active.is_(True),
                LoyaltyEarnRule.is_deleted.is_(False),
            )
            .order_by(LoyaltyEarnRule.priority.asc())
            .all()
        )

    @staticmethod
    def _score_line_item_rule(cfg: dict, line: Any, tier_m: Decimal) -> int:
        pid = cfg.get("fk_product_id") or cfg.get("product_id")
        pcode = (cfg.get("product_code") or cfg.get("plu") or "").strip().lower()
        match = False
        if pid:
            try:
                pu = UUID(str(pid))
                lp = getattr(line, "fk_product_id", None)
                if lp and UUID(str(lp)) == pu:
                    match = True
            except (ValueError, TypeError, AttributeError):
                pass
        if not match and pcode:
            lc = (getattr(line, "product_code", None) or "").strip().lower()
            if lc == pcode:
                match = True
        if not match:
            return 0
        extra = int(cfg.get("extra_points") or cfg.get("bonus_points_per_line") or 0)
        ppc = cfg.get("points_per_currency")
        line_total = Decimal(str(getattr(line, "total_price", None) or 0))
        pts = 0
        if ppc is not None:
            pts += LoyaltyEarnService._floor_money(line_total * Decimal(str(ppc)) * tier_m)
        if extra:
            pts += LoyaltyEarnService._floor_money(Decimal(extra) * tier_m)
        return pts

    @staticmethod
    def _score_category_rule(cfg: dict, line: Any, tier_m: Decimal) -> int:
        d_main = cfg.get("fk_department_main_group_id")
        d_sub = cfg.get("fk_department_sub_group_id")
        if not d_main and not d_sub:
            return 0
        match = True
        if d_main:
            try:
                dm = UUID(str(d_main))
                lm = getattr(line, "fk_department_main_group_id", None)
                if not lm or UUID(str(lm)) != dm:
                    match = False
            except (ValueError, TypeError, AttributeError):
                match = False
        if match and d_sub:
            try:
                ds = UUID(str(d_sub))
                ls = getattr(line, "fk_department_sub_group_id", None)
                if not ls or UUID(str(ls)) != ds:
                    match = False
            except (ValueError, TypeError, AttributeError):
                match = False
        if not match:
            return 0
        extra = int(cfg.get("extra_points") or 0)
        ppc = cfg.get("points_per_currency")
        line_total = Decimal(str(getattr(line, "total_price", None) or 0))
        pts = 0
        if ppc is not None:
            pts += LoyaltyEarnService._floor_money(line_total * Decimal(str(ppc)) * tier_m)
        if extra:
            pts += LoyaltyEarnService._floor_money(Decimal(extra) * tier_m)
        return pts

    @staticmethod
    def _evaluate_product_set(cfg: dict, lines: List[Any], tier_m: Decimal) -> int:
        raw_ids = cfg.get("product_ids") or cfg.get("required_product_ids") or []
        if not raw_ids:
            return 0
        try:
            required = {UUID(str(x)) for x in raw_ids}
        except (ValueError, TypeError):
            return 0
        present = set()
        for line in lines:
            lp = getattr(line, "fk_product_id", None)
            if lp:
                present.add(UUID(str(lp)))
        if not required.issubset(present):
            return 0
        bonus = int(cfg.get("bonus_points") or cfg.get("extra_points") or 0)
        if not bonus:
            return 0
        return LoyaltyEarnService._floor_money(Decimal(bonus) * tier_m)

    @staticmethod
    def compute_earn_breakdown(
        session,
        document_data: Dict[str, Any],
        head: Any,
        membership,
        program,
    ) -> Tuple[int, Dict[str, int]]:
        tier_m = LoyaltyEarnService._tier_multiplier(session, membership)
        net = LoyaltyEarnService._document_net(head)
        min_p = program.min_purchase_for_points
        min_ok = True
        if min_p is not None:
            min_ok = net >= Decimal(str(min_p))
        ppc = Decimal(str(program.points_per_currency or 0))
        program_base = 0
        if min_ok:
            program_base = LoyaltyEarnService._floor_money(net * ppc * tier_m)

        rules = LoyaltyEarnService._rules_for_program(session, program.id)
        doc_flat = 0
        for r in rules:
            if r.rule_type != "DOCUMENT_TOTAL":
                continue
            cfg = LoyaltyEarnService._parse_config(r)
            doc_flat += int(cfg.get("extra_points") or cfg.get("bonus_points") or 0)
        doc_flat_pts = LoyaltyEarnService._floor_money(Decimal(doc_flat) * tier_m)

        lines = LoyaltyEarnService._active_product_lines(document_data)
        line_pts = 0
        for r in rules:
            if r.rule_type == "LINE_ITEM":
                cfg = LoyaltyEarnService._parse_config(r)
                for line in lines:
                    line_pts += LoyaltyEarnService._score_line_item_rule(cfg, line, tier_m)
            elif r.rule_type in ("CATEGORY", "DEPARTMENT"):
                cfg = LoyaltyEarnService._parse_config(r)
                for line in lines:
                    line_pts += LoyaltyEarnService._score_category_rule(cfg, line, tier_m)

        set_pts = 0
        for r in rules:
            if r.rule_type in ("PRODUCT_SET", "BUNDLE"):
                cfg = LoyaltyEarnService._parse_config(r)
                set_pts += LoyaltyEarnService._evaluate_product_set(cfg, lines, tier_m)

        total = max(0, program_base + doc_flat_pts + line_pts + set_pts)
        breakdown = {
            "program_base": program_base,
            "document_rule_bonus": doc_flat_pts,
            "line_rules": line_pts,
            "product_set_rules": set_pts,
            "total": total,
        }
        return total, breakdown

    @staticmethod
    def stage_document_earn(document_data: Optional[Dict[str, Any]]) -> None:
        """Compute earn, set ``loyalty_points_earned`` on temp head, append loyalty snapshot."""
        if not document_data or not document_data.get("head"):
            return
        head = LoyaltyEarnService._unwrap(document_data["head"])
        from data_layer.model.definition.transaction_status import TransactionType

        tx_type = (getattr(head, "transaction_type", None) or "").lower()
        if tx_type != TransactionType.SALE.value:
            return

        def _clear_earn() -> None:
            head.loyalty_points_earned = 0
            if hasattr(head, "save"):
                head.save()

        try:
            from data_layer.engine import Engine
            from data_layer.model.definition.customer import Customer
            from data_layer.model.definition.customer_loyalty import CustomerLoyalty
            from data_layer.model.definition.loyalty_program import LoyaltyProgram
            from data_layer.model.definition.transaction_loyalty_temp import TransactionLoyaltyTemp

            cid = getattr(head, "fk_customer_id", None)
            if not cid:
                _clear_earn()
                return

            engine = Engine()
            with engine.get_session() as session:
                customer = session.query(Customer).filter(Customer.id == cid).first()
                if not customer or customer.is_walkin:
                    _clear_earn()
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
                    _clear_earn()
                    return

                program = (
                    session.query(LoyaltyProgram)
                    .filter(LoyaltyProgram.id == mem.fk_loyalty_program_id)
                    .first()
                )
                if not program or not program.is_active:
                    _clear_earn()
                    return

                total, breakdown = LoyaltyEarnService.compute_earn_breakdown(
                    session, document_data, head, mem, program
                )
                head.loyalty_points_earned = int(total)
                if hasattr(head, "save"):
                    head.save()

                prev_id = document_data.pop("_loyalty_earn_temp_row_id", None)
                if prev_id and document_data.get("loyalty"):
                    document_data["loyalty"] = [
                        x
                        for x in document_data["loyalty"]
                        if getattr(LoyaltyEarnService._unwrap(x), "id", None) != prev_id
                    ]

                tier_m = LoyaltyEarnService._tier_multiplier(session, mem)
                tname = LoyaltyEarnService._tier_display(session, mem)
                bal_before = int(mem.available_points or 0)
                extras = max(0, int(total) - int(breakdown["program_base"]))

                loy_row = TransactionLoyaltyTemp()
                loy_row.id = uuid4()
                loy_row.fk_transaction_head_id = head.id
                loy_row.fk_loyalty_member_id = mem.id
                loy_row.points_earned = int(total)
                loy_row.points_redeemed = 0
                loy_row.points_balance_before = bal_before
                loy_row.points_balance_after = bal_before + int(total)
                loy_row.redemption_amount = 0
                loy_row.loyalty_tier = tname or None
                loy_row.bonus_multiplier = Decimal(str(tier_m))
                loy_row.campaign_bonus = extras

                document_data.setdefault("loyalty", []).append(loy_row)
                document_data["_loyalty_earn_temp_row_id"] = loy_row.id

        except Exception as exc:
            logger.error("[LOYALTY_EARN] stage_document_earn: %s", exc)
            try:
                _clear_earn()
            except Exception:
                pass
