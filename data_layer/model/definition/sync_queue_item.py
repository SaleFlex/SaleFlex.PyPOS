"""
SaleFlex.PyPOS - SyncQueueItem model.

Implements the offline outbox pattern for the integration layer.
Every event that must be sent to an external system (GATE, ERP, payment
gateway) is first written as a SyncQueueItem row with status="pending".
SyncWorker processes the queue in the background and updates the status to
"sent" on success or increments retry_count on failure.

Copyright (c) 2026 Ferhat Mousavi

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

import json
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean
from sqlalchemy.sql import func

from data_layer.model.crud_model import Model, CRUD


class SyncQueueItem(Model, CRUD):
    """
    Offline outbox record for the integration layer.

    Status flow:
        pending → sent       (happy path)
        pending → failed     (all retries exhausted)
        failed  → pending    (manual reset for retry)

    Connector types:
        "gate"          → SaleFlex.GATE (transactions, closures, warehouse)
        "gate_erp"      → GATE-managed ERP relay
        "gate_payment"  → GATE-managed payment relay
        "erp"           → Direct third-party ERP connector
        "payment"       → Direct third-party payment gateway

    Event types:
        "transaction"         → completed sale document
        "closure"             → end-of-day closure
        "warehouse_movement"  → stock movement record
        "erp_sync"            → generic ERP payload
        "payment"             → payment request / confirmation
    """

    __tablename__ = "sync_queue_item"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    # Routing fields
    connector_type = Column(String(50), nullable=False, index=True)
    event_type     = Column(String(50), nullable=False, index=True)

    # JSON payload to be transmitted
    payload = Column(Text, nullable=False, default="{}")

    # Status tracking
    status        = Column(String(20), nullable=False, default="pending", index=True)
    retry_count   = Column(Integer, nullable=False, default=0)
    max_retries   = Column(Integer, nullable=False, default=3)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    sent_at    = Column(DateTime, nullable=True)

    # ------------------------------------------------------------------
    # Convenience class methods
    # ------------------------------------------------------------------

    @classmethod
    def create_pending(cls, connector_type: str, event_type: str,
                       payload: dict) -> "SyncQueueItem":
        """
        Create and persist a new pending outbox item.

        Args:
            connector_type: Routing key ("gate", "gate_erp", "erp", …).
            event_type:     Event category ("transaction", "closure", …).
            payload:        Data dict to be serialised as JSON.

        Returns:
            Persisted SyncQueueItem instance.
        """
        item = cls()
        item.connector_type = connector_type
        item.event_type = event_type
        item.payload = json.dumps(payload)
        item.status = "pending"
        item.save()
        return item

    @classmethod
    def get_pending(cls, connector_type: str | None = None):
        """
        Return all pending items, optionally filtered by connector_type.

        Args:
            connector_type: If provided, filter by this connector.

        Returns:
            List of SyncQueueItem instances with status="pending".
        """
        # TODO: Implement DB query using SQLAlchemy session.
        # Example:
        # with Engine().get_session() as session:
        #     q = session.query(cls).filter(cls.status == "pending")
        #     if connector_type:
        #         q = q.filter(cls.connector_type == connector_type)
        #     return q.order_by(cls.created_at).all()
        return []

    def get_payload_dict(self) -> dict:
        """Deserialise the stored JSON payload to a dict."""
        try:
            return json.loads(self.payload)
        except (json.JSONDecodeError, TypeError):
            return {}

    def mark_sent(self) -> None:
        """Update status to 'sent' and record the transmission timestamp."""
        self.status = "sent"
        self.sent_at = datetime.utcnow()
        self.save()

    def increment_retry(self, error_message: str = "") -> None:
        """
        Increment retry_count.  Mark as 'failed' when max_retries is reached.

        Args:
            error_message: Description of the failure for diagnostics.
        """
        self.retry_count += 1
        self.error_message = error_message
        if self.retry_count >= self.max_retries:
            self.status = "failed"
        self.save()
