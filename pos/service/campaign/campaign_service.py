"""
Local campaign evaluation: basket, time-window, and product-linked discounts.

Copyright (c) 2025-2026 Ferhat Mousavi
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from core.logger import get_logger
from data_layer.model.definition.campaign import Campaign
from data_layer.model.definition.campaign_product import CampaignProduct
from data_layer.model.definition.campaign_rule import CampaignRule
from data_layer.model.definition.campaign_type import CampaignType
from data_layer.model.definition.customer_segment_member import CustomerSegmentMember
from pos.service.campaign.application_policy import CAMPAIGN_DISCOUNT_TYPE_CODE

logger = get_logger(__name__)

Q2 = Decimal("0.01")

SUPPORTED_TYPE_CODES = frozenset({"BASKET_DISCOUNT", "TIME_BASED", "PRODUCT_DISCOUNT"})


@dataclass(frozen=True)
class CampaignDiscountProposal:
    """One proposed discount line for ``TransactionDiscountTemp`` (not yet persisted)."""

    campaign_id: UUID
    campaign_code: str
    campaign_name: str
    description: str
    scope: str  # "DOCUMENT" | "LINE"
    fk_transaction_product_temp_id: Optional[UUID]
    line_no: Optional[int]
    discount_amount: Decimal
    discount_rate: Optional[Decimal]
    temp_discount_type: str
    discount_code: str


@dataclass
class _LineCtx:
    id: UUID
    line_no: int
    fk_product_id: Optional[UUID]
    fk_department_main_group_id: UUID
    line_total: Decimal
    quantity: Decimal
    is_cancel: bool
    is_voided: bool


class CampaignService:
    """Evaluate auto-apply campaigns against the open sale document (no DB writes here).

    Persisted application to ``TransactionDiscountTemp`` is done by
    ``campaign_document_sync.sync_campaign_discounts_on_document``.
    """

    @staticmethod
    def campaign_discount_proposal_to_dict(p: CampaignDiscountProposal) -> Dict[str, Any]:
        """Serialize a proposal for API-style ``cart_data`` payloads (e.g. ``apply_campaign``)."""
        return {
            "campaign_id": str(p.campaign_id),
            "campaign_code": p.campaign_code,
            "campaign_name": p.campaign_name,
            "description": p.description,
            "scope": p.scope,
            "fk_transaction_product_temp_id": (
                str(p.fk_transaction_product_temp_id)
                if p.fk_transaction_product_temp_id is not None
                else None
            ),
            "line_no": p.line_no,
            "discount_amount": str(p.discount_amount),
            "discount_rate": str(p.discount_rate) if p.discount_rate is not None else None,
            "temp_discount_type": p.temp_discount_type,
            "discount_code": p.discount_code,
        }

    @staticmethod
    def evaluate_proposals(
        document_data: Mapping[str, Any],
        *,
        evaluated_at: Optional[datetime] = None,
        active_coupon_codes: Optional[Sequence[str]] = None,
        session: Optional[Session] = None,
    ) -> List[CampaignDiscountProposal]:
        """
        Return proposed CAMPAIGN discounts sorted by application order (priority descending,
        then greedy combinable stacking per ``application_policy``).

        Does not write to the database. Caller applies proposals to ``document_data`` if desired.

        Args:
            document_data: ``DocumentManager`` structure (``head``, ``products``, …).
            evaluated_at: Defaults to UTC now.
            active_coupon_codes: Uppercased coupon/campaign codes entered for this cart (for ``requires_coupon``).
            session: Optional SQLAlchemy session; if omitted, opens a short read-only session.
        """
        if not document_data or not document_data.get("head"):
            return []

        when = evaluated_at or datetime.now(timezone.utc)
        when_cmp = CampaignService._as_utc_naive(when)

        head = document_data["head"]
        coupon_set: Set[str] = {str(c).strip().upper() for c in (active_coupon_codes or ()) if str(c).strip()}

        lines = CampaignService._collect_lines(document_data)
        if session is not None:
            return CampaignService._evaluate_with_session(
                session, head, lines, when_cmp, coupon_set
            )

        from data_layer.engine import Engine

        try:
            with Engine().get_session() as s:
                return CampaignService._evaluate_with_session(s, head, lines, when_cmp, coupon_set)
        except Exception as exc:
            logger.error("[CampaignService] evaluate_proposals: %s", exc)
            return []

    @staticmethod
    def _collect_lines(document_data: Mapping[str, Any]) -> List[_LineCtx]:
        rows: List[_LineCtx] = []
        for p in document_data.get("products") or []:
            if getattr(p, "is_cancel", False) or getattr(p, "is_voided", False):
                continue
            pid = getattr(p, "id", None)
            if pid is None:
                continue
            rows.append(
                _LineCtx(
                    id=UUID(str(pid)),
                    line_no=int(getattr(p, "line_no", 0) or 0),
                    fk_product_id=getattr(p, "fk_product_id", None),
                    fk_department_main_group_id=UUID(str(getattr(p, "fk_department_main_group_id"))),
                    line_total=Decimal(str(getattr(p, "total_price", 0) or 0)),
                    quantity=Decimal(str(getattr(p, "quantity", 0) or 0)),
                    is_cancel=bool(getattr(p, "is_cancel", False)),
                    is_voided=bool(getattr(p, "is_voided", False)),
                )
            )
        return rows

    @staticmethod
    def _merch_subtotal(lines: Sequence[_LineCtx]) -> Decimal:
        return sum((ln.line_total for ln in lines), Decimal("0"))

    @staticmethod
    def _as_utc_naive(when: datetime) -> datetime:
        """Compare with ORM datetimes that are often stored without tz."""
        if when.tzinfo is None:
            return when
        return when.astimezone(timezone.utc).replace(tzinfo=None)

    @staticmethod
    def _evaluate_with_session(
        session: Session,
        head: Any,
        lines: Sequence[_LineCtx],
        when: datetime,
        coupon_set: Set[str],
    ) -> List[CampaignDiscountProposal]:
        fk_store = getattr(head, "fk_store_id", None)
        fk_customer = getattr(head, "fk_customer_id", None)

        types = {
            row.id: row
            for row in session.query(CampaignType)
            .filter(CampaignType.is_deleted.is_(False), CampaignType.is_active.is_(True))
            .all()
        }

        campaigns = (
            session.query(Campaign)
            .filter(Campaign.is_deleted.is_(False), Campaign.is_active.is_(True))
            .all()
        )

        rules_by: Dict[Any, List[CampaignRule]] = {}
        for r in (
            session.query(CampaignRule)
            .filter(CampaignRule.is_deleted.is_(False))
            .all()
        ):
            rules_by.setdefault(r.fk_campaign_id, []).append(r)

        cp_by: Dict[Any, List[CampaignProduct]] = {}
        for cp in (
            session.query(CampaignProduct)
            .filter(CampaignProduct.is_deleted.is_(False), CampaignProduct.is_active.is_(True))
            .all()
        ):
            cp_by.setdefault(cp.fk_campaign_id, []).append(cp)

        candidates: List[Tuple[Campaign, str]] = []
        for c in campaigns:
            ct = types.get(c.fk_campaign_type_id)
            if not ct or ct.code not in SUPPORTED_TYPE_CODES:
                continue
            if c.requires_coupon:
                if c.code.upper() not in coupon_set:
                    continue
            elif not c.is_auto_apply:
                continue
            if not CampaignService._store_ok(c, fk_store):
                continue
            if not CampaignService._in_date_range(c, when):
                continue
            if not CampaignService._in_time_window(c, when):
                continue
            if fk_customer and not CampaignService._segment_ok(session, c, fk_customer):
                continue
            if not fk_customer and c.fk_customer_segment_id is not None:
                continue
            candidates.append((c, ct.code))

        candidates.sort(key=lambda x: (-(x[0].priority or 0), str(x[0].code)))

        base_subtotal = CampaignService._merch_subtotal(lines)
        proposals: List[CampaignDiscountProposal] = []
        stop_further = False

        for camp, type_code in candidates:
            if stop_further:
                break
            rules = rules_by.get(camp.id, [])
            cps = cp_by.get(camp.id, [])

            if type_code in ("BASKET_DISCOUNT", "TIME_BASED"):
                props = CampaignService._proposals_basket(camp, lines, rules, base_subtotal)
            elif type_code == "PRODUCT_DISCOUNT":
                props = CampaignService._proposals_product(camp, lines, rules, cps)
            else:
                props = []

            if not props:
                continue

            for pr in props:
                proposals.append(pr)

            if not camp.is_combinable:
                stop_further = True

        return proposals

    @staticmethod
    def _store_ok(campaign: Campaign, fk_store_id: Any) -> bool:
        if campaign.fk_store_id is None:
            return True
        if fk_store_id is None:
            return False
        return UUID(str(campaign.fk_store_id)) == UUID(str(fk_store_id))

    @staticmethod
    def _segment_ok(session: Session, campaign: Campaign, fk_customer_id: Any) -> bool:
        if campaign.fk_customer_segment_id is None:
            return True
        row = (
            session.query(CustomerSegmentMember)
            .filter(
                CustomerSegmentMember.fk_customer_id == fk_customer_id,
                CustomerSegmentMember.fk_customer_segment_id == campaign.fk_customer_segment_id,
                CustomerSegmentMember.is_active.is_(True),
                CustomerSegmentMember.is_deleted.is_(False),
            )
            .first()
        )
        return row is not None

    @staticmethod
    def _normalize_db_datetime(dt: Optional[datetime]) -> Optional[datetime]:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt
        return dt.astimezone(timezone.utc).replace(tzinfo=None)

    @staticmethod
    def _in_date_range(campaign: Campaign, when: datetime) -> bool:
        sd = CampaignService._normalize_db_datetime(campaign.start_date)
        ed = CampaignService._normalize_db_datetime(campaign.end_date)
        d = when.date()
        if sd is not None and d < sd.date():
            return False
        if ed is not None and d > ed.date():
            return False
        return True

    @staticmethod
    def _in_time_window(campaign: Campaign, when: datetime) -> bool:
        if campaign.days_of_week:
            raw = str(campaign.days_of_week).strip()
            allowed: Set[int] = set()
            for part in raw.split(","):
                part = part.strip()
                if not part:
                    continue
                try:
                    allowed.add(int(part))
                except ValueError:
                    continue
            if allowed and when.isoweekday() not in allowed:
                return False

        st = campaign.start_time
        et = campaign.end_time
        if st is not None and et is not None:
            t = when.time()
            if st <= et:
                if not (st <= t <= et):
                    return False
            else:
                if not (t >= st or t <= et):
                    return False
        return True

    @staticmethod
    def _line_matches_rule(line: _LineCtx, rule: CampaignRule) -> bool:
        rt = (rule.rule_type or "").upper()
        if rt == "PRODUCT":
            if rule.fk_product_id is None or line.fk_product_id is None:
                return False
            return UUID(str(rule.fk_product_id)) == UUID(str(line.fk_product_id))
        if rt == "DEPARTMENT":
            if rule.fk_department_id is None:
                return False
            return UUID(str(rule.fk_department_id)) == line.fk_department_main_group_id
        return False

    @staticmethod
    def _line_passes_rules(line: _LineCtx, rules: Sequence[CampaignRule]) -> bool:
        if not rules:
            return True
        includes = [r for r in rules if r.is_include]
        excludes = [r for r in rules if not r.is_include]
        for r in excludes:
            if CampaignService._line_matches_rule(line, r):
                return False
        if not includes:
            return True
        return any(CampaignService._line_matches_rule(line, r) for r in includes)

    @staticmethod
    def _eligible_lines(lines: Sequence[_LineCtx], rules: Sequence[CampaignRule]) -> List[_LineCtx]:
        if not rules:
            return list(lines)
        return [ln for ln in lines if CampaignService._line_passes_rules(ln, rules)]

    @staticmethod
    def _eligible_subtotal(lines: Sequence[_LineCtx], rules: Sequence[CampaignRule]) -> Decimal:
        return CampaignService._merch_subtotal(CampaignService._eligible_lines(lines, rules))

    @staticmethod
    def _quantize_money(d: Decimal) -> Decimal:
        return d.quantize(Q2, rounding=ROUND_HALF_UP)

    @staticmethod
    def _discount_code(campaign: Campaign) -> str:
        code = (campaign.code or "")[:15]
        return code

    @staticmethod
    def _proposal_document(
        campaign: Campaign,
        amount: Decimal,
        rate: Optional[Decimal],
        description: str,
    ) -> Optional[CampaignDiscountProposal]:
        amt = CampaignService._quantize_money(amount)
        if amt <= 0:
            return None
        return CampaignDiscountProposal(
            campaign_id=UUID(str(campaign.id)),
            campaign_code=str(campaign.code or ""),
            campaign_name=str(campaign.name or ""),
            description=description,
            scope="DOCUMENT",
            fk_transaction_product_temp_id=None,
            line_no=None,
            discount_amount=amt,
            discount_rate=rate,
            temp_discount_type=CAMPAIGN_DISCOUNT_TYPE_CODE,
            discount_code=CampaignService._discount_code(campaign),
        )

    @staticmethod
    def _proposal_line(
        campaign: Campaign,
        line: _LineCtx,
        amount: Decimal,
        rate: Optional[Decimal],
        description: str,
    ) -> Optional[CampaignDiscountProposal]:
        amt = CampaignService._quantize_money(amount)
        if amt <= 0:
            return None
        return CampaignDiscountProposal(
            campaign_id=UUID(str(campaign.id)),
            campaign_code=str(campaign.code or ""),
            campaign_name=str(campaign.name or ""),
            description=description,
            scope="LINE",
            fk_transaction_product_temp_id=line.id,
            line_no=line.line_no,
            discount_amount=amt,
            discount_rate=rate,
            temp_discount_type=CAMPAIGN_DISCOUNT_TYPE_CODE,
            discount_code=CampaignService._discount_code(campaign),
        )

    @staticmethod
    def _proposals_basket(
        campaign: Campaign,
        lines: Sequence[_LineCtx],
        rules: Sequence[CampaignRule],
        base_merchandise_subtotal: Decimal,
    ) -> List[CampaignDiscountProposal]:
        eligible_total = CampaignService._eligible_subtotal(lines, rules)
        if campaign.min_purchase_amount is not None:
            if eligible_total < Decimal(str(campaign.min_purchase_amount)):
                return []
        if campaign.max_purchase_amount is not None:
            if eligible_total > Decimal(str(campaign.max_purchase_amount)):
                return []

        dtype = (campaign.discount_type or "").upper()
        desc = (campaign.notification_message or campaign.description or campaign.name or campaign.code or "").strip()

        if dtype == "PERCENTAGE":
            pct = Decimal(str(campaign.discount_percentage or 0))
            if pct <= 0:
                return []
            raw = eligible_total * (pct / Decimal("100"))
            if campaign.max_discount_amount is not None:
                cap = Decimal(str(campaign.max_discount_amount))
                raw = min(raw, cap)
            pr = CampaignService._proposal_document(campaign, raw, pct, desc or f"{pct}% off")
            return [pr] if pr else []

        if dtype == "FIXED_AMOUNT":
            fixed = Decimal(str(campaign.discount_value or 0))
            if fixed <= 0:
                return []
            raw = min(fixed, eligible_total)
            pr = CampaignService._proposal_document(campaign, raw, None, desc or f"{raw} off")
            return [pr] if pr else []

        return []

    @staticmethod
    def _proposals_product(
        campaign: Campaign,
        lines: Sequence[_LineCtx],
        rules: Sequence[CampaignRule],
        cps: Sequence[CampaignProduct],
    ) -> List[CampaignDiscountProposal]:
        if not cps:
            return []

        out: List[CampaignDiscountProposal] = []
        dtype = (campaign.discount_type or "").upper()

        for line in lines:
            if not CampaignService._line_passes_rules(line, rules):
                continue
            for cp in cps:
                if line.fk_product_id is None:
                    continue
                if UUID(str(cp.fk_product_id)) != UUID(str(line.fk_product_id)):
                    continue
                if cp.min_quantity is not None and line.quantity < Decimal(str(cp.min_quantity)):
                    continue
                if cp.max_quantity is not None and line.quantity > Decimal(str(cp.max_quantity)):
                    continue

                pct = cp.discount_percentage
                fixed_v = cp.discount_value
                if pct is None and fixed_v is None:
                    pct = campaign.discount_percentage
                    fixed_v = campaign.discount_value

                desc = (campaign.notification_message or campaign.description or campaign.name or "").strip()

                if dtype == "PERCENTAGE" and pct is not None:
                    pdec = Decimal(str(pct))
                    if pdec <= 0:
                        continue
                    raw = line.line_total * (pdec / Decimal("100"))
                    if campaign.max_discount_amount is not None:
                        cap = Decimal(str(campaign.max_discount_amount))
                        raw = min(raw, cap)
                    pr = CampaignService._proposal_line(
                        campaign, line, raw, pdec, desc or f"{pdec}% off {campaign.code}"
                    )
                    if pr:
                        out.append(pr)
                        break

                elif dtype == "FIXED_AMOUNT" and fixed_v is not None:
                    fixed = Decimal(str(fixed_v))
                    if fixed <= 0:
                        continue
                    raw = min(fixed, line.line_total)
                    pr = CampaignService._proposal_line(
                        campaign, line, raw, None, desc or f"{raw} off {campaign.code}"
                    )
                    if pr:
                        out.append(pr)
                        break

        return out


__all__ = ["CampaignService", "CampaignDiscountProposal", "SUPPORTED_TYPE_CODES"]
