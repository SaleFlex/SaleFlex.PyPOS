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
    DateTime, Float, ForeignKey, UUID, Numeric, Index
)

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin

from uuid import uuid4


class TransactionRefundTemp(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """Temporary version of TransactionRefund"""

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_refund_temp"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head_temp.id"), index=True)
    fk_original_transaction_id = Column(UUID, ForeignKey("transaction_head.id"), index=True)
    fk_transaction_product_id = Column(UUID, ForeignKey("transaction_product_temp.id"), nullable=True)
    refund_type = Column(String(50), nullable=False)
    refund_reason = Column(String(50), nullable=False)
    refund_reason_detail = Column(String(500), nullable=True)
    refund_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    refund_quantity = Column(Numeric(precision=15, scale=4), nullable=True)
    restocking_fee = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    requires_approval = Column(Boolean, nullable=False, default=True)
    approved_by = Column(UUID, ForeignKey("cashier.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    item_condition = Column(String(50), nullable=True)
    is_restocked = Column(Boolean, nullable=False, default=False)
    restocked_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<TransactionRefund(type='{self.refund_type}', amount='{self.refund_amount}')>"

    __table_args__ = (
        Index('idx_refund_transaction_temp', 'fk_transaction_head_id'),
        Index('idx_refund_original_temp', 'fk_original_transaction_id'),
    )