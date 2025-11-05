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


class TransactionVoid(Model, CRUD, AuditMixin):
    """
    Audit trail for voided transactions.
    No temp version needed - voids are permanent records.
    Note: Uses AuditMixin to track who voided the transaction and when.
    Intentionally does NOT use SoftDeleteMixin - void records should never be deleted.
    """

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_void"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head.id"), index=True)
    fk_transaction_product_id = Column(UUID, ForeignKey("transaction_product.id"), nullable=True)

    # Void details
    void_type = Column(String(50), nullable=False)  # "transaction", "line_item", "payment"
    void_reason = Column(String(50), nullable=False)
    void_reason_detail = Column(String(500), nullable=True)
    voided_amount = Column(Numeric(precision=15, scale=4), nullable=False)

    # Authorization
    requires_manager_approval = Column(Boolean, nullable=False, default=True)
    manager_id = Column(UUID, ForeignKey("cashier.id"), nullable=True)
    manager_password_verified = Column(Boolean, nullable=False, default=False)
    approved_at = Column(DateTime, nullable=True)

    # Fiscal compliance
    fiscal_cancellation_required = Column(Boolean, nullable=False, default=False)
    fiscal_cancellation_completed = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<TransactionVoid(type='{self.void_type}', amount='{self.voided_amount}')>"
