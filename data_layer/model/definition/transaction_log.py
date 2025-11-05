"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025 Ferhat Mousavi (ferhat.mousavi@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from sqlalchemy import (
    Column, Integer, BigInteger, Boolean, String,
    DateTime, Float, ForeignKey, UUID, Numeric, Index, func
)

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin

from uuid import uuid4


class TransactionLog(Model, CRUD, AuditMixin):
    """
    Comprehensive audit log for all transaction changes.
    Essential for compliance and troubleshooting.
    No temp version needed.
    Note: Uses AuditMixin to track who created the log entry and when.
    Intentionally does NOT use SoftDeleteMixin - log entries should never be deleted.
    """

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_log"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head.id"), index=True)

    # What changed
    entity_type = Column(String(50), nullable=False, index=True)  # "head", "product", "payment"
    entity_id = Column(UUID, nullable=True)
    action = Column(String(50), nullable=False, index=True)  # "create", "update", "delete", "void"

    # Change details
    field_name = Column(String(100), nullable=True)
    old_value = Column(String(1000), nullable=True)
    new_value = Column(String(1000), nullable=True)

    # Context
    change_reason = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Who & When (legacy fields - kept for backward compatibility, but AuditMixin provides these too)
    fk_cashier_id = Column(UUID, ForeignKey("cashier.id"), index=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return f"<TransactionLog(action='{self.action}', entity='{self.entity_type}')>"

    __table_args__ = (
        Index('idx_log_transaction', 'fk_transaction_head_id'),
        Index('idx_log_timestamp', 'timestamp'),
        Index('idx_log_entity', 'entity_type', 'entity_id'),
    )
