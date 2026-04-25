"""
SaleFlex.PyPOS - Office Closure Push Queue Model

Tracks the synchronisation state of completed end-of-day closures that must be
forwarded to SaleFlex.OFFICE.  The background OfficePushWorker retries failed
rows without blocking the main POS application.
"""

from sqlalchemy import Column, Integer, String, DateTime, UUID, ForeignKey, Index
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class OfficeClosurePushQueue(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    One row per completed Closure that needs to be pushed to OFFICE.
    """

    def __init__(
        self,
        fk_closure_id=None,
        closure_unique_id: str = None,
        status: str = "pending",
    ):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_closure_id = fk_closure_id
        self.closure_unique_id = closure_unique_id
        self.status = status
        self.retry_count = 0

    __tablename__ = "office_closure_push_queue"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_closure_id = Column(
        UUID,
        ForeignKey("closure.id"),
        nullable=False,
        index=True,
    )
    closure_unique_id = Column(String(50), nullable=False, index=True)

    # Synchronisation state: 'pending' | 'sent' | 'failed'
    status = Column(String(20), nullable=False, default="pending", index=True)

    retry_count = Column(Integer, nullable=False, default=0)
    sent_at = Column(DateTime, nullable=True)
    last_attempt_at = Column(DateTime, nullable=True)
    error_message = Column(String(500), nullable=True)

    __table_args__ = (
        Index("idx_office_closure_push_status", "status"),
        Index("idx_office_closure_push_closure", "fk_closure_id"),
    )

    def __repr__(self):
        return (
            f"<OfficeClosurePushQueue(closure='{self.closure_unique_id}', "
            f"status='{self.status}', retries={self.retry_count})>"
        )
