"""
SaleFlex.PyPOS - GateNotification model.

Persists inbound notifications received from SaleFlex.GATE so that:
- Notifications survive application restarts before the user acknowledges them.
- A complete notification history is available for audit/debugging.
- Unread counts can be queried without re-fetching from GATE.

Notification types (defined by GATE):
    "product_update"   → product / price data changed, rebuild product cache
    "campaign_update"  → campaign definitions changed, rebuild campaign cache
    "price_change"     → price-only change (subset of product_update)
    "terminal_message" → operator-to-operator message
    "system_alert"     → system-level alert (low disk, offline POS, etc.)
Copyright (C) 2025-2026 Mousavi.Tech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.sql import func

from data_layer.model.crud_model import Model, CRUD


class GateNotification(Model, CRUD):
    """
    Inbound notification record received from SaleFlex.GATE.

    Rows are created by NotificationSerializer.save_and_dispatch() and
    consumed (is_read = True) after the user acknowledges the notification
    in the UI or after the cache refresh it triggered is complete.
    """

    __tablename__ = "gate_notification"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    # Classification
    notification_type  = Column(String(50), nullable=False, index=True)
    title              = Column(String(255), nullable=True)
    body               = Column(Text, nullable=True)

    # Source terminal that sent the message (nullable for system-generated notifications)
    source_terminal_id = Column(String(100), nullable=True)

    # GATE-side identifier for deduplication and read-receipt acknowledgement
    gate_notification_id = Column(String(100), nullable=True, unique=True)

    # Read state
    is_read     = Column(Boolean, nullable=False, default=False)
    read_at     = Column(DateTime, nullable=True)

    # Timestamps
    received_at = Column(DateTime, server_default=func.now())

    # ------------------------------------------------------------------
    # Convenience class methods
    # ------------------------------------------------------------------

    @classmethod
    def create_from_payload(cls, payload: dict) -> "GateNotification":
        """
        Create and persist a notification from a GATE API response payload.

        Args:
            payload: Single notification dict from GATE's notifications endpoint.

        Returns:
            Persisted GateNotification instance.
        """
        notif = cls()
        notif.notification_type    = payload.get("type", "unknown")
        notif.title                = payload.get("title", "")
        notif.body                 = payload.get("body", "")
        notif.source_terminal_id   = payload.get("source_terminal_id")
        notif.gate_notification_id = payload.get("id")
        notif.is_read              = False
        notif.save()
        return notif

    @classmethod
    def get_unread(cls):
        """
        Return all unread notifications ordered by received_at ascending.

        Returns:
            List of GateNotification instances with is_read=False.
        """
        # TODO: Implement DB query.
        # with Engine().get_session() as session:
        #     return (session.query(cls)
        #             .filter(cls.is_read == False)
        #             .order_by(cls.received_at)
        #             .all())
        return []

    def mark_read(self) -> None:
        """Mark this notification as read and record the timestamp."""
        self.is_read = True
        self.read_at = datetime.utcnow()
        self.save()
