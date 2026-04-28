"""
SaleFlex.PyPOS - Office Push Queue Model

Tracks the synchronisation state of each completed transaction that must be
forwarded to SaleFlex.OFFICE.  A row is created for every closed document and
updated as the background push worker processes them.

Status values
-------------
pending  – Created, not yet sent to OFFICE.
sent     – Successfully received and acknowledged by OFFICE.
failed   – Last attempt failed; will be retried.
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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, UUID, ForeignKey, Index
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class OfficePushQueue(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    One row per completed TransactionHead that needs to be pushed to OFFICE.

    The background OfficePushWorker reads rows with status='pending' or
    status='failed' and attempts to forward them via the OFFICE REST API.
    """

    def __init__(
        self,
        fk_transaction_head_id=None,
        transaction_unique_id: str = None,
        status: str = "pending",
    ):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_transaction_head_id = fk_transaction_head_id
        self.transaction_unique_id  = transaction_unique_id
        self.status                 = status
        self.retry_count            = 0

    __tablename__ = "office_push_queue"

    id = Column(UUID, primary_key=True, default=uuid4)

    # Reference to the completed transaction head
    fk_transaction_head_id = Column(
        UUID,
        ForeignKey("transaction_head.id"),
        nullable=False,
        index=True,
    )
    transaction_unique_id = Column(String(50), nullable=False, index=True)

    # Synchronisation state: 'pending' | 'sent' | 'failed'
    status = Column(String(20), nullable=False, default="pending", index=True)

    retry_count     = Column(Integer,  nullable=False, default=0)
    sent_at         = Column(DateTime, nullable=True)
    last_attempt_at = Column(DateTime, nullable=True)
    error_message   = Column(String(500), nullable=True)

    __table_args__ = (
        Index("idx_office_push_status",  "status"),
        Index("idx_office_push_tx_head", "fk_transaction_head_id"),
    )

    def __repr__(self):
        return (
            f"<OfficePushQueue(tx='{self.transaction_unique_id}', "
            f"status='{self.status}', retries={self.retry_count})>"
        )
