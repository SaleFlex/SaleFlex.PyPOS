"""
Local campaign evaluation: basket, time-window, and product-linked discounts.

Copyright (c) 2025-2026 Ferhat Mousavi
"""

from __future__ import annotations

import fnmatch
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, DefaultDict, Dict, List, Mapping, Optional, Sequence, Set, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from core.logger import get_logger
from data_layer.model.definition.campaign import Campaign
from data_layer.model.definition.campaign_product import CampaignProduct
from data_layer.model.definition.campaign_rule import CampaignRule
from data_layer.model.definition.campaign_type import CampaignType
from data_layer.model.definition.customer_segment_member import CustomerSegmentMember
from data_layer.model.definition.payment_type import PaymentType as PaymentTypeRow
from data_layer.model.definition.product import Product
from data_layer.model.definition.product_barcode import ProductBarcode
from pos.service.campaign.active_campaign_cache import ActiveCampaignCache
from pos.service.campaign.application_policy import CAMPAIGN_DISCOUNT_TYPE_CODE
from pos.service.campaign.campaign_usage_limits import CampaignUsageLimits

logger = get_logger(__name__)

Q2 = Decimal("0.01")

SUPPORTED_TYPE_CODES = frozenset(
    {
        "BASKET_DISCOUNT",
        "TIME_BASED",
        "PRODUCT_DISCOUNT",
        "BUY_X_GET_Y",
        "PAYMENT_DISCOUNT",
    }
)

# Map ``TransactionPaymentTemp.payment_type`` (``EventName`` value) to seeded ``PaymentType.type_name``.
_EVENT_TO_PAYMENT_TYPE_NAME: Dict[str, str] = {
    "CASH_PAYMENT": "Cash",
    "CREDIT_PAYMENT": "Credit Card",
    "CHECK_PAYMENT": "Check",
    "CHARGE_SALE_PAYMENT": "Payment on credit",
    "PREPAID_PAYMENT": "Prepaid Card",
    "EXCHANGE_PAYMENT": "Foreign currency",
    "OTHER_PAYMENT": "Other",
    "BONUS_PAYMENT": "Bonus",
}


@dataclass(frozen=True)
class CampaignDiscountProposal:
    """One proposed discount line for ``TransactionDiscountTemp`` (not yet persisted)."""

    campaign_id: UUID
    campaign_code: str
    campaign_name: str
    description: str
    scope: str  # "DOCUMENT" | "LINE"
    fk_transaction_product_temp_id: Optional[UUID]
    fk_transaction_payment_temp_id: Optional[UUID]
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
    fk_department_sub_group_id: Optional[UUID]
    product_code: Optional[str]
    line_total: Decimal
    quantity: Decimal
    is_cancel: bool
    is_voided: bool


@dataclass
class _PayCtx:
    id: UUID
    line_no: int
    payment_type: str
    payment_total: Decimal
    is_cancel: bool


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
            "fk_transaction_payment_temp_id": (
                str(p.fk_transaction_payment_temp_id)
                if p.fk_transaction_payment_temp_id is not None
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
                session, document_data, head, lines, when_cmp, coupon_set
            )

        from data_layer.engine import Engine

        try:
            with Engine().get_session() as s:
                return CampaignService._evaluate_with_session(
                    s, document_data, head, lines, when_cmp, coupon_set
                )
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
            sub = getattr(p, "fk_department_sub_group_id", None)
            rows.append(
                _LineCtx(
                    id=UUID(str(pid)),
                    line_no=int(getattr(p, "line_no", 0) or 0),
                    fk_product_id=getattr(p, "fk_product_id", None),
                    fk_department_main_group_id=UUID(str(getattr(p, "fk_department_main_group_id"))),
                    fk_department_sub_group_id=(
                        UUID(str(sub)) if sub is not None else None
                    ),
                    product_code=(getattr(p, "product_code", None) or None),
                    line_total=Decimal(str(getattr(p, "total_price", 0) or 0)),
                    quantity=Decimal(str(getattr(p, "quantity", 0) or 0)),
                    is_cancel=bool(getattr(p, "is_cancel", False)),
                    is_voided=bool(getattr(p, "is_voided", False)),
                )
            )
        return rows

    @staticmethod
    def _collect_payments(document_data: Mapping[str, Any]) -> List[_PayCtx]:
        rows: List[_PayCtx] = []
        for p in document_data.get("payments") or []:
            if getattr(p, "is_cancel", False):
                continue
            pid = getattr(p, "id", None)
            if pid is None:
                continue
            rows.append(
                _PayCtx(
                    id=UUID(str(pid)),
                    line_no=int(getattr(p, "line_no", 0) or 0),
                    payment_type=str(getattr(p, "payment_type", "") or ""),
                    payment_total=Decimal(str(getattr(p, "payment_total", 0) or 0)),
                    is_cancel=bool(getattr(p, "is_cancel", False)),
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
    def _norm_name(s: str) -> str:
        return "".join(ch for ch in s.lower() if ch.isalnum())

    @staticmethod
    def _payment_event_to_type_id(session: Session) -> Dict[str, UUID]:
        rows = (
            session.query(PaymentTypeRow)
            .filter(PaymentTypeRow.is_deleted.is_(False))
            .all()
        )
        by_norm: Dict[str, UUID] = {}
        for r in rows:
            nm = (r.type_name or "").strip()
            if nm:
                by_norm[CampaignService._norm_name(nm)] = UUID(str(r.id))
        out: Dict[str, UUID] = {}
        for ev, label in _EVENT_TO_PAYMENT_TYPE_NAME.items():
            key = CampaignService._norm_name(label)
            if key in by_norm:
                out[ev] = by_norm[key]
        return out

    @staticmethod
    def _load_product_rule_context(
        session: Session, lines: Sequence[_LineCtx]
    ) -> Dict[UUID, Dict[str, Any]]:
        ids = {ln.fk_product_id for ln in lines if ln.fk_product_id}
        if not ids:
            return {}
        products = (
            session.query(Product)
            .filter(Product.id.in_(ids), Product.is_deleted.is_(False))
            .all()
        )
        by_id = {UUID(str(p.id)): p for p in products}
        barcodes: DefaultDict[UUID, List[str]] = defaultdict(list)
        for bc in (
            session.query(ProductBarcode)
            .filter(
                ProductBarcode.fk_product_id.in_(ids),
                ProductBarcode.is_deleted.is_(False),
            )
            .all()
        ):
            pid = UUID(str(bc.fk_product_id))
            for raw in (bc.barcode, bc.old_barcode):
                s = (raw or "").strip()
                if s:
                    barcodes[pid].append(s)
        out: Dict[UUID, Dict[str, Any]] = {}
        for pid in ids:
            p = by_id.get(pid)
            out[pid] = {
                "fk_manufacturer_id": (
                    UUID(str(p.fk_manufacturer_id))
                    if p is not None and p.fk_manufacturer_id is not None
                    else None
                ),
                "barcodes": barcodes.get(pid, []),
            }
        return out

    @staticmethod
    def _partition_rules(
        rules: Sequence[CampaignRule],
    ) -> Tuple[List[CampaignRule], List[CampaignRule]]:
        line_rules: List[CampaignRule] = []
        payment_rules: List[CampaignRule] = []
        for r in rules:
            rt = (r.rule_type or "").upper()
            if rt == "PAYMENT_TYPE":
                payment_rules.append(r)
            else:
                line_rules.append(r)
        return line_rules, payment_rules

    @staticmethod
    def _evaluate_with_session(
        session: Session,
        document_data: Mapping[str, Any],
        head: Any,
        lines: Sequence[_LineCtx],
        when: datetime,
        coupon_set: Set[str],
    ) -> List[CampaignDiscountProposal]:
        fk_store = getattr(head, "fk_store_id", None)
        fk_customer = getattr(head, "fk_customer_id", None)
        pays = CampaignService._collect_payments(document_data)
        product_ctx = CampaignService._load_product_rule_context(session, lines)
        event_to_pt_id = CampaignService._payment_event_to_type_id(session)

        bundle = ActiveCampaignCache.get()
        if bundle is None:
            try:
                ActiveCampaignCache.reload()
                bundle = ActiveCampaignCache.get()
            except Exception as exc:
                logger.warning(
                    "[CampaignService] active campaign cache unavailable, loading from DB: %s", exc
                )
                bundle = None

        if bundle is not None:
            types = bundle.types
            campaigns = bundle.campaigns
            rules_by = bundle.rules_by
            cp_by = bundle.cp_by
        else:
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

            rules_by = {}
            for r in (
                session.query(CampaignRule)
                .filter(CampaignRule.is_deleted.is_(False))
                .all()
            ):
                rules_by.setdefault(r.fk_campaign_id, []).append(r)

            cp_by = {}
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
            if not CampaignUsageLimits.allows_new_application(session, c, fk_customer):
                continue
            candidates.append((c, ct.code))

        candidates.sort(key=lambda x: (-(x[0].priority or 0), str(x[0].code)))

        proposals: List[CampaignDiscountProposal] = []
        stop_further = False
        doc_discount_accum = Decimal("0")
        line_discount_accum: DefaultDict[UUID, Decimal] = defaultdict(lambda: Decimal("0"))

        for camp, type_code in candidates:
            if stop_further:
                break
            rules = rules_by.get(camp.id, [])
            line_rules, payment_rules = CampaignService._partition_rules(rules)
            cps = cp_by.get(camp.id, [])

            if type_code in ("BASKET_DISCOUNT", "TIME_BASED"):
                props = CampaignService._proposals_basket(
                    camp,
                    lines,
                    line_rules,
                    line_discount_accum,
                    doc_discount_accum,
                    product_ctx,
                )
            elif type_code == "PRODUCT_DISCOUNT":
                props = CampaignService._proposals_product(
                    camp, lines, line_rules, cps, product_ctx, line_discount_accum
                )
            elif type_code == "BUY_X_GET_Y":
                props = CampaignService._proposals_buy_x_get_y(
                    camp,
                    lines,
                    line_rules,
                    cps,
                    product_ctx,
                    line_discount_accum,
                    doc_discount_accum,
                )
            elif type_code == "PAYMENT_DISCOUNT":
                props = CampaignService._proposals_payment_discount(
                    camp,
                    pays,
                    payment_rules,
                    line_rules,
                    lines,
                    line_discount_accum,
                    doc_discount_accum,
                    event_to_pt_id,
                    product_ctx,
                )
            else:
                props = []

            if not props:
                continue

            for pr in props:
                proposals.append(pr)
                if pr.scope == "DOCUMENT":
                    doc_discount_accum += pr.discount_amount
                elif pr.fk_transaction_product_temp_id is not None:
                    line_discount_accum[pr.fk_transaction_product_temp_id] += pr.discount_amount

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
    def _barcode_matches_pattern(text: Optional[str], pattern: Optional[str]) -> bool:
        if not text or not pattern:
            return False
        val = text.strip()
        pat = pattern.strip()
        low = pat.lower()
        if low.startswith("re:"):
            try:
                return re.search(pat[3:].strip(), val) is not None
            except re.error:
                return False
        if any(ch in pat for ch in "*?[]"):
            return bool(fnmatch.fnmatchcase(val, pat))
        return val.startswith(pat)

    @staticmethod
    def _line_matches_rule(
        line: _LineCtx,
        rule: CampaignRule,
        product_ctx: Optional[Mapping[UUID, Dict[str, Any]]],
    ) -> bool:
        rt = (rule.rule_type or "").upper()
        if rt == "PRODUCT":
            if rule.fk_product_id is None or line.fk_product_id is None:
                return False
            return UUID(str(rule.fk_product_id)) == UUID(str(line.fk_product_id))
        if rt == "DEPARTMENT":
            if rule.fk_department_id is None:
                return False
            return UUID(str(rule.fk_department_id)) == line.fk_department_main_group_id
        if rt == "BRAND":
            if rule.fk_product_manufacturer_id is None or line.fk_product_id is None:
                return False
            ctx = (product_ctx or {}).get(line.fk_product_id) or {}
            mid = ctx.get("fk_manufacturer_id")
            if mid is None:
                return False
            return mid == UUID(str(rule.fk_product_manufacturer_id))
        if rt == "BARCODE_PATTERN":
            if not rule.rule_value or not str(rule.rule_value).strip():
                return False
            pat = str(rule.rule_value).strip()
            candidates: List[str] = []
            pc = (line.product_code or "").strip()
            if pc:
                candidates.append(pc)
            if line.fk_product_id and product_ctx:
                for b in (product_ctx.get(line.fk_product_id) or {}).get("barcodes") or []:
                    if b and b not in candidates:
                        candidates.append(b)
            return any(
                CampaignService._barcode_matches_pattern(c, pat) for c in candidates
            )
        if rt == "CATEGORY":
            if line.fk_department_sub_group_id is None:
                return False
            rv = (rule.rule_value or "").strip()
            if not rv:
                return False
            try:
                cat_id = UUID(rv)
            except ValueError:
                return False
            return line.fk_department_sub_group_id == cat_id
        if rt == "PAYMENT_TYPE":
            return False
        return False

    @staticmethod
    def _line_passes_rules(
        line: _LineCtx,
        rules: Sequence[CampaignRule],
        product_ctx: Optional[Mapping[UUID, Dict[str, Any]]],
    ) -> bool:
        if not rules:
            return True
        includes = [r for r in rules if r.is_include]
        excludes = [r for r in rules if not r.is_include]
        for r in excludes:
            if CampaignService._line_matches_rule(line, r, product_ctx):
                return False
        if not includes:
            return True
        return any(
            CampaignService._line_matches_rule(line, r, product_ctx) for r in includes
        )

    @staticmethod
    def _eligible_lines(
        lines: Sequence[_LineCtx],
        rules: Sequence[CampaignRule],
        product_ctx: Optional[Mapping[UUID, Dict[str, Any]]],
    ) -> List[_LineCtx]:
        if not rules:
            return list(lines)
        return [
            ln for ln in lines if CampaignService._line_passes_rules(ln, rules, product_ctx)
        ]

    @staticmethod
    def _eligible_subtotal(
        lines: Sequence[_LineCtx],
        rules: Sequence[CampaignRule],
        product_ctx: Optional[Mapping[UUID, Dict[str, Any]]] = None,
    ) -> Decimal:
        return CampaignService._merch_subtotal(
            CampaignService._eligible_lines(lines, rules, product_ctx)
        )

    @staticmethod
    def _eligible_net_after_stack(
        lines: Sequence[_LineCtx],
        rules: Sequence[CampaignRule],
        line_accum: Mapping[UUID, Decimal],
        doc_accum: Decimal,
        product_ctx: Optional[Mapping[UUID, Dict[str, Any]]],
    ) -> Decimal:
        el = CampaignService._eligible_lines(lines, rules, product_ctx)
        raw = sum(
            max(Decimal("0"), ln.line_total - line_accum.get(ln.id, Decimal("0")))
            for ln in el
        )
        return max(Decimal("0"), raw - doc_accum)

    @staticmethod
    def _payment_matches_rule(
        pay: _PayCtx,
        rule: CampaignRule,
        event_to_pt_id: Mapping[str, UUID],
    ) -> bool:
        rt = (rule.rule_type or "").upper()
        if rt != "PAYMENT_TYPE":
            return False
        if rule.fk_payment_type_id is None:
            return False
        pid = event_to_pt_id.get(pay.payment_type.strip())
        if pid is None:
            return False
        return pid == UUID(str(rule.fk_payment_type_id))

    @staticmethod
    def _payment_passes_rules(
        pay: _PayCtx,
        rules: Sequence[CampaignRule],
        event_to_pt_id: Mapping[str, UUID],
    ) -> bool:
        if not rules:
            return True
        includes = [r for r in rules if r.is_include]
        excludes = [r for r in rules if not r.is_include]
        for r in excludes:
            if CampaignService._payment_matches_rule(pay, r, event_to_pt_id):
                return False
        if not includes:
            return True
        return any(
            CampaignService._payment_matches_rule(pay, r, event_to_pt_id) for r in includes
        )

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
            fk_transaction_payment_temp_id=None,
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
            fk_transaction_payment_temp_id=None,
            line_no=line.line_no,
            discount_amount=amt,
            discount_rate=rate,
            temp_discount_type=CAMPAIGN_DISCOUNT_TYPE_CODE,
            discount_code=CampaignService._discount_code(campaign),
        )

    @staticmethod
    def _proposal_payment(
        campaign: Campaign,
        pay: _PayCtx,
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
            fk_transaction_payment_temp_id=pay.id,
            line_no=None,
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
        line_accum: Mapping[UUID, Decimal],
        doc_accum: Decimal,
        product_ctx: Optional[Mapping[UUID, Dict[str, Any]]],
    ) -> List[CampaignDiscountProposal]:
        eligible_total = CampaignService._eligible_net_after_stack(
            lines, rules, line_accum, doc_accum, product_ctx
        )
        if campaign.min_purchase_amount is not None:
            if eligible_total < Decimal(str(campaign.min_purchase_amount)):
                return []
        if campaign.max_purchase_amount is not None:
            if eligible_total > Decimal(str(campaign.max_purchase_amount)):
                return []

        dtype = (campaign.discount_type or "").upper()
        desc = (
            campaign.notification_message
            or campaign.description
            or campaign.name
            or campaign.code
            or ""
        ).strip()

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
    def _bxgy_line_pool(
        lines: Sequence[_LineCtx],
        rules: Sequence[CampaignRule],
        cps: Sequence[CampaignProduct],
        product_ctx: Optional[Mapping[UUID, Dict[str, Any]]],
    ) -> List[_LineCtx]:
        pool: List[_LineCtx] = []
        for line in lines:
            if not CampaignService._line_passes_rules(line, rules, product_ctx):
                continue
            if cps:
                if line.fk_product_id is None:
                    continue
                if not any(
                    UUID(str(cp.fk_product_id)) == UUID(str(line.fk_product_id)) for cp in cps
                ):
                    continue
            pool.append(line)
        return pool

    @staticmethod
    def _proposals_buy_x_get_y(
        campaign: Campaign,
        lines: Sequence[_LineCtx],
        rules: Sequence[CampaignRule],
        cps: Sequence[CampaignProduct],
        product_ctx: Optional[Mapping[UUID, Dict[str, Any]]],
        line_accum: Mapping[UUID, Decimal],
        doc_accum: Decimal,
    ) -> List[CampaignDiscountProposal]:
        dtype = (campaign.discount_type or "").upper()
        if dtype != "BUY_X_GET_Y":
            return []
        buy_q = int(campaign.buy_quantity or 0)
        get_q = int(campaign.get_quantity or 0)
        if buy_q <= 0 or get_q <= 0:
            return []

        eligible_total = CampaignService._eligible_net_after_stack(
            lines, rules, line_accum, doc_accum, product_ctx
        )
        if campaign.min_purchase_amount is not None:
            if eligible_total < Decimal(str(campaign.min_purchase_amount)):
                return []
        if campaign.max_purchase_amount is not None:
            if eligible_total > Decimal(str(campaign.max_purchase_amount)):
                return []

        pool_lines = CampaignService._bxgy_line_pool(lines, rules, cps, product_ctx)
        units: List[Tuple[Decimal, _LineCtx]] = []
        for ln in pool_lines:
            n = int(ln.quantity)
            if n <= 0:
                continue
            net_line = max(
                Decimal("0"), ln.line_total - line_accum.get(ln.id, Decimal("0"))
            )
            up = net_line / ln.quantity if ln.quantity > 0 else Decimal("0")
            for _ in range(n):
                units.append((up, ln))
        if not units:
            return []
        group = buy_q + get_q
        if len(units) < group:
            return []
        free_count = (len(units) // group) * get_q
        if free_count <= 0:
            return []
        units.sort(key=lambda x: x[0])
        raw = sum(u[0] for u in units[:free_count])
        if campaign.max_discount_amount is not None:
            cap = Decimal(str(campaign.max_discount_amount))
            raw = min(raw, cap)
        raw = min(raw, eligible_total)
        desc = (
            campaign.notification_message
            or campaign.description
            or campaign.name
            or campaign.code
            or ""
        ).strip()
        pr = CampaignService._proposal_document(
            campaign,
            raw,
            None,
            desc or f"Buy {buy_q} get {get_q}",
        )
        return [pr] if pr else []

    @staticmethod
    def _proposals_payment_discount(
        campaign: Campaign,
        pays: Sequence[_PayCtx],
        payment_rules: Sequence[CampaignRule],
        line_rules: Sequence[CampaignRule],
        lines: Sequence[_LineCtx],
        line_accum: Mapping[UUID, Decimal],
        doc_accum: Decimal,
        event_to_pt_id: Mapping[str, UUID],
        product_ctx: Optional[Mapping[UUID, Dict[str, Any]]],
    ) -> List[CampaignDiscountProposal]:
        if not pays:
            return []
        eligible_pays = [
            p
            for p in pays
            if CampaignService._payment_passes_rules(p, payment_rules, event_to_pt_id)
        ]
        if not eligible_pays:
            return []
        anchor = min(eligible_pays, key=lambda x: x.line_no)
        eligible_total = CampaignService._eligible_net_after_stack(
            lines, line_rules, line_accum, doc_accum, product_ctx
        )
        if campaign.min_purchase_amount is not None:
            if eligible_total < Decimal(str(campaign.min_purchase_amount)):
                return []
        if campaign.max_purchase_amount is not None:
            if eligible_total > Decimal(str(campaign.max_purchase_amount)):
                return []

        dtype = (campaign.discount_type or "").upper()
        desc = (
            campaign.notification_message
            or campaign.description
            or campaign.name
            or campaign.code
            or ""
        ).strip()

        if dtype == "PERCENTAGE":
            pct = Decimal(str(campaign.discount_percentage or 0))
            if pct <= 0:
                return []
            raw = eligible_total * (pct / Decimal("100"))
            if campaign.max_discount_amount is not None:
                cap = Decimal(str(campaign.max_discount_amount))
                raw = min(raw, cap)
            raw = min(raw, eligible_total)
            pr = CampaignService._proposal_payment(
                campaign, anchor, raw, pct, desc or f"{pct}% payment promo"
            )
            return [pr] if pr else []

        if dtype == "FIXED_AMOUNT":
            fixed = Decimal(str(campaign.discount_value or 0))
            if fixed <= 0:
                return []
            raw = min(fixed, eligible_total)
            pr = CampaignService._proposal_payment(
                campaign, anchor, raw, None, desc or f"{raw} payment promo"
            )
            return [pr] if pr else []

        return []

    @staticmethod
    def _proposals_product(
        campaign: Campaign,
        lines: Sequence[_LineCtx],
        rules: Sequence[CampaignRule],
        cps: Sequence[CampaignProduct],
        product_ctx: Optional[Mapping[UUID, Dict[str, Any]]],
        line_accum: Mapping[UUID, Decimal],
    ) -> List[CampaignDiscountProposal]:
        if not cps:
            return []

        out: List[CampaignDiscountProposal] = []
        dtype = (campaign.discount_type or "").upper()

        for line in lines:
            if not CampaignService._line_passes_rules(line, rules, product_ctx):
                continue
            line_net = max(
                Decimal("0"),
                line.line_total - line_accum.get(line.id, Decimal("0")),
            )
            if line_net <= 0:
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

                desc = (
                    campaign.notification_message
                    or campaign.description
                    or campaign.name
                    or ""
                ).strip()

                if dtype == "PERCENTAGE" and pct is not None:
                    pdec = Decimal(str(pct))
                    if pdec <= 0:
                        continue
                    raw = line_net * (pdec / Decimal("100"))
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
                    raw = min(fixed, line_net)
                    pr = CampaignService._proposal_line(
                        campaign, line, raw, None, desc or f"{raw} off {campaign.code}"
                    )
                    if pr:
                        out.append(pr)
                        break

        return out


__all__ = ["CampaignService", "CampaignDiscountProposal", "SUPPORTED_TYPE_CODES"]
