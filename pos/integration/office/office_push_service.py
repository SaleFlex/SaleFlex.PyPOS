"""
SaleFlex.PyPOS - Office Push Service

Serialises completed TransactionHead records and all their related line items,
then forwards the payload to SaleFlex.OFFICE via the REST API.  Maintains an
OfficePushQueue table in the local SQLite database to track which documents
have been successfully delivered and to enable retry on failure.

Public interface
----------------
OfficePushService.enqueue(transaction_head_id)
    Call this immediately after a document is closed. Adds a 'pending' row to
    the queue and triggers a non-blocking push attempt.

OfficePushService.flush_pending()
    Push every 'pending' or 'failed' queue entry to OFFICE.  Returns True when
    all items were dispatched successfully, False otherwise.

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
    def flush_pending() -> bool:
        """
        Push all 'pending' and 'failed' queue items to OFFICE in a single batch.

        Sends the transactions and the current sequence counters together in
        one HTTP request.  On success each item is marked 'sent'; on failure
        each is marked 'failed' with an error message.

        The method is structured in three isolated phases so that SQLite
        sessions are never nested (which can cause "database is locked" errors
        with concurrent threads):

          Phase 1 – Read the queue  : open session, load rows, close session.
          Phase 2 – Build payloads  : each transaction loaded in its own session
                                      (no outer session is held open).
          Phase 3 – HTTP push       : no SQLite session; update statuses after.

        Returns True when all items were dispatched without error, False when
        at least one item could not be delivered.
        """
        if not OfficePushService.is_office_mode():
            return True

        from data_layer.engine import Engine
        from data_layer.model.definition.office_push_queue import OfficePushQueue
        from integration.office_client import OfficeClient, OfficeConnectionError

        # ----------------------------------------------------------------
        # Phase 1: Read queue – close the session before any other DB work
        # ----------------------------------------------------------------
        pending_items: list[dict] = []
        try:
            with Engine().get_session() as session:
                rows = (
                    session.query(OfficePushQueue)
                    .filter(OfficePushQueue.status.in_(["pending", "failed"]))
                    .order_by(OfficePushQueue.created_at.asc())
                    .all()
                )
                # Extract plain Python values while the session is open;
                # the session is closed as soon as the 'with' block exits.
                for row in rows:
                    pending_items.append({
                        "id":                      row.id,
                        "fk_transaction_head_id":  row.fk_transaction_head_id,
                        "transaction_unique_id":   row.transaction_unique_id,
                    })
        except Exception as exc:
            logger.error("[OfficePushService] Error reading push queue: %s", exc)
            return False

        if not pending_items:
            return True

        logger.info(
            "[OfficePushService] %d item(s) pending in push queue", len(pending_items)
        )

        # ----------------------------------------------------------------
        # Phase 2: Build payloads – each in its own short-lived session
        # ----------------------------------------------------------------
        queue_ids:    list[Any] = []
        transactions: list[dict] = []

        for item in pending_items:
            head_id = item["fk_transaction_head_id"]
            tx_id   = item["transaction_unique_id"]
            try:
                payload = _build_transaction_payload(head_id)
            except Exception as exc:
                logger.error(
                    "[OfficePushService] Error building payload for %s: %s", tx_id, exc
                )
                _mark_queue_failed(item["id"], f"Payload build error: {exc}")
                continue

            if payload is None:
                logger.warning(
                    "[OfficePushService] TransactionHead not found for queue item %s "
                    "(tx=%s) – marking failed",
                    item["id"], tx_id,
                )
                _mark_queue_failed(item["id"], "TransactionHead not found in local DB")
                continue

            queue_ids.append(item["id"])
            transactions.append(payload)
            logger.debug(
                "[OfficePushService] Payload built for transaction: %s", tx_id
            )

        if not transactions:
            logger.warning("[OfficePushService] No valid payloads to push")
            return False

        # ----------------------------------------------------------------
        # Phase 3: Push to OFFICE – no SQLite session held during HTTP call
        # ----------------------------------------------------------------
        sequences = _get_current_sequences()
        pos_id    = _get_pos_id()

        logger.info(
            "[OfficePushService] Pushing %d transaction(s) to OFFICE (pos_id=%d) ...",
            len(transactions), pos_id,
        )

        client = OfficeClient()
        try:
            result = client.push_transactions(
                pos_id=pos_id,
                transactions=transactions,
                sequences=sequences,
            )
            status  = result.get("status", "error")
            success = (status == "ok")
        except OfficeConnectionError as exc:
            logger.warning("[OfficePushService] OFFICE unreachable: %s", exc)
            for qid in queue_ids:
                _mark_queue_failed(qid, str(exc))
            return False
        except Exception as exc:
            logger.error("[OfficePushService] Push error: %s", exc, exc_info=True)
            for qid in queue_ids:
                _mark_queue_failed(qid, str(exc))
            return False

        # ----------------------------------------------------------------
        # Phase 3b: Update queue status (session closed during HTTP above)
        # ----------------------------------------------------------------
        if success:
            for qid in queue_ids:
                _mark_queue_sent(qid)
            logger.info(
                "[OfficePushService] Successfully pushed %d transaction(s) to OFFICE",
                len(queue_ids),
            )
        else:
            error_msg = result.get("message", "OFFICE returned non-ok status")
            for qid in queue_ids:
                _mark_queue_failed(qid, error_msg)
            logger.warning(
                "[OfficePushService] Push rejected by OFFICE: %s", error_msg
            )

        return success

    @staticmethod
    def has_pending() -> bool:
        """Return True when there are unsent (pending or failed) queue items."""
        from data_layer.engine import Engine
        from data_layer.model.definition.office_push_queue import OfficePushQueue

        try:
            with Engine().get_session() as session:
                count = (
                    session.query(OfficePushQueue)
                    .filter(OfficePushQueue.status.in_(["pending", "failed"]))
                    .count()
                )
                return count > 0
        except Exception:
            return False
