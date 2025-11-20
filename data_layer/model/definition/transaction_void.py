"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025 Ferhat Mousavi

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
