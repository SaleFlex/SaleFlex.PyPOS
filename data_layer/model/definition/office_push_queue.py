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
