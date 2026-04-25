"""
SaleFlex.PyPOS - Office Push Service

Serialises completed TransactionHead and Closure records with their related
detail rows, then forwards the payloads to SaleFlex.OFFICE via the REST API.
Maintains local queue tables to track which items have been successfully
delivered and to enable retry on failure.

Public interface
----------------
OfficePushService.enqueue(transaction_head_id)
    Call this immediately after a document is closed. Adds a 'pending' row to
    the queue and triggers a non-blocking push attempt.

OfficePushService.enqueue_closure(closure_id)
    Call this immediately after a closure is completed. Adds a 'pending' row to
    the closure queue and triggers a non-blocking push attempt.

OfficePushService.flush_pending()
    Push every 'pending' or 'failed' document and closure queue entry to OFFICE.
    Returns True when all items were dispatched successfully, False otherwise.

OfficePushService.is_office_mode() -> bool
    Returns True only when the app is running in 'office' mode.

Copyright (c) 2025-2026 Ferhat Mousavi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from core.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers – serialisation
# ---------------------------------------------------------------------------

def _row_to_dict(obj) -> dict[str, Any] | None:
    """
    Convert an SQLAlchemy ORM object to a JSON-serialisable dict.

    Falls back to the model's to_dict() method when available; otherwise
    iterates over the mapped column attributes directly.
    """
    if obj is None:
        return None
    if hasattr(obj, "to_dict"):
        try:
            return obj.to_dict()
        except Exception:
            pass
    try:
        from sqlalchemy import inspect as sa_inspect
        mapper = sa_inspect(type(obj))
        result: dict[str, Any] = {}
        for col in mapper.column_attrs:
            val = getattr(obj, col.key, None)
            if isinstance(val, datetime):
                result[col.key] = val.isoformat()
            elif hasattr(val, "hex"):          # UUID
                result[col.key] = str(val)
            else:
                result[col.key] = val
        return result
    except Exception as exc:
        logger.warning("[OfficePushService] _row_to_dict failed: %s", exc)
        return {}


def _build_transaction_payload(transaction_head_id) -> dict[str, Any] | None:
    """
    Load a completed TransactionHead and all its line-item children from the
    local database and return a single transaction dict ready for the OFFICE
    REST API.

    Returns None when the head cannot be found.
    """
    from uuid import UUID
    from data_layer.engine import Engine
    from data_layer.model.definition.transaction_head import TransactionHead
    from data_layer.model.definition.transaction_product import TransactionProduct
    from data_layer.model.definition.transaction_payment import TransactionPayment
    from data_layer.model.definition.transaction_discount import TransactionDiscount
    from data_layer.model.definition.transaction_department import TransactionDepartment
    from data_layer.model.definition.transaction_tax import TransactionTax
    from data_layer.model.definition.transaction_tip import TransactionTip
    from data_layer.model.definition.transaction_surcharge import TransactionSurcharge
    from data_layer.model.definition.transaction_note import TransactionNote
    from data_layer.model.definition.Transaction_loyalty import TransactionLoyalty
    from data_layer.model.definition.transaction_fiscal import TransactionFiscal
    from data_layer.model.definition.transaction_refund import TransactionRefund
    from data_layer.model.definition.transaction_change import TransactionChange
    from data_layer.model.definition.transaction_delivery import TransactionDelivery
    from data_layer.model.definition.transaction_kitchen_order import TransactionKitchenOrder

    try:
        head_uuid = UUID(str(transaction_head_id))
    except (ValueError, AttributeError):
        logger.error("[OfficePushService] Invalid head id: %s", transaction_head_id)
        return None

    with Engine().get_session() as session:
        head = (
            session.query(TransactionHead)
            .filter(TransactionHead.id == head_uuid)
            .first()
        )
        if head is None:
            logger.error(
                "[OfficePushService] TransactionHead not found: %s", head_uuid
            )
            return None

        def _load_lines(model_cls, fk_field):
            return [
                _row_to_dict(r)
                for r in session.query(model_cls)
                .filter(getattr(model_cls, fk_field) == head_uuid)
                .all()
            ]

        fiscal_row = (
            session.query(TransactionFiscal)
            .filter(TransactionFiscal.fk_transaction_head_id == head_uuid)
            .first()
        )

        return {
            "head":           _row_to_dict(head),
            "products":       _load_lines(TransactionProduct,     "fk_transaction_head_id"),
            "payments":       _load_lines(TransactionPayment,     "fk_transaction_head_id"),
            "discounts":      _load_lines(TransactionDiscount,    "fk_transaction_head_id"),
            "departments":    _load_lines(TransactionDepartment,  "fk_transaction_head_id"),
            "taxes":          _load_lines(TransactionTax,         "fk_transaction_head_id"),
            "tips":           _load_lines(TransactionTip,         "fk_transaction_head_id"),
            "surcharges":     _load_lines(TransactionSurcharge,   "fk_transaction_head_id"),
            "notes":          _load_lines(TransactionNote,        "fk_transaction_head_id"),
            "loyalty":        _load_lines(TransactionLoyalty,     "fk_transaction_head_id"),
            "refunds":        _load_lines(TransactionRefund,      "fk_transaction_head_id"),
            "changes":        _load_lines(TransactionChange,      "fk_transaction_head_id"),
            "deliveries":     _load_lines(TransactionDelivery,    "fk_transaction_head_id"),
            "kitchen_orders": _load_lines(TransactionKitchenOrder, "fk_transaction_head_id"),
            "fiscal":         _row_to_dict(fiscal_row),
        }


def _build_closure_payload(closure_id) -> dict[str, Any] | None:
    """
    Load a completed Closure and all related summary rows from the local
    database and return a single closure dict ready for the OFFICE REST API.
    """
    from uuid import UUID
    from data_layer.engine import Engine
    from data_layer.model.definition.closure import Closure
    from data_layer.model.definition.closure_vat_summary import ClosureVATSummary
    from data_layer.model.definition.closure_tip_summary import ClosureTipSummary
    from data_layer.model.definition.closure_discount_summary import ClosureDiscountSummary
    from data_layer.model.definition.closure_payment_type_summary import ClosurePaymentTypeSummary
    from data_layer.model.definition.closure_document_type_summary import ClosureDocumentTypeSummary
    from data_layer.model.definition.closure_department_summary import ClosureDepartmentSummary
    from data_layer.model.definition.closure_currency import ClosureCurrency
    from data_layer.model.definition.closure_cashier_summary import ClosureCashierSummary
    from data_layer.model.definition.closure_country_specific import ClosureCountrySpecific

    try:
        closure_uuid = UUID(str(closure_id))
    except (ValueError, AttributeError):
        logger.error("[OfficePushService] Invalid closure id: %s", closure_id)
        return None

    with Engine().get_session() as session:
        closure = session.query(Closure).filter(Closure.id == closure_uuid).first()
        if closure is None:
            logger.error("[OfficePushService] Closure not found: %s", closure_uuid)
            return None

        def _load_rows(model_cls):
            return [
                _row_to_dict(r)
                for r in session.query(model_cls)
                .filter(model_cls.fk_closure_id == closure_uuid)
                .all()
            ]

        country_specific = (
            session.query(ClosureCountrySpecific)
            .filter(ClosureCountrySpecific.fk_closure_id == closure_uuid)
            .first()
        )

        return {
            "closure":                 _row_to_dict(closure),
            "vat_summaries":           _load_rows(ClosureVATSummary),
            "tip_summaries":           _load_rows(ClosureTipSummary),
            "discount_summaries":      _load_rows(ClosureDiscountSummary),
            "payment_type_summaries":  _load_rows(ClosurePaymentTypeSummary),
            "document_type_summaries": _load_rows(ClosureDocumentTypeSummary),
            "department_summaries":    _load_rows(ClosureDepartmentSummary),
            "currency_summaries":      _load_rows(ClosureCurrency),
            "cashier_summaries":       _load_rows(ClosureCashierSummary),
            "country_specific":        _row_to_dict(country_specific),
        }


def _get_current_sequences() -> list[dict[str, Any]]:
    """
    Return the current sequence counter values from the local database.

    Queries the TransactionSequence table and returns a list of
    {"name": ..., "value": ...} dicts ready for the OFFICE payload.
    """
    from data_layer.engine import Engine
    from data_layer.model.definition.transaction_sequence import TransactionSequence

    sequences = []
    try:
        with Engine().get_session() as session:
            rows = session.query(TransactionSequence).all()
            for row in rows:
                if row.name and row.value is not None:
                    sequences.append({"name": row.name, "value": row.value})
    except Exception as exc:
        logger.warning("[OfficePushService] Could not read sequences: %s", exc)
    return sequences


def _get_pos_id() -> int:
    """Return the pos_no_in_store for this terminal from PosSettings."""
    try:
        from data_layer.engine import Engine
        from data_layer.model.definition.pos_settings import PosSettings
        with Engine().get_session() as session:
            settings = session.query(PosSettings).first()
            if settings and hasattr(settings, "pos_no_in_store"):
                return int(settings.pos_no_in_store or 1)
    except Exception:
        pass
    return 1


# ---------------------------------------------------------------------------
# OfficePushQueue helpers
# ---------------------------------------------------------------------------

def _mark_queue_sent(queue_id) -> None:
    from uuid import UUID
    from data_layer.engine import Engine
    from data_layer.model.definition.office_push_queue import OfficePushQueue

    now = datetime.now(timezone.utc)
    try:
        with Engine().get_session() as session:
            q = session.query(OfficePushQueue).filter(
                OfficePushQueue.id == queue_id
            ).first()
            if q:
                q.status          = "sent"
                q.sent_at         = now
                q.last_attempt_at = now
                q.error_message   = None
                session.commit()
    except Exception as exc:
        logger.warning("[OfficePushService] Could not mark queue item sent: %s", exc)


def _mark_queue_failed(queue_id, error: str) -> None:
    from data_layer.engine import Engine
    from data_layer.model.definition.office_push_queue import OfficePushQueue

    now = datetime.now(timezone.utc)
    try:
        with Engine().get_session() as session:
            q = session.query(OfficePushQueue).filter(
                OfficePushQueue.id == queue_id
            ).first()
            if q:
                q.status          = "failed"
                q.last_attempt_at = now
                q.retry_count     = (q.retry_count or 0) + 1
                q.error_message   = str(error)[:500]
                session.commit()
    except Exception as exc:
        logger.warning("[OfficePushService] Could not mark queue item failed: %s", exc)


def _mark_closure_queue_sent(queue_id) -> None:
    from data_layer.engine import Engine
    from data_layer.model.definition.office_closure_push_queue import OfficeClosurePushQueue

    now = datetime.now(timezone.utc)
    try:
        with Engine().get_session() as session:
            q = session.query(OfficeClosurePushQueue).filter(
                OfficeClosurePushQueue.id == queue_id
            ).first()
            if q:
                q.status = "sent"
                q.sent_at = now
                q.last_attempt_at = now
                q.error_message = None
                session.commit()
    except Exception as exc:
        logger.warning("[OfficePushService] Could not mark closure queue item sent: %s", exc)


def _mark_closure_queue_failed(queue_id, error: str) -> None:
    from data_layer.engine import Engine
    from data_layer.model.definition.office_closure_push_queue import OfficeClosurePushQueue

    now = datetime.now(timezone.utc)
    try:
        with Engine().get_session() as session:
            q = session.query(OfficeClosurePushQueue).filter(
                OfficeClosurePushQueue.id == queue_id
            ).first()
            if q:
                q.status = "failed"
                q.last_attempt_at = now
                q.retry_count = (q.retry_count or 0) + 1
                q.error_message = str(error)[:500]
                session.commit()
    except Exception as exc:
        logger.warning("[OfficePushService] Could not mark closure queue item failed: %s", exc)


# ---------------------------------------------------------------------------
# Public service
# ---------------------------------------------------------------------------

class OfficePushService:
    """
    Manages the OFFICE push queue for completed POS transactions.

    This service is used in two scenarios:
    1. Immediately after a document is closed (via enqueue + background push).
    2. Periodically by OfficePushWorker to retry any pending/failed items.
    """

    @staticmethod
    def is_office_mode() -> bool:
        """Return True when the POS is running in 'office' mode."""
        try:
            from settings.settings import Settings
            return Settings().app_mode == "office"
        except Exception:
            return False

    @staticmethod
    def enqueue(transaction_head_id, transaction_unique_id: str = "") -> None:
        """
        Add a completed transaction to the push queue with status 'pending'.

        This is safe to call from the main thread; the actual HTTP push runs
        via flush_pending() which is called from a background thread.

        Parameters
        ----------
        transaction_head_id:
            UUID of the TransactionHead record.
        transaction_unique_id:
            Human-readable transaction identifier for logging and deduplication.
        """
        if not OfficePushService.is_office_mode():
            return

        from data_layer.engine import Engine
        from data_layer.model.definition.office_push_queue import OfficePushQueue

        try:
            with Engine().get_session() as session:
                # Avoid duplicate queue entries
                existing = (
                    session.query(OfficePushQueue)
                    .filter(
                        OfficePushQueue.fk_transaction_head_id == transaction_head_id,
                        OfficePushQueue.status.in_(["pending", "sent"]),
                    )
                    .first()
                )
                if existing:
                    logger.debug(
                        "[OfficePushService] Transaction already queued: %s",
                        transaction_unique_id,
                    )
                    return

                q = OfficePushQueue(
                    fk_transaction_head_id=transaction_head_id,
                    transaction_unique_id=transaction_unique_id,
                    status="pending",
                )
                session.add(q)
                session.commit()

            logger.info(
                "[OfficePushService] Enqueued transaction: %s", transaction_unique_id
            )
        except Exception as exc:
            logger.error(
                "[OfficePushService] Failed to enqueue transaction %s: %s",
                transaction_unique_id, exc,
            )

    @staticmethod
    def enqueue_closure(closure_id, closure_unique_id: str = "") -> None:
        """
        Add a completed closure to the push queue with status 'pending'.

        The HTTP push is performed later by OfficePushWorker so the UI thread
        remains responsive during end-of-day processing.
        """
        if not OfficePushService.is_office_mode():
            return

        from data_layer.engine import Engine
        from data_layer.model.definition.office_closure_push_queue import OfficeClosurePushQueue

        try:
            with Engine().get_session() as session:
                existing = (
                    session.query(OfficeClosurePushQueue)
                    .filter(
                        OfficeClosurePushQueue.fk_closure_id == closure_id,
                        OfficeClosurePushQueue.status.in_(["pending", "sent"]),
                    )
                    .first()
                )
                if existing:
                    logger.debug(
                        "[OfficePushService] Closure already queued: %s",
                        closure_unique_id,
                    )
                    return

                q = OfficeClosurePushQueue(
                    fk_closure_id=closure_id,
                    closure_unique_id=closure_unique_id,
                    status="pending",
                )
                session.add(q)
                session.commit()

            logger.info("[OfficePushService] Enqueued closure: %s", closure_unique_id)
        except Exception as exc:
            logger.error(
                "[OfficePushService] Failed to enqueue closure %s: %s",
                closure_unique_id,
                exc,
            )

    @staticmethod
    def flush_pending() -> bool:
        """
        Push all 'pending' and 'failed' documents and closures to OFFICE.

        Each queue item is sent in its own REST request.  This keeps retry
        status precise: one bad document or closure does not hide the result of
        the remaining queue.  Current sequence counters are included with every
        request.

        Returns True when all items were dispatched without error, False when
        at least one item could not be delivered.
        """
        if not OfficePushService.is_office_mode():
            return True

        from data_layer.engine import Engine
        from data_layer.model.definition.office_push_queue import OfficePushQueue
        from data_layer.model.definition.office_closure_push_queue import OfficeClosurePushQueue
        from integration.office_client import OfficeClient, OfficeConnectionError

        transaction_items: list[dict] = []
        closure_items: list[dict] = []
        try:
            with Engine().get_session() as session:
                tx_rows = (
                    session.query(OfficePushQueue)
                    .filter(OfficePushQueue.status.in_(["pending", "failed"]))
                    .order_by(OfficePushQueue.created_at.asc())
                    .all()
                )
                closure_rows = (
                    session.query(OfficeClosurePushQueue)
                    .filter(OfficeClosurePushQueue.status.in_(["pending", "failed"]))
                    .order_by(OfficeClosurePushQueue.created_at.asc())
                    .all()
                )
                for row in tx_rows:
                    transaction_items.append({
                        "id":                      row.id,
                        "fk_transaction_head_id":  row.fk_transaction_head_id,
                        "transaction_unique_id":   row.transaction_unique_id,
                    })
                for row in closure_rows:
                    closure_items.append({
                        "id":                row.id,
                        "fk_closure_id":     row.fk_closure_id,
                        "closure_unique_id": row.closure_unique_id,
                    })
        except Exception as exc:
            logger.error("[OfficePushService] Error reading push queue: %s", exc)
            return False

        if not transaction_items and not closure_items:
            return True

        logger.info(
            "[OfficePushService] Pending OFFICE queue: %d transaction(s), %d closure(s)",
            len(transaction_items),
            len(closure_items),
        )

        client = OfficeClient()
        pos_id = _get_pos_id()
        all_success = True

        for item in transaction_items:
            tx_id = item["transaction_unique_id"]
            try:
                payload = _build_transaction_payload(item["fk_transaction_head_id"])
            except Exception as exc:
                logger.error(
                    "[OfficePushService] Error building payload for %s: %s", tx_id, exc
                )
                _mark_queue_failed(item["id"], f"Payload build error: {exc}")
                all_success = False
                continue

            if payload is None:
                logger.warning(
                    "[OfficePushService] TransactionHead not found for queue item %s "
                    "(tx=%s) – marking failed",
                    item["id"], tx_id,
                )
                _mark_queue_failed(item["id"], "TransactionHead not found in local DB")
                all_success = False
                continue

            try:
                result = client.push_transactions(
                    pos_id=pos_id,
                    transactions=[payload],
                    sequences=_get_current_sequences(),
                )
                if result.get("status") == "ok" and int(result.get("accepted", 0)) == 1:
                    _mark_queue_sent(item["id"])
                    logger.info("[OfficePushService] Transaction sent to OFFICE: %s", tx_id)
                else:
                    error_msg = result.get("message", "OFFICE rejected transaction")
                    _mark_queue_failed(item["id"], error_msg)
                    all_success = False
            except OfficeConnectionError as exc:
                logger.warning("[OfficePushService] OFFICE unreachable: %s", exc)
                _mark_queue_failed(item["id"], str(exc))
                all_success = False
            except Exception as exc:
                logger.error("[OfficePushService] Transaction push error: %s", exc, exc_info=True)
                _mark_queue_failed(item["id"], str(exc))
                all_success = False

        for item in closure_items:
            closure_uid = item["closure_unique_id"]
            try:
                payload = _build_closure_payload(item["fk_closure_id"])
            except Exception as exc:
                logger.error(
                    "[OfficePushService] Error building closure payload for %s: %s",
                    closure_uid,
                    exc,
                )
                _mark_closure_queue_failed(item["id"], f"Payload build error: {exc}")
                all_success = False
                continue

            if payload is None:
                _mark_closure_queue_failed(item["id"], "Closure not found in local DB")
                all_success = False
                continue

            try:
                result = client.push_closures(
                    pos_id=pos_id,
                    closures=[payload],
                    sequences=_get_current_sequences(),
                )
                if result.get("status") == "ok" and int(result.get("accepted", 0)) == 1:
                    _mark_closure_queue_sent(item["id"])
                    logger.info("[OfficePushService] Closure sent to OFFICE: %s", closure_uid)
                else:
                    error_msg = result.get("message", "OFFICE rejected closure")
                    _mark_closure_queue_failed(item["id"], error_msg)
                    all_success = False
            except OfficeConnectionError as exc:
                logger.warning("[OfficePushService] OFFICE unreachable: %s", exc)
                _mark_closure_queue_failed(item["id"], str(exc))
                all_success = False
            except Exception as exc:
                logger.error("[OfficePushService] Closure push error: %s", exc, exc_info=True)
                _mark_closure_queue_failed(item["id"], str(exc))
                all_success = False

        return all_success

    @staticmethod
    def has_pending() -> bool:
        """Return True when there are unsent document or closure queue items."""
        from data_layer.engine import Engine
        from data_layer.model.definition.office_push_queue import OfficePushQueue
        from data_layer.model.definition.office_closure_push_queue import OfficeClosurePushQueue

        try:
            with Engine().get_session() as session:
                tx_count = (
                    session.query(OfficePushQueue)
                    .filter(OfficePushQueue.status.in_(["pending", "failed"]))
                    .count()
                )
                closure_count = (
                    session.query(OfficeClosurePushQueue)
                    .filter(OfficeClosurePushQueue.status.in_(["pending", "failed"]))
                    .count()
                )
                return (tx_count + closure_count) > 0
        except Exception:
            return False
